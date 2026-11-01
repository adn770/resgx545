// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! TA (tiling engine and object writer): two rules of the records so far, the region test
//! (E542) and the object's vertex layout (E541). The engine itself (macrotiles, region
//! headers, control streams, the object writer) is 12.2 and refuses.

use crate::Outcome;

pub const OPEN: &[&str] = &["Q070", "Q100", "Q139", "Q086", "Q159", "Q160", "Q161", "Q164", "Q165", "Q068"];

pub fn refuse() -> Outcome {
    Outcome::unsupported("the tiling engine and the object writer are not modelled (12.2)", OPEN)
}

pub type Tri = [(f64, f64); 3];

/// Whether the TA lists a primitive in the 16 x 16 tile [x0, x0 + 16) x [y0, y0 + 16) of a
/// region (E542, H70-T1): the primitive's bounding box has max x >= x0, max y >= y0, min x <
/// x0 + 16 and min y < y0 + 16 (high sides open, low sides closed), and none of the three edge
/// lines has all four tile corners strictly outside it (a corner on the line counts).
pub fn tile_lists(t: &Tri, x0: f64, y0: f64) -> bool {
    let (x1, y1) = (x0 + 16.0, y0 + 16.0);
    let xs = t.map(|p| p.0);
    let ys = t.map(|p| p.1);
    let (bx0, bx1) =
        (xs.iter().cloned().fold(f64::MAX, f64::min), xs.iter().cloned().fold(f64::MIN, f64::max));
    let (by0, by1) =
        (ys.iter().cloned().fold(f64::MAX, f64::min), ys.iter().cloned().fold(f64::MIN, f64::max));
    if bx1 < x0 || by1 < y0 || bx0 >= x1 || by0 >= y1 {
        return false;
    }
    for i in 0..3 {
        let (a, b, c) = (t[i], t[(i + 1) % 3], t[(i + 2) % 3]);
        let (nx, ny) = (b.1 - a.1, a.0 - b.0);
        let side = nx * (c.0 - a.0) + ny * (c.1 - a.1);
        if [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
            .iter()
            .all(|&(x, y)| (nx * (x - a.0) + ny * (y - a.1)) * side < 0.0)
        {
            return false;
        }
    }
    true
}

/// The components a coordinate size code names, codes 1 to 5 (E541: 1, 2, 3, 3, 4); None for
/// the codes no record measured (0, 6, 7).
pub fn size_components(code: u32) -> Option<u32> {
    match code {
        1 => Some(1),
        2 => Some(2),
        3 | 4 => Some(3),
        5 => Some(4),
        _ => None,
    }
}

/// What the object holds per vertex for a vertex program of `n` coordinate outputs (E541).
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ObjectLayout {
    /// dwords a vertex takes in the object (the 1/w and the outputs, flagged sets packed)
    pub stored: u32,
    /// the format word's bits 15:8: 1 + n
    pub iterated: u32,
    /// the format word's bits 31:16 (0x0004 in every completed job)
    pub format_hi: u32,
    /// the four set masks that follow the size and format words
    pub masks: [u32; 4],
}

/// The object layout for `n` outputs, the coordinate size word (3 bits a set, set 0 lowest;
/// the `--blk 16` word) and the format word (one bit a set, the `--blk 17` word): the rule of
/// E541 (H70-F2 for the stored dwords, H70-M for the masks), the hang and fault the record
/// measured as refusals that name the record (Q165: not predicted, recalled), and a refusal for
/// what it leaves open (Q165, Q070).
pub fn object_layout(n: u32, sizes: u32, fmts: u32) -> Result<ObjectLayout, Outcome> {
    // the three jobs of E541's `alt` pattern that did not complete (n, sizes, formats, faulted);
    // the same settings completed at N = 4, 5, 6, 9 and 11 and the rule holds there (Q165 asks why)
    const FAILED: [(u32, u32, u32, bool); 3] = [(2, 5, 1, true), (3, 5, 1, false), (8, 29, 5, false)];
    if let Some(&(_, _, _, fault)) = FAILED.iter().find(|f| (f.0, f.1, f.2) == (n, sizes, fmts)) {
        // a recalled measurement, not a prediction: the rule says nothing about why these three
        // settings failed (Q165), so the model refuses them and names the record in `why`
        return Err(Outcome::unsupported(
            &format!(
                "E541 recorded a {} for these settings (n {n}, sizes {sizes}, formats {fmts}); the rule does not predict it",
                if fault { "fault" } else { "hang" }
            ),
            &["Q165"],
        ));
    }
    let nset =
        (0..8).rev().find(|&i| (sizes >> (3 * i)) & 7 != 0 || (fmts >> i) & 1 != 0).map_or(1, |i| i + 1);
    let (mut saved, mut masks) = (0, [0u32; 4]);
    for i in 0..nset {
        let (code, flagged, bit) = ((sizes >> (3 * i)) & 7, (fmts >> i) & 1 != 0, 1u32 << (i + 1));
        if code > 5 {
            return Err(Outcome::unsupported("a coordinate size code (6, 7) no record measured", &["Q070"]));
        }
        if flagged {
            let c = size_components(code).unwrap_or(0); // code 0 flagged: no component (E541, alt)
            saved += c - c.div_ceil(2);
            masks[0] |= bit;
        }
        if code == 1 {
            masks[1] |= bit;
        }
        if code == 3 || code == 5 {
            masks[2] |= bit;
        }
        if code == 4 || code == 5 {
            masks[3] |= bit;
        }
    }
    Ok(ObjectLayout { stored: 1 + n - saved, iterated: 1 + n, format_hi: 4, masks })
}

#[cfg(test)]
mod tests {
    use super::*;

    const T: Tri = [(0.0, 0.0), (100.0, 0.0), (0.0, 100.0)];

    #[test]
    fn a_triangle_inside_a_tile_is_listed() {
        let t: Tri = [(2.0, 2.0), (10.0, 3.0), (4.0, 12.0)];
        assert!(tile_lists(&t, 0.0, 0.0));
    }

    #[test]
    fn the_low_sides_are_closed_and_the_high_sides_open() {
        // max x exactly at the tile's low edge: listed; min x exactly at the high edge: not
        let left: Tri = [(-10.0, 2.0), (0.0, 8.0), (-10.0, 14.0)];
        assert!(tile_lists(&left, 0.0, 0.0));
        let right: Tri = [(16.0, 2.0), (26.0, 8.0), (16.0, 14.0)];
        assert!(!tile_lists(&right, 0.0, 0.0));
        let below: Tri = [(2.0, -10.0), (8.0, 0.0), (14.0, -10.0)];
        assert!(tile_lists(&below, 0.0, 0.0));
        let above: Tri = [(2.0, 16.0), (8.0, 26.0), (14.0, 16.0)];
        assert!(!tile_lists(&above, 0.0, 0.0));
    }

    #[test]
    fn a_tile_beyond_an_edge_is_not_listed_though_the_bounding_box_meets_it() {
        // the hypotenuse x + y = 100: the tile [80, 96) x [80, 96) lies wholly beyond it
        assert!(!tile_lists(&T, 80.0, 80.0));
    }

    #[test]
    fn an_edge_through_a_corner_counts_as_meeting_the_tile() {
        // the corner (60, 40) of the tile [60, 76) x [40, 56) is on x + y = 100
        assert!(tile_lists(&T, 60.0, 40.0));
        // with the edge 0.5 nearer the origin, all four corners are strictly beyond it
        let t: Tri = [(0.0, 0.0), (99.5, 0.0), (0.0, 99.5)];
        assert!(!tile_lists(&t, 60.0, 40.0));
    }

    #[test]
    fn size_codes_name_1_2_3_3_4_components_and_the_rest_are_unknown() {
        let c: Vec<_> = (0..8).map(size_components).collect();
        assert_eq!(c, [None, Some(1), Some(2), Some(3), Some(3), Some(4), None, None]);
    }

    #[test]
    fn a_plain_vertex_stores_one_dword_more_than_its_outputs() {
        // N = 4, no set flagged: 1/w + 4 outputs
        let l = object_layout(4, 1, 0).unwrap();
        assert_eq!((l.stored, l.iterated, l.format_hi), (5, 5, 4));
        assert_eq!(l.masks, [0, 0b10, 0, 0]);
    }

    #[test]
    fn a_flagged_set_packs_its_components_in_half_as_many_dwords() {
        // N = 4 with one flagged set of each size code 1 to 5: 5, 4, 4, 4, 3 (E541, 12 of 12)
        let got: Vec<u32> = (1..=5).map(|c| object_layout(4, c, 1).unwrap().stored).collect();
        assert_eq!(got, [5, 4, 4, 4, 3]);
        // N = 8, sets (3, 4) both flagged: 7; (5, 5): 5; (1, 5): 7
        assert_eq!(object_layout(8, 3 | 4 << 3, 3).unwrap().stored, 7);
        assert_eq!(object_layout(8, 5 | 5 << 3, 3).unwrap().stored, 5);
        assert_eq!(object_layout(8, 1 | 5 << 3, 3).unwrap().stored, 7);
    }

    #[test]
    fn masks_follow_size_and_format_bits() {
        // set 0 code 5 flagged, set 1 code 3 not: mask0 = set 0, mask1 = -, mask2 = both, mask3 = set 0
        let l = object_layout(5, 5 | 3 << 3, 1).unwrap();
        assert_eq!(l.masks, [0b10, 0, 0b110, 0b10]);
    }

    #[test]
    fn the_measured_hang_and_fault_are_predicted_for_those_inputs_only() {
        for (n, s, f) in [(2, 5, 1), (3, 5, 1), (8, 29, 5)] {
            match object_layout(n, s, f) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q165"]);
                    assert!(why.contains("E541") && why.contains("does not predict"), "{why}");
                }
                o => panic!("{o:?}"),
            }
        }
        // the same settings at other N completed: the rule computes them
        // (the set of code 0 with its format bit set takes no component: 4 of 4 completed jobs)
        let got: Vec<u32> = [(5, 29), (6, 29), (9, 93), (11, 93)]
            .iter()
            .map(|&(n, s)| object_layout(n, s, 5).unwrap().stored)
            .collect();
        assert_eq!(got, [4, 5, 8, 10]);
    }

    #[test]
    fn codes_no_record_measured_refuse() {
        // set 0 with code 6 or 7, flagged or not, and set 1 with code 6
        for sizes in [6u32, 7] {
            assert!(matches!(object_layout(4, sizes, 1), Err(Outcome::Unsupported { .. })), "{sizes}");
            assert!(matches!(object_layout(4, sizes, 0), Err(Outcome::Unsupported { .. })), "{sizes}");
        }
        assert!(matches!(object_layout(4, 6 << 3, 3), Err(Outcome::Unsupported { .. })));
        assert_eq!(object_layout(4, 0, 1).unwrap().stored, 5);
    }
}
