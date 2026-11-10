// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! MTE: viewport, cull, clamp, 1/w, window coordinates, clip planes (12.2): only what records
//! state. The state block's words (E347: presence 0xdf43, 18 dwords), the viewport on the clip
//! position (E061, E193), the 1/w the TA stores and its minimum and replacement (E063, E197), the
//! clip at z = -w and z = w (E287). Everything else refuses: culling (MTECTL bits 1:0), the
//! output select other than the library's, perspective w, a triangle the clip removes or cuts.

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q069", "Q039", "Q116", "Q162", "Q230"];

/// A refusing stub for the parts of the unit nothing models yet.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the MTE models the library's state block, w = 1 and whole triangles only", OPEN)
}

/// The state block of a draw (presence word 0xdf43).
#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub isp: [u32; 2],
    /// the pixel PDS words the TA copies into its object (E306)
    pub pds: [u32; 3],
    /// the viewport: x offset, x scale, y offset, y scale, z offset, z scale
    pub vp: [f32; 6],
}

/// The state block's word 14, WCLAMP: the model reads it nowhere (a w of 1 never reaches it). The
/// values dumped are the library's 0x3727c5ac and 1e-3 (ta-objects-wclamp: the object came out
/// byte for byte the same), so another value refuses (Q231).
const WCLAMP: [u32; 2] = [0x3727_c5ac, 0x3a83_126f];

pub fn state(w: &[u32]) -> Result<State, Outcome> {
    let open = |why: String, id: &str| Outcome::unsupported(&why, &[id]);
    if w.len() != 18 || w[0] != 0xdf43 {
        return Err(open(
            format!(
                "an MTE state block of {} words, presence {:#x}: only 0xdf43 of 18 words is placed (E347)",
                w.len(),
                w.first().copied().unwrap_or(0)
            ),
            "Q069",
        ));
    }
    if w[13] != 0x43000 {
        return Err(open(
            format!(
                "OUTSEL {:#x}: only the library's 0x43000 (4 dwords, 1/w stored) was matched to objects (E286)",
                w[13]
            ),
            "Q162",
        ));
    }
    // MTECTL: bits 1:0 cull a winding (E062: not modelled); bits 2 to 5 and 7 changed nothing on an unclipped triangle
    if w[15] != 0x0155_5620 || w[16] != 0 || w[17] != 0 {
        return Err(open(
            format!(
                "MTECTL {:#x}, COORDSIZE {:#x}, COORDFMT {:#x}: the library's words only (culling, coordinate sets are not modelled)",
                w[15], w[16], w[17]
            ),
            "Q069",
        ));
    }
    if !WCLAMP.contains(&w[14]) {
        return Err(open(
            format!("WCLAMP {:#x}: only {WCLAMP:#x?} were run, and the model reads it nowhere", w[14]),
            "Q231",
        ));
    }
    let f = |i: usize| f32::from_bits(w[i]);
    Ok(State { isp: [w[1], w[2]], pds: [w[3], w[4], w[5]], vp: [f(6), f(7), f(8), f(9), f(10), f(11)] })
}

/// The end-of-scene block (presence 0x2000): its term word.
pub fn term(w: &[u32]) -> Result<u32, Outcome> {
    match w {
        [0x2000, t] => Ok(*t),
        _ => Err(Outcome::unsupported(
            &format!("an end-of-scene block {w:x?}: only presence 0x2000 and a term word (E347)"),
            &["Q069"],
        )),
    }
}

/// A vertex after the MTE: window x and y, depth, and the 1/w the object stores.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Vertex {
    pub x: f32,
    pub y: f32,
    pub z: f32,
    pub rhw: f32,
}

/// The 1/w the TA stores: `rhw` kept above `min`, `clamp` stored in its place otherwise
/// (E197, [infer] from three values of the minimum). Returns the value and whether the
/// replacement was used.
pub fn stored_rhw(rhw: f32, min: f32, clamp: f32) -> (f32, bool) {
    if rhw > min { (rhw, false) } else { (clamp, true) }
}

fn refuse230(why: impl AsRef<str>) -> Outcome {
    Outcome::unsupported(why.as_ref(), &["Q230"])
}

/// The float32 reciprocal of `w` rounded toward zero (RZ32): what E754's e3i jobs measured stored
/// as 1/w inside the guard band, 4 of 4 (round-to-nearest refuted).
fn rhw_rz32(w: f32) -> f32 {
    let exact = 1.0f64 / f64::from(w);
    let r = exact as f32;
    if f64::from(r).abs() > exact.abs() { f32::from_bits(r.to_bits() - 1) } else { r }
}

/// The w values E754's e3i jobs ran: w = 3, 7, 0.003 and 3e-5, all three vertices alike, x and y
/// scaled by w (the divided position is the original triangle, inside the viewport), depth z = 0.
/// Anything else with a w other than 1 stays refused (Q230): other exponents, a perspective
/// triangle, depth, the guard band's limit.
fn band_w(c: &[[f32; 4]; 3]) -> Result<(), Outcome> {
    let w = c[0][3];
    if !(3e-5..=7.0).contains(&w) || c.iter().any(|v| v[3] != w) {
        return Err(refuse230(
            "a w other than 1 outside E754's runs (one w of 3e-5 to 7 at all three vertices): the 1/w and depth of a perspective vertex were not dumped (E063, E194)",
        ));
    }
    if c.iter().any(|v| v[2] != 0.0) {
        return Err(refuse230("the depth at a w other than 1 was not scored (E754)"));
    }
    if c.iter().any(|v| (v[0] / w).abs() > 1.0 || (v[1] / w).abs() > 1.0) {
        return Err(refuse230(
            "a vertex outside the viewport at a w other than 1: E754 ran inside it, the guard band's limit was not run",
        ));
    }
    Ok(())
}

/// The window coordinates the object's packed block can hold: 24 bits of (v + 4096) * 256.
const RANGE: std::ops::Range<f32> = -4096.0..12288.0;

/// The three vertices' clip positions through the viewport. Whole triangles with w = 1 inside
/// z = -w and z = w only: what the TA writes for a triangle the clip removes or cuts, and the depth
/// and 1/w of a perspective vertex, were not dumped (Q230). `rhw_min` and `rhw_clamp` are the
/// command's float words. Returns the vertices and whether the 1/w replacement was used.
pub fn triangle(
    st: &State,
    clip: [[u32; 4]; 3],
    rhw_min: u32,
    rhw_clamp: u32,
) -> Result<([Vertex; 3], bool), Outcome> {
    let c = clip.map(|v| v.map(f32::from_bits));
    if c.iter().any(|v| v.iter().any(|x| !x.is_finite())) {
        return Err(refuse230("a non-finite clip coordinate"));
    }
    if c.iter().any(|v| v[3] != 1.0) {
        band_w(&c)?;
    }
    // clip against z = -w and z = w (E287 measured pixels: a triangle wholly beyond a plane is
    // removed from the image, a plane through it cuts it); what the TA writes for either was not
    // dumped, so a vertex beyond a plane refuses
    if c.iter().any(|v| v[2] < -v[3] || v[2] > v[3]) {
        return Err(refuse230(
            "a vertex beyond z = -w or z = w: whether the TA writes an object for a triangle the clip removes, and what for one it cuts, was not dumped (E287 measured pixels)",
        ));
    }
    let mut used = false;
    let mut out = [Vertex { x: 0.0, y: 0.0, z: 0.0, rhw: 0.0 }; 3];
    for (o, v) in out.iter_mut().zip(&c) {
        let (min, clamp) = (f32::from_bits(rhw_min), f32::from_bits(rhw_clamp));
        let r = rhw_rz32(v[3]);
        if r == min {
            return Err(refuse230(
                "a 1/w equal to the minimum: E197's values were all clear of the boundary",
            ));
        }
        let (rhw, u) = stored_rhw(r, min, clamp);
        if u && v[3] != 1.0 {
            return Err(refuse230(
                "a 1/w replaced by the clamp at a w other than 1: E754's clamp jobs shrank the triangle by w / clamp and stored the clamp's reciprocal, no rule fits all",
            ));
        }
        used |= u;
        *o = Vertex {
            x: st.vp[0] + st.vp[1] * (v[0] / v[3]),
            y: st.vp[2] + st.vp[3] * (v[1] / v[3]),
            z: st.vp[4] + st.vp[5] * v[2],
            rhw,
        };
        if !RANGE.contains(&o.x) || !RANGE.contains(&o.y) {
            return Err(refuse230(format!(
                "window coordinate ({}, {}) outside the packed block's range",
                o.x, o.y
            )));
        }
    }
    Ok((out, used))
}

#[cfg(test)]
mod tests {
    use super::*;

    const F: fn(f32) -> u32 = f32::to_bits;

    /// The library's state block for a 128 x 128 target (build.rs of the scene: render.c).
    fn block(vp: [f32; 4]) -> Vec<u32> {
        vec![
            0xdf43,
            0x01d0_0200,
            0x10f0,
            0x0400_0004,
            0x0003_0001,
            0x0400_0000,
            F(vp[0]),
            F(vp[1]),
            F(vp[2]),
            F(vp[3]),
            F(0.5),
            F(0.5),
            0,
            0x43000,
            0x3727_c5ac,
            0x0155_5620,
            0,
            0,
        ]
    }

    fn refused(r: Result<impl std::fmt::Debug, Outcome>, id: &str) {
        match r {
            Err(Outcome::Unsupported { ids, .. }) => {
                assert!(ids.iter().any(|i| i == id), "{ids:?} lacks {id}")
            }
            r => panic!("not refused under {id}: {r:?}"),
        }
    }

    #[test]
    fn the_library_state_block_gives_isp_words_pds_words_and_viewport() {
        let s = state(&block([64.0; 4])).unwrap();
        assert_eq!((s.isp, s.pds), ([0x01d0_0200, 0x10f0], [0x0400_0004, 0x0003_0001, 0x0400_0000]));
        assert_eq!(s.vp, [64.0, 64.0, 64.0, 64.0, 0.5, 0.5]);
    }

    #[test]
    fn a_block_other_than_the_librarys_is_refused_by_question() {
        let mut w = block([64.0; 4]);
        w[0] = 0xd4c3; // another presence word: the words are placed by a table no record gives (E347)
        refused(state(&w), "Q069");
        let mut w = block([64.0; 4]);
        w[13] = 0x43100; // OUTSEL: bits 8, 10, 11, 15 or other sizes (Q162, E286)
        refused(state(&w), "Q162");
        let mut w = block([64.0; 4]);
        w[15] ^= 1; // MTECTL cull mode 1 culls a winding (E062): not modelled
        refused(state(&w), "Q069");
        let mut w = block([64.0; 4]);
        w[16] = 2; // a coordinate set (E192, E541's layout, other jobs)
        refused(state(&w), "Q069");
        refused(state(&w[..10]), "Q069");
        let mut w = block([64.0; 4]);
        w[14] = F(1.0); // WCLAMP: read nowhere by the model, the dumped values only (Q231)
        refused(state(&w), "Q231");
        w[14] = 0x3a83_126f; // 1e-3, dumped: the object did not change at w = 1
        assert!(state(&w).is_ok());
    }

    #[test]
    fn the_end_of_scene_block_holds_the_term_word() {
        assert_eq!(term(&[0x2000, 0x0003_0003]).unwrap(), 0x0003_0003);
        refused(term(&[0x2001, 0x3]), "Q069");
    }

    #[test]
    fn the_rhw_floats_replace_a_small_one_by_the_clamp_value_e197() {
        // 1/w of 0.8, 0.364 and 0.615, clamp 0.25: a minimum of 0.3 replaces none, 0.5 the 0.364,
        // 0.7 the 0.364 and the 0.615 (E197)
        let r = [0.8f32, 0.364, 0.615];
        let run = |min: f32| r.map(|v| stored_rhw(v, min, 0.25));
        assert_eq!(run(0.3), [(0.8, false), (0.364, false), (0.615, false)]);
        assert_eq!(run(0.5), [(0.8, false), (0.25, true), (0.615, false)]);
        assert_eq!(run(0.7), [(0.8, false), (0.25, true), (0.25, true)]);
    }

    fn clip(x: f32, y: f32, z: f32, w: f32) -> [u32; 4] {
        [F(x), F(y), F(z), F(w)]
    }

    #[test]
    fn a_vertex_goes_through_the_viewport_x_y_and_z_and_keeps_its_rhw() {
        let s = state(&block([63.875, 64.0, 63.875, 64.0])).unwrap();
        // the 128 x 128 job's (16, 16), (112, 40), (40, 112) in clip space
        let t = [clip(-0.75, -0.75, 0.0, 1.0), clip(0.75, -0.375, 0.0, 1.0), clip(-0.375, 0.75, 0.0, 1.0)];
        let (v, used) = triangle(&s, t, F(1e-6), F(1e-6)).unwrap();
        assert_eq!((v[0].x, v[0].y, v[0].z, v[0].rhw), (15.875, 15.875, 0.5, 1.0));
        assert_eq!((v[1].x, v[1].y), (111.875, 39.875));
        assert!(!used, "the clamp replaced nothing");
    }

    #[test]
    fn a_triangle_beyond_z_plus_or_minus_w_wholly_or_in_part_is_refused_and_one_on_the_plane_is_not() {
        let s = state(&block([64.0; 4])).unwrap();
        let at = |z: [f32; 3]| {
            [clip(-0.5, -0.5, z[0], 1.0), clip(0.5, -0.5, z[1], 1.0), clip(0.0, 0.5, z[2], 1.0)]
        };
        // E287 measured pixels only: no dump says what the TA writes for a removed triangle
        refused(triangle(&s, at([1.01; 3]), 0, 0), "Q230");
        refused(triangle(&s, at([-1.01; 3]), 0, 0), "Q230");
        // z = -w and z = w are inside (the comparison is strict)
        assert!(triangle(&s, at([1.0, -1.0, 0.0]), 0, 0).is_ok());
        assert!(triangle(&s, at([1.0; 3]), 0, 0).is_ok());
        assert!(triangle(&s, at([-1.0; 3]), 0, 0).is_ok());
        // z reaches the plane at one vertex only: the clipper cuts the triangle (E287): not modelled
        refused(triangle(&s, at([0.0, 0.0, 1.01]), 0, 0), "Q230");
        refused(triangle(&s, at([1.01, 1.01, -1.01]), 0, 0), "Q230");
        refused(triangle(&s, at([-1.01, 0.0, 0.0]), 0, 0), "Q230");
    }

    #[test]
    fn the_depth_is_the_viewport_offset_plus_scale_times_the_clip_z_with_its_sign() {
        // block(): z offset 0.5, scale 0.5
        let s = state(&block([64.0; 4])).unwrap();
        let t = [clip(-0.5, -0.5, 0.5, 1.0), clip(0.5, -0.5, -0.5, 1.0), clip(0.0, 0.5, 0.0, 1.0)];
        let (v, _) = triangle(&s, t, F(1e-6), F(1e-6)).unwrap();
        assert_eq!(v.map(|v| v.z), [0.75, 0.25, 0.5]);
    }

    #[test]
    fn a_1_over_w_equal_to_the_minimum_is_refused_and_either_side_is_not() {
        // E197's values were all clear of the boundary: whether the minimum itself is replaced is
        // not recorded
        let s = state(&block([64.0; 4])).unwrap();
        let t = [clip(-0.5, -0.5, 0.0, 1.0), clip(0.5, -0.5, 0.0, 1.0), clip(0.0, 0.5, 0.0, 1.0)];
        refused(triangle(&s, t, F(1.0), F(0.25)), "Q230");
        let (v, used) = triangle(&s, t, F(0.999), F(0.25)).unwrap();
        assert!(!used && v[0].rhw == 1.0);
        let (v, used) = triangle(&s, t, F(1.001), F(0.25)).unwrap();
        assert!(used && v[0].rhw == 0.25);
    }

    /// The triangle of E754's e3i jobs: x and y scaled by w, so the window x and y are the
    /// original (8, 8), (56, 20), (20, 56) of a 64 x 64 target.
    fn scaled(w: f32) -> [[u32; 4]; 3] {
        let n = |v: f32| v * w;
        [clip(n(-0.75), n(-0.75), 0.0, w), clip(n(0.75), n(-0.375), 0.0, w), clip(n(-0.375), n(0.75), 0.0, w)]
    }

    #[test]
    fn in_the_guard_band_the_stored_1_over_w_is_the_float32_reciprocal_truncated_e754() {
        let s = state(&block([32.0; 4])).unwrap();
        // E754 g-e3 [HW]: w = 3, 7, 0.003 and 3e-5, the stored word at all three vertices; the
        // rounded reciprocals (...ab, ...25, ...ab, ...56) are refuted
        for (w, word) in
            [(3.0f32, 0x3eaa_aaaau32), (7.0, 0x3e12_4924), (0.003, 0x43a6_aaaa), (3e-5, 0x4702_3555)]
        {
            let (v, used) = triangle(&s, scaled(w), 0, 0).unwrap();
            assert!(!used);
            for p in v {
                assert_eq!(p.rhw.to_bits(), word, "w = {w}");
            }
            // x and y equal the original triangle's (E754 in band)
            assert!((v[0].x - 8.0).abs() < 1e-3 && (v[1].y - 20.0).abs() < 1e-3, "w = {w}: {v:?}");
            assert_eq!(v[0].z, 0.5);
        }
        // w = 1 is the control (E651's object): the exact reciprocal
        assert_eq!(triangle(&s, scaled(1.0), 0, 0).unwrap().0[0].rhw, 1.0);
    }

    #[test]
    fn a_w_other_than_1_outside_what_e754_ran_is_refused() {
        let s = state(&block([32.0; 4])).unwrap();
        let w3 = |f: &dyn Fn(&mut [[u32; 4]; 3])| {
            let mut t = scaled(3.0);
            f(&mut t);
            t
        };
        // the w values run span 3e-5 to 7
        refused(triangle(&s, scaled(10.0), 0, 0), "Q230");
        refused(triangle(&s, scaled(1e-6), 0, 0), "Q230");
        refused(triangle(&s, scaled(-3.0), 0, 0), "Q230");
        // a vertex of another w (a perspective triangle): not run
        refused(triangle(&s, w3(&|t| t[1][3] = F(4.0)), 0, 0), "Q230");
        // depth at a w other than 1 was not scored; z = 0 only
        refused(triangle(&s, w3(&|t| t[0][2] = F(0.5)), 0, 0), "Q230");
        // a vertex outside the viewport after the divide: the guard band's limit was not run
        refused(triangle(&s, w3(&|t| t[2][0] = F(5.0)), 0, 0), "Q230");
        // the minimum 1/w replacing a w != 1 vertex: E754's clamp jobs shrank the triangle instead
        refused(triangle(&s, scaled(3.0), F(1.0), F(0.25)), "Q230");
        // 1/w equal to the minimum, as at w = 1
        refused(triangle(&s, scaled(4.0), F(0.25), F(0.25)), "Q230");
    }

    #[test]
    fn a_vertex_the_viewport_cannot_encode_is_refused() {
        let s = state(&block([64.0; 4])).unwrap();
        let far = [clip(-0.5, -0.5, 0.0, 1.0), clip(0.5, -0.5, 0.0, 1.0), clip(1e6, 0.5, 0.0, 1.0)];
        refused(triangle(&s, far, 0, 0), "Q230");
    }
}
