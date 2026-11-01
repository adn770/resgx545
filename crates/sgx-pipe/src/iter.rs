// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Iterators (12.3): the value a vertex attribute takes at a pixel. E606: for the one setup run
//! (coordinate set 0, source 1, two components, E437's program) the iterator evaluates the plane
//! through the three vertices' values at the pixel centre, up to an absolute error of 4 units of
//! 2^-23 where the attribute's range per root area is below 0.05, and up to 366 units above it;
//! no bit-exact arithmetic is known. So a value is `Near`, never matched, and a poorly
//! conditioned triangle refuses (Q200). Not modelled here, and refused wherever a scene would
//! need it: four components (Q021), no-wait fetches (Q027, Q093), other sources (Q098, Q180),
//! perspective (w other than 1), and the position source 0 (x + 0.375: E502, Q201).

use crate::Outcome;
use crate::isp::{DEPTH_UNIT, GRID, Tri};

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q021", "Q027", "Q093", "Q098", "Q180", "Q200", "Q201"];

/// A refusing stub for the parts of the unit nothing models yet.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the iterators model the plane at the pixel centre of one setup only (12.3)", OPEN)
}

/// What an iterated attribute is. E606 states the tolerance for the vertices' clip z; the clip x of
/// the same jobs reached 23 units in the same conditioning bin (the record's own table), so no
/// tolerance is known for another attribute and it refuses (Q200).
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Attr {
    ClipZ,
    Other,
}

/// E606's tolerance for an iterated clip z, in units of 2^-23 absolute.
pub const TOLERANCE: u32 = 4;
/// Value range per root area (in pixels) below which E606 measured the tolerance.
pub const CONDITIONING_LIMIT: f64 = 0.05;

/// The attribute's range per root area: (max - min) / sqrt(area in pixels^2), the area of the
/// triangle (half the cross product), at least 1e-3 pixels of root area. Infinite for no area.
pub fn conditioning(t: &Tri, vals: [f32; 3]) -> f64 {
    let area = t.area2().unsigned_abs() as f64 / 2.0 / (GRID * GRID) as f64;
    if area == 0.0 {
        return f64::INFINITY;
    }
    let (lo, hi) = vals.iter().fold((f32::MAX, f32::MIN), |(l, h), &v| (l.min(v), h.max(v)));
    (hi as f64 - lo as f64) / area.sqrt().max(1e-3)
}

/// The value at the centre of pixel (x, y): the plane through the vertices' values, exact. Refuses
/// the triangles E606 did not measure to the tolerance (Q200).
pub fn at_centre(t: &Tri, vals: [f32; 3], attr: Attr, x: u32, y: u32) -> Result<f64, Outcome> {
    if attr != Attr::ClipZ {
        return Err(Outcome::unsupported(
            "an iterated attribute other than the clip z: E606 states the tolerance for the clip z only (its clip x reached 23 units where the record's bound for the z is 4)",
            &["Q200"],
        ));
    }
    let c = conditioning(t, vals);
    if !c.is_finite() || c >= CONDITIONING_LIMIT {
        return Err(Outcome::unsupported(
            &format!(
                "the attribute's range per root area is {c:.3}: E606 measured {TOLERANCE} units only below {CONDITIONING_LIMIT} (up to 366 above)"
            ),
            &["Q200"],
        ));
    }
    Ok(Tri { v: t.v, z: vals }.depth_at(x, y))
}

/// Whether a recorded value is within the tolerance of the model's.
pub fn near(got: f32, want: f64) -> bool {
    (got as f64 - want).abs() / DEPTH_UNIT <= TOLERANCE as f64
}

/// What an iterated value's `Outcome` is: `Near` with the tolerance, never `Ok`.
pub fn outcome() -> Outcome {
    Outcome::Near { ulps: TOLERANCE }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tri() -> Tri {
        Tri { v: [(0, 0), (64 * 256, 0), (0, 64 * 256)], z: [0.0; 3] }
    }

    #[test]
    fn the_stub_names_its_questions() {
        match refuse() {
            Outcome::Unsupported { ids, why } => {
                assert!(!ids.is_empty() && !why.is_empty());
                assert_eq!(ids, OPEN);
            }
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn a_linear_attribute_is_the_plane_at_the_pixel_centre() {
        // value = x / 64 across the triangle: 0, 1, 0 at the vertices
        let v = at_centre(&tri(), [0.0, 1.0, 0.0], Attr::ClipZ, 9, 3).unwrap();
        assert!((v - 9.5 / 64.0).abs() < 1e-12);
    }

    #[test]
    fn the_position_source_is_not_the_centre_so_it_is_not_here() {
        // E502: source 0 gives x + 0.375: a different unit's input (Q201), the plane stays at the centre
        let v = at_centre(&tri(), [0.0, 1.0, 0.0], Attr::ClipZ, 0, 0).unwrap();
        assert!((v - 0.5 / 64.0).abs() < 1e-12 && (v - 0.375 / 64.0).abs() > 1e-4);
    }

    #[test]
    fn a_poorly_conditioned_triangle_refuses_and_names_q200() {
        // value range 1 over a root area of 32 pixels (area 2048): 0.03 passes; over a 1 pixel
        // triangle: refused
        assert!(at_centre(&tri(), [0.0, 1.0, 0.0], Attr::ClipZ, 0, 0).is_ok());
        let small = Tri { v: [(0, 0), (256, 0), (0, 256)], z: [0.0; 3] };
        match at_centre(&small, [0.0, 1.0, 0.0], Attr::ClipZ, 0, 0) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q200"]),
            o => panic!("{o:?}"),
        }
        let none = Tri { v: [(0, 0), (256, 256), (512, 512)], z: [0.0; 3] };
        assert!(at_centre(&none, [0.0, 1.0, 0.0], Attr::ClipZ, 0, 0).is_err());
    }

    #[test]
    fn an_attribute_other_than_the_clip_z_refuses_for_want_of_a_tolerance() {
        match at_centre(&tri(), [0.0, 1.0, 0.0], Attr::Other, 0, 0) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q200"]);
                assert!(why.contains("clip z"));
            }
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn the_tolerance_is_four_units_of_two_to_the_minus_23_absolute() {
        let u = DEPTH_UNIT;
        assert!(near((0.25 + 4.0 * u) as f32, 0.25));
        assert!(!near((0.25 + 5.0 * u) as f32, 0.25));
        assert!(near(-0.5, -0.5 + 3.9 * u));
        assert_eq!(outcome(), Outcome::Near { ulps: 4 });
    }
}
