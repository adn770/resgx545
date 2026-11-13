// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! `cube::point_index` (TEXTYPE 2 point-sampled with smp3d) against the kept cube jobs of
//! `$RESGX545_DATA` (the tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`):
//! E726's eight jobs (texture/p1141 tex-h-cube, the (s, t) rule's fit) and E844's two off-axis
//! jobs (render/closing-r4-render4x stage c, held out offline by E923). Every pixel's value is
//! 0xD0000000 | the dword index the sample read; the coordinates are the probe programs' own
//! (an fmad of (1 + x / 64 or 1 + y / 32) by K plus C, or a constant, all exact in f32). A pixel
//! the model refuses (an exact texel boundary at a major magnitude that is not a power of two,
//! Q284) is counted apart, never as a match; every other pixel must equal the model's index.

use sgx_pipe::Outcome;
use sgx_pipe::cube;
use sgx_pipe::data::Ctx;
use std::path::{Path, PathBuf};

const FIT: &str = "texture/p1141/out-hw/p1141tex-dumps/tex-h-cube";
const HELD: &str = "render/closing-r4-render4x/out/20261111-211315/c";

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env().root.filter(|r| r.join(FIT).is_dir() && r.join(HELD).is_dir());
    if b.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no cube jobs (RESGX545_DATA)");
        eprintln!("SKIPPED: no {FIT} or {HELD} (set RESGX545_DATA)");
    }
    b
}

/// One coordinate of the probe programs (p1141-cube.toml, closing-r4-render4x gen/cubegen.py).
#[derive(Clone, Copy)]
enum C {
    Const(f32),
    /// (1 + x / 64) K + C
    X(f32, f32),
    /// (1 + y / 32) K + C
    Y(f32, f32),
    /// 1 + (2 (x & 15) + 1) / 32 (cu-w02 and cu-w11's u)
    Map16,
}

fn coord(c: C, x: u32, y: u32) -> f32 {
    match c {
        C::Const(v) => v,
        C::X(k, a) => ((1.0 + x as f64 / 64.0) * k as f64 + a as f64) as f32,
        C::Y(k, a) => ((1.0 + y as f64 / 32.0) * k as f64 + a as f64) as f32,
        C::Map16 => (1.0 + (2 * (x & 15) + 1) as f64 / 32.0) as f32,
    }
}

/// The 64 x 32 o0 values of a probe's kept output ("probe NAME: row N: ...").
fn image(b: &Path, path: &str) -> Vec<u32> {
    let raw = std::fs::read(b.join(path)).unwrap_or_else(|e| panic!("{path}: {e}"));
    let text = String::from_utf8(sgx_pipe::gz::gunzip(&raw).unwrap()).unwrap();
    let mut img = vec![None; 64 * 32];
    for line in text.lines() {
        let Some(at) = line.find(": row ") else { continue };
        let (n, vals) = line[at + 6..].split_once(':').unwrap();
        let y: usize = n.trim().parse().unwrap();
        for (x, v) in vals.split_whitespace().enumerate() {
            img[y * 64 + x] = Some(u32::from_str_radix(v, 16).unwrap());
        }
    }
    img.into_iter().map(|p| p.expect("a pixel missing")).collect()
}

/// (matched, refused) over a job's 2048 pixels; panics on a mismatch.
fn replay(b: &Path, path: &str, uvw: [C; 3]) -> (u32, u32) {
    let img = image(b, path);
    let (mut ok, mut refused) = (0, 0);
    for y in 0..32 {
        for x in 0..64 {
            let c = uvw.map(|c| coord(c, x, y));
            let hw = img[(y * 64 + x) as usize];
            assert_eq!(hw >> 28, 0xd, "{path} ({x}, {y}): {hw:#x} is no texel tag");
            match cube::point_index(c, 16) {
                Ok(i) => {
                    assert_eq!(i, hw & 0x0fff_ffff, "{path} ({x}, {y}) at {c:?}");
                    ok += 1;
                }
                Err(Outcome::Unsupported { ids, .. }) => {
                    assert_eq!(ids, ["Q284"], "{path} ({x}, {y})");
                    refused += 1;
                }
                Err(o) => panic!("{path} ({x}, {y}): {o:?}"),
            }
        }
    }
    (ok, refused)
}

const L: C = C::X(1.5, -2.25);
const LY: C = C::Y(1.5, -2.25);

#[test]
fn e726_axis_and_sweep_jobs_fit_the_rule() {
    let Some(b) = base() else { return };
    // (job, u, v, w, refused): the six axis jobs refuse nothing (|ma| = 1), the two w sweeps
    // refuse the exact boundaries at |u| = 1 + odd / 32
    let jobs: [(&str, [C; 3], u32); 8] = [
        ("cu-zp", [L, LY, C::Const(1.0)], 0),
        ("cu-xp", [C::Const(1.0), L, LY], 0),
        ("cu-yp", [L, C::Const(1.0), LY], 0),
        ("cu-zn", [L, LY, C::Const(-1.0)], 0),
        ("cu-xn", [C::Const(-1.0), L, LY], 0),
        ("cu-yn", [L, C::Const(-1.0), LY], 0),
        ("cu-w02", [C::Map16, C::Const(0.53125), C::Y(2.0, -2.0)], 92),
        ("cu-w11", [C::Map16, C::Const(0.53125), C::Y(2.0, -3.0)], 64),
    ];
    for (job, uvw, want) in jobs {
        let (ok, refused) = replay(&b, &format!("{FIT}/{job}.txt.gz"), uvw);
        assert_eq!((ok, refused), (2048 - want, want), "{job}");
    }
}

#[test]
fn e844_off_axis_jobs_hold_out() {
    let Some(b) = base() else { return };
    // E844's method line: a, u = 1.5 (1 + x / 64) - 2.5, v = -0.5, w = 1.5 (1 + y / 32) - 2.25;
    // b, u = 0.5, v = 1.5 (1 + x / 64) - 2.25, w = 1.5 (1 + y / 32) - 2.5. E923: 2046 and 2044 of
    // 2048 under floor, every miss an exact boundary at a major magnitude not a power of two.
    let a = [C::X(1.5, -2.5), C::Const(-0.5), LY];
    let bb = [C::Const(0.5), L, C::Y(1.5, -2.5)];
    assert_eq!(replay(&b, &format!("{HELD}/c-cube-a.txt.gz"), a), (2021, 27));
    assert_eq!(replay(&b, &format!("{HELD}/c-cube-b.txt.gz"), bb), (2024, 24));
    // the control of E844 (E726's cu-xn rerun) under the same rule
    let xn = [C::Const(-1.0), L, LY];
    assert_eq!(replay(&b, &format!("{HELD}/c-cu-xn.txt.gz"), xn), (2048, 0));
}
