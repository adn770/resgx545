// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! PBE: the end-of-tile emit, pack modes 0 to 3 and the one- and two-channel modes, the stored
//! rectangle (12.1).
//!
//! The end-of-tile task hands the PBE four words and a sideband (doc/specs/fw_format.md 9.6):
//! EMIT0 and EMIT1 give the stored rectangle, inclusive, minimum and maximum x in bits 12:0 and
//! y in bits 28:16 (E267); EMIT2 has the number of four-pixel units stored of each 32 x 16 tile
//! in bits 15:8 (0x80 is the whole tile, E266) and the row pitch in bits 27:16 as (value + 1) x
//! 8 bytes (E267); EMIT3 is the byte address of pixel (0, 0), bits 1:0 ignored (E267). The
//! sideband's bits 5:0 are the pack mode and bit 9 the tile-relative flag (E030). Of the 64
//! pack modes 0 stores the colour as ARGB8888, 1 as ABGR8888, 2 as BGRA8888, 3 as RGB565 (E031,
//! E030); mode 8 one byte, the channel sideband bits 8:6 pick (0 alpha, 1 red, 2 green, 3 to 7
//! blue), mode 7 two bytes (0 alpha and red, 1 to 7 green and blue), modes 15, 18, 20, 27 and 28
//! the low 16 bits and 24 and 25 the blue byte whatever the field (E383, E999 for 20 and 27 at 0
//! to 3); a pixel of n bytes is at byte x n of its row, so a dword holds 4 / n pixels from its low
//! byte (every pixel of 139 kept images, tests/pbe_pack_images.rs). The rest refuse (Q044, and
//! Q012 for modes 22 and 34). Bit 25 of the word that loads CR_REG_0400 inverts the stored alpha
//! in the modes 0 to 2 and nothing in mode 3; no other bit of it changes a pixel in modes 0 to 3
//! (E268); in mode 8 bit 25 changes nothing (E385); the one- and two-channel modes ran with the
//! word 0x80 only.

use crate::Outcome;
use crate::mem::Mem;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q012", "Q040", "Q044", "Q046", "Q074", "Q054", "Q183"];

/// A refusing stub for what the pack modes 0 to 3 and the rectangle do not cover.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the pixel back end past pack modes 0 to 3 is not modelled", OPEN)
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Pack {
    Argb8888,
    Abgr8888,
    Bgra8888,
    Rgb565,
    /// mode 7 with sideband bits 8:6 = 0: alpha and red, two bytes (E383)
    AlphaRed,
    /// the colour's low 16 bits, green and blue: mode 7 at bits 8:6 = 1 to 7, modes 15, 18, 20, 27
    /// and 28 (E383, E999)
    Low16,
    /// one byte, the colour shifted right by this many bits: mode 8's field picks it, 24 and 25
    /// store blue (E383)
    Byte(u32),
}

impl Pack {
    pub fn bytes(self) -> u32 {
        match self {
            Pack::Rgb565 | Pack::AlphaRed | Pack::Low16 => 2,
            Pack::Byte(_) => 1,
            _ => 4,
        }
    }
}

/// The pack mode of a sideband, or the refusal naming the question of what is not modelled.
pub fn pack_of(sideband: u32) -> Result<Pack, Outcome> {
    if sideband & 0x200 == 0 {
        return Err(Outcome::unsupported("a sideband without the tile-relative bit 9", &["Q074"]));
    }
    // bits 8:6 pick a channel only in modes 7 and 8 and change no pixel in modes 0 to 3 (E030, E383);
    // bit 11 faults the job (E383, E1034) and bit 12's words vary in their low half (E1034): refused
    if sideband & 0xffff_fc00 != 0 {
        return Err(Outcome::unsupported("sideband bits 10 and up in a pack mode 0 to 3", &["Q046"]));
    }
    let field = sideband >> 6 & 7;
    match sideband & 0x3f {
        0 => Ok(Pack::Argb8888),
        1 => Ok(Pack::Abgr8888),
        2 => Ok(Pack::Bgra8888),
        3 => Ok(Pack::Rgb565),
        // E383: bits 8:6 = 0 to 7 in modes 7, 8, 15, 18, 24, 25 and 28
        7 if field == 0 => Ok(Pack::AlphaRed),
        7 | 15 | 18 | 28 => Ok(Pack::Low16),
        8 => Ok(Pack::Byte([24, 16, 8, 0, 0, 0, 0, 0][field as usize])),
        24 | 25 => Ok(Pack::Byte(0)),
        // E999: modes 20 and 27 store mode 15's image at bits 8:6 = 0 to 3, the only values run
        20 | 27 if field <= 3 => Ok(Pack::Low16),
        22 | 34 => Err(Outcome::unsupported("pack modes 22 and 34 read o0 as a float", &["Q012"])),
        m => Err(Outcome::unsupported(
            &format!("pack mode {m} at sideband bits 8:6 = {field} is not modelled"),
            &["Q044"],
        )),
    }
}

/// Whether the records give the image for the word that loads CR_REG_0400 in this sideband's
/// mode: in modes 0 to 3 no bit but 25 changes a pixel (E268); the one- and two-channel modes
/// ran with the word 0x80 only (E031, E383, E999), and mode 8 with bit 25 too, which changed
/// nothing there (E385, at bits 8:6 = 0).
pub fn reg0400_known(sideband: u32, reg: u32) -> Result<(), Outcome> {
    let ok = match sideband & 0x3f {
        0..=3 => true,
        8 if sideband >> 6 & 7 == 0 => reg & !(1 << 25) == 0x80,
        _ => reg == 0x80,
    };
    if ok {
        Ok(())
    } else {
        Err(Outcome::unsupported(
            &format!("the CR_REG_0400 word {reg:#x} in pack mode {} did not run", sideband & 0x3f),
            &["Q044"],
        ))
    }
}

/// Whether the records fix the RGB565 value of the colour `o0`. E031 stored two colours only,
/// 0xff203040 and 0x80ff8040, whose channels truncate and round to nearest to the same values;
/// no record gives the conversion where the two differ, so there the model does not know it (Q044).
/// Mode 3 is therefore not a fitted rule but a refusal outside the colours that cannot tell the
/// conversions apart.
pub fn rgb565_known(o0: u32) -> bool {
    let ch = |c: u32, bits: u32| {
        let max = (1u32 << bits) - 1;
        let trunc = c >> (8 - bits);
        let nearest = ((c * max + 127) / 255).min(max);
        let half_up = ((c + (1 << (7 - bits))) >> (8 - bits)).min(max);
        trunc == nearest && trunc == half_up
    };
    ch(o0 >> 16 & 0xff, 5) && ch(o0 >> 8 & 0xff, 6) && ch(o0 & 0xff, 5)
}

/// The refusal for a colour whose RGB565 value no record gives.
pub fn rgb565_unknown() -> Outcome {
    Outcome::unsupported(
        "RGB565 of a colour where truncation and rounding differ: no record gives it",
        &["Q044"],
    )
}

/// The value stored for a shader colour `o0` (0xAARRGGBB as the shader writes it) and the number
/// of bytes it takes. `invert_alpha` is bit 25 of the CR_REG_0400 word (E268).
pub fn pack_pixel(p: Pack, o0: u32, invert_alpha: bool) -> u32 {
    // E268: modes 0 to 2; E385: mode 8 (alpha at bits 8:6 = 0) unchanged; the other one- and
    // two-channel modes refuse the bit (reg0400_known)
    let inverts = matches!(p, Pack::Argb8888 | Pack::Abgr8888 | Pack::Bgra8888);
    let o0 = if invert_alpha && inverts { o0 ^ 0xff00_0000 } else { o0 };
    let (a, r, g, b) = (o0 >> 24, o0 >> 16 & 0xff, o0 >> 8 & 0xff, o0 & 0xff);
    match p {
        Pack::Argb8888 => o0,
        Pack::Abgr8888 => a << 24 | b << 16 | g << 8 | r,
        Pack::Bgra8888 => b << 24 | g << 16 | r << 8 | a,
        // the low bits of each channel dropped (0x80ff8040 -> 0xfc08, 0xff203040 -> 0x2188, E031)
        Pack::Rgb565 => r >> 3 << 11 | g >> 2 << 5 | b >> 3,
        Pack::AlphaRed => o0 >> 16,
        Pack::Low16 => o0 & 0xffff,
        Pack::Byte(s) => o0 >> s & 0xff,
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Emit {
    pub words: [u32; 4],
    pub sideband: u32,
}

/// Store the pixels of tile (tx, ty), 32 x 16 pixels in raster order in `colours`, that lie in
/// the emit's rectangle; the pixel (x, y) goes to FBADDR + y pitch + x bytes-per-pixel.
pub fn store_tile(
    e: &Emit,
    reg0400: u32,
    tile: (u32, u32),
    colours: &[u32],
    mem: &mut Mem,
) -> Result<(), Outcome> {
    let [w0, w1, w2, w3] = e.words;
    let pack = pack_of(e.sideband)?;
    reg0400_known(e.sideband, reg0400)?;
    // EMIT1 bit 31 hangs the job; the other bits above the 13-bit fields are ignored (E267)
    if w1 >> 31 != 0 {
        return Err(Outcome::Hang { record: "E267".into() });
    }
    let count = w2 >> 8 & 0xff;
    // EMIT2 bits 6:0 and 31:28 change the image (rotations, mirrors, averages: E267, E382) and
    // are not modelled; bit 7 changes nothing
    if w2 & 0x7f != 0 || w2 >> 28 != 0 {
        return Err(Outcome::unsupported("EMIT2 bits 6:0 or 31:28 set", &["Q040"]));
    }
    match count {
        0 => return Ok(()),
        c if c & 1 == 1 && c <= 0x80 => return Err(Outcome::Hang { record: "E266".into() }),
        0x80 => {}
        _ => return Err(Outcome::unsupported("a count other than 0, 0x80 and the odd values", &["Q040"])),
    }
    let (x0, y0, x1, y1) = (w0 & 0x1fff, w0 >> 16 & 0x1fff, w1 & 0x1fff, w1 >> 16 & 0x1fff);
    let pitch = ((w2 >> 16 & 0xfff) + 1) * 8;
    let base = w3 & !3;
    let invert = reg0400 >> 25 & 1 != 0;
    for (i, &c) in colours.iter().enumerate().take(512) {
        let (x, y) = (32 * tile.0 + i as u32 % 32, 16 * tile.1 + i as u32 / 32);
        if x < x0 || x > x1 || y < y0 || y > y1 {
            continue;
        }
        if pack == Pack::Rgb565 && !rgb565_known(c) {
            return Err(rgb565_unknown());
        }
        let v = pack_pixel(pack, c, invert);
        let addr = base.wrapping_add(y * pitch + x * pack.bytes());
        if pack.bytes() == 4 {
            mem.write32(addr, v)?;
        } else {
            // a dword holds 4 / bytes pixels from its low byte (E383, E999)
            let (a, sh) = (addr & !3, (addr & 3) * 8);
            let mask = if pack.bytes() == 2 { 0xffff } else { 0xff };
            let old = mem.read32(a)?;
            mem.write32(a, old & !(mask << sh) | (v & mask) << sh)?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    const A: u32 = 0xff20_3040;
    const B: u32 = 0x80ff_8040;

    #[test]
    fn modes_0_to_3_store_the_two_recorded_colours_as_the_hardware_did() {
        // E031: pack-modes dumps, background 0xff203040 and the shader colour 0x80ff8040
        let want = [
            (0x200, 0xff20_3040, 0x80ff_8040),
            (0x201, 0xff40_3020, 0x8040_80ff),
            (0x202, 0x4030_20ff, 0x4080_ff80),
            (0x203, 0x2188, 0xfc08),
        ];
        for (sb, a, b) in want {
            let p = pack_of(sb).unwrap();
            assert_eq!((pack_pixel(p, A, false), pack_pixel(p, B, false)), (a, b), "sideband {sb:#x}");
        }
        assert_eq!(pack_of(0x203).unwrap().bytes(), 2);
        assert_eq!(pack_of(0x200).unwrap().bytes(), 4);
    }

    #[test]
    fn rgb565_is_known_only_where_truncation_and_rounding_agree() {
        // E031's two colours; 0x80 -> 5 bits is 16 either way, 0x7f -> 15 truncated and 16 rounded
        assert!(rgb565_known(A) && rgb565_known(B));
        assert!(!rgb565_known(0xff7f_0000), "r = 0x7f: 15 truncated, 16 rounded");
        assert!(!rgb565_known(0xff00_0300), "g = 3: 0 truncated, 1 rounded");
        let mut m = mem_of(0x1000_0000, 512);
        let e = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x203);
        let r = store_tile(&e, 0x80, (0, 0), &[0xff7f_0000; 512], &mut m);
        assert!(matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q044"]), "{r:?}");
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xdead_beef, "nothing stored");
    }

    #[test]
    fn store_tile_inverts_alpha_when_reg_0400_bit_25_is_set() {
        // E268: bit 25 of the CR_REG_0400 word inverts the stored alpha in modes 0 to 2, not 3
        let e = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x200);
        let mut off = mem_of(0x1000_0000, 512);
        let mut on = mem_of(0x1000_0000, 512);
        store_tile(&e, 0x80, (0, 0), &[B; 512], &mut off).unwrap();
        store_tile(&e, 0x80 | 1 << 25, (0, 0), &[B; 512], &mut on).unwrap();
        assert_eq!(off.read32(0x1000_0000).unwrap(), 0x80ff_8040);
        assert_eq!(on.read32(0x1000_0000).unwrap(), 0x7fff_8040);
        let e565 = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x203);
        let mut m = mem_of(0x1000_0000, 512);
        store_tile(&e565, 0x80 | 1 << 25, (0, 0), &[B; 512], &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap() & 0xffff, 0xfc08);
    }

    #[test]
    fn bit_25_of_reg_0400_inverts_alpha_where_the_mode_has_it() {
        let p = |sb| pack_of(sb).unwrap();
        assert_eq!(pack_pixel(p(0x200), 0x80ff_8040, true), 0x7fff_8040);
        assert_eq!(pack_pixel(p(0x201), 0x80ff_8040, true), 0x7f40_80ff);
        assert_eq!(pack_pixel(p(0x202), 0x80ff_8040, true), 0x4080_ff7f);
        assert_eq!(pack_pixel(p(0x203), 0x80ff_8040, true), 0xfc08, "RGB565 stores no alpha");
    }

    #[test]
    fn other_modes_and_a_missing_tile_relative_bit_refuse_naming_their_questions() {
        let ids = |sb| match pack_of(sb).unwrap_err() {
            Outcome::Unsupported { ids, .. } => ids,
            o => panic!("{o:?}"),
        };
        assert_eq!(ids(0x216), ["Q012"]);
        assert_eq!(ids(0x222), ["Q012"]);
        assert_eq!(ids(0x204), ["Q044"]);
        // modes 20 and 27 ran at bits 8:6 = 0 to 3 only (E999)
        for m in [20u32, 27] {
            assert_eq!(ids(0x200 | 4 << 6 | m), ["Q044"], "mode {m}");
        }
        assert_eq!(ids(0x003), ["Q074"]);
        assert_eq!(ids(0x600), ["Q046"]);
        // bits 8:6 change no pixel in modes 0 to 3 (E030, E383)
        assert!(pack_of(0x200 | 7 << 6).is_ok());
    }

    #[test]
    fn the_one_and_two_channel_modes_store_e383s_and_e999s_values() {
        // E383: two colours whose bytes all differ and the background, every pixel
        let (c0, c1) = (0xc080_4020u32, 0x1357_9bdfu32);
        let store = |sb: u32, c: u32| {
            let p = pack_of(sb).unwrap();
            (pack_pixel(p, c, false), p.bytes())
        };
        // mode 8: one byte, bits 8:6 = 0 alpha, 1 red, 2 green, 3 to 7 blue
        for (f, want) in [(0, 0xc0), (1, 0x80), (2, 0x40), (3, 0x20), (7, 0x20)] {
            assert_eq!(store(0x208 | f << 6, c0), (want, 1), "mode 8 field {f}");
        }
        assert_eq!(store(0x248, c1), (0x57, 1));
        // mode 7: two bytes, 0 alpha and red, 1 to 7 green and blue
        assert_eq!(store(0x207, c0), (0xc080, 2));
        assert_eq!(store(0x207 | 5 << 6, c0), (0x4020, 2));
        assert_eq!(store(0x247, c1), (0x9bdf, 2));
        // 15, 18 and 28 (E383, bits 8:6 = 0 to 7) and 20 and 27 (E999, 0 to 3): the low 16 bits
        for (m, top) in [(15u32, 7u32), (18, 7), (28, 7), (20, 3), (27, 3)] {
            for f in 0..=top {
                assert_eq!(store(0x200 | f << 6 | m, c1), (0x9bdf, 2), "mode {m} field {f}");
            }
        }
        // 24 and 25: blue, one byte, whatever the field
        for m in [24u32, 25] {
            for f in 0..8 {
                assert_eq!(store(0x200 | f << 6 | m, c0), (0x20, 1), "mode {m} field {f}");
            }
        }
        // E031: the background 0xff203040 and the colour 0x80ff8040 in mode 8 and 7, field 0
        assert_eq!(store(0x208, A).0, 0xff);
        assert_eq!(store(0x207, B).0, 0x80ff);
    }

    #[test]
    fn the_new_modes_take_only_the_reg_0400_words_that_ran() {
        // E383, E999, E031 ran with the word 0x80; E385: bit 25 changes nothing in mode 8 (field 0)
        assert!(reg0400_known(0x20f, 0x80).is_ok());
        assert!(reg0400_known(0x208, 0x80 | 1 << 25).is_ok());
        for (sb, reg) in
            [(0x20f, 0x80 | 1 << 25), (0x207, 0x80 | 1 << 25), (0x248, 0x80 | 1 << 25), (0x218, 0x40)]
        {
            let r = reg0400_known(sb, reg);
            assert!(
                matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q044"]),
                "{sb:#x} {reg:#x}"
            );
        }
        // modes 0 to 3: no bit but 25 changes a pixel (E268)
        assert!(reg0400_known(0x200, 0x0f | 1 << 25).is_ok());
        // a store that the word does not admit stores nothing
        let e = emit([0, 31 | 15 << 16, 0x8000 | 3 << 16, 0x1000_0000], 0x20f);
        let mut m = mem_of(0x1000_0000, 512);
        assert!(store_tile(&e, 0x80 | 1 << 25, (0, 0), &[A; 512], &mut m).is_err());
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xdead_beef);
    }

    #[test]
    fn one_and_two_byte_pixels_fill_a_dword_from_its_low_byte() {
        // E383, E999 (every pixel of 130 kept images, tests/pbe_pack_images.rs): pixel x of a
        // row is at byte x * size, so the even pixel is the low half (or byte) of the dword
        let colours: Vec<u32> =
            (0..512).map(|i| if i % 2 == 1 { 0xc080_4020 } else { 0xff20_3040 }).collect();
        let mut m = mem_of(0x1000_0000, 512);
        let e = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x207);
        store_tile(&e, 0x80, (0, 0), &colours, &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xc080_ff20);
        assert_eq!(m.read32(0x1000_0000 + 64).unwrap(), 0xc080_ff20, "row 1 at the pitch of 64 bytes");
        let mut m = mem_of(0x1000_0000, 512);
        let e = emit([0, 31 | 15 << 16, 0x8000 | 3 << 16, 0x1000_0000], 0x208);
        store_tile(&e, 0x80, (0, 0), &colours, &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xc0ff_c0ff);
        assert_eq!(m.read32(0x1000_0000 + 32).unwrap(), 0xc0ff_c0ff);
    }

    fn emit(w: [u32; 4], sb: u32) -> Emit {
        Emit { words: w, sideband: sb }
    }

    fn mem_of(base: u32, dwords: usize) -> Mem {
        let mut m = Mem::new();
        m.load(base, &vec![0xdead_beef; dwords]).unwrap();
        m
    }

    #[test]
    fn a_tile_is_stored_inside_the_rectangle_only_at_the_pitch_and_address_of_the_words() {
        // rectangle x 2..=5, y 1..=2 inside tile (0, 0); pitch (0x7 + 1) * 8 = 64 bytes; bits 1:0
        // of the address are ignored
        let e = emit([2 | 1 << 16, 5 | 2 << 16, 0x8000 | 7 << 16, 0x1000_0003], 0x200);
        let colours: Vec<u32> = (0..512).map(|i| 0xff00_0000 | i).collect();
        let mut m = mem_of(0x1000_0000, 64);
        store_tile(&e, 0x80, (0, 0), &colours, &mut m).unwrap();
        let at = |x: u32, y: u32| m.read32(0x1000_0000 + 64 * y + 4 * x).unwrap();
        assert_eq!(at(2, 1), 0xff00_0000 | (32 + 2));
        assert_eq!(at(5, 2), 0xff00_0000 | (64 + 5));
        for (x, y) in [(1, 1), (6, 1), (2, 0), (2, 3)] {
            assert_eq!(at(x, y), 0xdead_beef, "({x}, {y}) is outside the rectangle");
        }
    }

    #[test]
    fn a_tile_further_along_stores_at_its_own_pixels_and_a_rgb565_pixel_takes_two_bytes() {
        let e = emit([0, 63 | 31 << 16, 0x8000 | 15 << 16, 0x2000_0000], 0x203);
        let mut m = mem_of(0x2000_0000, 64 * 32 / 2);
        store_tile(&e, 0x80, (1, 1), &vec![A; 512], &mut m).unwrap();
        // pixel (32, 16) is at 0x20000000 + 16 * 128 + 32 * 2, two pixels to a dword
        assert_eq!(m.read32(0x2000_0000 + 16 * 128 + 64).unwrap(), 0x2188_2188);
        assert_eq!(m.read32(0x2000_0000).unwrap(), 0xdead_beef, "tile (0, 0) was not stored");
    }

    #[test]
    fn count_zero_stores_nothing_an_odd_count_hangs_and_an_unmeasured_one_refuses() {
        let w2 = |count: u32| count << 8 | 7 << 16;
        let e = |c| emit([0, 31 | 15 << 16, w2(c), 0x1000_0000], 0x200);
        let mut m = mem_of(0x1000_0000, 512);
        store_tile(&e(0), 0x80, (0, 0), &[A; 512], &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xdead_beef);
        assert!(matches!(store_tile(&e(0x41), 0x80, (0, 0), &[A; 512], &mut m), Err(Outcome::Hang { .. })));
        // above 0x80 the whole tile is written with changes the record does not give (E266)
        assert!(matches!(
            store_tile(&e(0x81), 0x80, (0, 0), &[A; 512], &mut m),
            Err(Outcome::Unsupported { .. })
        ));
        assert!(matches!(
            store_tile(&e(0x40), 0x80, (0, 0), &[A; 512], &mut m),
            Err(Outcome::Unsupported { .. })
        ));
        assert!(matches!(
            store_tile(&e(0x90), 0x80, (0, 0), &[A; 512], &mut m),
            Err(Outcome::Unsupported { .. })
        ));
        // bits 6:0 and 31:28 of EMIT2 change the image (E267, E382): refused, not ignored
        let mut w = e(0x80);
        w.words[2] |= 1;
        assert!(matches!(store_tile(&w, 0x80, (0, 0), &[A; 512], &mut m), Err(Outcome::Unsupported { .. })));
        // an access past the mapped buffer is the memory's refusal, not a prediction
        let far = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x9000_0000], 0x200);
        assert!(matches!(
            store_tile(&far, 0x80, (0, 0), &[A; 512], &mut m),
            Err(Outcome::Unsupported { .. })
        ));
    }
}
