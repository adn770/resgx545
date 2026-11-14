// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! MTE: viewport, cull, clamp, 1/w, window coordinates, clip planes (12.2): only what records
//! state. The state block's words (E347: presence 0xdf43, 18 dwords), the viewport on the clip
//! position (E061, E193), the 1/w the TA stores and its minimum and replacement (E063, E197), the
//! clip at z = -w and z = w (E287), the structure of a triangle cut at one vertex (E782, E798).
//! The clipping datasets' census (E619) holds the same: a clip volume of z = -w to w, the w clamp
//! word and no x or y clipping rule. Everything else refuses: culling (MTECTL bits 1:0), the
//! output select other than the library's, perspective w, a triangle the clip removes, the 1/w
//! and depth of a cut one.

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q069", "Q039", "Q116", "Q162", "Q230", "Q296"];

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
    if w.len() == 20 && w[0] == 0xdfc3 {
        return Err(open(
            format!(
                "an MTE state block with the region clip (presence 0xdfc3, clip words {:#x}, {:#x}): its pixels are `region_clip`'s (E1060: whole 32 x 16 tiles), but the TA's region lists under it were not dumped, so the block is not placed",
                w[6], w[7]
            ),
            "Q069",
        ));
    }
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

/// The region clip of presence bit 7: the two words after the pixel programs (E347), word 0 the
/// enable in bit 31 and the first and last 32-pixel tile columns in bits 30:16 and 15:0, word 1 the
/// first and last 16-pixel tile rows in 31:16 and 15:0 (E348, from the closed driver's captures).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RegionClip {
    pub enable: bool,
    pub cols: (u32, u32),
    pub rows: (u32, u32),
}

pub fn region_clip(c0: u32, c1: u32) -> RegionClip {
    RegionClip {
        enable: c0 >> 31 != 0,
        cols: ((c0 >> 16) & 0x7fff, c0 & 0xffff),
        rows: (c1 >> 16, c1 & 0xffff),
    }
}

impl RegionClip {
    /// Whether the clip keeps pixel (x, y) of an object (E1060, 13 held-out rows at 64 x 64 to
    /// 256 x 256 and 100 x 60, every pixel): whole tiles of 32 x 16, first <= tile <= last in both,
    /// the rows counted from memory row 0 (GL's bottom under E348's positive y scale); with bit 31
    /// clear the object is not clipped.
    pub fn keeps(&self, x: u32, y: u32) -> bool {
        let (tx, ty) = (x / 32, y / 16);
        !self.enable || (self.cols.0 <= tx && tx <= self.cols.1 && self.rows.0 <= ty && ty <= self.rows.1)
    }
}

/// An object's pixels under the clip, row by row: a covered pixel in a tile the clip drops is not
/// drawn and the background object writes it, as it writes every pixel no object covers (E1060:
/// no pixel left at the target's fill).
pub fn clipped(w: u32, h: u32, covered: &[bool], clip: RegionClip) -> Vec<bool> {
    (0..h)
        .flat_map(|y| (0..w).map(move |x| (x, y)))
        .map(|(x, y)| covered[(y * w + x) as usize] && clip.keeps(x, y))
        .collect()
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

/// A kept vertex's 1/w word the rules do not give (split from Q230): RZ or RZ + 1, and no frozen
/// model of the word fits every read one (E851: 225 models over E842's words, none 19 of 19).
fn refuse296(why: impl AsRef<str>) -> Outcome {
    Outcome::unsupported(why.as_ref(), &["Q296"])
}

/// The float32 reciprocal of `w` rounded toward zero (RZ32): what E754's e3i jobs measured stored
/// as 1/w inside the guard band, 4 of 4 (round-to-nearest refuted).
fn rhw_rz32(w: f32) -> f32 {
    let exact = 1.0f64 / f64::from(w);
    let r = exact as f32;
    if f64::from(r).abs() > exact.abs() { f32::from_bits(r.to_bits() - 1) } else { r }
}

/// The stored 1/w less RZ of 1/w (0 or 1) by the 23-bit mantissa of w, for every mantissa whose
/// word was read at a kept vertex (196 words: E754, E782, E783, E795, E796, E798, E842 and E859;
/// `fold/posthoc_r5.txt` of render/closing-r5-pixel lists them), and the 123 new mantissas of
/// g6-rw's windows and boundary rows whose exact 1/w lies half an ulp or more above RZ (E879;
/// `fold/posthoc_r6.txt` of render/closing-r6-pixel lists them). H-MANT, "the delta is a function
/// of the mantissa of w alone", held on 42 of 42 held-out words at other exponents (E859) and 72
/// of 72 at six more (E879), and no mantissa read at two exponents shows both. Below half an ulp
/// the rule `rhw_frac_below_half` gives RZ (H-FRAC); above it which mantissas store RZ + 1 has no
/// rule, so a mantissa not listed refuses (Q296).
const RHW_MANTISSA: [(u32, u8); 253] = [
    (0x00_0000, 0),
    (0x00_0001, 0),
    (0x00_0003, 0),
    (0x02_0000, 1),
    (0x02_2921, 0),
    (0x04_0000, 0),
    (0x05_0000, 0),
    (0x06_0000, 0),
    (0x07_0000, 0),
    (0x08_0000, 0),
    (0x08_e700, 1),
    (0x09_0000, 0),
    (0x09_05fe, 0),
    (0x09_8b0e, 0),
    (0x0a_0000, 0),
    (0x0a_2d48, 0),
    (0x0a_336c, 0),
    (0x0a_b3cb, 0),
    (0x0b_0000, 0),
    (0x0c_0000, 1),
    (0x0c_cccd, 0),
    (0x0d_0000, 0),
    (0x0e_0000, 0),
    (0x0f_0000, 0),
    (0x0f_0c30, 0),
    (0x0f_4438, 0),
    (0x0f_d7d1, 1),
    (0x0f_d9d1, 1),
    (0x0f_dcd1, 1),
    (0x0f_dfd1, 1),
    (0x0f_e0d1, 1),
    (0x0f_e4d1, 1),
    (0x0f_e5d1, 1),
    (0x0f_e9d1, 0),
    (0x0f_ecd1, 0),
    (0x0f_edd1, 0),
    (0x0f_eed1, 1),
    (0x0f_efd1, 1),
    (0x0f_f0d1, 1),
    (0x0f_f1d1, 1),
    (0x0f_f4d1, 0),
    (0x0f_f5d1, 1),
    (0x0f_f6d1, 1),
    (0x0f_f8d1, 1),
    (0x0f_f9d1, 1),
    (0x0f_fed1, 1),
    (0x10_0000, 1),
    (0x10_00d1, 0),
    (0x12_0000, 0),
    (0x12_1814, 0),
    (0x12_9355, 0),
    (0x14_0000, 0),
    (0x14_80a2, 1),
    (0x15_80a2, 1),
    (0x15_8f4d, 1),
    (0x16_0000, 0),
    (0x16_80a2, 1),
    (0x18_0000, 0),
    (0x18_0235, 0),
    (0x18_80a2, 1),
    (0x19_999a, 0),
    (0x1a_0000, 0),
    (0x1b_80a2, 0),
    (0x1c_0000, 0),
    (0x1c_80a2, 0),
    (0x1d_0000, 0),
    (0x1d_80a2, 1),
    (0x1e_0000, 0),
    (0x1e_1de4, 1),
    (0x1f_0000, 0),
    (0x1f_1de4, 0),
    (0x1f_80a2, 1),
    (0x20_0000, 0),
    (0x21_0000, 0),
    (0x22_0000, 0),
    (0x22_1de4, 0),
    (0x22_524d, 0),
    (0x22_a0e9, 0),
    (0x23_0000, 0),
    (0x23_1de4, 1),
    (0x24_0000, 0),
    (0x24_1de4, 0),
    (0x24_80a2, 1),
    (0x25_0000, 0),
    (0x25_1de4, 1),
    (0x26_0000, 0),
    (0x26_1de4, 0),
    (0x26_6666, 0),
    (0x27_0000, 0),
    (0x27_80a2, 1),
    (0x28_0000, 0),
    (0x28_1de4, 1),
    (0x28_2e6c, 0),
    (0x28_3d12, 0),
    (0x28_6904, 0),
    (0x29_1de4, 1),
    (0x29_b969, 1),
    (0x2a_0000, 1),
    (0x2a_1de4, 0),
    (0x2b_1de4, 1),
    (0x2c_0000, 0),
    (0x2e_0000, 0),
    (0x2f_80a2, 1),
    (0x30_0000, 0),
    (0x30_80a2, 1),
    (0x31_1de4, 0),
    (0x31_80a2, 1),
    (0x32_0000, 0),
    (0x33_1de4, 1),
    (0x33_3333, 1),
    (0x34_0000, 1),
    (0x34_1de4, 1),
    (0x35_0000, 0),
    (0x35_1de4, 1),
    (0x35_80a2, 1),
    (0x36_0000, 0),
    (0x36_1de4, 0),
    (0x37_0000, 0),
    (0x37_1de4, 0),
    (0x38_0000, 0),
    (0x39_0000, 1),
    (0x39_7b97, 0),
    (0x39_80a2, 1),
    (0x3a_0000, 0),
    (0x3a_1de4, 1),
    (0x3b_0000, 0),
    (0x3b_1de4, 1),
    (0x3b_2b3a, 0),
    (0x3b_992f, 0),
    (0x3c_0000, 0),
    (0x3d_0000, 0),
    (0x3d_8656, 1),
    (0x3d_8856, 1),
    (0x3d_8a56, 1),
    (0x3d_8c56, 1),
    (0x3d_8e56, 1),
    (0x3d_9056, 1),
    (0x3d_9256, 1),
    (0x3d_9856, 0),
    (0x3d_9a56, 1),
    (0x3d_9d56, 1),
    (0x3d_9e56, 0),
    (0x3d_a056, 1),
    (0x3d_a156, 1),
    (0x3d_a456, 1),
    (0x3d_a556, 1),
    (0x3d_a856, 1),
    (0x3d_a956, 1),
    (0x3d_ad56, 1),
    (0x3d_ae56, 1),
    (0x3d_af56, 1),
    (0x3e_0000, 0),
    (0x3f_0000, 1),
    (0x3f_1de4, 1),
    (0x40_0000, 0),
    (0x41_1de4, 1),
    (0x42_0000, 0),
    (0x42_d7f6, 1),
    (0x42_d7f7, 1),
    (0x42_d7f8, 1),
    (0x42_d7fd, 1),
    (0x42_d7fe, 1),
    (0x42_d7ff, 1),
    (0x42_d804, 0),
    (0x42_d80b, 0),
    (0x42_d80c, 0),
    (0x42_d80d, 1),
    (0x42_d80e, 1),
    (0x42_d812, 0),
    (0x42_d813, 0),
    (0x42_d814, 1),
    (0x42_d815, 1),
    (0x44_0000, 0),
    (0x44_9ba6, 0),
    (0x46_0000, 0),
    (0x46_1de4, 1),
    (0x46_73ad, 1),
    (0x48_0000, 0),
    (0x48_26b3, 0),
    (0x4a_0000, 0),
    (0x4c_0000, 1),
    (0x4d_0000, 1),
    (0x4e_0000, 1),
    (0x4e_cfc1, 1),
    (0x4f_0000, 0),
    (0x50_0000, 0),
    (0x51_0000, 0),
    (0x52_0000, 0),
    (0x53_0000, 0),
    (0x54_0000, 0),
    (0x55_0000, 0),
    (0x56_0000, 0),
    (0x57_0000, 0),
    (0x58_0000, 1),
    (0x5a_0000, 0),
    (0x5c_0000, 0),
    (0x5e_0000, 0),
    (0x5e_5ca1, 0),
    (0x60_0000, 0),
    (0x60_4061, 0),
    (0x60_d10e, 1),
    (0x61_7069, 0),
    (0x62_0000, 0),
    (0x62_430c, 0),
    (0x62_caeb, 1),
    (0x63_99d4, 0),
    (0x64_0000, 1),
    (0x65_0000, 0),
    (0x66_0000, 0),
    (0x67_0000, 0),
    (0x68_0000, 0),
    (0x69_0000, 0),
    (0x6a_0000, 0),
    (0x6b_0000, 0),
    (0x6c_0000, 1),
    (0x6d_0000, 0),
    (0x6e_0000, 0),
    (0x6f_0000, 0),
    (0x70_0000, 0),
    (0x71_3881, 0),
    (0x72_0000, 0),
    (0x73_5d03, 0),
    (0x74_0000, 0),
    (0x74_6675, 1),
    (0x74_76a8, 0),
    (0x74_8b32, 0),
    (0x74_8b33, 1),
    (0x74_8b35, 1),
    (0x74_8b37, 1),
    (0x74_8b39, 0),
    (0x74_8b3b, 0),
    (0x74_8b3e, 1),
    (0x74_8b40, 1),
    (0x74_8b44, 0),
    (0x74_8b46, 0),
    (0x74_8b49, 1),
    (0x74_8b4b, 1),
    (0x74_8b4d, 1),
    (0x74_8b4f, 0),
    (0x74_8b51, 0),
    (0x74_8b52, 1),
    (0x74_8b54, 1),
    (0x74_8b5a, 0),
    (0x75_776e, 1),
    (0x76_0000, 0),
    (0x78_0000, 0),
    (0x7a_0000, 0),
    (0x7a_b3ec, 1),
    (0x7a_d92c, 1),
    (0x7b_a882, 0),
    (0x7c_0000, 0),
    (0x7e_0000, 0),
    (0x7f_fffe, 0),
];

/// The exponents of w at which words were read and H-MANT held out: E859's words at -2, -1, 0, 1,
/// 2 and 4 (E842's at 0 to 2; 3 lies between them), E879's at -12, -6, -3, 5, 8 and 12. Another
/// exponent refuses [the delta there is not read], except the two w read themselves below.
const RHW_EXP: [i32; 13] = [-12, -6, -3, -2, -1, 0, 1, 2, 3, 4, 5, 8, 12];

/// The w at exponents not in `RHW_EXP` whose word was read: E754's 3e-5 and 0.003, RZ.
const RHW_READ_LOW: [f32; 2] = [3e-5, 0.003];

/// H-FRAC: whether the exact 1/w of the 24-bit mantissa `m` (with its leading one) lies less
/// than half an ulp above RZ, the fraction of 2^47 / m below 0.5. No such mantissa stored RZ + 1:
/// 64 of 64 read before the rule was frozen (E872, SEMI) and 117 of 117 new ones held out (E879).
fn rhw_frac_below_half(m: u32) -> bool {
    let m = u64::from(m);
    2 * ((1u64 << 47) % m) < m
}

/// The stored 1/w less RZ of 1/w: by the mantissa table at an exponent of `RHW_EXP`, 0 for a
/// mantissa below half an ulp (H-FRAC) [infer from H-MANT for a pair of mantissa and exponent not
/// read], 0 at the w of `RHW_READ_LOW`, `None` elsewhere.
fn rhw_delta(w: f32) -> Option<u32> {
    if RHW_READ_LOW.contains(&w) {
        return Some(0);
    }
    let b = w.to_bits();
    let e = ((b >> 23) & 0xff) as i32 - 127;
    if w <= 0.0 || !RHW_EXP.contains(&e) {
        return None;
    }
    let m = b & 0x7f_ffff;
    if let Ok(i) = RHW_MANTISSA.binary_search_by_key(&m, |&(t, _)| t) {
        return Some(u32::from(RHW_MANTISSA[i].1));
    }
    rhw_frac_below_half(m | 0x80_0000).then_some(0)
}

/// The w values whose stored 1/w the model gives, at z = 0 for the depth: every vertex's w
/// known to `rhw_delta`, one w at all three vertices or a w of its own at each (E754 and E782
/// ran both shapes), every vertex inside the viewport after its divide. Anything else with a w
/// other than 1 stays refused: a w whose mantissa was not read or outside the exponents run
/// (Q296), depth at w other than 1 (no formula: E783, E795, E796), the guard band's limit (Q230).
fn band_w(c: &[[f32; 4]; 3]) -> Result<(), Outcome> {
    if c.iter().any(|v| v[3] <= 0.0 || v[3].is_nan()) {
        return Err(refuse230("a w at or below 0: no word of such a vertex was read"));
    }
    if c.iter().any(|v| rhw_delta(v[3]).is_none()) {
        return Err(refuse296(
            "a w whose 1/w word is not known: RZ of 1/w or one ulp above by the mantissa of w (H-MANT, E859, E879), a mantissa not read whose exact 1/w lies half an ulp or more above RZ (H-FRAC gives RZ below it, E872, E879), or an exponent no word was read at",
        ));
    }
    if c.iter().any(|v| v[2] != 0.0) {
        return Err(refuse230(
            "the depth at a w other than 1 has no formula (E783, E795, E796: every frozen rule refuted, words recorded)",
        ));
    }
    if c.iter().any(|v| (v[0] / v[3]).abs() > 1.0 || (v[1] / v[3]).abs() > 1.0) {
        return Err(refuse230(
            "a vertex outside the viewport at a w other than 1: E754 ran inside it, the guard band's limit was not run",
        ));
    }
    Ok(())
}

/// The window coordinates the object's packed block can hold: 24 bits of (v + 4096) * 256.
const RANGE: std::ops::Range<f32> = -4096.0..12288.0;

/// The three vertices' clip positions through the viewport. Whole triangles with w = 1 inside
/// z = -w and z = w, and the w other than 1 of `band_w` (z = 0): what the TA writes for a
/// triangle the clip removes is not modelled, a cut one has its structure only (`cut_triangle`),
/// and the depth at w other than 1 has no formula (E783, E795, Q230). The depth is the viewport's
/// offset + scale x z rounded once (E797). `rhw_min` and `rhw_clamp` are the command's float
/// words. Returns the vertices and whether the 1/w replacement was used.
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
        // w = 1 is in the table (RZ, exact)
        let r = f32::from_bits(rhw_rz32(v[3]).to_bits() + rhw_delta(v[3]).unwrap_or(0));
        if r == min {
            return Err(refuse230(
                "a 1/w equal to the minimum: E197's values were all clear of the boundary",
            ));
        }
        let (rhw, u) = stored_rhw(r, min, clamp);
        // E736 (clamp one ulp above w = 1e-3: the clamp's reciprocal, a 0.96-pixel square) and
        // E781 (six clamps: the word within 1 ulp of 1/clamp, RZ in 2 and RN in 3, the position
        // divided by the clamp): no rounding rule for the word, so refused
        if u && v[3] != 1.0 {
            return Err(refuse230(
                "a 1/w replaced by the clamp at a w other than 1: E754's clamp jobs shrank the triangle by w / clamp and stored the clamp's reciprocal, no rule fits all",
            ));
        }
        used |= u;
        *o = Vertex {
            x: st.vp[0] + st.vp[1] * (v[0] / v[3]),
            y: st.vp[2] + st.vp[3] * (v[1] / v[3]),
            z: v[2].mul_add(st.vp[5], st.vp[4]),
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

/// The span of w that the cut objects ran with (E782: 0.875 to 1.625; E798: up to 1.6875;
/// E777 at w = 1).
const CUT_W: std::ops::RangeInclusive<f32> = 0.875..=1.6875;

/// What the TA stored for a triangle the clip cut, as far as the cuts that ran say: the window
/// position of each vertex in stored order, whether the clip made it, and the prim words.
#[derive(Debug, Clone, PartialEq)]
pub struct CutObject {
    pub xy: Vec<(f32, f32)>,
    pub made: Vec<bool>,
    pub prims: Vec<[u32; 3]>,
}

/// The strip order of a convex polygon p0..p(n-1) (E777): p1, p2, p0, p3, p(n-1), p4, ...
fn zigzag(n: usize) -> Vec<usize> {
    let mut order = vec![1, 2, 0];
    let (mut lo, mut hi) = (3, n - 1);
    let mut turn = 0;
    while lo <= hi && order.len() < n {
        if turn % 2 == 0 {
            order.push(lo);
            lo += 1;
        } else {
            order.push(hi);
            hi -= 1;
        }
        turn += 1;
    }
    order.truncate(n);
    order
}

/// A triangle with exactly one vertex beyond exactly one of the planes z = w and z = -w, every w
/// in `CUT_W`: the Sutherland-Hodgman polygon in (x, y, z, w) of 4 vertices (the crossing, then
/// the end vertex when it is inside, edge by edge from vertex 0), stored in strip zigzag order,
/// window position offset + scale x / w with the vertex's own w (made ones included), prim words
/// index | 16 for a boundary edge (E777 at w = 1, E782 and E798 held out at w other than 1). The
/// 1/w and depth of the vertices are not given: the made 1/w has no rule (E782, E798) and the
/// depth at w other than 1 none (E783, E795); polygons of 3 or of 5 or more vertices and two
/// planes (E777 at w = 1 only) and other w refuse (Q230).
pub fn cut_triangle(st: &State, clip: [[u32; 4]; 3]) -> Result<CutObject, Outcome> {
    let c = clip.map(|v| v.map(f32::from_bits));
    if c.iter().any(|v| v.iter().any(|x| !x.is_finite())) {
        return Err(refuse230("a non-finite clip coordinate"));
    }
    if !c.iter().all(|v| CUT_W.contains(&v[3])) {
        return Err(refuse230(
            "a cut with a w outside 0.875 to 1.6875: the cut objects of E777, E782 and E798 ran inside it",
        ));
    }
    let above = c.iter().filter(|v| v[2] > v[3]).count();
    let below = c.iter().filter(|v| v[2] < -v[3]).count();
    let sign = match (above, below) {
        (1, 0) => 1.0,
        (0, 1) => -1.0,
        (0, 0) => return Err(refuse230("no vertex beyond z = w or z = -w: not a cut (see triangle)")),
        _ => {
            return Err(refuse230(
                "a cut leaving 3, or 5 or more, vertices or crossing both planes: not built here (E777 at w = 1; no such cut at w other than 1)",
            ));
        }
    };
    let p = c.map(|v| v.map(f64::from));
    // inside when d >= 0: w - z for the plane z = w, w + z for z = -w
    let d = |v: &[f64; 4]| v[3] - sign * v[2];
    let mut poly: Vec<([f64; 4], bool)> = Vec::new();
    for i in 0..3 {
        let (a, b) = (&p[i], &p[(i + 1) % 3]);
        let (da, db) = (d(a), d(b));
        if (da >= 0.0) != (db >= 0.0) {
            let t = da / (da - db);
            poly.push((std::array::from_fn(|k| a[k] + t * (b[k] - a[k])), true));
        }
        if db >= 0.0 {
            poly.push((*b, false));
        }
    }
    let n = poly.len();
    let zz = zigzag(n);
    let mut pos = vec![0; n];
    for (si, &pi) in zz.iter().enumerate() {
        pos[pi] = si;
    }
    let boundary = |a: usize, b: usize| {
        (0..n).any(|i| {
            let (x, y) = (pos[i], pos[(i + 1) % n]);
            (x, y) == (a, b) || (y, x) == (a, b)
        })
    };
    let prims = (0..n - 2)
        .map(|i| {
            let t = if i % 2 == 0 { [i, i + 1, i + 2] } else { [i + 1, i, i + 2] };
            std::array::from_fn(|k| t[k] as u32 | if boundary(t[k], t[(k + 1) % 3]) { 16 } else { 0 })
        })
        .collect();
    let mut xy = Vec::with_capacity(n);
    let mut made = Vec::with_capacity(n);
    for &i in &zz {
        let (v, m) = poly[i];
        let x = (f64::from(st.vp[0]) + f64::from(st.vp[1]) * v[0] / v[3]) as f32;
        let y = (f64::from(st.vp[2]) + f64::from(st.vp[3]) * v[1] / v[3]) as f32;
        if !RANGE.contains(&x) || !RANGE.contains(&y) {
            return Err(refuse230(format!("window coordinate ({x}, {y}) outside the packed block's range")));
        }
        xy.push((x, y));
        made.push(m);
    }
    Ok(CutObject { xy, made, prims })
}

#[cfg(test)]
mod tests {
    use super::*;

    const F: fn(f32) -> u32 = f32::to_bits;

    #[test]
    fn the_region_clip_words_read_as_e348_lays_them_out() {
        // E348's viewport 40,20,16,30 triangle clip: enable, column 1 to 1, rows 1 to 3
        assert_eq!(
            region_clip(0x8001_0001, 0x0001_0003),
            RegionClip { enable: true, cols: (1, 1), rows: (1, 3) }
        );
        // E348's clear clip of a 64 x 64 target, E1060's gate row
        assert_eq!(region_clip(0x8000_0001, 3), RegionClip { enable: true, cols: (0, 1), rows: (0, 3) });
        assert!(!region_clip(0x0001_0002, 0x0002_0004).enable);
    }

    #[test]
    fn the_region_clip_keeps_whole_32_by_16_tiles_inclusive_rows_from_y_0_e1060() {
        let c = region_clip(0x8001_0001, 0x0001_0003);
        // column 1 is x 32..63, rows 1 to 3 are y 16..63 (memory rows from 0, not from the bottom)
        assert!(c.keeps(32, 16) && c.keeps(63, 63) && c.keeps(40, 30));
        assert!(!c.keeps(31, 16) && !c.keeps(32, 15) && !c.keeps(64, 16) && !c.keeps(32, 64));
        // the last bound is inclusive: rows 1 to 2 keep y 47 (row 2), not 48 (row 3)
        let c = region_clip(0x8001_0002, 0x0001_0002);
        assert!(c.keeps(95, 47) && !c.keeps(95, 48) && !c.keeps(96, 47));
        // bit 31 clear: no clip at all (E1060's e128-off)
        let off = region_clip(0x0001_0002, 0x0002_0004);
        assert!(off.keeps(0, 0) && off.keeps(127, 127));
    }

    #[test]
    fn a_clipped_object_leaves_the_background_outside_the_kept_tiles_e1060() {
        // a full-target object on 64 x 64 under column 0, rows 2 to 3: x < 32, y >= 32
        let img = clipped(64, 64, &vec![true; 64 * 64], region_clip(0x8000_0000, 0x0002_0003));
        assert_eq!(img.iter().filter(|&&k| k).count(), 1024);
        assert!(img[32 * 64] && !img[31 * 64] && !img[32 * 64 + 32]);
    }

    #[test]
    fn a_block_with_the_region_clip_names_e1060_and_is_not_placed() {
        let mut b = block([64.0, 64.0, 64.0, 64.0]);
        b[0] = 0xdfc3;
        b.splice(6..6, [0x8000_0003, 7]);
        let Err(Outcome::Unsupported { why, .. }) = state(&b) else { panic!("a clip block is placed") };
        assert!(why.contains("E1060"), "{why}");
    }

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
    fn the_1_over_w_is_rz_plus_the_delta_of_the_mantissa_of_w_e859() {
        let s = state(&block([32.0; 4])).unwrap();
        let rhw = |w: f32| triangle(&s, scaled(w), 0, 0).map(|(v, _)| v.map(|p| p.rhw.to_bits()));
        // E859 [HW, held out]: words of g5-rw's dense table, RZ + 1 at d-15's 5.30388 and d-18's
        // 1.55041, RZ at d-14's 2.53125; the same w at all three vertices
        assert_eq!(rhw(f32::from_bits(0x40a9_b969)).unwrap(), [0x3e41_10ec; 3]);
        assert_eq!(rhw(f32::from_bits(0x3fc6_73ad)).unwrap(), [0x3f25_1e3e; 3]);
        assert_eq!(rhw(f32::from_bits(0x4022_0000)).unwrap(), [0x3eca_4587; 3]);
        // H-MANT (E859, 42 of 42 held out): the delta follows the mantissa at another exponent of
        // w inside the exponents run (-2 to 4): 1.125 is RZ + 1 (E842), so are 2.25 and 0.5625;
        // 1.25 is RZ, so is 10 (2^3, no word of that mantissa read there)
        for (w, d) in [(2.25f32, 1u32), (0.5625, 1), (9.0, 1), (0.7, 1), (1.4, 1), (10.0, 0), (2.5, 0)] {
            assert_eq!(rhw(w).unwrap(), [rhw_rz32(w).to_bits() + d; 3], "w = {w}");
        }
        // a mantissa never read whose exact 1/w lies half an ulp or more above RZ (2.1: frac
        // 0.678), and exponents no word was read at (2^10, 2^-20); the two w read below (E754)
        for w in [2.1f32, 1.25 * 1024.0, 1.25 / 1_048_576.0] {
            refused(triangle(&s, scaled(w), 0, 0), "Q296");
        }
        assert_eq!(rhw(3e-5).unwrap(), [0x4702_3555; 3]);
        assert_eq!(rhw(0.003).unwrap(), [0x43a6_aaaa; 3]);
    }

    #[test]
    fn the_1_over_w_is_rz_below_half_an_ulp_and_by_the_r6_table_above_e879() {
        let s = state(&block([32.0; 4])).unwrap();
        let rhw = |w: f32| triangle(&s, scaled(w), 0, 0).map(|(v, _)| v.map(|p| p.rhw.to_bits()));
        // E879 [HW, held out]: g6-rw's new mantissas with frac >= 0.5 are a table: l-16a-00's
        // third w stores RZ + 1, b-04's first RZ
        assert_eq!(rhw(f32::from_bits(0x3f95_80a2)).unwrap(), [0x3f5b_2e2a; 3]);
        assert_eq!(rhw(f32::from_bits(0x3f89_8b0e)).unwrap(), [0x3f6e_3ce7; 3]);
        // H-FRAC (E872 SEMI, E879 held out 117 of 117): a mantissa whose exact 1/w lies less
        // than half an ulp above RZ stores RZ, read or not (1.7: frac 0.311; 1.3: 0.243)
        for w in [1.7f32, 1.3] {
            assert_eq!(rhw(w).unwrap(), [rhw_rz32(w).to_bits(); 3], "w = {w}");
        }
        // H-MANT held out at exponents -12, -6, -3, 5, 8 and 12 (E879, 72 of 72): R4's rw-10 at
        // 2^-12 and 2^5 (RZ + 1, RZ + 1, RZ at the three vertices)
        for (w, word) in [
            (0x39cc_0000u32, 0x4520_a0a1u32),
            (0x39d8_0000, 0x4517_b426),
            (0x39cf_0000, 0x451e_4cad),
            (0x424c_0000, 0x3ca0_a0a1),
            (0x4258_0000, 0x3c97_b426),
            (0x424f_0000, 0x3c9e_4cad),
        ] {
            assert_eq!(rhw(f32::from_bits(w)).unwrap(), [word; 3], "w = {w:#x}");
        }
    }

    #[test]
    fn the_1_over_w_is_rz_only_at_the_w_that_were_run_and_one_ulp_above_at_9_and_0_7_e795() {
        let s = state(&block([32.0; 4])).unwrap();
        // E795, E796 [HW, read after the run]: one w at all three vertices, RZ of 1/w at w = 5,
        // 11 and 0.3; one ulp above it at w = 9 (0x3de38e39) and 0.7 (0x3fb6db6e), now given by
        // the mantissa table (E859)
        for (w, word) in [
            (5.0f32, 0x3e4c_ccccu32),
            (11.0, 0x3dba_2e8b),
            (0.3, 0x4055_5554),
            (9.0, 0x3de3_8e39),
            (0.7, 0x3fb6_db6e),
        ] {
            let (v, _) = triangle(&s, scaled(w), 0, 0).unwrap();
            assert_eq!(v.map(|p| p.rhw.to_bits()), [word; 3], "w = {w}");
        }
        // E798 [HW, read after the run]: a kept vertex at w = 1.40625, 1.59375 or 1.6875 stored
        // one ulp above RZ; E782's own triangle (0.875, 1.625, 1.0625) stays as measured
        let t =
            [clip(-0.75, -0.75, 0.0, 0.875), clip(0.75, -0.375, 0.0, 1.625), clip(-0.375, 0.75, 0.0, 1.0625)];
        assert!(triangle(&s, t, 0, 0).is_ok());
        for (w, d) in [(1.40625f32, 1u32), (1.59375, 1), (1.6875, 1), (1.25, 0)] {
            let mut u = t;
            u[2] = clip(-0.375 * w, 0.75 * w, 0.0, w);
            let (v, _) = triangle(&s, u, 0, 0).unwrap();
            assert_eq!(v[2].rhw.to_bits(), rhw_rz32(w).to_bits() + d, "w = {w}");
        }
    }

    #[test]
    fn a_w_other_than_1_outside_what_e754_ran_is_refused() {
        let s = state(&block([32.0; 4])).unwrap();
        let w3 = |f: &dyn Fn(&mut [[u32; 4]; 3])| {
            let mut t = scaled(3.0);
            f(&mut t);
            t
        };
        // a w whose mantissa was not read and lies half an ulp or more above RZ (2.1), or at an
        // exponent no word was read at (1280 = 1.25 x 2^10)
        refused(triangle(&s, scaled(2.1), 0, 0), "Q296");
        refused(triangle(&s, scaled(1280.0), 0, 0), "Q296");
        refused(triangle(&s, scaled(1e-6), 0, 0), "Q296");
        refused(triangle(&s, scaled(-3.0), 0, 0), "Q230");
        // a vertex of another w (a perspective triangle) whose mantissa was not read
        refused(triangle(&s, w3(&|t| t[1][3] = F(4.1)), 0, 0), "Q296");
        // depth at a w other than 1 has no formula (E783); z = 0 only
        refused(triangle(&s, w3(&|t| t[0][2] = F(0.5)), 0, 0), "Q230");
        // a vertex outside the viewport after the divide: the guard band's limit was not run
        refused(triangle(&s, w3(&|t| t[2][0] = F(5.0)), 0, 0), "Q230");
        // the minimum 1/w replacing a w != 1 vertex: E754's clamp jobs shrank the triangle instead
        refused(triangle(&s, scaled(3.0), F(1.0), F(0.25)), "Q230");
        // 1/w equal to the minimum, as at w = 1
        refused(triangle(&s, scaled(4.0), F(0.25), F(0.25)), "Q230");
    }

    #[test]
    fn a_perspective_triangle_divides_each_vertex_by_its_own_w_and_stores_its_rz_reciprocal_e782() {
        let s = state(&block([32.0; 4])).unwrap();
        // E782's t3-nocut [HW, held out]: z = 0, w = 0.5 x + 1.25 at x = -0.75, 0.75 and -0.375
        let t =
            [clip(-0.75, -0.75, 0.0, 0.875), clip(0.75, -0.375, 0.0, 1.625), clip(-0.375, 0.75, 0.0, 1.0625)];
        let (v, used) = triangle(&s, t, 0, 0).unwrap();
        assert!(!used);
        // the stored 1/w words, exactly RZ of 1/w at the three vertices
        assert_eq!(v.map(|p| p.rhw.to_bits()), [0x3f92_4924, 0x3f1d_89d8, 0x3f70_f0f0]);
        // the window position 32 + 32 x / w (the object packs it to 1/256: 4.5703, 46.7695,
        // 24.6172, 20.7070 and 54.5898 in the dump), the depth 0.5 at z = 0
        let want = [(4.5714, 4.5714), (46.7692, 24.6154), (20.7059, 54.5882)];
        for (p, (x, y)) in v.iter().zip(want) {
            assert!((p.x - x).abs() < 1e-3 && (p.y - y).abs() < 1e-3, "{p:?}");
            assert_eq!(p.z, 0.5);
        }
        // what was not run stays refused: a w whose mantissa was not read at one vertex, a vertex
        // outside the viewport after its own divide, and a depth other than 0 (E783)
        let with = |f: &dyn Fn(&mut [[u32; 4]; 3])| {
            let mut u = t;
            f(&mut u);
            u
        };
        refused(triangle(&s, with(&|u| u[0][3] = F(0.5)), 0, 0), "Q230");
        refused(triangle(&s, with(&|u| u[2][3] = F(2.1)), 0, 0), "Q296");
        refused(triangle(&s, with(&|u| u[0][0] = F(1.9)), 0, 0), "Q230");
        refused(triangle(&s, with(&|u| u[1][2] = F(-0.5)), 0, 0), "Q230");
    }

    #[test]
    fn a_vertex_the_viewport_cannot_encode_is_refused() {
        let s = state(&block([64.0; 4])).unwrap();
        let far = [clip(-0.5, -0.5, 0.0, 1.0), clip(0.5, -0.5, 0.0, 1.0), clip(1e6, 0.5, 0.0, 1.0)];
        refused(triangle(&s, far, 0, 0), "Q230");
    }

    #[test]
    fn the_viewport_z_words_are_offset_then_scale_and_the_depth_is_rounded_once_at_w_1_e797() {
        // E797 [HW, held out] at w = 1: block word 10 is the offset and 11 the scale (the swap
        // refuted 9 of 9); 0.6 + 0.3 z at z = -0.830491483 was stored 0x3eb3a2f3, the single
        // rounding of the sum (the product rounded first gives 0x3eb3a2f2)
        let rows = [
            (0.25f32, 0.5f32, -0.3125f32, 0x3dc0_0000u32),
            (0.5, 0.25, -0.3125, 0x3ed8_0000),
            (0.6, 0.3, -0.830_491_5, 0x3eb3_a2f3),
        ];
        for (off, scale, z, word) in rows {
            let mut b = block([32.0; 4]);
            b[10] = F(off);
            b[11] = F(scale);
            let s = state(&b).unwrap();
            let t = [clip(-0.75, -0.75, z, 1.0), clip(0.75, -0.375, z, 1.0), clip(-0.375, 0.75, z, 1.0)];
            let (v, _) = triangle(&s, t, 0, 0).unwrap();
            assert_eq!(v.map(|p| p.z.to_bits()), [word; 3], "{off} {scale} {z}");
        }
    }

    /// The tool's triangle with z = a x + b and w = c x + d (x and y unscaled), as the vertex
    /// programs of E782 and E798 made it.
    fn zw(a: f32, b: f32, c: f32, d: f32) -> [[u32; 4]; 3] {
        [(-0.75, -0.75), (0.75, -0.375), (-0.375, 0.75)].map(|(x, y)| clip(x, y, a * x + b, c * x + d))
    }

    /// A cut job: the clip positions, the packed window x and y of each stored vertex in 1/256
    /// pixel, and which vertices the clip made.
    type CutCase = ([[u32; 4]; 3], [(u32, u32); 4], [bool; 4]);

    #[test]
    fn a_triangle_cut_by_one_plane_at_one_vertex_is_the_polygon_of_e782_and_e798() {
        let s = state(&block([32.0; 4])).unwrap();
        // E782 [HW, held out] (the +w plane) and E798 [HW, held out] (both planes): stored order,
        // the made vertices and the prim words (16, 1, 18), (2, 17, 19) in all six; the window
        // within one 1/256 step of the packed fields
        let p = [true, false, true, false];
        let m = [false, false, true, true];
        let cases: [CutCase; 6] = [
            (zw(2.0, 1.0, 0.5, 1.25), [(9216, 9472), (5301, 13975), (9216, 4992), (1170, 1170)], p),
            (zw(2.0, 1.0, -0.5, 1.25), [(8875, 10069), (6055, 12466), (8875, 4523), (4411, 4411)], p),
            (zw(2.0, 1.0, 0.25, 1.5), [(9681, 8657), (6007, 12561), (9681, 5632), (3511, 3511)], p),
            (zw(2.0, 1.0, -0.25, 1.5), [(9452, 9058), (6264, 12047), (9452, 5317), (4551, 4551)], p),
            (zw(2.0, -0.25, 0.5, 1.25), [(11973, 6302), (5301, 13975), (5071, 3023), (5071, 13263)], m),
            (zw(2.0, -0.25, -0.25, 1.5), [(12873, 5851), (6264, 12047), (4706, 4575), (4706, 5229)], m),
        ];
        for (i, (t, xy, made)) in cases.into_iter().enumerate() {
            let o = cut_triangle(&s, t).unwrap();
            assert_eq!(o.made, made, "case {i}");
            assert_eq!(o.prims, vec![[16, 1, 18], [2, 17, 19]], "case {i}");
            for (p, q) in o.xy.iter().zip(xy) {
                let (x, y) = (p.0 * 256.0, p.1 * 256.0);
                assert!(
                    (x - q.0 as f32).abs() <= 1.0 && (y - q.1 as f32).abs() <= 1.0,
                    "case {i}: {p:?} {q:?}"
                );
            }
        }
    }

    #[test]
    fn a_cut_nothing_measured_is_refused() {
        let s = state(&block([32.0; 4])).unwrap();
        // two vertices beyond the plane (a polygon of 3), both planes crossed, no cut
        refused(cut_triangle(&s, zw(-2.0, 1.2, 0.0, 1.0)), "Q230");
        refused(cut_triangle(&s, zw(3.0, 0.0, 0.0, 1.0)), "Q230");
        refused(cut_triangle(&s, zw(0.0, 0.0, 0.5, 1.25)), "Q230");
        // a w outside the span the cuts ran with (0.875 to 1.6875)
        refused(cut_triangle(&s, zw(2.0, 1.0, 0.5, 2.0)), "Q230");
        refused(cut_triangle(&s, zw(2.0, 1.0, 1.0, 1.0)), "Q230");
        let mut t = zw(2.0, 1.0, 0.5, 1.25);
        t[0][0] = F(f32::NAN);
        refused(cut_triangle(&s, t), "Q230");
    }
}
