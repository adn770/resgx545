// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! A firmware (EDM) task of our own, as the simulator runs it (phase 11.29): the results page it
//! shares with the host, and the SGX register file for `ldr` and `str`.
//!
//! What the hardware showed (the 9b runs, 318 vectors of vectors/nokernel/usse/fwtask-9b, E534):
//! a `str` to 0x0814 or 0x0a78 is seen by every later `ldr` of that register and by the host, at once, with
//! no fence and at any distance run (0 to 64 instructions between, a `wdf`, an `idf`, neither); an
//! earlier `ldr` is not changed by a later `str`. That is what the register map below does, so
//! the model is the sequential one, and only for those two registers. Everything else is refused:
//! `str` to any other register or of a value wider than the register (17 and 6 bits), `ldr` of a
//! register not on the list or not seeded (the identity registers and CR_TIMER are read-only here
//! and a vector seeds them), an index of more than 14 bits, the register-index forms (no run used
//! them), and the clock-gate registers by name, for both. No timing, no lanes, no other writer of
//! the registers.

use crate::{Bus, Error};
use std::collections::BTreeMap;

/// Registers a firmware task of ours may `str` (byte offsets) with the widest value the runs stored:
/// CR_REG_0814 (17 bits) and CR_PDS_REG_0A78 (6 bits), as the host reads them back. A wider value
/// is refused, not masked: no run stored one.
pub const STR_OK: [(u32, u32); 2] = [(0x0814, 0x1_ffff), (0x0a78, 0x3f)];
/// And may `ldr`: CORE_ID, CORE_REVISION, CR_TIMER, and the two above. The first two and CR_TIMER
/// are read as the vector seeded them (CR_TIMER never advances); no vector of the 318 reads CORE_ID
/// or CORE_REVISION, so unit tests alone cover them.
pub const LDR_OK: [u32; 5] = [0x001c, 0x0020, 0x0144, 0x0814, 0x0a78];
/// The widest immediate index of `ldr` and `str` (14 bits); a wider one is no alias of a register.
const INDEX_MAX: u32 = 0x3fff;

fn no(what: String) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: what }
}

/// The results page (device memory the task and the host share) and the register file.
pub struct FwBus {
    base: u32,
    mem: Vec<u32>,
    regs: BTreeMap<u32, u32>,
}

impl FwBus {
    pub fn new(base: u32, dwords: usize) -> FwBus {
        FwBus { base, mem: vec![0; dwords], regs: BTreeMap::new() }
    }

    /// A register's value before the task runs (byte offset).
    pub fn seed_reg(&mut self, off: u32, value: u32) {
        self.regs.insert(off, value);
    }

    /// The register as the host reads it after the task.
    pub fn host_reg(&self, off: u32) -> Option<u32> {
        self.regs.get(&off).copied()
    }

    pub fn set_mem(&mut self, dword: usize, value: u32) {
        self.mem[dword] = value;
    }

    pub fn mem(&self, dword: usize) -> u32 {
        self.mem[dword]
    }

    fn slot(&self, addr: u32) -> Result<usize, Error> {
        let off = addr.wrapping_sub(self.base);
        if !off.is_multiple_of(4) || off as usize >= self.mem.len() * 4 {
            return Err(Error::Fault(addr));
        }
        Ok(off as usize / 4)
    }
}

impl Bus for FwBus {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        Ok(self.mem[self.slot(addr)?])
    }

    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        let i = self.slot(addr)?;
        self.mem[i] = v;
        Ok(())
    }

    fn register_index_forms(&self) -> bool {
        false
    }

    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        if index > INDEX_MAX {
            return Err(no(format!("ldr #{index:#x}: an index of more than 14 bits is not one that ran")));
        }
        let off = index * 4;
        if !LDR_OK.contains(&off) {
            return Err(no(format!(
                "ldr #{index}: register 0x{off:04x} is not one a firmware task of ours reads"
            )));
        }
        self.regs
            .get(&off)
            .copied()
            .ok_or_else(|| no(format!("ldr #{index}: register 0x{off:04x} read before it was seeded")))
    }

    fn reg_write(&mut self, index: u32, v: u32) -> Result<(), Error> {
        if index > INDEX_MAX {
            return Err(no(format!("str #{index:#x}: an index of more than 14 bits is not one that ran")));
        }
        let off = index * 4;
        let Some(&(_, mask)) = STR_OK.iter().find(|(o, _)| *o == off) else {
            return Err(no(format!(
                "str #{index}: register 0x{off:04x} is not one a firmware task of ours writes"
            )));
        };
        if v & !mask != 0 {
            return Err(no(format!(
                "str #{index}: {v:#x} is wider than register 0x{off:04x} ({mask:#x}); no run stored one"
            )));
        }
        self.regs.insert(off, v);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Bus, Error};

    fn bus() -> FwBus {
        let mut b = FwBus::new(0x3214_0000, 1024);
        b.seed_reg(0x0814, 0x15a5a);
        b.seed_reg(0x0a78, 0x15);
        b
    }

    #[test]
    fn a_str_is_seen_by_the_next_ldr_and_by_the_host() {
        let mut b = bus();
        assert_eq!(b.reg_read(0x0814 / 4).unwrap(), 0x15a5a);
        b.reg_write(0x0814 / 4, 0xa5a5).unwrap();
        assert_eq!(b.reg_read(0x0814 / 4).unwrap(), 0xa5a5);
        assert_eq!(b.host_reg(0x0814), Some(0xa5a5));
        assert_eq!(b.host_reg(0x0a78), Some(0x15));
    }

    #[test]
    fn str_only_on_the_two_registers() {
        let mut b = bus();
        for off in [0x0000u32, 0x0004, 0x0008, 0x000c, 0x0080, 0x0810, 0x0818, 0x0520, 0x0abc, 0x001c, 0x0144]
        {
            assert!(matches!(b.reg_write(off / 4, 1), Err(Error::Unsupported { .. })), "{off:#x}");
        }
        assert!(b.reg_write(0x0a78 / 4, 3).is_ok());
    }

    #[test]
    fn ldr_only_on_the_listed_registers_and_only_when_seeded() {
        let mut b = bus();
        b.seed_reg(0x001c, 0x0115_0000);
        assert_eq!(b.reg_read(7).unwrap(), 0x0115_0000);
        assert!(matches!(b.reg_read(8), Err(Error::Unsupported { .. })), "CORE_REVISION not seeded");
        for off in [0x0000u32, 0x0004, 0x0810, 0x0818, 0x0520] {
            assert!(matches!(b.reg_read(off / 4), Err(Error::Unsupported { .. })), "{off:#x}");
        }
    }

    /// The program run on a bus of ours, 100 steps at most.
    fn run_on(b: &mut FwBus, src: &[&str]) -> Result<(), Error> {
        let words: Vec<u64> =
            src.iter().map(|t| usse_isa::encode(t, usse_isa::Core::Sgx545).expect(t)).collect();
        let prog = crate::usse::Program::new(&words, usse_isa::Core::Sgx545);
        crate::usse::Machine::default().run(&prog, b, 100)
    }

    #[test]
    fn a_register_index_form_is_refused_as_never_run() {
        // E534: only the immediate-index forms ran; the index of `ldr rD, rI` and `str rI, rS` comes
        // from a register and no run used it, so the model does not take it
        let mut b = bus();
        let r = run_on(&mut b, &["mov r1, #0x00000205", "ldr r2, r1, drc0", "wdf drc0", "mov.end o0, r2"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "ldr by register: {r:?}");
        let r =
            run_on(&mut b, &["mov r1, #0x00000205", "mov r3, #0x00000007", "str r1, r3", "mov.end o0, r3"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "str by register: {r:?}");
        assert_eq!(b.host_reg(0x0814), Some(0x15a5a), "the refused str changed nothing");
        // the immediate forms still run
        let r = run_on(
            &mut b,
            &["mov r3, #0x00000007", "str #0x205, r3", "ldr r2, #0x205, drc0", "wdf drc0", "mov.end o0, r2"],
        );
        assert_eq!(r, Ok(()));
        assert_eq!(b.host_reg(0x0814), Some(7));
    }

    #[test]
    fn an_index_above_14_bits_is_not_an_alias_of_the_register() {
        // the immediate index is 14 bits: 0x4000 | 0x205 is no register nobody measured
        let mut b = bus();
        assert!(matches!(b.reg_write(0x4000 | 0x205, 7), Err(Error::Unsupported { .. })));
        assert!(matches!(b.reg_write(0xffff_c205, 7), Err(Error::Unsupported { .. })));
        assert_eq!(b.host_reg(0x0814), Some(0x15a5a));
        assert!(matches!(b.reg_read(0x4000 | 0x205), Err(Error::Unsupported { .. })));
        assert!(matches!(b.reg_read(0xffff_c205), Err(Error::Unsupported { .. })));
    }

    #[test]
    fn a_store_wider_than_the_register_is_refused_not_masked() {
        // 0x0814 is 17 bits and 0x0a78 6 bits as the host reads them; every run stored a value inside
        // them, so what a wider `str` leaves is not measured
        let mut b = bus();
        assert!(b.reg_write(0x0814 / 4, 0x1ffff).is_ok());
        assert!(matches!(b.reg_write(0x0814 / 4, 0x2_0000), Err(Error::Unsupported { .. })));
        assert!(b.reg_write(0x0a78 / 4, 0x3f).is_ok());
        assert!(matches!(b.reg_write(0x0a78 / 4, 0x40), Err(Error::Unsupported { .. })));
        assert_eq!(b.host_reg(0x0814), Some(0x1ffff));
        assert_eq!(b.host_reg(0x0a78), Some(0x3f));
    }

    #[test]
    fn the_results_page_is_memory_and_nothing_else_is() {
        let mut b = bus();
        b.store32(0x3214_0004, 5).unwrap();
        assert_eq!(b.load32(0x3214_0004).unwrap(), 5);
        assert_eq!(b.load32(0x3214_0ffc).unwrap(), 0);
        assert!(matches!(b.load32(0x3214_1000), Err(Error::Fault(_))));
        assert!(matches!(b.store32(0x0, 1), Err(Error::Fault(_))));
    }
}
