// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The coverage rule on E680's ten targets (96 x 64 to 4096 x 4096), coverage only: the frozen
//! sample is, per target and per class of group S1 (small, medium, large, centre, pairA, pairB),
//! the case of the lowest id in the cases table of the `isp/coverage-envelope` dataset of
//! `$RESGX545_DATA` (60 cases; the tests skip, saying so, without it and fail with
//! `RESGX545_REQUIRE_DATA`). Each case's whole image (the tool's `--pixels-rle` rows) must equal
//! `isp::coverage_image` pixel for pixel; the depth on those targets stays refused (Q262).

use sgx_pipe::Outcome;
use sgx_pipe::data::Ctx;
use sgx_pipe::isp::{self, Tri};
use std::collections::BTreeMap;
use std::path::PathBuf;

const TRIANGLE: u32 = 0xff00_ff00;
const BACKGROUND: u32 = 0xff20_3040;
const CLASSES: [&str; 6] = ["small", "medium", "large", "centre", "pairA", "pairB"];

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env().root.map(|r| r.join("isp/coverage-envelope")).filter(|d| d.is_dir());
    if b.is_none() {
        assert!(
            std::env::var_os("RESGX545_REQUIRE_DATA").is_none(),
            "no isp/coverage-envelope (RESGX545_DATA)"
        );
        eprintln!("SKIPPED: no isp/coverage-envelope (set RESGX545_DATA)");
    }
    b
}

struct Case {
    id: u32,
    w: u32,
    h: u32,
    v: [(i64, i64); 3],
}

/// The frozen sample: per (target, class) of S1, the lowest id.
fn sample(table: &str) -> Vec<Case> {
    let mut pick: BTreeMap<(u32, u32, String), Case> = BTreeMap::new();
    for l in table.lines() {
        let f: Vec<&str> = l.split('\t').collect();
        if f.len() < 13 || f[2] != "S1" || f[1] == "repeat" || !CLASSES.contains(&f[3]) {
            continue;
        }
        assert_eq!(f[6], "8", "case {}: vertices in 1/256 pixel", f[0]);
        let n = |i: usize| f[i].parse::<i64>().unwrap();
        let c = Case {
            id: f[0].parse().unwrap(),
            w: f[4].parse().unwrap(),
            h: f[5].parse().unwrap(),
            v: [(n(7), n(8)), (n(9), n(10)), (n(11), n(12))],
        };
        let key = (c.w, c.h, f[3].to_string());
        if pick.get(&key).is_none_or(|p| p.id > c.id) {
            pick.insert(key, c);
        }
    }
    pick.into_values().collect()
}

/// The image of a `--pixels-rle` output: rows "rle Y: 0xCOLOURxN ...", covered or not.
fn rle_image(text: &str, w: u32, h: u32) -> Vec<bool> {
    let mut img = vec![None; (w * h) as usize];
    for line in text.lines() {
        let Some(rest) = line.strip_prefix("rle ") else { continue };
        let (y, runs) = rest.split_once(':').unwrap();
        let y: u32 = y.trim().parse().unwrap();
        let mut x = 0;
        for run in runs.split_whitespace() {
            let (c, n) = run.trim_start_matches("0x").split_once('x').unwrap();
            let (c, n) = (u32::from_str_radix(c, 16).unwrap(), n.parse::<u32>().unwrap());
            assert!(c == TRIANGLE || c == BACKGROUND, "colour {c:#x}");
            for _ in 0..n {
                img[(y * w + x) as usize] = Some(c == TRIANGLE);
                x += 1;
            }
        }
        assert_eq!(x, w, "row {y}");
    }
    img.into_iter().map(|p| p.expect("a row missing")).collect()
}

#[test]
fn the_coverage_rule_draws_e680s_sample_pixel_for_pixel_on_its_ten_targets() {
    let Some(b) = base() else { return };
    let cases = sample(&std::fs::read_to_string(b.join("cases-1140.tsv")).unwrap());
    assert_eq!(cases.len(), 60, "10 targets x 6 classes");
    let mut targets = std::collections::BTreeSet::new();
    let mut covered = 0u64;
    for c in &cases {
        assert!(isp::E680_TARGETS.contains(&(c.w, c.h)), "{} x {}", c.w, c.h);
        targets.insert((c.w, c.h));
        let raw = std::fs::read(b.join("main/raw").join(format!("{}.txt.gz", c.id))).unwrap();
        let text = String::from_utf8(sgx_pipe::gz::gunzip(&raw).unwrap()).unwrap();
        let hw = rle_image(&text, c.w, c.h);
        let t = Tri { v: c.v, z: [0.5; 3] };
        let model = isp::coverage_image(c.w, c.h, &t).unwrap_or_else(|o| panic!("case {}: {o:?}", c.id));
        let wrong = hw.iter().zip(&model).filter(|(a, b)| a != b).count();
        assert_eq!(wrong, 0, "case {} ({} x {})", c.id, c.w, c.h);
        covered += hw.iter().filter(|&&p| p).count() as u64;
        // the depth on these targets is not measured (Q262)
        match isp::target_in_envelope(c.w, c.h) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q262"]),
            o => panic!("{o:?}"),
        }
    }
    assert_eq!(targets.len(), 10);
    assert!(covered > 1_000_000, "{covered} covered pixels");
}
