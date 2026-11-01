// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The PDS decoder against the C decoder (tools/usse-dis/pds-dis) on random
//! words and on words matching each form.

use pds_isa::{decode, forms};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn repo() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn random_words_match_c() {
    let c = std::env::var_os("PDS_DIS_C").map(PathBuf::from).unwrap_or(repo().join("tools/usse-dis/pds-dis"));
    if !c.is_file() {
        assert!(
            std::env::var_os("SKIP_C_CROSSCHECK").is_some_and(|v| v == "1"),
            "SKIPPED, NOT PASSED: build tools/usse-dis (make -C tools/usse-dis) or set SKIP_C_CROSSCHECK=1"
        );
        eprintln!("skipped: SKIP_C_CROSSCHECK=1 and no C pds-dis");
        return;
    }
    let mut x = 0x2545_f491_4f6c_dd1du64;
    let mut next = || {
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        (x.wrapping_mul(0x2545_F491_4F6C_DD1D) >> 32) as u32
    };
    let mut ws: Vec<u32> = (0..300_000).map(|_| next()).collect();
    for f in forms() {
        for _ in 0..2000 {
            ws.push((f.val as u32) | (next() & !(f.mask as u32)));
        }
    }
    let path = Path::new(env!("CARGO_TARGET_TMPDIR")).join("pds_words.bin");
    fs::write(&path, ws.iter().flat_map(|w| w.to_le_bytes()).collect::<Vec<u8>>()).unwrap();
    let out = Command::new(c).arg(&path).arg("0").output().unwrap();
    assert!(out.status.success());
    let want = String::from_utf8(out.stdout).unwrap();
    let mut n = 0;
    for (i, (line, &w)) in want.lines().zip(&ws).enumerate() {
        assert_eq!(format!("{i}: 0x{w:08X}\t{}", decode(w).text), line);
        n += 1;
    }
    assert_eq!(n, ws.len());
}
