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
//! hardware, stops the run.

use crate::pds::{self, Pds, Port};
use crate::{Bus, Error, Machine, Program};
use std::collections::{BTreeMap, HashMap, VecDeque};
use std::rc::Rc;
use usse_isa::Core;

/// SGX register dword indices (offset / 4) the loop itself acts on.
pub mod reg {
    pub const USE_CODE_BASE_0: u32 = 0x0a0c / 4;
    pub const EVENT_OTHER_PDS_EXEC: u32 = 0x0a68 / 4;
    pub const EVENT_OTHER_PDS_DATA: u32 = 0x0a6c / 4;
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
    queue: VecDeque<Work>,
}

impl Default for State {
    fn default() -> State {
        State {
            mem: Memory::default(),
            regs: BTreeMap::new(),
            log: Vec::new(),
            sa: [0; 128],
            sa_written: 0,
            queue: VecDeque::new(),
        }
    }
}

impl State {
    fn reg(&self, index: u32) -> Result<u32, Error> {
        self.regs
            .get(&index)
            .copied()
            .ok_or_else(|| why(format!("reads register 0x{:04x} before anything wrote it", index * 4)))
    }
}

/// The SGX.
#[derive(Default)]
pub struct Sgx {
    pub st: State,
    pub pds: Pds,
    /// USSE programs by code base, decoded once.
    programs: HashMap<u32, Rc<Program>>,
    pub steps: usize,
    /// An event program's ir0 and the counter it reads (tim), which the hardware gives and
    /// nothing here models.
    pub event_ir0: Option<u32>,
    pub event_tim: Option<u32>,
    /// pds::Pds::alu_specials_in_movs for every program (an assumption, off by default).
    pub alu_specials_in_movs: bool,
}

/// The longest program read from a code base, in instructions.
const MAX_CODE: usize = 0x4000;

impl Sgx {
    /// A register value known from the hardware, readable before anything writes it.
    pub fn seed(&mut self, index: u32, value: u32) {
        self.st.regs.insert(index, value);
    }

    /// A host register write (an init script, a kick).
    pub fn write_reg(&mut self, index: u32, value: u32) -> Result<(), Error> {
        self.st.regs.insert(index, value);
        self.st.log.push(Event::Write { host: true, index, value });
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
        if index == reg::EVENT_KICK && value & 1 != 0 {
            self.event(1 << 8)?;
        }
        Ok(())
    }

    /// An event: the other-event PDS program with the event word `ir1`, and the ir0 and
    /// counter the caller set (`event_ir0`, `event_tim`). The timer tick is ir0 bit 1 with
    /// nothing in ir1 (the microkernel's tick handler tests pa0 bit 1).
    pub fn event(&mut self, ir1: u32) -> Result<(), Error> {
        let addr = self.st.reg(reg::EVENT_OTHER_PDS_EXEC)? & !0xf;
        let data = self.st.reg(reg::EVENT_OTHER_PDS_DATA)? as usize * 4;
        let (ir0, tim) = (self.event_ir0, self.event_tim);
        self.st.queue.push_back(Work::Pds { addr, data, ir0, ir1: Some(ir1), tim, bank: Bank::Primary });
        Ok(())
    }

    /// Run the queued work until none is left.
    pub fn run(&mut self, max_steps: usize) -> Result<(), Error> {
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
        let prog = pds::Program::new(&self.st.mem.words(addr, data + 256), data);
        self.pds.ir = [ir0, ir1, None];
        self.pds.alu_specials_in_movs = self.alu_specials_in_movs;
        // tim is EVENT_TIMER: known while it is stopped; the caller may give a running value
        self.pds.tim = tim.or_else(|| {
            self.st.regs.get(&reg::EVENT_TIMER).filter(|v| *v >> 24 & 1 == 0).map(|v| v & 0x01ff_ffff)
        });
        self.pds.ifs = [None; 2];
        let mut bus = Unit { st: &mut self.st, bank, pa: [0; 128], written: 0 };
        let r = self.pds.run(&prog, &mut bus, max - self.steps);
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
        let prog = match self.programs.get(&base) {
            Some(p) => p.clone(),
            None => {
                let w: Vec<u64> = self
                    .st
                    .mem
                    .words(base, 2 * MAX_CODE)
                    .chunks_exact(2)
                    .map(|d| d[0] as u64 | (d[1] as u64) << 32)
                    .collect();
                let p = Rc::new(Program::new(&w, Core::Sgx545));
                self.programs.insert(base, p.clone());
                p
            }
        };
        let mut m = Machine { temps, pc, pa: *pa, sa: self.st.sa, ..Machine::default() };
        m.written.pa = written;
        m.written.sa = self.st.sa_written;
        let mut bus = Unit { st: &mut self.st, bank: Bank::Secondary, pa: [0; 128], written: 0 };
        let r = m.run(&prog, &mut bus, max - self.steps);
        self.steps += m.steps;
        // the secondary attributes outlive the task
        (self.st.sa, self.st.sa_written) = (m.sa, m.written.sa);
        r.map_err(|e| context(e, &format!("task 0x{base:08x}+{pc:#x}")))
    }
}

/// The bus one piece of work sees: memory, the registers, and where its PDS
/// port writes go.
struct Unit<'a> {
    st: &'a mut State,
    bank: Bank,
    /// The primary attributes a PDS program has written for the task it starts.
    pa: [u32; 128],
    written: u128,
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
        self.st.mem.load(addr)
    }

    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        self.st.mem.store(addr, v)
    }

    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        self.st.reg(index)
    }

    fn reg_write(&mut self, index: u32, value: u32) -> Result<(), Error> {
        self.st.regs.insert(index, value);
        self.st.log.push(Event::Write { host: false, index, value });
        Ok(())
    }

    /// emitpds s0, s1, s2: the control word (data rows at 27:23), the address
    /// >> 4, and ir0 for the program (hw_spec 11.2).
    fn emit(&mut self, text: &str, s: [u32; 3]) -> Result<(), Error> {
        if !text.starts_with("emitpds") {
            return Err(why(format!("{text}: no unit for this emit")));
        }
        let data = (s[0] >> 23 & 31) as usize * 4;
        self.st.queue.push_back(Work::Pds {
            addr: s[1] << 4,
            data,
            ir0: Some(s[2]),
            ir1: None,
            tim: None,
            bank: Bank::Secondary,
        });
        Ok(())
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
                    let v = self.st.mem.load(w[0].wrapping_add(4 * i))?;
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

    /// The doutu code word of instruction `pc` at code base 15 with 8 temporaries.
    fn code_word(pc: u32) -> u32 {
        0x0200_0000 | pc << 4 | 0xf
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
        s.write_reg(reg::EVENT_KICK, 1).unwrap();
        s.run(10_000).unwrap();
        assert_eq!(s.st.mem.load(DATA).unwrap(), 0x100);
        assert_eq!(s.st.mem.load(DATA + 4).unwrap(), 0x0100_1234);
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
        assert!(s.st.log.contains(&Event::Pds { addr: CODE + 0x1000, data: 4, ir0: Some(7) }));
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
}
