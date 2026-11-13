// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! ZLS: the depth/stencil store and load (12.4). The address rule (E465, E489), the control word
//! (E411, E337), the stored depth formats 0 to 2 and the negation (E466, E490), the load by bits 1,
//! 13 and 14 with the sign cleared (E467), the pass over a loaded buffer and the band of an edge
//! tile (E730, E831, E885, E903). What no record states refuses by question: formats 3 to 7 (Q120),
//! the stencil's in-tile order and its edge tiles (Q121), the
//! overflowed job's store (Q107), the integer formats' values outside 0 to 1 (E977) and at an
//! edge of an odd size (E991 ran 80 x 40), overlapping tiles and the pitches past the scratch
//! buffer (Q242), a load of an integer format or a loaded depth the compare cannot decide
//! (Q243: E977 read an integer format's load as the dword's float, two rows only), the load and the
//! pass over edge tiles (Q243), bit 0 beyond the one control it ran on and the control bits no run explained (Q071),
//! bit 19 with an integer format or a load (Q101). Every refusal depends on the input alone.

use crate::Outcome;

/// Open questions that block the rest of the unit.
/// The status of the address rule (rules.rs).
pub const STORE_STATUS: crate::rules::Status = crate::rules::ZLS_ADDRESS;

pub const OPEN: &[&str] = &["Q071", "Q107", "Q120", "Q121", "Q242", "Q243"];

pub fn refuse() -> Outcome {
    Outcome::unsupported("zls: this input is not one a record states (12.4)", OPEN)
}

fn open(why: String, ids: &[&str]) -> Outcome {
    Outcome::unsupported(&why, ids)
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

/// Whether pixel (x, y) of a W x H target's tiles lies in the band the store keeps the depth of
/// the tile pass in: x + 0.5 < 1.25 W and y + 0.5 < 1.25 H (rule A, E730, held out at even sizes
/// in E831, at odd heights in E885 and at odd widths in E903, where FLOOR, x < floor(1.25 W), is
/// one column short); past it, in the target's tiles, the store holds the background depth 1.0.
/// W and H are the viewport's (E903's poke twins: with the viewport's x scale poked to 9.5 at W 20
/// the band was W 19's, with CR_MTE_SCREEN poked it stayed W 20's); the tool sets them to the
/// target's.
pub fn in_band(x: u32, y: u32, w: u32, h: u32) -> bool {
    u64::from(x) * 4 + 2 < u64::from(w) * 5 && u64::from(y) * 4 + 2 < u64::from(h) * 5
}

/// What `check_store` found in a pair of stored depth dumps.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct StoreCheck {
    /// dwords that left the fill
    pub stored: u64,
    /// decode to a pixel whose rule address is the dword's own
    pub at_rule: u64,
    /// at the rule's address, for a pixel past the target (x >= W or y >= H) inside the band
    /// ([`in_band`], E831): the depth of the tile pass, as the band says
    pub at_rule_outside: u64,
    /// the background depth 1.0 in both ramps, in a tile of the target, at a pixel past the band
    /// (E831)
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
            if !in_grid {
                c.background_tiles += 1;
            } else if !in_band(32 * tx + ix, 16 * ty + iy, w, h) {
                c.background_outside += 1;
            } else {
                c.other += 1;
            }
        } else if vx == 0 && vy == 0 {
            c.zero += 1;
        } else if let (Some(px), Some(py)) = (decode_ramp(vx, w), decode_ramp(vy, h))
            && store_dword(px, py, g) as usize == i
            && (px < w && py < h || in_band(px, py, w, h))
        {
            if px < w && py < h {
                c.at_rule += 1;
            } else {
                c.at_rule_outside += 1;
            }
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

// ---- 12.4: the control word, the stored formats, the load -------------------------------------

/// Bits of CR_ISP_ZLSCTL whose single flip changed nothing in E411 (12, 15, 16, 20 to 23, 27 to
/// 31; 13 and 14 act only with bit 1, which the decoding below says). Set together with others
/// they were not run, but the closed driver sets 12, 16 and 20 in every value (E337).
/// The control 0x0017100c with bit 0 set: the one value E411 ran with bit 0 (twice).
pub const BIT0_RAN: u32 = 0x0017_100d;

const CTL_NO_EFFECT: u32 = 1 << 12 | 1 << 15 | 1 << 16 | 0xf << 20 | 0x1f << 27;

/// CR_ISP_ZLSCTL as the records read it (E411, E465, E466, E467): G (bits 11:3, the tile pitch),
/// bit 1 the load on, 14 the depth and 13 the stencil it loads, bit 2 the stores on with 18 the
/// depth's and 17 the stencil's, bit 19 the negated float, bits 26:24 the stored depth format.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Ctl {
    pub word: u32,
}

impl Ctl {
    /// Decode a control word. Bit 0 set writes no colour pixel (E057, E411) and stores what the
    /// control stores, seen in two runs of 0x0017100d (E411, control-bits); with any other
    /// control the store under bit 0 was not seen: refused (Q071).
    pub fn decode(word: u32) -> Result<Ctl, Outcome> {
        if word & 1 != 0 && word != BIT0_RAN {
            return Err(open(
                format!(
                    "CR_ISP_ZLSCTL {word:#x}: with bit 0 the colour image is not written (E057), and \
                     the depth and stencil store was seen only for {BIT0_RAN:#x} (E411)"
                ),
                &["Q071"],
            ));
        }
        Ok(Ctl { word })
    }

    /// False with bit 0 set: every pixel of the target kept its sentinel (E057, E411).
    pub fn writes_pixels(&self) -> bool {
        !self.bit(0)
    }

    fn bit(&self, b: u32) -> bool {
        self.word >> b & 1 != 0
    }

    pub fn g(&self) -> u32 {
        self.word >> 3 & 0x1ff
    }
    pub fn load(&self) -> bool {
        self.bit(1)
    }
    pub fn load_depth(&self) -> bool {
        self.bit(1) && self.bit(14)
    }
    pub fn load_stencil(&self) -> bool {
        self.bit(1) && self.bit(13)
    }
    pub fn store_depth(&self) -> bool {
        self.bit(2) && self.bit(18)
    }
    pub fn store_stencil(&self) -> bool {
        self.bit(2) && self.bit(17)
    }
    pub fn negate(&self) -> bool {
        self.bit(19)
    }
    pub fn format_code(&self) -> u32 {
        self.word >> 24 & 7
    }
    /// The bits no record gives a meaning to and a flip showed nothing for (ignored, E411).
    pub fn ignored_bits(&self) -> u32 {
        self.word & CTL_NO_EFFECT
    }

    pub fn format(&self) -> Result<Format, Outcome> {
        match self.format_code() {
            0 => Ok(Format::F32),
            1 => Ok(Format::U24),
            2 => Ok(Format::U16),
            // E985 read the layouts of 3 to 6 from E978's kept dumps with a loaded stencil, fitted at
            // 64 x 32 and checked at 96 x 48 (SEMI): no run held them out
            c @ 3..=6 => Err(open(
                format!(
                    "stored depth format {c}: its layout was read offline at two sizes only (E985, SEMI; E466, E490, \
                     E978)"
                ),
                &["Q120"],
            )),
            c => Err(open(
                format!("stored depth format {c}: its layout was not decoded (E466, E490, E978, E985)"),
                &["Q120"],
            )),
        }
    }
}

/// The stored depth formats of E466 that a record decodes.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Format {
    /// the float32, 512 dwords a tile
    F32,
    /// min(floor(z * 2^24), 0xffffff), 512 dwords a tile (E977)
    U24,
    /// the 24-bit value >> 8, two rows a dword, 256 dwords a tile (E490's layout, E977)
    U16,
}

/// The status of the integer formats' value rules: held out as frozen in E977 (measured).
pub const INT_FORMAT_STATUS: crate::rules::Status = crate::rules::ZLS_INT_FORMATS;

/// The depths E490's ramps hold: 0.25 + 0.5 (p + 0.5) / (3 size) for p < size spans 0.250081 to
/// 0.416585 (the x ramp of 1024); the load pass's triangles ran there.
pub const RAMP_DEPTH: std::ops::RangeInclusive<f32> = 0.25..=0.4166;

/// The integer formats' depths that ran: 0 to 1 (E977's two ramps at three pitches; E490's
/// ramp and E411's clear value inside it).
pub const INT_DEPTH: std::ops::RangeInclusive<f32> = 0.0..=1.0;

/// The depths bit 19 ran over with an integer format: E490's ramp and E981's 0 to 0.3 (and the 0
/// a negative depth reaches the store as), where it changed no dword.
pub const NEGATE_INT_DEPTH: std::ops::RangeInclusive<f32> = 0.0..=0.4166;

/// The dword a pixel's depth `z` is stored as in `fmt` (the 16-bit value in the low half for
/// U16; the packing of two rows is [`store`]'s). Bit 19 negates the float (E490: 786432 of
/// 786432); with an integer format it changed no dword over 0 to 0.4166 (E490, E981) and any
/// other depth refuses (Q101). The 24-bit value is min(floor(z * 2^24), 0xffffff) and the 16-bit
/// one its >> 8 (E977: held out over 0 to 1 at three pitches; round(z * 0xffffff), E466's fit,
/// failed from 0.5 up and agreed below where E466's dumps lay); a depth outside 0 to 1 refuses
/// (Q242). A negative depth made after the clip reached the store as 0.0 in every format (E981),
/// which the caller's depth already is.
pub fn encode_depth(fmt: Format, negate: bool, z: f32) -> Result<u32, Outcome> {
    match fmt {
        Format::F32 => Ok(z.to_bits() ^ u32::from(negate) << 31),
        Format::U24 | Format::U16 => {
            if !INT_DEPTH.contains(&z) {
                return Err(open(
                    format!("depth {z} in an integer format: only 0 to 1 ran (E977)"),
                    &["Q242"],
                ));
            }
            if negate && !NEGATE_INT_DEPTH.contains(&z) {
                return Err(open(
                    format!("bit 19 with an integer format and depth {z}: only 0 to 0.4166 ran (E490, E981)"),
                    &["Q101"],
                ));
            }
            let v = ((z as f64 * 16777216.0).floor() as u32).min(0x00ff_ffff);
            Ok(if fmt == Format::U16 { v >> 8 } else { v })
        }
    }
}

/// The dword inside a 256-dword slot of the 16-bit format: x0 y1 x1 y2 x2 y3 x3 x4 from the
/// lowest bit; the row's low bit y0 chooses the half of the dword (E490, from the dumps, G = 33).
pub fn in_tile_index16(x: u32, y: u32) -> u32 {
    let (x, y) = (x & 31, y & 15);
    let mut k = 0;
    for b in 0..4 {
        k |= (x >> b & 1) << (2 * b);
        if b < 3 {
            k |= (y >> (b + 1) & 1) << (2 * b + 1);
        }
    }
    k | (x >> 4 & 1) << 7
}

/// The dwords a depth store writes, by dword index of the buffer.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct Stored {
    pub words: std::collections::BTreeMap<u32, u32>,
}

type Dwords = std::collections::BTreeSet<u32>;

fn has_edge(w: u32, h: u32) -> bool {
    !w.is_multiple_of(32) || !h.is_multiple_of(16)
}

/// A target with edge tiles stores by the band (E831) at even sizes, odd heights (E885) and odd
/// widths (E903), in the float format. An integer format stores the floor rule of the float the
/// same pixel stores, inside the target (E977) and past it (E991), both at 80 x 40 only: an
/// integer format at an odd width or height refuses (Q242).
fn edge_store(ctl: &Ctl, w: u32, h: u32) -> Result<(), Outcome> {
    if has_edge(w, h) && ctl.format_code() != 0 && (w % 2 == 1 || h % 2 == 1) {
        return Err(open(
            format!("a {w} x {h} target in an integer format: its edge tiles ran at an even size only"),
            &["Q242"],
        ));
    }
    Ok(())
}

/// Tiles of a row that share a dword with the next row's: a pitch G + 1 below the tiles a row
/// needs. E465 counted the dwords written there and nothing says which pixel a shared dword
/// holds.
fn no_overlap(w: u32, g: u32) -> Result<(), Outcome> {
    if g + 1 < w.div_ceil(32) {
        return Err(open(
            format!(
                "pitch {} tiles under the {} a row of {w} pixels needs: tiles overlap, which pixel a shared dword holds was not measured",
                g + 1,
                w.div_ceil(32)
            ),
            &["Q242"],
        ));
    }
    Ok(())
}

/// The dwords of the depth buffer a store writes, for counting: overlapping tiles allowed (E465
/// counted them), values not given.
fn depth_dwords(ctl: &Ctl, w: u32, h: u32, stencil_buffer: bool) -> Result<Dwords, Outcome> {
    let mut d = Dwords::new();
    if !ctl.store_depth() || matches!(ctl.format_code(), 4 | 7) && !stencil_buffer {
        return Ok(d);
    }
    let fmt = ctl.format()?;
    edge_store(ctl, w, h)?;
    let g = ctl.g();
    // every dword of the target's tiles (E831: the band's pixels and the background past it)
    let (tw, th) = (32 * w.div_ceil(32), 16 * h.div_ceil(16));
    match fmt {
        Format::F32 | Format::U24 => {
            for y in 0..th {
                for x in 0..tw {
                    d.insert(store_dword(x, y, g));
                }
            }
        }
        Format::U16 => {
            // E490's layout, derived at G = 33, held out at G 7, 9 and 2 (E977), every row pair
            // of the tiles past an edge too (E991)
            for y in (0..th).step_by(2) {
                for x in 0..tw {
                    d.insert(256 * ((y >> 4) * (g + 1) + (x >> 5)) + in_tile_index16(x, y));
                }
            }
        }
    }
    Ok(d)
}

/// The dwords of the stencil buffer a store writes: 128 a tile slot (Q121: the in-tile order is
/// not modelled, nor what an edge tile stores; E985 read byte j of a tile as the depth's in-tile
/// index j on the lane-0 bytes only, offline and SEMI).
fn stencil_dwords(ctl: &Ctl, w: u32, h: u32) -> Result<Dwords, Outcome> {
    let mut d = Dwords::new();
    if !ctl.store_stencil() {
        return Ok(d);
    }
    if has_edge(w, h) {
        return Err(open(
            format!("the stencil store of a {w} x {h} target: edge tiles were not measured"),
            &["Q121"],
        ));
    }
    for ty in 0..h / 16 {
        for tx in 0..w / 32 {
            d.extend((0..128).map(|j| 128 * (ty * (ctl.g() + 1) + tx) + j));
        }
    }
    Ok(d)
}

/// The dwords a store of a W x H target through `ctl` writes into the depth buffer and into the
/// stencil buffer, as counts of E411's flips and E465's overlap cases use them (no values):
/// the same refusals as [`store`] except for overlapping tiles. `stencil_buffer` is whether
/// the target has one (formats 4 and 7 store nothing without, E490).
pub fn dword_sets(ctl: &Ctl, w: u32, h: u32, stencil_buffer: bool) -> Result<(Dwords, Dwords), Outcome> {
    Ok((depth_dwords(ctl, w, h, stencil_buffer)?, stencil_dwords(ctl, w, h)?))
}

/// E411's scratch runs (a 16-page buffer, a 64 x 64 target): G of 0, 1 and 3 stored and G with
/// any of bits 2 to 8 set (bits 5 to 11 of the control) faulted the job; that the store's extent
/// ran past the buffer is [infer] (E991: G 3 stored past it without a fault). Refuses the faulted pitches in that arrangement (Q242); the same
/// pitches in a large buffer ran (E490 at G = 33), so this is a check of the arrangement, not of
/// the word.
pub fn check_scratch_pitch(ctl: &Ctl) -> Result<(), Outcome> {
    if ctl.g() > 3 {
        return Err(open(
            format!("G = {} in the 16-page scratch run: E411's jobs with bits 5 to 11 set faulted", ctl.g()),
            &["Q242"],
        ));
    }
    Ok(())
}

/// The depth store of a W x H target for the control `ctl`: `depth(x, y)` is the depth the tile
/// pass left at the pixel (a measured input, or the plane's: the caller says which). Nothing is
/// stored with the stores off (E411, E466: bit 2 or bit 18 clear), nor in formats 4 and 7 without a
/// stencil buffer (E466, E490: 0 dwords); the other formats of E466 refuse (Q120: E978 counted
/// their dwords with a loaded stencil, none decoded); overlapping tiles
/// refuse (Q242: [`dword_sets`] counts those). A target with edge tiles stores every dword of
/// its tiles: `depth` inside the band ([`in_band`]), the background 1.0 past it (E831, E885,
/// E903), in the float format, and in the integer formats at an even width and height (E977,
/// E991; odd sizes refuse, Q242).
pub fn store(
    ctl: &Ctl,
    w: u32,
    h: u32,
    stencil_buffer: bool,
    depth: &dyn Fn(u32, u32) -> f32,
) -> Result<Stored, Outcome> {
    let mut s = Stored::default();
    let wanted = depth_dwords(ctl, w, h, stencil_buffer)?;
    if wanted.is_empty() {
        return Ok(s);
    }
    no_overlap(w, ctl.g())?;
    let (fmt, g) = (ctl.format()?, ctl.g());
    let banded = |x: u32, y: u32| if in_band(x, y, w, h) { depth(x, y) } else { 1.0 };
    match fmt {
        Format::F32 | Format::U24 => {
            for y in 0..16 * h.div_ceil(16) {
                for x in 0..32 * w.div_ceil(32) {
                    s.words.insert(store_dword(x, y, g), encode_depth(fmt, ctl.negate(), banded(x, y))?);
                }
            }
        }
        Format::U16 => {
            for y in (0..16 * h.div_ceil(16)).step_by(2) {
                for x in 0..32 * w.div_ceil(32) {
                    let (lo, hi) = (
                        encode_depth(fmt, ctl.negate(), banded(x, y))?,
                        encode_depth(fmt, ctl.negate(), banded(x, y + 1))?,
                    );
                    let slot = (y >> 4) * (g + 1) + (x >> 5);
                    s.words.insert(256 * slot + in_tile_index16(x, y), lo | hi << 16);
                }
            }
        }
    }
    Ok(s)
}

/// The sign bit of a loaded depth is cleared: 0xdeadbeef reads 0x5eadbeef, 0x80000000 reads 0
/// (E467; a mask or an absolute value, which the data cannot tell).
pub fn load_word(v: u32) -> u32 {
    v & 0x7fff_ffff
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Test {
    Never,
    Less,
}

/// What a pass over a loaded buffer stored.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct Pass {
    pub depth: std::collections::BTreeMap<u32, u32>,
    pub stencil: std::collections::BTreeMap<u32, u32>,
    /// covered pixels that passed the depth test
    pub drawn: u64,
}

/// A W x H target (whole tiles) drawn with a flat plane of depth `z` over the pixels `covers`
/// says, depth test `test`, from the buffers' loaded dwords (`load_depth(i)` and `load_stencil(i)`
/// read dword i of the load buffers, the address the store writes: E467) and the clear depth.
/// Without bits 1 and 14 the pass starts from the clear value, with them from the loaded depth
/// with its sign cleared; the stencil store copies the loaded dword or stores 0 per 128-dword
/// tile slot (E466, E467: the copy is by dword, not by pixel: Q121). Float format only (Q243: a load
/// of formats 1 and 2 compared the dword as a float in E977's two rows, not modelled); a
/// compare closer than the planes' tolerance refuses (Q200: 12.3's rule), a compare against a
/// loaded NaN or infinity refuses (Q243: E977's six rows order NaN above every finite depth, one
/// size, not modelled), a triangle depth other than 0.5 and the ramp's refuses
/// (Q242), bit 19 with a load refuses (Q101) and so do edge tiles (Q243: E831's band is the
/// store's without a load) and overlapping tiles (Q242).
#[allow(clippy::too_many_arguments)]
pub fn pass(
    ctl: &Ctl,
    w: u32,
    h: u32,
    clear: f32,
    z: f32,
    test: Test,
    covers: &dyn Fn(u32, u32) -> bool,
    load_depth: &dyn Fn(u32) -> u32,
    load_stencil: &dyn Fn(u32) -> u32,
) -> Result<Pass, Outcome> {
    if has_edge(w, h) {
        return Err(open(
            format!("a pass over a {w} x {h} target: the load and the pass ran on whole tiles"),
            &["Q243"],
        ));
    }
    no_overlap(w, ctl.g())?;
    if !(z == 0.5 || RAMP_DEPTH.contains(&z)) {
        return Err(open(format!("a triangle at depth {z}: only 0.5 and 0.25 to 0.4166 ran"), &["Q242"]));
    }
    if ctl.negate() && ctl.load() {
        return Err(open(
            "bit 19 with a load: the loaded sign is cleared and re-negated, not run".into(),
            &["Q101"],
        ));
    }
    let mut out = Pass::default();
    let g = ctl.g();
    if ctl.store_depth() {
        if ctl.format()? != Format::F32 {
            return Err(open("a loaded or stored integer depth format was not run".into(), &["Q243"]));
        }
        for y in 0..h {
            for x in 0..w {
                let i = store_dword(x, y, g);
                let base = if ctl.load_depth() { load_word(load_depth(i)) } else { clear.to_bits() };
                let mut v = base;
                if covers(x, y) && test == Test::Less {
                    let b = f32::from_bits(base);
                    if !b.is_finite() {
                        return Err(open(format!("a compare against the loaded {base:#x}"), &["Q243"]));
                    }
                    let d = z as f64 - b as f64;
                    if d.abs() <= f64::from(crate::isp::DEPTH_TOLERANCE) * crate::isp::DEPTH_UNIT {
                        return Err(open(
                            format!("pixel ({x}, {y}): depths within the planes' tolerance"),
                            &["Q200"],
                        ));
                    }
                    if d < 0.0 {
                        v = z.to_bits();
                        out.drawn += 1;
                    }
                }
                out.depth.insert(i, v ^ u32::from(ctl.negate()) << 31);
            }
        }
    }
    if ctl.store_stencil() {
        let (tw, th) = (w / 32, h / 16);
        for ty in 0..th {
            for tx in 0..tw {
                let slot = ty * (g + 1) + tx;
                for j in 0..128 {
                    let i = 128 * slot + j;
                    out.stencil.insert(i, if ctl.load_stencil() { load_stencil(i) } else { 0 });
                }
            }
        }
    }
    Ok(out)
}

/// The dwords of one run's dump that left the fill and are not in what the model stored.
pub fn unexplained(dump: &[u32], stored: &Stored) -> u64 {
    dump.iter().enumerate().filter(|&(i, &v)| v != FILL && !stored.words.contains_key(&(i as u32))).count()
        as u64
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
    fn pixels_past_the_target_follow_the_band_of_e831() {
        // 34 x 18: edge tiles hold pixels past x = 34 and y = 18; the band is x < 42, y < 22
        let (mut ax, mut ay) = dumps(34, 18, 3, 512 * 8);
        // the ramp continues past the target inside the band: pixel (41, 2) with its own values
        let i = store_dword(41, 2, 3) as usize;
        (ax[i], ay[i]) = (ramp(41, 34), ramp(2, 18));
        // and the background past the band at (50, 3) and (42, 21)
        for (x, y) in [(50, 3), (42, 21)] {
            let j = store_dword(x, y, 3) as usize;
            (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        }
        let c = check_store(34, 18, 3, &ax, &ay);
        assert_eq!(c.at_rule, 34 * 18);
        assert_eq!((c.at_rule_outside, c.background_outside, c.other), (1, 2, 0));
        // the ramp past the band and the background inside it are what the band rules out
        let (mut ax, mut ay) = dumps(34, 18, 3, 512 * 8);
        let i = store_dword(42, 2, 3) as usize;
        (ax[i], ay[i]) = (ramp(42, 34), ramp(2, 18));
        let j = store_dword(41, 21, 3) as usize;
        (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        let c = check_store(34, 18, 3, &ax, &ay);
        assert_eq!((c.at_rule_outside, c.background_outside, c.other), (0, 0, 2));
    }

    #[test]
    fn pixels_past_an_odd_width_follow_rule_a_after_e903() {
        // 35 x 18: 1.25 W = 43.75, rule A keeps columns 0 to 43 (E903 held out at 7, 11, 23, 35,
        // 43, 51): column 43 inside the band, 44 and 50 past it; FLOOR's edge (43) is a mismatch
        let (mut ax, mut ay) = dumps(35, 18, 3, 512 * 8);
        let i = store_dword(43, 2, 3) as usize;
        (ax[i], ay[i]) = (ramp(43, 35), ramp(2, 18));
        for (x, y) in [(44, 3), (50, 3)] {
            let j = store_dword(x, y, 3) as usize;
            (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        }
        let c = check_store(35, 18, 3, &ax, &ay);
        assert_eq!(c.at_rule, 35 * 18);
        assert_eq!((c.at_rule_outside, c.background_outside, c.other), (1, 2, 0));
        let (mut ax, mut ay) = dumps(35, 18, 3, 512 * 8);
        let j = store_dword(43, 2, 3) as usize;
        (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        assert_eq!(check_store(35, 18, 3, &ax, &ay).other, 1);
    }

    #[test]
    fn pixels_past_an_odd_height_follow_rule_a_after_e885() {
        // 34 x 19: 1.25 H = 23.75, rule A keeps rows 0 to 23 (E885 held out at 7, 11, 23, 35);
        // row 23 inside the band, row 24 past it
        let (mut ax, mut ay) = dumps(34, 19, 3, 512 * 8);
        let i = store_dword(2, 23, 3) as usize;
        (ax[i], ay[i]) = (ramp(2, 34), ramp(23, 19));
        let j = store_dword(3, 24, 3) as usize;
        (ax[j], ay[j]) = (BACKGROUND, BACKGROUND);
        let c = check_store(34, 19, 3, &ax, &ay);
        assert_eq!(c.at_rule, 34 * 19);
        assert_eq!((c.at_rule_outside, c.background_outside, c.other), (1, 1, 0));
    }

    #[test]
    fn the_band_is_rule_a_x_plus_half_below_1_25_w() {
        // E730's sizes and E831's held-out cells: the band's extent, before the tile cut
        for (w, x) in [(34u32, 42u32), (66, 82), (20, 25), (36, 45), (44, 55), (76, 95), (32, 40)] {
            assert!(in_band(x - 1, 0, w, 18) && !in_band(x, 0, w, 18), "W {w}");
        }
        for (h, y) in [(18u32, 22u32), (20, 25), (28, 35), (36, 45), (34, 42)] {
            assert!(in_band(0, y - 1, 34, h) && !in_band(0, y, 34, h), "H {h}");
        }
        // E885's odd heights at W 34: rule A, one row more than FLOOR at the .75 cells (7, 11, 19,
        // 23, 35) and the same at the .25 cells (17, 21)
        for (h, y) in [(7u32, 9u32), (11, 14), (19, 24), (23, 29), (35, 44), (17, 21), (21, 26)] {
            assert!(in_band(0, y - 1, 34, h) && !in_band(0, y, 34, h), "H {h}");
        }
        // E903's odd widths at H 18: rule A, one column more than FLOOR at the .75 cells (7, 11,
        // 19, 23, 35, 43, 51) and the same at the .25 cells (17, 21, 33)
        for (w, x) in [(7u32, 9u32), (11, 14), (19, 24), (23, 29), (35, 44), (43, 54), (51, 64), (17, 21)] {
            assert!(in_band(x - 1, 0, w, 18) && !in_band(x, 0, w, 18), "W {w}");
        }
        for (w, x) in [(21u32, 26u32), (33, 41)] {
            assert!(in_band(x - 1, 0, w, 18) && !in_band(x, 0, w, 18), "W {w}");
        }
    }

    #[test]
    fn a_store_past_the_target_holds_the_depth_in_the_band_and_the_background_beyond() {
        let n = |s: &Stored, v: f32| s.words.values().filter(|&&d| d == v.to_bits()).count();
        // E831's controls: 34 x 18 at G = 1 and 66 x 34 at G = 2 (0x171014), the full-screen ramp
        let s = store(&ctl(0x0017_100c), 34, 18, false, &|_, _| 0.3).unwrap();
        assert_eq!((s.words.len(), n(&s, 0.3), n(&s, 1.0)), (2048, 924, 1124));
        let s = store(&ctl(0x0017_1014), 66, 34, false, &|_, _| 0.3).unwrap();
        assert_eq!((s.words.len(), n(&s, 0.3)), (9 * 512, 3444));
        // held out: the band past the tile area is cut at it (z-w32 704, z-w64 1408, z-h32 1344)
        let s = store(&ctl(0x0017_100c), 32, 18, false, &|_, _| 0.3).unwrap();
        assert_eq!((s.words.len(), n(&s, 0.3)), (1024, 704));
        let s = store(&ctl(0x0017_100c), 64, 18, false, &|_, _| 0.3).unwrap();
        assert_eq!(n(&s, 0.3), 1408);
        let s = store(&ctl(0x0017_100c), 34, 32, false, &|_, _| 0.3).unwrap();
        assert_eq!(n(&s, 0.3), 1344);
        for (w, h, want) in [(20, 18, 550), (36, 18, 990), (44, 18, 1210), (34, 20, 1050), (34, 28, 1344)] {
            let s = store(&ctl(0x0017_100c), w, h, false, &|_, _| 0.3).unwrap();
            assert_eq!(n(&s, 0.3), want, "{w} x {h}");
        }
        // a triangle short of the band is its own raster: the depth the pass left, 1.0 elsewhere
        let tri = |x: u32, y: u32| if x >= 24 && y >= 8 && x < 40 && y < 20 { 0.3 } else { 1.0 };
        let s = store(&ctl(0x0017_100c), 34, 18, false, &tri).unwrap();
        assert_eq!((n(&s, 0.3), n(&s, 1.0)), (16 * 12, 2048 - 16 * 12));
        // E885: odd heights at W 34 store rule A's set (42 columns times the band's rows)
        for (h, want) in [(17, 882), (19, 1008), (7, 378), (11, 588), (21, 1092), (23, 1218), (35, 1848)] {
            let s = store(&ctl(0x0017_100c), 34, h, false, &|_, _| 0.3).unwrap();
            assert_eq!(n(&s, 0.3), want, "34 x {h}");
        }
        // E903: odd widths at H 18 store rule A's set (the band's columns times 22 rows)
        let odd = [(19, 528), (35, 968), (7, 198), (11, 308), (23, 638), (43, 1188), (51, 1408)];
        for (w, want) in odd.into_iter().chain([(17, 462), (21, 572), (33, 902)]) {
            let s = store(&ctl(0x0017_100c), w, 18, false, &|_, _| 0.3).unwrap();
            assert_eq!(n(&s, 0.3), want, "{w} x 18");
        }
    }

    #[test]
    fn a_store_past_the_target_refuses_integer_formats_and_the_stencil() {
        let d = |_: u32, _: u32| 0.25f32;
        // odd sizes store by rule A in the float format: odd heights (E885), odd widths (E903)
        assert!(store(&ctl(0x0017_100c), 35, 18, false, &d).is_ok());
        assert!(store(&ctl(0x0017_100c), 35, 19, false, &d).is_ok());
        assert!(store(&ctl(0x0017_100c), 34, 19, false, &d).is_ok());
        // the integer formats ran at an edge at an even size only (E977, E991); odd sizes are Q242's
        assert!(store(&ctl(0x0017_100c | 1 << 24), 34, 18, false, &d).is_ok());
        assert!(store(&ctl(0x0017_110c | 2 << 24), 34, 18, false, &d).is_ok());
        assert_eq!(ids(store(&ctl(0x0017_100c | 1 << 24), 35, 18, false, &d)), ["Q242"]);
        assert_eq!(ids(store(&ctl(0x0017_110c | 2 << 24), 34, 19, false, &d)), ["Q242"]);
        // the stencil store of an edge tile was not measured (Q121, its in-tile order)
        assert_eq!(ids(dword_sets(&ctl(0x0017_110c), 34, 16, true)), ["Q121"]);
        let (d, st) = dword_sets(&ctl(0x0015_110c), 34, 16, true).unwrap();
        assert_eq!((d.len(), st.len()), (1024, 0));
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

    // ---- 12.4 ----

    fn ctl(w: u32) -> Ctl {
        Ctl::decode(w).unwrap()
    }

    #[test]
    fn the_closed_drivers_values_decode_as_e337_and_e467_read_them() {
        // 0x0017100c: G 1, both stores, no load; 0x0017700e: bits 1, 13, 14 load both
        let c = ctl(0x0017_100c);
        assert_eq!(
            (c.g(), c.load(), c.store_depth(), c.store_stencil(), c.negate()),
            (1, false, true, true, false)
        );
        let c = ctl(0x0017_700e);
        assert_eq!((c.load_depth(), c.load_stencil(), c.store_depth()), (true, true, true));
        // bits 1 and 13 only: the stencil loads, the depth does not
        let c = ctl(0x0017_300e);
        assert_eq!((c.load_depth(), c.load_stencil()), (false, true));
        // 0x0011700a: loads both, stores nothing (bits 2, 17, 18 clear); 0x00140008: bit 2 clear
        let c = ctl(0x0011_700a);
        assert_eq!(
            (c.load_depth(), c.load_stencil(), c.store_depth(), c.store_stencil()),
            (true, true, false, false)
        );
        assert!(!ctl(0x0014_0008).store_depth());
    }

    #[test]
    fn bits_13_and_14_do_nothing_without_bit_1() {
        let c = ctl(0x0017_710c);
        assert_eq!((c.load(), c.load_depth(), c.load_stencil()), (false, false, false));
    }

    fn ids(r: Result<impl std::fmt::Debug, Outcome>) -> Vec<String> {
        match r {
            Err(Outcome::Unsupported { ids, .. }) => ids,
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn the_formats_3_to_7_refuse_by_question() {
        for f in [3u32, 4, 5, 6, 7] {
            assert_eq!(ids(ctl(0x0017_110c | f << 24).format()), ["Q120"]);
        }
        // E985 read 3 to 6 offline at two sizes (SEMI, held out by no run); 7 was not decoded
        let why = |f: u32| match ctl(0x0017_110c | f << 24).format() {
            Err(Outcome::Unsupported { why, .. }) => why,
            r => panic!("{r:?}"),
        };
        for f in [3u32, 4, 5, 6] {
            assert!(why(f).contains("E985"), "{f}: {}", why(f));
        }
        assert!(why(7).contains("not decoded"), "{}", why(7));
        assert_eq!(ctl(0x0017_110c | 2 << 24).format(), Ok(Format::U16));
    }

    #[test]
    fn bit_0_is_decoded_only_for_the_control_e411_ran_it_on() {
        // E411 (control-bits, two runs): 0x0017100c with bit 0 set writes no pixel and stores
        // the control's pages
        let c = ctl(0x0017_100d);
        assert!(!c.writes_pixels());
        assert!(ctl(0x0017_100c).writes_pixels());
        assert_eq!((c.store_depth(), c.store_stencil(), c.g()), (true, true, 1));
        // any other control with bit 0 set: what it stores was not seen
        assert_eq!(ids(Ctl::decode(0x0017_110d)), ["Q071"]);
        assert_eq!(ids(Ctl::decode(0xffff_ffff)), ["Q071"]);
    }

    #[test]
    fn bit_0_stores_what_the_control_stores() {
        let (a, b) = (ctl(0x0017_100c), ctl(0x0017_100d));
        assert_eq!(dword_sets(&a, 64, 64, true).unwrap(), dword_sets(&b, 64, 64, true).unwrap());
    }

    #[test]
    fn the_flips_of_e411_that_changed_nothing_are_ignored_bits() {
        assert_eq!(
            ctl(0x0017_100c | 1 << 21).ignored_bits(),
            1 << 21 | 0x0017_100c & (1 << 12 | 1 << 16 | 1 << 20)
        );
    }

    #[test]
    fn float_stores_the_bits_and_bit_19_flips_the_sign() {
        assert_eq!(encode_depth(Format::F32, false, 0.5), Ok(0x3f00_0000));
        assert_eq!(encode_depth(Format::F32, true, 1.0), Ok(0xbf80_0000)); // E411: -1.0
    }

    /// The fourth candidate of E663: the usual unorm conversion, floor(z * 2^24) clamped to 24 bits.
    fn floor_2p24_clamp(z: f32) -> u32 {
        ((z as f64 * 16777216.0).floor() as u32).min(0xff_ffff)
    }

    fn ramp_z(p: u32, size: u32) -> f32 {
        0.25f32 + 0.5 * (p as f32 + 0.5) / (3.0 * size as f32)
    }

    #[test]
    fn the_integer_formats_refuse_a_depth_outside_0_to_1() {
        // E977 stored depths from 0 to 1 (two ramps, three pitches); nothing outside ran
        for fmt in [Format::U24, Format::U16] {
            for z in [-0.5f32, -0.01, 1.01, 1.5, f32::NAN, f32::INFINITY] {
                assert_eq!(ids(encode_depth(fmt, false, z)), ["Q242"], "{fmt:?} {z}");
            }
            for z in [0.0f32, 0.2, 0.25, 0.5, 0.75, 0.9, 1.0] {
                assert!(encode_depth(fmt, false, z).is_ok(), "{fmt:?} {z}");
            }
        }
    }

    #[test]
    fn bit_19_changes_no_integer_dword_over_0_to_the_ramp() {
        // E490 over 0.25 to 0.4166, E981 over 0 to 0.3: byte-identical dumps with and without it
        for z in [0.0f32, 0.1, ramp_z(7, 1024), 0.4166] {
            for fmt in [Format::U24, Format::U16] {
                assert_eq!(encode_depth(fmt, true, z), encode_depth(fmt, false, z), "{z}");
            }
        }
        for z in [0.5f32, 0.9, 1.0] {
            assert_eq!(ids(encode_depth(Format::U24, true, z)), ["Q101"], "{z}");
            assert_eq!(ids(encode_depth(Format::U16, true, z)), ["Q101"], "{z}");
        }
    }

    #[test]
    fn the_24_bit_rule_is_floor_of_z_times_2_to_the_24_clamped() {
        // E977: floor held at every dword of three ramps, round(z * 0xffffff) failed from 0.5 up
        for z in [0.6f32, 0.75, 0.9, 0.1, 0.01] {
            assert_eq!(encode_depth(Format::U24, false, z), Ok(floor_2p24_clamp(z)), "{z}");
            assert_eq!(encode_depth(Format::U16, false, z), Ok(floor_2p24_clamp(z) >> 8), "{z}");
        }
        assert_ne!(((0.75f64 * 16777215.0 + 0.5).floor()) as u32, floor_2p24_clamp(0.75));
        assert_eq!(encode_depth(Format::U24, false, 0.75), Ok(0x00c0_0000));
        // the two agree on every single-precision depth of E490's ramp, so its counts stand
        let (lo, hi) = (0.25f32.to_bits(), 0.4166f32.to_bits());
        for bits in (lo..=hi).step_by(97) {
            let z = f32::from_bits(bits);
            assert_eq!(((z as f64 * 16777215.0 + 0.5).floor()) as u32, floor_2p24_clamp(z), "{z}");
        }
    }

    #[test]
    fn the_integer_formats_round_the_ramp_and_the_clear_value_stores_all_ones() {
        // E411: bit 24 stores 1.0 as 0x00ffffff, bit 25 as 0xffff in both halves
        assert_eq!(encode_depth(Format::U24, false, 1.0), Ok(0x00ff_ffff));
        assert_eq!(encode_depth(Format::U16, false, 1.0), Ok(0xffff));
        assert_eq!(encode_depth(Format::U24, false, 0.25), Ok(4194304)); // 4194303.75 rounds up
        assert_eq!(encode_depth(Format::U16, false, 0.25), Ok(0x4000));
    }

    #[test]
    fn the_16_bit_index_is_x0_y1_x1_y2_x2_y3_x3_x4() {
        let order = [('x', 0), ('y', 1), ('x', 1), ('y', 2), ('x', 2), ('y', 3), ('x', 3), ('x', 4)];
        for (pos, (axis, bit)) in order.into_iter().enumerate() {
            let (x, y) = if axis == 'x' { (1 << bit, 0) } else { (0, 1 << bit) };
            assert_eq!(in_tile_index16(x, y), 1 << pos, "{axis}{bit}");
        }
        assert_eq!(in_tile_index16(0, 1), in_tile_index16(0, 0), "y0 is the half, not the index");
    }

    #[test]
    fn a_16_bit_store_packs_the_even_row_low_and_the_odd_row_high() {
        let c = ctl(0x0017_110c | 2 << 24);
        let s = store(&c, 32, 16, false, &|_, y| if y == 0 { 0.25 } else { 1.0 }).unwrap();
        assert_eq!(s.words.len(), 256);
        assert_eq!(s.words[&in_tile_index16(0, 0)], 0xffff_4000);
        // the slots are 256 dwords at the tile pitch (G + 1 = 34)
        let s = store(&c, 64, 16, false, &|_, _| 0.25).unwrap();
        assert!(s.words.contains_key(&256) && !s.words.contains_key(&512));
    }

    #[test]
    fn an_integer_store_of_an_edge_target_is_the_float_stores_floor_at_every_dword() {
        // E991 (r9-x's z242-c, 80 x 40 at G 2): past the target the 24-bit dword is
        // min(floor(z0 * 2^24), 0xffffff) and the 16-bit half floor(z0 * 2^16) in E490's layout,
        // z0 the float the same pixel stores (the band's depth or 1.0), 1408 and 704 of 1408 and 704
        let (w, h, g) = (80, 40, 2);
        let d = |x: u32, y: u32| 0.25 + (x + 2 * y) as f32 / 400.0;
        let base = 0x0015_1004 | g << 3; // depth stored, no stencil store
        let f = store(&ctl(base), w, h, false, &d).unwrap();
        let u24 = store(&ctl(base | 1 << 24), w, h, false, &d).unwrap();
        assert_eq!(u24.words.len(), 9 * 512, "every dword of the 3 x 3 tiles");
        assert_eq!(u24.words.keys().collect::<Vec<_>>(), f.words.keys().collect::<Vec<_>>());
        let fl = |v: u32, s: f64| (f64::from(f32::from_bits(v)) * s).floor() as u32;
        for (i, v) in &f.words {
            assert_eq!(u24.words[i], fl(*v, 16777216.0).min(0xff_ffff), "dword {i}");
        }
        let u16 = store(&ctl(base | 2 << 24), w, h, false, &d).unwrap();
        assert_eq!(u16.words.len(), 9 * 256);
        for y in (0..48).step_by(2) {
            for x in 0..96 {
                let i = 256 * ((y >> 4) * (g + 1) + (x >> 5)) + in_tile_index16(x, y);
                let (lo, hi) = (f.words[&store_dword(x, y, g)], f.words[&store_dword(x, y + 1, g)]);
                assert_eq!(u16.words[&i], fl(lo, 65536.0).min(0xffff) | fl(hi, 65536.0).min(0xffff) << 16);
            }
        }
        let (dd, _) = dword_sets(&ctl(base | 2 << 24), w, h, false).unwrap();
        assert_eq!(dd, u16.words.keys().copied().collect());
    }

    #[test]
    fn a_16_bit_store_takes_its_layout_at_any_pitch() {
        // E977: E490's 16-bit layout held at G 7, 9 and 2 (slots of 256 at the pitch G + 1)
        let s = store(&ctl(0x0017_100c | 2 << 24), 64, 16, false, &|_, _| 0.25).unwrap();
        assert!(s.words.contains_key(&256) && s.words.len() == 512);
    }

    #[test]
    fn stores_that_are_off_or_that_e490_found_empty_store_nothing() {
        let d = |_: u32, _: u32| 0.5f32;
        assert!(store(&ctl(0x0017_1108), 32, 16, false, &d).unwrap().words.is_empty(), "bit 2 clear");
        assert!(store(&ctl(0x0013_110c), 32, 16, false, &d).unwrap().words.is_empty(), "bit 18 clear");
        for f in [4u32, 7] {
            assert!(store(&ctl(0x0017_110c | f << 24), 32, 16, false, &d).unwrap().words.is_empty());
            // with a stencil buffer the layout of formats 4 and 7 is not decoded
            assert!(store(&ctl(0x0017_110c | f << 24), 32, 16, true, &d).is_err());
        }
    }

    #[test]
    fn a_float_store_is_one_dword_a_pixel_at_the_address_rule() {
        let s = store(&ctl(0x0017_110c), 64, 32, false, &|x, y| (x + y) as f32).unwrap();
        assert_eq!(s.words.len(), 2048);
        assert_eq!(s.words[&store_dword(33, 17, 33)], 50f32.to_bits());
    }

    #[test]
    fn a_loaded_depth_loses_its_sign_bit() {
        for (v, want) in [
            (0xbe80_0000, 0x3e80_0000),
            (0xdead_beef, 0x5ead_beef),
            (0xffff_ffff, 0x7fff_ffff),
            (0x8000_0000, 0),
        ] {
            assert_eq!(load_word(v), want);
        }
    }

    fn run(c: u32, test: Test, ld: &dyn Fn(u32) -> u32) -> Result<Pass, Outcome> {
        pass(&ctl(c), 64, 32, 1.0, 0.5, test, &|_, _| true, ld, &|i| i)
    }

    #[test]
    fn without_bits_1_and_14_the_pass_starts_from_the_clear_value() {
        for c in [0x0017_110c, 0x0017_110e, 0x0017_310c, 0x0017_510c, 0x0017_710c, 0x0017_310e] {
            let p = run(c, Test::Never, &|i| i).unwrap();
            assert!(p.depth.values().all(|&v| v == 0x3f80_0000), "{c:#x}");
            assert_eq!(p.depth.len(), 2048);
        }
    }

    #[test]
    fn with_bits_1_and_14_the_loaded_depth_is_stored_with_its_sign_cleared() {
        let p = run(0x0017_510e, Test::Never, &|_| 0xbe80_0000).unwrap();
        assert!(p.depth.values().all(|&v| v == 0x3e80_0000));
    }

    #[test]
    fn the_depth_test_less_runs_against_the_loaded_depth() {
        let p =
            run(0x0017_510e, Test::Less, &|i| if i & 1 == 0 { 0.25f32.to_bits() } else { 0.75f32.to_bits() })
                .unwrap();
        assert_eq!(p.drawn, 1024);
        let n = |v: f32| p.depth.values().filter(|&&d| d == v.to_bits()).count();
        assert_eq!((n(0.25), n(0.5)), (1024, 1024));
        // without the load the clear 1.0 loses to 0.5 everywhere
        assert_eq!(run(0x0017_110c, Test::Less, &|i| i).unwrap().drawn, 2048);
    }

    #[test]
    fn a_compare_inside_the_planes_tolerance_refuses_q200() {
        let r = run(0x0017_510e, Test::Less, &|_| 0.5f32.to_bits() + 2);
        assert!(matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q200"]));
    }

    #[test]
    fn the_stencil_copies_the_loaded_dword_by_slot_or_stores_zero() {
        let p = run(0x0017_310e, Test::Never, &|i| i).unwrap();
        assert_eq!(p.stencil.len(), 2 * 2 * 128);
        assert!(p.stencil.iter().all(|(&i, &v)| v == i));
        let p = run(0x0017_110e, Test::Never, &|i| i).unwrap();
        assert!(p.stencil.values().all(|&v| v == 0));
        let p = run(0x0011_710a, Test::Never, &|i| i).unwrap();
        assert!(p.depth.is_empty() && p.stencil.is_empty(), "load-only stores nothing (E467)");
    }

    #[test]
    fn a_pass_refuses_edge_tiles_and_integer_formats() {
        // E831's band is the store's without a load; the load and the pass ran on whole tiles
        let r = pass(&ctl(0x0017_110c), 34, 18, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert!(matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q243"]));
        let r = run(0x0017_110c | 1 << 24, Test::Never, &|i| i);
        assert!(matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q243"]));
    }

    #[test]
    fn a_store_refuses_what_no_run_measured_by_input_alone() {
        let d = |_: u32, _: u32| 0.5f32;
        let q = |r: Result<Stored, Outcome>| ids(r);
        // pixels past the target in an integer format at an odd width or an odd height (Q242)
        assert_eq!(q(store(&ctl(0x0017_110c | 2 << 24), 33, 16, false, &|_, _| 0.25)), ["Q242"]);
        assert_eq!(q(store(&ctl(0x0017_110c | 2 << 24), 32, 17, false, &|_, _| 0.25)), ["Q242"]);
        assert_eq!(q(store(&ctl(0x0017_110c | 1 << 24), 35, 18, false, &|_, _| 0.25)), ["Q242"]);
        // overlapping tiles (pitch G + 1 below the tiles of a row): which pixel a shared dword
        // holds was not measured, only how many dwords were written (E465)
        assert_eq!(q(store(&ctl(0x0017_100c), 1024, 768, false, &d)), ["Q242"]);
        assert_eq!(q(store(&ctl(0x0017_110c | 2 << 24), 2048, 16, false, &|_, _| 0.25)), ["Q242"]);
        // whole tiles at a pitch that does not overlap still store
        assert_eq!(store(&ctl(0x0017_100c), 32, 16, false, &d).unwrap().words.len(), 512);
    }

    #[test]
    fn the_dword_sets_are_what_a_store_writes_and_allow_overlap_for_counting() {
        let c = ctl(0x0017_110c);
        let s = store(&c, 64, 32, false, &|_, _| 0.5).unwrap();
        let (d, st) = dword_sets(&c, 64, 32, true).unwrap();
        assert_eq!(d, s.words.keys().copied().collect());
        assert_eq!(st.len(), 4 * 128);
        // E411 flip of bit 3 (G = 0) on 64 x 64: 5 slots of depth and of stencil, 3200 dwords
        let (d, st) = dword_sets(&ctl(0x0017_1004), 64, 64, true).unwrap();
        assert_eq!((d.len(), st.len()), (5 * 512, 5 * 128));
        // the 16-bit format at G = 33 and at G = 1 (E977), and a refused edge
        let (d, _) = dword_sets(&ctl(0x0017_110c | 2 << 24), 64, 32, true).unwrap();
        assert_eq!(d.len(), 64 * 32 / 2);
        assert_eq!(ids(dword_sets(&ctl(0x0017_110c), 34, 16, true)), ["Q121"]);
        let (d, _) = dword_sets(&ctl(0x0017_100c | 2 << 24), 64, 64, true).unwrap();
        assert_eq!(d.len(), 64 * 64 / 2, "E977: any pitch");
        assert_eq!(ids(dword_sets(&ctl(0x0017_100c | 4 << 24), 64, 64, true)), ["Q120"]);
        // the stores off, nothing; formats 4 and 7 without a stencil buffer, nothing
        let (d, st) = dword_sets(&ctl(0x0017_1008), 64, 64, true).unwrap();
        assert!(d.is_empty() && st.is_empty());
        let (d, _) = dword_sets(&ctl(0x0017_110c | 7 << 24), 64, 32, false).unwrap();
        assert!(d.is_empty());
    }

    #[test]
    fn the_scratch_runs_of_e411_faulted_at_every_g_bit_from_bit_5() {
        // G 0, 1 and 3 (bit 3 cleared, the control, bit 4 set) ran; bits 5 to 11 set faulted
        for w in [0x0017_1004, 0x0017_100c, 0x0017_101c] {
            assert!(check_scratch_pitch(&ctl(w)).is_ok(), "{w:#x}");
        }
        for b in 5..=11 {
            assert_eq!(ids(check_scratch_pitch(&ctl(0x0017_100c ^ 1 << b))), ["Q242"], "bit {b}");
        }
    }

    #[test]
    fn a_pass_pins_its_addresses_to_the_store_rule() {
        // load every dword with its own address as a depth, at G = 2 (pitch 3 tiles) on 2 x 2 tiles
        let c = ctl(0x0017_7016);
        assert_eq!(c.g(), 2);
        let tag = |i: u32| 0x3e00_0000 + i;
        let p = pass(&c, 64, 32, 1.0, 0.5, Test::Never, &|_, _| true, &tag, &|i| i).unwrap();
        for y in 0..32 {
            for x in 0..64 {
                let i = store_dword(x, y, 2);
                assert_eq!(p.depth[&i], tag(i), "({x}, {y})");
            }
        }
        assert_eq!(p.depth.len(), 2048);
        // the stencil: 128 dwords at 128 * (ty * (G + 1) + tx), each the loaded dword of its index
        let want: std::collections::BTreeSet<u32> =
            [0, 1, 3, 4].into_iter().flat_map(|slot| (0..128).map(move |j| 128 * slot + j)).collect();
        assert_eq!(p.stencil.keys().copied().collect::<std::collections::BTreeSet<_>>(), want);
        assert!(p.stencil.iter().all(|(&i, &v)| v == i));
    }

    #[test]
    fn a_pass_negates_with_bit_19_and_refuses_it_with_a_load() {
        let p =
            pass(&ctl(0x0017_110c | 1 << 19), 32, 16, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i)
                .unwrap();
        assert!(p.depth.values().all(|&v| v == 0xbf80_0000));
        let r =
            pass(&ctl(0x0017_510e | 1 << 19), 32, 16, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert_eq!(ids(r), ["Q101"]);
        // bit 19 with a load of the stencil only does not load the depth: still refused (the
        // loaded value would be re-negated, and nothing ran)
        let r =
            pass(&ctl(0x0017_310e | 1 << 19), 32, 16, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert_eq!(ids(r), ["Q101"]);
    }

    #[test]
    fn a_pass_refuses_a_triangle_depth_that_never_ran_and_nan() {
        for z in [5.0f32, -1.0, 0.0, 0.9, f32::NAN, f32::INFINITY] {
            let r = pass(&ctl(0x0017_110c), 32, 16, 1.0, z, Test::Never, &|_, _| true, &|i| i, &|i| i);
            assert_eq!(ids(r), ["Q242"], "{z}");
        }
        // the 0.5 of E467 and E411 and the ramps' 0.25 to 0.4166 are what ran
        for z in [0.5f32, 0.25, 0.4166] {
            assert!(
                pass(&ctl(0x0017_110c), 32, 16, 1.0, z, Test::Never, &|_, _| true, &|i| i, &|i| i).is_ok()
            );
        }
    }

    #[test]
    fn a_loaded_infinity_or_nan_refuses_a_compare_but_not_a_copy() {
        for v in [0x7f80_0000u32, 0x7fc0_0000, 0xff80_0000, 0x7fff_ffff] {
            let r = run(0x0017_510e, Test::Less, &|_| v);
            assert_eq!(ids(r), ["Q243"], "{v:#x}");
            // under the test never the loaded dword is only copied (E467: 0xffffffff reads 0x7fffffff)
            assert!(run(0x0017_510e, Test::Never, &|_| v).is_ok(), "{v:#x}");
        }
    }

    #[test]
    fn dwords_the_model_did_not_store_are_unexplained() {
        let s = store(&ctl(0x0017_110c), 32, 16, false, &|_, _| 0.5).unwrap();
        let mut d = vec![FILL; 1024];
        for &i in s.words.keys() {
            d[i as usize] = 0;
        }
        assert_eq!(unexplained(&d, &s), 0);
        d[600] = 7;
        assert_eq!(unexplained(&d, &s), 1);
    }
}
