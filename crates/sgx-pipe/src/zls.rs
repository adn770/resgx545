// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! ZLS: the depth/stencil store layout (E465, E489). Only the address rule exists; the store
//! itself (formats, overflow, loads) is 12.4 and refuses.

use crate::Outcome;

/// Open questions that block the rest of the unit.
/// The status of the address rule (rules.rs).
pub const STORE_STATUS: crate::rules::Status = crate::rules::ZLS_ADDRESS;

pub const OPEN: &[&str] = &["Q107", "Q120", "Q121", "Q122"];

pub fn refuse() -> Outcome {
    Outcome::unsupported("zls store and load are not modelled (12.4); only the address rule of E465", OPEN)
}

/// The dword index inside a 32 x 16 tile of the pixel (x, y) of the tile: the bits y0 x0 y1 x1
/// y2 x2 y3 x3 x4 from the lowest (E465).
pub fn in_tile_index(x: u32, y: u32) -> u32 {
    let (x, y) = (x & 31, y & 15);
    let mut i = 0;
    for b in 0..4 {
        i |= ((y >> b) & 1) << (2 * b) | ((x >> b) & 1) << (2 * b + 1);
    }
    i | ((x >> 4) & 1) << 8
}

/// The pixel (x, y) of a 32 x 16 tile that dword `k` of its slot holds: the inverse of
/// [`in_tile_index`].
pub fn in_tile_pixel(k: u32) -> (u32, u32) {
    let (mut x, mut y) = (((k >> 8) & 1) << 4, 0);
    for b in 0..4 {
        y |= ((k >> (2 * b)) & 1) << b;
        x |= ((k >> (2 * b + 1)) & 1) << b;
    }
    (x, y)
}

/// The dword of the depth buffer that holds pixel (x, y) when the store's pitch is G + 1 tiles
/// (`G` is CR_ISP_ZLSCTL bits 11:3): 512 * (ty * (G + 1) + tx) + the in-tile index (E465).
pub fn store_dword(x: u32, y: u32, g: u32) -> u32 {
    512 * ((y >> 4) * (g + 1) + (x >> 5)) + in_tile_index(x, y)
}

/// What `check_store` found in a pair of stored depth dumps.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct StoreCheck {
    /// dwords that left the fill
    pub stored: u64,
    /// decode to a pixel whose rule address is the dword's own
    pub at_rule: u64,
    /// at the rule's address, for a pixel past the target (x >= W or y >= H): what the store
    /// holds there is open (Q122), so these are not counted matched
    pub at_rule_outside: u64,
    /// the background depth 1.0 in both ramps, in a tile of the target, at a pixel past it (Q122)
    pub background_outside: u64,
    /// the background depth 1.0 in both ramps, in a slot that is no tile of the target
    /// (the overflowed jobs' tiles after the zero ones: Q107)
    pub background_tiles: u64,
    /// zero in both ramps (E489: the overflowed jobs, Q107)
    pub zero: u64,
    /// at another address, or not decodable and not one of the above
    pub other: u64,
    pub slots: u64,
    pub slots_equal: bool,
    /// where no two tiles share an address: pixels with their own values at the rule address,
    /// and pixels without (None when tiles overlap)
    pub back: Option<(u64, u64)>,
}

pub const FILL: u32 = 0xdead_beef;
pub const BACKGROUND: u32 = 0x3f80_0000;

/// A stored ramp dword's pixel index along an axis of `size` pixels: depth = 0.25 + 0.5 * (p +
/// 0.5) / (3 * size), within 0.05 of a pixel's centre (the decoding of E465 and E489).
pub fn decode_ramp(v: u32, size: u32) -> Option<u32> {
    let p = (f32::from_bits(v) as f64 - 0.25) * 6.0 * size as f64;
    let q = (p - 0.5).round();
    (q >= 0.0 && (p - 0.5 - q).abs() <= 0.05).then_some(q as u32)
}

/// Check the rule over a pair of dumps (the x-ramp and the y-ramp job of one case) of a W x H
/// target with pitch G + 1 tiles. Both dumps are the depth buffer as little-endian dwords.
pub fn check_store(w: u32, h: u32, g: u32, ax: &[u32], ay: &[u32]) -> StoreCheck {
    let mut c = StoreCheck::default();
    let mut slots = std::collections::BTreeSet::new();
    for (i, &vx) in ax.iter().enumerate() {
        if vx == FILL {
            continue;
        }
        let vy = ay.get(i).copied().unwrap_or(FILL);
        c.stored += 1;
        slots.insert(i >> 9);
        // the tile this slot is, and the pixel of the dword in it
        let (slot, k) = ((i >> 9) as u32, (i & 511) as u32);
        let (ty, tx) = (slot / (g + 1), slot % (g + 1));
        let in_grid = tx < w.div_ceil(32) && ty < h.div_ceil(16);
        let (ix, iy) = in_tile_pixel(k);
        let past = 32 * tx + ix >= w || 16 * ty + iy >= h;
        if vx == BACKGROUND && vy == BACKGROUND && (!in_grid || past) {
            if in_grid { c.background_outside += 1 } else { c.background_tiles += 1 }
        } else if vx == 0 && vy == 0 {
            c.zero += 1;
        } else if let (Some(px), Some(py)) = (decode_ramp(vx, w), decode_ramp(vy, h))
            && store_dword(px, py, g) as usize == i
        {
            if px >= w || py >= h { c.at_rule_outside += 1 } else { c.at_rule += 1 }
        } else {
            c.other += 1;
        }
    }
    let (tw, th) = (w.div_ceil(32), h.div_ceil(16));
    let want: std::collections::BTreeSet<usize> =
        (0..th).flat_map(|ty| (0..tw).map(move |tx| (ty * (g + 1) + tx) as usize)).collect();
    c.slots = slots.len() as u64;
    c.slots_equal = slots == want;
    if g + 1 >= tw {
        let (mut ok, mut bad) = (0, 0);
        for y in 0..h {
            for x in 0..w {
                let i = store_dword(x, y, g) as usize;
                let hit = ax.get(i).is_some_and(|&v| v != FILL && decode_ramp(v, w) == Some(x))
                    && ay.get(i).is_some_and(|&v| decode_ramp(v, h) == Some(y));
                if hit { ok += 1 } else { bad += 1 }
            }
        }
        c.back = Some((ok, bad));
    }
    c
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ramp(p: u32, size: u32) -> u32 {
        (0.25f32 + 0.5 * (p as f32 + 0.5) / (3.0 * size as f32)).to_bits()
    }

    /// A pair of dumps for a W x H target the way the rule says the hardware stores them.
    fn dumps(w: u32, h: u32, g: u32, len: usize) -> (Vec<u32>, Vec<u32>) {
        let (mut ax, mut ay) = (vec![FILL; len], vec![FILL; len]);
        for y in 0..h {
            for x in 0..w {
                let i = store_dword(x, y, g) as usize;
                ax[i] = ramp(x, w);
                ay[i] = ramp(y, h);
            }
        }
        (ax, ay)
    }

    #[test]
    fn in_tile_order_is_y0_x0_y1_x1_y2_x2_y3_x3_x4() {
        // the bit positions from the lowest: y0 0, x0 1, y1 2, x1 3, y2 4, x2 5, y3 6, x3 7, x4 8
        let order =
            [('y', 0), ('x', 0), ('y', 1), ('x', 1), ('y', 2), ('x', 2), ('y', 3), ('x', 3), ('x', 4)];
        for (pos, (axis, bit)) in order.into_iter().enumerate() {
            let (x, y) = if axis == 'x' { (1 << bit, 0) } else { (0, 1 << bit) };
            assert_eq!(in_tile_index(x, y), 1 << pos, "{axis}{bit}");
        }
    }

    #[test]
    fn the_in_tile_pixel_inverts_the_index() {
        for y in 0..16 {
            for x in 0..32 {
                assert_eq!(in_tile_pixel(in_tile_index(x, y)), (x, y));
            }
        }
    }

    #[test]
    fn the_in_tile_index_is_a_permutation_of_512() {
        let mut seen = vec![false; 512];
        for y in 0..16 {
            for x in 0..32 {
                let i = in_tile_index(x, y) as usize;
                assert!(i < 512 && !seen[i]);
                seen[i] = true;
            }
        }
    }

    #[test]
    fn tiles_start_at_512_ty_g_plus_1_plus_tx() {
        assert_eq!(store_dword(32, 0, 1), 512);
        assert_eq!(store_dword(0, 16, 1), 1024);
        assert_eq!(store_dword(32, 16, 1), 1536);
        assert_eq!(store_dword(33, 17, 1), 1536 + 3);
        assert_eq!(store_dword(0, 16, 511), 512 * 512);
    }

    #[test]
    fn ramp_decode_round_trips_and_rejects_off_centre_values() {
        for p in [0u32, 1, 17, 63] {
            assert_eq!(decode_ramp(ramp(p, 64), 64), Some(p));
        }
        assert_eq!(decode_ramp(0, 64), None);
        assert_eq!(decode_ramp((0.25f32 + 0.5 * 1.0 / (3.0 * 64.0)).to_bits(), 64), None); // a pixel edge
    }

    #[test]
    fn a_store_as_the_rule_says_is_all_at_the_rule() {
        let (ax, ay) = dumps(64, 32, 1, 512 * 8);
        let c = check_store(64, 32, 1, &ax, &ay);
        assert_eq!((c.stored, c.at_rule, c.other, c.background_outside, c.zero), (2048, 2048, 0, 0, 0));
        assert!(c.slots_equal);
        assert_eq!(c.slots, 4);
        assert_eq!(c.back, Some((2048, 0))); // G + 1 = 2 is the tiles of a row: no overlap
    }

    #[test]
    fn a_dword_at_another_address_is_counted_other() {
        let (mut ax, ay) = dumps(64, 32, 1, 512 * 8);
        let (a, b) = (store_dword(3, 3, 1) as usize, store_dword(40, 20, 1) as usize);
        ax.swap(a, b);
        let c = check_store(64, 32, 1, &ax, &ay);
        assert_eq!(c.other, 2);
        assert_eq!(c.at_rule, 2046);
    }

    #[test]
    fn zero_is_counted_apart_and_background_over_a_pixel_of_the_target_is_not_explained() {
        let (mut ax, mut ay) = dumps(64, 32, 1, 512 * 8);
        let (a, b) = (store_dword(0, 0, 1) as usize, store_dword(1, 0, 1) as usize);
        (ax[a], ay[a]) = (BACKGROUND, BACKGROUND);
        (ax[b], ay[b]) = (0, 0);
        let c = check_store(64, 32, 1, &ax, &ay);
        // the zero is E489's overflow (Q107); background where a pixel of the target belongs is
        // nothing a record explains: it is "other", a mismatch
        assert_eq!(
            (c.zero, c.at_rule, c.other, c.background_outside, c.background_tiles),
            (1, 2046, 1, 0, 0)
        );
    }

    #[test]
    fn pixels_past_the_target_are_counted_apart_whatever_they_hold() {
        // 34 x 18: edge tiles hold pixels past x = 34 and y = 18 (Q122: what they store is open)
        let (mut ax, mut ay) = dumps(34, 18, 3, 512 * 8);
        // the ramp continues past the target in the real dumps: pixel (40, 2) with its own values
        let i = store_dword(40, 2, 3) as usize;
        (ax[i], ay[i]) = (ramp(40, 34), ramp(2, 18));
        // and a background dword at (50, 3), outside as well
        let j = store_dword(50, 3, 3) as usize;
        (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        let c = check_store(34, 18, 3, &ax, &ay);
        assert_eq!(c.at_rule, 34 * 18);
        assert_eq!((c.at_rule_outside, c.background_outside, c.other), (1, 1, 0));
    }

    #[test]
    fn background_in_a_slot_that_is_no_tile_of_the_target_is_q107_territory() {
        // 4096 x 4096 at G = 0: one tile a row, slots 0..255 are the target's; slot 300 is not
        let (mut ax, mut ay) = (vec![FILL; 512 * 301], vec![FILL; 512 * 301]);
        for k in 0..512 {
            (ax[512 * 300 + k], ay[512 * 300 + k]) = (BACKGROUND, BACKGROUND);
        }
        let c = check_store(4096, 4096, 0, &ax, &ay);
        assert_eq!((c.background_tiles, c.background_outside, c.other), (512, 0, 0));
    }

    #[test]
    fn the_backward_walk_counts_pixels_where_tiles_do_not_overlap() {
        let (ax, ay) = dumps(64, 32, 2, 512 * 12);
        let c = check_store(64, 32, 2, &ax, &ay);
        assert_eq!(c.back, Some((2048, 0)));
    }
}
