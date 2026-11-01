// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The PDS encoder against the C assembler (tools/usse-asm/pds-asm): the text
//! of decoded words (random, and per form) must assemble to the same word, and
//! that word must decode back to the text. Without the C assembler the test
//! fails, unless SKIP_C_CROSSCHECK=1 asks to skip it.

use pds_isa::{decode, forms};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn repo() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn decoded_texts_assemble_as_in_c() {
    let asm = repo().join("tools/usse-asm/pds-asm");
    if !asm.is_file() {
        assert!(
            std::env::var_os("SKIP_C_CROSSCHECK").is_some_and(|v| v == "1"),
            "SKIPPED, NOT PASSED: build tools/usse-asm (make -C tools/usse-asm) or set SKIP_C_CROSSCHECK=1"
        );
        eprintln!("skipped: SKIP_C_CROSSCHECK=1 and no C pds-asm");
        return;
    }
    let mut x = 0x9e37_79b9u32;
    let mut next = || {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        x
    };
    let mut ws: Vec<u32> = (0..30_000).map(|_| next()).collect();
    for f in forms() {
        for _ in 0..300 {
            ws.push((f.val as u32) | (next() & !(f.mask as u32)));
        }
    }
    let texts: Vec<String> = ws.iter().map(|&w| decode(w)).filter(|i| i.valid).map(|i| i.text).collect();
    let dir = Path::new(env!("CARGO_TARGET_TMPDIR"));
    let (s, o) = (dir.join("pds_asm.s"), dir.join("pds_asm.bin"));
    fs::write(&s, texts.join("\n") + "\n").unwrap();
    let r = Command::new(&asm).arg("-o").arg(&o).arg(&s).output().unwrap();
    assert!(r.status.success(), "{}", String::from_utf8_lossy(&r.stderr));
    let want: Vec<u32> =
        fs::read(&o).unwrap().chunks_exact(4).map(|b| u32::from_le_bytes(b.try_into().unwrap())).collect();
    assert_eq!(want.len(), texts.len());
    for (t, &w) in texts.iter().zip(&want) {
        assert_eq!(pds_isa::encode(t), Some(w), "{t}");
        assert_eq!(decode(w).text, *t);
    }
}
