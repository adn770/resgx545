// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The PDS decoder against the closed-binary goldens (`*.pds-dis.txt` under
//! golden/ of the private data repository, the C decoder's pinned output).

use pds_isa::decode;
use std::fs;
use std::path::{Path, PathBuf};

fn repo() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    for e in fs::read_dir(dir).unwrap() {
        let p = e.unwrap().path();
        if p.is_dir() {
            walk(&p, out);
        } else if p.to_string_lossy().ends_with(".pds-dis.txt") {
            out.push(p);
        }
    }
}

#[test]
fn corpus_goldens_decode_byte_for_byte() {
    let corpus = std::env::var_os("RESGX545_DATA_PRIVATE")
        .map(PathBuf::from)
        .unwrap_or(repo().join("../resgx545-data-private"));
    if !corpus.join("golden").is_dir() {
        eprintln!("SKIPPED, NOT PASSED: no closed-binary goldens; set RESGX545_DATA_PRIVATE");
        return;
    }
    let mut files = Vec::new();
    walk(&corpus.join("golden"), &mut files);
    assert!(!files.is_empty());
    let (mut lines, mut bad) = (0, Vec::new());
    for f in &files {
        for line in fs::read_to_string(f).unwrap().lines() {
            // "<index>: 0x<HEX8>\t<text>", "data" for the data segment
            let (head, want) = line.split_once('\t').unwrap();
            if want == "data" {
                continue;
            }
            let w = u32::from_str_radix(head.split_once("0x").unwrap().1, 16).unwrap();
            let got = decode(w).text;
            lines += 1;
            if got != want && bad.len() < 20 {
                bad.push(format!("{}: {w:08X}\n  want {want}\n  got  {got}", f.display()));
            }
        }
    }
    assert!(bad.is_empty(), "differ:\n{}", bad.join("\n"));
    eprintln!("{} files, {lines} instructions equal", files.len());
}
