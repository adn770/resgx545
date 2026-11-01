// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The device address space of a job: flat for now (12.0), pages mapped on demand by the loader.
//! The MMU (two-level walk, lists, banks, requestors, fault fields) is 12.5 (`bif`); until then
//! an access to an unmapped address is refused, not predicted as a fault, because no record
//! says what the hardware does for the requestor that would make it (Q076, Q003).

use crate::Outcome;
use std::collections::BTreeMap;

const PAGE: u32 = 4096;

#[derive(Debug, Default, Clone)]
pub struct Mem {
    pages: BTreeMap<u32, Box<[u8; PAGE as usize]>>,
}

impl Mem {
    pub fn new() -> Mem {
        Mem::default()
    }

    /// Map the pages that cover [base, base + len), zero filled; mapped pages keep their bytes.
    pub fn map(&mut self, base: u32, len: u32) {
        let (first, last) = (base / PAGE, (base as u64 + len.max(1) as u64 - 1) / PAGE as u64);
        for p in first..=last as u32 {
            self.pages.entry(p).or_insert_with(|| Box::new([0; PAGE as usize]));
        }
    }

    fn refuse(addr: u32) -> Outcome {
        Outcome::unsupported(
            &format!("access to unmapped address {addr:#010x} (flat memory: no MMU model yet)"),
            &["Q076", "Q003"],
        )
    }

    pub fn read32(&self, addr: u32) -> Result<u32, Outcome> {
        if !addr.is_multiple_of(4) {
            return Err(Outcome::unsupported(&format!("unaligned dword read at {addr:#010x}"), &[]));
        }
        let p = self.pages.get(&(addr / PAGE)).ok_or_else(|| Mem::refuse(addr))?;
        let o = (addr % PAGE) as usize;
        Ok(u32::from_le_bytes([p[o], p[o + 1], p[o + 2], p[o + 3]]))
    }

    pub fn write32(&mut self, addr: u32, v: u32) -> Result<(), Outcome> {
        if !addr.is_multiple_of(4) {
            return Err(Outcome::unsupported(&format!("unaligned dword write at {addr:#010x}"), &[]));
        }
        let p = self.pages.get_mut(&(addr / PAGE)).ok_or_else(|| Mem::refuse(addr))?;
        let o = (addr % PAGE) as usize;
        p[o..o + 4].copy_from_slice(&v.to_le_bytes());
        Ok(())
    }

    /// Map and fill [base, base + 4 * words.len()).
    pub fn load(&mut self, base: u32, words: &[u32]) -> Result<(), Outcome> {
        self.map(base, 4 * words.len() as u32);
        for (i, &w) in words.iter().enumerate() {
            self.write32(base + 4 * i as u32, w)?;
        }
        Ok(())
    }

    pub fn mapped_pages(&self) -> usize {
        self.pages.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mapped_memory_reads_back_what_was_written_across_a_page_edge() {
        let mut m = Mem::new();
        m.map(0x1000_0ff8, 16);
        assert_eq!(m.mapped_pages(), 2);
        m.write32(0x1000_0ffc, 0xdead_beef).unwrap();
        m.write32(0x1000_1000, 7).unwrap();
        assert_eq!(m.read32(0x1000_0ffc).unwrap(), 0xdead_beef);
        assert_eq!(m.read32(0x1000_1000).unwrap(), 7);
        assert_eq!(m.read32(0x1000_0ff8).unwrap(), 0, "mapped memory starts zero");
    }

    #[test]
    fn an_unmapped_access_is_refused_naming_the_questions_not_predicted_as_a_fault() {
        let mut m = Mem::new();
        for o in [m.read32(0x2000_0000).unwrap_err(), m.write32(0x2000_0000, 1).unwrap_err()] {
            match o {
                Outcome::Unsupported { ids, .. } => assert_eq!(ids, ["Q076", "Q003"]),
                o => panic!("{o:?}"),
            }
        }
    }

    #[test]
    fn load_maps_and_fills_and_an_unaligned_access_is_refused() {
        let mut m = Mem::new();
        m.load(0x3000_0000, &[1, 2, 3]).unwrap();
        assert_eq!(m.read32(0x3000_0008).unwrap(), 3);
        assert!(matches!(m.read32(0x3000_0002), Err(Outcome::Unsupported { .. })));
        m.map(u32::MAX - 3, 4); // the last page: no overflow
        assert!(m.read32(u32::MAX - 3).is_ok());
    }
}
