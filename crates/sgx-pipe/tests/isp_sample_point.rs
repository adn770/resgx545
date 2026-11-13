// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The single-sample point of CR_ISP_MULTISAMPLECTL byte 0 (E1018) replayed on E064's sweep: all
//! 256 values of the render's cmd:16 bits 7:0 on the tool's 64x64 triangle, `raw.txt` of the
//! `isp/sample-positions` dataset of `$RESGX545_DATA` (skipped, saying so, without it; a failure
//! with `RESGX545_REQUIRE_DATA`). Every value's triangle count must be the model's, and the values
//! must fall into the same 27 classes by the model's image as by the hardware's hash.

use sgx_pipe::data::Ctx;
use sgx_pipe::isp::{self, Tri};
use std::collections::BTreeMap;
use std::path::PathBuf;

fn raw() -> Option<PathBuf> {
    let p = Ctx::from_env().root.map(|r| r.join("isp/sample-positions/raw.txt")).filter(|p| p.is_file());
    if p.is_none() {
        assert!(
            std::env::var_os("RESGX545_REQUIRE_DATA").is_none(),
            "no isp/sample-positions (RESGX545_DATA)"
        );
        eprintln!("SKIPPED: no isp/sample-positions (set RESGX545_DATA)");
    }
    p
}

/// The tool's 64x64 triangle (`sgxfive_tri_default`): (8, 8), (56, 20), (20, 56) pixels.
fn tri() -> Tri {
    Tri { v: [(8 * 256, 8 * 256), (56 * 256, 20 * 256), (20 * 256, 56 * 256)], z: [0.5; 3] }
}

/// byte 0 -> (count, hash): the baseline is 0x88, each case `cmd:16^=X` is 0x88 ^ X (E064).
fn observed(text: &str) -> BTreeMap<u32, (usize, String)> {
    let mut out = BTreeMap::new();
    let (mut n, mut hash) = (None, None);
    for l in text.lines() {
        if let Some(c) = l.strip_prefix("=== case ") {
            n = Some(match c.strip_prefix("cmd:16^=0x") {
                Some(x) => 0x88 ^ u32::from_str_radix(x, 16).unwrap(),
                None => {
                    assert_eq!(c, "baseline");
                    0x88
                }
            });
            hash = None;
        } else if let Some(h) = l.strip_prefix("target: 64x64 hash ") {
            hash = Some(h.to_string());
        } else if let Some(r) = l.strip_prefix("tri 64x64 #1: ").filter(|r| r.contains(" triangle,")) {
            let count = r.split_whitespace().next().unwrap().parse().unwrap();
            assert!(
                out.insert(n.unwrap(), (count, hash.clone().expect("a hash before the count"))).is_none()
            );
        }
    }
    out
}

#[test]
fn byte_0_places_the_sample_on_e064s_256_values_counts_and_classes() {
    let Some(p) = raw() else { return };
    let obs = observed(&std::fs::read_to_string(p).unwrap());
    assert_eq!(obs.len(), 256);
    let t = tri();
    let (mut by_image, mut by_hash) = (BTreeMap::new(), BTreeMap::new());
    for (&n, (count, hash)) in &obs {
        let img = isp::coverage_image_sampled(64, 64, &t, n).unwrap_or_else(|o| panic!("{n:#x}: {o:?}"));
        assert_eq!(img.iter().filter(|&&c| c).count(), *count, "byte 0 = {n:#x}");
        by_image.entry(img).or_insert_with(Vec::new).push(n);
        by_hash.entry(hash.clone()).or_insert_with(Vec::new).push(n);
    }
    let mut a: Vec<_> = by_image.into_values().collect();
    let mut b: Vec<_> = by_hash.into_values().collect();
    a.sort();
    b.sort();
    assert_eq!(b.len(), 27, "E064: 27 images");
    assert_eq!(a, b, "the values the model draws alike are the values the hardware hashed alike");
}

#[test]
fn the_nibbles_swapped_would_miss_e064s_counts() {
    // the control: x in bits 7:4 (E1018's rival SWAPPED, 226 of 256 counts) must fail
    let Some(p) = raw() else { return };
    let obs = observed(&std::fs::read_to_string(p).unwrap());
    let t = tri();
    let held = obs
        .iter()
        .filter(|&(&n, (count, _))| {
            let swapped = (n & 0xf) << 4 | n >> 4;
            let img = isp::coverage_image_sampled(64, 64, &t, swapped).unwrap();
            img.iter().filter(|&&c| c).count() == *count
        })
        .count();
    assert_eq!(held, 226);
}
