// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! SGX Series-5 PDS (Programmable Data Sequencer) instruction decoder.
//!
//! A PDS program is a data segment (constants, in two banks ds0/ds1) followed
//! by 32-bit little-endian instructions; the EDM is entered through such
//! programs. The form table is generated from isa/pds/ (isa/README.md) and
//! walked with the form engine of `usse_isa::form`, as the C decoder in
//! tools/usse-dis/pds.c does; its text is the C decoder's, byte for byte.

mod kinds;
#[rustfmt::skip]
mod table;

use std::sync::OnceLock;
use usse_isa::form::{Ctx, Fields, Form, Table};

/// A decoded word.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Insn {
    pub word: u32,
    /// True if a form decoded it.
    pub valid: bool,
    /// The form that decoded it (its index in `forms()`).
    pub form: Option<usize>,
    /// The text, as pds-dis prints it; `.word 0x...` for an undecoded word.
    pub text: String,
}

/// Every form of the table, in decoding order.
pub fn forms() -> impl Iterator<Item = &'static Form> {
    table::FORMS.iter()
}

/// Encode one PDS instruction, written as the decoder prints it. None if no
/// form matches.
pub fn encode(text: &str) -> Option<u32> {
    encode_with(text, &Ctx::default())
}

/// Encode with a context (the assembler's label resolver).
pub fn encode_with(text: &str, cx: &Ctx) -> Option<u32> {
    usse_isa::encode::encode_in(table(), text, cx).map(|w| w as u32)
}

/// The form table, dispatched by the opcode w[31:27].
pub fn table() -> &'static Table {
    static T: OnceLock<Table> = OnceLock::new();
    T.get_or_init(|| Table::new(table::FORMS, 27))
}

/// Decode to the form and its field values, without text.
pub fn decode_fields(word: u32) -> Option<Fields> {
    table().fields(word as u64, &Ctx::default())
}

/// Decode one PDS instruction.
pub fn decode(word: u32) -> Insn {
    match table().decode(word as u64, &Ctx::default()) {
        Some((i, text)) => Insn { word, valid: true, form: Some(i), text },
        None => Insn { word, valid: false, form: None, text: format!(".word 0x{word:08X}") },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decodes_halt_and_nop() {
        // the opcodes alone: halt (predicate 7, always) and nop
        assert_eq!(decode(0xAF000000).text, "halt");
        assert_eq!(decode(0xB0000000).text, "nop");
        assert!(!decode(0x77000000).valid); // opcode 0x0e is reserved
        assert_eq!(decode(0x77000000).text, ".word 0x77000000");
    }

    #[test]
    fn mov_specials_are_a_selector_and_bit_9() {
        // selector = index >> 1 over ir0, ir1, pc, tim; bit 9 of the word as .0/.1;
        // selector 4 and up stays undecoded
        let sel = ["ir0", "ir1", "pc", "tim"];
        for v in 128..136u32 {
            let w = 0x1700_0000 | v << 9;
            let (s, b) = (sel[((v - 128) >> 1) as usize], v & 1);
            assert_eq!(decode(w).text, format!("mov32 ds0[0], {s}.{b}"));
            assert_eq!(encode(&decode(w).text), Some(w));
        }
        assert!(!decode(0x1700_0000 | 136 << 9).valid);
        for v in 256..272u32 {
            let w = 0x0F00_0000 | v << 8;
            let (s, b, h) = (sel[((v - 256) >> 2) as usize], v >> 1 & 1, ["l", "h"][(v & 1) as usize]);
            assert_eq!(decode(w).text, format!("mov16 ds0[0], {s}.{b}.{h}"));
            assert_eq!(encode(&decode(w).text), Some(w));
        }
        assert!(!decode(0x0F00_0000 | 272 << 8).valid);
    }
}
