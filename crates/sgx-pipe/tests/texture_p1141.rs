// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! `sgx-sim`'s texture unit against the held-out fills of E723 (T0 bit 27, sRGB to half), E724
//! (format 27, ETC1) and E725 (types 3 and 1) in the `texture/p1141` dataset of `$RESGX545_DATA`
//! (the tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`). Every pixel of
//! every such job (64 x 32 each) is sampled with the job's state words, coordinates and texels
//! (`gen/cases.json`: the scratch dword i is 0xD0000000 | i unless the job injected it) and the
//! first register the sample writes must equal the recorded o0. The bilinear sRGB fills (Q282)
//! and type 4 (its stride fitted only, E725) must stay refused.

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
    let state =
        [u32_of(spec.get("t0")), u32_of(spec.get("t1")), u32_of(spec.get("base")), u32_of(spec.get("t3"))];
    let s = Sample {
        state,
        u: coord(spec.get("u"), x, y),
        v: coord(spec.get("v"), x, y),
        one_d: false,
        srd: Srd::None,
        pcf: None,
        lod: Lod::Flat,
    };
    let mut load = |a: u32| Ok(inject.get(&(a / 4)).copied().unwrap_or(0xd000_0000 | (a / 4)));
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
fn bilinear_srgb_and_type_4_stay_refused() {
    let Some(b) = base() else { return };
    let cases = parse(&std::fs::read_to_string(b.join("gen/cases.json")).unwrap());
    for name in ["g-bl-st-a", "g-bl-st-b", "ty4-8x8", "ty4-32x32", "ty4-32x16", "ty4-16x32"] {
        let j = job(&b, &cases, name);
        let r = sample_at(&j.spec, &injected(&j.spec), 3, 2);
        assert!(matches!(r, Err(tex::Fail::Open(_))), "{name}: {r:?}");
    }
}
