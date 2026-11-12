// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! R7-geo's depth jobs (stages zd and zf of `render/closing-r7-geo` in `$RESGX545_DATA`; the
//! tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`): every kept image of
//! a random triangle must equal `isp::coverage_image` pixel for pixel, on E680's four targets of
//! zd (E912) and on the ten targets of zf around E606's (E913), and the depth on all of them
//! refuses (E606's tolerance missed by 1- and 2-pixel triangles there): Q262 on E680's targets,
//! Q240 on the others.

use sgx_pipe::Outcome;
use sgx_pipe::data::Ctx;
use sgx_pipe::isp::{self, Tri};
use std::collections::BTreeSet;
use std::path::PathBuf;

const TRIANGLE: u32 = 0xff00_ff00;
const BACKGROUND: u32 = 0xff20_3040;
const ATTEMPT: &str = "render/closing-r7-geo/out/20261112-211113";

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env().root.map(|r| r.join(ATTEMPT)).filter(|d| d.is_dir());
    if b.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATTEMPT} (RESGX545_DATA)");
        eprintln!("SKIPPED: no {ATTEMPT} (set RESGX545_DATA)");
    }
    b
}

/// One kept job: the target, the vertices in 1/256 pixel and the image rows (empty above the
/// sizes the session printed: zd's 640 x 480 and up keep the depth dump only).
struct Job {
    w: u32,
    h: u32,
    v: [(i64, i64); 3],
    rows: Vec<Vec<u32>>,
}

fn job(text: &str) -> Job {
    let (mut w, mut h, mut v, mut rows) = (0, 0, [(0, 0); 3], vec![]);
    for l in text.lines() {
        if let Some(r) = l.strip_prefix("tri: vertices256 ") {
            let n: Vec<i64> =
                r.split(',').next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
            v = [(n[0], n[1]), (n[2], n[3]), (n[4], n[5])];
        } else if let Some(r) = l.strip_prefix("target: ") {
            let (a, b) = r.split_whitespace().next().unwrap().split_once('x').unwrap();
            (w, h) = (a.parse().unwrap(), b.parse().unwrap());
        } else if let Some(r) = l.strip_prefix("row ") {
            let (_, px) = r.split_once(':').unwrap();
            rows.push(px.split_whitespace().map(|t| u32::from_str_radix(&t[2..], 16).unwrap()).collect());
        }
    }
    Job { w, h, v, rows }
}

fn replay(stage: &str, want: &[(u32, u32)], depth_q: &str) {
    let Some(b) = base() else { return };
    let dir = b.join(stage);
    let mut sizes = BTreeSet::new();
    let mut n = 0;
    for e in std::fs::read_dir(&dir).unwrap() {
        let p = e.unwrap().path();
        let name = p.file_name().unwrap().to_string_lossy().into_owned();
        if !name.starts_with(&format!("{stage}-")) || name.contains("-ctl-") || !name.ends_with(".txt.gz") {
            continue;
        }
        let raw = std::fs::read(&p).unwrap();
        let j = job(&String::from_utf8(sgx_pipe::gz::gunzip(&raw).unwrap()).unwrap());
        sizes.insert((j.w, j.h));
        // the depth on every target of the session refuses
        match isp::target_in_envelope(j.w, j.h) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, [depth_q], "{name}"),
            o => panic!("{name}: {o:?}"),
        }
        let t = Tri { v: j.v, z: [0.5; 3] };
        let model = isp::coverage_image(j.w, j.h, &t).unwrap_or_else(|o| panic!("{name}: {o:?}"));
        if j.rows.is_empty() {
            continue;
        }
        assert_eq!(j.rows.len(), j.h as usize, "{name}");
        for (y, row) in j.rows.iter().enumerate() {
            for (x, &p) in row.iter().enumerate() {
                assert!(p == TRIANGLE || p == BACKGROUND, "{name} ({x}, {y}) {p:#x}");
                assert_eq!(p == TRIANGLE, model[y * j.w as usize + x], "{name} ({x}, {y})");
            }
        }
        n += 1;
    }
    assert_eq!(sizes, want.iter().copied().collect(), "{stage}");
    assert!(n >= 24, "{stage}: {n} images compared");
}

#[test]
fn the_coverage_rule_draws_every_kept_image_of_zf_on_the_ten_targets_around_e606s() {
    replay("zf", &isp::E913_TARGETS, "Q240");
}

#[test]
fn the_coverage_rule_draws_every_kept_image_of_zd_and_the_depth_there_refuses() {
    replay("zd", &[(512, 256), (640, 480), (1024, 768), (2048, 1024), (4096, 4096)], "Q262");
}
