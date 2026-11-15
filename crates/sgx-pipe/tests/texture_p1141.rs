// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! `sgx-sim`'s texture unit against the held-out fills of E723 (T0 bit 27, sRGB to half), E724
//! (format 27, ETC1) and E725 (types 3 and 1) in the `texture/p1141` dataset of `$RESGX545_DATA`
//! (the tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`). Every pixel of
//! every such job (64 x 32 each) is sampled with the job's state words, coordinates and texels
//! (`gen/cases.json`: the scratch dword i is 0xD0000000 | i unless the job injected it) and the
//! first register the sample writes must equal the recorded o0. The bilinear sRGB fills follow
//! E982's stage rule (fitted on r9-x's single-stage rows, frozen before either fill was scored;
//! a later held-out row missed it, E1004, answered with the flush and the level lerp by E1038);
//! type 4 (its stride fitted only, E725) must stay refused. E722's T3 address jobs (tex-c-addr:
//! levels, scale and bit 10) replay under its chain A4 with the probe's 16-page scratch, the three
//! that faulted there are refused as reads past the scratch (E743, E760, E787), and S1's p-d rows
//! (`render/closing-s1`) replay at 64 and 21 pages; E567's type 5 rt5-2d (E894) replays by E942's
//! bits, its smp3d rows refused.

use sgx_pipe::data::Ctx;
use sgx_sim::json::{Json, parse};
use sgx_sim::tex::{self, Lod, Sample, Srd};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env().root.map(|r| r.join("texture/p1141")).filter(|d| d.is_dir());
    if b.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no texture/p1141 (RESGX545_DATA)");
        eprintln!("SKIPPED: no texture/p1141 (set RESGX545_DATA)");
    }
    b
}

fn u32_of(j: &Json) -> u32 {
    j.num().expect("a number") as u32
}

/// One coordinate of pixel (x, y) by the generator's rule (p1132's catalog): ("map", axis, a,
/// offset, exponent bits) puts texel q at 1 + (2q + 1) / 2^(a + 1) times the exponent; ("lin",
/// axis, K, C) is (1 + x / 64 or 1 + y / 32) K + C, rounded to f32.
fn coord(rule: &Json, x: u32, y: u32) -> f32 {
    let r = rule.arr();
    let p = |i: usize| u32_of(&r[i]);
    let along = if r[1].str() == Some("x") { x } else { y };
    match r[0].str().unwrap() {
        "map" => {
            let (a, off, exp) = (p(2), p(3), p(4));
            let q = (along | off) & ((1 << a) - 1);
            f32::from_bits(exp | (2 * q + 1) << (22 - a))
        }
        "lin" => {
            let shift = if r[1].str() == Some("x") { 17 } else { 18 };
            let uf = f32::from_bits(0x3f80_0000 | along << shift) as f64;
            (uf * f32::from_bits(p(2)) as f64 + f32::from_bits(p(3)) as f64) as f32
        }
        k => panic!("coordinate rule {k}"),
    }
}

/// The 64 x 32 o0 values of a job's kept output ("probe NAME: row N: ...").
fn rows(text: &str) -> Vec<u32> {
    let mut img = vec![None; 64 * 32];
    for line in text.lines() {
        let Some(at) = line.find(": row ") else { continue };
        let (n, vals) = line[at + 6..].split_once(':').unwrap();
        let y: usize = n.trim().parse().unwrap();
        let vals: Vec<u32> = vals.split_whitespace().map(|v| u32::from_str_radix(v, 16).unwrap()).collect();
        assert_eq!(vals.len(), 64, "row {y}");
        for (x, v) in vals.into_iter().enumerate() {
            img[y * 64 + x] = Some(v);
        }
    }
    img.into_iter().map(|p| p.expect("a row missing")).collect()
}

struct Job {
    spec: Json,
    image: Vec<u32>,
}

fn job(b: &Path, cases: &Json, name: &str) -> Job {
    let c = cases.arr().iter().find(|c| c.get("name").str() == Some(name)).expect(name);
    assert_eq!(c.get("set").str(), Some("heldout"), "{name}");
    let p =
        b.join("out-hw/p1141tex-dumps").join(c.get("script").str().unwrap()).join(format!("{name}.txt.gz"));
    let text = String::from_utf8(sgx_pipe::gz::gunzip(&std::fs::read(&p).unwrap()).unwrap()).unwrap();
    Job { spec: c.get("spec").clone(), image: rows(&text) }
}

/// Sample pixel (x, y) of a job: the first register written, or the refusal.
fn sample_at(spec: &Json, inject: &BTreeMap<u32, u32>, x: u32, y: u32) -> Result<u32, tex::Fail> {
    sample_in(spec, inject, x, y, None)
}

/// Sample pixel (x, y) with the probe's scratch of `pages` 4 KiB pages at the texture's base (None:
/// unbounded): a read past it is the bus's fault, as sgx-sim's memory gives it.
fn sample_in(
    spec: &Json,
    inject: &BTreeMap<u32, u32>,
    x: u32,
    y: u32,
    pages: Option<u32>,
) -> Result<u32, tex::Fail> {
    let state =
        [u32_of(spec.get("t0")), u32_of(spec.get("t1")), u32_of(spec.get("base")), u32_of(spec.get("t3"))];
    let s = Sample {
        csc: None,
        state,
        u: coord(spec.get("u"), x, y),
        v: coord(spec.get("v"), x, y),
        one_d: false,
        srd: Srd::None,
        pcf: None,
        lod: Lod::Flat,
    };
    let mut load = |a: u32| match pages {
        Some(n) if a >= 4096 * n => Err(sgx_sim::Error::Fault(a)),
        _ => Ok(inject.get(&(a / 4)).copied().unwrap_or(0xd000_0000 | (a / 4))),
    };
    tex::sample(&s, &mut load).map(|r| r[0])
}

fn injected(spec: &Json) -> BTreeMap<u32, u32> {
    spec.get("inject").obj().iter().map(|(k, v)| (k.parse().unwrap(), u32_of(v))).collect()
}

/// Every pixel of each named job: the model equals the hardware.
fn exact(names: &[&str]) {
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    for name in names {
        let j = job(&b, &cases, name);
        let inject = injected(&j.spec);
        for y in 0..32 {
            for x in 0..64 {
                let got =
                    sample_at(&j.spec, &inject, x, y).unwrap_or_else(|e| panic!("{name} ({x}, {y}): {e:?}"));
                assert_eq!(got, j.image[(y * 64 + x) as usize], "{name} ({x}, {y})");
            }
        }
    }
}

#[test]
fn srgb_point_samples_equal_e723s_held_out_fills() {
    exact(&["g-st8x4", "g-tw8x8", "g-tw32x32", "g-tw8x8-s2"]);
}

#[test]
fn etc1_equals_e724s_held_out_fills() {
    exact(&["e16a", "e16b", "e32x16", "e16x32", "e8x16", "e8x8"]);
}

#[test]
fn types_3_and_1_equal_e725s_held_out_fills() {
    exact(&[
        "ty3-8x8",
        "ty3-32x32",
        "ty3-32x16",
        "ty3-16x32",
        "ty1-8x8",
        "ty1-32x32",
        "ty1-32x16",
        "ty1-16x32",
    ]);
}

#[test]
fn bilinear_srgb_equals_e723s_fills_by_e982s_stage_rule() {
    // E982: x then y, each stage on two halves floored to the larger one's ulp, lerped
    // exactly and rounded to nearest with ties up, A unchanged at weight 0
    exact(&["g-bl-st-a", "g-bl-st-b"]);
}

#[test]
fn type_4_at_32x32_reads_its_block_and_the_rest_stays_refused() {
    // E1055 (r15-tex's held-out 32 x 32 reference): type 4 at 32 x 32 reads dword 32 t + s, its
    // 32 x 32 block (E941); E725's job at that size replays exactly
    exact(&["ty4-32x32"]);
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    for name in ["ty4-8x8", "ty4-32x16", "ty4-16x32"] {
        let j = job(&b, &cases, name);
        let r = sample_at(&j.spec, &injected(&j.spec), 3, 2);
        assert!(matches!(r, Err(tex::Fail::Open(_))), "{name}: {r:?}");
    }
}

/// E722's tex-c-addr jobs that completed (13 of 16, all held out; A4 fitted on E566's 12): T3 bits
/// 28:27 (the level L), 19:18 (the address scale e) and 10 on twiddled and strided textures, run
/// with the probe's 16-page (64 KiB) scratch at the texture's base.
const AD_RAN: [&str; 13] = [
    "ad-tw64x64-L1e0",
    "ad-tw64x64-L2e0",
    "ad-tw64x64-L3e0",
    "ad-tw64x64-L1e1",
    "ad-tw64x64-L0e0b10",
    "ad-tw32x64-L1e0",
    "ad-tw32x64-L2e1",
    "ad-tw128x32-L1e0",
    "ad-tw128x32-L0e2",
    "ad-st128x32-L1e0",
    "ad-st128x32-L2e1",
    "ad-st128x32-L0e0b10",
    "ad-st32x64-L1e0",
];
/// E722's three jobs that faulted at 16 pages (their A4 extents 86016, 174080 and 87040 bytes).
const AD_FAULTED: [&str; 3] = ["ad-tw64x64-L2e2", "ad-tw64x64-L3e3", "ad-st128x32-L3e2"];

/// Every pixel of `spec` under a scratch of `pages` against `image`.
fn exact_in(name: &str, spec: &Json, image: &[u32], pages: u32) {
    let inject = injected(spec);
    for y in 0..32 {
        for x in 0..64 {
            let got = sample_in(spec, &inject, x, y, Some(pages))
                .unwrap_or_else(|e| panic!("{name} ({x}, {y}): {e:?}"));
            assert_eq!(got, image[(y * 64 + x) as usize], "{name} ({x}, {y})");
        }
    }
}

/// The refusal of a read past the probe's scratch names the records of the probe's layout.
fn past_scratch(r: Result<u32, tex::Fail>) -> bool {
    matches!(&r, Err(tex::Fail::Open(w))
        if w.contains("past the probe's scratch") && ["E743", "E760", "E787"].iter().all(|e| w.contains(e)))
}

#[test]
fn t3_address_chain_equals_e722s_held_out_fills() {
    // A4: the dword base + ((off + idx) << e), off the sum of the level sizes below L (not the
    // stride), idx E561's tile index of (X >> L, Y >> L) at the level's size or, strided,
    // X >> L + stride (Y >> L); bit 10 the base dword
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    for name in AD_RAN {
        let j = job(&b, &cases, name);
        exact_in(name, &j.spec, &j.image, 16);
    }
}

#[test]
fn t3_reads_past_the_probe_s_scratch_are_refused_naming_its_layout() {
    // E722's three faults at 16 pages: every pixel's A4 read lies past the 64 KiB scratch, where
    // the hardware reads the probe's own surfaces or faults (E743, E760, E787)
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    for name in AD_FAULTED {
        let c = cases.arr().iter().find(|c| c.get("name").str() == Some(name)).expect(name);
        let spec = c.get("spec");
        let inject = injected(spec);
        for (x, y) in (0..32).flat_map(|y| (0..64).map(move |x| (x, y))) {
            assert!(past_scratch(sample_in(spec, &inject, x, y, Some(16))), "{name} ({x}, {y})");
        }
    }
}

#[test]
fn t3_address_chain_at_the_pages_s1_ran_equals_e743s_images() {
    // E743 (S1 p-d; repeated byte for byte by E760): E722's three faulting jobs at 64 pages and
    // L2e2 at 21 complete and equal A4 at their own page count; at 20 pages every A4 read is past
    // the scratch (E760: 128 words without the 0xD tag at 20 and 19 pages, E787: the probe's
    // sentinel at 18, a fault at 17), refused
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    let s1 = Ctx::from_env().root.unwrap().join("render/closing-s1/out/p-d");
    let spec = |name: &str| {
        cases.arr().iter().find(|c| c.get("name").str() == Some(name)).expect(name).get("spec").clone()
    };
    for (row, case, pages) in [
        ("d-L2e2-64", "ad-tw64x64-L2e2", 64),
        ("d-L3e3-64", "ad-tw64x64-L3e3", 64),
        ("d-st-L3e2-64", "ad-st128x32-L3e2", 64),
        ("d-L2e2-21", "ad-tw64x64-L2e2", 21),
    ] {
        let text = gunzip_text(&s1.join(format!("{row}.txt.gz")));
        exact_in(row, &spec(case), &rows(&text), pages);
    }
    let sp = spec("ad-tw64x64-L2e2");
    for pages in [20, 19, 18, 17] {
        for (x, y) in (0..32).flat_map(|y| (0..64).map(move |x| (x, y))) {
            assert!(
                past_scratch(sample_in(&sp, &injected(&sp), x, y, Some(pages))),
                "{pages} pages ({x}, {y})"
            );
        }
    }
}

fn gunzip_text(p: &Path) -> String {
    String::from_utf8(sgx_pipe::gz::gunzip(&std::fs::read(p).unwrap()).unwrap()).unwrap()
}

#[test]
fn type_5_at_16x16_equals_e894s_rows_and_its_smp3d_rows_stay_refused() {
    // E894 (post hoc, not held out): E567's rt5-2d, a 16 x 16 type 5 texture over the map fill,
    // stores 0 at x mod 16 below 8 and 0x0000ffff above in all 32 rows: E942's bit 0 of dword
    // floor(t / 8), t = 16 y + x, over the tag 0xD0000000 | i. smp3d (rt5-3d-w5, -w15) is modelled
    // only for types 0, 6 and 7 and stays refused
    let Some(_) = base() else { return };
    let root = Ctx::from_env().root.unwrap().join("texture/p1132/tx-types-risky");
    let specs = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../tools/texture/p1132/gen/specs.json");
    let specs = parse(&std::fs::read_to_string(specs).unwrap());
    let spec = specs.get("rt5-2d").get("spec").clone();
    exact_in("rt5-2d", &spec, &rows(&gunzip_text(&root.join("rt5-2d.txt.gz"))), 16);
    for name in ["rt5-3d-w5", "rt5-3d-w15"] {
        let sp = specs.get(name).get("spec");
        let state =
            [u32_of(sp.get("t0")), u32_of(sp.get("t1")), u32_of(sp.get("base")), u32_of(sp.get("t3"))];
        assert!(tex::smp3d_as_2d(state, false).is_err(), "{name}");
    }
}
