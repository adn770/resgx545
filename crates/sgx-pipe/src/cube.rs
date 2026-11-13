// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The cube map of TEXTYPE 2 point-sampled by smp3d: which dword of the texture a coordinate
//! (u, v, w) reads.
//!
//! - Faces (E726, E844): six 256-dword blocks of a 16 x 16 twiddled face in the order +x, -x,
//!   +y, -y, +z, -z, the face that of the coordinate of largest magnitude |ma| and its sign
//!   (held out on 2048 of 2048 pixels of two off-axis jobs, E844).
//! - (s, t) in a face (E923: fitted on E726's eight jobs, frozen, held out offline on E844's two
//!   at 4090 of 4096): the public cube-map table, our u, v, w as x, y, z [infer]: +x s = -w,
//!   t = -v; -x s = +w, t = -v; +y s = +u, t = +w; -y s = +u, t = -w; +z s = +u, t = -v;
//!   -z s = -u, t = -v; each divided by |ma|, texel floor((q + 1) / 2 * 16), and the face-local
//!   index the Morton interleave of (s, t) with t in bit 0 (E724's "y in the low bit"); held
//!   out on hardware on four new off-axis 16 x 16 programs (E930).
//! - Faces of 8 x 8 (E930): the same rule with 8 for 16 (texel floor((q + 1) / 2 * 8), a 3-bit
//!   Morton), faces 64 dwords apart, held out on three programs.
//! - Faces of 32 x 32 (E930, E951): 1024 dwords apart, (s, t) as at 16 with 32 for 16, and the
//!   face-local index E561's twiddle law of a 32-bit texture: tiles of 16 x 16 interleaved as the
//!   16 x 16 face, the tiles in raster order with s first (bit 8 = s4, bit 9 = t4). E930 read
//!   that index post hoc on its three 32 x 32 jobs (4831 of 4831 predicted pixels); E951 shows it
//!   is E561's law, recorded before E930 ran, at every (s, t) [algebra]; held out on three new
//!   directions (E955).
//! - Faces of 64 x 64 (E955): 4096 dwords apart, E561's law (tiles of 16 x 16 in raster order
//!   with s first: bits 8, 9 = s4, s5 and 10, 11 = t4, t5), held out on three programs against a
//!   pairwise order of the bits above 7 (refuted 3 of 3). Faces of 4 x 4 (E955): 16 dwords apart,
//!   the 2-bit Morton (E561's whole texture when smaller than a tile), held out on two programs
//!   against faces 64 dwords apart (refuted 2 of 2).
//!
//! Refused, naming Q284: two coordinates of equal largest magnitude (E956: the higher axis's face,
//! w over v over u, held out on four sweeps of 32 tie pixels with the third coordinate small, but
//! post hoc 7 of the 599 tie pixels of the kept cube jobs, none of the sweeps', the third
//! coordinate 0.62 to 0.93 of |ma|, read the lower axis's face: no rule); a coordinate exactly on
//! a texel boundary when |ma| is not a power of two (at a power of two the upper texel every time, the floor;
//! otherwise E923's 14 misses, and E931's and E956's boundaries going up or down by their place,
//! no rule frozen); faces of any size other than 4, 8, 16, 32 and 64.
//! Bilinear filtering, and so a face edge's taps, is not modelled here at all (E931, E956: the
//! out-of-face tap reads another face; the adjacent texel held on one edge of two; Q284).

use crate::Outcome;

/// The face sizes read, each held out: 16 x 16, 256 dwords a face, and 8 x 8, 64 (E726, E844,
/// E930); 32 x 32, 1024, and 64 x 64, 4096, E561's law (E951, E955); 4 x 4, 16 (E955).
pub const FACE_SIZES: [u32; 5] = [4, 8, 16, 32, 64];

/// The face of (u, v, w): 2 * axis + (coordinate < 0), axis 0, 1, 2 for u, v, w (E844), and
/// the axis. Refuses a tie between the two largest magnitudes and the zero vector.
pub fn face(c: [f32; 3]) -> Result<(u32, usize), Outcome> {
    let a = c.map(f32::abs);
    let ax = (0..3).fold(0, |m, i| if a[i] > a[m] { i } else { m });
    if a[ax] == 0.0 || !a[ax].is_finite() {
        return Err(Outcome::unsupported("a cube coordinate of zero or non-finite magnitude", &["Q284"]));
    }
    if (0..3).any(|i| i != ax && a[i] == a[ax]) {
        return Err(Outcome::unsupported(
            "two cube coordinates of equal largest magnitude (a face tie: mostly the higher axis, no rule, E956)",
            &["Q284"],
        ));
    }
    Ok((2 * ax as u32 + (c[ax] < 0.0) as u32, ax))
}

/// The face's signed (s, t) numerators, by the public cube-map table (E923).
fn st(face: u32, [u, v, w]: [f32; 3]) -> (f32, f32) {
    match face {
        0 => (-w, -v),
        1 => (w, -v),
        2 => (u, w),
        3 => (u, -w),
        4 => (u, -v),
        _ => (-u, -v),
    }
}

/// The texel of numerator `c` over magnitude `ma` (|c| < ma) in a face of `size`:
/// floor((c / ma + 1) * size / 2), exact.
fn texel(c: f32, ma: f32, size: u32) -> Result<u32, Outcome> {
    // h c and k * ma (|k| <= h, h = size / 2 a power of two) are exact in f64, so the boundary
    // test is exact, and a quotient that is not an integer cannot round onto one (its distance
    // from it is far above 2^-53)
    let h = (size / 2) as f64;
    let r = h * c as f64 / ma as f64;
    let k = r.floor();
    if k * ma as f64 == h * c as f64 && !is_pow2(ma) {
        return Err(Outcome::unsupported(
            "a cube coordinate exactly on a texel boundary with |ma| not a power of two (E923's ties)",
            &["Q284"],
        ));
    }
    let t = k as i64 + h as i64;
    assert!((0..size as i64).contains(&t), "texel {t} outside the face ({c} / {ma})");
    Ok(t as u32)
}

fn is_pow2(x: f32) -> bool {
    x.is_normal() && x.to_bits() & 0x007f_ffff == 0
}

/// Morton index of (s, t) in a 16 x 16 face, t in bit 0.
#[cfg(test)]
fn twiddle(s: u32, t: u32) -> u32 {
    twiddle_bits(s, t, 4)
}

/// Morton index of (s, t) over `bits` bits each, t in bit 0.
fn twiddle_bits(s: u32, t: u32, bits: u32) -> u32 {
    (0..bits).fold(0, |i, b| i | (t >> b & 1) << (2 * b) | (s >> b & 1) << (2 * b + 1))
}

/// E561's index of (s, t) in a face of `size` (a power of two): tiles of min(size, 16) square,
/// the Morton interleave inside a tile (t in bit 0), the tiles in raster order with s first.
fn e561_index(s: u32, t: u32, size: u32) -> u32 {
    let tw = size.min(16);
    let tile = s / tw + (t / tw) * (size / tw);
    tile * tw * tw + twiddle_bits(s % tw, t % tw, tw.trailing_zeros())
}

/// The dword index (face * size * size + local) that a point sample of a TEXTYPE 2 texture of
/// faces `size` x `size` reads at (u, v, w).
pub fn point_index(c: [f32; 3], size: u32) -> Result<u32, Outcome> {
    if !FACE_SIZES.contains(&size) {
        return Err(Outcome::unsupported("a cube face size other than 4, 8, 16, 32 or 64 (E955)", &["Q284"]));
    }
    let (f, ax) = face(c)?;
    let ma = c[ax].abs();
    let (sc, tc) = st(f, c);
    let (s, t) = (texel(sc, ma, size)?, texel(tc, ma, size)?);
    Ok(f * size * size + e561_index(s, t, size))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn refused(r: Result<u32, Outcome>) -> bool {
        matches!(r, Err(Outcome::Unsupported { ids, .. }) if ids == ["Q284"])
    }

    #[test]
    fn the_face_is_the_largest_magnitude_and_its_sign() {
        assert_eq!(face([1.0, 0.5, -0.25]).unwrap(), (0, 0));
        assert_eq!(face([-1.0, 0.5, -0.25]).unwrap(), (1, 0));
        assert_eq!(face([0.1, 0.9, 0.2]).unwrap(), (2, 1));
        assert_eq!(face([0.1, -0.9, 0.2]).unwrap(), (3, 1));
        assert_eq!(face([0.1, 0.2, 0.3]).unwrap(), (4, 2));
        assert_eq!(face([0.1, 0.2, -0.3]).unwrap(), (5, 2));
        assert!(face([0.5, -0.5, 0.1]).is_err(), "a face tie is refused (E956: no rule)");
        assert!(face([0.0, 0.0, 0.0]).is_err());
    }

    #[test]
    fn the_public_table_puts_each_face_corner() {
        // the (s, t) = (0, 0) corner of each face (index face * 256) by the table: s and t at -1
        let lo = -0.96875; // 15.5 / 16 below the centre: texel 0
        assert_eq!(point_index([1.0, -lo, -lo], 16), Ok(0));
        assert_eq!(point_index([-1.0, -lo, lo], 16), Ok(256));
        assert_eq!(point_index([lo, 1.0, lo], 16), Ok(512));
        assert_eq!(point_index([lo, -1.0, -lo], 16), Ok(768));
        assert_eq!(point_index([lo, -lo, 1.0], 16), Ok(1024));
        assert_eq!(point_index([-lo, -lo, -1.0], 16), Ok(1280));
        // t in bit 0: on +z, t = -v one texel up from 0 is index 1, s one texel is index 2
        assert_eq!(point_index([lo, -lo - 0.125, 1.0], 16), Ok(1024 + 1));
        assert_eq!(point_index([lo + 0.125, -lo, 1.0], 16), Ok(1024 + 2));
        assert_eq!(point_index([0.999, -0.999, 1.0], 16), Ok(1024 + 255));
    }

    #[test]
    fn a_boundary_goes_up_at_a_power_of_two_and_is_refused_otherwise() {
        // +z, |ma| = 1: s = u = 0 is the boundary of texels 7 and 8, the upper one
        assert_eq!(point_index([0.0, -0.03, 1.0], 16), Ok(1024 + twiddle(8, 8)));
        assert_eq!(point_index([0.0, -0.03, 2.0], 16), Ok(1024 + twiddle(8, 8)));
        // |ma| = 1.5: u = 0.1875 is exactly (q + 1) * 8 = 9
        assert!(refused(point_index([0.1875, -0.03, 1.5], 16)));
        assert!(refused(point_index([0.0, -0.03, 1.5], 16)), "q = 0 at a non-power-of-two |ma|");
        assert_eq!(point_index([0.1876, -0.03, 1.5], 16), Ok(1024 + twiddle(9, 8)));
    }

    #[test]
    fn a_32_x_32_face_reads_e561_s_tiles() {
        // +z, |ma| = 1: u = 0.3 is s texel floor(1.3 * 16) = 20, -v = 0.6 is t texel 25: tile
        // (1, 1) of 16 x 16 (index 3 in raster order, s first), local (4, 9) (E561, E951)
        assert_eq!(point_index([0.3, -0.6, 1.0], 32), Ok(4 * 1024 + 3 * 256 + twiddle(4, 9)));
        // s = 20, t = 9: tile (1, 0), index 1: bit 8 is s4 and bit 9 is t4 (E930's post hoc form)
        assert_eq!(point_index([0.3, 0.4, 1.0], 32), Ok(4 * 1024 + 256 + twiddle(4, 9)));
        assert_eq!(point_index([-0.999, 0.999, -1.0], 32), Ok(5 * 1024 + 256 + twiddle(15, 0)));
    }

    #[test]
    fn an_8_x_8_face_is_the_rule_with_8_and_other_sizes_are_refused() {
        // +z, |ma| = 1: u = 0.3 is s texel floor(1.3 * 4) = 5, -v = 0.6 is t texel 6
        assert_eq!(point_index([0.3, -0.6, 1.0], 8), Ok(4 * 64 + twiddle_bits(5, 6, 3)));
        assert_eq!(point_index([-0.999, 0.999, -1.0], 8), Ok(5 * 64 + twiddle_bits(7, 0, 3)));
        assert!(refused(point_index([0.1, 0.2, 1.0], 2)));
        assert!(refused(point_index([0.1, 0.2, 1.0], 128)));
    }

    #[test]
    fn faces_of_4_and_64() {
        // 4 x 4: +z, |ma| = 1, u = 0.3 is s texel floor(1.3 * 2) = 2, -v = 0.6 is t 3; 16 apart
        assert_eq!(point_index([0.3, -0.6, 1.0], 4), Ok(4 * 16 + twiddle_bits(2, 3, 2)));
        // 64 x 64: u = 0.3 is s 41, -v = 0.6 is t 51: tile (2, 3) of four a row, index 14, local
        // (9, 3); bits 8, 9 = s4, s5 and 10, 11 = t4, t5 (E561, E955)
        assert_eq!(point_index([0.3, -0.6, 1.0], 64), Ok(4 * 4096 + 14 * 256 + twiddle(9, 3)));
    }
}
