// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The ISP's coverage, depth and iteration against the recorded images of E606 and E607 (the
//! `isp/arith-1138` dataset of `$RESGX545_DATA`; the tests skip, saying so, without it and fail with
//! `RESGX545_REQUIRE_DATA`). Coverage is exact on every pixel of every image, reported fitted (the
//! rule is the record's fit); the depth is within 3 units of 2^-23 wherever the plane's gradient is
//! below 0.03 and refused above; the iterated clip z is within 4 units wherever its range per root
//! area is below 0.05 and refused above; the clip x has no stated tolerance and refuses. The
//! model record is E660 (2752 images: E606's 1536, E607's 874 fine and 342 fine2 cases).

use sgx_pipe::Outcome;
use sgx_pipe::arith::*;
use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::isp;
use std::path::PathBuf;

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env().root.map(|r| r.join("isp/arith-1138")).filter(|d| d.is_dir());
    if b.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no isp/arith-1138 (RESGX545_DATA)");
        eprintln!("SKIPPED: no isp/arith-1138 (set RESGX545_DATA)");
    }
    b
}

fn gz(p: PathBuf) -> Vec<u8> {
    sgx_pipe::gz::gunzip(&std::fs::read(&p).unwrap_or_else(|e| panic!("{}: {e}", p.display()))).unwrap()
}

#[derive(Debug, Default)]
struct Totals {
    cases: u64,
    refused: u64,
    colour_wrong: u64,
    background_wrong: u64,
    depth_checked: u64,
    depth_within: u64,
    depth_refused: u64,
    pixels: u64,
}

fn depth_jobs(set: &str, file: &str, dir: &str) -> Totals {
    let b = base().unwrap();
    let mut t = Totals::default();
    for c in parse_cases(&std::fs::read_to_string(b.join(file)).unwrap()) {
        if !c.jobs.contains('D') || (!set.is_empty() && c.set != set) {
            continue;
        }
        t.cases += 1;
        let tri = match tri_of(&c) {
            Ok(tri) => tri,
            Err(Outcome::Unsupported { ids, .. }) => {
                assert!(ids == ["Q240"] || ids == ["Q199"], "{ids:?}");
                t.refused += 1;
                continue;
            }
            Err(o) => panic!("{o:?}"),
        };
        let d = b.join(dir).join("D");
        let img =
            parse_image(&String::from_utf8_lossy(&gz(d.join(format!("{}.txt.gz", c.id)))), c.w, c.h).unwrap();
        let raw = dwords(&gz(d.join(format!("{}.depth.gz", c.id))));
        let dep = depth_image(&raw, c.w, c.h, pitch_g(c.w)).unwrap();
        let r = check_case(&tri, &c, &img, &dep);
        assert_eq!(r.colour_wrong + r.background_wrong, 0, "case {}", c.id);
        t.pixels += r.pixels;
        t.colour_wrong += r.colour_wrong;
        t.background_wrong += r.background_wrong;
        t.depth_checked += r.depth_checked;
        t.depth_within += r.depth_within;
        t.depth_refused += r.depth_refused;
    }
    t
}

#[test]
fn the_main_sweep_of_1536_images_is_reproduced_pixel_for_pixel_and_the_depth_within_3_units() {
    if base().is_none() {
        return;
    }
    let t = depth_jobs("", "cases.tsv", "main");
    assert_eq!((t.cases, t.refused), (1536, 0));
    assert_eq!((t.colour_wrong, t.background_wrong), (0, 0));
    assert_eq!(t.pixels, 14368768, "E606: 0 of 14368768 pixels mispredicted");
    // E606: 330075 covered pixels of fit and held-out at a gradient below 0.03; the repeats' too
    assert_eq!((t.depth_checked, t.depth_within), (330075 + 531 + 238, 330075 + 531 + 238));
    assert!(t.depth_refused > 0);
}

#[test]
fn the_fine_sets_of_e607_round_half_up_to_1_256_and_reproduce_every_image() {
    if base().is_none() {
        return;
    }
    let fine = depth_jobs("", "cases-fine.tsv", "fine");
    assert_eq!((fine.cases, fine.refused, fine.colour_wrong, fine.background_wrong), (874, 0, 0, 0));
    assert_eq!(fine.depth_checked, fine.depth_within);
    let fine2 = depth_jobs("", "cases-fine2.tsv", "fine2");
    // the 80 tiny-edge cases are on a 256 x 256 target: outside E606's sizes, refused (Q240)
    assert_eq!((fine2.cases, fine2.refused, fine2.colour_wrong, fine2.background_wrong), (422, 80, 0, 0));
    assert_eq!(fine2.depth_checked, fine2.depth_within);
}

#[test]
fn the_iterated_clip_z_is_within_4_units_and_the_clip_x_has_no_tolerance_to_check_against() {
    let Some(b) = base() else { return };
    let (mut checked, mut within, mut refused_x, mut wrong_cov) = (0u64, 0u64, 0u64, 0u64);
    for c in parse_cases(&std::fs::read_to_string(b.join("cases.tsv")).unwrap()) {
        if !c.jobs.contains('I') || c.set == "repeat" {
            continue;
        }
        let tri = tri_of(&c).unwrap();
        for k in 0..2u32 {
            let p = b.join("main").join(format!("I{k}")).join(format!("{}.txt.gz", c.id));
            let img = parse_image(&String::from_utf8_lossy(&gz(p)), c.w, c.h).unwrap();
            let r = check_iteration(&tri, &c, k, &img);
            wrong_cov += r.coverage_wrong;
            if k == 0 {
                checked += r.checked;
                within += r.within;
            } else {
                assert_eq!(r.checked, 0);
                refused_x += r.refused;
            }
        }
    }
    assert_eq!(wrong_cov, 0);
    // E606's table: pa0 below 0.05 range per root area, 116 triangles and 132050 pixels, max 3.7
    assert_eq!((checked, within), (132050, 132050));
    assert!(refused_x > 0);
}

/// The first render's image hash of E148's 13 sizes, E023's 128 x 96 and E174's 1024 x 768 and
/// 4096 x 4096 (the output of the runs): the library's triangle (8, 8), (56, 20), (20, 56) of a
/// 64 x 64 target, scaled, green on 0xff203040.
const FIRST_TRIANGLE: [(u32, u32, u64); 16] = [
    (64, 64, 0x99385a04ee01c585),
    (64, 128, 0x2f5dd87647c184e5),
    (64, 144, 0xb0d377886161df05),
    (64, 160, 0xf50c4d35490d22c5),
    (64, 192, 0x2fd97e2adceaf4c5),
    (64, 256, 0x26278369c4d1de25),
    (128, 64, 0x09154a26fa60fae5),
    (128, 128, 0x4a18985ca7f4b4e5),
    (128, 144, 0x5d1de4d7c7145be5),
    (128, 256, 0x661e1c72abc8c525),
    (256, 64, 0x75064171352dee25),
    (256, 128, 0x93c9ee017930f6a5),
    (256, 256, 0x6f2fbd77531efe25),
    (128, 96, 0x78d7390431620b65),
    (1024, 768, 0xc9e301d225fe2325),
    (4096, 4096, 0x08197f1b8b083325),
];

/// The default triangle of a w x h target on the ISP's grid (1/16 pixel vertices, scaled).
fn default_triangle(w: u32, h: u32) -> isp::Tri {
    let v = |x: i64, y: i64| (x * 16 * w as i64 / 64 * 16, y * 16 * h as i64 / 64 * 16);
    isp::Tri { v: [v(8, 8), v(56, 20), v(20, 56)], z: [0.5; 3] }
}

#[test]
fn the_rule_alone_reproduces_the_first_triangles_hash_at_all_16_sizes_whether_or_not_e606_ran_them() {
    // Analysis, not the model: the model refuses what E606 did not run (Q240: 13 of the 16 sizes), the
    // rule itself, asked at the other sizes, gives E148's and E174's recorded image exactly, hash for hash
    for (w, h, hash) in FIRST_TRIANGLE {
        let t = default_triangle(w, h);
        let img: Vec<u32> = (0..h)
            .flat_map(|y| (0..w).map(move |x| (x, y)))
            .map(|(x, y)| if t.covers(x, y) { GREEN } else { BG })
            .collect();
        assert_eq!(sgx_pipe::scene::fnv64(&img), hash, "{w} x {h}");
        let inside = isp::target_in_envelope(w, h).is_ok();
        assert_eq!(inside, [(64, 64), (128, 128), (256, 128)].contains(&(w, h)), "{w} x {h}");
    }
}
