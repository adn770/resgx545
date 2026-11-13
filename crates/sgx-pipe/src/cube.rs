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
//!   index the Morton interleave of (s, t) with t in bit 0 (E724's "y in the low bit").
//!
//! Refused, naming Q284: two coordinates of equal largest magnitude (no job ran a face tie); a
//! coordinate exactly on a texel boundary when |ma| is not a power of two (at a power of two the
//! upper texel every time, the floor; otherwise E923's 14 misses, which go both ways for one
//! |ma|); a face size other than 16 (one size ran). Bilinear filtering, and so a face edge's
//! taps, is not modelled here at all (Q284).

use crate::Outcome;

/// The one face size measured (E726, E844): 16 x 16, 256 dwords a face.
pub const FACE_SIZE: u32 = 16;

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
            "two cube coordinates of equal largest magnitude (a face tie, never run)",
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

/// The texel of numerator `c` over magnitude `ma` (|c| < ma): floor((c / ma + 1) * 8), exact.
fn texel(c: f32, ma: f32) -> Result<u32, Outcome> {
    // 8c and k * ma (|k| <= 8) are exact in f64, so the boundary test is exact, and a quotient
    // that is not an integer cannot round onto one (its distance from it is far above 2^-53)
    let r = 8.0 * c as f64 / ma as f64;
    let k = r.floor();
    if k * ma as f64 == 8.0 * c as f64 && !is_pow2(ma) {
        return Err(Outcome::unsupported(
            "a cube coordinate exactly on a texel boundary with |ma| not a power of two (E923's ties)",
            &["Q284"],
        ));
    }
    let t = k as i64 + 8;
    assert!((0..16).contains(&t), "texel {t} outside the face ({c} / {ma})");
    Ok(t as u32)
}

fn is_pow2(x: f32) -> bool {
    x.is_normal() && x.to_bits() & 0x007f_ffff == 0
}

/// Morton index of (s, t) in a 16 x 16 face, t in bit 0.
fn twiddle(s: u32, t: u32) -> u32 {
    (0..4).fold(0, |i, b| i | (t >> b & 1) << (2 * b) | (s >> b & 1) << (2 * b + 1))
}

/// The dword index (face * 256 + local) that a point sample of a TEXTYPE 2 texture of faces
/// `size` x `size` reads at (u, v, w).
pub fn point_index(c: [f32; 3], size: u32) -> Result<u32, Outcome> {
    if size != FACE_SIZE {
        return Err(Outcome::unsupported("a cube face size other than 16 x 16 (one size ran)", &["Q284"]));
    }
    let (f, ax) = face(c)?;
    let ma = c[ax].abs();
    let (sc, tc) = st(f, c);
    let (s, t) = (texel(sc, ma)?, texel(tc, ma)?);
    Ok(f * 256 + twiddle(s, t))
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
        assert!(face([0.5, -0.5, 0.1]).is_err(), "a face tie is refused");
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
    fn other_face_sizes_are_refused() {
        assert!(refused(point_index([0.1, 0.2, 1.0], 8)));
        assert!(refused(point_index([0.1, 0.2, 1.0], 32)));
    }
}
