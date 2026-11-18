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
//! byte (every pixel of 139 kept images, tests/pbe_pack_images.rs). Every narrowed channel
//! truncates (RGB565 and modes 4 to 6, every byte value: E1146); at bits 8:6 = 0 mode 4 stores
//! ARGB1555, its alpha bit set where the alpha is at or above the word's low byte (E1136), mode 5
//! ARGB4444, mode 6 the alpha byte over RGB332 (E031, E1146), and the 40 ARGB8888-like modes
//! store o0 as mode 0 (E031, E1146). Modes 9, 10, 12, 13 store whole colours at a layout no record
//! gives, 14 faults, 26 stores other values (Q302), 22 and 34 are Q012's. Bit 25 of the word that
//! loads CR_REG_0400 inverts the alpha before it is packed in modes 0 to 2 and 4 to 6, so mode 4
//! thresholds the inverted alpha (E268, E1135, E1146), and nothing in the other modes; no other
//! bit of it changes a pixel in modes 0 to 3 (E268); elsewhere the words that ran are admitted
//! (E385, E1135, E1136, E1146: `reg0400_known`).

use crate::Outcome;
use crate::mem::Mem;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q012", "Q040", "Q302", "Q046", "Q074", "Q054", "Q183"];

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
    /// mode 4 at bits 8:6 = 0: the one-bit alpha by the low byte's threshold, RGB 5 bits each
    Argb1555,
    /// mode 5 at bits 8:6 = 0: four bits a channel
    Argb4444,
    /// mode 6 at bits 8:6 = 0: the alpha byte over RGB332
    A8Rgb332,
    /// the 40 ARGB8888-like modes at bits 8:6 = 0: o0 as it is, bit 25 inverting nothing (E1135)
    Argb8888Like,
}

/// The ARGB8888-like pack modes other than 0 (E031's class; E1146: every byte in every channel).
pub const ARGB8888_LIKE: [u32; 40] = [
    11, 16, 17, 19, 21, 23, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
];

impl Pack {
    pub fn bytes(self) -> u32 {
        match self {
            Pack::Rgb565
            | Pack::AlphaRed
            | Pack::Low16
            | Pack::Argb1555
            | Pack::Argb4444
            | Pack::A8Rgb332 => 2,
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
    if sideband & 0xffff_fc00 == 0x1000 && sideband & 0x3f <= 6 {
        // E383: words of no colour; E1028, E1034: no fixed image (their replicate controls failed; post
        // hoc a high half fixed pixel for pixel, a low half and a class layout that vary between runs,
        // fields that follow o0)
        return Err(Outcome::unsupported("sideband bit 12 in pack modes 0 to 6 (E1028)", &["Q046"]));
    }
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
        // E031, E1146: at bits 8:6 = 0, the only field run
        4 if field == 0 => Ok(Pack::Argb1555),
        5 if field == 0 => Ok(Pack::Argb4444),
        6 if field == 0 => Ok(Pack::A8Rgb332),
        m if field == 0 && ARGB8888_LIKE.contains(&m) => Ok(Pack::Argb8888Like),
        9 | 10 | 12 | 13 => Err(Outcome::unsupported(
            "pack modes 9, 10, 12 and 13 store whole colours at a layout no record gives (E1146)",
            &["Q302"],
        )),
        22 | 34 => Err(Outcome::unsupported("pack modes 22 and 34 read o0 as a float", &["Q012"])),
        m => Err(Outcome::unsupported(
            &format!("pack mode {m} at sideband bits 8:6 = {field} is not modelled"),
            &["Q302"],
        )),
    }
}

/// Whether the records give the image for the word that loads CR_REG_0400 in this sideband's
/// mode: in modes 0 to 3 no bit but 25 changes a pixel (E268); the one- and two-channel modes
/// ran with the word 0x80 (E031, E383, E999) and, at bits 8:6 = 0, with these, none of which
/// changed a pixel: bit 25 in modes 7, 8, 15, 18, 20, 24, 25, 27 and 28 (E385, E1135), the low
/// bytes 0x00, 0x40, 0xc0, 0xff and 0xf80 in 7 and 8 (E1136), 0xf80 in 15, 20, 24 and 27 (E1136).
/// Modes 4 to 6: 0x80 and bit 25 (E1135), bit 25 with the low bytes 0x40 and 0xc0 (E1146), the low
/// bytes 0x00, 0x40, 0xc0, 0xff and 0xf80 in 5 and 6 (E1136), in mode 4 E385's and E1136's low
/// bytes and E385's bits 8 to 11 one at a time; the ARGB8888-like modes 0x80 and bit 25 (E1135),
/// mode 11 0x40, 0xc0 and 0xf80 too (E1136). Any other word, or another field, did not run.
pub fn reg0400_known(sideband: u32, reg: u32) -> Result<(), Outcome> {
    const B25: u32 = 0x80 | 1 << 25;
    const R3: [u32; 2] = [0x0200_0040, 0x0200_00c0];
    const M4: [u32; 17] = [
        0x00, 0x02, 0x08, 0x3e, 0x40, 0x42, 0x78, 0x84, 0xbc, 0xc0, 0xc4, 0xfc, 0xff, 0x180, 0x280, 0x480,
        0x880,
    ];
    let field0 = sideband >> 6 & 7 == 0;
    let ok = match sideband & 0x3f {
        0..=3 => true,
        4 if field0 => reg == 0x80 || reg == B25 || R3.contains(&reg) || M4.contains(&reg),
        5 | 6 if field0 => matches!(reg, 0x80 | B25 | 0x00 | 0x40 | 0xc0 | 0xff | 0xf80) || R3.contains(&reg),
        11 if field0 => matches!(reg, 0x80 | B25 | 0x40 | 0xc0 | 0xf80),
        m if field0 && ARGB8888_LIKE.contains(&m) => matches!(reg, 0x80 | B25),
        7 | 8 if field0 => matches!(reg, 0x80 | B25 | 0x00 | 0x40 | 0xc0 | 0xff | 0xf80),
        15 | 20 | 24 | 27 if field0 => matches!(reg, 0x80 | B25 | 0xf80),
        18 | 25 | 28 if field0 => matches!(reg, 0x80 | B25),
        _ => reg == 0x80,
    };
    if ok {
        Ok(())
    } else {
        Err(Outcome::unsupported(
            &format!("the CR_REG_0400 word {reg:#x} in pack mode {} did not run", sideband & 0x3f),
            &["Q302"],
        ))
    }
}

/// The value stored for a shader colour `o0` (0xAARRGGBB as the shader writes it) under the word
/// 0x80, or 0x80 with bit 25 when `invert_alpha` (E268): `pack_pixel_word` with that word.
pub fn pack_pixel(p: Pack, o0: u32, invert_alpha: bool) -> u32 {
    pack_pixel_word(p, o0, 0x80 | (invert_alpha as u32) << 25)
}

/// The value stored for a shader colour `o0` under the CR_REG_0400 word `reg`: bit 25 inverts the
/// alpha before it is packed (E268, E1135, E1146), bits 7:0 are mode 4's alpha threshold (E1136).
pub fn pack_pixel_word(p: Pack, o0: u32, reg: u32) -> u32 {
    // E268: modes 0 to 2; E1135, E1146: modes 4 to 6, mode 4's threshold then taking the inverted
    // alpha; E385, E1135: mode 8 (alpha at bits 8:6 = 0), mode 7 (alpha and red) and the
    // ARGB8888-like modes unchanged, as every one- and two-channel mode the bit ran in
    let inverts = matches!(
        p,
        Pack::Argb8888 | Pack::Abgr8888 | Pack::Bgra8888 | Pack::Argb1555 | Pack::Argb4444 | Pack::A8Rgb332
    );
    let o0 = if reg >> 25 & 1 != 0 && inverts { o0 ^ 0xff00_0000 } else { o0 };
    let (a, r, g, b) = (o0 >> 24, o0 >> 16 & 0xff, o0 >> 8 & 0xff, o0 & 0xff);
    match p {
        Pack::Argb8888 => o0,
        Pack::Abgr8888 => a << 24 | b << 16 | g << 8 | r,
        Pack::Bgra8888 => b << 24 | g << 16 | r << 8 | a,
        // the low bits of each channel dropped (E031; every byte value of every channel, E1146)
        Pack::Rgb565 => r >> 3 << 11 | g >> 2 << 5 | b >> 3,
        Pack::Argb1555 => ((a >= (reg & 0xff)) as u32) << 15 | r >> 3 << 10 | g >> 3 << 5 | b >> 3,
        Pack::Argb4444 => a >> 4 << 12 | r >> 4 << 8 | g >> 4 << 4 | b >> 4,
        Pack::A8Rgb332 => a << 8 | r >> 5 << 5 | g >> 5 << 2 | b >> 6,
        Pack::Argb8888Like => o0,
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
    for (i, &c) in colours.iter().enumerate().take(512) {
        let (x, y) = (32 * tile.0 + i as u32 % 32, 16 * tile.1 + i as u32 / 32);
        if x < x0 || x > x1 || y < y0 || y > y1 {
            continue;
        }
        let v = pack_pixel_word(pack, c, reg0400);
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
    fn rgb565_truncates_every_channel() {
        // E1146: r35-pk's ramp, every byte value in every channel, stored v >> 3, v >> 2, v >> 3
        // (H-RZ on every pixel of two rows; round half up, half to even and scaling refuted)
        let p = pack_of(0x203).unwrap();
        for v in 0..256u32 {
            let want = v >> 3 << 11 | v >> 2 << 5 | v >> 3;
            assert_eq!(pack_pixel(p, 0xff00_0000 | v << 16 | v << 8 | v, false), want, "{v:#x}");
        }
        // 0x7f stores 15 (truncated), where rounding would give 16
        assert_eq!(pack_pixel(p, 0xff7f_0000, false), 15 << 11);
        let mut m = mem_of(0x1000_0000, 512);
        let e = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x203);
        store_tile(&e, 0x80, (0, 0), &[0xff7f_0300; 512], &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0x7800_7800);
    }

    #[test]
    fn modes_4_to_6_truncate_and_bit_25_inverts_the_alpha_before_mode_4s_threshold() {
        let p = |sb| pack_of(sb).unwrap();
        // E031's two colours (and E1146's ramp: H-RZ on every pixel of modes 4, 5 and 6)
        for (sb, a, b) in [(0x204, 0x90c8, 0xfe08), (0x205, 0xf234, 0x8f84), (0x206, 0xff25, 0x80f1)] {
            assert_eq!((pack_pixel(p(sb), A, false), pack_pixel(p(sb), B, false)), (a, b), "{sb:#x}");
            assert_eq!(p(sb).bytes(), 2);
        }
        // channels truncate: 0x7f in four bits is 7, in three 3, in two (blue of mode 6) 1
        assert_eq!(pack_pixel(p(0x205), 0x7f7f_7f7f, false), 0x7777);
        assert_eq!(pack_pixel(p(0x206), 0x007f_7f7f, false), 3 << 5 | 3 << 2 | 1);
        // E1136: mode 4's alpha bit is set at or above the low byte
        assert_eq!(pack_pixel_word(p(0x204), 0x7f00_0000, 0x80) >> 15, 0);
        assert_eq!(pack_pixel_word(p(0x204), 0x8000_0000, 0x80) >> 15, 1);
        assert_eq!(pack_pixel_word(p(0x204), 0x0200_0000, 0x02) >> 15, 1);
        // E1146: with bit 25 the threshold takes the inverted alpha (255 - a >= the low byte): at
        // 0x40 set for alpha 0 to 191, at 0xc0 for 0 to 63; at 0x80 the same as inverting the bit
        for (reg, last_set) in [(0x0200_0040u32, 191u32), (0x0200_00c0, 63), (0x0200_0080, 127)] {
            for a in 0..256u32 {
                let bit = pack_pixel_word(p(0x204), a << 24, reg) >> 15;
                assert_eq!(bit, (a <= last_set) as u32, "{reg:#x} alpha {a}");
            }
        }
        // E1135, E1146: bit 25 inverts mode 5's alpha nibble and mode 6's alpha byte, whatever
        // the low byte
        for reg in [0x0200_0080u32, 0x0200_0040, 0x0200_00c0] {
            assert_eq!(pack_pixel_word(p(0x205), B, reg), 0x8f84 ^ 0xf000);
            assert_eq!(pack_pixel_word(p(0x206), B, reg), 0x80f1 ^ 0xff00);
        }
        // the other fields of modes 4 to 6 did not run
        assert!(pack_of(0x244).is_err() && pack_of(0x245).is_err() && pack_of(0x246).is_err());
    }

    #[test]
    fn the_argb8888_like_modes_store_o0_and_bit_25_changes_nothing() {
        // E031 (two colours), E1146 (every byte in every channel, 40 of 40 modes): mode 0's image;
        // E1135: bit 25 changes nothing in them
        let like =
            [11u32, 16, 17, 19, 21, 23, 29, 30, 31, 32, 33].into_iter().chain(35..64).collect::<Vec<_>>();
        assert_eq!(like.len(), 40);
        for m in like {
            let p = pack_of(0x200 | m).unwrap();
            assert_eq!(p.bytes(), 4);
            assert_eq!(pack_pixel(p, B, false), B, "mode {m}");
            assert_eq!(pack_pixel(p, B, true), B, "mode {m}");
            assert!(reg0400_known(0x200 | m, 0x80 | 1 << 25).is_ok(), "mode {m}");
            assert!(pack_of(0x240 | m).is_err(), "mode {m}: field 1 did not run");
        }
        // E1136: the low bytes 0x40, 0xc0 and 0xf80 change nothing in mode 11
        for reg in [0x40u32, 0xc0, 0xf80] {
            assert!(reg0400_known(0x20b, reg).is_ok());
            assert!(reg0400_known(0x210, reg).is_err(), "mode 16 ran 0x80 and bit 25 only");
        }
    }

    #[test]
    fn modes_9_10_12_13_store_whole_colours_at_a_layout_no_record_gives() {
        // E031, E1146: whole 32-bit colours, a quarter or half of the target, 12 and 13 past it
        for m in [9u32, 10, 12, 13] {
            match pack_of(0x200 | m) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q302"]);
                    assert!(why.contains("layout"), "{why}");
                }
                o => panic!("mode {m}: {o:?}"),
            }
        }
    }

    #[test]
    fn the_words_r35_pk_ran_are_known_in_modes_0_and_4_to_6() {
        for m in [0u32, 4, 5, 6] {
            for reg in [0x0200_0040u32, 0x0200_00c0] {
                assert!(reg0400_known(0x200 | m, reg).is_ok(), "mode {m} {reg:#x}");
            }
        }
        // E1136, E385: mode 4's low bytes that ran; another did not
        for reg in [0x02u32, 0x08, 0x3e, 0x42, 0x78, 0x84, 0xbc, 0xc4, 0xfc, 0x00, 0x40, 0xc0, 0xff, 0x880] {
            assert!(reg0400_known(0x204, reg).is_ok(), "{reg:#x}");
        }
        assert!(reg0400_known(0x204, 0x41).is_err());
        assert!(reg0400_known(0x204, 0x0200_0041).is_err());
        assert!(reg0400_known(0x205, 0x84).is_err(), "mode 5 ran 0x00, 0x40, 0xc0, 0xff, 0xf80");
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
        assert_eq!(ids(0x209), ["Q302"]);
        assert_eq!(ids(0x21a), ["Q302"], "mode 26 (E032)");
        // modes 20 and 27 ran at bits 8:6 = 0 to 3 only (E999)
        for m in [20u32, 27] {
            assert_eq!(ids(0x200 | 4 << 6 | m), ["Q302"], "mode {m}");
        }
        assert_eq!(ids(0x003), ["Q074"]);
        assert_eq!(ids(0x600), ["Q046"]);
        // bits 8:6 change no pixel in modes 0 to 3 (E030, E383)
        assert!(pack_of(0x200 | 7 << 6).is_ok());
    }

    #[test]
    fn sideband_bit_12_has_no_model() {
        // E1028: bit 12's words in modes 0 to 6 are no fixed image (its replicate control failed;
        // post hoc a per-pixel class layout that moves between sessions, fields that follow o0)
        for m in 0..7u32 {
            match pack_of(0x1200 | m) {
                Err(Outcome::Unsupported { why, ids }) => {
                    assert_eq!(ids, ["Q046"], "mode {m}");
                    assert!(why.contains("E1028"), "{why}");
                }
                o => panic!("mode {m}: {o:?}"),
            }
        }
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
        // what no record ran: another field, a low byte or bits 11:8 where only bit 25 ran, a
        // low byte with bit 25
        for (sb, reg) in [
            (0x247, 0x80 | 1 << 25),
            (0x248, 0x80 | 1 << 25),
            (0x218, 0x40),
            (0x20f, 0x40),
            (0x212, 0xf80),
            (0x208, 0x40 | 1 << 25),
        ] {
            let r = reg0400_known(sb, reg);
            assert!(
                matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q302"]),
                "{sb:#x} {reg:#x}"
            );
        }
        // modes 0 to 3: no bit but 25 changes a pixel (E268)
        assert!(reg0400_known(0x200, 0x0f | 1 << 25).is_ok());
        // a store that the word does not admit stores nothing
        let e = emit([0, 31 | 15 << 16, 0x8000 | 3 << 16, 0x1000_0000], 0x20f);
        let mut m = mem_of(0x1000_0000, 512);
        assert!(store_tile(&e, 0x40, (0, 0), &[A; 512], &mut m).is_err());
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0xdead_beef);
    }

    #[test]
    fn the_words_r34_q044_ran_are_known_in_the_modes_it_ran_them() {
        // E1135: bit 25 changes nothing in modes 7 (alpha and red) and 8 (alpha) at bits 8:6 = 0,
        // 15, 18, 20, 24, 25, 27, 28; E1136: the low bytes 0x00, 0x40, 0xc0, 0xff and 0xf80 change
        // nothing in modes 7 and 8, 0xf80 nothing in 15, 20, 24, 27
        let b25 = 0x80 | 1 << 25;
        for m in [7u32, 8] {
            for reg in [0x80, b25, 0x00, 0x40, 0xc0, 0xff, 0xf80] {
                assert!(reg0400_known(0x200 | m, reg).is_ok(), "mode {m} {reg:#x}");
            }
        }
        for m in [15u32, 20, 24, 27] {
            for reg in [0x80, b25, 0xf80] {
                assert!(reg0400_known(0x200 | m, reg).is_ok(), "mode {m} {reg:#x}");
            }
        }
        for m in [18u32, 25, 28] {
            assert!(reg0400_known(0x200 | m, b25).is_ok(), "mode {m}");
        }
        // bit 25 leaves mode 7's alpha as the shader wrote it (0x80ff8040 -> 0x80ff, E1135)
        assert_eq!(pack_pixel(pack_of(0x207).unwrap(), 0x80ff_8040, true), 0x80ff);
        let e = emit([0, 31 | 15 << 16, 0x8000 | 7 << 16, 0x1000_0000], 0x207);
        let mut m = mem_of(0x1000_0000, 512);
        store_tile(&e, b25, (0, 0), &[B; 512], &mut m).unwrap();
        assert_eq!(m.read32(0x1000_0000).unwrap(), 0x80ff_80ff);
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
