// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! One SGX as its microkernel (the EDM) sees it: memory, the register file,
//! the PDS and the USSE, and the work that passes between them. Events start
//! PDS programs, PDS programs start USSE tasks, USSE tasks start PDS programs
//! (`emitpds`); here that runs single-threaded and deterministically, one
//! piece of work at a time in the order it was issued (the hardware overlaps
//! them). No timing, caches or MMU: device addresses are the EDM's.
//!
//! The launch rules are doc/specs/hw_spec.md 11.1-11.3 and
//! doc/specs/pds_isa.md 3.4, each cited where it is used. A register
//! nobody wrote, and the caller did not seed with a value known from the
//! hardware, stops the run. With a hardware model (`hw::HwModel`, the firmware-in-sim track)
//! every read is answered by a run write, a cited seed, a landed rule or a kept snapshot, and a
//! tracer (`trace::Tracer`) may record what the run did, pass by pass.

use crate::hw::{HwModel, Source};
use crate::pds::{self, Pds, Port};
use crate::trace::{Ev, Tracer, Unit as TraceUnit};
use crate::{Bus, Error, Machine, Program};
use std::collections::{BTreeMap, BTreeSet, HashMap, VecDeque};
use std::rc::Rc;
use usse_isa::Core;

/// SGX register dword indices (offset / 4) the loop itself acts on.
pub mod reg {
    pub const EVENT_HOST_CLEAR2: u32 = 0x0114 / 4;
    pub const EVENT_STATUS2: u32 = 0x0118 / 4;
    pub const EVENT_STATUS: u32 = 0x012c / 4;
    pub const EVENT_HOST_CLEAR: u32 = 0x0134 / 4;
    pub const USE_CODE_BASE_0: u32 = 0x0a0c / 4;
    pub const EVENT_OTHER_PDS_EXEC: u32 = 0x0a68 / 4;
    pub const EVENT_OTHER_PDS_DATA: u32 = 0x0a6c / 4;
    /// EVENT_KICKER: the address (bits 31:4) of the kernel's kicker word W (boot_sequence.md 2).
    pub const EVENT_KICKER: u32 = 0x0ac4 / 4;
    pub const EVENT_KICK: u32 = 0x0ac8 / 4;
    /// EVENT_TIMER: the microkernel's tick, 24-bit count, bit 24 runs it; the PDS
    /// reads and writes it as `tim` (sgx545defs.h, pds_isa 8.9).
    pub const EVENT_TIMER: u32 = 0x0acc / 4;
    pub const EVENT_KICK2: u32 = 0x0ae8 / 4;
}

/// Where a PDS program's `douta`/`doutd` writes land.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Bank {
    /// The started task's primary attributes: an event's inputs.
    Primary,
    /// The EDM's secondary attributes: an `emitpds` launch (PDS #11 DMAs
    /// TA3DCtl into `sa`, hw_spec 11.1).
    Secondary,
}

/// What happened, in order.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    /// A register write by the host or by the firmware.
    Write { host: bool, index: u32, value: u32 },
    /// A PDS program started: address, data dwords, ir0.
    Pds { addr: u32, data: usize, ir0: Option<u32> },
    /// A USSE task started: code base, instruction index, temporaries.
    Task { base: u32, pc: usize, temps: usize },
}

#[derive(Clone)]
enum Work {
    Pds { addr: u32, data: usize, ir0: Option<u32>, ir1: Option<u32>, tim: Option<u32>, bank: Bank },
    Task { base: u32, pc: usize, temps: usize, pa: Box<[u32; 128]>, written: u128 },
}

/// Device memory: 4 KiB pages.
#[derive(Default)]
pub struct Memory {
    pages: BTreeMap<u32, Box<[u32; 1024]>>,
}

impl Memory {
    /// Map `bytes` at `addr` (dword aligned), little endian; the rest of each page is 0.
    pub fn map(&mut self, addr: u32, bytes: &[u8]) {
        for (i, c) in bytes.chunks(4).enumerate() {
            let mut w = [0u8; 4];
            w[..c.len()].copy_from_slice(c);
            let a = addr.wrapping_add(4 * i as u32);
            self.pages.entry(a >> 12).or_insert_with(|| Box::new([0; 1024]))[(a as usize & 0xfff) / 4] =
                u32::from_le_bytes(w);
        }
    }

    pub fn load(&self, addr: u32) -> Result<u32, Error> {
        match self.pages.get(&(addr >> 12)) {
            Some(p) if addr.is_multiple_of(4) => Ok(p[(addr as usize & 0xfff) / 4]),
            _ => Err(Error::Fault(addr)),
        }
    }

    pub fn store(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        match self.pages.get_mut(&(addr >> 12)) {
            Some(p) if addr.is_multiple_of(4) => {
                p[(addr as usize & 0xfff) / 4] = v;
                Ok(())
            }
            _ => Err(Error::Fault(addr)),
        }
    }

    /// The mapped dwords from `addr` up to the first unmapped page, at most `max`.
    fn words(&self, addr: u32, max: usize) -> Vec<u32> {
        (0..max as u32).map_while(|i| self.load(addr.wrapping_add(4 * i)).ok()).collect()
    }
}

/// The state the work shares.
pub struct State {
    pub mem: Memory,
    pub regs: BTreeMap<u32, u32>,
    pub log: Vec<Event>,
    /// The EDM's secondary attributes, kept from one task to the next (pds_isa 3.4).
    pub sa: [u32; 128],
    pub sa_written: u128,
    /// The counter a program a task emits reads while the timer runs: a running count the
    /// caller gives (`set_emit_tim`), since the sim keeps no clock. E1133: bit 24 alone in
    /// 31:24 and bits 23:0 at most 400000 through a kick pass (no write or stop), at a phase no
    /// row gives; None refuses the read as before. A stopped timer is read from the register.
    emit_tim: Option<u32>,
    /// `Sgx::emit_s2_is_ir0`, copied in before each program.
    emit_s2_is_ir0: bool,
    queue: VecDeque<Work>,
    /// The registers `Sgx::seed` set that nothing has written since.
    seeded: BTreeSet<u32>,
    /// The hardware model; `None`: a register is known only once written or seeded.
    pub hw: Option<HwModel>,
    tracer: Option<Box<dyn Tracer>>,
    /// The register whose read stopped the run, for the trace's refusal.
    last_refused: Option<u32>,
}

impl Default for State {
    fn default() -> State {
        State {
            mem: Memory::default(),
            regs: BTreeMap::new(),
            log: Vec::new(),
            sa: [0; 128],
            sa_written: 0,
            emit_tim: None,
            emit_s2_is_ir0: false,
            queue: VecDeque::new(),
            seeded: BTreeSet::new(),
            hw: None,
            tracer: None,
            last_refused: None,
        }
    }
}

impl State {
    /// What a write to an event clear register does, by the host or a task, before it is stored:
    /// `CR_EVENT_HOST_CLEAR2` with STATUS2 known clears the bits written of the latched bit 6
    /// (E821 host, E822 a task's `str #69`, 3 of 3 rounds each: from 0x440 bit 6 gives 0x400, bit
    /// 15 leaves it); any other value, or another latched state, is refused. A write of bit 18
    /// to `CR_EVENT_HOST_CLEAR` with STATUS known is refused (E823: one job, post hoc). With the
    /// status register unknown the write is only stored, as before.
    fn clear_event(&mut self, index: u32, value: u32) -> Result<(), Error> {
        if index == reg::EVENT_HOST_CLEAR2
            && let Some(&st) = self.regs.get(&reg::EVENT_STATUS2)
        {
            let next = match value {
                _ if st & 0x40 == 0 || st & !0x440 != 0 => None,
                0x40 => Some(st & !0x40),
                0x8000 => Some(st),
                _ => None,
            };
            let Some(next) = next else {
                return Err(why(format!(
                    "CR_EVENT_HOST_CLEAR2 = {value:#x} with STATUS2 {st:#x}: only bit 6 and bit 15 on the latched \
                     0x440 were run (E821, E822)"
                )));
            };
            self.regs.insert(reg::EVENT_STATUS2, next);
        }
        if index == reg::EVENT_HOST_CLEAR
            && value >> 18 & 1 != 0
            && self.regs.contains_key(&reg::EVENT_STATUS)
        {
            return Err(why("CR_EVENT_HOST_CLEAR bit 18: one job, post hoc (E823; row B1P has not run)"));
        }
        Ok(())
    }

    /// A register read and what answered it: the hardware model when there is one, else a
    /// written or seeded value; nothing: the run stops.
    fn read(&mut self, index: u32) -> Result<(u32, Source), Error> {
        let known = self.regs.get(&index).copied();
        let r = match &mut self.hw {
            // a legacy seed (`Sgx::seed`) cites nothing: under the model only its seeds count
            Some(hw) => hw.read(index, known.filter(|_| !self.seeded.contains(&index))),
            None => match known {
                Some(v) if self.seeded.contains(&index) => Ok((v, Source::Seed)),
                Some(v) => Ok((v, Source::Written)),
                None => Err(why(format!("reads register 0x{:04x} before anything wrote it", index * 4))),
            },
        };
        if r.is_err() {
            self.last_refused = Some(index);
        }
        r
    }

    fn reg(&mut self, index: u32) -> Result<u32, Error> {
        self.read(index).map(|(v, _)| v)
    }

    fn store_reg(&mut self, index: u32, value: u32, host: bool) {
        self.regs.insert(index, value);
        self.seeded.remove(&index);
        if let Some(hw) = &mut self.hw {
            hw.on_write(index, value);
        }
        self.log.push(Event::Write { host, index, value });
        self.trace(|| Ev::RegWrite { index, value, host });
    }

    /// An effect of a task (a register write, a store, an emit), which a replayed read the
    /// hardware model has not proven a spin may not precede (hw::HwModel::replay).
    fn effect(&mut self) -> Result<(), Error> {
        self.hw.as_mut().map_or(Ok(()), HwModel::effect)
    }

    fn trace(&mut self, e: impl FnOnce() -> Ev) {
        if let Some(t) = &mut self.tracer {
            t.record(&e());
        }
    }

    fn load_traced(&mut self, addr: u32) -> Result<u32, Error> {
        let value = self.mem.load(addr)?;
        self.trace(|| Ev::Load { addr, value });
        Ok(value)
    }
}

/// The SGX.
#[derive(Default)]
pub struct Sgx {
    pub st: State,
    pub pds: Pds,
    /// USSE programs by code base and length, decoded once.
    programs: HashMap<(u32, usize), Rc<Program>>,
    pub steps: usize,
    /// An event program's ir0 and the counter it reads (tim), which the hardware gives and
    /// nothing here models.
    pub event_ir0: Option<u32>,
    pub event_tim: Option<u32>,
    /// The count byte, bits 31:24 of the event word every event carries (Q290, E768): the host
    /// kicks served since the load, mod 256. It starts at 0; the kernel's boot and the arm each
    /// send a GETMISCINFO, so an armed firmware reads 2 (set it, and the kicker word with it).
    /// The hardware does not read the kicker word W per event (E819 Q1, H-KW refuted), nor latch W
    /// at a served kick: with W written to 0x42 before an ordinary kick (bumped to 0x43) the ticks
    /// after it carried 3 (E834, H-LATCH refuted, H-CNT consistent), so the count is of served
    /// kicks; the sim serves only a kick whose W is bumped by one (see `write_reg`), and refuses a
    /// kick after W was set otherwise (Q290).
    pub event_count: u8,
    /// Set by an EVENT_KICK write with the kicker word unchanged, which the hardware did not
    /// consume (E819 Q3); every later event and kick is refused (Q290).
    pub kick_unconsumed: bool,
    /// pds::Pds::alu_specials_in_movs for every program (an assumption, off by default).
    pub alu_specials_in_movs: bool,
    /// An emitted program's `ir0` is `emitpds`'s s2 (an assumption, off by default: E146 read it
    /// from the operand order only [infer], and E488 measured a client fill's emit with s2 0, 1,
    /// 0xFFFFFFFF and 0xE17D0001 giving ir0.0 3, 3, 2, 3, so s2 is not ir0 there). Off, the
    /// program's `ir0` and `ir1` are unknown and a program that reads them is refused.
    pub emit_s2_is_ir0: bool,
    /// The instructions a task reads from its code base: `MAX_CODE` unless set. Our own tasks sit
    /// at instruction 0x4000 (tools/fwtask OWN_INDEX), past the default window.
    pub code_len: Option<usize>,
    /// The task state that outlives a task, `None` by default: each task then starts with it
    /// unwritten, and a read of it is refused. Set, every task starts from it and what the task
    /// leaves replaces it (E536: pclink, p1 to p3, r20, r21, i0 and i1 at a firmware task's entry
    /// were as the task before left them); the caller seeds the first entry with what a run read.
    pub carry: Option<Carry>,
    /// Passes run to the end (the queue empty), counted from 0.
    pub passes: u64,
}

/// A firmware task's entry state that the task before left (`Sgx::carry`); `None`: unknown.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Carry {
    pub pclink: Option<u32>,
    pub p: [Option<bool>; 4],
    pub r20: Option<u32>,
    pub r21: Option<u32>,
    pub i0: Option<u32>,
    pub i1: Option<u32>,
}

impl Carry {
    fn enter(&self, m: &mut Machine) {
        if let Some(l) = self.pclink {
            m.set_link(l);
        }
        for (n, v) in self.p.iter().enumerate() {
            if let Some(v) = v {
                m.set_pred(n, *v);
            }
        }
        for (n, v) in [(20, self.r20), (21, self.r21)] {
            if let Some(v) = v {
                (m.r[n], m.written.r) = (v, m.written.r | 1 << n);
            }
        }
        for (n, v) in [(0, self.i0), (1, self.i1)] {
            if let Some(v) = v {
                (m.i[n], m.written.i) = (v, m.written.i | 1 << n);
            }
        }
    }

    fn leave(&mut self, m: &Machine) {
        if m.link_set {
            self.pclink = Some(m.link);
        }
        for n in 0..4 {
            if m.p_set >> n & 1 != 0 {
                self.p[n] = Some(m.p[n]);
            }
        }
        let r = |n: usize| (m.written.r >> n & 1 != 0).then_some(m.r[n]);
        let i = |n: usize| (m.written.i >> n & 1 != 0).then_some(m.i[n]);
        (self.r20, self.r21) = (r(20).or(self.r20), r(21).or(self.r21));
        (self.i0, self.i1) = (i(0).or(self.i0), i(1).or(self.i1));
    }
}

/// The longest program read from a code base, in instructions.
const MAX_CODE: usize = 0x4000;

/// The first instruction of our own tasks' page in the EDM code base (tools/fwtask OWN_INDEX).
const OWN_INDEX: usize = 0x4000;

impl Sgx {
    /// A register value known from the hardware, readable before anything writes it.
    pub fn seed(&mut self, index: u32, value: u32) {
        self.st.regs.insert(index, value);
        self.st.seeded.insert(index);
    }

    /// Record what the run does from here on (`trace::Tracer`), replacing any tracer before.
    pub fn trace_to(&mut self, t: Box<dyn Tracer>) {
        self.st.tracer = Some(t);
    }

    /// Stop tracing; the tracer, finished (a file sink flushed).
    pub fn take_trace(&mut self) -> Option<Result<Box<dyn Tracer>, std::io::Error>> {
        self.st.tracer.take().map(|mut t| t.finish().map(|_| t))
    }

    /// Queue a USSE task (a caller that starts one directly: tests, scenarios).
    pub fn queue_task(&mut self, base: u32, pc: usize, temps: usize) {
        self.st.queue.push_back(Work::Task { base, pc, temps, pa: Box::new([0; 128]), written: 0 });
    }

    /// A host register write (an init script, a kick).
    pub fn write_reg(&mut self, index: u32, value: u32) -> Result<(), Error> {
        self.st.clear_event(index, value)?;
        self.st.store_reg(index, value, true);
        // EVENT_KICK2 runs the other-event PDS program (hw_spec 11.1-11.2):
        // its address in bits 31:4, its data size in rows of four dwords
        if index == reg::EVENT_KICK2 && value & 1 != 0 {
            let addr = self.st.reg(reg::EVENT_OTHER_PDS_EXEC)? & !0xf;
            let data = self.st.reg(reg::EVENT_OTHER_PDS_DATA)? as usize * 4;
            self.st.queue.push_back(Work::Pds {
                addr,
                data,
                ir0: None,
                ir1: None,
                tim: None,
                bank: Bank::Primary,
            });
        }
        // EVENT_KICK, the host's command kick: the event word's bit 8 (read from
        // the handler it reaches)
        // and the count byte steps after the kick's own event, which carries the old value
        if index == reg::EVENT_KICK && value & 1 != 0 {
            self.kick()?;
        }
        Ok(())
    }

    /// An EVENT_KICK write, by the kicker word W at the address in EVENT_KICKER (mod 256). W
    /// bumped by one since the last served kick, as the kernel does before each write: one event
    /// with the kick bit and the count before the bump (E746, E768, E816 G0). W unchanged: no
    /// event, the count and W left, the command not answered (E819 Q3, 3 of 3); [infer] the
    /// event needs W to change. E834 repeated it (no kick entry in 5 of 5, the ticks after it kept
    /// the count and carried pa2 0x01061a74, and an ordinary kick after it in a second window was
    /// served at once with the count unchanged); whether an event stays pending and what the
    /// marked ticks mean are open (Q290), so the sim refuses every later event and kick. W set to
    /// any other value, then kicked: refused (E819 Q2 could not read the count after it; E834 read
    /// 3 after W 0x42 bumped to 0x43, a single row, Q290).
    fn kick(&mut self) -> Result<(), Error> {
        if self.kick_unconsumed {
            return Err(why("a kick after a kick that was not consumed: not run (Q290, E819)"));
        }
        let kicker = self.st.reg(reg::EVENT_KICKER)? & !0xf;
        let w = self.st.mem.load(kicker)? & 0xff;
        let count = u32::from(self.event_count);
        if w == (count + 1) & 0xff {
            self.event(1 << 8)?;
            self.event_count = w as u8;
        } else if w == count {
            self.kick_unconsumed = true;
        } else {
            return Err(why(format!(
                "a kick with the kicker word at {w:#x} and the count at {count:#x}: only a bump by one \
                 (E768) and no bump (E819 Q3) were run (Q290)"
            )));
        }
        Ok(())
    }

    /// The running count an emitted program reads (see `emit_tim`); a value outside E1133's
    /// rule (bit 24 alone in 31:24, bits 23:0 at most 400000) is refused.
    pub fn set_emit_tim(&mut self, v: Option<u32>) -> Result<(), Error> {
        if let Some(t) = v {
            if t >> 24 != 1 || t & 0x00ff_ffff > 400_000 {
                return Err(why(format!(
                    "{t:#010x} is not a running count (E1133: bit 24 alone in 31:24, bits 23:0 at most 400000)"
                )));
            }
        }
        self.st.emit_tim = v;
        Ok(())
    }

    pub fn emit_tim(&self) -> Option<u32> {
        self.st.emit_tim
    }

    /// An event: the other-event PDS program with the event word `ir1`, and the ir0 and
    /// counter the caller set (`event_ir0`, `event_tim`). The timer tick is ir0 bit 1 with
    /// nothing in ir1 (the microkernel's tick handler tests pa0 bit 1), and the count byte
    /// (`event_count`) in bits 31:24 of ir1 as every event carries it.
    pub fn event(&mut self, ir1: u32) -> Result<(), Error> {
        if self.kick_unconsumed {
            return Err(why(
                "an event after a kick that was not consumed: its count and whether the kick stays pending \
                 are open (Q290, E819 Q3)",
            ));
        }
        let addr = self.st.reg(reg::EVENT_OTHER_PDS_EXEC)? & !0xf;
        let data = self.st.reg(reg::EVENT_OTHER_PDS_DATA)? as usize * 4;
        let (ir0, tim) = (self.event_ir0, self.event_tim);
        let ir1 = ir1 | u32::from(self.event_count) << 24;
        if let Some(hw) = &mut self.st.hw {
            hw.on_event(ir0, ir1);
        }
        self.st.trace(|| Ev::Event { ir0, ir1 });
        self.st.queue.push_back(Work::Pds { addr, data, ir0, ir1: Some(ir1), tim, bank: Bank::Primary });
        Ok(())
    }

    /// Run the queued work until none is left: one pass. A stop is traced as a refusal.
    pub fn run(&mut self, max_steps: usize) -> Result<(), Error> {
        let ran = !self.st.queue.is_empty();
        let r = self.run_queue(max_steps);
        match &r {
            Ok(()) if ran => {
                let n = self.passes;
                self.passes += 1;
                self.st.trace(|| Ev::Pass { n, time: None });
            }
            Ok(()) => {}
            Err(e) => {
                let index = self.st.last_refused.take();
                let (pc, why) = match e {
                    Error::Unsupported { pc, why, .. } => (*pc, why.clone()),
                    Error::Fault(a) => (0, format!("fault at 0x{a:08x}")),
                    Error::PcOutOfRange(pc) => (*pc, "pc out of range".to_string()),
                    Error::StepLimit => (0, "step limit".to_string()),
                };
                self.st.trace(|| Ev::Refusal { index, pc, why });
            }
        }
        r
    }

    fn run_queue(&mut self, max_steps: usize) -> Result<(), Error> {
        self.st.last_refused = None;
        self.st.emit_s2_is_ir0 = self.emit_s2_is_ir0;
        while let Some(w) = self.st.queue.pop_front() {
            if self.steps >= max_steps {
                return Err(Error::StepLimit);
            }
            match w {
                Work::Pds { addr, data, ir0, ir1, tim, bank } => {
                    self.run_pds(addr, data, [ir0, ir1, tim], bank, max_steps)?
                }
                Work::Task { base, pc, temps, pa, written } => {
                    self.run_task(base, pc, temps, pa, written, max_steps)?
                }
            }
        }
        Ok(())
    }

    fn run_pds(
        &mut self,
        addr: u32,
        data: usize,
        [ir0, ir1, tim]: [Option<u32>; 3],
        bank: Bank,
        max: usize,
    ) -> Result<(), Error> {
        self.st.log.push(Event::Pds { addr, data, ir0 });
        self.st.trace(|| Ev::PdsStart { addr, data });
        let prog = pds::Program::new(&self.st.mem.words(addr, data + 256), data);
        self.pds.ir = [ir0, ir1, None];
        self.pds.alu_specials_in_movs = self.alu_specials_in_movs;
        // tim is EVENT_TIMER: known while it is stopped; the caller may give a running value
        self.pds.tim = tim.or_else(|| {
            self.st.regs.get(&reg::EVENT_TIMER).filter(|v| *v >> 24 & 1 == 0).map(|v| v & 0x01ff_ffff)
        });
        self.pds.ifs = [None; 2];
        let mut bus = Unit { st: &mut self.st, bank, pa: [0; 128], written: 0, own: false };
        // Pds::run, one step at a time so that each instruction can be traced
        let limit = max - self.steps;
        self.pds.start(&prog);
        let r = loop {
            if self.pds.steps >= limit {
                break Err(Error::StepLimit);
            }
            let pc = self.pds.pc;
            bus.st.trace(|| Ev::Insn { unit: TraceUnit::Pds, base: addr, pc });
            match self.pds.step(&prog, &mut bus) {
                Ok(true) => break Ok(()),
                Ok(false) => {}
                Err(e) => break Err(e),
            }
        };
        self.steps += self.pds.steps;
        r.map_err(|e| context(e, &format!("PDS 0x{addr:08x}")))
    }

    fn run_task(
        &mut self,
        base: u32,
        pc: usize,
        temps: usize,
        pa: Box<[u32; 128]>,
        written: u128,
        max: usize,
    ) -> Result<(), Error> {
        self.st.log.push(Event::Task { base, pc, temps });
        self.st.trace(|| Ev::TaskStart {
            base,
            pc,
            pa: std::array::from_fn(|n| (written >> n & 1 != 0).then_some(pa[n])),
        });
        let len = self.code_len.unwrap_or(MAX_CODE);
        let prog = match self.programs.get(&(base, len)) {
            Some(p) => p.clone(),
            None => {
                let w: Vec<u64> = self
                    .st
                    .mem
                    .words(base, 2 * len)
                    .chunks_exact(2)
                    .map(|d| d[0] as u64 | (d[1] as u64) << 32)
                    .collect();
                let p = Rc::new(Program::new(&w, Core::Sgx545));
                self.programs.insert((base, len), p.clone());
                p
            }
        };
        let mut m = Machine { temps, pc, pa: *pa, sa: self.st.sa, edm_task: true, ..Machine::default() };
        m.written.pa = written;
        m.written.sa = self.st.sa_written;
        // the task's pa0 to pa4 are sa64 to sa68 (S2 e2r): the words the PDS program wrote with
        // DOUTA land there, so the pa and sa views agree
        for n in 0..5 {
            if written >> n & 1 != 0 {
                (m.sa[64 + n], m.written.sa) = (pa[n], m.written.sa | 1 << (64 + n));
            }
        }
        if let Some(c) = &self.carry {
            c.enter(&mut m);
        }
        let own = pc >= OWN_INDEX;
        let mut bus = Unit { st: &mut self.st, bank: Bank::Secondary, pa: [0; 128], written: 0, own };
        // Machine::run, one step at a time so that each instruction can be traced
        let limit = max - self.steps;
        let r = loop {
            if m.steps >= limit {
                break Err(Error::StepLimit);
            }
            let pc = m.pc;
            bus.st.trace(|| Ev::Insn { unit: TraceUnit::Usse, base, pc });
            if let Some(hw) = &mut bus.st.hw {
                hw.at(base, pc);
                if hw.waits_at() == Some((base, pc)) {
                    hw.arrive(base, pc, || spin_key(&m));
                }
            }
            match m.step(&prog, &mut bus) {
                Ok(true) => break bus.st.hw.as_mut().map_or(Ok(()), HwModel::task_end),
                Ok(false) => {}
                Err(e) => break Err(e),
            }
        };
        self.steps += m.steps;
        if let Some(c) = &mut self.carry {
            c.leave(&m);
        }
        // the secondary attributes outlive the task
        (self.st.sa, self.st.sa_written) = (m.sa, m.written.sa);
        r.map_err(|e| context(e, &format!("task 0x{base:08x}+{pc:#x}")))
    }
}

/// A task's whole state between instructions, but its pc and step count, as words: two arrivals
/// at a replayed read with the same key and nothing written in between are a spin
/// (hw::HwModel::arrive). Every field is named, so a new one does not go unseen; a state the key
/// cannot hold whole (bounds, unknown values, a quad) gets a fresh nonce and proves no spin.
fn spin_key(m: &Machine) -> Vec<u32> {
    use std::sync::atomic::{AtomicU32, Ordering};
    static NONCE: AtomicU32 = AtomicU32::new(0);
    let Machine {
        core: _,
        pixel,
        tri_pixel,
        vertex,
        r,
        i,
        o,
        pa,
        sa,
        p,
        p_set,
        pc: _,
        link,
        link_set,
        steps: _,
        written,
        pending,
        pending_unknown,
        moe_inc,
        moe_swizzle,
        moe_base,
        moe_addr,
        moe_range,
        index,
        quad,
        quad_i1,
        temps,
        near,
        uniform,
        bounds,
        near_mem,
        now: _,
        firh_latch,
        firh_written,
        fitted,
        coeffs,
        csc_unloaded,
        csc,
        unknown,
        phase,
        vertex_task,
        code_index,
        edm_task,
        mov_dest,
        locks,
    } = m;
    let mut k: Vec<u32> = Vec::with_capacity(700);
    if pixel.is_some()
        || vertex.is_some()
        || quad.is_some()
        || coeffs.is_some()
        || !bounds.is_empty()
        || !near_mem.is_empty()
        || !unknown.is_empty()
        || !pending_unknown.is_empty()
    {
        k.push(NONCE.fetch_add(1, Ordering::Relaxed));
        k.push(u32::MAX);
    }
    let flag = |b: bool| u32::from(b);
    k.extend(r.iter().chain(i).chain(o).chain(pa).chain(sa));
    k.extend(p.iter().map(|&b| flag(b)));
    k.extend([u32::from(*p_set), *link, flag(*link_set), flag(*tri_pixel), flag(*near), flag(*uniform)]);
    for w in [written.r, written.o, written.pa, written.sa] {
        k.extend([w as u32, (w >> 32) as u32, (w >> 64) as u32, (w >> 96) as u32]);
    }
    k.extend([u32::from(written.i), u32::from(written.index)]);
    k.push(pending.len() as u32);
    for (drc, reg, v) in pending {
        let (bank, n) = match reg {
            crate::usse::Reg::R(n) => (0, *n),
            crate::usse::Reg::Pa(n) => (1, *n),
        };
        k.extend([*drc, bank, n as u32, *v]);
    }
    let opt4 = |o: &Option<[i32; 4]>| {
        o.map_or([u32::MAX; 5], |a| [0, a[0] as u32, a[1] as u32, a[2] as u32, a[3] as u32])
    };
    k.extend(opt4(moe_inc));
    for s in moe_swizzle {
        k.extend(opt4(s));
    }
    k.extend(moe_base.iter().chain(moe_range).chain(&moe_addr.1).chain(index));
    k.extend(moe_addr.0.iter().map(|&x| x as u32));
    k.extend([quad_i1.map_or(u32::MAX, |v| v), *temps as u32, flag(*fitted), flag(*csc_unloaded)]);
    k.extend(firh_latch.iter().map(|b| b.map_or(u32::MAX, u32::from)));
    k.extend(firh_written.iter().map(|&b| flag(b)));
    k.extend(csc.map_or([u32::MAX; 5], |c| c));
    k.extend(phase.map_or([u32::MAX; 2], |(a, b)| [a as u32, b as u32]));
    k.extend([flag(*vertex_task), *code_index, flag(*edm_task), flag(*mov_dest), u32::from(*locks)]);
    k
}

/// The bus one piece of work sees: memory, the registers, and where its PDS
/// port writes go.
struct Unit<'a> {
    st: &'a mut State,
    bank: Bank,
    /// The primary attributes a PDS program has written for the task it starts.
    pa: [u32; 128],
    written: u128,
    /// The work is a task of ours: one started at `OWN_INDEX` or later.
    own: bool,
}

impl Unit<'_> {
    fn attr(&mut self, n: usize, v: u32) -> Result<(), Error> {
        if n >= 128 {
            return Err(why(format!("attribute {n}")));
        }
        match self.bank {
            Bank::Primary => (self.pa[n], self.written) = (v, self.written | 1 << n),
            Bank::Secondary => (self.st.sa[n], self.st.sa_written) = (v, self.st.sa_written | 1 << n),
        }
        Ok(())
    }
}

impl Bus for Unit<'_> {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.st.load_traced(addr)
    }

    fn store32(&mut self, addr: u32, value: u32) -> Result<(), Error> {
        self.st.effect()?;
        self.st.mem.store(addr, value)?;
        self.st.trace(|| Ev::Store { addr, value });
        Ok(())
    }

    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        let (value, source) = self.st.read(index)?;
        self.st.trace(|| Ev::RegRead { index, value, source });
        Ok(value)
    }

    fn reg_write(&mut self, index: u32, value: u32) -> Result<(), Error> {
        self.st.effect()?;
        self.st.clear_event(index, value)?;
        self.st.store_reg(index, value, false);
        Ok(())
    }

    /// emitpds s0, s1, s2: the control word (data rows at 27:23) and the address >> 4. s2 is
    /// not ir0 or ir1 of the started program (E488: s2 0, 1, 0xFFFFFFFF and 0xE17D0001 gave
    /// ir0.0 3, 3, 2, 3, varying from run to run, and ir1.0 0), so both stay unknown and a
    /// program that reads them is refused, unless the caller assumes `emit_s2_is_ir0`.
    fn emit(&mut self, text: &str, s: [u32; 3]) -> Result<(), Error> {
        if !text.starts_with("emitpds") {
            return Err(why(format!("{text}: no unit for this emit")));
        }
        // E1148, E1149, E1150 (Q128): from our own task the issuer went on past the emit, the
        // started entry never stored and the EDM's tick stopped; the crumb image's first `movs
        // tim` never reached 0x0acc, so the program never ran [infer: a client's does reach it,
        // E1152]. Without the emit the same task ran to done (E1151); a lone `halt` image stopped
        // it as well (E1153), and so did crumb's program with 3 rows and #14's control word in
        // the firmware's own PDS page (E1154): not the program, its page, rows or control word.
        // From a GETMISCINFO kick pass the same word with s2 0 scored CANNOT TELL (E1155); with
        // #14's sideband 0x843 and s2 0x00020000 (the request bit) the emitted program ran and
        // its doutu started our entry to done (E1156). Which of the sideband, s2 and the pass
        // decides is open, and the sim does not know the pass: not a model either way, refused.
        if self.own {
            let sideband = text.rsplit_once('#').and_then(|(_, n)| n.trim().strip_prefix("0x"));
            let sideband = sideband.and_then(|n| u32::from_str_radix(n, 16).ok());
            if sideband == Some(0x843) && s[2] == 0x0002_0000 {
                let tail = "#14's sideband and s2 ran once from a kick pass (E1156); which of the \
                            sideband, s2 and the pass decides is open";
                return Err(why(format!("emitpds from our own task: {tail} (Q128)")));
            }
            let tail = "the emitted program did not start [infer], the tick stopped";
            return Err(why(format!(
                "emitpds from our own task: {tail} (E1148-E1150, E1153, E1154, E1155, Q128)"
            )));
        }
        self.st.effect()?;
        self.st.trace(|| Ev::Emit { s });
        let data = (s[0] >> 23 & 31) as usize * 4;
        // a running timer: the caller's count (E1133); a stopped one: run_pds reads the register
        let running = self.st.regs.get(&reg::EVENT_TIMER).is_some_and(|v| v >> 24 & 1 == 1);
        self.st.queue.push_back(Work::Pds {
            addr: s[1] << 4,
            data,
            ir0: self.st.emit_s2_is_ir0.then_some(s[2]),
            ir1: None,
            tim: if running { self.st.emit_tim } else { None },
            bank: Bank::Secondary,
        });
        Ok(())
    }

    fn fence(&mut self, wait: bool) {
        self.st.trace(|| Ev::Fence { wait });
    }

    fn port(&mut self, port: Port, w: [u32; 4]) -> Result<(), Error> {
        match port {
            // U0: CBASE 3:0, the instruction index 19:4, temporaries in fours
            // 31:24 (pds_isa 3.4); the code base register holds ADDR[24:0] in
            // 128-byte units (hw_spec 11.3)
            Port::Doutu => {
                let cb = self.st.reg(reg::USE_CODE_BASE_0 + (w[0] & 0xf))?;
                let base = (cb & 0x01ff_ffff) << 7;
                let (pc, temps) = ((w[0] >> 4 & 0xffff) as usize, (w[0] >> 24) as usize * 4);
                let (pa, written) = (Box::new(self.pa), self.written);
                self.st.queue.push_back(Work::Task { base, pc, temps, pa, written });
                Ok(())
            }
            // burst ctl[3:0]+1 dwords, lines ctl[7:4]+1, into attribute
            // ctl[19:8], stride ctl[29:22]+1 dwords (attested with
            // the stride equal to the burst only)
            Port::Doutd => {
                let c = w[1];
                let (burst, lines, dst, stride) =
                    ((c & 0xf) + 1, (c >> 4 & 0xf) + 1, (c >> 8 & 0xfff) as usize, (c >> 22 & 0xff) + 1);
                if stride != burst {
                    return Err(why(format!(
                        "doutd with a stride of {stride} for a burst of {burst} is open"
                    )));
                }
                for i in 0..burst * lines {
                    let v = self.st.load_traced(w[0].wrapping_add(4 * i))?;
                    self.attr(dst + i as usize, v)?;
                }
                Ok(())
            }
            // the value, then the attribute in ctl[19:8] (pds_isa 3.4)
            Port::Douta => self.attr((w[1] >> 8 & 0xfff) as usize, w[0]),
            // the first word's bits 24-0 into EVENT_TIMER (pds_isa 8.9)
            Port::Tim => self.reg_write(reg::EVENT_TIMER, w[0] & 0x01ff_ffff),
            p => Err(why(format!("movs to {p:?}: the port is open (pds_isa 3.4)"))),
        }
    }
}

fn why(s: impl Into<String>) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: s.into() }
}

/// Say which piece of work stopped.
fn context(e: Error, what: &str) -> Error {
    match e {
        Error::Unsupported { pc, text, why } => {
            Error::Unsupported { pc, text, why: format!("{what}: {why}") }
        }
        e => e,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const CODE: u32 = 0xE800_0000;
    const DATA: u32 = 0xF000_0000;

    fn usse(src: &str) -> Vec<u8> {
        src.lines()
            .map(str::trim)
            .filter(|l| !l.is_empty())
            .flat_map(|l| usse_isa::encode(l, Core::Sgx545).unwrap_or_else(|| panic!("{l}")).to_le_bytes())
            .collect()
    }

    fn pds(data: &[u32], src: &str) -> Vec<u8> {
        let mut w = data.to_vec();
        w.extend(src.lines().map(str::trim).filter(|l| !l.is_empty()).map(|l| pds_isa::encode(l).unwrap()));
        w.iter().flat_map(|x| x.to_le_bytes()).collect()
    }

    /// An SGX with the EDM code base at CODE (USE_CODE_BASE_15, hw_spec 11.3).
    fn sgx() -> Sgx {
        let mut s = Sgx::default();
        s.write_reg(reg::USE_CODE_BASE_0 + 15, 0x07d0_0000).unwrap();
        s
    }

    /// Where the tests keep the kicker word W (the boot writes its address to EVENT_KICKER).
    const KICKER: u32 = 0xF100_0000;

    /// The kicker word mapped at KICKER with the value `w`, its address in EVENT_KICKER.
    fn with_kicker(s: &mut Sgx, w: u32) {
        s.st.mem.map(KICKER, &w.to_le_bytes());
        s.write_reg(reg::EVENT_KICKER, KICKER).unwrap();
    }

    /// The kernel's kick: W bumped (mod 256), then EVENT_KICK written.
    fn kick(s: &mut Sgx) -> Result<(), Error> {
        let w = s.st.mem.load(KICKER).unwrap();
        s.st.mem.store(KICKER, (w + 1) & 0xff).unwrap();
        s.write_reg(reg::EVENT_KICK, 1)
    }

    /// The doutu code word of instruction `pc` at code base 15 with 8 temporaries.
    fn code_word(pc: u32) -> u32 {
        0x0200_0000 | pc << 4 | 0xf
    }

    #[test]
    fn an_events_douta_words_land_in_sa_64_up_as_pa_too() {
        // S2 e2r: in an EDM task started by the event program pa_n is sa_(64+n); the DOUTA words
        // of the program (pa0, pa2) land in sa64 and sa66, so pa2 and sa66 read the same
        let mut s = sgx();
        s.st.mem.map(
            CODE,
            &usse("mov r0, pa0\nmov r1, pa2\nmov r2, sa64\nmov r3, sa66\nstr #64, r1\nstr #65, r3\nstr #66, r2\nnop.end"),
        );
        let prog = pds(
            &[code_word(0), 0x1111, 0, 0x200, 0x2222, 0, 0, 0],
            "movs douta, ds0[1], ds1[0], ds0[1], ds0[1]\nmovs douta, ds0[2], ds1[1], ds0[2], ds0[2]\n\
             movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 2).unwrap();
        s.write_reg(reg::EVENT_KICK2, 1).unwrap();
        s.run(10_000).unwrap();
        assert_eq!((s.st.regs[&64], s.st.regs[&65], s.st.regs[&66]), (0x2222, 0x2222, 0x1111));
        assert_eq!((s.st.sa[64], s.st.sa[66]), (0x1111, 0x2222));
    }

    #[test]
    fn kick2_runs_the_other_event_program_and_its_task() {
        let mut s = sgx();
        // task: store pa0 to DATA, write register 0x100 from pa1, end
        s.st.mem.map(
            CODE,
            &usse(&format!("mov r0, #0x{DATA:08X}\nstad.bpcache [r0,+#0], pa0\nstr #64, pa1\nnop.end")),
        );
        s.st.mem.map(DATA, &[0; 16]);
        // the event program: douta pa0 = ds0[1], pa1 = ds0[2] (attributes 0 and 1 in ds1[0..1]); doutu
        let prog = pds(
            &[code_word(0), 0x1111, 0, 0x100, 0x2222, 0, 0, 0],
            "movs douta, ds0[1], ds1[0], ds0[1], ds0[1]\nmovs douta, ds0[2], ds1[1], ds0[2], ds0[2]\n\
             movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 2).unwrap();
        s.write_reg(reg::EVENT_KICK2, 1).unwrap();
        s.run(10_000).unwrap();
        assert_eq!(s.st.mem.load(DATA).unwrap(), 0x1111);
        assert_eq!(s.st.regs[&64], 0x2222);
        assert!(s.st.log.contains(&Event::Task { base: CODE, pc: 0, temps: 8 }));
    }

    #[test]
    fn a_kick_runs_the_event_program_with_the_kick_bit() {
        // EVENT_KICK: the other-event program with ir1 bit 8, the host kick
        let mut s = sgx();
        s.alu_specials_in_movs = true;
        s.event_tim = Some(0x0100_1234);
        s.st.mem.map(
            CODE,
            &usse(&format!(
                "mov r0, #0x{DATA:08X}\nstad.bpcache [r0,+#0], pa0\nstad.bpcache [r0,+#1], pa1\nnop.end"
            )),
        );
        s.st.mem.map(DATA, &[0; 16]);
        // pa0 = ir1.l, pa1 = tim.l (the attribute numbers in ds1[0], ds1[1])
        let prog = pds(
            &[code_word(0), 0, 0, 0x100],
            "movs douta, ir1.l, ds1[0], ir1.l, ir1.l\n\
                                                      movs douta, tim.l, ds1[1], tim.l, tim.l\n\
                                                      movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        with_kicker(&mut s, 0);
        kick(&mut s).unwrap();
        s.run(10_000).unwrap();
        assert_eq!(s.st.mem.load(DATA).unwrap(), 0x100);
        assert_eq!(s.st.mem.load(DATA + 4).unwrap(), 0x0100_1234);
    }

    #[test]
    fn every_event_carries_the_count_of_host_kicks_mod_256_a_kicks_own_before_its_bump() {
        // Q290 (E768): pa1 bits 31:24 of every event are the host kicks (EVENT_KICK writes: the
        // boot's and the arm's GETMISCINFO, a client job's command buffer kicks) since the load,
        // mod 256; a kick's own event carries the value before its bump, the next event the
        // bumped one. The sim starts at 0 and does not run the kernel's boot: a caller that
        // wants an armed firmware's 2 sets `event_count`.
        let mut s = sgx();
        s.alu_specials_in_movs = true;
        s.event_ir0 = Some(2);
        s.st.mem.map(CODE, &usse(&format!("mov r0, #0x{DATA:08X}\nstad.bpcache [r0,+#1], pa1\nnop.end")));
        s.st.mem.map(DATA, &[0xff; 16]);
        let prog = pds(
            &[code_word(0), 0, 0, 0x100],
            "movs douta, ir0.l, ds1[0], ir0.l, ir0.l\n\
                                                      movs douta, ir1.l, ds1[1], ir1.l, ir1.l\n\
                                                      movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        fn pa1(s: &mut Sgx, kicked: bool) -> u32 {
            if kicked {
                kick(s).unwrap();
            } else {
                s.event(0).unwrap();
            }
            s.run(10_000).unwrap();
            s.st.mem.load(DATA + 4).unwrap()
        }
        // an armed firmware: the boot's and the arm's GETMISCINFO made it 2, and W with it
        s.event_count = 2;
        with_kicker(&mut s, 2);
        assert_eq!(pa1(&mut s, false), 0x0200_0000);
        assert_eq!(pa1(&mut s, true), 0x0200_0100);
        assert_eq!(pa1(&mut s, false), 0x0300_0000);
        // 254 kicks after 2 wrap the byte to 0 (E768: the logged kicks read 0, 1, 2, 3)
        s.event_count = 2;
        with_kicker(&mut s, 2);
        for _ in 0..254 {
            kick(&mut s).unwrap();
        }
        s.st.queue.clear();
        assert_eq!(s.event_count, 0);
        let kicks: Vec<u32> = (0..4).map(|_| pa1(&mut s, true)).collect();
        assert_eq!(kicks, [0x0000_0100, 0x0100_0100, 0x0200_0100, 0x0300_0100]);
        assert_eq!(pa1(&mut s, false), 0x0400_0000);
        // KICK2 (the boot's own kick of the other-event program) bumps nothing
        let before = s.event_count;
        s.write_reg(reg::EVENT_KICK2, 1).unwrap();
        s.st.queue.clear();
        assert_eq!(s.event_count, before);
    }

    #[test]
    fn two_kicks_queued_behind_a_running_task_are_two_events_with_their_own_counts() {
        // Q290 (E794): two kicks that arrive while a task holds the EDM were logged as two
        // entries, K and K + 1, and the tick after them carried K + 2 (3 of 3 jobs); the sim's
        // queue keeps each kick as its own event, with the count it had when it was written
        let mut s = sgx();
        s.event_count = 2;
        with_kicker(&mut s, 2);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        kick(&mut s).unwrap();
        kick(&mut s).unwrap();
        s.event(0).unwrap();
        let words: Vec<u32> =
            s.st.queue
                .iter()
                .map(|w| match w {
                    Work::Pds { ir1: Some(ir1), .. } => *ir1,
                    _ => panic!("not an event"),
                })
                .collect();
        assert_eq!(words, [0x0200_0100, 0x0300_0100, 0x0400_0000]);
    }

    #[test]
    fn an_event_runs_the_event_program_with_its_inputs() {
        // the timer tick: EVENT_STATUS.TIMER, which the event program gets as ir0 bit 1
        // (the microkernel's tick handler tests pa0 bit 1), nothing in ir1
        let mut s = sgx();
        s.alu_specials_in_movs = true;
        s.event_ir0 = Some(2);
        s.st.mem.map(
            CODE,
            &usse(&format!(
                "mov r0, #0x{DATA:08X}\nstad.bpcache [r0,+#0], pa0\nstad.bpcache [r0,+#1], pa1\nnop.end"
            )),
        );
        s.st.mem.map(DATA, &[0xff; 16]);
        let prog = pds(
            &[code_word(0), 0, 0, 0x100],
            "movs douta, ir0.l, ds1[0], ir0.l, ir0.l\n\
                                                      movs douta, ir1.l, ds1[1], ir1.l, ir1.l\n\
                                                      movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        s.event(0).unwrap();
        s.run(10_000).unwrap();
        assert_eq!((s.st.mem.load(DATA).unwrap(), s.st.mem.load(DATA + 4).unwrap()), (2, 0));
    }

    #[test]
    fn a_traced_task_start_carries_the_event_s_inputs_and_each_pass_ends_traced() {
        // fwsim's C4: the entry of the task an event starts, with pa0 to pa3 as its PDS program
        // wrote them
        let mut s = armed();
        s.alu_specials_in_movs = true;
        s.event_ir0 = Some(2);
        s.st.mem.map(CODE, &usse("nop.end"));
        let prog = pds(
            &[code_word(0), 0, 0, 0x100],
            "movs douta, ir0.l, ds1[0], ir0.l, ir0.l\n\
             movs douta, ir1.l, ds1[1], ir1.l, ir1.l\n\
             movs doutu, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt",
        );
        s.st.mem.map(CODE + 0x1000, &prog);
        let rec = Rc::new(std::cell::RefCell::new(Vec::new()));
        s.trace_to(Box::new(rec.clone()));
        s.event(0).unwrap();
        s.run(10_000).unwrap();
        s.run(10_000).unwrap();
        let ev = rec.borrow().clone();
        assert_eq!(ev[0], Ev::Event { ir0: Some(2), ir1: 0x0200_0000 });
        assert_eq!(ev[1], Ev::PdsStart { addr: CODE + 0x1000, data: 4 });
        assert!(ev.contains(&Ev::TaskStart {
            base: CODE,
            pc: 0,
            pa: [Some(2), Some(0x0200_0000), None, None]
        }));
        // one pass: the second run had nothing queued
        assert_eq!(ev.iter().filter(|e| matches!(e, Ev::Pass { .. })).count(), 1);
        assert_eq!(s.passes, 1);
    }

    #[test]
    fn tim_is_the_event_timer_register() {
        // EVENT_TIMER (0xacc, sgx545defs.h): a movs tim writes it (bits 24-0), a PDS
        // program's tim reads it while it is stopped (bit 24 clear); running, it is unknown
        let mut s = sgx();
        s.st.mem.map(DATA, &[0; 16]);
        let load = pds(&[0xfe00_1234, 0, 0, 0], "movs tim, ds0[0], ds0[1], ds1[0], ds1[1]\nhalt");
        s.st.mem.map(CODE + 0x1000, &load);
        s.st.queue.push_back(Work::Pds {
            addr: CODE + 0x1000,
            data: 4,
            ir0: None,
            ir1: None,
            tim: None,
            bank: Bank::Secondary,
        });
        s.run(100).unwrap();
        assert_eq!(s.st.regs[&reg::EVENT_TIMER], 0x0000_1234);
        assert!(s.st.log.contains(&Event::Write { host: false, index: reg::EVENT_TIMER, value: 0x1234 }));
        let read = pds(&[0, 0, 0, 0], "or ds0[48], tim, ds1[1]\nhalt");
        s.st.mem.map(CODE + 0x2000, &read);
        let run = |s: &mut Sgx| {
            s.st.queue.push_back(Work::Pds {
                addr: CODE + 0x2000,
                data: 4,
                ir0: None,
                ir1: None,
                tim: None,
                bank: Bank::Secondary,
            });
            s.run(100)
        };
        run(&mut s).unwrap();
        assert_eq!(s.pds.ds[0][48], 0x1234);
        // the firmware's own setting (enable set, 400000): counting, so unknown
        s.write_reg(reg::EVENT_TIMER, 0x0106_1a80).unwrap();
        assert!(matches!(run(&mut s), Err(Error::Unsupported { ref why, .. }) if why.contains("tim")));
    }

    #[test]
    fn the_host_reads_a_pds_tim_write_at_0x0acc() {
        // E1152 (r38-n3c-s1 th): a client fill's PDS `movs tim` of 0x00abcde0 replaced the
        // running count the host sampled at 0x0acc and held to the reset, as the PDS read it
        // back: one register, the host's read is the program's write
        let mut s = sgx();
        s.st.mem.map(DATA, &[0; 16]);
        s.write_reg(reg::EVENT_TIMER, 0x0106_1a80).unwrap();
        let load = pds(&[0x00ab_cde0, 0, 0, 0], "movs tim, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt");
        s.st.mem.map(CODE + 0x1000, &load);
        s.st.queue.push_back(Work::Pds {
            addr: CODE + 0x1000,
            data: 4,
            ir0: None,
            ir1: None,
            tim: None,
            bank: Bank::Secondary,
        });
        s.run(100).unwrap();
        assert!(matches!(s.st.read(reg::EVENT_TIMER), Ok((0x00ab_cde0, Source::Written))));
        // bit 24 clear: stopped, so a later read is the same value
        assert!(matches!(s.st.read(reg::EVENT_TIMER), Ok((0x00ab_cde0, _))));
    }

    #[test]
    fn an_emitted_program_reads_the_callers_running_count() {
        // E1133: while the timer runs (bit 24 set) its count is a running count, bits 23:0 at
        // most 400000, at a phase no row gives; an emitted program's tim is the caller's
        // `emit_tim`, refused without one, and a stopped timer is read from the register
        let mut s = sgx();
        s.st.mem.map(DATA, &[0; 16]);
        s.st.mem.map(CODE + 0x1000, &pds(&[0, 0, 0, 0], "or ds0[48], tim, ds1[1]\nhalt"));
        s.st.mem.map(CODE, &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nemitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end"));
        let go = |s: &mut Sgx| {
            let mut pa = [0; 128];
            (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x1000) >> 4, 7);
            s.st.queue.push_back(Work::Task {
                base: CODE,
                pc: 0,
                temps: 8,
                pa: Box::new(pa),
                written: 0b10101,
            });
            s.run(10_000)
        };
        s.write_reg(reg::EVENT_TIMER, 0x0106_1a80).unwrap();
        assert!(matches!(go(&mut s), Err(Error::Unsupported { ref why, .. }) if why.contains("tim")));
        let mut s2 = sgx();
        s2.st.mem.map(DATA, &[0; 16]);
        s2.st.mem.map(CODE + 0x1000, &pds(&[0, 0, 0, 0], "or ds0[48], tim, ds1[1]\nhalt"));
        s2.st.mem.map(CODE, &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nemitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end"));
        s2.write_reg(reg::EVENT_TIMER, 0x0106_1a80).unwrap();
        s2.set_emit_tim(Some(0x0102_0304)).unwrap();
        go(&mut s2).unwrap();
        assert_eq!(s2.pds.ds[0][48], 0x0102_0304);
        // stopped (bit 24 clear): the register, not the caller's count
        s2.write_reg(reg::EVENT_TIMER, 0x0000_0042).unwrap();
        go(&mut s2).unwrap();
        assert_eq!(s2.pds.ds[0][48], 0x42);
        // the rule: bit 24 alone in 31:24, bits 23:0 at most 400000
        for bad in [0x0106_1a81u32, 0x0002_0000, 0x0300_0000] {
            assert!(s2.set_emit_tim(Some(bad)).is_err(), "{bad:#x}");
        }
        assert!(s2.set_emit_tim(Some(0x0106_1a80)).is_ok() && s2.set_emit_tim(None).is_ok());
    }

    #[test]
    fn an_emit_and_the_fences_are_traced_with_values_only() {
        // fwsim (N3d O2): a trace reader needs the emit's three operand values and where a
        // task fences, without instruction text: an emit event carries s0-s2, a fence event
        // whether it issues (idf) or waits (wdf)
        let mut s = sgx();
        s.st.mem.map(DATA, &[0; 16]);
        s.st.mem.map(CODE + 0x1000, &pds(&[0, 0, 0, 0], "halt"));
        s.st.mem.map(
            CODE,
            &usse(
                "mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nidf drc0, bif\nwdf drc0\n\
                 emitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nwdf drc0\nnop.end",
            ),
        );
        let mut pa = [0; 128];
        (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x1000) >> 4, 0x0002_0000);
        s.st.queue.push_back(Work::Task { base: CODE, pc: 0, temps: 8, pa: Box::new(pa), written: 0b10101 });
        let rec = Rc::new(std::cell::RefCell::new(Vec::new()));
        s.trace_to(Box::new(rec.clone()));
        s.run(10_000).unwrap();
        let ev: Vec<Ev> = rec
            .borrow()
            .iter()
            .filter(|e| matches!(e, Ev::Emit { .. } | Ev::Fence { .. } | Ev::PdsStart { .. }))
            .cloned()
            .collect();
        assert_eq!(
            ev,
            [
                Ev::Fence { wait: false },
                Ev::Fence { wait: true },
                Ev::Emit { s: [1 << 23, (CODE + 0x1000) >> 4, 0x0002_0000] },
                Ev::Fence { wait: true },
                Ev::PdsStart { addr: CODE + 0x1000, data: 4 },
            ]
        );
        for e in &ev {
            let j = e.json();
            assert!(!["idf", "wdf", "emit"].iter().any(|w| j.contains(w)), "{j}");
        }
    }

    #[test]
    fn the_secondaries_persist_into_the_next_task() {
        let mut s = sgx();
        s.st.mem.map(DATA, &(0..8u32).flat_map(|i| (0xA0 + i).to_le_bytes()).collect::<Vec<_>>());
        let ctl = 0x01c0_0407;
        s.st.mem.map(
            CODE + 0x1000,
            &pds(
                &[DATA, ctl, code_word(2), 0],
                "movs doutd, ds0[0], ds0[1], ds0[0], ds0[0]\n\
                 movs doutu, ds1[0], ds1[0], ds1[0], ds1[0]\nhalt",
            ),
        );
        s.st.mem.map(
            CODE,
            &usse(
                "emitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end\nstr #65, sa5\nnop.end",
            ),
        );
        let mut pa = [0; 128];
        (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x1000) >> 4, 7);
        // r0, r2, r4 come from a mov the test skips: start with them in pa and copy
        s.st.mem.map(
            CODE + 0x2000,
            &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nemitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end"),
        );
        s.st.queue.push_back(Work::Task {
            base: CODE + 0x2000,
            pc: 0,
            temps: 8,
            pa: Box::new(pa),
            written: 0b10101,
        });
        s.run(10_000).unwrap();
        // sa4.. = DATA's dwords; the task at insn 2 wrote register 65 from sa5
        assert_eq!(&s.st.sa[4..12], &[0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7]);
        assert_eq!(s.st.regs[&65], 0xA1);
        // E488: s2 is not ir0 of the started program: unknown unless assumed
        assert!(s.st.log.contains(&Event::Pds { addr: CODE + 0x1000, data: 4, ir0: None }));
    }

    #[test]
    fn the_s2_is_ir0_assumption_gives_the_program_s2() {
        let mut s = sgx();
        s.emit_s2_is_ir0 = true;
        s.st.mem.map(DATA, &[0; 16]);
        s.st.mem.map(CODE + 0x1000, &pds(&[0, 0, 0, 0], "mov32 ds0[48], ir0.0\nhalt"));
        s.st.mem.map(CODE, &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nemitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end"));
        let mut pa = [0; 128];
        (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x1000) >> 4, 7);
        s.st.queue.push_back(Work::Task { base: CODE, pc: 0, temps: 8, pa: Box::new(pa), written: 0b10101 });
        s.run(10_000).unwrap();
        assert_eq!(s.pds.ds[0][48], 7);
    }

    #[test]
    fn an_emitted_program_does_not_get_s2_as_ir0() {
        // E488: with s2 0, 1, 0xFFFFFFFF and 0xE17D0001 the program saw ir0.0 3, 3, 2, 3 (a
        // number that moves from run to run) and ir1.0 0: s2 is neither, and ir0 is not a rule
        // of the operands, so a program that reads ir0 or ir1 is refused
        for s2 in [0u32, 1, 0xFFFF_FFFF, 0xE17D_0001] {
            let mut s = sgx();
            s.st.mem.map(DATA, &[0; 16]);
            s.st.mem.map(CODE + 0x1000, &pds(&[0, 0, 0, 0], "mov32 ds0[48], ir0.0\nhalt"));
            s.st.mem.map(CODE, &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nemitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end"));
            let mut pa = [0; 128];
            (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x1000) >> 4, s2);
            s.st.queue.push_back(Work::Task {
                base: CODE,
                pc: 0,
                temps: 8,
                pa: Box::new(pa),
                written: 0b10101,
            });
            let r = s.run(10_000);
            assert!(
                matches!(r, Err(Error::Unsupported { ref why, .. }) if why.contains("ir0")),
                "s2 {s2:#x}: {r:?}"
            );
        }
    }

    #[test]
    fn unknown_registers_and_open_dmas_stop() {
        let mut s = sgx();
        assert!(matches!(s.write_reg(reg::EVENT_KICK2, 1), Err(Error::Unsupported { .. })));
        let mut s = sgx();
        s.st.mem.map(CODE, &usse("ldr r0, #7, drc0\nwdf drc0\nnop.end"));
        s.st.queue.push_back(Work::Task { base: CODE, pc: 0, temps: 8, pa: Box::new([0; 128]), written: 0 });
        assert!(matches!(s.run(100), Err(Error::Unsupported { ref why, .. }) if why.contains("0x001c")));
        s.seed(7, 0x0115_0000);
        s.st.queue.push_back(Work::Task { base: CODE, pc: 0, temps: 8, pa: Box::new([0; 128]), written: 0 });
        s.run(100).unwrap();
    }

    /// An armed SGX (count 2, W 2) with an event program and nothing queued.
    fn armed() -> Sgx {
        let mut s = sgx();
        s.event_count = 2;
        with_kicker(&mut s, 2);
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        s
    }

    fn queued_words(s: &Sgx) -> Vec<u32> {
        s.st.queue
            .iter()
            .map(|w| match w {
                Work::Pds { ir1: Some(ir1), .. } => *ir1,
                _ => panic!("not an event"),
            })
            .collect()
    }

    fn refused(r: Result<(), Error>) -> bool {
        matches!(r, Err(Error::Unsupported { .. }))
    }

    #[test]
    fn a_kick_without_the_bump_is_not_consumed() {
        // E819 Q3, 3 of 3: the EVENT_KICK write with W unchanged raised no kick entry, the count
        // and W stayed, the command was not answered; what follows it (whether an event stays
        // pending, the count and pa2 of the ticks after it: Q290) is refused, as is a second kick
        // (row Q4 has not run)
        let mut s = armed();
        s.write_reg(reg::EVENT_KICK, 1).unwrap();
        assert!(queued_words(&s).is_empty());
        assert_eq!(s.event_count, 2);
        assert_eq!(s.st.mem.load(KICKER).unwrap(), 2);
        assert!(s.kick_unconsumed);
        assert!(matches!(s.event(0), Err(Error::Unsupported { ref why, .. }) if why.contains("Q290")));
        assert!(refused(kick(&mut s)));
        assert!(refused(s.write_reg(reg::EVENT_KICK, 1)));
    }

    #[test]
    fn writing_the_kicker_word_alone_changes_nothing() {
        // E819 Q1, 3 of 3: W = 0x42 with no kick, the ticks after it carried the count 2
        let mut s = armed();
        s.st.mem.store(KICKER, 0x42).unwrap();
        s.event(0).unwrap();
        assert_eq!(queued_words(&s), [0x0200_0000]);
        assert!(!s.kick_unconsumed);
    }

    #[test]
    fn a_kick_after_the_kicker_word_was_set_is_refused() {
        // E819 Q2 could not read the count after it (H-LATCH 0x43 against H-CNT 3): row Q2'
        let mut s = armed();
        s.st.mem.store(KICKER, 0x42).unwrap();
        assert!(matches!(kick(&mut s), Err(Error::Unsupported { ref why, .. }) if why.contains("Q290")));
        assert!(queued_words(&s).is_empty());
        assert_eq!(s.event_count, 2);
    }

    #[test]
    fn a_kick_reads_the_kicker_word_where_event_kicker_points() {
        // CR_EVENT_KICKER (0x0ac4) holds the word's address, bits 31:4 (boot_sequence.md, E006):
        // without it the kick is refused, as any register nobody wrote
        let mut s = sgx();
        s.write_reg(reg::EVENT_OTHER_PDS_EXEC, CODE + 0x1000).unwrap();
        s.write_reg(reg::EVENT_OTHER_PDS_DATA, 1).unwrap();
        assert!(refused(s.write_reg(reg::EVENT_KICK, 1)));
        assert_eq!(reg::EVENT_KICKER, 0x0ac4 / 4);
        // the low four bits of the register are not the address
        let mut s = armed();
        s.write_reg(reg::EVENT_KICKER, KICKER | 0xf).unwrap();
        kick(&mut s).unwrap();
        assert_eq!(queued_words(&s), [0x0200_0100]);
        assert_eq!(s.event_count, 3);
    }

    fn status2_after(by_task: bool, status2: u32, clear: u32) -> Result<u32, Error> {
        let mut s = sgx();
        s.seed(reg::EVENT_STATUS2, status2);
        if by_task {
            s.st.mem.map(CODE, &usse(&format!("mov r0, #0x{clear:08X}\nstr #69, r0\nnop.end")));
            s.st.queue.push_back(Work::Task {
                base: CODE,
                pc: 0,
                temps: 8,
                pa: Box::new([0; 128]),
                written: 0,
            });
            s.run(100)?;
        } else {
            s.write_reg(reg::EVENT_HOST_CLEAR2, clear)?;
        }
        Ok(s.st.regs[&reg::EVENT_STATUS2])
    }

    #[test]
    fn host_clear2_clears_the_bits_written_of_the_latched_status2_bit_6() {
        // E821 (host) and E822 (a task's str #69), 3 of 3 rounds each: STATUS2 0x440 after a loop
        // fill; bit 15 (not set) leaves it, bit 6 clears bit 6 alone
        assert_eq!((reg::EVENT_HOST_CLEAR2, reg::EVENT_STATUS2), (0x0114 / 4, 0x0118 / 4));
        for by_task in [false, true] {
            assert_eq!(status2_after(by_task, 0x440, 0x40).unwrap(), 0x400, "task {by_task}");
            assert_eq!(status2_after(by_task, 0x440, 0x8000).unwrap(), 0x440, "task {by_task}");
            // other writes and other latched states were not run
            for (st, clear) in
                [(0x440, 0x400), (0x440, 0x8040), (0x440, 0x1), (0x400, 0x40), (0x8440, 0x8000)]
            {
                assert!(
                    refused(status2_after(by_task, st, clear).map(|_| ())),
                    "{st:#x} {clear:#x} task {by_task}"
                );
            }
        }
    }

    #[test]
    fn host_clear_of_status_bit_18_is_refused() {
        // E823: one job, post hoc (row B1P has not run); with STATUS known a write of bit 18 to
        // CR_EVENT_HOST_CLEAR (0x0134) is refused
        assert_eq!((reg::EVENT_HOST_CLEAR, reg::EVENT_STATUS), (0x0134 / 4, 0x012c / 4));
        let mut s = sgx();
        s.seed(reg::EVENT_STATUS, 0x2004_0000);
        assert!(refused(s.write_reg(reg::EVENT_HOST_CLEAR, 1 << 18)));
        assert_eq!(s.st.regs[&reg::EVENT_STATUS], 0x2004_0000);
    }

    fn task_at(s: &mut Sgx, pc: usize) {
        s.st.queue.push_back(Work::Task { base: CODE, pc, temps: 32, pa: Box::new([0; 128]), written: 0 });
    }

    #[test]
    fn a_task_past_the_default_window_runs_only_with_a_longer_code_window() {
        // our own tasks sit at instruction 0x4000 of the EDM code base (the page the kernel maps
        // at heap + 0x20000, tools/fwtask OWN_INDEX); the default window ends before it
        let mut s = sgx();
        s.st.mem.map(CODE, &vec![0; 0x20000]);
        s.st.mem.map(CODE + 0x20000, &usse("mov r1, #5\nstr #65, r1\nnop.end"));
        task_at(&mut s, 0x4000);
        assert!(s.run(100).is_err());
        let mut s = sgx();
        s.st.mem.map(CODE, &vec![0; 0x20000]);
        s.st.mem.map(CODE + 0x20000, &usse("mov r1, #5\nstr #65, r1\nnop.end"));
        s.code_len = Some(0x4000 + 3);
        task_at(&mut s, 0x4000);
        s.run(100).unwrap();
        assert_eq!(s.st.regs[&65], 5);
    }

    #[test]
    fn an_emitpds_from_our_own_tasks_page_is_refused() {
        // E1148, E1149, E1150 (Q128): from our own task (instruction 0x4000 on) the firmware's
        // emitpds form went on in the issuer, the started entry never stored, the EDM's tick
        // stopped, and the crumb image's first `movs tim` never showed: the emitted program
        // did not run [infer]. The simulator would run it and start the task, so it refuses.
        let emit = "mov r0, pa0\nmov r2, pa2\nmov r4, pa4\n\
                    emitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end";
        let go = |own: bool| {
            let mut s = sgx();
            s.st.mem.map(DATA, &[0; 16]);
            s.st.mem.map(CODE + 0x100000, &pds(&[0, 0, 0, 0], "halt"));
            let pc = if own { 0x4000 } else { 0 };
            if own {
                s.st.mem.map(CODE, &vec![0; 0x20000]);
            }
            s.st.mem.map(CODE + 8 * pc as u32, &usse(emit));
            s.code_len = Some(0x4000 + 8);
            let mut pa = [0; 128];
            (pa[0], pa[2], pa[4]) = (1 << 23, (CODE + 0x100000) >> 4, 7);
            s.st.queue.push_back(Work::Task { base: CODE, pc, temps: 8, pa: Box::new(pa), written: 0b10101 });
            s.run(10_000)
        };
        go(false).unwrap();
        assert!(matches!(go(true), Err(Error::Unsupported { ref why, .. })
            if why.contains("E1150") && why.contains("own task")));
        // E1151 (r38-n3c-s1 n0): the same task without the emit ran to done with the tick
        // going, so only the emit is refused: the rest of an own task's page runs
        let mut s = sgx();
        s.st.mem.map(DATA, &[0; 16]);
        s.st.mem.map(CODE, &vec![0; 0x20000]);
        s.st.mem.map(CODE + 8 * 0x4000, &usse("mov r0, pa0\nmov r2, pa2\nmov r4, pa4\nnop.end"));
        s.code_len = Some(0x4000 + 8);
        s.st.queue.push_back(Work::Task {
            base: CODE,
            pc: 0x4000,
            temps: 8,
            pa: Box::new([0; 128]),
            written: 0b10101,
        });
        s.run(10_000).unwrap();
    }

    #[test]
    fn an_own_task_emit_is_refused_whatever_the_program_page_rows_or_control() {
        // E1153 (r38-n3c-s4 H): a lone `halt` image (2 rows, control 0x01000100, the kernel's
        // own page) stopped the tick as v1 and crumb did, so no instruction of the program is
        // needed; E1154 (r38-n3c-s3 M): crumb's program with 3 rows and #14's control word
        // 0x01800100, in the firmware's own PDS page past #14's image, never started either.
        // The refusal does not depend on the program, its page, its rows or its control word.
        let emit = "mov r0, pa0\nmov r2, pa2\nmov r4, pa4\n\
                    emitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x00000843\nnop.end";
        let crumb = "movs tim, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt";
        for (rows, at, prog) in [(2u32, 0x100000u32, "halt"), (3, 0x80100, crumb)] {
            let mut s = sgx();
            s.st.mem.map(DATA, &[0; 16]);
            s.st.mem.map(CODE, &vec![0; 0x20000]);
            s.st.mem.map(CODE + at, &pds(&vec![0; rows as usize * 4], prog));
            s.st.mem.map(CODE + 8 * 0x4000, &usse(emit));
            s.code_len = Some(0x4000 + 8);
            let mut pa = [0; 128];
            (pa[0], pa[2], pa[4]) = (rows << 23 | 0x100, (CODE + at) >> 4, 0);
            s.st.queue.push_back(Work::Task {
                base: CODE,
                pc: 0x4000,
                temps: 8,
                pa: Box::new(pa),
                written: 0b10101,
            });
            assert!(matches!(s.run(10_000), Err(Error::Unsupported { ref why, .. })
                if why.contains("E1153") && why.contains("E1154") && why.contains("own task")));
        }
    }

    #[test]
    fn an_own_task_emit_with_14s_sideband_and_s2_is_refused_citing_the_one_run() {
        // E1156 (r39-n3d-z Z): from a GETMISCINFO kick pass, our word with #14's sideband 0x843
        // and s2 0x00020000 (the request bit) started crumb3 in #14's page; it ran to its last
        // `tim` marker and its doutu started our entry 1 to done. Which of the sideband, s2 and
        // the kick pass decides is open (Q128), so the simulator still refuses, naming the run;
        // E1155 (r39-n3d-k K: our word, s2 0, a kick pass) scored CANNOT TELL.
        let crumb = "movs tim, ds0[0], ds0[0], ds0[0], ds0[0]\nhalt";
        for (sideband, s2, ran) in [(0x843u32, 0x0002_0000u32, true), (0, 0, false), (0x843, 0, false)] {
            let emit = format!(
                "mov r0, pa0\nmov r2, pa2\nmov r4, pa4\n\
                 emitpds.tasks.taske #0 /* incp */, r0, r2, r4, #0x{sideband:08x}\nnop.end"
            );
            let mut s = sgx();
            s.st.mem.map(DATA, &[0; 16]);
            s.st.mem.map(CODE, &vec![0; 0x20000]);
            s.st.mem.map(CODE + 0x80100, &pds(&[0; 12], crumb));
            s.st.mem.map(CODE + 8 * 0x4000, &usse(&emit));
            s.code_len = Some(0x4000 + 8);
            let mut pa = [0; 128];
            (pa[0], pa[2], pa[4]) = (3 << 23 | 0x100, (CODE + 0x80100) >> 4, s2);
            s.st.queue.push_back(Work::Task {
                base: CODE,
                pc: 0x4000,
                temps: 8,
                pa: Box::new(pa),
                written: 0b10101,
            });
            let r = s.run(10_000);
            assert!(
                matches!(r, Err(Error::Unsupported { ref why, .. })
                if why.contains("own task") && why.contains("Q128")
                    && why.contains("E1156") == ran && why.contains("E1155") != ran),
                "{r:?}"
            );
        }
    }

    #[test]
    fn without_a_carry_each_task_starts_with_pclink_and_the_predicates_unwritten() {
        let mut s = sgx();
        s.st.mem.map(CODE, &usse("mov r1, pclink\nstr #65, r1\nnop.end"));
        task_at(&mut s, 0);
        assert!(refused(s.run(100)));
    }

    /// A hardware model replaying CR_EVENT_STATUS after a kick's CR_CACHE_CTRL write, armed.
    fn replaying(s: &mut Sgx) {
        use crate::hw::{CACHE_CTRL, EVENT_STATUS};
        let mut hw = HwModel::default();
        hw.replay(
            EVENT_STATUS,
            (CACHE_CTRL, 0x1000_ffff),
            &[0x2000_0000, 0x2400_0000, 0x2000_0000],
            &["the rise", "the fall", "after the fall"],
            "E1115",
        )
        .unwrap();
        hw.on_event(Some(0), 0x0200_0100);
        hw.on_write(CACHE_CTRL, 0x1000_ffff);
        s.st.hw = Some(hw);
    }

    #[test]
    fn a_task_spinning_on_a_replayed_register_moves_on_with_the_kept_order() {
        // the poll's state is the same at each read while the word lacks bit 26: a spin, so it
        // reads the next kept word and goes on to its write
        let mut s = sgx();
        replaying(&mut s);
        let poll = "mov r1, #0x04000000\nldr r0, #75, drc0\nwdf drc0\nand.testtaz.chan0 !c0, p0, r0, r1\n\
                    p0 br -#0x00000003\nstr #77, r1\nnop.end";
        s.st.mem.map(CODE, &usse(poll));
        task_at(&mut s, 0);
        s.run(1000).unwrap();
        assert_eq!(s.st.regs[&reg::EVENT_HOST_CLEAR], 0x0400_0000);
        let hw = s.st.hw.as_ref().unwrap();
        assert_eq!(hw.answered["replay"], 3);
        assert_eq!(hw.replay_log().len(), 1);
    }

    #[test]
    fn a_read_the_task_acts_on_without_a_spin_stops_naming_the_measurement() {
        // read once and written on: whether the word had changed by then is a time
        let mut s = sgx();
        replaying(&mut s);
        s.st.mem.map(CODE, &usse("ldr r0, #75, drc0\nwdf drc0\nstr #64, r0\nnop.end"));
        task_at(&mut s, 0);
        let r = s.run(1000);
        assert!(matches!(r, Err(Error::Unsupported { ref why, .. }) if why.contains("the rise")), "{r:?}");
        assert!(!s.st.regs.contains_key(&64));
    }

    #[test]
    fn a_poll_that_counts_is_no_spin() {
        // a loop whose state changes at every read never proves a spin: the step limit, not a word
        let mut s = sgx();
        replaying(&mut s);
        let poll = "mov r1, #0x04000000\nmov r2, #0x00000000\nmov r3, #0x00000001\nldr r0, #75, drc0\nwdf drc0\n\
                    iadd32.skipinv.testtanz.chan0 r2, p1, r3, r2\nand.testtaz.chan0 !c0, p0, r0, r1\np0 br -#0x00000004\nnop.end";
        s.st.mem.map(CODE, &usse(poll));
        task_at(&mut s, 0);
        assert_eq!(s.run(500), Err(Error::StepLimit));
        assert!(s.st.hw.as_ref().unwrap().replay_log().is_empty());
    }

    #[test]
    fn under_a_hardware_model_every_read_has_one_source_or_the_run_stops() {
        // fwsim: a read is a run write, a cited seed, a landed rule or a kept reset value
        let task = |s: &mut Sgx| {
            s.st.mem.map(CODE, &usse("ldr r0, #16, drc0\nwdf drc0\nstr #64, r0\nnop.end"));
            task_at(s, 0);
            s.run(100)
        };
        let mut s = sgx();
        s.seed(16, 0x55);
        s.st.hw = Some(HwModel::default());
        // a legacy seed cites nothing: under the model it answers nothing
        assert!(refused(task(&mut s)));
        assert_eq!(s.st.hw.as_ref().unwrap().refused.get(&16), Some(&1));
        let mut hw = HwModel::default();
        hw.reset(16, 0x1e00);
        s.st.hw = Some(hw);
        task(&mut s).unwrap();
        assert_eq!(s.st.regs[&64], 0x1e00);
        assert_eq!(s.st.hw.as_ref().unwrap().answered["reset"], 1);
    }

    #[test]
    fn the_served_event_count_follows_the_ticks_the_sgx_delivers() {
        let mut s = armed();
        let mut hw = HwModel::default();
        hw.count_serv_events(0x0001_0003, "E009").unwrap();
        s.st.hw = Some(hw);
        s.event_ir0 = Some(2);
        s.event(0).unwrap();
        s.event(0).unwrap();
        s.st.queue.clear();
        assert_eq!(s.st.read(crate::hw::USE0_SERV_EVENT).unwrap(), (0x0001_0005, Source::Rule("E009")));
        s.event_ir0 = Some(0);
        kick(&mut s).unwrap();
        assert!(s.st.read(crate::hw::USE0_SERV_EVENT).is_err());
    }

    #[test]
    fn a_seeded_carry_gives_each_task_what_the_task_before_left() {
        // E536: pclink, p1 to p3, r20, r21, i0 and i1 at a task's entry were as the task before
        // left them; the first entry is seeded with what a run read there
        let mut s = sgx();
        s.st.mem.map(
            CODE,
            &usse(
                "mov r1, pclink\nstr #65, r1\nmov r1, r20\nstr #66, r1\nmov r1, i0\nstr #67, r1\n\
                 p0 mov r2, #9\nstr #68, r2\n\
                 mov r3, #6\nmov pclink, r3\nmov r20, #0x00000044\nnop.end",
            ),
        );
        s.carry = Some(Carry {
            pclink: Some(0x98),
            p: [Some(true), None, None, None],
            r20: Some(0x11),
            i0: Some(0x22),
            ..Carry::default()
        });
        task_at(&mut s, 0);
        s.run(1000).unwrap();
        assert_eq!([65, 66, 67, 68].map(|r| s.st.regs[&r]), [0x98, 0x11, 0x22, 9]);
        let c = s.carry.clone().unwrap();
        assert_eq!((c.pclink, c.r20, c.i0, c.p[0]), (Some(6), Some(0x44), Some(0x22), Some(true)));
        task_at(&mut s, 0);
        s.run(1000).unwrap();
        assert_eq!([65, 66].map(|r| s.st.regs[&r]), [6, 0x44]);
    }
}
