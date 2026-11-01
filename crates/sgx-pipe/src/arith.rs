// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The ISP's triangle arithmetic against the recorded images of E606 and E607 (12.3): the cases of
//! `isp/arith-1138/cases*.tsv` (vertices in 1/2^K pixel, K = 8 unless a last column says more), the
//! colour image and the stored depth of the depth job of each, and the iteration probes' images.
//! The model under test is [`crate::isp`]: coverage by the exact test, depth by the plane through
//! the rounded vertices, the iterated value by the plane through the attribute (`crate::iter`).

use crate::Outcome;
use crate::isp::{self, Tri};
use crate::zls;

pub const GREEN: u32 = 0xff00_ff00;
pub const BG: u32 = 0xff20_3040;

#[derive(Debug, Clone, PartialEq)]
pub struct Case {
    pub id: u32,
    pub set: String,
    pub class: String,
    pub w: u32,
    pub h: u32,
    /// the vertices as integers in 1/2^unit pixel
    pub v: [(i64, i64); 3],
    pub z: [f32; 3],
    pub jobs: String,
    pub unit: u32,
}

pub fn parse_cases(text: &str) -> Vec<Case> {
    text.lines()
        .filter_map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            if f.len() < 16 {
                return None;
            }
            let n = |i: usize| f[i].parse::<i64>().ok();
            let v = [(n(5)?, n(6)?), (n(7)?, n(8)?), (n(9)?, n(10)?)];
            Some(Case {
                id: f[0].parse().ok()?,
                set: f[1].to_string(),
                class: f[2].to_string(),
                w: f[3].parse().ok()?,
                h: f[4].parse().ok()?,
                v,
                z: [f[11].parse().ok()?, f[12].parse().ok()?, f[13].parse().ok()?],
                jobs: f[15].to_string(),
                unit: f.get(16).and_then(|u| u.parse().ok()).unwrap_or(8),
            })
        })
        .collect()
}

/// The pixel rows of a tool's output ("row N: 0x..." of `tri`, "probe NAME: row N: ..." of `probe`):
/// w x h dwords, or None when a row is missing or short.
pub fn parse_image(text: &str, w: u32, h: u32) -> Option<Vec<u32>> {
    let mut img = vec![0u32; (w * h) as usize];
    let mut seen = vec![false; h as usize];
    for line in text.lines() {
        let Some(at) = line.find("row ") else { continue };
        if at > 0 && !line[..at].contains("probe ") {
            continue;
        }
        let Some((n, vals)) = line[at + 4..].split_once(':') else { continue };
        let Ok(y) = n.trim().parse::<u32>() else { continue };
        let vals: Vec<u32> = vals
            .split_whitespace()
            .filter_map(|t| u32::from_str_radix(t.trim_start_matches("0x"), 16).ok())
            .collect();
        if y < h && vals.len() == w as usize {
            img[(y * w) as usize..((y + 1) * w) as usize].copy_from_slice(&vals);
            seen[y as usize] = true;
        }
    }
    seen.iter().all(|&s| s).then_some(img)
}

/// The library's pitch for the dump of a w-wide target: G = tiles across - 1, at least 1 (the
/// tiles of a row do not overlap; run_p1138.py).
pub fn pitch_g(w: u32) -> u32 {
    w.div_ceil(32).saturating_sub(1).max(1)
}

/// The depth of every pixel from a depth-buffer dump (E465's address rule).
pub fn depth_image(raw: &[u32], w: u32, h: u32, g: u32) -> Option<Vec<u32>> {
    let mut out = Vec::with_capacity((w * h) as usize);
    for y in 0..h {
        for x in 0..w {
            out.push(*raw.get(zls::store_dword(x, y, g) as usize)?);
        }
    }
    Some(out)
}

/// The triangle of a case on the ISP's grid, or the refusal: the vertices are converted from their
/// own unit to pixels and rounded half up to 1/256 (E607); the envelope of E606 applies.
pub fn tri_of(c: &Case) -> Result<Tri, Outcome> {
    isp::target_in_envelope(c.w, c.h)?;
    let scale = (1u64 << c.unit) as f64;
    let mut v = [(0, 0); 3];
    for (o, &(x, y)) in v.iter_mut().zip(&c.v) {
        *o = (isp::snap(x as f64 / scale)?, isp::snap(y as f64 / scale)?);
    }
    let t = Tri { v, z: c.z };
    isp::vertices_in_envelope(c.w, c.h, &t)?;
    Ok(t)
}

/// What the model says of one case against its recorded depth job.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct CaseCheck {
    pub pixels: u64,
    /// pixels whose colour (covered or not) differs from the recorded image
    pub colour_wrong: u64,
    /// covered pixels checked for depth, and those within the tolerance
    pub depth_checked: u64,
    pub depth_within: u64,
    /// the largest error of a checked pixel, in 2^-23
    pub depth_max_units: f64,
    /// uncovered pixels whose stored depth is not 1.0
    pub background_wrong: u64,
    /// the covered pixels the depth check refused: gradient at or above the limit
    pub depth_refused: u64,
}

/// Check the coverage and the depth of `c` against the recorded colour image and depth image.
pub fn check_case(t: &Tri, c: &Case, image: &[u32], depth: &[u32]) -> CaseCheck {
    let mut r = CaseCheck::default();
    let low = t.gradient() < isp::DEPTH_GRADIENT_LIMIT;
    for y in 0..c.h {
        for x in 0..c.w {
            let i = (y * c.w + x) as usize;
            r.pixels += 1;
            let covered = t.covers(x, y);
            let want = if covered { GREEN } else { BG };
            if image[i] != want {
                r.colour_wrong += 1;
            }
            let got = f32::from_bits(depth[i]) as f64;
            if !covered {
                r.background_wrong += u64::from(depth[i] != zls::BACKGROUND);
            } else if low {
                r.depth_checked += 1;
                let e = (got - t.depth_at(x, y)).abs() / isp::DEPTH_UNIT;
                r.depth_max_units = r.depth_max_units.max(e);
                r.depth_within += u64::from(e <= isp::DEPTH_TOLERANCE as f64);
            } else {
                r.depth_refused += 1;
            }
        }
    }
    r
}

/// What the iteration probe of a case says against its recorded image.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct IterCheck {
    pub pixels: u64,
    /// pixels that differ in coverage: a covered pixel holding the background colour, or an
    /// uncovered one holding a value
    pub coverage_wrong: u64,
    /// covered pixels checked against the plane and those within the tolerance
    pub checked: u64,
    pub within: u64,
    pub max_units: f64,
    /// covered pixels of poorly conditioned triangles: refused (Q200)
    pub refused: u64,
}

/// The vertex values the probe iterated: pa0 the vertices' clip z (2 z - 1), pa1 the clip x
/// (window x over half the width, minus 1): `which` is 0 or 1 (iter.toml, extra2_p1138.py).
pub fn iter_values(c: &Case, which: u32) -> [f32; 3] {
    let k = (1u64 << c.unit) as f64;
    std::array::from_fn(|i| {
        if which == 0 {
            (2.0 * c.z[i] as f64 - 1.0) as f32
        } else {
            (c.v[i].0 as f64 / k / (c.w as f64 / 2.0) - 1.0) as f32
        }
    })
}

/// Check coverage and iterated value of a probe image (the colour is the iterated float where the
/// ISP covers, the background colour elsewhere).
pub fn check_iteration(t: &Tri, c: &Case, which: u32, image: &[u32]) -> IterCheck {
    let vals = iter_values(c, which);
    let mut r = IterCheck::default();
    for y in 0..c.h {
        for x in 0..c.w {
            let v = image[(y * c.w + x) as usize];
            r.pixels += 1;
            if !t.covers(x, y) {
                r.coverage_wrong += u64::from(v != BG);
                continue;
            }
            let attr = if which == 0 { crate::iter::Attr::ClipZ } else { crate::iter::Attr::Other };
            match crate::iter::at_centre(t, vals, attr, x, y) {
                Err(_) => r.refused += 1,
                Ok(want) => {
                    if v == BG {
                        r.coverage_wrong += 1;
                        continue;
                    }
                    r.checked += 1;
                    let e = (f32::from_bits(v) as f64 - want).abs() / isp::DEPTH_UNIT;
                    r.max_units = r.max_units.max(e);
                    r.within += u64::from(crate::iter::near(f32::from_bits(v), want));
                }
            }
        }
    }
    r
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_case_line_parses_with_its_unit() {
        let l = "7\tfit\tsmall\t64\t64\t1\t2\t3\t4\t5\t6\t0.25\t0.5\t0.75\t-\tD";
        let c = &parse_cases(l)[0];
        assert_eq!((c.id, c.w, c.v[2], c.z[2], c.unit), (7, 64, (5, 6), 0.75, 8));
        let c = &parse_cases(&format!("{l}\t12"))[0];
        assert_eq!(c.unit, 12);
        assert!(parse_cases("short\tline").is_empty());
    }

    #[test]
    fn rows_of_both_tool_forms_parse_and_a_missing_row_is_none() {
        let t = "row 0: 0x1 0x2\nprobe p: row 1: 3 4\nnoise row 2: 9\n";
        assert_eq!(parse_image(t, 2, 2).unwrap(), vec![1, 2, 3, 4]);
        assert!(parse_image("row 0: 0x1 0x2\n", 2, 2).is_none());
    }

    #[test]
    fn the_pitch_is_tiles_across_minus_one_and_at_least_one() {
        assert_eq!([pitch_g(64), pitch_g(128), pitch_g(256), pitch_g(32)], [1, 3, 7, 1]);
    }

    #[test]
    fn a_depth_buffer_dump_reads_back_through_the_store_rule() {
        // a 64 x 32 target, G = 1: two tiles side by side, 512 dwords each
        let mut raw = vec![zls::FILL; 2048];
        raw[zls::store_dword(33, 17, 1) as usize] = 0x3f00_0000;
        let d = depth_image(&raw, 64, 32, 1).unwrap();
        assert_eq!(d[17 * 64 + 33], 0x3f00_0000);
        assert!(depth_image(&raw[..100], 64, 32, 1).is_none());
    }
}
