// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r34-q044's kept rows (`render/closing-r34-q044` in `$RESGX545_DATA`; the test skips, saying
//! so, without it and fails with `RESGX545_REQUIRE_DATA`), replayed on `pbe::store_tile`: every
//! row of its four stages whose sideband `pbe::pack_of` models and whose word `reg0400_known`
//! admits (E1135: bit 25; E1136: the low bytes and 0xf80), dword for dword. A row's sideband, word
//! and form come from the session's frozen tables: the colour form (o0 = 0x80ff8040 over the
//! background 0xff203040, the triangle's pixels read from E031's mode 0 image) and the ramp form
//! (E385's: alpha per pixel from the session's predictions/p2/alpha.txt, RGB 0x00ff8040). Rows
//! the model refuses (modes 9, 10, 12, 13, 22, 26, 34) are counted, never replayed; since E1146
//! modes 4 to 6 and the ARGB8888-like modes replay too, a held-out check of r35-pk's model.

use sgx_pipe::data::Ctx;
use sgx_pipe::mem::Mem;
use sgx_pipe::pbe::{self, Emit};

const S: &str = "render/closing-r34-q044";
const ATT: &str = "render/closing-r34-q044/out/20261116-232915";
const MODE0: &str = "pbe/pack-modes/pbe-pack-modes-packmode-00/raw.txt";
const BACKGROUND: u32 = 0xff20_3040;
const BASE: u32 = 0x1000_0000;

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(ATT).is_dir() && r.join(MODE0).is_file()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATT} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {ATT} or {MODE0} (set RESGX545_DATA)");
    None
}

fn text(c: &Ctx, rel: &str) -> String {
    let b = if rel.ends_with(".gz") { c.read_gz(rel, "") } else { c.read(rel, "") };
    String::from_utf8(b.unwrap()).unwrap()
}

/// The 4096 dwords of the `row N:` lines of a probe output (the first image).
fn image(t: &str) -> Vec<u32> {
    let mut out = Vec::new();
    for line in t.lines() {
        let Some((_, what)) = line.strip_prefix("probe ").and_then(|r| r.split_once(": ")) else {
            continue;
        };
        if let Some(rest) = what.strip_prefix("row ") {
            let (_, vals) = rest.split_once(':').unwrap();
            out.extend(vals.split_whitespace().map(|w| u32::from_str_radix(w, 16).unwrap()));
        }
    }
    assert_eq!(out.len(), 4096);
    out
}

fn arg(args: &[&str], opt: &str) -> String {
    args[args.iter().position(|a| *a == opt).unwrap() + 1].to_string()
}

/// The image `store_tile` gives a row: `colour[i]` per pixel, the background elsewhere.
fn modelled(colour: &[Option<u32>], sb: u32, reg: u32) -> Vec<u32> {
    let size = pbe::pack_of(sb).unwrap().bytes();
    let mut mem = Mem::new();
    mem.load(BASE, &vec![0xdead_beef; 4096]).unwrap();
    let e = Emit { words: [0, 63 | 63 << 16, 0x8000 | (64 * size / 8 - 1) << 16, BASE], sideband: sb };
    for (tx, ty) in (0..4).flat_map(|ty| (0..2).map(move |tx| (tx, ty))) {
        let cs: Vec<u32> = (0..512)
            .map(|i| colour[(64 * (16 * ty + i / 32) + 32 * tx + i % 32) as usize].unwrap_or(BACKGROUND))
            .collect();
        pbe::store_tile(&e, reg, (tx, ty), &cs, &mut mem).unwrap();
    }
    (0..4096).map(|i| mem.read32(BASE + 4 * i).unwrap()).collect()
}

#[test]
fn every_modelled_row_of_r34_q044_is_the_models() {
    let Some(c) = ctx() else { return };
    let mode0 = image(&text(&c, MODE0));
    let colour: Vec<Option<u32>> = mode0.iter().map(|&w| (w != BACKGROUND).then_some(0x80ff_8040)).collect();
    assert_eq!(colour.iter().flatten().count(), 1062, "E031's triangle");
    let ramp: Vec<Option<u32>> = text(&c, &format!("{S}/predictions/p2/alpha.txt"))
        .split_whitespace()
        .map(|t| (t != "-").then(|| u32::from_str_radix(t, 16).unwrap() << 24 | 0x00ff_8040))
        .collect();
    assert_eq!(ramp.iter().flatten().count(), 1062, "E385's ramp");
    let (mut done, mut refused) = (Vec::new(), 0);
    for stage in ["s0", "p1", "p2", "pw"] {
        for line in text(&c, &format!("{S}/tables/{stage}.txt")).lines() {
            if line.starts_with('#') || line.trim().is_empty() {
                continue;
            }
            let f: Vec<&str> = line.splitn(6, '|').collect();
            let args: Vec<&str> = f[5].split_whitespace().collect();
            let sb = u32::from_str_radix(arg(&args, "--sideband").trim_start_matches("0x"), 16).unwrap();
            let reg = u32::from_str_radix(arg(&args, "--cmd").trim_start_matches("11=0x"), 16).unwrap();
            if pbe::pack_of(sb).is_err() || pbe::reg0400_known(sb, reg).is_err() {
                refused += 1;
                continue;
            }
            let form = if f[5].contains("ramp.bin") { &ramp } else { &colour };
            let kept = image(&text(&c, &format!("{ATT}/{stage}/{}.txt.gz", f[0])));
            let want = modelled(form, sb, reg);
            let differ = want.iter().zip(&kept).filter(|(a, b)| a != b).count();
            assert_eq!(differ, 0, "{} (sideband {sb:#x}, word {reg:#x}): {differ} dwords differ", f[0]);
            done.push(f[0].to_string());
        }
    }
    assert_eq!((done.len(), refused), (EXPECT_DONE, 198 - EXPECT_DONE), "{done:?}");
}

/// s0 3 (mode 0) + 1 (mode 8 ramp) + 3 (mode 4, E1146); p1 1 + 18 (7, 8, 15, 18, 20, 24, 25,
/// 27, 28: reference and bit 25) + 6 (4, 5, 6) + 80 (the 40 ARGB8888-like modes, E1146); p2 1
/// (mode 0) + 8 (1, 2) + 12 (7, 8) + 10 (3, 15, 20, 24, 27) + 11 (mode 4) + 12 (5, 6) + 4 (11);
/// pw 1. Refused: 9, 10, 12, 13 (their layout), 22, 26, 34
const EXPECT_DONE: usize = 170;
