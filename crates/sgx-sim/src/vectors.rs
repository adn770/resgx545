// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The hardware instruction vectors (doc/specs/vectors.md, files in the data repository's
//! vectors/ directory): how one runs on the simulator and compares with its
//! readback. The tests, the coverage report and the tools share this.

use crate::json::Json;
use crate::pds::{self, Pds, Port};
use crate::{Bound, Bus, Error, Machine, Memory, Program, run_quad};
use std::collections::BTreeMap;
use std::path::PathBuf;
use usse_isa::Core;

pub const SCRATCH_BASE: u32 = 0x3e00_3000;
pub const SCRATCH_DWORDS: usize = 0x4000;
pub const LIMM_MASK: u64 = 0xFF30_0000_0000_0000;
pub const LIMM_VAL: u64 = 0xFC20_0000_0000_0000;

/// The vectors directory of the data repository: `$RESGX545_DATA`, else `resgx545-data`
/// beside this tree (tools/records/datasets.py finds it the same way); None when absent.
pub fn data() -> Option<PathBuf> {
    let root = match std::env::var_os("RESGX545_DATA") {
        Some(p) if !p.is_empty() => PathBuf::from(p),
        _ => PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../resgx545-data"),
    };
    Some(root.join("vectors")).filter(|d| d.is_dir())
}

/// sgxfive-test's patch: a limm of 0x5CAFnnnn loads the scratch address + nnnn.
pub fn patch_scratch(w: u64) -> u64 {
    let limm = usse_isa::form::Field {
        k: &usse_isa::form::Num { radix: usse_isa::form::Radix::Hex, mul: 1, add: 0 },
        c: &[
            usse_isa::form::Chunk { lo: 0, w: 21 },
            usse_isa::form::Chunk { lo: 36, w: 5 },
            usse_isa::form::Chunk { lo: 44, w: 6 },
        ],
        r: "",
    };
    let imm = limm.get(w);
    if w & LIMM_MASK == LIMM_VAL && imm & !0xffff == 0x5CAF_0000 {
        limm.put(w, SCRATCH_BASE + (imm & 0xffff))
    } else {
        w
    }
}

/// How a vector matches: exactly, or with near values (Machine::near) in
/// it, each within the bound the hardware was measured to, or only with a value the task
/// cannot know accepted whatever the hardware read.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Outcome {
    Exact,
    /// Near values, each within its measured bound (float functions, the PDS fetch pc's
    /// Bound::Lag), and none of Bound::Bits.
    Near,
    /// A value the task does not know, read as any value of its width (Bound::Bits: the PDS
    /// timer a program did not load), reached the readback: that dword is not checked
    /// beyond its width. Near, and counted apart from the bounded near values.
    AnyValue,
    /// The readback agrees with a result of firh's fixed bank 1 or 2 (Machine::fitted), whose
    /// tap families were fitted to these same vectors (FIXED_BANKS, E292): consistent with the
    /// fit, not a hardware check. Counted apart, with the vectors that stop (coverage_json).
    Fitted,
}

impl Outcome {
    /// Whether the match rests on near values (Near or AnyValue).
    pub fn is_near(self) -> bool {
        matches!(self, Outcome::Near | Outcome::AnyValue)
    }
}

/// The reason coverage_json gives the vectors that match only as fitted (Outcome::Fitted).
pub const FITTED: &str = "firh's fixed bank 1 or 2, whose taps are fitted to these vectors (in-sample, \
                          not a hardware check)";

/// Run one vector: how it matches, else why not ("unsupported: ..." for
/// what the simulator does not model yet). A near value that differs from the
/// readback within its bound matches; one computed from a near value
/// (Bound::Derived) has no bound and stops it.
pub fn run_scalar(v: &Json) -> Result<Outcome, String> {
    run_scalar_with(v, |_| {})
}

/// run_scalar with the instance set up further first (state a vector does not record).
pub fn run_scalar_with(v: &Json, setup: impl FnOnce(&mut Machine)) -> Result<Outcome, String> {
    // a program placed in the code heap (init.placed, which tools/usse-asm/convert_extra.py adds)
    // is the one that ran, from the code base the placement gives (Machine::code_index)
    let placed = v.get("init").get("placed");
    let (words, code_index): (Vec<u64>, u32) = match placed.get("offset").num() {
        Some(off) => (
            placed.get("words").arr().iter().map(|w| patch_scratch(w.hex().unwrap())).collect(),
            (off as u32) % 0x80000 / 8,
        ),
        None => {
            (v.get("program").get("words").arr().iter().map(|w| patch_scratch(w.hex().unwrap())).collect(), 0)
        }
    };
    let prog = Program::new(&words, Core::Sgx545);
    let mut mem =
        Memory { base: SCRATCH_BASE, words: (0..SCRATCH_DWORDS as u32).map(|i| 0xD000_0000 | i).collect() };
    let temps = v.get("init").get("temps").num().map_or(124, |t| t as usize);
    // a fill whose readback is one o0: every instance alike
    let mut m =
        Machine { temps, near: true, uniform: true, coeffs: job_coeffs(v), csc_unloaded: job_csc_unloaded(v), code_index, ..Machine::default() };
    setup(&mut m);
    match m.run(&prog, &mut mem, 10_000) {
        Ok(()) => {}
        Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: {e}")),
        Err(e) => return Err(format!("error: {e}")),
    }
    compare(v, &m, &mem)
}

/// A firmware task vector (init.task "firmware"): the wrapper runs from its first instruction over
/// the results page and the register file the vector gives, to its tail call (`lapc`: the closed
/// task it jumps to is not modelled), and the page dwords and the registers the readback lists
/// must equal what it left.
pub fn run_firmware(v: &Json) -> Result<Outcome, String> {
    use crate::fwtask::FwBus;
    let words: Vec<u64> = v.get("program").get("words").arr().iter().map(|w| w.hex().unwrap()).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let init = v.get("init");
    let page = init.get("page");
    let mut bus = FwBus::new(page.get("base").hex().unwrap() as u32, page.get("dwords").num().unwrap() as usize);
    for (k, val) in init.get("mem").obj() {
        bus.set_mem(usize::from_str_radix(k.trim_start_matches("0x"), 16).unwrap(), val.hex().unwrap() as u32);
    }
    for (k, val) in init.get("regs").obj() {
        bus.seed_reg(u32::from_str_radix(k.trim_start_matches("0x"), 16).unwrap(), val.hex().unwrap() as u32);
    }
    let mut m = Machine { temps: init.get("temps").num().map_or(32, |n| n as usize), ..Machine::default() };
    m.pc = v.get("program").get("entry").num().map_or(0, |e| e as usize);
    seed_task_state(&mut m, init.get("state"))?;
    let mut finished = false;
    // sa64 is the one register whose write the hardware did not keep (E536): a read of it after
    // the task wrote it is not a measured case, so it stops the vector
    let mut sa64_written = false;
    for _ in 0..FW_STEPS {
        // the wrapper ends in its tail call: the closed task after it is not part of the vector
        let text = Machine::text(&prog, m.pc);
        if text.is_some_and(|t| t.starts_with("lapc")) {
            finished = true;
            break;
        }
        if let Some(t) = text {
            let (reads, writes) = sa64_use(t);
            if reads && sa64_written {
                return Err("unsupported: reads sa64 after the task wrote it (the hardware kept \
                            the value the host or the closed task left, not the write: E536)"
                    .into());
            }
            sa64_written |= writes;
        }
        match m.step(&prog, &mut bus) {
            Ok(true) => {
                finished = true;
                break;
            }
            Ok(false) => {}
            Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: {e}")),
            Err(e) => return Err(format!("error: {e}")),
        }
    }
    if !finished {
        // a wrapper that does not end is not compared on whatever state it had reached
        return Err(format!("unsupported: the wrapper did not reach its tail call in {FW_STEPS} steps"));
    }
    let rb = v.get("readback");
    for (k, val) in rb.get("mem").obj() {
        let i = usize::from_str_radix(k.trim_start_matches("0x"), 16).unwrap();
        let want = val.hex().unwrap() as u32;
        if bus.mem(i) != want {
            return Err(format!("page dword {k}: want {want:#x}, got {:#x}", bus.mem(i)));
        }
    }
    check_task_state(&m, rb.get("state"))?;
    for (k, val) in rb.get("regs").obj() {
        let off = u32::from_str_radix(k.trim_start_matches("0x"), 16).unwrap();
        let want = val.hex().unwrap() as u32;
        if bus.host_reg(off) != Some(want) {
            return Err(format!("register {k}: want {want:#x}, got {:?}", bus.host_reg(off)));
        }
    }
    Ok(Outcome::Exact)
}

/// The step budget of a firmware vector: the slow task of E539 spins 100000 iterations of three
/// instructions.
const FW_STEPS: usize = 3_000_000;

/// A register number of `bank` from an init.state or readback.state key: a bank has `size`
/// registers, and a key that is not one is a stop (a vector of ours that is wrong), not a panic.
fn bank_key(bank: &str, k: &str, size: usize) -> Result<usize, String> {
    match k.parse::<usize>() {
        Ok(n) if n < size => Ok(n),
        _ => Err(format!("unsupported: state key {bank}{k} is not a register")),
    }
}

/// Whether an instruction's text reads sa64 (an operand after the destination) and whether it
/// writes it (the destination): the text is `[pN] mnemonic dst, src, ...`.
fn sa64_use(t: &str) -> (bool, bool) {
    let mut ops = t.split_whitespace().skip_while(|w| w.trim_start_matches('!').starts_with('p') && w.len() <= 3);
    ops.next(); // the mnemonic
    let rest = ops.collect::<Vec<_>>().join(" ");
    let operands: Vec<&str> = rest.split(',').map(str::trim).collect();
    let writes = operands.first().is_some_and(|d| *d == "sa64");
    let reads = operands.iter().skip(1).any(|s| s.contains("sa64"));
    (reads, writes)
}

/// What the hardware held at a firmware task's entry (init.state, phase 11.30): the task state
/// that outlives a task (E536: sa, the temporaries r20 and r21, i0 and i1, p1 to p3 and pclink
/// were as the task before left them), and the event words in pa. The values are what a reader
/// task read; nothing is modelled about how they got there.
fn seed_task_state(m: &mut Machine, st: &Json) -> Result<(), String> {
    for (k, val) in st.get("sa").obj() {
        let n = bank_key("sa", k, 128)?;
        m.sa[n] = val.hex().unwrap() as u32;
        m.written.sa |= 1 << n;
    }
    for (k, val) in st.get("r").obj() {
        let n = bank_key("r", k, 128)?;
        m.r[n] = val.hex().unwrap() as u32;
        m.written.r |= 1 << n;
    }
    for (k, val) in st.get("i").obj() {
        let n = bank_key("i", k, 4)?;
        m.i[n] = val.hex().unwrap() as u32;
        m.written.i |= 1 << n;
    }
    for (k, val) in st.get("pa").obj() {
        let n = bank_key("pa", k, 128)?;
        m.pa[n] = val.hex().unwrap() as u32;
        m.written.pa |= 1 << n;
    }
    for (k, val) in st.get("p").obj() {
        let n = bank_key("p", k, 4)?;
        m.p[n] = val.hex().unwrap() != 0;
        m.p_set |= 1 << n;
    }
    if let Some(l) = st.get("pclink").hex() {
        m.link = l as u32;
        m.link_set = true;
    }
    Ok(())
}

/// readback.state: the registers the task must have left as the hardware read them.
fn check_task_state(m: &Machine, st: &Json) -> Result<(), String> {
    for (bank, get) in [
        ("sa", (|m: &Machine, n: usize| m.sa[n]) as fn(&Machine, usize) -> u32),
        ("r", |m, n| m.r[n]),
        ("i", |m, n| m.i[n]),
    ] {
        for (k, val) in st.get(bank).obj() {
            let (n, want) = (bank_key(bank, k, if bank == "i" { 4 } else { 128 })?, val.hex().unwrap() as u32);
            if get(m, n) != want {
                return Err(format!("{bank}{n}: want {want:#x}, got {:#x}", get(m, n)));
            }
        }
    }
    for (k, val) in st.get("p").obj() {
        let (n, want) = (bank_key("p", k, 4)?, val.hex().unwrap() != 0);
        if m.p[n] != want {
            return Err(format!("p{n}: want {want}, got {}", m.p[n]));
        }
    }
    Ok(())
}

/// The USE filter coefficients of the job a vector ran in (init.job.use_coeffs, written by
/// vectors.py): None where the vector does not carry its job.
pub fn job_coeffs(v: &Json) -> Option<crate::usse::FilterBlock> {
    let c = v.get("init").get("job").get("use_coeffs");
    match c.get("load") {
        Json::Bool(false) => Some(crate::usse::FilterBlock::default()),
        Json::Bool(true) => {
            let w: Vec<u32> = c.get("words").arr().iter().filter_map(|w| w.hex()).map(|w| w as u32).collect();
            Some(crate::usse::FilterBlock {
                mode: c.get("mode").hex()? as u32,
                groups: Some(w.try_into().ok()?),
            })
        }
        _ => None,
    }
}

/// Whether the job a vector ran in left the colour-space set unloaded: its recorded pokes of the
/// transfer command (init.job.pokes) do not set the load flag, xfer:17 bit 0 (transfer.md 3.2).
/// False where the vector does not carry its job: the YUV formats are then not modelled.
pub fn job_csc_unloaded(v: &Json) -> bool {
    let Json::Arr(pokes) = v.get("init").get("job").get("pokes") else { return false };
    let mut word17 = 0u32;
    for k in pokes.iter().filter_map(|k| k.str()) {
        let Some(rest) = k.strip_prefix("xfer:17") else { continue };
        let (flip, val) = match (rest.strip_prefix("^="), rest.strip_prefix('=')) {
            (Some(x), _) => (true, x),
            (_, Some(x)) => (false, x),
            _ => continue,
        };
        let val = match val.strip_prefix("0x") {
            Some(h) => u32::from_str_radix(h, 16),
            None => val.parse(),
        };
        let Ok(val) = val else { return false };
        word17 = if flip { word17 ^ val } else { val };
    }
    word17 & 1 == 0
}

/// A vector file, each vector given its job (init.job) from the file's sidecar where it does
/// not carry one: `vectors.py jobs` writes vectors/jobs/<the file's path under vectors/>,
/// `.job.json` for `.vec.json`, for the files converted before vectors carried their job.
pub fn load(path: &std::path::Path) -> Json {
    let mut d = crate::json::parse(&std::fs::read_to_string(path).unwrap());
    let Some(side) = sidecar(path).and_then(|p| std::fs::read_to_string(p).ok()) else { return d };
    let side = crate::json::parse(&side);
    let jobs = side.get("jobs");
    if let Json::Obj(top) = &mut d
        && let Some((_, Json::Arr(vs))) = top.iter_mut().find(|(k, _)| k == "vectors")
    {
        for v in vs {
            let id = v.get("id").str().unwrap_or("").to_string();
            let job = jobs.get(&id);
            if let (Json::Obj(fields), false) = (v, matches!(job, Json::Null))
                && let Some((_, Json::Obj(init))) = fields.iter_mut().find(|(k, _)| k == "init")
                && !init.iter().any(|(k, _)| k == "job")
            {
                init.push(("job".to_string(), job.clone()));
            }
        }
    }
    d
}

/// The sidecar of a vector file (load): the nearest `vectors` directory above it, then
/// jobs/ and the same path.
fn sidecar(path: &std::path::Path) -> Option<PathBuf> {
    let name = path.file_name()?.to_str()?.strip_suffix(".vec.json")?;
    let mut rel = vec![format!("{name}.job.json")];
    let mut dir = path.parent()?;
    while dir.file_name()? != "vectors" {
        rel.push(dir.file_name()?.to_str()?.to_string());
        dir = dir.parent()?;
    }
    Some(rel.iter().rev().fold(dir.join("jobs"), |p, c| p.join(c)))
}

/// The scratch dwords and o0 a run left, against the vector's readback.
fn compare(v: &Json, m: &Machine, mem: &Memory) -> Result<Outcome, String> {
    let rb = v.get("readback");
    let mut want: BTreeMap<usize, u32> = BTreeMap::new();
    for (off, val) in rb.get("scratch").obj() {
        let off = usize::from_str_radix(off.trim_start_matches("0x"), 16).unwrap();
        want.insert(off / 4, val.hex().unwrap() as u32);
    }
    let (mut diffs, mut near, mut any) = (Vec::new(), false, false);
    let mut check = |what: String, got: u32, want: u32, bound: Option<&Bound>| -> Result<(), String> {
        near |= bound.is_some();
        any |= matches!(bound, Some(Bound::Bits(_) | Bound::Mask(_)));
        match bound {
            _ if got == want => {}
            Some(Bound::Derived) => return Err(format!("unsupported: {what} is computed from a near value")),
            Some(b) if b.admits(got, want) => {}
            _ => diffs.push(format!("{what} got 0x{got:08x} want 0x{want:08x}")),
        }
        Ok(())
    };
    // sgxfive-test lists a fill probe's changed scratch dwords in address
    // order, at most 32 (probe_scratch): with 32 listed, those past the last
    // are not known (the x-mip probes store 85)
    let known = if want.len() >= 32 { want.keys().max().copied() } else { None };
    for (i, &got) in mem.words.iter().enumerate() {
        if known.is_some_and(|k| i > k) {
            break;
        }
        let w = want.get(&i).copied().unwrap_or(0xD000_0000 | i as u32);
        check(format!("scratch[0x{:03x}]", i * 4), got, w, m.near_mem.get(&(SCRATCH_BASE + 4 * i as u32)))?;
    }
    if let Some(o0) = rb.get("o0").hex() {
        if let Some(w) = m.unknown.get(&("o", 0)) {
            return Err(format!("unsupported: {w} (in o0)"));
        }
        check("o0".to_string(), m.o[0], o0 as u32, m.bounds.get(&("o", 0)))?;
    }
    if !diffs.is_empty() {
        return Err(diffs[..diffs.len().min(4)].join("; "));
    }
    Ok(if m.fitted {
        Outcome::Fitted
    } else if any {
        Outcome::AnyValue
    } else if near {
        Outcome::Near
    } else {
        Outcome::Exact
    })
}

/// The task a PDS vector's program runs as: a fill's secondary program,
/// whose douta writes (value, then the attribute in bits 19-8 of the control
/// word) reach the secondary attributes of the fill's USE tasks, within the
/// PDS state's secondary attribute size (pds_isa 3.4). Its doutu is taken; the
/// other ports are open.
struct Secondary {
    attrs: usize,
    sa: [u32; 128],
    written: u128,
    /// The port writes so far, and the attribute each douta wrote (by write index).
    writes: usize,
    douta: Vec<(usize, usize)>,
    /// The scratch buffer's dwords, which the PDS reaches through `low`: the probe's
    /// mapping of it in the first MiB (sgxfive-test probe --low), if any.
    scratch: Vec<u32>,
    low: Option<u32>,
}

impl Secondary {
    fn word(&mut self, addr: u32) -> Option<&mut u32> {
        let off = addr.checked_sub(self.low?)?;
        self.scratch.get_mut(off as usize / 4)
    }
}

impl Bus for Secondary {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.word(addr).map(|w| *w).ok_or(Error::Fault(addr))
    }

    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        *self.word(addr).ok_or(Error::Fault(addr))? = v;
        Ok(())
    }

    fn port(&mut self, port: Port, w: [u32; 4]) -> Result<(), Error> {
        let open = |why: String| Error::Unsupported { pc: 0, text: String::new(), why };
        self.writes += 1;
        if port == Port::Douta {
            self.douta.push((self.writes - 1, (w[1] >> 8 & 0xfff) as usize));
        }
        match port {
            Port::Douta => {
                let n = (w[1] >> 8 & 0xfff) as usize;
                if n >= self.attrs.min(128) {
                    return Err(open(format!(
                        "douta to sa{n}, past the {} secondary attributes",
                        self.attrs
                    )));
                }
                (self.sa[n], self.written) = (w[0], self.written | 1 << n);
                Ok(())
            }
            Port::Doutu => Ok(()),
            // EVENT_TIMER: the Pds keeps the value the program reads back (pds_isa 8.9)
            Port::Tim => Ok(()),
            p => Err(open(format!("movs to {p:?}: the port is open (pds_isa 3.4)"))),
        }
    }
}

/// Run a PDS vector (pds_isa 8): its program as the fill's PDS secondary
/// program, then the USE program it names (sa_dump.s) with the secondary
/// attributes the PDS wrote, against the readback; the PDS reaches the scratch
/// buffer through the probe's low mapping of it, if any. A job the hardware
/// lost because it hung matches a program that does not halt, and one that
/// faulted a program that faults.
///
/// Every 16 x 16 tile of the fill (64 pixels wide, its instances in raster order) runs the
/// program with its own inputs (Pds::fill_secondary) and its pixels store to the same scratch
/// dwords, so the readback is one tile's: the vector matches if one tile's run does. Else
/// the error of the first tile, or a mismatch if a tile ran to one. run_pds_tile_match says
/// which tile.
pub fn run_pds(v: &Json) -> Result<Outcome, String> {
    run_pds_tile_match(v).map(|(o, _)| o)
}

/// run_pds with the tile (tile_x, tile_y) whose run matched, the first in raster order: a
/// vector whose program does not depend on the tile matches on (0, 0), so a match on another
/// tile is one that needed that tile's inputs (its ir0). The readback does not say which
/// tile's pixel stored last, so the coverage report counts these (pds_tiles).
pub fn run_pds_tile_match(v: &Json) -> Result<(Outcome, (u32, u32)), String> {
    let init = v.get("init");
    if init.get("task").str() != Some("pds-secondary") {
        return Err(format!("unsupported: the task {:?}", init.get("task").str()));
    }
    let instances = init.get("instances").num().unwrap_or(2048.0) as u32;
    let (tw, th) = (FILL_WIDTH.div_ceil(16), (instances / FILL_WIDTH).max(1).div_ceil(16));
    let mut err: Option<String> = None;
    for ty in 0..th {
        for tx in 0..tw {
            match run_pds_tile(v, Pds::fill_secondary(tx, ty)) {
                Ok(o) => return Ok((o, (tx, ty))),
                Err(e) => match &err {
                    Some(f) if !f.starts_with("unsupported") || e.starts_with("unsupported") => {}
                    _ => err = Some(e),
                },
            }
        }
    }
    Err(err.unwrap_or_default())
}

/// The fill's width in pixels (sgxfive-test probe): 64.
const FILL_WIDTH: u32 = 64;

/// run_pds for one tile's PDS.
fn run_pds_tile(v: &Json, mut pds: Pds) -> Result<Outcome, String> {
    let (p, init) = (v.get("program"), v.get("init"));
    let words: Vec<u32> = p.get("words").arr().iter().map(|w| w.hex().unwrap() as u32).collect();
    let prog = pds::Program::new(&words, p.get("data").num().unwrap_or(0.0) as usize);
    let mut bus = Secondary {
        attrs: init.get("attrs").num().unwrap_or(0.0) as usize,
        sa: [0; 128],
        written: 0,
        writes: 0,
        douta: Vec::new(),
        scratch: (0..SCRATCH_DWORDS as u32).map(|i| 0xD000_0000 | i).collect(),
        low: init.get("scratch").get("low").hex().map(|a| a as u32),
    };
    let failed = v.get("readback").get("failed").str();
    let hung = failed.is_some_and(|f| f.starts_with("job hung"));
    let faulted = failed.is_some_and(|f| f.starts_with("job faulted"));
    match pds.run(&prog, &mut bus, 10_000) {
        Err(Error::StepLimit) if hung => return Ok(Outcome::Exact),
        // a load or store outside what the job mapped faults, as the hardware's did (E127)
        Err(Error::Fault(_)) if faulted => return Ok(Outcome::Exact),
        // a jump out of the program fetches memory the job did not map: the hardware's
        // 24-bit targets 2 MiB and more past it faulted (pds-encoding-bits-flow-bra)
        Err(Error::PcOutOfRange(_)) if faulted => return Ok(Outcome::Exact),
        Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: {e}")),
        Err(e) => return Err(format!("error: {e}")),
        Ok(()) if failed.is_some() => {
            return Err(format!("the hardware job failed ({}), the PDS halted", failed.unwrap()));
        }
        Ok(()) => {}
    }
    let words: Vec<u64> =
        init.get("use").get("words").arr().iter().map(|w| patch_scratch(w.hex().unwrap())).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let mut mem = Memory { base: SCRATCH_BASE, words: std::mem::take(&mut bus.scratch) };
    let temps = init.get("temps").num().map_or(124, |t| t as usize);
    let mut m = Machine { temps, near: true, sa: bus.sa, coeffs: job_coeffs(v), csc_unloaded: job_csc_unloaded(v), ..Machine::default() };
    m.written.sa = bus.written;
    // an attribute written last from a near value (the fetch pc) keeps its bound
    let mut sa_near = BTreeMap::new();
    for &(i, n) in &bus.douta {
        sa_near.insert(n, pds.port_near.get(i).and_then(|w| w[0]));
    }
    for (n, b) in sa_near {
        if let Some(b) = b {
            m.bounds.insert(("sa", n), b);
        }
    }
    match m.run(&prog, &mut mem, 10_000) {
        Ok(()) => {}
        Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: USE: {e}")),
        Err(e) => return Err(format!("error: USE: {e}")),
    }
    compare(v, &m, &mem)
}

/// Probes whose readback a single instance cannot reproduce, and why: the run (a prefix of
/// the raw file's path in the data repository), the probe or a vector's id, the reason.
pub const SKIP: &[(&str, &str, &str)] = &[
    // (a row with an empty run prefix applies to the first and the follow-up round alike; the
    // one for late-load case 9 names the follow-up round only)
    // every instance loads and stores one shared dword: the readback is whichever instance's
    // dump came last, after others' stores or not, which no one instance determines
    ("", "usse-cache-control-modes", "instances share the dword they store"),
    ("", "usse-cache-control-late-n1024__2", "instances share the dword they store"),
    ("", "usse-cache-control-late-n1024__10", "instances share the dword they store"),
    ("followup/", "usse-cache-control-late-n1024__9", "instances share the dword they store"),
    // the sampler keeps what it fetched; a store to a fetched texel is not seen
    ("", "texture-sampler-cache-texcache", "the sampler cache is not modelled"),
    ("", "texture-sampler-cache-texcache2", "the sampler cache is not modelled"),
    // timing probes: a loop of up to 1e7 iterations, past the simulator's step limit
    ("usse/loop-timing/", "", "the loop runs more steps than the simulator's limit"),
    // the fill's one pixel (38, 6) reads another i127 than its neighbours' rule gives (first round only)
    (
        "usse/internal-registers/",
        "usse-internal-registers-bank7__16",
        "one pixel of 2048 reads an unexplained i127",
    ),
    // a store job's outcome depends on the jobs before it, or differs between two runs of
    // the same program (a fault after a fault, a total-1 store that faults in one run only)
    ("", "pds-memory-mem2__0", "faults in one run only"),
    ("pds/store-totals/", "pds-store-totals-runs__10", "faults in one run of three, after a faulted job"),
    ("", "pds-memory-mem3__14", "ran after a faulted job"),
    ("", "pds-memory-mem3__15", "ran after a faulted job"),
    ("", "pds-memory-mem5__5", "faults in one run only"),
    ("", "pds-memory-mem5__13", "faults in one run only"),
    ("", "pds-memory-mem6__1", "ran after a faulted job"),
    ("", "pds-memory-mem6__2", "ran after a faulted job"),
    ("", "pds-memory-mem6__6", "ran after a faulted job"),
    ("", "pds-memory-mem6__10", "ran after a faulted job"),
    // an instance reads another instance's unfenced store: what it sees is a matter of timing and
    // of the order of the tiles (E514, Q143), which the simulator does not model
    (
        "usse/store-own2/",
        "usse-store-own2-cross__5",
        "another instance's unfenced store: timing and tile order (E514)",
    ),
    (
        "usse/store-own2/",
        "usse-store-own2-cross__6",
        "another instance's unfenced store: timing and tile order (E514)",
    ),
    (
        "usse/store-own2/",
        "usse-store-own2-cross__7",
        "another instance's unfenced store: timing and tile order (E514)",
    ),
    (
        "usse/store-own3/",
        "usse-store-own3-cross",
        "another instance's unfenced store: timing and tile order (E514)",
    ),
    // the fill's PDS program runs to its end and the job faults or hangs in the task the USSE
    // program starts with `emitpds` (E488, E520), which the simulator does not model: the PDS
    // vectors of these runs (63 of 65; the two jobs that ran are in the runs too) are left out
    ("usse/emit-addend/", "", "the job faulted or hung in the task an emitpds started (E488, E520)"),
    ("usse/emit-addend2/", "", "the job faulted or hung in the task an emitpds started (E488, E520)"),
    ("usse/emitpds/", "", "the job faulted or hung in the task an emitpds started (E488, E520)"),
];

/// The fill's width: instances are in raster order, 64 x 32.
pub const WIDTH: usize = 64;

/// Run a vector that reports every pixel, with pa0 = (y << 16) | x, as the
/// fill's aligned 2x2 quads (TL, TR, BL, BR); every pixel's o0 must match.
/// The scratch dwords are not compared: every instance stores to the same ones.
pub fn run_pixels(v: &Json) -> Result<Outcome, String> {
    let words: Vec<u64> =
        v.get("program").get("words").arr().iter().map(|w| patch_scratch(w.hex().unwrap())).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let temps = v.get("init").get("temps").num().map_or(124, |t| t as usize);
    let pixels: Vec<u32> =
        v.get("readback").get("pixels").arr().iter().map(|p| p.hex().unwrap() as u32).collect();
    let height = pixels.len() / WIDTH;
    let mut fitted = false;
    for y0 in (0..height).step_by(2) {
        for x0 in (0..WIDTH).step_by(2) {
            let at = [(x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)];
            let mut quad: [Machine; 4] = Default::default();
            for (m, &(x, y)) in quad.iter_mut().zip(&at) {
                m.temps = temps;
                m.coeffs = job_coeffs(v);
                m.csc_unloaded = job_csc_unloaded(v);
                m.pa[0] = (y as u32) << 16 | x as u32;
                m.pixel = Some((x as u32, y as u32));
                m.written.pa |= 1;
            }
            let mut mem = Memory {
                base: SCRATCH_BASE,
                words: (0..SCRATCH_DWORDS as u32).map(|i| 0xD000_0000 | i).collect(),
            };
            match run_quad(&mut quad, &prog, &mut mem, 10_000) {
                Ok(()) => {}
                Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: {e}")),
                Err(e) => return Err(format!("error: {e}")),
            }
            for (m, &(x, y)) in quad.iter().zip(&at) {
                fitted |= m.fitted;
                let want = pixels[y * WIDTH + x];
                if m.o[0] != want {
                    return Err(format!("pixel ({x}, {y}) o0 got 0x{:08x} want 0x{want:08x}", m.o[0]));
                }
            }
        }
    }
    Ok(if fitted { Outcome::Fitted } else { Outcome::Exact })
}

/// Whether a probe's run is on the skip list, and why.
pub fn skipped(raw: &str, probe: &str, id: &str) -> Option<&'static str> {
    SKIP.iter().find(|(r, p, _)| (p.is_empty() || *p == probe || *p == id) && raw.starts_with(r)).map(|s| s.2)
}

/// What a vector needs: one instance (the uniform o0 and the scratch), every
/// pixel as quads, a PDS program as a fill's secondary (run_pds), or nothing a
/// simulator can compare (failed USSE jobs, pixels that differ without being
/// reported).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Kind {
    Scalar,
    Pixels,
    Pds,
    /// A firmware (EDM) task of our own, run to its tail call over `fwtask::FwBus`.
    Firmware,
    None,
}

pub fn kind(v: &Json) -> Kind {
    if v.get("init").get("task").str() == Some("firmware") {
        return Kind::Firmware;
    }
    let tri = v.get("provenance").get("options").arr().iter().any(|o| o.str() == Some("--tri"));
    if v.get("program").get("isa").str() == Some("pds") {
        // on the triangle host the PDS program is the primary's, not the fill's secondary
        return if tri { Kind::None } else { Kind::Pds };
    }
    let rb = v.get("readback");
    if rb.get("failed").str().is_some() || v.get("program").get("isa").str() != Some("usse") {
        return Kind::None;
    }
    let coords = v.get("init").get("pa0").str() == Some("coords");
    if !rb.get("pixels").arr().is_empty() && coords {
        return Kind::Pixels;
    }
    // on the triangle host the scene decides which pixels run the slot's shader: one colour
    // over the target may be the background (isp-stencil-st-front-never), not its output
    if rb.get("o0").str().is_none() || coords || tri { Kind::None } else { Kind::Scalar }
}

/// Run a vector of either kind: Ok, or "unsupported: ..." / a mismatch.
pub fn run(v: &Json) -> Option<Result<Outcome, String>> {
    match kind(v) {
        Kind::Scalar => Some(run_scalar(v)),
        Kind::Pixels => Some(run_pixels(v)),
        Kind::Pds => Some(run_pds(v)),
        Kind::Firmware => Some(run_firmware(v)),
        Kind::None => None,
    }
}

/// A vertex task vector (init.task "vertex", phase 11.33): the program runs once per vertex of the draw
/// (init.instances of them, init.per vertices a task), as Machine::vertex, and the outputs init.outputs of each equal
/// readback.vertices; init.skip names vertices the hardware readback does not decode.
pub fn run_vertex(v: &Json) -> Result<Outcome, String> {
    let words: Vec<u64> = v.get("program").get("words").arr().iter().map(|w| w.hex().unwrap()).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let init = v.get("init");
    let n = init.get("instances").num().ok_or("no init.instances")? as u32;
    let per = init.get("per").num().ok_or("no init.per")? as u32;
    let temps = init.get("temps").num().map_or(124, |t| t as usize);
    let skip: Vec<u32> = init.get("skip").arr().iter().filter_map(|x| x.num()).map(|x| x as u32).collect();
    let outs: Vec<usize> =
        init.get("outputs").arr().iter().filter_map(|o| o.str()?.strip_prefix('o')?.parse().ok()).collect();
    let rows = v.get("readback").get("vertices").arr();
    if rows.len() != n as usize {
        return Err(format!("readback holds {} vertices, init.instances is {n}", rows.len()));
    }
    for i in (0..n).filter(|i| !skip.contains(i)) {
        let mut mem = Memory { base: SCRATCH_BASE, words: vec![] };
        let mut m = Machine { temps, vertex: Some((i, per, n)), ..Machine::default() };
        match m.run(&prog, &mut mem, 10_000) {
            Ok(()) => {}
            Err(e @ Error::Unsupported { .. }) => return Err(format!("unsupported: {e}")),
            Err(e) => return Err(format!("error: {e}")),
        }
        for (k, o) in outs.iter().enumerate() {
            let want = rows[i as usize].arr()[k].hex().ok_or("a readback value")? as u32;
            if m.o[*o] != want {
                return Err(format!("vertex {i} o{o}: model {:#x}, hardware {want:#x}", m.o[*o]));
            }
        }
    }
    Ok(Outcome::Exact)
}

/// The forms a probe tests: its OP text (the provenance inputs, or the
/// parameters with {NAME} replaced from the inputs), assembled line by line
/// (a raw `.long 0x<word>` line as its word); lines that do not assemble on
/// their own are left out, and so are the set-up moves, tests and waits when
/// the OP has another form.
pub fn under_test(v: &Json) -> Vec<usize> {
    let Some(op) = op_text(v) else { return vec![] };
    if kind(v) == Kind::Pds {
        return pds_under_test(&op);
    }
    let mut forms = vec![];
    for line in op.lines() {
        let raw = line.trim().strip_prefix(".long").and_then(|t| {
            let t = t.split(';').next()?.trim();
            u64::from_str_radix(t.strip_prefix("0x").or(t.strip_prefix("0X"))?, 16).ok()
        });
        if let Some(w) = raw.or_else(|| usse_isa::encode(line.trim(), Core::Sgx545))
            && let Some(f) = usse_isa::decode_fields(w, Core::Sgx545)
            && !forms.contains(&f.form)
        {
            forms.push(f.form);
        }
    }
    let setup =
        |f: &usize| matches!(usse_isa::table().forms[*f].op, "mov" | "mov_imm" | "test" | "nop" | "wdf");
    if forms.iter().any(|f| !setup(f)) {
        forms.retain(|f| !setup(f));
    }
    forms
}

/// A probe's OP text: the provenance inputs, or the parameters with {NAME}
/// replaced from the inputs.
fn op_text(v: &Json) -> Option<String> {
    let p = v.get("provenance");
    let (inputs, params) = (p.get("inputs"), p.get("params"));
    let mut op = inputs.get("OP").str().or(params.get("OP").str())?.to_string();
    for (k, val) in inputs.obj().iter().chain(params.obj()) {
        if let Some(s) = val.str() {
            op = op.replace(&format!("{{{k}}}"), s);
        }
    }
    Some(op)
}

/// The PDS forms an OP uses (its lines without labels, any label taken as 0);
/// the moves that read results out (mov32), the waits and the ends are left
/// out when the OP has another form.
fn pds_under_test(op: &str) -> Vec<usize> {
    let resolve = |_: &str| Some(0u64);
    let cx = usse_isa::Ctx { core: Core::Sgx545, resolve: Some(&resolve) };
    let mut forms = vec![];
    for line in op.lines() {
        let line = line.split(';').next().unwrap_or("").trim();
        let line = match line.split_once(':') {
            Some((l, rest)) if l.chars().all(|c| c.is_ascii_alphanumeric() || c == '_') => rest.trim(),
            _ => line,
        };
        if let Some(w) = pds_isa::encode_with(line, &cx)
            && let Some(f) = pds_isa::decode_fields(w)
            && !forms.contains(&f.form)
        {
            forms.push(f.form);
        }
    }
    let setup = |f: &usize| matches!(pds_isa::forms().nth(*f).map(|f| f.op), Some("mov32" | "nop" | "halt"));
    if forms.iter().any(|f| !setup(f)) {
        forms.retain(|f| !setup(f));
    }
    forms
}

/// The vector files under `dir` (data()): every `*.vec.json` of its subdirectories, in path
/// order (the jobs/ sidecars are not vector files).
pub fn probe_files(dir: &std::path::Path) -> Vec<PathBuf> {
    fn walk(d: &std::path::Path, out: &mut Vec<PathBuf>) {
        for e in std::fs::read_dir(d).into_iter().flatten().flatten() {
            let p = e.path();
            if p.is_dir() {
                walk(&p, out);
            } else if p.file_name().and_then(|n| n.to_str()).is_some_and(|n| n.ends_with(".vec.json")) {
                out.push(p);
            }
        }
    }
    let mut v = vec![];
    walk(dir, &mut v);
    v.sort();
    v
}

/// The reason of an unsupported outcome, with numbers taken out, so that one
/// reason is counted once ("reads r5 before ..." and "reads r9 ..." alike).
pub fn reason(e: &str) -> String {
    let why = e.rsplit(": ").next().unwrap_or(e);
    // a PDS stop cites its section of the reference; the reason is the text before it
    let why = why.split(" (pds_isa").next().unwrap_or(why);
    // "unsupported: <pc>: <text>: no semantics ...": by mnemonic
    if why.starts_with("no semantics") {
        let parts: Vec<&str> = e.splitn(4, ": ").collect();
        let text = parts.get(2).copied().unwrap_or("");
        let m = text.split_whitespace().find(|t| !(t.starts_with('p') || t.starts_with('!')) || t.len() > 3);
        return format!("no semantics yet: {}", m.unwrap_or("").split('.').next().unwrap());
    }
    let mut out = String::new();
    for c in why.chars() {
        if c.is_ascii_digit() {
            if !out.ends_with('N') {
                out.push('N');
            }
        } else {
            out.push(c);
        }
    }
    out
}

fn esc(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}

/// The simulator's coverage of the vectors in `dir` (data(); the report is
/// `doc/isa/sim-coverage.json`, which `cargo run --release -p sgx-sim --example coverage`
/// writes): for each form of the USSE table, its op and, by the probes whose instructions under
/// test use it, how many vectors match, stop unsupported or mismatch, with the unsupported
/// reasons. A vector that agrees only with a fitted result (Outcome::Fitted) counts with the
/// stops, its reason FITTED, and the totals' "fitted" says how many. "near" counts, by probe,
/// the matches that rest on near values, and the totals' "any" the USSE ones of them that rest
/// on a value read as any value (Outcome::AnyValue: the firh latch's unwritten bytes); for the
/// PDS forms "any" counts the part of those that rest on a value read as any value of its
/// width (Outcome::AnyValue), and the totals give "pds_near", "pds_any" and the tiles the PDS
/// matches ran on ("pds_tiles", run_pds_tile_match).
pub fn coverage_json(dir: &std::path::Path) -> String {
    type Counts = [usize; 3];
    let table = usse_isa::table();
    let mut probes: Vec<BTreeMap<String, Counts>> = vec![BTreeMap::new(); table.forms.len()];
    let mut whys: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); table.forms.len()];
    let mut totals: BTreeMap<&str, Counts> = BTreeMap::new();
    let mut all_whys: BTreeMap<String, usize> = BTreeMap::new();
    let mut nears: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); table.forms.len()];
    let (mut all_near, mut all_any, mut all_fitted) = (0, 0, 0);
    let npds = pds_isa::forms().count();
    let mut pds_probes: Vec<BTreeMap<String, Counts>> = vec![BTreeMap::new(); npds];
    let mut pds_whys: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); npds];
    let mut pds_all_whys: BTreeMap<String, usize> = BTreeMap::new();
    let mut pds_nears: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); npds];
    let mut pds_anys: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); npds];
    let (mut pds_near, mut pds_any) = (0, 0);
    let mut pds_tiles: BTreeMap<(u32, u32), usize> = BTreeMap::new();
    for path in probe_files(dir) {
        let d = load(&path);
        let raw = d.get("run").get("raw").str().unwrap_or("").to_string();
        for v in d.get("vectors").arr() {
            let probe = v.get("provenance").get("probe").str().unwrap_or("").to_string();
            if skipped(&raw, &probe, v.get("id").str().unwrap_or("")).is_some() {
                continue;
            }
            let k = kind(v);
            if k == Kind::Pds {
                let rt = run_pds_tile_match(v);
                if let Ok((_, t)) = &rt {
                    *pds_tiles.entry(*t).or_default() += 1;
                }
                let r = rt.map(|(o, _)| o);
                let near = r.as_ref().is_ok_and(|o| o.is_near());
                let any = r == Ok(Outcome::AnyValue);
                pds_near += near as usize;
                pds_any += any as usize;
                let slot = match &r {
                    Ok(_) => 0,
                    Err(e) if e.starts_with("unsupported") => 1,
                    Err(_) => 2,
                };
                totals.entry("pds").or_default()[slot] += 1;
                let why = r.as_ref().err().filter(|_| slot == 1).map(|e| reason(e));
                if let Some(w) = &why {
                    *pds_all_whys.entry(w.clone()).or_default() += 1;
                }
                for f in under_test(v) {
                    pds_probes[f].entry(probe.clone()).or_default()[slot] += 1;
                    if near {
                        *pds_nears[f].entry(probe.clone()).or_default() += 1;
                    }
                    if any {
                        *pds_anys[f].entry(probe.clone()).or_default() += 1;
                    }
                    if let Some(w) = &why {
                        *pds_whys[f].entry(w.clone()).or_default() += 1;
                    }
                }
                continue;
            }
            let Some(r) = run(v) else { continue };
            let near = r.as_ref().is_ok_and(|o| o.is_near());
            all_near += near as usize;
            all_any += (r == Ok(Outcome::AnyValue)) as usize;
            all_fitted += (r == Ok(Outcome::Fitted)) as usize;
            // a fitted match is not a hardware check: it counts with the stops, its reason FITTED
            let slot = match &r {
                Ok(Outcome::Fitted) => 1,
                Ok(_) => 0,
                Err(e) if e.starts_with("unsupported") => 1,
                Err(_) => 2,
            };
            let class = match k {
                Kind::Pixels => "pixels",
                Kind::Firmware => "firmware",
                _ => "scalar",
            };
            totals.entry(class).or_default()[slot] += 1;
            let why = match &r {
                Ok(Outcome::Fitted) => Some(FITTED.to_string()),
                Err(e) if slot == 1 => Some(reason(e)),
                _ => None,
            };
            if let Some(w) = &why {
                *all_whys.entry(w.clone()).or_default() += 1;
            }
            for f in under_test(v) {
                probes[f].entry(probe.clone()).or_default()[slot] += 1;
                if near {
                    *nears[f].entry(probe.clone()).or_default() += 1;
                }
                if let Some(w) = &why {
                    *whys[f].entry(w.clone()).or_default() += 1;
                }
            }
        }
    }
    let mut o = String::from("{\n  \"format\": \"sgx-sim-coverage\",\n  \"version\": 1,\n");
    o += "  \"generated\": \"cargo run --release -p sgx-sim --example coverage\",\n  \"totals\": {";
    o += &totals.iter().map(|(k, c)| format!("\"{k}\": {c:?}")).collect::<Vec<_>>().join(", ");
    o += &format!(
        ", \"near\": {all_near}, \"any\": {all_any}, \"fitted\": {all_fitted}, \"pds_near\": {pds_near}, \
         \"pds_any\": {pds_any}"
    );
    o += ", \"pds_tiles\": {";
    o += &pds_tiles.iter().map(|((x, y), n)| format!("\"{x},{y}\": {n}")).collect::<Vec<_>>().join(", ");
    o += "}},\n  \"unsupported\": {";
    o += &all_whys.iter().map(|(w, n)| format!("\"{}\": {n}", esc(w))).collect::<Vec<_>>().join(", ");
    o += "},\n  \"pds_unsupported\": {";
    o += &pds_all_whys.iter().map(|(w, n)| format!("\"{}\": {n}", esc(w))).collect::<Vec<_>>().join(", ");
    o += "},\n  \"forms\": [\n";
    let rows: Vec<String> = table
        .forms
        .iter()
        .enumerate()
        .map(|(i, f)| {
            let op = match crate::sim_op(f) {
                "" => "null".to_string(),
                op => format!("\"{op}\""),
            };
            let pr: Vec<String> = probes[i].iter().map(|(p, c)| format!("\"{}\": {c:?}", esc(p))).collect();
            let wh: Vec<String> = whys[i].iter().map(|(w, n)| format!("\"{}\": {n}", esc(w))).collect();
            let ne: Vec<String> = nears[i].iter().map(|(p, n)| format!("\"{}\": {n}", esc(p))).collect();
            format!(
                "    {{\"form\": {i}, \"op\": {op}, \"probes\": {{{}}}, \"near\": {{{}}}, \"unsupported\": {{{}}}}}",
                pr.join(", "),
                ne.join(", "),
                wh.join(", ")
            )
        })
        .collect();
    o += &rows.join(",\n");
    o += "\n  ],\n  \"pds_forms\": [\n";
    let rows: Vec<String> = pds_isa::forms()
        .enumerate()
        .map(|(i, f)| {
            let op = if f.op.is_empty() { "null".to_string() } else { format!("\"{}\"", f.op) };
            let pr: Vec<String> =
                pds_probes[i].iter().map(|(p, c)| format!("\"{}\": {c:?}", esc(p))).collect();
            let wh: Vec<String> = pds_whys[i].iter().map(|(w, n)| format!("\"{}\": {n}", esc(w))).collect();
            let ne: Vec<String> = pds_nears[i].iter().map(|(p, n)| format!("\"{}\": {n}", esc(p))).collect();
            let an: Vec<String> = pds_anys[i].iter().map(|(p, n)| format!("\"{}\": {n}", esc(p))).collect();
            format!(
                "    {{\"form\": {i}, \"op\": {op}, \"probes\": {{{}}}, \"near\": {{{}}}, \"any\": {{{}}}, \
                 \"unsupported\": {{{}}}}}",
                pr.join(", "),
                ne.join(", "),
                an.join(", "),
                wh.join(", ")
            )
        })
        .collect();
    o += &rows.join(",\n");
    o += "\n  ]\n}\n";
    o
}

#[cfg(test)]
mod tests {
    /// A fill vector whose PDS program passes ir0 to sa0 and whose shader stores sa0 to scratch
    /// dword 0, read back as `got`.
    fn ir0_vector(got: u32) -> crate::json::Json {
        pds_vector("or ds0[48], ir0, ds1[1]", got)
    }

    /// The same with `first` in place of the read of ir0.
    fn pds_vector(first: &str, got: u32) -> crate::json::Json {
        pds_vector_failed(first, got, "null")
    }

    /// The same, the job's failure given (JSON: null or a string).
    fn pds_vector_failed(first: &str, got: u32, failed: &str) -> crate::json::Json {
        let enc = |t: &str| format!("\"0x{:08x}\"", pds_isa::encode(t).unwrap());
        let code: Vec<&str> = first
            .lines()
            .chain([
                "movs douta, ds0[48], ds1[0], ds0[48], ds0[48]",
                "movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]",
                "halt",
            ])
            .collect();
        let words: Vec<String> = ["\"0x0\"".into(), "\"0x0\"".into(), "\"0x0\"".into(), "\"0x0\"".into()]
            .into_iter()
            .chain(code.iter().map(|t| enc(t)))
            .collect();
        // sa_dump.s cut to sa0: phas, the scratch address, stad sa0, idf, wdf, end
        let usew = [
            "0xfa44070000000000",
            "0xfca1705003af0000",
            "0xf0220000b0074000",
            "0xf820000000000000",
            "0xf920000000000000",
            "0xfca430d10007a000",
        ];
        let usew: Vec<String> = usew.iter().map(|w| format!("\"{w}\"")).collect();
        crate::json::parse(&format!(
            r#"{{"program": {{"isa": "pds", "data": 4, "words": [{}]}},
                "init": {{"task": "pds-secondary", "instances": 2048, "temps": 32, "attrs": 16,
                          "use": {{"words": [{}]}}}},
                "readback": {{"failed": {failed}, "o0": null,
                              "scratch": {{"0x000": "0x{got:08x}"}}}},
                "provenance": {{"options": ["--pds", "4"]}}}}"#,
            words.join(", "),
            usew.join(", ")
        ))
    }

    #[test]
    fn a_vector_s_job_gives_the_coefficients() {
        use crate::usse::FilterBlock;
        let v = |job: &str| crate::json::parse(&format!(r#"{{"init": {{"job": {job}}}}}"#));
        let words: Vec<String> = (1..=9).map(|i| format!("\"0x{i:08x}\"")).collect();
        let loaded = format!(
            r#"{{"pokes": [], "use_coeffs": {{"load": true, "mode": "0x00000007", "words": [{}]}}}}"#,
            words.join(", ")
        );
        assert_eq!(
            super::job_coeffs(&v(&loaded)),
            Some(FilterBlock { mode: 7, groups: Some([1, 2, 3, 4, 5, 6, 7, 8, 9]) })
        );
        let none = r#"{"pokes": [], "use_coeffs": {"load": false}}"#;
        assert_eq!(super::job_coeffs(&v(none)), Some(FilterBlock::default()));
        // a vector without its job: not known
        assert_eq!(super::job_coeffs(&crate::json::parse(r#"{"init": {}}"#)), None);
    }

    #[test]
    fn a_vector_s_job_says_whether_the_colour_space_set_is_unloaded() {
        let v = |job: &str| crate::json::parse(&format!(r#"{{"init": {{"job": {job}}}}}"#));
        // p1132 tx-formats-yuv-nocsc: no pokes
        assert!(super::job_csc_unloaded(&v(r#"{"pokes": [], "use_coeffs": {"load": false}}"#)));
        // the pokes of tx-formats-yuv-csc set the flag
        assert!(!super::job_csc_unloaded(&v(r#"{"pokes": ["xfer:17^=0x1", "xfer:18=0x00950095"]}"#)));
        assert!(!super::job_csc_unloaded(&v(r#"{"pokes": ["xfer:17=1"]}"#)));
        // set and flipped back, other words, other forms
        assert!(super::job_csc_unloaded(&v(r#"{"pokes": ["xfer:17=1", "xfer:17^=0x1", "xfer:18=5"]}"#)));
        assert!(super::job_csc_unloaded(&v(r#"{"pokes": ["xfer:17^=0x4"]}"#)));
        // a vector without its job: not known
        assert!(!super::job_csc_unloaded(&crate::json::parse(r#"{"init": {}}"#)));
    }

    #[test]
    fn a_vector_file_takes_its_jobs_from_the_sidecar() {
        // vectors.py jobs: vectors/jobs/<path>.job.json beside the files converted before
        // vectors carried their job; the vector files themselves are left as they were
        let d = std::env::temp_dir().join(format!("sgx-sim-jobs-{}", std::process::id()));
        let (vd, jd) = (d.join("vectors/usse/x"), d.join("vectors/jobs/usse/x"));
        std::fs::create_dir_all(&vd).unwrap();
        std::fs::create_dir_all(&jd).unwrap();
        std::fs::write(
            vd.join("t.vec.json"),
            r#"{"vectors": [{"id": "t__0", "init": {"temps": 8}}, {"id": "t__1", "init": {}}]}"#,
        )
        .unwrap();
        std::fs::write(
            jd.join("t.job.json"),
            r#"{"format": "sgx545-vector-jobs", "jobs": {"t__0": {"pokes": [],
                "use_coeffs": {"load": false}}}}"#,
        )
        .unwrap();
        let b = super::load(&vd.join("t.vec.json"));
        let vs = b.get("vectors").arr();
        assert_eq!(super::job_coeffs(&vs[0]), Some(crate::usse::FilterBlock::default()));
        assert_eq!(vs[0].get("init").get("temps").num(), Some(8.0));
        assert_eq!(super::job_coeffs(&vs[1]), None);
        // the sidecars are not vector files
        let files = super::probe_files(&d.join("vectors"));
        assert_eq!(files, vec![vd.join("t.vec.json")]);
        std::fs::remove_dir_all(&d).unwrap();
    }

    #[test]
    fn a_jump_out_of_the_program_matches_a_faulted_job() {
        // bra's target is 24 bits (pds-encoding-bits-flow-bra): one far past the program made
        // the hardware fetch unmapped memory, and the job faulted
        assert!(super::run_pds(&pds_vector("bra 0x80004", 0)).is_err());
        let failed = "\"job faulted, context lost (Input/output error)\"";
        let v = pds_vector_failed("bra 0x80004", 0, failed);
        assert_eq!(super::run_pds(&v), Ok(super::Outcome::Exact));
    }

    #[test]
    fn a_fetch_pc_read_matches_up_to_two_below() {
        // pc.0 at instruction 0 is modelled as 3; the hardware's 1 to 3 match as near values
        for got in [1, 2, 3] {
            let v = pds_vector("mov32 ds0[48], pc.0", got);
            assert_eq!(super::run_pds(&v), Ok(super::Outcome::Near));
        }
        assert!(super::run_pds(&pds_vector("mov32 ds0[48], pc.0", 4)).is_err());
        let e = super::run_pds(&pds_vector("add ds0[48], ds0[1], ds1[1]\nmov32 ds0[48], pc.0", 0));
        assert!(e.is_err());
    }

    #[test]
    fn a_fill_vector_is_one_tile_s_secondary_program() {
        // every tile of the 64 x 32 fill runs the program with its own ir0 (tile_y << 10 |
        // tile_x) and stores to the same scratch dwords: the readback is one tile's
        assert_eq!(super::run_pds(&ir0_vector(0x403)), Ok(super::Outcome::Exact));
        assert_eq!(super::run_pds(&ir0_vector(0x002)), Ok(super::Outcome::Exact));
        let e = super::run_pds(&ir0_vector(0x404)).unwrap_err();
        assert!(!e.starts_with("unsupported"), "{e}");
        // and says which tile's run matched: (0, 0) unless the readback needs another's ir0
        let exact = super::Outcome::Exact;
        assert_eq!(super::run_pds_tile_match(&ir0_vector(0x403)), Ok((exact, (3, 1))));
        assert_eq!(super::run_pds_tile_match(&ir0_vector(0)), Ok((exact, (0, 0))));
    }

    #[test]
    fn a_firmware_task_that_runs_out_of_steps_is_a_stop() {
        // a wrapper that never reaches its tail call must not be compared on a partial state
        let w = format!("\"0x{:016x}\"", usse_isa::encode("br #0x00000000", usse_isa::Core::Sgx545).unwrap());
        let v = crate::json::parse(&format!(
            r#"{{"program": {{"isa": "usse", "words": [{w}]}},
                "init": {{"task": "firmware", "page": {{"base": "0x32140000", "dwords": 8}},
                          "mem": {{}}, "regs": {{}}}},
                "readback": {{"mem": {{}}, "regs": {{}}}}}}"#
        ));
        let r = super::run_firmware(&v);
        assert!(r.as_ref().is_err_and(|e| e.starts_with("unsupported")), "{r:?}");
    }

    /// A firmware vector from instruction texts ending in the tail call, with the given
    /// `init` additions (a JSON object body, may be empty) and `readback.state` body.
    fn fw_vector(texts: &[&str], init_extra: &str, state_rb: &str) -> crate::json::Json {
        let words: Vec<String> = texts
            .iter()
            .map(|t| format!("\"0x{:016x}\"", usse_isa::encode(t, usse_isa::Core::Sgx545).expect(t)))
            .collect();
        crate::json::parse(&format!(
            r#"{{"program": {{"isa": "usse", "words": [{}]}},
                "init": {{"task": "firmware", "page": {{"base": "0x32140000", "dwords": 8}},
                          "mem": {{}}, "regs": {{}}{init_extra}}},
                "readback": {{"mem": {{}}, "regs": {{}}, "state": {{{state_rb}}}}}}}"#,
            words.join(", ")
        ))
    }

    #[test]
    fn a_firmware_task_starts_from_the_state_the_vector_gives_and_is_compared_on_what_it_left() {
        // E536: sa, r, i and p1 to p3 are what the task before left; the readback is what the task
        // leaves for the next one
        let init = r#", "state": {"sa": {"100": "0x0000a5a5"}, "r": {"20": "0x00000007"}, "p": {"1": "0x1"}}"#;
        let t = ["mov r2, sa100", "mov sa101, r2", "mov r21, r20", "lapc"];
        let ok = fw_vector(&t, init, r#""sa": {"101": "0x0000a5a5"}, "r": {"21": "0x00000007"}"#);
        assert_eq!(super::run_firmware(&ok), Ok(super::Outcome::Exact));
        let bad = fw_vector(&t, init, r#""sa": {"101": "0x00000001"}"#);
        assert!(super::run_firmware(&bad).is_err_and(|e| e.contains("sa101: want 0x1")));
        // a register the vector does not give is still the environment's: a stop
        let unseeded = fw_vector(&["mov r2, sa100", "lapc"], "", "");
        assert!(super::run_firmware(&unseeded).is_err_and(|e| e.starts_with("unsupported")));
    }

    #[test]
    fn the_temporaries_of_a_firmware_task_are_the_vectors_and_one_past_them_is_a_stop() {
        let t = ["mov r123, r0", "lapc"];
        let with = fw_vector(&t, r#", "temps": 124, "state": {"r": {"0": "0x0"}}"#, "");
        assert_eq!(super::run_firmware(&with), Ok(super::Outcome::Exact));
        let without = fw_vector(&t, r#", "state": {"r": {"0": "0x0"}}"#, "");
        assert!(super::run_firmware(&without).is_err_and(|e| e.starts_with("unsupported")));
    }

    #[test]
    fn a_read_of_sa64_after_the_task_wrote_it_is_a_stop_and_a_seeded_one_is_not() {
        // the hardware read 2, not the marker, at the next event (E536): what the task itself would
        // read back is not measured
        let init = r#", "state": {"sa": {"64": "0x00000002"}, "r": {"2": "0x00000009"}}"#;
        let after = fw_vector(&["mov sa64, r2", "mov r3, sa64", "lapc"], init, "");
        assert!(super::run_firmware(&after).is_err_and(|e| e.contains("sa64 after the task wrote it")));
        let seeded = fw_vector(&["mov r3, sa64", "lapc"], init, r#""r": {"3": "0x00000002"}"#);
        assert_eq!(super::run_firmware(&seeded), Ok(super::Outcome::Exact));
        let only_written = fw_vector(&["mov sa64, r2", "lapc"], init, "");
        assert_eq!(super::run_firmware(&only_written), Ok(super::Outcome::Exact));
    }

    #[test]
    fn a_state_key_that_is_not_a_register_is_a_stop_and_not_a_panic() {
        for init in [r#", "state": {"i": {"4": "0x0"}}"#, r#", "state": {"sa": {"128": "0x0"}}"#, r#", "state": {"p": {"x": "0x1"}}"#] {
            let v = fw_vector(&["lapc"], init, "");
            assert!(super::run_firmware(&v).is_err_and(|e| e.starts_with("unsupported: state key")), "{init}");
        }
        let v = fw_vector(&["lapc"], "", r#""i": {"7": "0x0"}"#);
        assert!(super::run_firmware(&v).is_err_and(|e| e.starts_with("unsupported: state key")));

    }

    #[test]
    fn a_timer_the_task_did_not_load_matches_as_any_value() {
        // Bound::Bits(25) admits every 25-bit value: such a match is counted apart, not as a
        // bounded near value (pds-timer-tim-words, pds_isa 8.9)
        for got in [0, 0x1ab_cdef] {
            let v = pds_vector("mov32 ds0[48], tim.0", got);
            assert_eq!(super::run_pds(&v), Ok(super::Outcome::AnyValue));
        }
        assert!(super::run_pds(&pds_vector("mov32 ds0[48], tim.0", 0x200_0000)).is_err());
        assert!(super::Outcome::AnyValue.is_near() && super::Outcome::Near.is_near());
        assert!(!super::Outcome::Exact.is_near());
    }

    #[test]
    fn a_raw_word_tests_the_form_it_decodes_to() {
        // usse-form-coverage-form2-test-e50 0: the form enc[50] selects has no text the
        // assembler takes, so the probe writes the word
        let op =
            "mov r16, #0\\n.long 0x4804188001570082 ; iadd32.testpat.chan0 r10, p0, r1, r2\\np0 mov r16, #1";
        let v = crate::json::parse(&format!(
            r#"{{"program": {{"isa": "usse"}}, "provenance": {{"inputs": {{"OP": "{op}"}}}}}}"#
        ));
        let form = usse_isa::decode_fields(0x4804188001570082, usse_isa::Core::Sgx545).unwrap().form;
        assert!(super::under_test(&v).contains(&form), "{form}: {:?}", super::under_test(&v));
    }

    #[test]
    fn a_triangle_host_vector_with_one_colour_is_not_the_shader_s() {
        // isp-stencil-st-front-never: on the triangle host the scene decides which pixels run
        // the slot's shader (a stencil that removes the triangle leaves the background
        // everywhere), so a uniform readback is not its output; a fill's is
        let tri = crate::json::parse(
            r#"{"program": {"isa": "usse"}, "init": {"pa0": "fill"}, "readback": {"o0": "0xff203040"},
                "provenance": {"options": ["--tri", "pixel", "--isp2", "0x000000ff"]}}"#,
        );
        assert_eq!(super::kind(&tri), super::Kind::None);
        let fill = crate::json::parse(
            r#"{"program": {"isa": "usse"}, "init": {"pa0": "fill"}, "readback": {"o0": "0x0000000a"},
                "provenance": {"options": ["--temps", "32"]}}"#,
        );
        assert_eq!(super::kind(&fill), super::Kind::Scalar);
    }

    #[test]
    fn the_skip_rows_of_the_unfenced_store_probes_apply() {
        assert!(
            super::skipped("usse/store-own2/x/raw.txt", "usse-store-own2-cross", "usse-store-own2-cross__5")
                .is_some()
        );
        // the other cases of the probe are replayed
        assert!(
            super::skipped("usse/store-own2/x/raw.txt", "usse-store-own2-cross", "usse-store-own2-cross__4")
                .is_none()
        );
    }
}
