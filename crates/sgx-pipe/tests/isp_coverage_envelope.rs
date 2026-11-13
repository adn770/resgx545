// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The coverage rule on E680's ten targets (96 x 64 to 4096 x 4096), coverage only: the frozen
//! sample is, per target and per class of group S1 (small, medium, large, centre, pairA, pairB),
//! the case of the lowest id in the cases table of the `isp/coverage-envelope` dataset of
//! `$RESGX545_DATA` (60 cases; the tests skip, saying so, without it and fail with
//! `RESGX545_REQUIRE_DATA`). Each case's whole image (the tool's `--pixels-rle` rows) must equal
//! `isp::coverage_image` pixel for pixel; the depth on those targets stays refused (Q262).
//! Groups S2 (E681: 588 sweeps across the half-grid tie, vertices in 1/4096 pixel, 1/1024 from
//! 2048 wide, through `isp::snap`) and S5 (E682: 160 long edges at a cross product of +-1 in
//! 1/65536 pixel squared through the target's centre pixel) are replayed whole, every case.

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

/// Every case of a group of the cases table: (id, set, class, w, h, vertices in pixels as the
/// table's integers over 2^bits).
struct Swept {
    id: u32,
    set: String,
    class: String,
    w: u32,
    h: u32,
    bits: u32,
    n: [(i64, i64); 3],
}

fn group(table: &str, g: &str) -> Vec<Swept> {
    table
        .lines()
        .filter_map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            (f.len() >= 13 && f[2] == g).then(|| {
                let n = |i: usize| f[i].parse::<i64>().unwrap();
                Swept {
                    id: f[0].parse().unwrap(),
                    set: f[1].to_string(),
                    class: f[3].to_string(),
                    w: f[4].parse().unwrap(),
                    h: f[5].parse().unwrap(),
                    bits: f[6].parse().unwrap(),
                    n: [(n(7), n(8)), (n(9), n(10)), (n(11), n(12))],
                }
            })
        })
        .collect()
}

/// A vertex on the 1/256 grid by `round` from the table's integer over 2^bits.
fn grid(c: &Swept, round: fn(i64, u32) -> i64) -> Tri {
    Tri { v: c.n.map(|(x, y)| (round(x, c.bits), round(y, c.bits))), z: [0.5; 3] }
}

/// E607's rule through the model: isp::snap of the nominal coordinate.
fn half_up(n: i64, bits: u32) -> i64 {
    isp::snap(n as f64 / f64::from(1u32 << bits)).unwrap()
}

/// E681's rivals: half down and floor to 1/256.
fn half_down(n: i64, bits: u32) -> i64 {
    let d = 1i64 << (bits - 8);
    (n + d / 2 - 1).div_euclid(d)
}

fn floor(n: i64, bits: u32) -> i64 {
    n.div_euclid(1i64 << (bits - 8))
}

/// The hardware's rows of a case: per row the one run of triangle pixels [a, b), or None. A row
/// with two runs cannot be a triangle's (its rows are intervals) and fails the case.
fn hw_rows(b: &std::path::Path, c: &Swept) -> Vec<Option<(u32, u32)>> {
    let raw = std::fs::read(b.join("main/raw").join(format!("{}.txt.gz", c.id))).unwrap();
    let text = String::from_utf8(sgx_pipe::gz::gunzip(&raw).unwrap()).unwrap();
    let mut rows = vec![None; c.h as usize];
    let mut seen = vec![false; c.h as usize];
    for line in text.lines() {
        let Some(rest) = line.strip_prefix("rle ") else { continue };
        let (y, runs) = rest.split_once(':').unwrap();
        let y: usize = y.trim().parse().unwrap();
        let mut x = 0;
        for run in runs.split_whitespace() {
            let (col, n) = run.trim_start_matches("0x").split_once('x').unwrap();
            let (col, n) = (u32::from_str_radix(col, 16).unwrap(), n.parse::<u32>().unwrap());
            assert!(col == TRIANGLE || col == BACKGROUND, "case {}: colour {col:#x}", c.id);
            if col == TRIANGLE {
                assert!(rows[y].is_none(), "case {} row {y}: two runs", c.id);
                rows[y] = Some((x, x + n));
            }
            x += n;
        }
        assert_eq!(x, c.w, "case {} row {y}", c.id);
        seen[y] = true;
    }
    assert!(seen.iter().all(|&s| s), "case {}: a row missing", c.id);
    rows
}

/// The rows where the model's coverage differs from the hardware's. The model's covered pixels
/// in a row form an interval (each edge's test is a half-line along the row), so a drawn row
/// [a, b) agrees iff the model covers a and b - 1 and neither a - 1 nor b; a row with no drawn
/// pixel is scanned whole when a sample of it lies within the vertices' y range, and holds no
/// covered sample otherwise.
fn wrong_rows(w: u32, h: u32, t: &Tri, rows: &[Option<(u32, u32)>]) -> usize {
    isp::coverage_target_in_envelope(w, h).unwrap();
    isp::coverage_vertices_in_envelope(w, h, t).unwrap();
    let (lo, hi) = (t.v.iter().map(|v| v.1).min().unwrap(), t.v.iter().map(|v| v.1).max().unwrap());
    let no = |x: i64, y: u32| x < 0 || x >= i64::from(w) || !t.covers(x as u32, y);
    (0..h)
        .filter(|&y| match rows[y as usize] {
            Some((a, b)) => {
                !(t.covers(a, y) && t.covers(b - 1, y) && no(i64::from(a) - 1, y) && no(i64::from(b), y))
            }
            None => {
                let sy = i64::from(y) * 256 + 128;
                sy >= lo && sy <= hi && (0..w).any(|x| t.covers(x, y))
            }
        })
        .count()
}

/// Run `f` over the cases on every core, a case at a time: the 4096 x 4096 targets are the
/// slow ones.
fn par<T: Send>(cases: &[Swept], f: impl Fn(&Swept) -> T + Sync) -> Vec<T> {
    let k = std::thread::available_parallelism().map_or(4, |n| n.get());
    let next = std::sync::atomic::AtomicUsize::new(0);
    let mut out: Vec<(usize, T)> = std::thread::scope(|s| {
        let hs: Vec<_> = (0..k)
            .map(|_| {
                s.spawn(|| {
                    let mut v = Vec::new();
                    loop {
                        let i = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                        let Some(c) = cases.get(i) else { break v };
                        v.push((i, f(c)));
                    }
                })
            })
            .collect();
        hs.into_iter().flat_map(|h| h.join().unwrap()).collect()
    });
    out.sort_by_key(|p| p.0);
    out.into_iter().map(|p| p.1).collect()
}

#[test]
fn e681s_588_tie_sweeps_are_the_half_up_rule_pixel_for_pixel() {
    let Some(b) = base() else { return };
    let cases = group(&std::fs::read_to_string(b.join("cases-1140.tsv")).unwrap(), "S2");
    assert_eq!(cases.len(), 588);
    assert_eq!(cases.iter().filter(|c| c.set == "fit").count(), 300);
    // (wrong pixels under half up, cases half down misses, cases floor misses)
    let r = par(&cases, |c| {
        assert!(c.bits == 12 || (c.bits == 10 && c.w >= 2048), "case {}: 1/{}", c.id, 1u32 << c.bits);
        let rows = hw_rows(&b, c);
        let diff = |t: Tri| wrong_rows(c.w, c.h, &t, &rows);
        (c.id, diff(grid(c, half_up)), diff(grid(c, half_down)) > 0, diff(grid(c, floor)) > 0)
    });
    let wrong: Vec<_> = r.iter().filter(|x| x.1 > 0).map(|x| (x.0, x.1)).collect();
    assert!(wrong.is_empty(), "cases off the rule: {wrong:?}");
    // the replay discriminates: E681's rivals miss 42 and 204 cases
    assert_eq!(r.iter().filter(|x| x.2).count(), 42, "half down");
    assert_eq!(r.iter().filter(|x| x.3).count(), 204, "floor");
}

#[test]
fn e682s_160_long_edges_at_a_cross_product_of_one_are_the_exact_edge_test() {
    let Some(b) = base() else { return };
    let cases = group(&std::fs::read_to_string(b.join("cases-1140.tsv")).unwrap(), "S5");
    assert_eq!(cases.len(), 160);
    assert_eq!(cases.iter().filter(|c| c.set == "heldout").count(), 80);
    let r = par(&cases, |c| {
        assert_eq!(c.bits, 8, "case {}", c.id);
        let t = Tri { v: c.n, z: [0.5; 3] };
        let rows = hw_rows(&b, c);
        let (cx, cy) = (c.w / 2, c.h / 2);
        (c.id, c.class.clone(), wrong_rows(c.w, c.h, &t, &rows), t.covers(cx, cy))
    });
    let wrong: Vec<_> = r.iter().filter(|x| x.2 > 0).map(|x| (x.0, x.2)).collect();
    assert!(wrong.is_empty(), "cases off the rule: {wrong:?}");
    // half the cases draw the centre pixel, half do not: the edge decides it
    let inside = r.iter().filter(|x| x.3).count();
    assert_eq!(inside, 80, "centre pixels drawn");
}
