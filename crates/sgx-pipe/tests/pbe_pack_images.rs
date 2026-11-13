// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The one- and two-channel pack modes against every kept image of the jobs that measured them,
//! dword for dword: E383's `pbe/sideband-channels` (modes 7, 8, 15, 18, 24, 25 and 28 at sideband
//! bits 8:6 = 0 to 7, two colours whose bytes all differ: 112 images), r10-x's stage sb (E999:
//! modes 20 and 27 at 0 to 3 and two mode 8 controls: 18 images) and E031's `pbe/pack-modes` in
//! the same modes (9 images), in `$RESGX545_DATA` (the test skips, saying so, without it and fails
//! with `RESGX545_REQUIRE_DATA`). The job is the library's 64 x 64 triangle over the background
//! 0xff203040; which pixels it covers is read from E031's mode 0 image (ARGB8888, 1062 pixels), the
//! rest is `pbe::store_tile` over the eight tiles at the pitch of 64 pixels of the mode's size,
//! into a target filled with 0xdeadbeef. Measured rules: every image must be equal.

use sgx_pipe::data::Ctx;
use sgx_pipe::mem::Mem;
use sgx_pipe::pbe::{self, Emit};

const BACKGROUND: u32 = 0xff20_3040;
const MODE0: &str = "pbe/pack-modes/pbe-pack-modes-packmode-00/raw.txt";
const SB: &str = "render/closing-r10-x/out/20261113-101116/sb";
const BASE: u32 = 0x1000_0000;

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(MODE0).is_file() && r.join(SB).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {MODE0} or {SB} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {MODE0} or {SB} (set RESGX545_DATA)");
    None
}

/// The images of a probe output: case name, sideband and the 4096 dwords of its rows.
fn images(text: &str) -> Vec<(String, u32, Vec<u32>)> {
    let mut out: Vec<(String, u32, Vec<u32>)> = Vec::new();
    for line in text.lines() {
        let Some(rest) = line.strip_prefix("probe ") else { continue };
        let Some((name, what)) = rest.split_once(": ") else { continue };
        if let Some(at) = what.find("(sideband 0x") {
            let sb = u32::from_str_radix(&what[at + 12..at + 20], 16).unwrap();
            out.push((name.to_string(), sb, Vec::new()));
        } else if what.starts_with("row ") {
            let (_, vals) = what.split_once(':').unwrap();
            let img = &mut out.last_mut().unwrap().2;
            img.extend(vals.split_whitespace().map(|w| u32::from_str_radix(w, 16).unwrap()));
        }
    }
    for (name, _, img) in &out {
        assert_eq!(img.len(), 4096, "{name}");
    }
    out
}

/// The 64 x 64 image the triangle job stores in `sb` with `colour`, through `pbe::store_tile`.
fn modelled(covered: &[bool], sb: u32, colour: u32) -> Vec<u32> {
    let size = pbe::pack_of(sb).unwrap().bytes();
    let mut mem = Mem::new();
    mem.load(BASE, &vec![0xdead_beef; 4096]).unwrap();
    // the rectangle (0, 0) to (63, 63), the whole of each tile, the pitch of 64 pixels
    let e = Emit { words: [0, 63 | 63 << 16, 0x8000 | (64 * size / 8 - 1) << 16, BASE], sideband: sb };
    for (tx, ty) in (0..4).flat_map(|ty| (0..2).map(move |tx| (tx, ty))) {
        let colours: Vec<u32> = (0..512)
            .map(|i| {
                let (x, y) = (32 * tx + i % 32, 16 * ty + i / 32);
                if covered[(64 * y + x) as usize] { colour } else { BACKGROUND }
            })
            .collect();
        pbe::store_tile(&e, 0x80, (tx, ty), &colours, &mut mem).unwrap();
    }
    (0..4096).map(|i| mem.read32(BASE + 4 * i).unwrap()).collect()
}

fn text(c: &Ctx, rel: &str) -> String {
    let b = if rel.ends_with(".gz") { c.read_gz(rel, "") } else { c.read(rel, "") };
    String::from_utf8(b.unwrap()).unwrap()
}

/// The colour of a case: E383's `__0`/`__1` and r10-x's `-c0`/`-c1` (sb-c0.bin, sb-c1.bin).
fn colour_of(case: &str) -> u32 {
    if case.ends_with('0') { 0xc080_4020 } else { 0x1357_9bdf }
}

#[test]
fn every_kept_image_of_the_one_and_two_channel_modes_is_the_models() {
    let Some(c) = ctx() else { return };
    let mode0 = images(&text(&c, MODE0));
    let covered: Vec<bool> = mode0[0].2.iter().map(|&w| w != BACKGROUND).collect();
    assert_eq!(covered.iter().filter(|&&b| b).count(), 1062, "E031's triangle");
    let root = c.root.clone().unwrap();
    let mut jobs: Vec<(String, String)> = Vec::new();
    for e in std::fs::read_dir(root.join("pbe/sideband-channels")).unwrap() {
        let n = e.unwrap().file_name().into_string().unwrap();
        // the bit 11 (faults) and bit 12 (words of no colour) jobs are not pack modes
        if n.starts_with("pbe-sideband-channels-0") {
            jobs.push((format!("pbe/sideband-channels/{n}/raw.txt"), "E383".into()));
        }
    }
    for e in std::fs::read_dir(root.join(SB)).unwrap() {
        let n = e.unwrap().file_name().into_string().unwrap();
        if n.starts_with("sb-") && n.ends_with(".txt.gz") {
            jobs.push((format!("{SB}/{n}"), "E999".into()));
        }
    }
    jobs.sort();
    let (mut n383, mut n999) = (0, 0);
    for (rel, rec) in &jobs {
        let t = text(&c, rel);
        for (case, sb, kept) in images(&t) {
            // r10-x's probe names its case by the program (sb-c0, sb-c1)
            let want = modelled(&covered, sb, colour_of(&case));
            let differ = want.iter().zip(&kept).filter(|(a, b)| a != b).count();
            assert_eq!(differ, 0, "{rel} {case} (sideband {sb:#x}, {rec}): {differ} dwords differ");
            if rec == "E383" { n383 += 1 } else { n999 += 1 }
        }
    }
    assert_eq!((n383, n999), (112, 18));
    // E031: the background and 0x80ff8040, field 0
    for m in [7u32, 8, 15, 18, 20, 24, 25, 27, 28] {
        let rel = format!("pbe/pack-modes/pbe-pack-modes-packmode-{m:02}/raw.txt");
        let imgs = images(&text(&c, &rel));
        assert_eq!(imgs.len(), 1, "{rel}");
        let want = modelled(&covered, 0x200 | m, 0x80ff_8040);
        assert_eq!(want, imgs[0].2, "{rel}");
    }
}
