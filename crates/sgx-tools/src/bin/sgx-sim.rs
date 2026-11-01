// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! sgx-sim: run a USSE program on the simulator (crates/sgx-sim) and print what
//! it wrote, or run corpus vectors against their hardware readbacks.
//!
//!   sgx-sim [--core 540|545] [--set REG=VALUE]... [--temps N] [--max N]
//!           [--near] [--task pixel|vertex] [--trace | --quad X,Y] <program.s | program.bin | ->
//!   sgx-sim --pds [--data N] [--set REG=VALUE]... [--max N] [--trace]
//!           <program.s | program.bin | ->
//!   sgx-sim --vectors FILE.vec.json [--id ID]
//!
//! A program is assembly source (usse-asm's syntax) or, with the .bin suffix, raw
//! little-endian 64-bit words. It runs as one instance, or with --quad as the
//! 2x2 quad holding pixel (X, Y) with pa0 = (y << 16) | x in each instance.
//! Memory is the probe harness's scratch buffer: 64 KiB at 0x3e003000 filled
//! with 0xd0000000 | i, and a limm of 0x5cafnnnn loads its address + nnnn.
//! REG is rN, iN, paN, saN, oN, pN or pclink; VALUE is decimal or 0x-hex. The emits
//! (emitpix, emitvcbvtx, ...) are listed with their three source values. With
//! --near, the float functions the hardware gives only to a bound (frcp, fsin,
//! ...) give their nearest value, printed with "~ <bound>"; without it they
//! stop the program where the hardware is not exact.
//!
//! With --pds the program is a PDS program (pds-asm's syntax, or raw 32-bit
//! words with --data N data dwords first) run on one PDS (sgx_sim::pds): REG is
//! dsB[n] (a temporary or row the program may read), ir0-ir2, tim, if0 or if1,
//! which are unknown otherwise; port writes (movs) are listed with their words.

use sgx_sim::pds::{self, Pds, Port};
use sgx_sim::vectors::{self, SCRATCH_BASE, SCRATCH_DWORDS};
use sgx_sim::{Bus, Error, Machine, Memory, Program, run_quad};
use sgx_tools::asm::{Isa, PDS, assemble_hinted};
use std::fmt::Write as _;
use std::io::Read as _;
use std::process::ExitCode;
use usse_isa::{Core, decode, encode_with};

const USAGE: &str = "usage: sgx-sim [--core 540|545] [--set REG=VALUE]... [--temps N] [--max N]
               [--near] [--task pixel|vertex] [--trace | --quad X,Y] <program.s | program.bin | ->
       sgx-sim --pds [--data N] [--set REG=VALUE]... [--max N] [--trace] <program.s | program.bin | ->
       sgx-sim --vectors FILE.vec.json [--id ID]";

fn list(idx: usize, w: u64, _: bool, core: Core) -> String {
    format!("{idx:6}: 0x{w:016X}\t{}", decode(w, core).text)
}

const USSE: Isa = Isa {
    name: "sgx-sim",
    width: 8,
    raw: ".long",
    data_segment: false,
    encode: encode_with,
    table: usse_isa::table,
    list,
};

fn num(s: &str) -> Option<u32> {
    match s.strip_prefix("0x").or(s.strip_prefix("0X")) {
        Some(h) => u32::from_str_radix(h, 16).ok(),
        None => s.parse().ok(),
    }
}

/// Preset a register (and mark it written): rN, iN, paN, saN, oN or pN.
fn set(m: &mut Machine, reg: &str, v: u32) -> Option<()> {
    if reg == "pclink" {
        m.set_link(v);
        return Some(());
    }
    let split = reg.find(|c: char| c.is_ascii_digit())?;
    let (bank, n) = (&reg[..split], reg[split..].parse::<usize>().ok()?);
    match bank {
        "r" if n < 128 => (m.r[n], m.written.r) = (v, m.written.r | 1 << n),
        "i" if n < 3 => (m.i[n], m.written.i) = (v, m.written.i | 1 << n),
        "pa" if n < 128 => (m.pa[n], m.written.pa) = (v, m.written.pa | 1 << n),
        "sa" if n < 128 => (m.sa[n], m.written.sa) = (v, m.written.sa | 1 << n),
        "o" if n < 128 => (m.o[n], m.written.o) = (v, m.written.o | 1 << n),
        "p" if n < 4 => m.set_pred(n, v != 0).then_some(())?,
        _ => return None,
    }
    Some(())
}

/// The registers an instance has written, one per line.
fn state(m: &Machine) -> String {
    let mut s = String::new();
    let banks: [(&str, &[u32], u128); 4] = [
        ("r", &m.r, m.written.r),
        ("pa", &m.pa, m.written.pa),
        ("sa", &m.sa, m.written.sa),
        ("o", &m.o, m.written.o),
    ];
    for (name, regs, written) in banks {
        for (n, v) in regs.iter().enumerate() {
            if written >> n & 1 != 0 {
                let _ = writeln!(s, "{name}{n} = 0x{v:08x}{}", near(m, name, n));
            }
        }
        if name == "r" {
            for n in 0..3 {
                if m.written.i >> n & 1 != 0 {
                    let _ = writeln!(s, "i{n} = 0x{:08x}{}", m.i[n], near(m, "i", n));
                }
            }
        }
    }
    let _ = writeln!(s, "p = {}{}{}{} (p3-p0)", m.p[3] as u8, m.p[2] as u8, m.p[1] as u8, m.p[0] as u8);
    s
}

/// A near value's bound (sgx_sim::Machine::near), after the value.
fn near(m: &Machine, bank: &'static str, n: usize) -> String {
    m.bounds.get(&(bank, n)).map_or(String::new(), |b| format!(" ~ {b}"))
}

/// What changed between two states of an instance, indented for a trace.
fn changes(a: &Machine, b: &Machine) -> String {
    let (x, y) = (state(a), state(b));
    let old: Vec<&str> = x.lines().collect();
    y.lines().filter(|l| !old.contains(l)).map(|l| format!("    {l}\n")).collect()
}

/// The scratch memory, logging stores for a trace, and the emits.
struct Scratch {
    mem: Memory,
    stores: Vec<(u32, u32)>,
    emits: Vec<String>,
}

impl Bus for Scratch {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.mem.load32(addr)
    }
    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        self.stores.push((addr, v));
        self.mem.store32(addr, v)
    }
    fn emit(&mut self, text: &str, srcs: [u32; 3]) -> Result<(), Error> {
        let name = text.split(['.', ' ']).next().unwrap_or(text);
        self.emits.push(format!("{name} 0x{:08x}, 0x{:08x}, 0x{:08x}", srcs[0], srcs[1], srcs[2]));
        Ok(())
    }
}

fn scratch() -> Scratch {
    Scratch {
        mem: Memory {
            base: SCRATCH_BASE,
            words: (0..SCRATCH_DWORDS as u32).map(|i| 0xD000_0000 | i).collect(),
        },
        stores: Vec::new(),
        emits: Vec::new(),
    }
}

fn memory_changes(s: &Scratch, m: &Machine) -> String {
    let mut o = String::new();
    for (i, &w) in s.mem.words.iter().enumerate() {
        let (was, a) = (0xD000_0000 | i as u32, SCRATCH_BASE + 4 * i as u32);
        if w != was {
            let near = m.near_mem.get(&a).map_or(String::new(), |b| format!(" ~ {b}"));
            let _ = writeln!(o, "[0x{a:08x}] = 0x{w:08x} (was 0x{was:08x}){near}");
        }
    }
    o
}

fn load(path: &str, core: Core) -> Result<Vec<u64>, String> {
    let mut bytes = Vec::new();
    if path == "-" {
        let _ = std::io::stdin().read_to_end(&mut bytes);
    } else {
        bytes = std::fs::read(path).map_err(|e| format!("{path}: {e}"))?;
    }
    if path.ends_with(".bin") {
        if bytes.len() % 8 != 0 {
            return Err(format!("{path}: not a whole number of 64-bit words"));
        }
        return Ok(bytes.chunks(8).map(|c| u64::from_le_bytes(c.try_into().unwrap())).collect());
    }
    let a = assemble_hinted(&USSE, &bytes, if path == "-" { "<stdin>" } else { path }, core, true);
    if a.errors > 0 {
        return Err(String::from_utf8_lossy(&a.messages).trim_end().to_string());
    }
    Ok(a.words)
}

/// A PDS program's port writes, in order; no memory.
#[derive(Default)]
struct Ports(Vec<(Port, [u32; 4])>);

impl Bus for Ports {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        Err(Error::Fault(addr))
    }
    fn store32(&mut self, addr: u32, _: u32) -> Result<(), Error> {
        Err(Error::Fault(addr))
    }
    fn port(&mut self, port: Port, w: [u32; 4]) -> Result<(), Error> {
        self.0.push((port, w));
        Ok(())
    }
}

fn port_line(port: Port, w: &[u32; 4]) -> String {
    format!("movs {port:?} 0x{:08x}, 0x{:08x}, 0x{:08x}, 0x{:08x}", w[0], w[1], w[2], w[3]).to_lowercase()
}

/// Preset a PDS register: dsB[n], ir0-ir2, tim, if0, if1.
fn set_pds(m: &mut Pds, reg: &str, v: u32) -> Option<()> {
    if let Some(rest) = reg.strip_prefix("ds") {
        let (b, n) = rest.split_once('[')?;
        let (b, n) = (b.parse::<usize>().ok()?, n.strip_suffix(']')?.parse::<usize>().ok()?);
        if b > 1 || n > 63 {
            return None;
        }
        (m.ds[b][n], m.known[b]) = (v, m.known[b] | 1 << n);
        return Some(());
    }
    match reg {
        "ir0" | "ir1" | "ir2" => m.ir[(reg.as_bytes()[2] - b'0') as usize] = Some(v),
        "tim" => m.tim = Some(v),
        "if0" | "if1" => m.ifs[(reg.as_bytes()[2] - b'0') as usize] = Some(v != 0),
        _ => return None,
    }
    Some(())
}

/// The PDS registers a run knows, past what the data segment loaded.
fn pds_state(m: &Pds, data: &[u32]) -> String {
    let mut s = String::new();
    for b in 0..2 {
        for n in 0..64 {
            let i = n / 2 * 4 + b * 2 + (n & 1);
            if m.known[b] >> n & 1 != 0 && data.get(i) != Some(&m.ds[b][n]) {
                let _ = writeln!(s, "ds{b}[{n}] = 0x{:08x}", m.ds[b][n]);
            }
        }
    }
    let p = |v: Option<bool>| v.map_or("?", |b| if b { "1" } else { "0" });
    let _ = writeln!(
        s,
        "p = {}{}{} (p2-p0), aluz {}, alun {}",
        p(m.p[2]),
        p(m.p[1]),
        p(m.p[0]),
        p(m.aluz),
        p(m.alun)
    );
    s
}

fn run_pds(path: &str, data: Option<usize>, sets: &[(String, u32)], max: usize, trace: bool) -> ExitCode {
    let mut bytes = Vec::new();
    if path == "-" {
        let _ = std::io::stdin().read_to_end(&mut bytes);
    } else if let Err(e) = std::fs::File::open(path).and_then(|mut f| f.read_to_end(&mut bytes)) {
        eprintln!("{path}: {e}");
        return ExitCode::from(2);
    }
    let (words, ndata) = if path.ends_with(".bin") {
        let Some(n) = data else {
            eprintln!("sgx-sim: a .bin PDS program needs --data N");
            return ExitCode::from(2);
        };
        (bytes.chunks_exact(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect::<Vec<_>>(), n)
    } else {
        let a = assemble_hinted(&PDS, &bytes, if path == "-" { "<stdin>" } else { path }, Core::Sgx545, true);
        if a.errors > 0 {
            eprintln!("{}", String::from_utf8_lossy(&a.messages).trim_end());
            return ExitCode::from(2);
        }
        (a.words.iter().map(|&w| w as u32).collect(), a.ndata)
    };
    let prog = pds::Program::new(&words, ndata);
    let mut m = Pds::default();
    m.start(&prog);
    for (r, v) in sets {
        if set_pds(&mut m, r, *v).is_none() {
            eprintln!("sgx-sim: --set {r}: not a PDS register (dsB[n], ir0-ir2, tim, if0, if1)");
            return ExitCode::from(2);
        }
    }
    let mut bus = Ports::default();
    let r = loop {
        if m.steps >= max {
            break Err(Error::StepLimit);
        }
        let (before, pc, ports) = (trace.then(|| m.clone()), m.pc, bus.0.len());
        let r = m.step(&prog, &mut bus);
        if let Some(b) = before {
            println!("{pc}: {}", prog.text(pc).unwrap_or("?"));
            let old = pds_state(&b, &[]);
            for l in pds_state(&m, &[]).lines().filter(|l| !old.lines().any(|o| o == *l)) {
                println!("    {l}");
            }
            for (port, w) in &bus.0[ports..] {
                println!("    {}", port_line(*port, w));
            }
        }
        match r {
            Ok(true) => break Ok(()),
            Ok(false) => {}
            Err(e) => break Err(e),
        }
    };
    match &r {
        Ok(()) => println!("halted after {} steps", m.steps),
        Err(e) => {
            println!("stopped after {} steps", m.steps);
            eprintln!(
                "{}: {e}",
                if matches!(e, Error::Unsupported { .. }) { "unsupported" } else { "error" }
            );
        }
    }
    print!("{}", pds_state(&m, &prog.data));
    for (port, w) in &bus.0 {
        println!("{}", port_line(*port, w));
    }
    match r {
        Ok(()) => ExitCode::SUCCESS,
        Err(Error::Unsupported { .. }) => ExitCode::from(1),
        Err(_) => ExitCode::from(2),
    }
}

fn run_vectors(path: &str, id: Option<&str>) -> ExitCode {
    let text = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{path}: {e}");
            return ExitCode::from(2);
        }
    };
    let d = sgx_sim::json::parse(&text);
    let raw = d.get("run").get("raw").str().unwrap_or("").to_string();
    let (mut pass, mut unsup, mut fail, mut skip) = (0, 0, 0, 0);
    for v in d.get("vectors").arr() {
        let vid = v.get("id").str().unwrap_or("");
        if id.is_some_and(|i| i != vid) {
            continue;
        }
        let probe = v.get("provenance").get("probe").str().unwrap_or("");
        if let Some(why) = vectors::skipped(&raw, probe, vid) {
            skip += 1;
            if id.is_some() {
                println!("{vid}: skipped ({why})");
            }
            continue;
        }
        match vectors::run(v) {
            None => skip += 1,
            Some(Ok(_)) => pass += 1,
            Some(Err(e)) if e.starts_with("unsupported") => {
                unsup += 1;
                if id.is_some() {
                    println!("{vid}: {e}");
                }
            }
            Some(Err(e)) => {
                fail += 1;
                println!("{vid}: {e}");
            }
        }
    }
    println!("{pass} match, {unsup} unsupported, {fail} mismatch, {skip} skipped");
    if fail > 0 { ExitCode::from(1) } else { ExitCode::SUCCESS }
}

fn main() -> ExitCode {
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let (mut core, mut sets, mut temps, mut max) = (Core::Sgx545, Vec::new(), 124, 100_000);
    let (mut trace, mut quad, mut input, mut vecs, mut id) = (false, None, None, None, None);
    let (mut near, mut pds, mut data, mut vertex) = (false, false, None, false);
    let mut i = 0;
    let usage = || {
        eprintln!("{USAGE}");
        ExitCode::from(2)
    };
    while i < argv.len() {
        let a = argv[i].as_str();
        let mut arg = || {
            i += 1;
            argv.get(i).cloned()
        };
        match a {
            "--core" => core = if arg().as_deref() == Some("540") { Core::Sgx540 } else { Core::Sgx545 },
            "--set" => match arg().and_then(|s| s.split_once('=').map(|(r, v)| (r.to_string(), num(v)))) {
                Some((r, Some(v))) => sets.push((r, v)),
                _ => return usage(),
            },
            "--temps" => match arg().and_then(|s| s.parse().ok()) {
                Some(n) => temps = n,
                None => return usage(),
            },
            "--max" => match arg().and_then(|s| s.parse().ok()) {
                Some(n) => max = n,
                None => return usage(),
            },
            "--trace" => trace = true,
            "--near" => near = true,
            "--task" => match arg().as_deref() {
                Some("vertex") => vertex = true,
                Some("pixel") => vertex = false,
                _ => return usage(),
            },
            "--pds" => pds = true,
            "--data" => match arg().and_then(|s| s.parse().ok()) {
                Some(n) => data = Some(n),
                None => return usage(),
            },
            "--quad" => match arg().and_then(|s| {
                let (x, y) = s.split_once(',')?;
                Some((x.parse::<u32>().ok()?, y.parse::<u32>().ok()?))
            }) {
                Some(p) => quad = Some(p),
                None => return usage(),
            },
            "--vectors" => vecs = arg(),
            "--id" => id = arg(),
            _ if input.is_none() && (!a.starts_with('-') || a == "-") => input = Some(a.to_string()),
            _ => return usage(),
        }
        i += 1;
    }
    if let Some(v) = vecs {
        return run_vectors(&v, id.as_deref());
    }
    let Some(input) = input else { return usage() };
    if pds {
        if quad.is_some() || near {
            eprintln!("sgx-sim: --pds runs one PDS program: no --quad or --near");
            return ExitCode::from(2);
        }
        return run_pds(&input, data, &sets, max, trace);
    }
    if trace && quad.is_some() {
        eprintln!("sgx-sim: --trace runs one instance, not a quad");
        return ExitCode::from(2);
    }
    let words = match load(&input, core) {
        Ok(w) => w.into_iter().map(vectors::patch_scratch).collect::<Vec<_>>(),
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::from(2);
        }
    };
    let prog = Program::new(&words, core);
    let new = || -> Option<Machine> {
        let mut m = Machine { core, temps, near, vertex_task: vertex, ..Machine::default() };
        for (r, v) in &sets {
            set(&mut m, r, *v)?;
        }
        Some(m)
    };
    let Some(m0) = new() else { return usage() };
    let mut bus = scratch();
    let (result, shown) = match quad {
        Some((x, y)) => {
            let (x0, y0) = (x & !1, y & !1);
            let mut q: [Machine; 4] = [m0.clone(), m0.clone(), m0.clone(), m0];
            for (k, m) in q.iter_mut().enumerate() {
                let (px, py) = (x0 + (k as u32 & 1), y0 + (k as u32 >> 1));
                (m.pa[0], m.written.pa) = (py << 16 | px, m.written.pa | 1);
            }
            let r = run_quad(&mut q, &prog, &mut bus, max);
            let k = ((y - y0) * 2 + (x - x0)) as usize;
            (r, q[k].clone())
        }
        None => {
            let mut m = m0;
            let r = loop {
                if m.steps >= max {
                    break Err(Error::StepLimit);
                }
                let before = trace.then(|| m.clone());
                let pc = m.pc;
                bus.stores.clear();
                let emitted = bus.emits.len();
                let r = m.step(&prog, &mut bus);
                if let Some(b) = before {
                    print!("{pc}: {}\n{}", Machine::text(&prog, pc).unwrap_or("?"), changes(&b, &m));
                    for (a, v) in &bus.stores {
                        println!("    [0x{a:08x}] = 0x{v:08x}");
                    }
                    for e in &bus.emits[emitted..] {
                        println!("    emit {e}");
                    }
                }
                match r {
                    Ok(true) => break Ok(()),
                    Ok(false) => {}
                    Err(e) => break Err(e),
                }
            };
            (r, m)
        }
    };
    match &result {
        Ok(()) => println!("ended after {} steps", shown.steps),
        Err(e) => {
            println!("stopped after {} steps", shown.steps);
            eprintln!(
                "{}: {e}",
                if matches!(e, Error::Unsupported { .. }) { "unsupported" } else { "error" }
            );
        }
    }
    print!("{}{}", state(&shown), memory_changes(&bus, &shown));
    for e in &bus.emits {
        println!("emit {e}");
    }
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(Error::Unsupported { .. }) => ExitCode::from(1),
        Err(_) => ExitCode::from(2),
    }
}
