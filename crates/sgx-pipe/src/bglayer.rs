// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! A render's one-layer background object (Q190, closed by E970 to E972): the 23 dwords of a
//! transfer copy's object (words 0-2 the PDS words, 3-8 the layer's (u, v) at the three vertices,
//! 9 = 0, 10 the format word, 11-14 = 0, 15-22 the vertices in the 80-bit encoding of
//! `xfer::vertices`), built by the kernel when the tag says one layer. What a background pixel
//! samples: the plane through the coordinates read vertex by vertex (TL, TR, BL: E971, 30 of 30
//! held out), anchored at the vertices words 15-22 give (E972, 20 of 20; the render box's
//! coverage does not follow them, E590 and E972), evaluated at the pixel centre, and the texture
//! unit's point sample of the copy's stride texture, which clamps outside [0, 1) (E974, 17453 of
//! 17453 pixels, post hoc; sgx-sim's stride rule). The same plane as a transfer copy's
//! (`xfer::uv`), here off the target's rectangle too.
//!
//! Refused (Q066, E973): word 1 other than one or four attribute rows (0 rows gives other
//! texels), words 9 and 13 other than 0, 1.0, 2.0, -1.0 or 0xffffffff, words 11, 12 and 14
//! other than 0, 1.0, 0.25, 0.5, 1.5 or -1.0 (E1006: every finite value run changes nothing;
//! 0xffffffff changes the picture: open), the format word outside the seven values E973 and
//! E069 ran without a change (0xffffffff gives texel (0, 0) everywhere: open), a coordinate that is
//! not finite, a triangle with no area (Q200, the iterators' arithmetic).

use crate::Outcome;
use crate::xfer::{lod_of, uv, vertices};
use sgx_sim::tex;

type R<T> = Result<T, Outcome>;

/// The words of the one-layer object.
pub const WORDS: usize = 23;
/// Word 10 values measured to change nothing (E069 on a copy; E973 on a render).
pub const FORMAT_SAME: [u32; 7] = [0, 0x202, 0x404, 0x101, 0xffff, 0x1_0000, 0x8000_0000];
const ONE: u32 = 0x3f80_0000;
/// Words 9 and 13 values measured to change nothing (E973: 0, 1.0, 0xffffffff; E1006: 2.0, -1.0).
pub const W9_13_SAME: [u32; 5] = [0, ONE, 0xffff_ffff, 0x4000_0000, 0xbf80_0000];
/// Words 11, 12 and 14 values measured to change nothing (E973: 0, 1.0; E1006: 0.25, 0.5, 1.5,
/// -1.0); 0xffffffff changes the picture (E973).
pub const W11_14_SAME: [u32; 6] = [0, ONE, 0x3e80_0000, 0x3f00_0000, 0x3fc0_0000, 0xbf80_0000];

fn open(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

/// The object is one the records model, or why not.
pub fn check(bg: &[u32]) -> R<()> {
    if bg.len() < WORDS {
        return Err(open("a one-layer background object has 23 dwords", &["Q066"]));
    }
    if bg[1] != 0x3_0001 && bg[1] != 0x3_0004 {
        return Err(open(format!("background word 1 is {:#x}: only one or four rows ran", bg[1]), &["Q066"]));
    }
    let any = |w: usize, ok: &[u32]| ok.contains(&bg[w]);
    if !any(9, &W9_13_SAME) || !any(13, &W9_13_SAME) {
        return Err(open("background words 9 or 13 at a value no record ran", &["Q066"]));
    }
    if [11, 12, 14].iter().any(|&w| !any(w, &W11_14_SAME)) {
        return Err(open(
            "background words 11, 12 or 14 at a value no record ran (E973, E1006; 0xffffffff changes the picture)",
            &["Q066"],
        ));
    }
    if !FORMAT_SAME.contains(&bg[10]) {
        return Err(open(
            format!("format word {:#x}: not one of the values that change nothing", bg[10]),
            &["Q066"],
        ));
    }
    if bg[3..9].iter().any(|&c| !f32::from_bits(c).is_finite()) {
        return Err(open("a layer coordinate is not finite", &["Q200"]));
    }
    if vertices(bg, 15).is_none() {
        return Err(open("the background object is too short", &["Q066"]));
    }
    Ok(())
}

/// The layer's iterated (u, v) at the centre of pixel (x, y).
pub fn coords(bg: &[u32], x: u32, y: u32) -> R<(f32, f32)> {
    check(bg)?;
    uv(bg, x, y)
}

/// The texel word background pixel (x, y) samples from the copy's texture `state` (T0-T3).
pub fn sample(bg: &[u32], state: [u32; 4], x: u32, y: u32, load: &mut tex::Load) -> R<u32> {
    let (u, v) = coords(bg, x, y)?;
    let s =
        tex::Sample { csc: None, state, u, v, one_d: false, srd: tex::Srd::None, pcf: None, lod: lod_of(bg) };
    let r = tex::sample(&s, load).map_err(|f| match f {
        tex::Fail::Open(w) => open(format!("texture sample: {w}"), &["Q300"]),
        tex::Fail::Load(e) => open(format!("texture read: {e:?}"), &["Q300"]),
    })?;
    r.first().copied().ok_or_else(|| open("an empty texture sample", &["Q300"]))
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The kernel's object for a 64 x 64 target (fork fafea977): the identity plane over the box.
    fn identity() -> Vec<u32> {
        let mut o = vec![0x0400_0004, 0x3_0001, 0x0c00_00f0, 0, 0, ONE, 0, 0, ONE, 0, 0x202, 0, 0, 0, 0];
        o.extend([0x0010_0000, 0x1000, 0, 0x1040_0010, 0, 0x0010_4000, 0x1000, 0]);
        o
    }

    /// The library's copy texture over a 64 x 64 RGBA8888 source at 0x3e800000
    /// (sgxfive_tex_words), and a source whose texel names its position.
    const STATE: [u32; 4] =
        [(63 & 7) << 9 | (63 >> 3) << 17, 0xcc00_0000 | 63 << 12 | 63, 0x3e80_0000, 0xa080_0000];

    fn texel(x: u32, y: u32) -> u32 {
        ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x
    }

    fn at(bg: &[u32], x: u32, y: u32) -> R<u32> {
        let mut load = |a: u32| {
            let i = (a - 0x3e80_0000) / 4;
            Ok(texel(i % 64, i / 64))
        };
        sample(bg, STATE, x, y, &mut load)
    }

    #[test]
    fn the_identity_object_samples_each_pixels_own_texel() {
        // E970: 3034 of 3034 background pixels of the 64 x 64 render
        let o = identity();
        for (x, y) in [(0, 0), (63, 0), (5, 40), (63, 63)] {
            assert_eq!(at(&o, x, y), Ok(texel(x, y)));
        }
    }

    #[test]
    fn the_coordinates_are_read_vertex_by_vertex() {
        // E971: u0 (word 3) = 0.5 moves u at TL only: u = 0.5 + 0.5 px/64 - 0.5 py/64
        let mut o = identity();
        o[3] = 0.5f32.to_bits();
        let (u, v) = coords(&o, 10, 40).unwrap();
        assert!((u - (0.5 + 0.5 * 10.5 / 64.0 - 0.5 * 40.5 / 64.0)).abs() < 1e-6);
        assert!((v - 40.5 / 64.0).abs() < 1e-6);
    }

    #[test]
    fn the_plane_follows_the_vertex_words() {
        // E972: TR x at 80 (word 18) gives u = px / 80, the box's coverage unchanged
        let mut o = identity();
        o[18] = 0x1050_0010;
        let (u, _) = coords(&o, 40, 3).unwrap();
        assert!((u - 40.5 / 80.0).abs() < 1e-6);
        assert_eq!(at(&o, 40, 3), Ok(texel(32, 3)));
    }

    #[test]
    fn outside_the_unit_square_the_stride_texture_clamps() {
        // E974: v1 = 0.5 (word 6) puts v above 1 at the bottom right: texel row 63
        let mut o = identity();
        o[6] = 0.5f32.to_bits();
        assert_eq!(at(&o, 63, 63), Ok(texel(63, 63)));
        o[6] = 0;
        o[4] = 1.0f32.to_bits(); // v0 = 1: v = 1 - px/64 at the top, from 1 down
        assert_eq!(at(&o, 0, 0), Ok(texel(0, 63)));
    }

    #[test]
    fn a_sampler_word_the_texture_unit_refuses_is_refused_under_q300() {
        // T0 bit 30 (the second format table, x-smp2 17: not measured) on the copy's texture:
        // tex::sample refuses it, and the layer names Q300 (Q078's successor), not Q078
        let mut st = STATE;
        st[0] |= 1 << 30;
        let mut load = |_: u32| Ok(0);
        let e = sample(&identity(), st, 1, 1, &mut load).unwrap_err();
        assert!(format!("{e:?}").contains("[\"Q300\"]"), "{e:?}");
    }

    #[test]
    fn what_e973_changed_is_refused() {
        for (w, v) in
            [(1, 0x3_0000), (11, 0xffff_ffff), (12, 0xffff_ffff), (14, 0xffff_ffff), (10, 0xffff_ffff)]
        {
            let mut o = identity();
            o[w] = v;
            let e = at(&o, 1, 1).unwrap_err();
            assert!(format!("{e:?}").contains("Q066"), "word {w}");
        }
        // a coordinate that is not finite is the iterators' arithmetic (Q200, into which Q205
        // folded)
        let mut o = identity();
        o[3] = 0x7fc0_0000;
        assert!(format!("{:?}", at(&o, 1, 1).unwrap_err()).contains("[\"Q200\"]"));
        // and what changed nothing is modelled
        for (w, v) in [(9, 0xffff_ffff), (13, 0xffff_ffff), (11, ONE), (10, 0x8000_0000), (1, 0x3_0004)] {
            let mut o = identity();
            o[w] = v;
            assert_eq!(at(&o, 7, 9), Ok(texel(7, 9)), "word {w}");
        }
    }

    #[test]
    fn the_finite_values_e1006_ran_in_words_9_and_11_to_14_change_nothing() {
        // r10-geo bgw: 0.25, 0.5, 1.5 and -1.0 in words 11, 12, 14, 2.0 and -1.0 in 9 and 13,
        // every background pixel its own texel (H-INERT 16 of 16; a factor, H-SCALE0, 0 of 12)
        let (q, h, f, m, two) = (0x3e80_0000, 0x3f00_0000, 0x3fc0_0000, 0xbf80_0000, 0x4000_0000);
        for (w, v) in [(11, q), (11, h), (11, f), (11, m), (12, q), (12, h), (12, f), (12, m)]
            .into_iter()
            .chain([(14, q), (14, h), (14, f), (14, m), (9, two), (9, m), (13, two), (13, m)])
        {
            let mut o = identity();
            o[w] = v;
            for (x, y) in [(1, 1), (7, 9), (40, 60), (63, 63)] {
                assert_eq!(at(&o, x, y), Ok(texel(x, y)), "word {w} = {v:#x}");
            }
        }
        // values no record ran stay refused: 2.0 in word 12, 0.25 in word 9
        for (w, v) in [(12, two), (9, q), (11, 0x4120_0000)] {
            let mut o = identity();
            o[w] = v;
            assert!(format!("{:?}", at(&o, 1, 1).unwrap_err()).contains("Q066"), "word {w} = {v:#x}");
        }
    }
}
