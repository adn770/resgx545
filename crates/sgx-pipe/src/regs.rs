// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The register file, the only interface to the units (plan section 5): offset, name, measured
//! width and access rule. A register nobody listed, a value wider than the measured width and
//! a write to a read-only register refuse. The table is generated from the glossary in 12.6
//! (doc/register_coverage.md: 217 registers, 117 with a measured width); until then it is
//! filled by the caller.

use crate::Outcome;
use std::collections::BTreeMap;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Access {
    ReadWrite,
    ReadOnly,
}

#[derive(Debug, Clone)]
pub struct Def {
    pub name: String,
    /// bits the register holds, where measured
    pub width: Option<u32>,
    pub access: Access,
}

#[derive(Debug, Default)]
pub struct RegFile {
    defs: BTreeMap<u32, Def>,
    vals: BTreeMap<u32, u32>,
}

impl RegFile {
    pub fn new() -> RegFile {
        RegFile::default()
    }

    pub fn define(&mut self, offset: u32, name: &str, width: Option<u32>, access: Access) {
        self.defs.insert(offset, Def { name: name.to_string(), width, access });
    }

    fn def(&self, offset: u32) -> Result<&Def, Outcome> {
        self.defs.get(&offset).ok_or_else(|| {
            Outcome::unsupported(
                &format!("register {offset:#06x} is not in the table (doc/register_coverage.md)"),
                &[],
            )
        })
    }

    pub fn write(&mut self, offset: u32, v: u32) -> Result<(), Outcome> {
        let d = self.def(offset)?;
        if d.access == Access::ReadOnly {
            return Err(Outcome::unsupported(&format!("write to the read-only register {}", d.name), &[]));
        }
        match d.width {
            Some(w) if w < 32 && v >> w != 0 => {
                return Err(Outcome::unsupported(
                    &format!("{v:#x} is wider than the {w} bits measured of {}", d.name),
                    &[],
                ));
            }
            None => {
                return Err(Outcome::unsupported(&format!("the width of {} was not measured", d.name), &[]));
            }
            _ => {}
        }
        self.vals.insert(offset, v);
        Ok(())
    }

    /// A register that was never written reads as unseeded: refused, not zero.
    pub fn read(&self, offset: u32) -> Result<u32, Outcome> {
        let d = self.def(offset)?;
        self.vals
            .get(&offset)
            .copied()
            .ok_or_else(|| Outcome::unsupported(&format!("{} was never written or seeded", d.name), &[]))
    }

    /// Seed a value without the access rule (a read-only register's reset value).
    pub fn seed(&mut self, offset: u32, v: u32) -> Result<(), Outcome> {
        self.def(offset)?;
        self.vals.insert(offset, v);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn file() -> RegFile {
        let mut r = RegFile::new();
        r.define(0x0814, "TEST_RW17", Some(17), Access::ReadWrite);
        r.define(0x0a78, "TEST_RO", Some(32), Access::ReadOnly);
        r.define(0x0b00, "TEST_NOWIDTH", None, Access::ReadWrite);
        r
    }

    #[test]
    fn a_listed_register_reads_back_its_write() {
        let mut r = file();
        r.write(0x0814, 0x1ffff).unwrap();
        assert_eq!(r.read(0x0814).unwrap(), 0x1ffff);
    }

    #[test]
    fn unlisted_wide_read_only_and_unmeasured_writes_refuse() {
        let mut r = file();
        assert!(matches!(r.write(0x0999, 1), Err(Outcome::Unsupported { .. })));
        assert!(matches!(r.write(0x0814, 0x20000), Err(Outcome::Unsupported { .. })));
        assert!(matches!(r.write(0x0a78, 1), Err(Outcome::Unsupported { .. })));
        assert!(matches!(r.write(0x0b00, 1), Err(Outcome::Unsupported { .. })));
        assert!(matches!(r.read(0x0999), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn an_unseeded_register_does_not_read_as_zero_and_seeding_bypasses_the_access_rule() {
        let mut r = file();
        assert!(matches!(r.read(0x0a78), Err(Outcome::Unsupported { .. })));
        r.seed(0x0a78, 0x5a).unwrap();
        assert_eq!(r.read(0x0a78).unwrap(), 0x5a);
    }
}
