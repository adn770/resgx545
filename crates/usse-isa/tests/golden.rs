// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The goldens: every `*.usse-dis.txt` under golden/ of the private data repository (the C
//! decoder's pinned output) must come out of this decoder byte for byte.

mod common;

use std::fs;
use std::path::Path;
use usse_isa::{Core, decode};

fn walk(dir: &Path, out: &mut Vec<std::path::PathBuf>) {
    for e in fs::read_dir(dir).unwrap() {
        let p = e.unwrap().path();
        if p.is_dir() {
            walk(&p, out);
        } else if p.to_string_lossy().ends_with(".usse-dis.txt") {
            out.push(p);
        }
    }
}

#[test]
fn corpus_goldens_decode_byte_for_byte() {
    let Some(corpus) = common::corpus() else {
        eprintln!("SKIPPED, NOT PASSED: no closed-binary goldens; set RESGX545_DATA_PRIVATE");
        return;
    };
    if !corpus.join("golden").is_dir() {
        eprintln!("SKIPPED, NOT PASSED: no golden/ in the private data repository yet (the capture work)");
        return;
    }
    let mut files = Vec::new();
    walk(&corpus.join("golden"), &mut files);
    assert!(!files.is_empty(), "no *.usse-dis.txt under {}", corpus.display());
    let (mut lines, mut bad) = (0, Vec::new());
    for f in &files {
        for line in fs::read_to_string(f).unwrap().lines() {
            // "<pc>: 0x<ENC16>\t<text>"
            let (head, want) = line.split_once('\t').unwrap();
            let hex = head.split_once("0x").unwrap().1;
            let enc = u64::from_str_radix(hex, 16).unwrap();
            let got = decode(enc, Core::Sgx545).text;
            lines += 1;
            if got != want {
                bad.push(format!("{}: {enc:016X}\n  want {want}\n  got  {got}", f.display()));
            }
        }
    }
    assert!(
        bad.is_empty(),
        "{} of {lines} lines differ:\n{}",
        bad.len(),
        bad[..bad.len().min(20)].join("\n")
    );
    eprintln!("{} files, {lines} lines equal", files.len());
}
