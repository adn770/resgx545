// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The made-up word of every form (tools/usse-dis/pinned.tsv, test_pinned.py)
//! decodes with its form to its pinned text here too.

mod common;

use usse_isa::{Core, decode, forms};

#[test]
fn pinned_words_decode_as_pinned() {
    let tsv = std::fs::read_to_string(common::repo().join("tools/usse-dis/pinned.tsv")).unwrap();
    let mut hit = vec![false; forms().count()];
    let mut bad = Vec::new();
    for line in tsv.lines().filter(|l| !l.is_empty() && !l.starts_with('#')) {
        let v: Vec<&str> = line.split('\t').collect();
        if v[0] != "usse" {
            continue;
        }
        let (form, word, text) =
            (v[1].parse::<usize>().unwrap(), u64::from_str_radix(v[2], 16).unwrap(), v[3]);
        let insn = decode(word, Core::Sgx545);
        if let Some(i) = insn.form {
            hit[i] = true;
        }
        if insn.form != Some(form) || insn.text != text {
            bad.push(format!("{word:016X}: form {form} {text:?}; got {:?} {:?}", insn.form, insn.text));
        }
    }
    assert!(bad.is_empty(), "{}", bad.join("\n"));
    let missing: Vec<usize> = (0..hit.len()).filter(|&i| !hit[i]).collect();
    assert!(missing.is_empty(), "forms without a pinned word: {missing:?}");
}
