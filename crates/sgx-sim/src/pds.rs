// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The PDS interpreter, over pds-isa's form table (each form's `op` and its
//! fields' roles in isa/pds/forms/).
//!
//! Semantics come from doc/specs/pds_isa.md only, most of them measured
//! (its section 8, the PDS vectors). What the reference leaves
//! open stops the program with [`Error::Unsupported`]: the meaning of most
//! ports (handed to the [`Bus`]), `load`/`store` and the fences, `if0`/`if1`
//! unless the task says, `mr01`/`mr23`, `pc` as a source, the specials other
//! than `ir0` in a `movs` and in `mov16`/`mov32`, the carry after a port
//! write and after `adc`/`sbc` under `alum signed` (the PDS vectors).

use crate::{Bound, Bus, Error};
use pds_isa::forms;
use usse_isa::form::Form;

/// The destinations of `movs`/`movsa` (`w[3:0]`), as pds-dis names them.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Port {
    Mr,
    Slc,
    Douti,
    Doutd,
    Doutt,
    Doutu,
    Douta,
    Tim,
    Doutc,
    Douts,
    Ir0,
}

impl Port {
    fn from_field(v: u32) -> Option<Port> {
        use Port::*;
        Some(match v {
            0 => Mr,
            1 => Slc,
            2 => Douti,
            3 => Doutd,
            4 => Doutt,
            5 => Doutu,
            6 => Douta,
            7 => Tim,
            8 => Doutc,
            9 => Douts,
            15 => Ir0,
            _ => return None,
        })
    }
}

#[derive(Clone)]
struct Insn {
    form: Option<&'static Form>,
    v: [u32; 10],
    text: String,
    /// A source index the decoder leaves undecoded (the role, its value): the word is decoded
    /// with that field read as 0 instead, and the source reads what the hardware read there
    /// (`raw_source`).
    raw: Option<(&'static str, u32)>,
}

impl Insn {
    fn get(&self, role: &str) -> u32 {
        let f = self.form.expect("a decoded instruction");
        f.role(role).map(|i| self.v[i]).unwrap_or_else(|| panic!("{}: no field {role}", f.op))
    }
}

/// A PDS program: its data segment and its instructions, decoded once.
pub struct Program {
    pub data: Vec<u32>,
    insns: Vec<Insn>,
}

impl Program {
    /// `words` is the whole program; the first `data` dwords are its data segment.
    pub fn new(words: &[u32], data: usize) -> Program {
        let forms: Vec<&'static Form> = forms().collect();
        let insns = words[data.min(words.len())..]
            .iter()
            .map(|&w| {
                let i = pds_isa::decode(w);
                match pds_isa::decode_fields(w) {
                    Some(f) => Insn { form: Some(forms[f.form]), v: f.v, text: i.text, raw: None },
                    None => match reread(w) {
                        Some((f, raw)) => {
                            Insn { form: Some(forms[f.form]), v: f.v, text: i.text, raw: Some(raw) }
                        }
                        None => Insn { form: None, v: [0; 10], text: i.text, raw: None },
                    },
                }
            })
            .collect();
        Program { data: words[..data.min(words.len())].to_vec(), insns }
    }

    pub fn len(&self) -> usize {
        self.insns.len()
    }

    pub fn is_empty(&self) -> bool {
        self.insns.is_empty()
    }

    /// The text of instruction `pc` (for traces).
    pub fn text(&self, pc: usize) -> Option<&str> {
        self.insns.get(pc).map(|i| i.text.as_str())
    }
}

/// A word whose source index the decoder leaves undecoded, decoded with that field 0, and
/// the field (role, value): the source sweeps of mov16, mov32, mov64, the ALU, mul and shl
/// (`pds-moves-index-*`, pds_isa 8.9). Other words stay undecoded.
fn reread(w: u32) -> Option<(usse_isa::form::Fields, (&'static str, u32))> {
    let (lo, width, role) = match w >> 27 {
        1 => (8, 9, "src"),
        2 => (9, 8, "src"),
        3 => (10, 7, "src"),
        8..=11 | 24..=26 | 28 | 29 => (17, 7, "src1"),
        12 => (16, 8, "src1"),
        30 => (16, 8, "src"),
        _ => return None,
    };
    let mask = ((1u32 << width) - 1) << lo;
    let f = pds_isa::decode_fields(w & !mask)?;
    Some((f, (role, (w & mask) >> lo)))
}

/// One PDS unit. The two banks persist from one task to the next, as on the
/// hardware (pds_isa 3.1); `known` says which dwords hold a value the
/// simulation knows: the data segment of the running program and what a
/// task wrote.
#[derive(Clone, Debug)]
pub struct Pds {
    pub ds: [[u32; 64]; 2],
    pub known: [u64; 2],
    /// ir0-ir2 and tim, when the task kind says what they hold.
    pub ir: [Option<u32>; 3],
    pub tim: Option<u32>,
    /// if0, if1, when the task kind says.
    pub ifs: [Option<bool>; 2],
    /// pc.0 reads the fetch pc, modelled as the instruction's index + 3, which the hardware
    /// gives up to 2 below (Bound::Lag; pds_isa 8.11). Off: pc is open.
    pub fetch_pc: bool,
    /// The bound of each dword that holds a near value (one read from the fetch pc, or
    /// computed from one: Derived); None for an exact one.
    pub near: [[Option<Bound>; 64]; 2],
    /// The bounds of each port write's four words, in the order of the writes (of this task).
    pub port_near: Vec<[Option<Bound>; 4]>,
    /// A timer the task did not load reads as any 25-bit value (Bound::Bits): EVENT_TIMER
    /// keeps bits 24-0, running or stopped by an earlier job (pds_isa 8.9). Off: tim is open.
    pub timer_any: bool,
    /// The running instruction's own state (what it has read, whether it moves).
    pub exec: Exec,
    /// What mov16/mov32's selector 1 (`ir1.0`) reads, when the task kind says: it is not
    /// always the ALU's ir1 (pds_isa 8.9).
    pub sel_ir1: Option<u32>,
    /// mr01 and mr23 (mov64's sources), when the task kind says.
    pub mr: Option<[u32; 4]>,
    /// `tstz` of source 65 (`ir1` by the decoder's name) tests whether `ir0` is 0, as measured
    /// in a fill's secondary, the primary pixel and the pixel-event programs (E262, E263); on
    /// for those task kinds only. That it reads `ir0` is inferred, and `tstn` of it was never
    /// measured: it stops (pds_isa 8.9).
    pub test65_is_ir0_zero: bool,
    /// Off by default: a `movs` reads specials 1 and 2 (`ir1.l`, `tim.l`) as the ALU reads
    /// `ir1` and `tim`. Measured to agree in a fill's secondary program (pds_isa 8.9); in the
    /// microkernel's event program the firmware's own fast paths need `ir1.l` to, and the
    /// `tim.l` it passes on is never read. Not measured in other tasks.
    pub alu_specials_in_movs: bool,
    pub p: [Option<bool>; 3],
    pub aluz: Option<bool>,
    pub alun: Option<bool>,
    /// The high dword `add`/`sub` leave (+1, 0, -1) for `adc`/`sbc`.
    pub carry: Option<i64>,
    pub signed: bool,
    /// The one return register (pds_isa 8.8).
    pub link: Option<usize>,
    pub pc: usize,
    pub steps: usize,
    /// Loaded dwords not yet in their registers: a load lands at the next rfence or rwfence,
    /// and is lost if none follows (hardware: pds-memory-mem, E143).
    pub pending: Vec<(usize, usize, u32)>,
    /// The dwords this task's stores wrote, and the first store's address: rwfence after a
    /// store faults, and stores totalling 2-4 dwords fault at the end (E143, E144).
    pub stored: (u32, u32),
    /// The ds0 pair (its even index) mov128 with lastpair (bit 15) writes to both halves of its row:
    /// the data-row pair the last mov32 or movs read from ds0 (pds-mov128-bit15-*, E379).
    /// None when no such read is known or an instruction not measured to keep it ran.
    pub pair15: Option<usize>,
}

impl Default for Pds {
    fn default() -> Pds {
        Pds {
            ds: [[0; 64]; 2],
            known: [0; 2],
            ir: [None; 3],
            tim: None,
            ifs: [None; 2],
            sel_ir1: None,
            mr: None,
            test65_is_ir0_zero: false,
            fetch_pc: false,
            timer_any: false,
            near: [[None; 64]; 2],
            port_near: Vec::new(),
            exec: Exec::default(),
            alu_specials_in_movs: false,
            p: [None; 3],
            aluz: None,
            alun: None,
            carry: None,
            signed: false,
            link: None,
            pc: 0,
            steps: 0,
            pending: Vec::new(),
            stored: (0, 0),
            pair15: None,
        }
    }
}

/// The running instruction's state: the bound of what it has read so far, and whether it
/// moves its source unchanged (a near value keeps its bound).
#[derive(Clone, Debug, Default)]
pub struct Exec {
    now: std::cell::Cell<Option<Bound>>,
    moving: bool,
}

enum Next {
    Step,
    Jump(usize),
    Halt,
}

/// What an instruction does to the ALU state it does not write: the flags
/// and the carry.
#[derive(PartialEq)]
enum Keeps {
    /// Measured to leave both, or flow control.
    Both,
    /// Not measured: both become unknown.
    Neither,
}

impl Pds {
    /// The PDS as a fill's secondary program sees it: neither if0 nor if1
    /// tests true (pds_isa 3.3).
    pub fn secondary() -> Pds {
        Pds { ifs: [Some(false); 2], ..Pds::default() }
    }

    /// The secondary program of a fill's tile (tile_x, tile_y), 16 x 16 tiles: ir0 is the
    /// tile position tile_y << 10 | tile_x; the ALU's ir1, mov32's selector 1 and mr01/mr23
    /// read 0; a movs reads ir1.l and tim.l as the ALU does and ir2.l (its special 3) as 0;
    /// pc.0 is the fetch pc; tim, unless the task loads it, any 25-bit value; tstz of
    /// source 65 tests ir0 for 0 (pds_isa 3.2, 8.9, 8.11). if0/if1 as secondary().
    pub fn fill_secondary(tile_x: u32, tile_y: u32) -> Pds {
        Pds {
            ir: [Some(tile_y << 10 | tile_x), Some(0), Some(0)],
            sel_ir1: Some(0),
            mr: Some([0; 4]),
            test65_is_ir0_zero: true,
            fetch_pc: true,
            timer_any: true,
            alu_specials_in_movs: true,
            ..Pds::secondary()
        }
    }

    /// Load `prog`'s data segment (rows of four dwords, two per bank: row r is
    /// ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1]) and reset the per-task state.
    /// The temporaries and the rows past the segment keep what earlier tasks
    /// left; only what the simulation itself put there is known.
    pub fn start(&mut self, prog: &Program) {
        for (i, &w) in prog.data.iter().enumerate() {
            let (b, n) = ((i >> 1) & 1, (i >> 2) * 2 + (i & 1));
            if n < 64 {
                self.ds[b][n] = w;
                self.known[b] |= 1 << n;
                self.near[b][n] = None;
            }
        }
        self.p = [None; 3];
        self.aluz = None;
        self.alun = None;
        self.carry = None;
        self.signed = false;
        self.link = None;
        self.pc = 0;
        self.steps = 0;
        self.pending.clear();
        self.stored = (0, 0);
        self.pair15 = None;
        self.port_near.clear();
    }

    /// What `insn` does to the pair mov128's lastpair flag (bit 15) reads (pds-mov128-bit15-*,
    /// E379). Only what the runs measured is modelled: a `mov32` from `ds0[2]` or `ds0[9]` and
    /// a `movs` from the `ds0` pair 2 or 6 name that pair; a `mov32` from `ds1[9]`, a `not` of a
    /// temporary (`ds0[48-55]` or `ds1[48-55]`), a `movs` from the temporary pair 50 and a
    /// `mov64` from `mr01` keep it. Any other instruction (a `movsa`, another row or pair, a
    /// `not` of a data row, `mr23`, a plain `mov128`, one its predicate skips) leaves it open.
    fn latch15(&self, insn: &Insn, op: &str, form_ds1: bool) -> Option<Option<usize>> {
        let open = Some(None);
        match op {
            "mov32" => match insn.get("src") as usize {
                n @ (2 | 9) => Some(Some(n & !1)),
                73 => None,
                _ => open,
            },
            "movs" => {
                let v = insn.get("srcs");
                let (pair, ir) = ((v >> 13 & 31) as usize * 2, v >> 18 & 1 != 0);
                match (ir, pair) {
                    (false, 2 | 6) => Some(Some(pair)),
                    (false, 50) => None,
                    _ => open,
                }
            }
            "not" => {
                let n = insn.get(if form_ds1 { "ds1" } else { "src" }) as usize;
                if (48..56).contains(&n) { None } else { open }
            }
            "mov64" if insn.get("src") == 64 => None,
            _ => open,
        }
    }

    /// Start `prog` and run it until `halt`.
    pub fn run(&mut self, prog: &Program, bus: &mut dyn Bus, max_steps: usize) -> Result<(), Error> {
        self.start(prog);
        loop {
            if self.steps >= max_steps {
                return Err(Error::StepLimit);
            }
            if self.step(prog, bus)? {
                return Ok(());
            }
        }
    }

    /// Run the instruction at `pc`: true after `halt`.
    pub fn step(&mut self, prog: &Program, bus: &mut dyn Bus) -> Result<bool, Error> {
        self.steps += 1;
        let pc = self.pc;
        let insn = prog.insns.get(pc).ok_or(Error::PcOutOfRange(pc))?;
        let next = self.exec(insn, bus).map_err(|e| match e {
            Error::Unsupported { why, .. } => Error::Unsupported { pc, text: insn.text.clone(), why },
            e => e,
        })?;
        match next {
            Next::Step => self.pc += 1,
            Next::Jump(t) => self.pc = t,
            // stores totalling 2-4 dwords fault on the first one's page once they have
            // landed (E144)
            Next::Halt if (2..=4).contains(&self.stored.0) => {
                return Err(Error::Fault(self.stored.1 & !0xfff));
            }
            Next::Halt => return Ok(true),
        }
        Ok(false)
    }

    fn exec(&mut self, insn: &Insn, bus: &mut dyn Bus) -> Result<Next, Error> {
        let Some(form) = insn.form else { return Err(why("undecoded")) };
        let op = form.op;
        self.exec.now.set(None);
        self.exec.moving = matches!(op, "mov32" | "mov64" | "mov128");
        // load, store and the fences have no predicate; nop has none either
        if form.role("pred").is_some() && !self.pred(insn.get("pred"))? {
            self.pair15 = None;
            return Ok(Next::Step);
        }
        // mov128's lastpair reads the pair as the instructions before it left it; a mov128
        // reads it first and leaves it open (not measured)
        if op != "mov128" {
            if let Some(l) = self.latch15(insn, op, form.role("ds1").is_some()) {
                self.pair15 = l;
            }
        }
        let keeps = match op {
            "movs" | "movsa" => {
                self.port(insn, op == "movsa", bus)?;
                // a port write keeps the flags and the carry (pds_isa 8.3, 8.5)
                Keeps::Both
            }
            "mov16" => {
                let (b, n) = (insn.get("bank") as usize, insn.get("dst") as usize);
                // a half of a read-only row lands in the temporary ds[48 + (n & 15)],
                // whose other half is kept (pds_isa 8.7)
                let d = if n >> 1 < 48 { 48 + (n >> 1 & 15) } else { n >> 1 };
                let h = match self.raw_source(insn, "src")? {
                    Some(x) => half(x, 0),
                    None => self.src9h(insn.get("src"))?,
                };
                let src_near = self.exec.now.take();
                let old = self.ds(b, d)?;
                let v = if n & 1 != 0 { old & 0xffff | h << 16 } else { old & 0xffff_0000 | h };
                // a near low half keeps its bound in the dword (the high half exact); a near
                // high half has none; an exact low half replaces the near one
                let bound = match (src_near, n & 1) {
                    (Some(b), 0) => Some(b),
                    (Some(_), _) => Some(Bound::Derived),
                    (None, 0) => None,
                    (None, _) => self.near[b][48 + (d & 15)],
                };
                self.put(b, d, v);
                self.near[b][48 + (d & 15)] = bound;
                Keeps::Both
            }
            "mov32" => {
                let v = match self.raw_source(insn, "src")? {
                    Some(x) => x,
                    None => self.src8(insn.get("src"))?,
                };
                self.put(insn.get("bank") as usize, insn.get("dst") as usize, v);
                Keeps::Both
            }
            "mov64" => {
                let s = insn.get("src");
                let pair = if let Some(x) = self.raw_source(insn, "src")? {
                    [x, x]
                } else if s >= 64 {
                    let mr = self.mr.ok_or_else(|| why("mr01/mr23 are open (pds_isa 7.4)"))?;
                    let k = if s == 64 { 0 } else { 2 };
                    [mr[k], mr[k + 1]]
                } else {
                    let (sb, sn) = ((s >> 5) as usize, (s & 31) as usize * 2);
                    [self.ds(sb, sn)?, self.ds(sb, sn + 1)?]
                };
                let (b, n) = (insn.get("bank") as usize, insn.get("dst") as usize * 2);
                self.put(b, n, pair[0]);
                self.put(b, n + 1, pair[1]);
                Keeps::Both
            }
            "mov128" => {
                // lastpair (bit 15) makes it write the ds0 pair the last mov32 or movs read
                // from a data row to both halves of its destination row, whatever its source
                // row, swap and other unmapped bits (pds-mov128-bit15-*, E379)
                let latched = self.pair15.take();
                if insn.get("lastpair") != 0 {
                    let p = latched.ok_or_else(|| {
                        why("mov128 with lastpair after an instruction not measured to name or \
                             keep the pair is open (pds_isa 8.13)")
                    })?;
                    let pair = [self.ds(0, p)?, self.ds(0, p + 1)?];
                    let d = insn.get("dst") as usize * 2;
                    for (k, v) in [pair[0], pair[1], pair[0], pair[1]].into_iter().enumerate() {
                        self.put(k >> 1, d + (k & 1), v);
                    }
                    return Ok(Next::Step);
                }
                let s = insn.get("src") as usize * 2;
                let mut row = [self.ds(0, s)?, self.ds(0, s + 1)?, self.ds(1, s)?, self.ds(1, s + 1)?];
                if insn.get("swap") != 0 {
                    row = [row[2], row[3], row[0], row[1]];
                }
                let d = insn.get("dst") as usize * 2;
                for (k, v) in row.into_iter().enumerate() {
                    self.put(k >> 1, d + (k & 1), v);
                }
                Keeps::Both
            }
            // hardware (pds-memory-mem to pds-memory-mem6, E143, E144): load and store move 1-8 dwords
            // between the dword address and ds<bank>[48+]; a load's dwords land only at the
            // next fence, a store writes the registers as they are at once
            "load" | "store" => {
                let (addr, b, r) = (insn.get("addr") * 4, insn.get("bank") as usize, insn.get("range"));
                let (first, n) = (48 + (r & 15) as usize, ((r >> 4) + 7 & 7) as usize + 1);
                if first + n > 64 {
                    return Err(why("a load or store past ds[63]"));
                }
                if op == "load" {
                    for k in 0..n {
                        let v = bus.load32(addr + 4 * k as u32)?;
                        self.pending.push((b, first + k, v));
                    }
                } else {
                    for k in 0..n {
                        bus.store32(addr + 4 * k as u32, self.ds(b, first + k)?)?;
                    }
                    if self.stored.0 == 0 {
                        self.stored.1 = addr;
                    }
                    self.stored.0 += n as u32;
                }
                Keeps::Both
            }
            "fence" => {
                // rwfence after a store faults on page 0 (E143, E144)
                if insn.get("op") == 1 && self.stored.0 > 0 {
                    return Err(Error::Fault(0));
                }
                for (b, n, v) in std::mem::take(&mut self.pending) {
                    self.put(b, n, v);
                }
                Keeps::Both
            }
            "alu" => self.alu(insn)?,
            "mul" => {
                let x = match self.raw_source(insn, "src1")? {
                    Some(x) => x,
                    None => self.mula(insn.get("src1"))?,
                };
                let y = self.half1(insn.get("src2"))?;
                let r = if self.signed {
                    ((x as u16 as i16 as i32) * (y as u16 as i16 as i32)) as u32
                } else {
                    x.wrapping_mul(y)
                };
                self.dst7(insn.get("dst"), r);
                // mul sets the flags from its result and keeps the carry (pds_isa 8.3)
                self.set_flags(r);
                Keeps::Both
            }
            "abs" | "not" => {
                let x = match form.role("ds1") {
                    Some(_) => self.ds(1, insn.get("ds1") as usize)?,
                    None if op == "abs" => self.src7(insn.get("src"), 2)?,
                    None => self.src7(insn.get("src"), 3)?,
                };
                let r = match op {
                    "not" => !x,
                    _ if self.signed => (x as i32).wrapping_abs() as u32,
                    _ => x,
                };
                self.dst7(insn.get("dst"), r);
                Keeps::Both
            }
            "tstz" | "tstn" => {
                let x = match form.role("ds1") {
                    Some(_) => self.ds(1, insn.get("ds1") as usize)?,
                    // a test's source 65 (ir1 by the decoder's name): tstz of it is true
                    // exactly where ir0 is 0 in a fill, the pixel-event and the primary pixel
                    // programs (pds-task-inputs-*, E262, E263, pds_isa 8.9); tstn of it, and
                    // other tasks (the microkernel's event program), are open
                    None if insn.get("src") == 65 => {
                        if op != "tstz" || !self.test65_is_ir0_zero {
                            return Err(why("tstn of source 65, or a test of it in this task, is open"));
                        }
                        self.input(0)?
                    }
                    None => self.src7(insn.get("src"), 2)?,
                };
                let p = insn.get("pdst") as usize;
                if p > 2 {
                    return Err(why(format!("tst writes no predicate with pdst {p}")));
                }
                self.p[p] = match self.exec.now.get() {
                    Some(_) => None,
                    None => Some(if op == "tstz" { x == 0 } else { x >> 31 != 0 }),
                };
                Keeps::Both
            }
            "shl" | "shr" => {
                let x = match self.raw_source(insn, "src")? {
                    Some(x) => x,
                    None => self.shsrc(insn.get("src"))?,
                };
                // the amount is the 7-bit field unsigned; 32 and up give 0 (pds_isa 8.4)
                let n = insn.get("n");
                let r = match (op, self.signed) {
                    ("shl", _) => x.checked_shl(n).unwrap_or(0),
                    (_, false) => x.checked_shr(n).unwrap_or(0),
                    // an arithmetic shr by 32 or more fills with the sign (pds_isa 8.4)
                    (_, true) => ((x as i32) >> n.min(31)) as u32,
                };
                self.dst7(insn.get("dst"), r);
                Keeps::Both
            }
            "alum" => {
                self.signed = insn.get("mode") != 0;
                Keeps::Both
            }
            "bra" => return Ok(Next::Jump(insn.get("target") as usize)),
            "call" => {
                self.link = Some(self.pc + 1);
                return Ok(Next::Jump(insn.get("target") as usize));
            }
            "rtn" => return self.link.map(Next::Jump).ok_or_else(|| why("rtn before any call")),
            "halt" => return Ok(Next::Halt),
            "nop" => Keeps::Both,
            _ => return Err(why(format!("no semantics for {op:?}"))),
        };
        if keeps == Keeps::Neither {
            self.carry = None;
            (self.aluz, self.alun) = (None, None);
        }
        Ok(Next::Step)
    }

    /// aluz is a zero result; alun a negative one under alum signed only (pds_isa 8.3).
    fn set_flags(&mut self, r: u32) {
        if self.exec.now.get().is_some() {
            // from a near value: not known
            (self.aluz, self.alun) = (None, None);
            return;
        }
        self.aluz = Some(r == 0);
        self.alun = Some(self.signed && r >> 31 != 0);
    }

    /// The two-source group: add and sub are modular and set the flags and
    /// the carry; adc and sbc add that carry; the logic ops are as named.
    fn alu(&mut self, insn: &Insn) -> Result<Keeps, Error> {
        let x = match self.raw_source(insn, "src1")? {
            Some(x) => x,
            None => self.src7(insn.get("src1"), 3)?,
        };
        let nx = self.exec.now.take();
        let y = self.ds(1, insn.get("src2") as usize)?;
        let ny = self.exec.now.take();
        let (a, b) = (x as i64, y as i64);
        let name = ALU_OPS.iter().find(|(o, _)| *o == insn.get("op")).map(|(_, n)| *n).unwrap_or("");
        // a near operand with an exact 0 that leaves it unchanged keeps its bound
        let bound = match (nx, ny) {
            (None, None) => None,
            (Some(b), None) if y == 0 && matches!(name, "or" | "xor" | "add" | "sub") => Some(b),
            (None, Some(b)) if x == 0 && matches!(name, "or" | "xor" | "add") => Some(b),
            _ => Some(Bound::Derived),
        };
        self.exec.now.set(bound);
        self.exec.moving = true;
        let (r, keeps) = match name {
            "add" | "sub" => {
                let exact = if name == "add" { a + b } else { a - b };
                let r = exact as u32;
                // the high dword of the exact result; under alum signed the
                // signed overflow, exact = signed(r) + c * 2^32 (pds_isa 8.5)
                self.carry = Some(if self.signed {
                    let (sa, sb) = (x as i32 as i64, y as i32 as i64);
                    let e = if name == "add" { sa + sb } else { sa - sb };
                    (e - r as i32 as i64) >> 32
                } else {
                    exact >> 32
                });
                self.set_flags(r);
                if self.exec.now.get().is_some() {
                    self.carry = None;
                }
                self.dst7(insn.get("dst"), r);
                return Ok(Keeps::Both);
            }
            "adc" | "sbc" => {
                let c =
                    self.carry.ok_or_else(|| why(format!("{name} before an add or sub set the carry")))?;
                let exact = if name == "adc" { a + b + c } else { a - b + c };
                // they set the flags from their result (pds_isa 8.3) and leave its high
                // dword, or under alum signed the signed overflow, as add/sub (pds_isa 8.5)
                self.set_flags(exact as u32);
                self.carry = Some(if self.signed {
                    let (sa, sb) = (x as i32 as i64, y as i32 as i64);
                    let e = if name == "adc" { sa + sb + c } else { sa - sb + c };
                    (e - exact as u32 as i32 as i64) >> 32
                } else {
                    exact >> 32
                });
                self.dst7(insn.get("dst"), exact as u32);
                return Ok(Keeps::Both);
            }
            // the logic ops keep the flags and the carry (pds_isa 8.3, 8.5)
            "and" => (x & y, Keeps::Both),
            "xor" => (x ^ y, Keeps::Both),
            "or" => (x | y, Keeps::Both),
            "nor" => (!(x | y), Keeps::Both),
            "nand" => (!(x & y), Keeps::Both),
            _ => return Err(why(format!("ALU opcode {}", insn.get("op")))),
        };
        self.dst7(insn.get("dst"), r);
        Ok(keeps)
    }

    /// `movs`/`movsa`: the four words, in operand order, to the bus. `movsa`
    /// adds the third word to a `doutd` address.
    fn port(&mut self, insn: &Insn, add: bool, bus: &mut dyn Bus) -> Result<(), Error> {
        let v = insn.get("srcs");
        let (b1, b0, ir) = ((v >> 8 & 31) as usize * 2, (v >> 13 & 31) as usize, v >> 18 & 1 != 0);
        let mut w = [0u32; 4];
        let mut near = [None; 4];
        for (k, word) in w.iter_mut().enumerate() {
            self.exec.now.set(None);
            let slot = 3 - k;
            let (sel, hi) = (v >> (2 * slot) & 3, (v >> (2 * slot) & 1) as usize);
            *word = if sel & 2 != 0 {
                self.ds(1, b1 + hi)?
            } else if ir {
                // the specials are 64-bit pairs like ds0's: .l the low word, .h the
                // high one, which read 0; special 0 .l is ir0 (pds_isa 8.9)
                match (b0, hi) {
                    (_, 1) => 0,
                    (0, _) => self.ir[0].ok_or_else(|| why("ir0 is not known for this task"))?,
                    (1, _) if self.alu_specials_in_movs => self.input(1)?,
                    (2, _) if self.alu_specials_in_movs => self.timer()?,
                    (3, _) if self.ir[2].is_some() => self.input(2)?,
                    _ => {
                        let name = ["ir0", "ir1", "tim", "ir2"].get(b0).unwrap_or(&"?");
                        return Err(why(format!("{name}.l as a movs source is open (pds_isa 7.9)")));
                    }
                }
            } else {
                self.ds(0, b0 * 2 + hi)?
            };
            near[k] = self.exec.now.get();
        }
        self.port_near.push(near);
        let port = Port::from_field(insn.get("port")).ok_or_else(|| why("reserved port"))?;
        if add {
            if port != Port::Doutd {
                return Err(why(format!("movsa to {port:?} is open (pds_isa 7.1)")));
            }
            w[0] = w[0].wrapping_add(w[2]);
        }
        if port == Port::Tim {
            // the first word's bits 24-0 load the counter; bit 24 set keeps it running,
            // so its value is then unknown (pds_isa 8.9, pds-timer-tim-words)
            self.tim = (w[0] >> 24 & 1 == 0).then_some(w[0] & 0x01ff_ffff);
        }
        bus.port(port, w)
    }

    fn pred(&self, p: u32) -> Result<bool, Error> {
        let known =
            |v: Option<bool>, name: &str| v.ok_or_else(|| why(format!("({name}) before it is known")));
        match p {
            0..=2 => known(self.p[p as usize], ["p0", "p1", "p2"][p as usize]),
            3 | 4 => known(self.ifs[p as usize - 3], ["if0", "if1"][p as usize - 3])
                .map_err(|_| why("if0/if1 are open for this task (pds_isa 7.2)")),
            5 => known(self.aluz, "aluz"),
            6 => known(self.alun, "alun"),
            _ => Ok(true),
        }
    }

    /// dsB[n], if known.
    fn ds(&self, b: usize, n: usize) -> Result<u32, Error> {
        if n >= 64 || self.known[b] >> n & 1 == 0 {
            return Err(why(format!("reads ds{b}[{n}] before the program writes it")));
        }
        if let Some(x) = self.near[b][n] {
            self.note(x);
        }
        Ok(self.ds[b][n])
    }

    /// The running instruction reads a near value: a second one makes it Derived.
    fn note(&self, b: Bound) {
        self.exec.now.set(Some(if self.exec.now.get().is_some() { Bound::Derived } else { b }));
    }

    /// A write to dsB[n] lands in the temporary dsB[48 + (n & 15)] (pds_isa 3.1).
    fn put(&mut self, b: usize, n: usize, v: u32) {
        let t = 48 + (n & 15);
        self.ds[b][t] = v;
        self.known[b] |= 1 << t;
        let now = self.exec.now.get();
        self.near[b][t] = if self.exec.moving { now } else { now.map(|_| Bound::Derived) };
    }

    /// A seven-bit destination: ds0[0-63], then ds1[0-63].
    fn dst7(&mut self, v: u32, x: u32) {
        self.put((v >> 6 & 1) as usize, (v & 63) as usize, x);
    }

    fn input(&self, i: usize) -> Result<u32, Error> {
        self.ir[i].ok_or_else(|| why(format!("ir{i} is not known for this task")))
    }

    fn timer(&self) -> Result<u32, Error> {
        match self.tim {
            Some(t) => Ok(t),
            None if self.timer_any => {
                self.note(Bound::Bits(25));
                Ok(0)
            }
            None => Err(why("tim is not known for this task")),
        }
    }

    /// The specials of mov16 (`half`) and mov32 by their index k: selector k >> 1 over
    /// ir0, ir1, pc, tim, and bit 9 of the word (k & 1, spelled .0/.1), which mov32 does
    /// not decode and with which mov16 reads 0 (pds_isa 8.9, pds-x-index-*, tier H).
    /// ir1 here and pc (the fetch pc, its index + 1 to 3) are open.
    fn special_pc(&self, i: u32, half: bool) -> Result<u32, Error> {
        let j = match (half, i & 1) {
            (true, 1) => return Ok(0),
            _ => i & !1,
        };
        match j {
            0 => self.input(0),
            6 => self.timer(),
            2 => self.sel_ir1.ok_or_else(|| why("ir1 as a mov16/mov32 source is open (pds_isa 8.9)")),
            4 if self.fetch_pc => {
                self.note(Bound::Lag(2));
                Ok(self.pc as u32 + 3)
            }
            4 => Err(why("pc as a mov16/mov32 source (the fetch pc) is open (pds_isa 8.9)")),
            _ => Err(why(format!("special source {i}"))),
        }
    }

    /// What an undecoded source index reads (Program::new's reread): shl's 130 the counter,
    /// as its 66 through the ALU; every other one 0 (pds-moves-index-*, pds_isa 8.9). None for
    /// a decoded source.
    fn raw_source(&self, insn: &Insn, role: &str) -> Result<Option<u32>, Error> {
        match insn.raw {
            Some((r, v)) if r == role => {
                let op = insn.form.map_or("", |f| f.op);
                if op == "shr" {
                    return Err(why(format!("shr source {v} (not swept)")));
                }
                if op == "shl" && v == 130 { self.timer().map(Some) } else { Ok(Some(0)) }
            }
            _ => Ok(None),
        }
    }

    /// A seven-bit first source: ds0[0-63], then the first `n` of ir0, ir1, tim.
    fn src7(&self, v: u32, n: u32) -> Result<u32, Error> {
        match v {
            0..64 => self.ds(0, v as usize),
            64 | 65 if v - 64 < n => self.input((v - 64) as usize),
            66 if n == 3 => self.timer(),
            _ => Err(why(format!("source {v}"))),
        }
    }

    fn src8(&self, v: u32) -> Result<u32, Error> {
        if v < 128 { self.ds((v >> 6) as usize, (v & 63) as usize) } else { self.special_pc(v - 128, false) }
    }

    fn src9h(&self, v: u32) -> Result<u32, Error> {
        let r = v >> 1;
        let x = if r < 128 {
            self.ds((r >> 6) as usize, (r & 63) as usize)?
        } else {
            self.special_pc(r - 128, true)?
        };
        // the .h of a lagging value below 0xfffd is 0 whatever the lag
        if v & 1 != 0 && matches!(self.exec.now.get(), Some(Bound::Lag(n)) if x < 0x1_0000 - n) {
            self.exec.now.set(None);
        }
        Ok(half(x, v))
    }

    /// mul's first source: halves of ds0, then of ir0, ir1, tim.
    fn mula(&self, v: u32) -> Result<u32, Error> {
        let x = match v >> 1 {
            r @ 0..64 => self.ds(0, r as usize)?,
            64 | 65 => self.input((v >> 1) as usize - 64)?,
            66 => self.timer()?,
            _ => return Err(why(format!("mul source {v}"))),
        };
        Ok(half(x, v))
    }

    fn half1(&self, v: u32) -> Result<u32, Error> {
        Ok(half(self.ds(1, (v >> 1) as usize)?, v))
    }

    /// shl/shr source: ds0/ds1, then ir0, ir1.
    fn shsrc(&self, v: u32) -> Result<u32, Error> {
        match v {
            0..128 => self.ds((v >> 6) as usize, (v & 63) as usize),
            128 | 129 => self.input((v - 128) as usize),
            _ => Err(why(format!("shift source {v}"))),
        }
    }
}

const ALU_OPS: &[(u32, &str)] = &[
    (8, "add"),
    (9, "sub"),
    (10, "adc"),
    (11, "sbc"),
    (24, "or"),
    (25, "and"),
    (26, "xor"),
    (28, "nor"),
    (29, "nand"),
];

/// The low (bit 0 of `sel` clear) or high 16 bits of `x`.
fn half(x: u32, sel: u32) -> u32 {
    if sel & 1 != 0 { x >> 16 } else { x & 0xffff }
}

fn why(s: impl Into<String>) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: s.into() }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The port writes a program makes; no memory.
    #[derive(Default)]
    struct Ports(Vec<(Port, [u32; 4])>);

    impl Bus for Ports {
        fn load32(&mut self, a: u32) -> Result<u32, Error> {
            Err(Error::Fault(a))
        }
        fn store32(&mut self, a: u32, _: u32) -> Result<(), Error> {
            Err(Error::Fault(a))
        }
        fn port(&mut self, port: Port, words: [u32; 4]) -> Result<(), Error> {
            self.0.push((port, words));
            Ok(())
        }
    }

    fn prog(data: &[u32], src: &str) -> Program {
        let mut w = data.to_vec();
        for line in src.lines().map(str::trim).filter(|l| !l.is_empty()) {
            w.push(pds_isa::encode(line).unwrap_or_else(|| panic!("{line}")));
        }
        Program::new(&w, data.len())
    }

    /// Run `src` with the data segment `data` (one row: ds0[0], ds0[1],
    /// ds1[0], ds1[1] and so on) on a secondary-program PDS.
    fn run(data: &[u32], src: &str) -> Result<(Pds, Ports), Error> {
        let (mut m, mut bus) = (Pds::secondary(), Ports::default());
        m.run(&prog(data, src), &mut bus, 1000)?;
        Ok((m, bus))
    }

    fn why_of(r: Result<(Pds, Ports), Error>) -> String {
        match r {
            Err(Error::Unsupported { why, .. }) => why,
            Err(e) => panic!("{e}"),
            Ok(_) => panic!("ran"),
        }
    }

    #[test]
    fn data_rows_interleave_the_banks() {
        // dwords 0-3 are ds0[0], ds0[1], ds1[0], ds1[1]; 4-7 ds0[2], ds0[3], ...
        let (m, bus) =
            run(&[1, 2, 3, 4, 5, 6, 7, 8], "movs douta, ds0[2], ds0[3], ds1[2], ds1[3]\nhalt").unwrap();
        assert_eq!(bus.0, vec![(Port::Douta, [5, 6, 7, 8])]);
        assert_eq!((m.ds[0][1], m.ds[1][1]), (2, 4));
    }

    #[test]
    fn writes_land_in_the_temporaries() {
        // a write to dsB[n] lands in dsB[48 + (n & 15)] (pds_isa 3.1)
        let (m, _) = run(&[7, 0, 9, 0], "mov32 ds1[1], ds0[0]\nmov32 ds0[36], ds1[0]\nhalt").unwrap();
        assert_eq!((m.ds[1][49], m.ds[0][52], m.ds[1][1]), (7, 9, 0));
    }

    #[test]
    fn unwritten_registers_are_unknown() {
        assert!(why_of(run(&[0; 4], "mov32 ds0[48], ds0[60]\nhalt")).contains("ds0[60]"));
        // past the data segment too
        assert!(why_of(run(&[0; 4], "mov32 ds0[48], ds0[2]\nhalt")).contains("ds0[2]"));
    }

    #[test]
    fn temporaries_persist_between_tasks() {
        let (mut m, mut bus) = (Pds::secondary(), Ports::default());
        m.run(&prog(&[5, 0, 0, 0], "mov32 ds0[60], ds0[0]\nhalt"), &mut bus, 100).unwrap();
        m.run(&prog(&[0; 4], "mov32 ds0[48], ds0[60]\nhalt"), &mut bus, 100).unwrap();
        assert_eq!(m.ds[0][48], 5);
    }

    #[test]
    fn add_sub_are_modular_and_set_the_flags() {
        let (m, _) =
            run(&[0xffff_ffff, 3, 1, 3], "add ds0[48], ds0[0], ds1[0]\nsub ds0[49], ds0[1], ds1[1]\nhalt")
                .unwrap();
        assert_eq!((m.ds[0][48], m.ds[0][49]), (0, 0));
        assert_eq!((m.aluz, m.alun), (Some(true), Some(false)));
    }

    #[test]
    fn alun_needs_alum_signed() {
        let src = "sub ds0[48], ds0[0], ds1[0]\n(alun) mov32 ds0[49], ds1[0]\nhalt";
        let (m, _) = run(&[1, 0, 2, 0], src).unwrap();
        assert_eq!(m.known[0] >> 49 & 1, 0);
        let (m, _) = run(&[1, 0, 2, 0], &format!("alum signed\n{src}")).unwrap();
        assert_eq!(m.ds[0][49], 2);
    }

    #[test]
    fn adc_and_sbc_add_the_high_dword() {
        // 0xffffffff + 1 carries (+1); 0 - 1 borrows (-1): adc adds it, sbc too
        let (m, _) = run(
            &[0xffff_ffff, 5, 1, 2],
            "add ds0[48], ds0[0], ds1[0]\nadc ds0[49], ds0[1], ds1[1]\n\
             sub ds0[51], ds0[48], ds1[0]\nsbc ds0[52], ds0[1], ds1[1]\nhalt",
        )
        .unwrap();
        assert_eq!((m.ds[0][48], m.ds[0][49]), (0, 8));
        assert_eq!((m.ds[0][51], m.ds[0][52]), (0xffff_ffff, 2));
        assert!(why_of(run(&[0; 4], "adc ds0[48], ds0[0], ds1[0]\nhalt")).contains("carry"));
    }

    #[test]
    fn logic_ops_and_the_flags_they_keep() {
        let (m, _) = run(
            &[0xf0f0, 0, 0xff00, 0],
            "and ds0[48], ds0[0], ds1[0]\nxor ds0[49], ds0[0], ds1[0]\n\
             nor ds0[50], ds0[0], ds1[0]\nnand ds0[51], ds0[0], ds1[0]\nhalt",
        )
        .unwrap();
        assert_eq!(&m.ds[0][48..52], &[0xf000, 0x0ff0, !0xfff0, !0xf000]);
        let (m, _) =
            run(&[0, 0, 0, 0], "sub ds0[60], ds0[0], ds1[0]\nand ds0[48], ds0[0], ds1[0]\nhalt").unwrap();
        assert_eq!(m.aluz, Some(true)); // and keeps the flags (pds_isa 8.3)
        let (m, _) =
            run(&[0, 0, 0, 0], "sub ds0[60], ds0[0], ds1[0]\nor ds0[48], ds0[0], ds1[0]\nhalt").unwrap();
        assert_eq!(m.aluz, Some(true)); // so does or (pds_isa 8.3)
    }

    #[test]
    fn shifts_take_the_amount_unsigned() {
        let (m, _) = run(
            &[0x8000_0010, 0, 0, 0],
            "shl ds0[48], ds0[0], 4\nshr ds0[49], ds0[0], 4\nshl ds0[50], ds0[0], 32\n\
             shr ds0[51], ds0[0], 4294967295\nalum signed\nshr ds0[52], ds0[0], 4\nhalt",
        )
        .unwrap();
        assert_eq!(&m.ds[0][48..53], &[0x100, 0x0800_0001, 0, 0, 0xf800_0001]);
    }

    #[test]
    fn mul_multiplies_halves() {
        let src = "mul ds0[48], ds0[0].l, ds1[0].h\nhalt";
        let (m, _) = run(&[0xffff, 0, 0x0002_0000, 0], src).unwrap();
        assert_eq!(m.ds[0][48], 0x1fffe);
        let (m, _) = run(&[0xffff, 0, 0x0002_0000, 0], &format!("alum signed\n{src}")).unwrap();
        assert_eq!(m.ds[0][48], (-2i32) as u32);
    }

    #[test]
    fn abs_is_the_identity_unless_signed() {
        let src = "abs ds0[48], ds0[0]\nabs ds0[49], ds1[0]\nnot ds0[50], ds0[0]\nhalt";
        let d = [(-5i32) as u32, 0, 0x8000_0000, 0];
        let (m, _) = run(&d, src).unwrap();
        assert_eq!(&m.ds[0][48..51], &[(-5i32) as u32, 0x8000_0000, 4]);
        let (m, _) = run(&d, &format!("alum signed\n{src}")).unwrap();
        assert_eq!(&m.ds[0][48..50], &[5, 0x8000_0000]);
    }

    #[test]
    fn mov16_names_a_half() {
        // ds0[97] is the high half of ds0[48]; the low half is kept
        let (m, _) =
            run(&[0x1111_2222, 0, 0xaaaa_bbbb, 0], "mov32 ds0[48], ds0[0]\nmov16 ds0[97], ds1[0].l\nhalt")
                .unwrap();
        assert_eq!(m.ds[0][48], 0xbbbb_2222);
        assert!(why_of(run(&[0; 4], "mov16 ds0[96], ds1[0].l\nhalt")).contains("ds0[48]"));
        // a half of a read-only row lands in the temporary ds[48 + (n & 15)], whose other
        // half is kept (pds_isa 8.7)
        let (m, _) =
            run(&[0x1111_2222, 0, 0xaaaa_bbbb, 0], "mov32 ds0[49], ds0[0]\nmov16 ds0[35], ds1[0].l\nhalt")
                .unwrap();
        assert_eq!(m.ds[0][49], 0xbbbb_2222);
    }

    #[test]
    fn the_ops_tried_keep_or_set_the_flags_and_keep_the_carry() {
        // add carries out (+1); every op tried keeps it for the adc (pds_isa 8.5)
        for op in [
            "or ds0[50], ds0[0], ds1[0]",
            "nor ds0[50], ds0[0], ds1[0]",
            "nand ds0[50], ds0[0], ds1[0]",
            "shr ds0[50], ds0[0], 1",
            "abs ds0[50], ds0[0]",
            "mul ds0[50], ds0[0].l, ds1[0].l",
            "mov16 ds0[100], ds1[0].l",
            "tstn p0, ds0[0]",
            "and ds0[50], ds0[0], ds1[0]",
            "shl ds0[50], ds0[0], 1",
            "not ds0[50], ds0[0]",
            "mov32 ds0[50], ds0[0]",
            "mov64 ds0[50], ds0[0]",
            "mov128 ds[50], ds[0]",
            "tstz p0, ds0[0]",
            "alum unsigned",
            "nop",
        ] {
            let src = format!(
                "mov32 ds0[50], ds0[0]\nadd ds0[48], ds0[0], ds1[0]\n{op}\n\
                               adc ds0[49], ds0[1], ds1[1]\nhalt"
            );
            let (m, _) = run(&[0xffff_ffff, 0, 1, 0], &src).unwrap_or_else(|e| panic!("{op}: {e}"));
            assert_eq!(m.ds[0][49], 1, "{op}");
        }
        // the flags: kept by these, set from the result by mul, adc and sbc (pds_isa 8.3)
        for op in [
            "or ds0[50], ds0[1], ds1[0]",
            "nor ds0[50], ds0[0], ds1[0]",
            "nand ds0[50], ds0[1], ds1[0]",
            "shr ds0[50], ds1[0], 0",
            "abs ds0[50], ds1[0]",
            "mov16 ds0[100], ds1[0].l",
            "tstn p0, ds1[0]",
        ] {
            let src = format!("mov32 ds0[50], ds0[0]\nsub ds0[48], ds0[1], ds1[1]\n{op}\nhalt");
            let (m, _) = run(&[0xffff_ffff, 0, 1, 0], &src).unwrap_or_else(|e| panic!("{op}: {e}"));
            assert_eq!(m.aluz, Some(true), "{op} keeps aluz");
        }
        for op in
            ["mul ds0[50], ds0[0].l, ds1[0].l", "adc ds0[50], ds0[1], ds1[0]", "sbc ds0[50], ds0[1], ds1[0]"]
        {
            let src = format!("sub ds0[48], ds0[1], ds1[1]\n{op}\nhalt");
            let (m, _) = run(&[0xffff_ffff, 0, 1, 0], &src).unwrap_or_else(|e| panic!("{op}: {e}"));
            assert_eq!(m.aluz, Some(false), "{op} sets aluz from its nonzero result");
        }
        // alum keeps both (pds_isa 8.3)
        let (m, _) = run(&[0; 4], "sub ds0[48], ds0[1], ds1[1]\nalum signed\nhalt").unwrap();
        assert_eq!((m.aluz, m.carry), (Some(true), Some(0)));
    }

    #[test]
    fn round_three_flags_carry_and_shifts() {
        // mov64, mov128, alum and a port write keep the flags (pds_isa 8.3)
        for op in [
            "mov64 ds0[50], ds0[0]",
            "mov128 ds[50], ds[0]",
            "alum unsigned",
            "movs douta, ds0[0], ds1[0], ds0[0], ds0[0]",
        ] {
            let src = format!("sub ds0[48], ds0[1], ds1[1]\n{op}\nhalt");
            let (m, _) = run(&[5, 0, 1, 0], &src).unwrap_or_else(|e| panic!("{op}: {e}"));
            assert_eq!(m.aluz, Some(true), "{op}");
        }
        // adc/sbc leave the high dword of their exact result: ~0 + 0 + 1 carries again
        let (m, _) = run(
            &[0xffff_ffff, 0, 1, 0],
            "add ds0[48], ds0[0], ds1[0]\nadc ds0[49], ds0[0], ds1[1]\n\
                          adc ds0[50], ds0[1], ds1[1]\nhalt",
        )
        .unwrap();
        assert_eq!((m.ds[0][49], m.ds[0][50]), (0, 1));
        // under alum signed the carry is the overflow: exact = signed(r) + c * 2^32
        for (x, y, c) in [(0x7fff_ffffu32, 1u32, 1i64), (0xffff_ffff, 1, 0), (0x8000_0000, 0x8000_0000, -1)] {
            let (m, _) = run(&[x, 0, y, 0], "alum signed\nadd ds0[48], ds0[0], ds1[0]\nhalt").unwrap();
            assert_eq!(m.carry, Some(c), "{x:#x} + {y:#x}");
        }
        let (m, _) = run(&[0x8000_0000, 0, 1, 0], "alum signed\nsub ds0[48], ds0[0], ds1[0]\nhalt").unwrap();
        assert_eq!(m.carry, Some(-1));
        // an arithmetic shr by 32 or more fills with the sign (pds_isa 8.4)
        let (m, _) = run(
            &[0x8000_0001, 0x4000_0001, 0, 0],
            "alum signed\nshr ds0[48], ds0[0], 33\nshr ds0[49], ds0[1], 4294967295\nhalt",
        )
        .unwrap();
        assert_eq!((m.ds[0][48], m.ds[0][49]), (0xffff_ffff, 0));
    }

    #[test]
    fn round_four_carries_and_tests() {
        // a movs keeps the carry (pds_isa 8.5)
        let (m, _) = run(
            &[0xffff_ffff, 0, 1, 0],
            "add ds0[48], ds0[0], ds1[0]\nmovs douta, ds0[0], ds1[0], ds0[0], ds0[0]\n\
                          adc ds0[49], ds0[1], ds1[1]\nhalt",
        )
        .unwrap();
        assert_eq!(m.ds[0][49], 1);
        // under alum signed adc/sbc leave the signed overflow, as add/sub
        let (m, _) = run(
            &[0x7fff_ffff, 0, 0, 0],
            "alum signed\nadd ds0[48], ds0[1], ds1[1]\nadc ds0[49], ds0[0], ds1[0]\nhalt",
        )
        .unwrap();
        assert_eq!(m.carry, Some(0));
        let (m, _) = run(
            &[0x7fff_ffff, 0, 1, 0],
            "alum signed\nadd ds0[48], ds0[1], ds1[1]\nadc ds0[49], ds0[0], ds1[0]\nhalt",
        )
        .unwrap();
        assert_eq!((m.ds[0][49], m.carry), (0x8000_0000, Some(1)));
        // tstz of ir1 (source 65) is true where ir0 is 0, unlike the ALU's ir1, in the task
        // kinds measured (pds-task-inputs-*, E262, E263, pds_isa 8.9)
        for (ir0, p0) in [(1, false), (0, true)] {
            let mut m =
                Pds { ir: [Some(ir0), Some(0), Some(0)], test65_is_ir0_zero: true, ..Pds::secondary() };
            m.run(&prog(&[0; 4], "tstz p0, ir1\nhalt"), &mut Ports::default(), 10).unwrap();
            assert_eq!(m.p[0], Some(p0));
        }
        // tstn of it was never measured, and other tasks (the event program) stop
        let mut m = Pds { ir: [Some(0); 3], test65_is_ir0_zero: true, ..Pds::secondary() };
        let e = m.run(&prog(&[0; 4], "tstn p0, ir1\nhalt"), &mut Ports::default(), 10);
        assert!(matches!(e, Err(Error::Unsupported { .. })), "{e:?}");
        let mut m = Pds { ir: [Some(0), Some(0), Some(0)], ..Pds::secondary() };
        let e = m.run(&prog(&[0; 4], "tstz p0, ir1\nhalt"), &mut Ports::default(), 10);
        assert!(matches!(e, Err(Error::Unsupported { .. })), "{e:?}");
    }

    #[test]
    fn mov16_and_mov32_specials_by_index() {
        // mov32 does not decode bit 9 (ir0.1 reads ir0), mov16 reads 0 with it
        // (pds_isa 8.9, pds-x-index-*)
        let mut m =
            Pds { ir: [Some(0x0001_0402), Some(9), Some(11)], tim: Some(0x0090_a090), ..Pds::secondary() };
        m.run(
            &prog(
                &[0; 4],
                "mov32 ds0[48], ir0.1\nmov32 ds0[50], ds0[1]\nmov16 ds0[100], ir0.1.l\n\
                              mov16 ds0[101], ir0.0.h\nhalt",
            ),
            &mut Ports::default(),
            10,
        )
        .unwrap();
        assert_eq!((m.ds[0][48], m.ds[0][50]), (0x0001_0402, 0x0001_0000));
        // tim.0 reads the counter; ir1 and pc (the fetch pc) are open
        for src in
            ["mov32 ds0[48], ir1.1", "mov32 ds0[48], ir1.0", "mov32 ds0[48], pc.0", "mov16 ds0[96], ir1.0.l"]
        {
            let e = Pds { ir: [Some(1), Some(1), Some(1)], tim: Some(5), ..Pds::secondary() }.run(
                &prog(&[0; 4], &format!("{src}\nhalt")),
                &mut Ports::default(),
                10,
            );
            assert!(matches!(e, Err(Error::Unsupported { .. })), "{src}: {e:?}");
        }
    }

    #[test]
    fn movs_tim_loads_the_counter() {
        // the first word's bits 24-0; bit 24 clear: stopped, set: running, value unknown
        let (m, bus) = run(
            &[0xfe12_3456, 1, 2, 0],
            "movs tim, ds0[0], ds0[1], ds1[0], ds1[1]\n\
                                                      or ds0[48], tim, ds1[1]\nhalt",
        )
        .unwrap();
        assert_eq!((m.ds[0][48], m.tim), (0x0012_3456, Some(0x0012_3456)));
        // and the bus sees the write (EVENT_TIMER on an SGX)
        assert_eq!(bus.0, vec![(Port::Tim, [0xfe12_3456, 1, 2, 0])]);
        let (m, _) = run(&[0x0100_0010, 0, 0, 0], "movs tim, ds0[0], ds0[1], ds1[0], ds1[1]\nhalt").unwrap();
        assert_eq!(m.tim, None);
    }

    #[test]
    fn mov32_numbers_the_specials_its_own_way() {
        // only ir0 reads the same as through the ALU (pds_isa 8.9)
        let mut m = Pds::secondary();
        m.ir = [Some(7), Some(9), Some(11)];
        m.run(
            &prog(&[0; 4], "mov32 ds0[48], ir0.0\nor ds0[49], ir1, ds1[1]\nhalt"),
            &mut Ports::default(),
            10,
        )
        .unwrap();
        assert_eq!((m.ds[0][48], m.ds[0][49]), (7, 9));
        // mov32's ir0.1 is ir0 again (bit 9 not decoded, mov16_and_mov32_specials_by_index)
        let p = prog(&[0; 4], "mov32 ds0[48], ir0.1\nhalt");
        let mut m = Pds { ir: [Some(7), Some(9), Some(11)], ..Pds::secondary() };
        m.run(&p, &mut Ports::default(), 10).unwrap();
        assert_eq!(m.ds[0][48], 7);
    }

    #[test]
    fn movs_specials_like_the_alu_only_when_assumed() {
        // specials 1 and 2 (.l) read what the ALU reads as ir1 and tim: measured to agree in a
        // fill's secondary program (pds_isa 8.9), an assumption elsewhere
        let src = "movs douta, ir1.l, ds1[0], ir1.l, ir1.l\nmovs douta, tim.l, ds1[0], tim.l, tim.l\nhalt";
        let mut m = Pds { ir: [Some(1), Some(0x100), None], tim: Some(5), ..Pds::secondary() };
        assert!(matches!(
            m.run(&prog(&[0; 4], src), &mut Ports::default(), 10),
            Err(Error::Unsupported { .. })
        ));
        let mut m = Pds {
            ir: [Some(1), Some(0x100), None],
            tim: Some(5),
            alu_specials_in_movs: true,
            ..Pds::secondary()
        };
        let mut bus = Ports::default();
        m.run(&prog(&[0; 4], src), &mut bus, 10).unwrap();
        assert_eq!((bus.0[0].1[0], bus.0[1].1[0]), (0x100, 5));
    }

    #[test]
    fn movs_reads_the_specials_as_words() {
        // special 0 .l is ir0, all 32 bits; .h read 0 (pds_isa 8.9)
        let mut m = Pds::secondary();
        m.ir[0] = Some(0x0012_3456);
        let mut bus = Ports::default();
        m.run(&prog(&[0; 4], "movs douta, ir0.l, ds1[0], ir0.h, ir0.l\nhalt"), &mut bus, 10).unwrap();
        assert_eq!(bus.0, vec![(Port::Douta, [0x0012_3456, 0, 0, 0x0012_3456])]);
        // the others (ir1, tim, ir2 by the reference's names) are open
        assert!(why_of(run(&[0; 4], "movs douta, tim.l, ds1[0], tim.l, tim.l\nhalt")).contains("tim"));
    }

    #[test]
    fn mov128_lastpair_writes_the_pair_the_last_mov32_or_movs_read() {
        // hardware (pds-mov128-bit15-*, E379): mov128 ds[52], ds[4], lastpair writes the
        // data-row ds0 pair the last mov32 or movs read, to both halves, whatever its source
        let data = [
            0, 0, 0, 0, 0xa2, 0xa3, 0xb2, 0xb3, 0xa4, 0xa5, 0xb4, 0xb5, 0xa6, 0xa7, 0xb6, 0xb7, 0xa8, 0xa9,
            0xb8, 0xb9,
        ];
        let with = |src: &str| {
            let mut words = data.to_vec();
            for line in src.lines() {
                words.push(pds_isa::encode(line).unwrap_or_else(|| panic!("{line}")));
            }
            words.push(pds_isa::encode("mov128 ds[52], ds[4], lastpair").unwrap());
            words.push(pds_isa::encode("halt").unwrap());
            let mut m = Pds::fill_secondary(0, 0);
            m.run(&Program::new(&words, data.len()), &mut Ports::default(), 50).map(|_| m)
        };
        let pair = |src: &str| {
            let m = with(src).unwrap_or_else(|e| panic!("{src}: {e:?}"));
            assert_eq!(m.ds[0][52..54], m.ds[1][52..54], "{src}: both halves");
            m.ds[0][52..54].to_vec()
        };
        // a mov32 from ds0[9] and from ds0[2] name their pair; a mov32 from ds1[9] and a not of
        // a temporary, ds0 or ds1, keep it (the probe template, then each case's lines)
        assert_eq!(pair("mov32 ds0[48], ds0[9]\nmov32 ds1[48], ds1[9]\nnot ds0[48], ds0[48]"), [0xa8, 0xa9]);
        assert_eq!(
            pair(
                "mov32 ds1[55], ds1[9]\nmov32 ds0[48], ds0[9]\nnot ds1[55], ds1[55]\n\
                         not ds0[48], ds0[48]"
            ),
            [0xa8, 0xa9]
        );
        assert_eq!(pair("mov32 ds0[48], ds0[9]\nmov32 ds0[50], ds0[2]"), [0xa2, 0xa3]);
        // a movs to mr or douta from the pairs 2 and 6 names it; a movs from the temporary pair
        // 50 and a mov64 from mr01 keep it
        assert_eq!(pair("movs mr, ds0[2], ds0[3], ds1[2], ds1[3]\nmov64 ds0[48], mr01"), [0xa2, 0xa3]);
        assert_eq!(pair("movs douta, ds0[6], ds1[2], ds0[6], ds0[6]"), [0xa6, 0xa7]);
        assert_eq!(
            pair(
                "mov32 ds0[48], ds0[9]\nmov32 ds0[50], ds1[9]\n\
                         movs douta, ds0[50], ds1[2], ds0[50], ds0[50]"
            ),
            [0xa8, 0xa9]
        );
        // what no run measured stays open: a mov32 from another row or from another ds1 row, a
        // movsa, a movs from another temporary pair, a not of a data row or of another
        // temporary, a mov64 from mr23, a plain mov128, an add, and the first read
        for src in [
            "mov32 ds0[48], ds0[4]",
            "mov32 ds0[48], ds0[9]\nmov32 ds1[48], ds1[3]",
            "movsa doutd, ds0[6], ds1[2], ds0[6], ds0[6]",
            "mov32 ds0[52], ds0[2]\nmov32 ds0[48], ds0[9]\n\
             movs douta, ds0[52], ds1[2], ds0[52], ds0[52]",
            "mov32 ds0[48], ds0[9]\nnot ds0[48], ds0[6]",
            "mov32 ds0[48], ds0[9]\nnot ds1[48], ds1[6]",
            "mov32 ds1[56], ds1[9]\nmov32 ds0[48], ds0[9]\nnot ds1[48], ds1[56]",
            "movs mr, ds0[2], ds0[3], ds1[2], ds1[3]\nmov64 ds0[48], mr23",
            "mov32 ds0[48], ds0[9]\nmov128 ds[50], ds[2]",
            "mov32 ds0[48], ds0[9]\nadd ds0[49], ds0[48], ds1[2]",
            "nop",
        ] {
            let e = with(src);
            let open = matches!(e, Err(Error::Unsupported { ref why, .. }) if why.contains("lastpair"));
            assert!(open, "{src}: {e:?}");
        }
    }

    #[test]
    fn mov64_and_mov128_rows() {
        let d = [1, 2, 3, 4, 5, 6, 7, 8];
        let (m, _) = run(&d, "mov64 ds1[48], ds0[2]\nmov128 ds[50], ds[2], swap\nhalt").unwrap();
        assert_eq!(&m.ds[1][48..50], &[5, 6]);
        // the row ds0[2], ds0[3], ds1[2], ds1[3] = 5, 6, 7, 8 with its pairs swapped
        assert_eq!((&m.ds[0][50..52], &m.ds[1][50..52]), (&[7, 8][..], &[5, 6][..]));
    }

    #[test]
    fn tests_set_predicates_and_obey_theirs() {
        let (m, _) = run(
            &[0, 0x8000_0000, 1, 0],
            "tstz p0, ds0[0]\ntstn p1, ds0[1]\ntstz p2, ds1[0]\n(p2) tstz p0, ds1[0]\nhalt",
        )
        .unwrap();
        assert_eq!(m.p, [Some(true), Some(true), Some(false)]);
        assert!(why_of(run(&[0; 4], "(p0) halt")).contains("p0"));
    }

    #[test]
    fn flow_has_one_return_register() {
        // call f; halt; f: mov32; rtn
        let (m, _) = run(&[9, 0, 0, 0], "call 2\nhalt\nmov32 ds0[48], ds0[0]\nrtn").unwrap();
        assert_eq!((m.ds[0][48], m.pc), (9, 1));
        // a nested call's return loops: the job never ends (pds_isa 8.8)
        let p = prog(&[0; 4], "call 2\nhalt\ncall 4\nrtn\nrtn");
        assert_eq!(Pds::secondary().run(&p, &mut Ports::default(), 1000), Err(Error::StepLimit));
        // bra goes to the instruction index, both ways
        let (m, _) =
            run(&[3, 0, 1, 0], "mov32 ds0[48], ds0[0]\nsub ds0[48], ds0[48], ds1[0]\n(aluz) halt\nbra 1")
                .unwrap();
        assert_eq!(m.ds[0][48], 0);
    }

    #[test]
    fn movsa_adds_the_third_word_to_a_doutd_address() {
        let (_, bus) =
            run(&[0x1000, 7, 0, 0, 0, 0, 0x40, 0], "movsa doutd, ds0[0], ds0[1], ds1[2], ds1[2]\nhalt")
                .unwrap();
        assert_eq!(bus.0, vec![(Port::Doutd, [0x1040, 7, 0x40, 0x40])]);
        assert!(why_of(run(&[0; 8], "movsa douta, ds0[0], ds0[1], ds1[2], ds1[2]\nhalt")).contains("movsa"));
    }

    /// Memory of 0x500 dwords at 0x10000 (dword k holds 0xd000_0000 | k), and no ports.
    struct Mem(Vec<u32>);

    impl Bus for Mem {
        fn load32(&mut self, a: u32) -> Result<u32, Error> {
            self.0.get((a.wrapping_sub(0x10000) / 4) as usize).copied().ok_or(Error::Fault(a))
        }
        fn store32(&mut self, a: u32, v: u32) -> Result<(), Error> {
            let w = self.0.get_mut((a.wrapping_sub(0x10000) / 4) as usize).ok_or(Error::Fault(a))?;
            *w = v;
            Ok(())
        }
        fn port(&mut self, _: Port, _: [u32; 4]) -> Result<(), Error> {
            Ok(())
        }
    }

    /// ds0[50-55] written, for the stores of more than two dwords
    const FILL: &str = "mov32 ds0[50], ds0[2]\nmov32 ds0[51], ds0[2]\nmov32 ds0[52], ds0[2]\n\
                        mov32 ds0[53], ds0[2]\nmov32 ds0[54], ds0[2]\nmov32 ds0[55], ds0[2]\n";

    fn run_mem(src: &str) -> (Result<(), Error>, Pds, Mem) {
        let (mut m, mut bus) = (Pds::secondary(), Mem((0..0x500).map(|k| 0xd000_0000 | k).collect()));
        let pre = "mov32 ds0[48], ds0[2]\nmov32 ds0[49], ds0[3]\nmov32 ds1[48], ds1[2]\n";
        let r =
            m.run(&prog(&[0, 0, 0, 0, 0x11, 0x22, 0x99, 0xaa], &format!("{pre}{src}\nhalt")), &mut bus, 1000);
        (r, m, bus)
    }

    #[test]
    fn loads_land_at_a_fence_and_stores_at_once() {
        // hardware (pds-memory-mem, pds-memory-mem2, E143): a load's registers keep their old
        // values until rfence or rwfence, even 4 nops on and at the program's end
        let (r, m, _) = run_mem("load 0x00010008, ds0[48-49]\nnop\nnop\nnop\nnop");
        assert_eq!((r, m.ds[0][48], m.ds[0][49]), (Ok(()), 0x11, 0x22));
        for f in ["rfence", "rwfence"] {
            let (r, m, _) = run_mem(&format!("load 0x00010008, ds0[48-49]\n{f}"));
            assert_eq!((r, m.ds[0][48], m.ds[0][49]), (Ok(()), 0xd000_0002, 0xd000_0003), "{f}");
        }
        // a store takes the registers as they are: a load not yet fenced is not in them
        let (r, _, mem) = run_mem("load 0x00010008, ds0[48]\nstore 0x00010020, ds0[48]");
        assert_eq!((r, mem.0[8]), (Ok(()), 0x11));
        let (r, _, mem) = run_mem("load 0x00010008, ds0[48]\nrfence\nstore 0x00010020, ds0[48]");
        assert_eq!((r, mem.0[8]), (Ok(()), 0xd000_0002));
        // a load after a store reads the stored value
        let (r, m, _) = run_mem("store 0x00010020, ds1[48]\nload 0x00010020, ds0[48]\nrfence");
        assert_eq!((r, m.ds[0][48]), (Ok(()), 0x99));
        let fill: String = (50..56).map(|k| format!("mov32 ds0[{k}], ds0[2]\n")).collect();
        let (r, _, mem) = run_mem(&format!("{fill}store 0x00010000, ds0[48-55]"));
        assert_eq!(
            (r, &mem.0[..9]),
            (Ok(()), &[0x11, 0x22, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xd000_0008][..])
        );
    }

    #[test]
    fn stores_totalling_two_to_four_dwords_fault_after_landing() {
        // hardware (pds-memory-mem2 to pds-memory-mem5, E143, E144): a program whose stores total
        // 1 or 5 or more dwords completes, one whose stores total 2-4 faults at its end on the
        // first store's page, after every store has landed, however the dwords are split
        for (src, total) in [
            ("store 0x00011020, ds0[48-49]", 2),
            ("store 0x00010000, ds0[48-51]", 4),
            ("store 0x00010000, ds0[48-50]", 3),
            ("store 0x00010000, ds0[48]\nstore 0x00010004, ds0[49]", 2),
            ("store 0x00010000, ds0[48]\nrfence\nstore 0x00010004, ds0[49]", 2),
            ("store 0x00010000, ds0[48-49]\nstore 0x00010020, ds0[48]", 3),
        ] {
            let (r, _, mem) = run_mem(&format!("{FILL}{src}"));
            let page = if src.starts_with("store 0x00011020") { 0x11000 } else { 0x10000 };
            assert_eq!(r, Err(Error::Fault(page)), "{src}");
            let landed = mem.0.iter().enumerate().filter(|&(i, &w)| w != 0xd000_0000 | i as u32).count();
            assert_eq!(landed, total, "{src}");
        }
        for src in [
            "store 0x00010000, ds0[48]",
            "store 0x00010000, ds0[48-52]",
            "store 0x00010000, ds0[48-51]\nstore 0x00010020, ds0[48]",
            "store 0x00010000, ds0[48-55]\nstore 0x00010020, ds0[48-49]",
            "store 0x00010000, ds0[48-49]\nstore 0x00010020, ds0[48-55]",
        ] {
            assert_eq!(run_mem(&format!("{FILL}{src}")).0, Ok(()), "{src}");
        }
    }

    #[test]
    fn rwfence_after_a_store_faults_on_page_0() {
        // hardware (E143, E144): rwfence after any store faults on page 0, also with an rfence
        // or nops between; rwfence before a store, or with no store, completes; rfence does
        for src in [
            "store 0x00010000, ds0[48]\nrwfence",
            "store 0x00010000, ds0[48-55]\nrwfence",
            "store 0x00010000, ds0[48]\nrfence\nrwfence",
        ] {
            assert_eq!(run_mem(&format!("{FILL}{src}")).0, Err(Error::Fault(0)), "{src}");
        }
        for src in [
            "rwfence\nrwfence",
            "rwfence\nstore 0x00010000, ds0[48]",
            "store 0x00010000, ds0[48]\nrfence",
            "load 0x00010008, ds0[48]\nrwfence\nstore 0x00010000, ds0[48]",
        ] {
            assert_eq!(run_mem(&format!("{FILL}{src}")).0, Ok(()), "{src}");
        }
    }

    #[test]
    fn a_fill_tile_knows_its_inputs() {
        // a fill's secondary program: ir0 the tile position tile_y << 10 | tile_x, the ALU's
        // ir1 and mov32's ir1.0 0, mr01/mr23 0, movs ir1.l as the ALU's ir1 (pds_isa 3.2, 8.9)
        let mut m = Pds::fill_secondary(2, 1);
        let mut bus = Ports::default();
        let src = "or ds0[48], ir0, ds1[1]\nor ds0[49], ir1, ds1[1]\nmov32 ds0[50], ir1.0\n\
                   mov32 ds0[51], ir0.0\nmov64 ds0[52], mr01\n\
                   movs douta, ir1.l, ds1[0], ir1.h, ir1.l\nhalt";
        m.run(&prog(&[0, 0, 7, 0], src), &mut bus, 20).unwrap();
        assert_eq!(&m.ds[0][48..54], &[0x402, 0, 0, 0x402, 0, 0]);
        assert_eq!(bus.0, vec![(Port::Douta, [0, 7, 0, 0])]);
        // movs special 3 (ir2.l) reads 0 in a fill too (pds_isa 8.9)
        let mut bus = Ports::default();
        let src = "movs douta, ir2.l, ds1[0], ir2.h, ir2.l\nhalt";
        Pds::fill_secondary(1, 0).run(&prog(&[0, 0, 7, 0], src), &mut bus, 20).unwrap();
        assert_eq!(bus.0, vec![(Port::Douta, [0, 7, 0, 0])]);
        // what is open in a fill stays so: mov128 with bit 15 before any mov32 or movs from a
        // data row (pds_isa 8.13)
        let p = Program::new(&[0x2700_8868, pds_isa::encode("halt").unwrap()], 0);
        let e = Pds::fill_secondary(0, 0).run(&p, &mut Ports::default(), 10);
        let open = matches!(e, Err(Error::Unsupported { ref why, .. }) if why.contains("mov128"));
        assert!(open, "{e:?}");
    }

    #[test]
    fn source_indices_past_the_decoded_ones_read_0() {
        // hardware (pds-moves-index-*, pds_isa 8.9): the specials the decoder leaves undecoded
        // read 0: mov32 136-255, mov16 272-511, mov64 64-127, the ALU's first source 67-127,
        // mul's halves past tim, shl's past 130
        let words = [0x1701_1060u32, 0x0f01_2060, 0x1f01_a060, 0xc7a0_0430, 0x6790_2430, 0xf790_0030];
        let enc = |t: &str| pds_isa::encode(t).unwrap();
        for w in words {
            // ds0[48] starts as 0x12345678; each word writes ds0[48] (mov16: its low half)
            let mut words = vec![0x1234_5678u32];
            words.resize(20, 0);
            words.extend([enc("mov32 ds0[48], ds0[0]"), w, enc("halt")]);
            let p = Program::new(&words, 20);
            let mut m = Pds::secondary();
            m.run(&p, &mut Ports::default(), 10).unwrap_or_else(|e| panic!("{w:08x}: {e}"));
            let want = if w >> 27 == 1 { 0x1234_0000 } else { 0 };
            assert_eq!(m.ds[0][48], want, "{w:08x}");
        }
        // an index past the decoded ones does not hide another field's open value
        let p = Program::new(&[0, 0, 0, 0, 0xc7a0_0c30, enc("halt")], 4);
        assert!(matches!(
            Pds::secondary().run(&p, &mut Ports::default(), 10),
            Err(Error::Unsupported { .. })
        ));
    }

    #[test]
    fn pc_reads_the_fetch_pc_up_to_two_below() {
        // pc.0 is the fetch pc: the reading instruction's index plus 3, or plus 1 or 2 where
        // fetch fell behind (pds_isa 8.11, pds-fetch-pc-*): index + 3, near, Lag(2); moves keep
        // the bound, arithmetic on it has none, a port write carries it
        let mut m = Pds::fill_secondary(0, 0);
        let mut bus = Ports::default();
        let src = "mov32 ds0[50], ds0[0]\nmov32 ds0[48], pc.0\nmov32 ds1[48], ds0[48]\n\
                   mov16 ds0[100], pc.0.l\nmov16 ds0[101], pc.0.h\n\
                   movs douta, ds0[48], ds1[0], ds0[48], ds0[48]\n\
                   add ds0[49], ds0[48], ds1[1]\nhalt";
        m.run(&prog(&[0, 0, 0, 1], src), &mut bus, 20).unwrap();
        assert_eq!((m.ds[0][48], m.ds[1][48], m.ds[0][50]), (4, 4, 6));
        assert_eq!((m.near[0][48], m.near[1][48]), (Some(Bound::Lag(2)), Some(Bound::Lag(2))));
        // the .l half of a pc below 65536 lags as the dword does; its .h is 0, exactly
        assert_eq!(m.near[0][50], Some(Bound::Lag(2)));
        let lag = Some(Bound::Lag(2));
        assert_eq!(m.port_near, vec![[lag, None, lag, lag]]);
        assert_eq!((m.near[0][49], m.aluz), (Some(Bound::Derived), None));
        // a write of an exact value clears the bound; a task that does not say keeps pc open
        m.run(&prog(&[0, 0, 0, 0], "mov32 ds0[48], ds0[0]\nhalt"), &mut bus, 20).unwrap();
        assert_eq!(m.near[0][48], None);
        assert!(why_of(run(&[0; 4], "mov32 ds0[48], pc.0\nhalt")).contains("pc"));
    }

    #[test]
    fn a_fill_reads_an_unknown_timer_as_any_25_bit_value() {
        // EVENT_TIMER keeps bits 24-0 (pds_isa 8.9); running, or stopped by an earlier job, its
        // value is not the task's to know: a read is near, Bits(25); a move or an or with 0
        // keeps the bound, other arithmetic has none
        let mut m = Pds::fill_secondary(0, 0);
        let mut bus = Ports::default();
        let src = "mov32 ds0[48], tim.0\nor ds0[49], tim, ds1[1]\nadd ds0[50], tim, ds1[1]\n\
                   or ds1[50], ds0[49], ds1[1]\nnot ds0[51], tim\n\
                   movs douta, tim.l, ds1[0], tim.h, tim.l\nhalt";
        m.run(&prog(&[0, 0, 0, 0], src), &mut bus, 20).unwrap();
        let b = Some(Bound::Bits(25));
        assert_eq!(&m.near[0][48..52], &[b, b, b, Some(Bound::Derived)]);
        assert_eq!(m.near[1][50], b);
        assert_eq!(m.port_near, vec![[b, None, None, b]]);
        // a stopped timer the task loaded itself is exact
        let src = "movs tim, ds0[0], ds0[1], ds1[0], ds1[1]\nmov32 ds0[48], tim.0\nhalt";
        m.run(&prog(&[5, 0, 0, 0], src), &mut bus, 20).unwrap();
        assert_eq!((m.ds[0][48], m.near[0][48]), (5, None));
    }

    #[test]
    fn open_semantics_stop() {
        assert!(why_of(run(&[0; 4], "mov32 ds0[48], ir1.0\nhalt")).contains("ir1"));
        assert!(why_of(run(&[0; 4], "mov32 ds0[48], ir0.0\nhalt")).contains("ir0"));
        assert!(why_of(run(&[0; 4], "movs douta, ir0.l, ir0.l, ir0.l, ir0.l\nhalt")).contains("ir0"));
        let mut m = Pds::default();
        let p = prog(&[0; 4], "(if0) halt");
        assert!(matches!(m.run(&p, &mut Ports::default(), 10), Err(Error::Unsupported { .. })));
    }
}
