// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! ISP: the multisample store window of a tile (E503). The unit itself (coverage, depth,
//! stencil, pass types, the background object) is 12.3 and refuses; the arithmetic of coverage
//! and depth for an arbitrary triangle is Q205 (open, no record).

use crate::Outcome;

pub const OPEN: &[&str] = &["Q066", "Q030", "Q086", "Q089", "Q138", "Q141", "Q205"];

pub fn refuse() -> Outcome {
    Outcome::unsupported("the ISP (coverage, depth, stencil) is not modelled (12.3); arithmetic open", OPEN)
}

/// The source pixel (x, y) that the stored pixel (a, b) of tile (tx, ty), 32 x 16 pixels, holds
/// in a multisampled render of `mode` (CR_ISP_MSAA mode 0 to 2) with `te_aa` the CR_TE_AA word
/// (E503): x = 32 tx + 16 b31 + a div sx, y = 16 ty + 8 b30 + b div sy, (sx, sy) = (1, 1),
/// (2, 1), (2, 2) for the modes 0, 1, 2; b30 counts in mode 2 only. Mode 0 was run with both
/// bits clear only, and mode 3 not at all: they refuse for other inputs.
pub fn msaa_source(mode: u32, te_aa: u32, tx: u32, ty: u32, a: u32, b: u32) -> Result<(u32, u32), Outcome> {
    let (b31, b30) = (te_aa >> 31 & 1, te_aa >> 30 & 1);
    let (sx, sy) = match mode {
        0 if b31 | b30 == 0 => (1, 1),
        1 => (2, 1),
        2 => (2, 2),
        0 => {
            return Err(Outcome::unsupported(
                "the window of mode 0 with CR_TE_AA bits 31 or 30 set was not measured",
                &["Q141"],
            ));
        }
        _ => {
            // no question asks about mode 3 (no run used it): Q030 is the MSAA question that
            // covers the tile and window past the first
            return Err(Outcome::unsupported("the window of mode 3 was not measured", &["Q030"]));
        }
    };
    let b30 = if mode == 2 { b30 } else { 0 };
    Ok((32 * tx + 16 * b31 + a / sx, 16 * ty + 8 * b30 + b / sy))
}

/// What `check_windows` found in a pair of dumps of one multisampled render.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct WindowCheck {
    /// pixels the dumps hold in both ramps
    pub stored: u64,
    /// decodable to a source pixel in both
    pub decodable: u64,
    /// tiles with a decodable pixel
    pub tiles: u64,
    /// of those, tiles whose every decodable pixel is the rule's
    pub equal: u64,
    /// tiles decodable in all 512 pixels
    pub full: u64,
    /// tiles that are both equal and fully decodable (the others that are equal hold background
    /// pixels, Q141)
    pub equal_full: u64,
    /// decodable pixels that differ from the rule
    pub wrong: u64,
}

/// Dump pixels: (x, y, dword).
pub type Rows = Vec<(u32, u32, u32)>;

/// The offsets of the decoding (E502 / E503's post hoc reading): the iterated position of a
/// pixel is (x + 0.375, y + 0.125) in every mode.
pub const OX: f64 = 0.375;
pub const OY: f64 = 0.125;

/// Parse a dump's text: lines `row N: v v v ...` of hex dwords into (x, y, dword); a token that
/// is not a hex number keeps its column and is left out.
pub fn parse_rows(text: &str) -> Vec<(u32, u32, u32)> {
    let mut out = vec![];
    for line in text.lines() {
        // "row N: v v ..." anywhere in the line (the dump's lines may carry a prefix)
        let Some(at) = line.find("row ") else { continue };
        let Some((n, vals)) = line[at + 4..].split_once(": ") else { continue };
        let Ok(y) = n.trim().parse::<u32>() else { continue };
        for (x, tok) in vals.split_whitespace().enumerate() {
            if let Ok(v) = u32::from_str_radix(tok, 16) {
                out.push((x as u32, y, v));
            }
        }
    }
    out
}

fn source_of(v: u32, off: f64) -> Option<u32> {
    let x = f32::from_bits(v) as f64 - off;
    (x.is_finite() && (x - x.round()).abs() < 1e-4 && x > -1.0 && x < 4096.0).then(|| x.round() as u32)
}

/// Check the window rule over the x-position and y-position dumps of one render.
pub fn check_windows(
    mode: u32,
    te_aa: u32,
    x: &[(u32, u32, u32)],
    y: &[(u32, u32, u32)],
) -> Result<WindowCheck, Outcome> {
    msaa_source(mode, te_aa, 0, 0, 0, 0)?; // refuse the modes and bits no record measured
    let ymap: std::collections::HashMap<(u32, u32), u32> = y.iter().map(|&(a, b, v)| ((a, b), v)).collect();
    let mut c = WindowCheck::default();
    // per tile: decodable pixels, wrong ones
    let mut tiles = std::collections::BTreeMap::<(u32, u32), (u64, u64)>::new();
    for &(px, py, vx) in x {
        let Some(&vy) = ymap.get(&(px, py)) else { continue };
        c.stored += 1;
        let (Some(sx), Some(sy)) = (source_of(vx, OX), source_of(vy, OY)) else { continue };
        c.decodable += 1;
        let t = tiles.entry((px / 32, py / 16)).or_default();
        t.0 += 1;
        if msaa_source(mode, te_aa, px / 32, py / 16, px % 32, py % 16)? != (sx, sy) {
            t.1 += 1;
            c.wrong += 1;
        }
    }
    for &(n, wrong) in tiles.values() {
        c.tiles += 1;
        c.equal += (wrong == 0) as u64;
        c.full += (n == 512) as u64;
        c.equal_full += (wrong == 0 && n == 512) as u64;
    }
    Ok(c)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mode_1_doubles_in_x_and_the_window_is_the_left_16_columns_unless_b31() {
        assert_eq!(msaa_source(1, 0, 0, 0, 0, 0).unwrap(), (0, 0));
        assert_eq!(msaa_source(1, 0, 0, 0, 5, 3).unwrap(), (2, 3)); // 5 div 2, y not halved
        assert_eq!(msaa_source(1, 0x2000_0000, 1, 2, 31, 15).unwrap(), (32 + 15, 32 + 15));
        assert_eq!(msaa_source(1, 0xa000_0000, 0, 0, 0, 0).unwrap(), (16, 0)); // b31
    }

    #[test]
    fn mode_2_doubles_in_both_and_b30_shifts_the_window_8_rows() {
        assert_eq!(msaa_source(2, 0x2000_0000, 0, 0, 31, 15).unwrap(), (15, 7));
        assert_eq!(msaa_source(2, 0x6000_0000, 0, 0, 0, 0).unwrap(), (0, 8)); // b30
        assert_eq!(msaa_source(2, 0xe000_0000, 1, 1, 0, 0).unwrap(), (32 + 16, 16 + 8));
    }

    #[test]
    fn b30_does_not_act_in_mode_1() {
        assert_eq!(msaa_source(1, 0x6000_0000, 0, 0, 0, 0).unwrap(), (0, 0));
    }

    #[test]
    fn mode_3_names_the_msaa_question_and_mode_0_bits_the_window_one() {
        for (mode, te, q) in [(3, 0x2000_0000, "Q030"), (0, 0x6000_0000, "Q141")] {
            match msaa_source(mode, te, 0, 0, 0, 0) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, [q]),
                o => panic!("{o:?}"),
            }
        }
    }

    #[test]
    fn modes_and_bits_no_record_measured_refuse() {
        // mode 0 ran only with b31 = b30 = 0; mode 3 and above never
        assert_eq!(msaa_source(0, 0x2000_0000, 1, 1, 7, 9).unwrap(), (39, 25));
        assert!(matches!(msaa_source(0, 0x6000_0000, 0, 0, 0, 0), Err(Outcome::Unsupported { .. })));
        assert!(matches!(msaa_source(0, 0xa000_0000, 0, 0, 0, 0), Err(Outcome::Unsupported { .. })));
        assert!(matches!(msaa_source(3, 0x2000_0000, 0, 0, 0, 0), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn rows_parse_with_columns_kept_over_a_bad_token() {
        let t = "junk\nrow 0: 3f800000 zz 40000000\n[ 12.5] row 1: 1\n";
        assert_eq!(parse_rows(t), vec![(0, 0, 0x3f800000), (2, 0, 0x40000000), (0, 1, 1)]);
    }

    fn pos(v: u32, off: f64) -> u32 {
        ((v as f64 + off) as f32).to_bits()
    }

    /// dumps of a W x H mode-`mode` render stored the way the rule says
    fn render(w: u32, h: u32, mode: u32, te: u32) -> (Rows, Rows) {
        let (mut x, mut y) = (vec![], vec![]);
        for py in 0..h {
            for px in 0..w {
                let (sx, sy) = msaa_source(mode, te, px / 32, py / 16, px % 32, py % 16).unwrap();
                x.push((px, py, pos(sx, OX)));
                y.push((px, py, pos(sy, OY)));
            }
        }
        (x, y)
    }

    #[test]
    fn a_render_stored_as_the_rule_says_has_every_tile_equal() {
        let (x, y) = render(64, 32, 2, 0xe000_0000);
        let c = check_windows(2, 0xe000_0000, &x, &y).unwrap();
        assert_eq!((c.stored, c.decodable, c.tiles, c.equal, c.full, c.wrong), (2048, 2048, 4, 4, 4, 0));
        assert_eq!(c.equal_full, 4);
    }

    #[test]
    fn a_wrong_pixel_makes_its_tile_unequal() {
        let (mut x, y) = render(64, 32, 1, 0x2000_0000);
        x[5].2 = pos(60, OX);
        let c = check_windows(1, 0x2000_0000, &x, &y).unwrap();
        assert_eq!((c.tiles, c.equal, c.wrong), (4, 3, 1));
    }

    #[test]
    fn undecodable_pixels_are_not_counted_as_wrong() {
        let (mut x, y) = render(32, 16, 1, 0x2000_0000);
        x[0].2 = 0x3f800000 + 1; // 1.0000001: not a position + 0.375
        let c = check_windows(1, 0x2000_0000, &x, &y).unwrap();
        assert_eq!((c.decodable, c.wrong, c.equal, c.full, c.equal_full), (511, 0, 1, 0, 0));
    }
}
