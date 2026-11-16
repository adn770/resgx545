// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! What a run of `sgx::Sgx` did, step by step, for the firmware-in-sim track (fwsim): which
//! piece of work started, the index of each instruction it ran, every register read with the
//! source that answered it (`hw::Source`), every register write and memory access, the events
//! delivered, the pass boundaries and the refusals.
//!
//! A trace of the closed firmware is derived from it, so the clean-room terms of the track hold
//! here: an event carries indices, addresses and values, never instruction text (the decoder's
//! text stays out of every event, a refusal included), and the file sink writes only under
//! `<private data>/firmware/fwsim/` and refuses any other path. The engine names nothing of the
//! firmware; structure words get their glossary names at summary time, outside this crate.

use crate::hw::Source;
use std::fmt::Write as _;
use std::fs::File;
use std::io::{self, BufWriter, Write};
use std::path::{Component, Path, PathBuf};

/// Which interpreter ran an instruction.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Unit {
    Pds,
    Usse,
}

/// One thing a run did.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Ev {
    /// An event delivered to the event program: ir0 (None: unknown) and the event word ir1.
    Event {
        ir0: Option<u32>,
        ir1: u32,
    },
    /// A PDS program started: its address and data dwords.
    PdsStart {
        addr: u32,
        data: usize,
    },
    /// A USSE task started: its code base, instruction index and the primary attributes pa0
    /// to pa3 its PDS program wrote (None: not written), an event's inputs.
    TaskStart {
        base: u32,
        pc: usize,
        pa: [Option<u32>; 4],
    },
    /// An instruction about to run: the unit, the program's base (PDS: its address) and the index.
    Insn {
        unit: Unit,
        base: u32,
        pc: usize,
    },
    /// A register read and what answered it.
    RegRead {
        index: u32,
        value: u32,
        source: Source,
    },
    /// A register write, by the host or by the firmware.
    RegWrite {
        index: u32,
        value: u32,
        host: bool,
    },
    Load {
        addr: u32,
        value: u32,
    },
    Store {
        addr: u32,
        value: u32,
    },
    /// A pass ended (the queue ran empty): its number from 0 and the model time at its entry.
    Pass {
        n: u64,
        time: Option<u32>,
    },
    /// The run stopped: the register when a read stopped it, the instruction index, the reason
    /// (no instruction text).
    Refusal {
        index: Option<u32>,
        pc: usize,
        why: String,
    },
}

impl Ev {
    /// The event as one JSON object (one line of a `.jsonl` trace).
    pub fn json(&self) -> String {
        let x = |v: u32| format!("\"0x{v:08x}\"");
        let opt = |v: Option<u32>| v.map_or("null".to_string(), x);
        match self {
            Ev::Event { ir0, ir1 } => {
                format!("{{\"ev\":\"event\",\"ir0\":{},\"ir1\":{}}}", opt(*ir0), x(*ir1))
            }
            Ev::PdsStart { addr, data } => {
                format!("{{\"ev\":\"pds\",\"addr\":{},\"data\":{data}}}", x(*addr))
            }
            Ev::TaskStart { base, pc, pa } => format!(
                "{{\"ev\":\"task\",\"base\":{},\"pc\":{pc},\"pa\":[{}]}}",
                x(*base),
                pa.iter().map(|v| opt(*v)).collect::<Vec<_>>().join(",")
            ),
            Ev::Insn { unit, base, pc } => {
                let u = if *unit == Unit::Pds { "pds" } else { "usse" };
                format!("{{\"ev\":\"insn\",\"unit\":\"{u}\",\"base\":{},\"pc\":{pc}}}", x(*base))
            }
            Ev::RegRead { index, value, source } => format!(
                "{{\"ev\":\"rd\",\"reg\":\"0x{:04x}\",\"value\":{},\"source\":\"{}\"}}",
                index * 4,
                x(*value),
                source.name()
            ),
            Ev::RegWrite { index, value, host } => format!(
                "{{\"ev\":\"wr\",\"reg\":\"0x{:04x}\",\"value\":{},\"host\":{host}}}",
                index * 4,
                x(*value)
            ),
            Ev::Load { addr, value } => {
                format!("{{\"ev\":\"ld\",\"addr\":{},\"value\":{}}}", x(*addr), x(*value))
            }
            Ev::Store { addr, value } => {
                format!("{{\"ev\":\"st\",\"addr\":{},\"value\":{}}}", x(*addr), x(*value))
            }
            Ev::Pass { n, time } => format!("{{\"ev\":\"pass\",\"n\":{n},\"time\":{}}}", opt(*time)),
            Ev::Refusal { index, pc, why } => format!(
                "{{\"ev\":\"refusal\",\"reg\":{},\"pc\":{pc},\"why\":{}}}",
                index.map_or("null".to_string(), |i| format!("\"0x{:04x}\"", i * 4)),
                quote(why)
            ),
        }
    }
}

fn quote(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            c if (c as u32) < 0x20 => {
                let _ = write!(o, "\\u{:04x}", c as u32);
            }
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

/// Where a run's events go.
pub trait Tracer {
    fn record(&mut self, e: &Ev);
    /// Called once the run is over (a file sink flushes).
    fn finish(&mut self) -> io::Result<()> {
        Ok(())
    }
}

/// Keep the events in memory (the tests, and a caller that summarises them itself).
impl Tracer for Vec<Ev> {
    fn record(&mut self, e: &Ev) {
        self.push(e.clone());
    }
}

/// Keep the events where the caller can read them while the run holds the tracer.
impl Tracer for std::rc::Rc<std::cell::RefCell<Vec<Ev>>> {
    fn record(&mut self, e: &Ev) {
        self.borrow_mut().push(e.clone());
    }
}

/// The directory every fwsim output lives in: `<private data>/firmware/fwsim`.
pub fn fwsim_root(private: &Path) -> PathBuf {
    private.join("firmware").join("fwsim")
}

/// `path` if it lies under `<private>/firmware/fwsim/` once resolved (symbolic links of the
/// existing part followed, no `..`), else the reason it is refused. The file need not exist.
pub fn checked_out_path(path: &Path, private: &Path) -> Result<PathBuf, String> {
    let refuse = |why: &str| Err(format!("{}: {why}", path.display()));
    if path.components().any(|c| matches!(c, Component::ParentDir)) {
        return refuse("a trace path may not hold `..`");
    }
    let root =
        fwsim_root(private).canonicalize().map_err(|e| format!("{}: {e}", fwsim_root(private).display()))?;
    // resolve the longest existing ancestor, keep the rest as written
    let mut existing = path.to_path_buf();
    let mut rest = Vec::new();
    while !existing.exists() {
        match (existing.file_name().map(|n| n.to_os_string()), existing.parent()) {
            (Some(n), Some(p)) => {
                rest.push(n);
                existing = p.to_path_buf();
            }
            _ => return refuse("no existing directory above it"),
        }
    }
    let mut full = existing.canonicalize().map_err(|e| format!("{}: {e}", existing.display()))?;
    full.extend(rest.iter().rev());
    if full == root || !full.starts_with(&root) {
        return refuse("traces live only under the private data's firmware/fwsim/");
    }
    Ok(full)
}

/// A trace file: one JSON object a line. Its constructor refuses a path outside
/// `<private>/firmware/fwsim/`.
pub struct FileSink {
    out: BufWriter<File>,
    err: Option<io::Error>,
}

impl FileSink {
    pub fn create(path: &Path, private: &Path) -> Result<FileSink, String> {
        let full = checked_out_path(path, private)?;
        if let Some(dir) = full.parent() {
            std::fs::create_dir_all(dir).map_err(|e| format!("{}: {e}", dir.display()))?;
        }
        let f = File::create(&full).map_err(|e| format!("{}: {e}", full.display()))?;
        Ok(FileSink { out: BufWriter::new(f), err: None })
    }
}

impl Tracer for FileSink {
    fn record(&mut self, e: &Ev) {
        if self.err.is_none()
            && let Err(err) = writeln!(self.out, "{}", e.json())
        {
            self.err = Some(err);
        }
    }

    fn finish(&mut self) -> io::Result<()> {
        if let Some(e) = self.err.take() {
            return Err(e);
        }
        self.out.flush()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sgx::{Sgx, reg};
    use std::cell::RefCell;
    use std::rc::Rc;
    use usse_isa::Core;

    const CODE: u32 = 0xE800_0000;
    const DATA: u32 = 0xF000_0000;

    fn usse(src: &str) -> Vec<u8> {
        src.lines()
            .map(str::trim)
            .filter(|l| !l.is_empty())
            .flat_map(|l| usse_isa::encode(l, Core::Sgx545).unwrap_or_else(|| panic!("{l}")).to_le_bytes())
            .collect()
    }

    /// A two-line synthetic task (no firmware): read register 0x40, store it to DATA, write
    /// register 0x100 from it; then the end.
    fn two_line_task(s: &mut Sgx) {
        s.write_reg(reg::USE_CODE_BASE_0 + 15, 0x07d0_0000).unwrap();
        s.st.mem.map(CODE, &usse(&format!("mov r0, #0x{DATA:08X}\nldr r1, #16, drc0\nwdf drc0\nstad.bpcache [r0,+#0], r1\nstr #64, r1\nnop.end")));
        s.st.mem.map(DATA, &[0; 16]);
        s.seed(16, 0x1234);
        s.queue_task(CODE, 0, 8);
    }

    #[test]
    fn a_sink_records_the_task_its_reads_writes_and_stores_without_instruction_text() {
        let mut s = Sgx::default();
        two_line_task(&mut s);
        let rec = Rc::new(RefCell::new(Vec::new()));
        s.trace_to(Box::new(rec.clone()));
        s.run(100).unwrap();
        let ev = rec.borrow().clone();
        assert_eq!(ev[0], Ev::TaskStart { base: CODE, pc: 0, pa: [None; 4] });
        assert!(ev.contains(&Ev::Insn { unit: Unit::Usse, base: CODE, pc: 0 }));
        assert!(ev.contains(&Ev::RegRead { index: 16, value: 0x1234, source: Source::Seed }));
        assert!(ev.contains(&Ev::Store { addr: DATA, value: 0x1234 }));
        assert!(ev.contains(&Ev::RegWrite { index: 64, value: 0x1234, host: false }));
        assert!(matches!(ev.last(), Some(Ev::Pass { n: 0, .. })));
        // FW-7: indices, values and effects only
        let text: String = ev.iter().map(Ev::json).collect();
        for word in ["mov", "ldr", "stad", "str ", "nop", "wdf"] {
            assert!(!text.contains(word), "{word} in {text}");
        }
    }

    #[test]
    fn a_refusal_is_traced_with_its_register_and_no_instruction_text() {
        let mut s = Sgx::default();
        s.write_reg(reg::USE_CODE_BASE_0 + 15, 0x07d0_0000).unwrap();
        s.st.mem.map(CODE, &usse("ldr r0, #7, drc0\nwdf drc0\nnop.end"));
        s.queue_task(CODE, 0, 8);
        let rec = Rc::new(RefCell::new(Vec::new()));
        s.trace_to(Box::new(rec.clone()));
        assert!(s.run(100).is_err());
        let ev = rec.borrow().clone();
        let Some(Ev::Refusal { index, why, .. }) = ev.last() else { panic!("{ev:?}") };
        assert_eq!(*index, Some(7));
        assert!(why.contains("0x001c") && !why.contains("ldr"), "{why}");
    }

    fn scratch(name: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("sgx-sim-trace-{}-{name}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(fwsim_root(&d)).unwrap();
        std::fs::create_dir_all(d.join("render")).unwrap();
        d
    }

    #[test]
    fn the_file_sink_writes_only_under_the_private_data_s_firmware_fwsim() {
        let private = scratch("sink");
        let ok = fwsim_root(&private).join("m1-test").join("trace.jsonl");
        let mut sink = FileSink::create(&ok, &private).unwrap();
        sink.record(&Ev::Pass { n: 0, time: None });
        sink.finish().unwrap();
        assert_eq!(std::fs::read_to_string(&ok).unwrap(), "{\"ev\":\"pass\",\"n\":0,\"time\":null}\n");
        for bad in [
            private.join("render").join("trace.jsonl"),
            private.join("firmware").join("trace.jsonl"),
            fwsim_root(&private),
            fwsim_root(&private).join("..").join("trace.jsonl"),
            std::env::temp_dir().join("trace.jsonl"),
        ] {
            assert!(FileSink::create(&bad, &private).is_err(), "{}", bad.display());
        }
        // a symbolic link inside fwsim/ that leads out of it is followed, and refused
        #[cfg(unix)]
        {
            let link = fwsim_root(&private).join("out");
            std::os::unix::fs::symlink(private.join("render"), &link).unwrap();
            assert!(FileSink::create(&link.join("trace.jsonl"), &private).is_err());
        }
        std::fs::remove_dir_all(&private).unwrap();
    }
}
