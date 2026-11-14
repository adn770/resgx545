// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! ZLS: the depth/stencil store and load (12.4). The address rule (E465, E489), the control word
//! (E411, E337), the stored depth formats 0 to 2 and the negation (E466, E490), the load by bits 1,
//! 13 and 14 with the sign cleared (E467), the pass over a loaded buffer and the band of an edge
//! tile (E730, E831, E885, E903), the stencil's byte a pixel and its test (E284, E988), the
//! background depth's sign (E987), formats 3 and 4 with a loaded and stored stencil (E985, E986).
//! What no record states refuses by question: formats 3 and 4 otherwise and 5 to 7
//! (Q120), the overflowed job's store (Q107: E628, E629, E1020, [`final_store`]), a NaN depth in an
//! integer format other than a kept load's (Q299; the overlapping stores follow E996, E1041 and
//! E1051 in every format, the pass over them E1064 and, with edge tiles, E1068), a pass plane outside 0 to 1 (Q069: only the viewport's z offset brings one; E1050 ran the pass over edge tiles, with bit 19, in
//! the integer formats and at depths of 0 to 1, E1059 at seven depths fed the no-load plane), bit
//! 20 cleared with formats 5 to 7, bit 12 cleared with a load and bit 16 cleared with a depth load,
//! a stencil store or the 16-bit format (Q071, E997, E1030, E1063), the stencil test's source under any
//! mix of the control's inert bits but those that ran (Q071, E988, E989, E1030, E1042, E1053). The
//! depth load reads from its own base, render details dword 12, rounded down to 16 bytes
//! ([`load_base`]: E1029, E1040); [`pass`] still loads at the store's address. Every refusal
//! depends on the input alone.

use crate::Outcome;

/// Open questions that block the rest of the unit.
/// The status of the address rule (rules.rs).
pub const STORE_STATUS: crate::rules::Status = crate::rules::ZLS_ADDRESS;

pub const OPEN: &[&str] = &["Q069", "Q071", "Q107", "Q120", "Q299"];

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

/// The dword of the depth buffer that holds pixel (x, y) under `ctl`: [`store_dword`] at its pitch,
/// or with bit 16 cleared the linear image's 32 (G + 1) y + x (E997, E1030).
pub fn store_dword_of(ctl: &Ctl, x: u32, y: u32) -> u32 {
    if ctl.linear_store() { 32 * (ctl.g() + 1) * y + x } else { store_dword(x, y, ctl.g()) }
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
/// Bit 20: cleared alone it changed nothing in formats 0 (E1030's ramp, E1063 at 640 x 480) and with
/// bit 12 cleared and a depth load (E1063's zb4-20-d12), but in formats 6 and 7 it moved the stored
/// records (E1063: the per-tile records packed one after another from dword 2048, post hoc).
const CTL_RECORDS: u32 = 1 << 20;

/// Bit 16: cleared, the depth store is a linear image of the tile area, rows of 32 (G + 1) dwords
/// in y order (E997, post hoc, and its correction: 4608 of 4608 by (x, y)); E1030 separated it from
/// bits 12 and 20 (r13-zls zbits: the ramp's store E997's dump byte for byte exactly when bit 16 is
/// clear, 6 of 6 held out). E411's single flips compared stored pages, which the layout keeps.
const CTL_LINEAR: u32 = 1 << 16;
/// Bit 12: cleared, the stencil load reads another byte order (E1030, post hoc: a linear image of
/// 64-byte rows at G 1); its depth store stays tiled (E1030). E1042 held the rows at 32 (G + 1)
/// bytes out at G 2 and read a depth load under it linear too (dword 64 y + x at G 1); not modelled
/// here, the loads under it still refuse (Q071). E1042 also read bits 21 to 23 together as the
/// stencil test's read of 0 and bit 16 with the 16-bit format as a halfword image, neither
/// modelled.
const CTL_LOAD_ORDER: u32 = 1 << 12;

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
    /// control stores without it: 0x0017100d (E411, two runs) and formats 0 to 2 at G 2 and the
    /// depth load (E997, 4 of 4 held out), and with the stencil loaded under E988's st1, E1030's
    /// bit 16 cleared and formats 6 and 7 (E1063, H-B0 4 of 4 held out). Bit 20 cleared with formats
    /// 5 to 7 refuses (Q071: E1063 saw the format 6 and 7 records move, post hoc).
    /// Bit 12 cleared with a load refuses (Q071: E1030 read the stencil load in another order post
    /// hoc; a depth load under it was not run); bit 16 cleared (the linear store, E1030) with a
    /// depth load or the 16-bit format refuses (Q071: not run), and its stencil store into a stencil
    /// buffer does in [`dword_sets`] (E1030 read it linear post hoc).
    pub fn decode(word: u32) -> Result<Ctl, Outcome> {
        let c = Ctl { word };
        if word & CTL_RECORDS == 0 && c.format_code() >= 5 {
            return Err(open(
                format!(
                    "CR_ISP_ZLSCTL {word:#x}: bit 20 cleared with format {}: the records moved (E1063, \
                     post hoc at one size)",
                    c.format_code()
                ),
                &["Q071"],
            ));
        }
        if c.load() && word & CTL_LOAD_ORDER == 0 {
            return Err(open(
                format!(
                    "CR_ISP_ZLSCTL {word:#x}: bit 12 cleared with a load: the stencil load reads another \
                     byte order (E1030, post hoc), a depth load under it was not run"
                ),
                &["Q071"],
            ));
        }
        if c.linear_store() && (c.load_depth() || c.format_code() == 2) {
            return Err(open(
                format!(
                    "CR_ISP_ZLSCTL {word:#x}: bit 16 cleared stores a linear image (E997, E1030); with a \
                     depth load or the 16-bit format its layout was not read"
                ),
                &["Q071"],
            ));
        }
        Ok(c)
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
    /// Bits 1 and 14 together (E664); bit 1 alone loads no depth (E739).
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
    /// Bit 16 cleared with the depth store on: the linear image of [`store_dword_of`] (E1030).
    pub fn linear_store(&self) -> bool {
        self.store_depth() && self.word & CTL_LINEAR == 0
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
            // E985 read the layouts of 3 and 4 from E978's kept dumps with a loaded stencil and E986
            // held them out: they pack the stencil, so [`store_packed`] models them, not this
            c @ 3..=4 => Err(open(
                format!(
                    "stored depth format {c} packs the stencil with the depth (E985, E986): store_packed \
                     models it with a loaded stencil, a plain depth store refuses"
                ),
                &["Q120"],
            )),
            // E985 read 5 and 6 at two sizes (SEMI); E986: where a tile row repeats one depth they
            // store less; E1015 read format 6's groups of four constant rows and format 7's template
            // under a constant stencil, not their variable-length runs; E1031 held both out but for a
            // flat tile (44 dwords of another form): refused whole
            c @ 5..=6 => Err(open(
                format!(
                    "stored depth format {c}: its layout was read offline where every pixel of a tile row \
                     differs only (E985, SEMI; E986: less where a row repeats one depth; E466, E490, E978)"
                ),
                &["Q120"],
            )),
            c => Err(open(
                format!(
                    "stored depth format {c}: its layout was not decoded (E466, E490, E978, E985; E986: it \
                     depends on the stencil data)"
                ),
                &["Q120"],
            )),
        }
    }
}

impl Ctl {
    /// Formats 3 and 4 as they ran (E978, E985, E986): the stencil loaded (bits 1 and 13) and
    /// stored (bit 17), the depth stored (bits 2 and 18), no depth load, bit 19 clear, G + 1 the
    /// tiles across (the two were never parted, E985), whole tiles or, for format 3, the edge
    /// tiles of an even size (E986's 40 x 20). Anything else refuses (Q120): without a stencil
    /// load E466 counted another layout (965120 dwords at 1024 x 768), and 5 to 7 store less
    /// where a tile row repeats one depth (E986).
    pub fn packed(&self, w: u32, h: u32) -> Result<Packed, Outcome> {
        let c = self.format_code();
        let fmt = match c {
            3 => Packed::DepthStencil,
            4 => Packed::Stencil,
            _ => {
                return Err(open(
                    format!("stored depth format {c} is not a packed format modelled (E985, E986)"),
                    &["Q120"],
                ));
            }
        };
        let why = if !(self.load_stencil() && self.store_stencil() && self.store_depth()) {
            "ran only with the stencil loaded (bits 1, 13) and the stencil and depth stores on (E978, E986)"
        } else if self.negate() {
            "ran only with bit 19 clear (E986)"
        } else if self.load_depth() {
            "ran only without a depth load (E986)"
        } else if w.div_ceil(32) != self.g() + 1 {
            "ran only with G + 1 the tiles across, which E985 could not part from the pitch"
        } else if has_edge(w, h) && (fmt == Packed::Stencil || w % 2 == 1 || h % 2 == 1) {
            "ran past an edge only in format 3 at 40 x 20 (E986)"
        } else {
            return Ok(fmt);
        };
        Err(open(format!("stored depth format {c} at {w} x {h}, control {:#x}: {why}", self.word), &["Q120"]))
    }
}

/// Stored depth formats 3 and 4 (E985's layouts, held out byte for byte by E986): a tile in block
/// 2 tw (ty >> 1) + 2 tx + (ty & 1), tw the tiles across.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Packed {
    /// format 3: 640 dwords a block, 16 chunks of 160 bytes (a row each), pixel x's record the
    /// float with its sign bit set (little endian) then the stencil byte
    DepthStencil,
    /// format 4: no depth; 160 dwords of each 256-dword block, 8 groups of 80 bytes (rows 2n and
    /// 2n + 1), record 8 (y & 1) + x div 4 the byte 0xf0 then the stencil bytes of x + 3 down to x
    Stencil,
}

/// The byte of record `p` (a pixel of a row in format 3, a quad in format 4), byte `q`, in its
/// chunk or group: 1 + 17 g + 5 (2 - p mod 3) + q with g = p div 3, less 32 from 16 (g + 1) up
/// (E985, fitted; held out by E986). No mechanism is known [infer].
pub fn packed_addr(p: u32, q: u32) -> u32 {
    let g = p / 3;
    let a = 1 + 17 * g + 5 * (2 - p % 3) + q;
    if a >= 16 * (g + 1) { a - 32 } else { a }
}

fn packed_block(tx: u32, ty: u32, tw: u32) -> u32 {
    2 * tw * (ty >> 1) + 2 * tx + (ty & 1)
}

/// The store of formats 3 and 4 ([`Ctl::packed`]): `depth(x, y)` as [`store`] takes it (the
/// band's depth, the background 1.0 past it, E986 at 40 x 20) and `stencil(x, y)` the stencil
/// byte of the pixel at the store (E986's rows: the loaded byte at [`stencil_byte`], no stencil
/// operation ran). E986: 12 rows (the x ramp under the index fill and fills 0x00, 0xff and 0xa5,
/// a y ramp, the plane over 0 to 1, 40 x 20's edge tiles) byte for byte, every changed dword
/// predicted; the stencil store is not written ([`dword_sets`]).
pub fn store_packed(
    ctl: &Ctl,
    w: u32,
    h: u32,
    depth: &dyn Fn(u32, u32) -> f32,
    stencil: &dyn Fn(u32, u32) -> u8,
) -> Result<Stored, Outcome> {
    let fmt = ctl.packed(w, h)?;
    let tw = w.div_ceil(32);
    let mut bytes = std::collections::BTreeMap::<u32, u8>::new();
    for ty in 0..h.div_ceil(16) {
        for tx in 0..tw {
            let blk = packed_block(tx, ty, tw);
            match fmt {
                Packed::DepthStencil => {
                    for r in 0..16 {
                        for x in 0..32 {
                            let (px, py) = (32 * tx + x, 16 * ty + r);
                            let z = if in_band(px, py, w, h) { depth(px, py) } else { 1.0 };
                            let d = (z.to_bits() | 1 << 31).to_le_bytes();
                            let rec = [d[0], d[1], d[2], d[3], stencil(px, py)];
                            for (q, b) in (0..).zip(rec) {
                                bytes.insert(2560 * blk + 160 * r + packed_addr(x, q), b);
                            }
                        }
                    }
                }
                Packed::Stencil => {
                    for n in 0..8 {
                        for m in 0..16 {
                            let (y, x0) = (16 * ty + 2 * n + m / 8, 32 * tx + 4 * (m % 8));
                            let rec = [
                                0xf0,
                                stencil(x0 + 3, y),
                                stencil(x0 + 2, y),
                                stencil(x0 + 1, y),
                                stencil(x0, y),
                            ];
                            for (q, b) in (0..).zip(rec) {
                                bytes.insert(1024 * blk + 80 * n + packed_addr(m, q), b);
                            }
                        }
                    }
                }
            }
        }
    }
    let mut s = Stored::default();
    for (&o, &b) in &bytes {
        *s.words.entry(o / 4).or_insert(0) |= u32::from(b) << (8 * (o % 4));
    }
    debug_assert_eq!(bytes.len(), 4 * s.words.len(), "every packed dword is written whole");
    Ok(s)
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

/// The integer formats' range: 0 to 1 (E977's two ramps at three pitches; E490's ramp and E411's
/// clear value inside it); past it the conversion clamps (E1051).
pub const INT_DEPTH: std::ops::RangeInclusive<f32> = 0.0..=1.0;

/// The dword a pixel's depth `z` is stored as in `fmt` (the 16-bit value in the low half for
/// U16; the packing of two rows is [`store`]'s). Bit 19 negates the float (E490: 786432 of
/// 786432); with an integer format it changed no dword over 0 to 0.4166 (E490, E981, and E987's
/// background 0.25), and no route that ran brings a negative depth to the integer conversion
/// (E981: a negative depth after the clip stores 0; E987: the background's sign is cleared), so
/// over 0 to 1 it changes nothing [infer: a positive depth's sign bit is clear]. The 24-bit value is min(floor(z * 2^24), 0xffffff) and the 16-bit
/// one its >> 8 (E977: held out over 0 to 1 at three pitches; round(z * 0xffffff), E466's fit,
/// failed from 0.5 up and agreed below where E466's dumps lay). Outside 0 to 1 the same rule
/// clamps: a depth above 1 stores 0xffffff and 0xffff, a negative one 0 (E1051: 1.25 and -0.25 by
/// the viewport's z offset in both formats, 4 of 4 held out; format 0 stored 1.25 itself, so the
/// clamp is the conversion's; E981: a negative depth stored 0 in every format). A NaN depth stores
/// the top of the range, 0xffffff and 0xffff, above every depth as in the compare (E1064: kept
/// loads 0x7fc00000, 0xffc00000 and 0x7f800001 in both formats, 5 of 5 held out; E995).
pub fn encode_depth(fmt: Format, negate: bool, z: f32) -> Result<u32, Outcome> {
    match fmt {
        Format::F32 => Ok(z.to_bits() ^ u32::from(negate) << 31),
        Format::U24 | Format::U16 => {
            let z = if z.is_nan() { 1.0 } else { z };
            let z = z.clamp(INT_DEPTH.start().to_owned(), INT_DEPTH.end().to_owned());
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

/// The dwords of the depth buffer a store writes, for counting: overlapping tiles allowed (E465
/// counted them), values not given.
fn depth_dwords(ctl: &Ctl, w: u32, h: u32, stencil_buffer: bool) -> Result<Dwords, Outcome> {
    let mut d = Dwords::new();
    if !ctl.store_depth() || matches!(ctl.format_code(), 4 | 7) && !stencil_buffer {
        return Ok(d);
    }
    if let c @ 3..=4 = ctl.format_code() {
        let fmt = ctl.packed(w, h)?;
        let (n, tw) = (if fmt == Packed::DepthStencil { 640 } else { 160 }, w.div_ceil(32));
        for ty in 0..h.div_ceil(16) {
            for tx in 0..tw {
                let base = if c == 3 { 640 } else { 256 } * packed_block(tx, ty, tw);
                d.extend(base..base + n);
            }
        }
        return Ok(d);
    }
    let fmt = ctl.format()?;
    let g = ctl.g();
    // every dword of the target's tiles (E831: the band's pixels and the background past it)
    let (tw, th) = (32 * w.div_ceil(32), 16 * h.div_ceil(16));
    match fmt {
        Format::F32 | Format::U24 => {
            for y in 0..th {
                for x in 0..tw {
                    d.insert(store_dword_of(ctl, x, y));
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

/// The dwords of the stencil buffer a store writes: 128 a tile slot, a byte a pixel at
/// [`stencil_byte`], edge tiles included (E988: at 40 x 20 the bytes past the target are the
/// loaded ones, with E831's band tested as the target is; E985 read lane 0 offline).
/// Formats 3 and 4 write no stencil store (E978, E986: 21 of 21 rows of formats 3 to 7).
fn stencil_dwords(ctl: &Ctl, w: u32, h: u32) -> Result<Dwords, Outcome> {
    let mut d = Dwords::new();
    if !ctl.store_stencil() || matches!(ctl.format_code(), 3 | 4) {
        return Ok(d);
    }
    for ty in 0..h.div_ceil(16) {
        for tx in 0..w.div_ceil(32) {
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
    if ctl.linear_store() && ctl.store_stencil() {
        // E1030 read the stencil store under bit 16 post hoc as a linear image of 32 (G + 1)-byte
        // rows (64 at G 1): as a set its dwords are the tiled ones when the tiles across are G + 1
        // (E411's flip of bit 16 stored the control's pages), otherwise it refuses
        if stencil_buffer && w.div_ceil(32) != ctl.g() + 1 {
            return Err(open(
                format!(
                    "CR_ISP_ZLSCTL {:#x}: the stencil store with bit 16 cleared (E1030, post hoc)",
                    ctl.word
                ),
                &["Q071"],
            ));
        }
        let st = if stencil_buffer { stencil_dwords(ctl, w, h)? } else { Dwords::new() };
        return Ok((depth_dwords(ctl, w, h, stencil_buffer)?, st));
    }
    Ok((depth_dwords(ctl, w, h, stencil_buffer)?, stencil_dwords(ctl, w, h)?))
}

/// The first page a store reaches that nothing maps, in the order the 3D stores (E996's tile
/// order, a tile's depth then its stencil), the depth buffer at page `depth_page` and the stencil
/// buffer at `stencil_page` of a region of which pages 0 to `mapped - 1` are mapped: E1070
/// (r18-flag f1, held out) measured that a ZLS store faults the job there (0x90200: `FAULT_REQ` bit
/// 9, `FAULT_TYPE` 1) and lands without a fault on a page past its buffer that is mapped (G 3's
/// pages 16 and 18 in t10's colour buffer, the image exact). Formats other than the float and
/// 24-bit ones refuse, as [`store`]'s pages do not decide them here.
pub fn first_unmapped_page(
    ctl: &Ctl,
    w: u32,
    h: u32,
    depth_page: u32,
    stencil_page: Option<u32>,
    mapped: u32,
) -> Result<Option<u32>, Outcome> {
    if !matches!(ctl.format()?, Format::F32 | Format::U24) || ctl.linear_store() {
        return Err(open(format!("the pages of a store through {:#x}: not decided", ctl.word), &["Q071"]));
    }
    for (tx, ty) in visit_order(w, h) {
        if ctl.store_depth() {
            for y in 16 * ty..16 * ty + 16 {
                for x in 32 * tx..32 * tx + 32 {
                    let p = depth_page + store_dword_of(ctl, x, y) / 1024;
                    if p >= mapped {
                        return Ok(Some(p));
                    }
                }
            }
        }
        if let Some(sp) = stencil_page.filter(|_| ctl.store_stencil()) {
            let p = sp + 128 * (ty * (ctl.g() + 1) + tx) / 1024;
            if p >= mapped {
                return Ok(Some(p));
            }
        }
    }
    Ok(None)
}

/// E411's scratch runs (a 16-page scratch at 0x3e001000, the stencil buffer at its page 4, the
/// depth buffer at page 12, a 64 x 64 target): G of 0, 1 and 3 stored and G with any of bits 2 to
/// 8 set (bits 5 to 11 of the control) faulted the job. With the tool's colour buffer right after
/// the scratch (5 pages with its guard, as t10's at 64 x 64: E1070's premise, read from the kept
/// `layout: fb` lines) pages 0 to 20 are mapped, and [`first_unmapped_page`] gives the page of all
/// 14 of E411's faults (0x90200 at 0x3e016 for G 5 and 17, 0x3e017 for G 9, then 0x3e01e, 0x3e02e,
/// 0x3e04e and 0x3e08e for G 33 to 257: post hoc, read at E1070's fold) and none for G 0, 1 and 3.
/// The model refuses those jobs with the fault it predicts (E1070); the same pitches in a large
/// buffer ran (E490 at G = 33), so this is a check of the arrangement, not of the word.
pub fn check_scratch_pitch(ctl: &Ctl) -> Result<(), Outcome> {
    const SCRATCH: u32 = 0x3e00_1000;
    if ctl.g() <= 3 {
        // E411's stores at G 0, 1 and 3, every flip of the other bits among them, ran
        return Ok(());
    }
    match first_unmapped_page(ctl, 64, 64, 12, Some(4), 16 + 5)? {
        Some(p) => Err(Outcome::Fault { addr: SCRATCH + 0x1000 * p, record: "E1070".into() }),
        None => Ok(()),
    }
}

/// The depth store of a W x H target for the control `ctl`: `depth(x, y)` is the depth the tile
/// pass left at the pixel (a measured input, or the plane's: the caller says which). Nothing is
/// stored with the stores off (E411, E466: bit 2 or bit 18 clear), nor in formats 4 and 7 without a
/// stencil buffer (E466, E490: 0 dwords); formats 3 and 4 hold the stencil and are
/// [`store_packed`]'s, 5 to 7 refuse (Q120: E986, stored less where a row repeats one depth; E1031 and E1043's flat
/// tiles are a fixed form not coded here, stored where the plane is one float, E1054). Overlapping tiles (a pitch under the tiles
/// a row needs) store tile by tile in the region header order, so a shared slot holds the tile
/// visited last (E996: 5 of 5 pitches at 64 x 32 to 256 x 64 and format 1 at G 0, every shared
/// dword), in the float format also with edge tiles and at four macrotiles a side (E1041: 65 x 33
/// at G 1 and 640 x 480 at G 2, 2 of 2 held out), and in the integer formats by the floor rule of
/// those floats (E1051: format 2 at 64 x 32 G 0 and 160 x 48 G 2, format 1 at 65 x 33 G 1 and
/// 640 x 480 G 2, 4 of 4 held out). A target with edge tiles
/// stores every dword of its tiles: `depth` inside the band ([`in_band`]), the background 1.0
/// past it (E831, E885, E903), in the float format and, by the floor rule of that float, in the
/// integer formats (E977, E991 at 80 x 40; E1041 at 63 x 31 and 65 x 33, 4 of 4 held out).
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
    let (fmt, g) = (ctl.format()?, ctl.g());
    let banded = |x: u32, y: u32| if in_band(x, y, w, h) { depth(x, y) } else { 1.0 };
    match fmt {
        Format::F32 | Format::U24 => {
            // tile by tile in the order the 3D visits them (E996), a later tile overwriting
            for (tx, ty) in visit_order(w, h) {
                for y in 16 * ty..16 * ty + 16 {
                    for x in 32 * tx..32 * tx + 32 {
                        s.words.insert(
                            store_dword_of(ctl, x, y),
                            encode_depth(fmt, ctl.negate(), banded(x, y))?,
                        );
                    }
                }
            }
        }
        Format::U16 => {
            // tile by tile in the visit order too (E1051's 16-bit overlaps), a row pair a dword
            for (tx, ty) in visit_order(w, h) {
                for y in (16 * ty..16 * ty + 16).step_by(2) {
                    for x in 32 * tx..32 * tx + 32 {
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
    }
    Ok(s)
}

/// The final render's depth store of a job that took `partial_renders` partial renders: [`store`]
/// without one. After one it refuses (Q107): what the store holds is not the scene's depth stored
/// by the address rule. E628: outside a zero region of the first macrotile row it holds the load
/// buffer's dword at each address, load bits or not, and the load buffer comes back zeroed there;
/// E629: its sign bit is set exactly when the first abort's threshold was raised (E625); E1020
/// (round 12 offline): at 1024 x 768 G 1 it is not E996's overlay of the same job's G 33 store
/// (0 of 10 dumps, every G 1 dump a prefix of 15104 zero dwords and then mostly one tile repeated),
/// where the overlay of a job without a partial render holds at that size (E489's G 0, 1 and 2
/// ramps, 6 of 6, every dword). Neither the zero prefix nor the tile order has a rule.
pub fn final_store(
    ctl: &Ctl,
    w: u32,
    h: u32,
    stencil_buffer: bool,
    partial_renders: u32,
    depth: &dyn Fn(u32, u32) -> f32,
) -> Result<Stored, Outcome> {
    if partial_renders > 0 {
        return Err(open(
            format!(
                "the final store of a {w} x {h} job after {partial_renders} partial render(s): the loaded \
                 buffer outside a zero region (E628), the sign by the raise (E629), not the overlay of the \
                 tiles (E1020); no rule gives the zero prefix or the tile order"
            ),
            &["Q107"],
        ));
    }
    store(ctl, w, h, stencil_buffer, depth)
}

/// The byte of the stencil buffer that holds pixel (x, y)'s stencil, for a load and a store alike:
/// 512 bytes a tile slot at the depth's pitch, byte j of the slot the depth's in-tile index
/// (y0 x0 y1 x1 y2 x2 y3 x3 x4, [`in_tile_index`]). E988: through the stencil test, 13 of 13 held-out
/// rows on every byte lane and on 40 x 20's edge tiles, the image and the stored bytes; the raster
/// and the 16-bit format's orders failed.
pub fn stencil_byte(x: u32, y: u32, g: u32) -> u32 {
    512 * ((y >> 4) * (g + 1) + (x >> 5)) + in_tile_index(x, y)
}

/// The background depth (render details dword 16, CR_ISP_BGOBJDEPTH) as the pass starts from it
/// without a load: the word with its sign cleared, as a loaded depth's is (E467). E987: -0.25
/// stored 0.25 in format 0 (with bit 19 -0.25), 0x400000 in format 1 and 0x4000 a half in format
/// 2, bit 19 or not, at every background pixel; -0.0 stored 0; 0.25 and 1.0 stored themselves.
pub fn clear_word(bg: u32) -> u32 {
    bg & 0x7fff_ffff
}

/// Where the stencil test of a render reads its stencil from.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum StencilSource {
    /// the loaded byte at [`stencil_byte`] (E988, control 0x0017300e)
    Loaded,
    /// 0, whatever was loaded: every EQUAL-to-0 test passed and the invert stored 0xff (E989); no
    /// linear map of the loaded bytes gives it (E1014: held out 2 of 2, frozen before the rows)
    Zero,
    /// the test fails at every pixel and the loaded byte is stored unchanged (bit 15 alone: E1042
    /// post hoc, E1053 held out at 96 x 32 G 2 and against reference 1)
    Fail,
    /// [`column_byte`] of the pixel's x, whatever was loaded, stored in the loaded byte's place
    /// (bit 23 alone: E1042 post hoc, E1053 held out at 96 x 32 G 2 and over the index fill)
    Column,
}

/// The byte the stencil test reads under bit 23 alone: one of 0x3f, 0x80 and 0 by x mod 16, in
/// every row (E1042's zb2-b23, E1053 2 of 2 held out; no rule of x found).
pub fn column_byte(x: u32) -> u8 {
    const COL: [u8; 16] = [0x3f, 0x80, 0, 0, 0x80, 0, 0, 0x3f, 0, 0, 0x3f, 0x80, 0, 0x3f, 0x80, 0];
    COL[(x % 16) as usize]
}

/// The control bits E989 flipped together: 15, 21 to 23 and 27 to 31 set, 12, 16 and 20 cleared.
const E989_FLIPPED: u32 = 1 << 15 | 0x7 << 21 | 0x1f << 27;
/// Those bits as the stencil-loading control of E467 and E988 holds them (12, 16 and 20 set).
const E988_INERT: u32 = 1 << 12 | 1 << 16 | 1 << 20;

/// The stencil the test reads under `ctl` with the stencil load on: the loaded one with the bits
/// E411 found inert as E467's control has them (E988) and with bit 16, bit 20 or both cleared
/// (E1030: E988's count and image, 3 of 3 held out); 0 with bits 15, 21 to 23 and 27 to 31 set,
/// with 12, 16 and 20 set (E1030, held out) or cleared (E989). Bit 12 cleared reads another order
/// (E1030, post hoc) and refuses, as any other mix does, or no stencil load (Q071). With E988's
/// inert bits as they are: bits 21, 22 and 27 to 31 alone and 27 to 31 together read the loaded
/// byte (E1042, 1024 drawn and E988's image), 21 to 23 together read 0 (E1042) and so do 21 or 22
/// with 23 (E1053, 2 of 2 held out); bit 15 alone fails ([`StencilSource::Fail`]) and bit 23 alone
/// reads [`column_byte`] (E1053).
pub fn stencil_source(ctl: &Ctl) -> Result<StencilSource, Outcome> {
    if !ctl.load_stencil() {
        return Err(open(
            "a stencil test without a stencil load: its start value is not modelled".into(),
            &["Q071"],
        ));
    }
    let b = ctl.ignored_bits();
    if b == E989_FLIPPED || b == E989_FLIPPED | E988_INERT {
        return Ok(StencilSource::Zero);
    }
    if b & !(1 << 16 | 1 << 20) == 1 << 12 {
        return Ok(StencilSource::Loaded);
    }
    if b & E988_INERT == E988_INERT {
        let set = b & !E988_INERT;
        if set == 1 << 15 {
            return Ok(StencilSource::Fail);
        }
        if set == 1 << 23 {
            return Ok(StencilSource::Column);
        }
        if [5u32 << 21, 6 << 21, 7 << 21].contains(&set) {
            return Ok(StencilSource::Zero);
        }
        if set.count_ones() == 1 && set & (3 << 21 | 0x1f << 27) != 0 || set == 0x1f << 27 {
            return Ok(StencilSource::Loaded);
        }
    }
    Err(open(
        format!(
            "CR_ISP_ZLSCTL's inert bits {b:#x} under a stencil test: only E988's, E989's and E1030's ran"
        ),
        &["Q071"],
    ))
}

/// ISP word 2's test on a stencil byte `s` with the reference `reference` (ISP word 0 bits 7:0):
/// whether the stencil test passes, and the byte stored. E284: (reference & mask) compares with
/// (s & mask) by bits 27:25 (0 never, 1 less, 2 equal, 3 less or equal, 4 greater, 5 not equal,
/// 6 greater or equal, 7 always), mask bits 15:8; the operation is bits 24:22 when the test
/// fails, 21:19 when it passes and the depth fails, 18:16 when both pass (0 keep, 1 zero, 2 the
/// reference, 3 and 4 increment and decrement clamped, 5 invert, 6 and 7 wrapping); bits 7:0 are
/// written; bits 31:28 change nothing. E988 ran EQUAL with invert against loaded stencils.
pub fn stencil_test(isp2: u32, reference: u8, s: u8, depth_pass: bool) -> (bool, u8) {
    let m = (isp2 >> 8) as u8;
    let (r, v) = (reference & m, s & m);
    let pass = match isp2 >> 25 & 7 {
        0 => false,
        1 => r < v,
        2 => r == v,
        3 => r <= v,
        4 => r > v,
        5 => r != v,
        6 => r >= v,
        _ => true,
    };
    let op = if !pass {
        isp2 >> 22
    } else if !depth_pass {
        isp2 >> 19
    } else {
        isp2 >> 16
    } & 7;
    let new = match op {
        0 => s,
        1 => 0,
        2 => reference,
        3 => s.saturating_add(1),
        4 => s.saturating_sub(1),
        5 => !s,
        6 => s.wrapping_add(1),
        _ => s.wrapping_sub(1),
    };
    let wm = isp2 as u8;
    (pass, (s & !wm) | (new & wm))
}

/// The tiles of a W x H target in the order the 3D visits and stores them: the region header
/// order of the library's grid (ta::headers: macrotiles column-major, 4 x 4-region blocks raster
/// inside; E652, E893), held by the overlapping stores of E996.
pub fn visit_order(w: u32, h: u32) -> Vec<(u32, u32)> {
    let t = crate::ta::tiling(w, h);
    let order = crate::ta::header_order(&t, crate::ta::Grid::LIBRARY);
    let mut out = vec![];
    for m in 0..t.n * t.n {
        for &i in &order {
            let (c, r) = ((m / t.n) * t.mx + i % t.mx, (m % t.n) * t.my + i / t.mx);
            if c < t.tx && r < t.ty {
                out.push((c, r));
            }
        }
    }
    out
}

/// The bytes the depth load base drops: render details dword 12 is rounded down to 16 bytes (E1029:
/// +4 loads unmoved, +0x40 moved; E1040 held 16 out of 8 to 64 on five moves, 5 of 5).
pub const LOAD_GRANULE: u32 = 16;

/// The address the depth load reads its first tile from, as an offset from the ZLS base: dword 12
/// rounded down to [`LOAD_GRANULE`] (E1029, E1040); the tiles follow E465's layout from there.
pub fn load_base(rd12: u32) -> u32 {
    rd12 & !(LOAD_GRANULE - 1)
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

/// A W x H target drawn with a flat plane of depth `z` over the pixels `covers` says: [`pass_plane`]
/// with the plane one value.
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
    pass_plane(ctl, w, h, clear, &|_, _| z, test, covers, load_depth, load_stencil)
}

/// A W x H target drawn with a plane whose depth at pixel (x, y) is `z(x, y)` over the pixels
/// `covers` says and E831's band ([`in_band`]: the full-screen triangle's pixel tasks run there
/// past the target), depth test `test`, from the buffers' loaded dwords (`load_depth(i)` and
/// `load_stencil(i)` read dword i of the load buffers, the address the store writes: E467) and
/// the clear depth. Without bits 1 and 14 the pass starts from the clear value (the background
/// depth) with its sign cleared ([`clear_word`], E987), with them from the loaded dword with its
/// sign cleared, compared as a float in every format (E977, E1040; E1050's integer rows); a
/// pixel past the band keeps its start value (E1050: the load kept past the band of 34 x 18,
/// H-EDGE, and E831's background 1.0 without one). Less is strict (E995; E1050 at 0.75 over a
/// loaded 0.75), NaN and infinity loaded are above every depth (E977, E995), and a compare closer
/// than the planes' tolerance refuses (Q200: 12.3's rule). The store encodes every pixel's depth
/// by [`encode_depth`]: bit 19 negates the kept loaded depth too (E1050, 2 of 2), the integer
/// formats take the floor rule. `drawn` counts the target's pixels. The stencil store copies the
/// loaded dword or stores 0 per 128-dword tile slot (E466, E467; a pixel's byte is
/// [`stencil_byte`], E988). Over overlapping tiles (G + 1 under the tiles across) each tile loads
/// its slot's dwords and passes on its own, and a shared slot holds the tile visited last
/// ([`visit_order`]: E1064 at 64 x 32 G 0 and 160 x 48 G 2 with E996's plane, the depth and the
/// stencil load, 4 of 4 held out), edge tiles included (E1068: 65 x 33 G 1 and 63 x 31 G 0 over a
/// 0.2 load, the whole 32 x 16 tile of an edge tile loaded and passed, 2 of 2 held out). A plane depth
/// outside 0 to 1 or NaN refuses (Q069, the z offset's: E1050 ran 0, 0.125, 0.75 and 1; E1059 the planes of 0.0625
/// to 0.625 a no-load twin stores, 7 of 7).
#[allow(clippy::too_many_arguments)]
pub fn pass_plane(
    ctl: &Ctl,
    w: u32,
    h: u32,
    clear: f32,
    z: &dyn Fn(u32, u32) -> f32,
    test: Test,
    covers: &dyn Fn(u32, u32) -> bool,
    load_depth: &dyn Fn(u32) -> u32,
    load_stencil: &dyn Fn(u32) -> u32,
) -> Result<Pass, Outcome> {
    let (tw, th) = (w.div_ceil(32), h.div_ceil(16));
    for y in 0..16 * th {
        for x in 0..32 * tw {
            let d = z(x, y);
            if !(0.0..=1.0).contains(&d) {
                return Err(open(format!("a plane at depth {d}: E1050 ran 0 to 1"), &["Q069"]));
            }
        }
    }
    let mut out = Pass::default();
    let g = ctl.g();
    if ctl.store_depth() {
        let fmt = ctl.format()?;
        let mut depth = std::collections::BTreeMap::new();
        for y in 0..16 * th {
            for x in 0..32 * tw {
                let i = store_dword(x, y, g);
                let base =
                    if ctl.load_depth() { load_word(load_depth(i)) } else { clear_word(clear.to_bits()) };
                let mut v = f32::from_bits(base);
                if covers(x, y) && in_band(x, y, w, h) && test == Test::Less {
                    // the loaded magnitude (sign cleared above), NaN and infinity above every
                    // depth (E977, E995)
                    let zp = z(x, y);
                    let d = if v.is_finite() { zp as f64 - v as f64 } else { f64::NEG_INFINITY };
                    if d.abs() <= f64::from(crate::isp::DEPTH_TOLERANCE) * crate::isp::DEPTH_UNIT && d != 0.0
                    {
                        return Err(open(
                            format!("pixel ({x}, {y}): depths within the planes' tolerance"),
                            &["Q200"],
                        ));
                    }
                    if d < 0.0 {
                        v = zp;
                        if x < w && y < h {
                            out.drawn += 1;
                        }
                    }
                }
                depth.insert((x, y), v);
            }
        }
        // tile by tile in the order the 3D stores them: a slot shared by overlapping tiles keeps
        // the last (E996, E1064)
        let tiles = if g + 1 < tw {
            visit_order(w, h)
        } else {
            (0..th).flat_map(|r| (0..tw).map(move |c| (c, r))).collect()
        };
        for (tx, ty) in tiles {
            for yy in 0..16 {
                for xx in 0..32 {
                    let (x, y) = (32 * tx + xx, 16 * ty + yy);
                    let v = depth[&(x, y)];
                    match fmt {
                        Format::F32 => {
                            out.depth
                                .insert(store_dword(x, y, g), v.to_bits() ^ u32::from(ctl.negate()) << 31);
                        }
                        Format::U24 => {
                            out.depth.insert(store_dword(x, y, g), encode_depth(fmt, ctl.negate(), v)?);
                        }
                        // E490's layout: a row pair a dword, the even row low
                        Format::U16 if y % 2 == 0 => {
                            let lo = encode_depth(fmt, ctl.negate(), v)?;
                            let hi = encode_depth(fmt, ctl.negate(), depth[&(x, y + 1)])?;
                            let slot = (y >> 4) * (g + 1) + (x >> 5);
                            out.depth.insert(256 * slot + in_tile_index16(x, y), lo | hi << 16);
                        }
                        Format::U16 => {}
                    }
                }
            }
        }
    }
    if ctl.store_stencil() {
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
        // the integer formats store the floor rule past the target at even (E977, E991) and odd
        // sizes (E1041: 63 x 31 and 65 x 33, formats 1 and 2, 4 of 4 held out)
        assert!(store(&ctl(0x0017_100c | 1 << 24), 34, 18, false, &d).is_ok());
        assert!(store(&ctl(0x0017_110c | 2 << 24), 34, 18, false, &d).is_ok());
        assert!(store(&ctl(0x0017_100c | 1 << 24), 35, 18, false, &d).is_ok());
        assert!(store(&ctl(0x0017_110c | 2 << 24), 34, 19, false, &d).is_ok());
        // the stencil store of an edge tile: its tiles' 128 dwords a slot (E988's 40 x 20 rows)
        let (_, st) = dword_sets(&ctl(0x0017_110c), 34, 16, true).unwrap();
        assert_eq!(st.len(), 2 * 128);
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
    fn bit_1_without_bit_14_loads_no_depth_e739() {
        // E739: two objects under 0x0017100e drew over the background depth 1.0, not the loaded 0.25:
        // the load needs bit 14 with bit 1 (E664)
        let c = ctl(0x0017_100e);
        assert!(c.load() && !c.load_depth() && c.store_depth());
    }

    #[test]
    fn the_final_store_of_an_overflowed_job_is_refused_e628_e629_e1020() {
        let d = |_: u32, _: u32| 0.3;
        // no partial render: the plain store, E996's overlay at an overlapping pitch
        for (w, h, word) in [(64, 32, 0x0017_1004u32), (34, 18, 0x0017_100c)] {
            assert_eq!(
                final_store(&ctl(word), w, h, false, 0, &d),
                store(&ctl(word), w, h, false, &d),
                "{w}x{h}"
            );
        }
        // after a partial render: the loaded buffer outside a zero prefix (E628), the sign set by the
        // raise (E629), and at 1024 x 768 G 1 not the overlay of the same job's G 33 store (E1020)
        for word in [0x0017_100cu32, 0x0017_110c, 0x0017_510e] {
            match final_store(&ctl(word), 1024, 768, false, 1, &d) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q107"], "{why}");
                    assert!(why.contains("E1020") && why.contains("E628") && why.contains("E629"), "{why}");
                }
                r => panic!("{word:#x}: {r:?}"),
            }
        }
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
        // E985 read 3 to 6 offline (3 and 4 held out by E986: store_packed's); 7 was not decoded
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

    /// E986's zst2 control at 64 x 32: G 1, the stencil loaded (bits 1, 13) and stored (17).
    fn zst2(fmt: u32) -> Ctl {
        ctl(0x0017_300e | fmt << 24)
    }

    fn packed_bytes(s: &Stored) -> std::collections::BTreeMap<u32, u8> {
        s.words.iter().flat_map(|(&i, &v)| (0..4).map(move |q| (4 * i + q, (v >> (8 * q)) as u8))).collect()
    }

    #[test]
    fn format_3_is_a_5_byte_record_a_pixel_in_e985s_blocks() {
        // E985 (SEMI) held out by E986 on every plane: record (x) of row r at byte 160 r + addr
        let depth = |x: u32, y: u32| 0.25 + (x + 32 * y) as f32 / 4096.0;
        let sten = |x: u32, y: u32| (x ^ 7 * y) as u8;
        let s = store_packed(&zst2(3), 64, 32, &depth, &sten).unwrap();
        assert_eq!(s.words.len(), 4 * 640);
        let b = packed_bytes(&s);
        // tile (1, 1) sits in block 2 tw (ty >> 1) + 2 tx + (ty & 1) = 3, 640 dwords a block
        for (tx, ty, blk) in [(0u32, 0u32, 0u32), (1, 0, 2), (0, 1, 1), (1, 1, 3)] {
            for (x, r) in [(0u32, 0u32), (2, 5), (31, 15), (17, 9)] {
                let (px, py) = (32 * tx + x, 16 * ty + r);
                let rec = (depth(px, py).to_bits() | 1 << 31).to_le_bytes();
                let base = 2560 * blk + 160 * r;
                for q in 0..4 {
                    assert_eq!(b[&(base + packed_addr(x, q))], rec[q as usize], "{px} {py} {q}");
                }
                assert_eq!(b[&(base + packed_addr(x, 4))], sten(px, py));
            }
        }
        // E985's address rule: record P byte q at 1 + 17 g + 5 (2 - P mod 3) + q, less 32 from
        // 16 (g + 1) up; the 32 records of a row fill its 160 bytes once each
        assert_eq!((packed_addr(0, 0), packed_addr(2, 0), packed_addr(3, 4)), (11, 1, 0));
        let all: std::collections::BTreeSet<u32> =
            (0..32).flat_map(|p| (0..5).map(move |q| packed_addr(p, q))).collect();
        assert_eq!(all, (0..160).collect());
    }

    #[test]
    fn format_4_stores_0xf0_and_four_stencil_bytes_a_quad_and_no_depth() {
        let sten = |x: u32, y: u32| (3 * x + 64 * y) as u8;
        let s = store_packed(&zst2(4), 64, 32, &|_, _| f32::NAN, &sten).unwrap();
        assert_eq!(s.words.len(), 4 * 160, "E978: 640 dwords at 64 x 32");
        let b = packed_bytes(&s);
        // group n rows 2n, 2n + 1; record m = 8 (y & 1) + x div 4: 0xf0, then x + 3, + 2, + 1, + 0
        let (n, y, qd) = (3u32, 7u32, 5u32);
        let m = 8 * (y & 1) + qd;
        let base = 1024 * 2 + 80 * n; // tile (1, 0) in block 2, 256 dwords a block
        assert_eq!(b[&(base + packed_addr(m, 0))], 0xf0);
        for (q, k) in (1..5).zip([3u32, 2, 1, 0]) {
            assert_eq!(b[&(base + packed_addr(m, q))], sten(32 + 4 * qd + k, y));
        }
    }

    #[test]
    fn the_packed_formats_refuse_what_did_not_run() {
        let z = |_: u32, _: u32| 0.5f32;
        let s = |_: u32, _: u32| 0u8;
        let q120 = |c: u32, w: u32, h: u32| ids(store_packed(&ctl(c), w, h, &z, &s));
        // formats 5 to 7 (E986: they store less where a row repeats a depth), 0 to 2 are store's
        for f in [0u32, 1, 2, 5, 6, 7] {
            assert_eq!(q120(0x0017_300e | f << 24, 64, 32), ["Q120"], "{f}");
        }
        for f in [3u32, 4] {
            // no stencil load (E466's runs without one stored another layout), bit 19, a depth load
            assert_eq!(q120(0x0017_100e | f << 24, 64, 32), ["Q120"], "{f}");
            assert_eq!(q120(0x0017_300e | f << 24 | 1 << 19, 64, 32), ["Q120"], "{f}");
            assert_eq!(q120(0x0017_700e | f << 24, 64, 32), ["Q120"], "{f}");
            // without the stencil store bit (every row ran with bit 17)
            assert_eq!(q120(0x0015_300e | f << 24, 64, 32), ["Q120"], "{f}");
            // tiles across other than G + 1: the two were never parted (E985)
            assert_eq!(q120(0x0017_3016 | f << 24, 64, 32), ["Q120"], "{f}");
            // odd sizes with edge tiles
            assert_eq!(q120(0x0017_300e | f << 24, 41, 20), ["Q120"], "{f}");
        }
        // edge tiles: format 3 ran at 40 x 20 (E986), format 4 did not
        assert!(store_packed(&zst2(3), 40, 20, &z, &s).is_ok());
        assert_eq!(ids(store_packed(&zst2(4), 40, 20, &z, &s)), ["Q120"]);
        // store refuses the packed formats: it has no stencil bytes
        assert_eq!(ids(store(&zst2(3), 64, 32, true, &z)), ["Q120"]);
    }

    #[test]
    fn the_packed_formats_count_their_blocks_and_no_stencil_store() {
        for (f, n) in [(3u32, 640usize), (4, 160)] {
            let (d, st) = dword_sets(&zst2(f), 64, 32, true).unwrap();
            assert_eq!((d.len(), st.len()), (4 * n, 0), "{f}");
            // E985's 96 x 48 at G 2: nine tiles
            let (d, st) = dword_sets(&ctl(0x0017_3016 | f << 24), 96, 48, true).unwrap();
            assert_eq!((d.len(), st.len()), (9 * n, 0), "{f}");
        }
        // E411's flip of bit 26 (format 4, no load) still refuses
        assert_eq!(ids(dword_sets(&ctl(0x0017_100c | 4 << 24), 64, 64, true)), ["Q120"]);
    }

    #[test]
    fn bit_0_writes_no_colour_and_stores_as_without_it_under_e997s_controls() {
        // E411 (control-bits, two runs): 0x0017100c with bit 0 set writes no pixel and stores
        // the control's pages
        let c = ctl(0x0017_100d);
        assert!(!c.writes_pixels());
        assert!(ctl(0x0017_100c).writes_pixels());
        assert_eq!((c.store_depth(), c.store_stencil(), c.g()), (true, true, 1));
        // E997: formats 0, 1, 2 at G 2 and the depth load, each as without bit 0, no colour
        for w in [0x0017_1015u32, 0x0117_1015, 0x0217_1015, 0x0017_500f] {
            let (a, b) = (ctl(w), ctl(w & !1));
            assert!(!a.writes_pixels() && b.writes_pixels(), "{w:#x}");
            assert_eq!(dword_sets(&a, 64, 32, false).unwrap(), dword_sets(&b, 64, 32, false).unwrap());
        }
        // E1063: with the stencil loaded too (E988's st1, bit 16 cleared, formats 6 and 7), 4 of 4
        for w in [0x0017_300fu32, 0x0016_300f, 0x0617_300f, 0x0717_300f, 0x0017_700f] {
            let c = Ctl::decode(w).unwrap();
            assert!(!c.writes_pixels() && c.load_stencil(), "{w:#x}");
        }
        // bit 20 cleared with formats 5 to 7 moved the records (E1063, post hoc)
        assert_eq!(ids(Ctl::decode(0x0607_300e)), ["Q071"]);
        assert_eq!(ids(Ctl::decode(0xffef_ffff)), ["Q071"]);
        assert!(Ctl::decode(0x0007_109c).is_ok(), "format 0: bit 20 cleared changed nothing (E1063)");
    }

    #[test]
    fn the_inert_bits_together_decode_and_bit_16_alone_selects_the_linear_store() {
        // E997: 15, 21 to 23 and 27 to 31 set together change nothing
        let c = ctl(0xf8f7_9014);
        assert_eq!((c.g(), c.format_code(), c.store_depth(), c.linear_store()), (2, 0, true, false));
        // E1030 (r13-zls zbits, 6 of 6 held out): of bits 12, 16 and 20 cleared alone and in pairs
        // on E977's ramp store, exactly the words with bit 16 clear store E997's linear image
        for w in [0x0016_1014u32, 0x0016_0014, 0x0006_1014, 0x0006_0014, 0x0106_0014] {
            assert!(ctl(w).linear_store(), "{w:#x}");
        }
        for w in [0x0017_1014u32, 0x0017_0014, 0x0007_1014, 0x0007_0014] {
            assert!(!ctl(w).linear_store(), "{w:#x}");
        }
        // not run: bit 12 clear with a load (E1030: the stencil load reads another order, post
        // hoc), bit 16 clear with a depth load, a stencil store or the 16-bit format
        for w in [0xf8e6_a00eu32, 0x0017_200e, 0x0016_400e, 0x0216_1014, 0x0006_400e] {
            assert_eq!(ids(Ctl::decode(w)), ["Q071"], "{w:#x}");
        }
        assert_eq!(ids(dword_sets(&ctl(0x0016_3006), 64, 32, true)), ["Q071"], "stencil store");
        // with the tiles across G + 1 the linear stencil store's dwords are the tiled ones (E411's
        // flip of bit 16 at 64 x 64, G 1: the control's pages)
        let (lin, til) =
            (dword_sets(&ctl(0x0016_100c), 64, 64, true), dword_sets(&ctl(0x0017_100c), 64, 64, true));
        assert_eq!(lin.unwrap().1, til.unwrap().1);
        // with nothing loaded or stored (E337's texture attachment value) the word decodes
        assert!(!ctl(0x0014_0008).store_depth());
    }

    #[test]
    fn the_linear_store_holds_the_tiled_values_at_32_g_plus_1_y_plus_x() {
        // E997 (post hoc) and E1030 (zbr-c16, -c12-16, -c16-20 byte for byte E997's dump): dword
        // 32 (G + 1) y + x holds what the tiled store puts at store_dword(x, y, G), edge tiles too
        let (lin, til) = (
            store(&ctl(0x0016_1014), 80, 40, false, &plane).unwrap(),
            store(&ctl(0x0017_1014), 80, 40, false, &plane).unwrap(),
        );
        assert_eq!(lin.words.len(), 4608);
        for y in 0..48 {
            for x in 0..96 {
                assert_eq!(lin.words[&(96 * y + x)], til.words[&store_dword(x, y, 2)], "({x}, {y})");
            }
        }
        let (d, _) = dword_sets(&ctl(0x0016_1014), 80, 40, false).unwrap();
        assert_eq!(d, lin.words.keys().copied().collect());
    }

    fn plane(x: u32, y: u32) -> f32 {
        // every pixel its own depth, as r10-x zov's plane
        0.25 + (y as f32) / 256.0 + (x as f32) / 65536.0
    }

    #[test]
    fn an_overlapping_store_keeps_the_tile_visited_last_in_header_order() {
        // E996: 160 x 48 at G 2, tile (4, 0) shares slot 4 with (1, 1); the header order visits
        // macrotile column 0 (tiles x 0 to 3) before column 1, so (4, 0) is last (raster: (1, 1))
        let s = store(&ctl(0x0017_1014), 160, 48, false, &plane).unwrap();
        for k in 0..512 {
            let (x, y) = in_tile_pixel(k);
            assert_eq!(s.words[&(512 * 4 + k)], plane(128 + x, y).to_bits(), "dword {k}");
        }
        // 64 x 32 at G 0: tile (0, 1) is visited after (1, 0); format 1 by the floor rule
        let s = store(&ctl(0x0117_1004), 64, 32, false, &plane).unwrap();
        let (x, y) = in_tile_pixel(5);
        assert_eq!(s.words[&(512 + 5)], encode_depth(Format::U24, false, plane(x, 16 + y)).unwrap());
    }

    #[test]
    fn an_overlapping_store_refuses_what_e996_and_e1041_did_not_run() {
        // the 16-bit format and the 24-bit one with edge tiles or four macrotiles a side store
        // since E1051 (4 of 4 held out)
        assert!(store(&ctl(0x0217_1004), 64, 32, false, &plane).is_ok());
        assert!(store(&ctl(0x0117_1004), 64, 40, false, &plane).is_ok());
        assert!(store(&ctl(0x0117_1024), 640, 480, false, &plane).is_ok());
        // the float format with edge tiles (E1041's 65 x 33 at G 1) and four macrotiles a side
        // (E1041's 640 x 480 at G 2): the tile the 3D visits last owns the slot
        assert!(store(&ctl(0x0017_1004), 64, 40, false, &plane).is_ok());
        assert!(store(&ctl(0x0017_1024), 640, 480, false, &plane).is_ok());
    }

    #[test]
    fn the_depth_load_base_drops_its_low_4_bits() {
        // E1029's six offset moves and E1040's five (rd:12 = 0x1000 + m, the store dword k holding
        // the depth buffer's dword k + d): of 4 to 128 bytes only a granule of 16 gives all eleven
        for (m, d) in [
            (0x1000u32, 1024u32),
            (0x4000, 4096),
            (0x10000, 16384),
            (0x800, 512),
            (0x40, 16),
            (0x4, 0),
            (0x8, 0),
            (0x10, 4),
            (0x20, 8),
            (0x1008, 1024),
            (0x1020, 1032),
        ] {
            assert_eq!((load_base(0x1000 + m) - 0x1000) / 4, d, "move {m:#x}");
        }
        assert_eq!(LOAD_GRANULE, 16);
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
            // E1051: above 1 clamps, below 0 stores 0; E1064: a kept NaN stores the top
            for z in [-0.5f32, -0.01, 1.01, 1.5, f32::INFINITY] {
                assert!(encode_depth(fmt, false, z).is_ok(), "{fmt:?} {z}");
            }
            let top = if fmt == Format::U24 { 0xff_ffff } else { 0xffff };
            assert_eq!(encode_depth(fmt, false, f32::NAN), Ok(top), "{fmt:?}");
            for z in [0.0f32, 0.2, 0.25, 0.5, 0.75, 0.9, 1.0] {
                assert!(encode_depth(fmt, false, z).is_ok(), "{fmt:?} {z}");
            }
        }
    }

    #[test]
    fn bit_19_changes_no_integer_dword_over_0_to_1() {
        // E490 over 0.25 to 0.4166, E981 over 0 to 0.3: byte-identical dumps with and without it;
        // E987: the background's 0.25 likewise, and no route brings a negative depth to the
        // integer conversion (E981, E987), so over the rest of 0 to 1 it changes nothing [infer]
        for z in [0.0f32, 0.1, ramp_z(7, 1024), 0.4166, 0.5, 0.9, 1.0] {
            for fmt in [Format::U24, Format::U16] {
                assert_eq!(encode_depth(fmt, true, z), encode_depth(fmt, false, z), "{z}");
            }
        }
        // outside 0 to 1 neither (E1051: 1.25 clamps, -0.25 stores 0, bit 19 or not)
        for z in [-0.25f32, 1.5] {
            assert_eq!(encode_depth(Format::U24, true, z), encode_depth(Format::U24, false, z), "{z}");
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
    fn a_pass_takes_edge_tiles_integer_formats_and_whole_overlapping_tiles() {
        // E831's band is the store's without a load; the load and the pass ran on whole tiles
        // since E1050 both run (H-EDGE, H-INT-PASS); overlapping whole tiles since E1064, with edge
        // tiles since E1068
        let r = pass(&ctl(0x0017_110c), 34, 18, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert!(r.is_ok());
        assert!(run(0x0017_110c | 1 << 24, Test::Never, &|i| i).is_ok());
        let r = pass(&ctl(0x0017_1004), 64, 32, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert_eq!(r.unwrap().depth.len(), 3 * 512, "E1064: slots 0 to 2");
        let r = pass(&ctl(0x0017_1004), 65, 32, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i);
        assert_eq!(r.unwrap().depth.len(), 4 * 512, "E1068: 65 x 32 G 0, slots 0 to 3");
    }

    #[test]
    fn a_store_refuses_what_no_run_measured_by_input_alone() {
        let d = |_: u32, _: u32| 0.5f32;
        // overlapping tiles in the 16-bit format: which pixel a shared dword holds was not
        // measured, only how many dwords were written (E465)
        assert!(store(&ctl(0x0017_110c | 2 << 24), 2048, 16, false, &|_, _| 0.25).is_ok(), "E1051");
        // the float format overlapping at four macrotiles a side stores (E1041)
        assert!(store(&ctl(0x0017_100c), 1024, 768, false, &d).is_ok());
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
        assert!(dword_sets(&ctl(0x0017_110c), 34, 16, true).is_ok(), "E988: edge tiles");
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
    fn the_scratch_runs_of_e411_faulted_at_the_first_unmapped_page() {
        // G 0, 1 and 3 (bit 3 cleared, the control, bit 4 set) ran; bits 5 to 11 set faulted at the
        // pages E411's kernel log names (zls/control-bits, both runs of each), E1070's rule
        for w in [0x0017_1004, 0x0017_100c, 0x0017_101c] {
            assert!(check_scratch_pitch(&ctl(w)).is_ok(), "{w:#x}");
        }
        let pages =
            [0x3e01_6000, 0x3e01_7000, 0x3e01_6000, 0x3e01_e000, 0x3e02_e000, 0x3e04_e000, 0x3e08_e000];
        for (b, want) in (5..=11).zip(pages) {
            match check_scratch_pitch(&ctl(0x0017_100c ^ 1 << b)) {
                Err(Outcome::Fault { addr, record }) => {
                    assert_eq!((addr, record.as_str()), (want, "E1070"), "bit {b}")
                }
                o => panic!("bit {b}: {o:?}"),
            }
        }
    }

    #[test]
    fn a_store_faults_at_its_first_unmapped_page_as_e1070() {
        // r18-flag f1 (t10, a 16-page depth buffer at 0x3e001000, the ZLS base 0x3e000000 with
        // rd:13 = 0xd000, so the store starts at buffer page 12; the colour buffer maps pages 16 to
        // 20): G 3 stores pages 12, 14, 16 and 18, all mapped; G 5 faults at page 21 (0x3e016000)
        assert_eq!(first_unmapped_page(&ctl(0x0017_101c), 64, 64, 12, None, 21), Ok(None));
        assert_eq!(first_unmapped_page(&ctl(0x0017_102c), 64, 64, 12, None, 21), Ok(Some(21)));
        // past the buffer alone (H-PAST-ANY, refuted) G 3 would fault at page 16
        assert_eq!(first_unmapped_page(&ctl(0x0017_101c), 64, 64, 12, None, 16), Ok(Some(16)));
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
    fn a_pass_negates_with_bit_19_with_and_without_a_load() {
        let p =
            pass(&ctl(0x0017_110c | 1 << 19), 32, 16, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i)
                .unwrap();
        assert!(p.depth.values().all(|&v| v == 0xbf80_0000));
        // with a load the kept depth is stored negated too (E1050)
        let p =
            pass(&ctl(0x0017_510e | 1 << 19), 32, 16, 1.0, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i)
                .unwrap();
        assert!(p.depth.iter().all(|(&i, &v)| v == i | 1 << 31));
    }

    #[test]
    fn a_pass_refuses_a_triangle_depth_outside_0_to_1_and_nan() {
        for z in [5.0f32, -1.0, f32::NAN, f32::INFINITY] {
            let r = pass(&ctl(0x0017_110c), 32, 16, 1.0, z, Test::Never, &|_, _| true, &|i| i, &|i| i);
            assert_eq!(ids(r), ["Q069"], "{z}");
        }
        // E467, E411 and the ramps, and since E1050 0 to 1 (0, 0.125, 0.75, 1 held out)
        for z in [0.5f32, 0.25, 0.4166, 0.0, 0.9, 1.0] {
            assert!(
                pass(&ctl(0x0017_110c), 32, 16, 1.0, z, Test::Never, &|_, _| true, &|i| i, &|i| i).is_ok()
            );
        }
    }

    #[test]
    fn a_loaded_infinity_or_nan_is_above_every_depth_under_less() {
        // E977 (NaN and infinity under less, against 0.5) and E995 (NaN above every depth under
        // the compares 2, 3, 5, 6): with its sign cleared the loaded dword compares as a magnitude
        for v in [0x7f80_0000u32, 0x7fc0_0000, 0xff80_0000, 0x7fff_ffff] {
            let p = run(0x0017_510e, Test::Less, &|_| v).unwrap();
            assert_eq!(p.drawn, 2048, "{v:#x}");
            assert!(p.depth.values().all(|&d| d == 0x3f00_0000), "{v:#x}");
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

    #[test]
    fn a_negative_background_depth_is_stored_with_its_sign_cleared() {
        // E987: render details dword 16 at -0.25 stored 0.25 at every background pixel in format
        // 0 (bit 19: -0.25), 0x400000 in format 1 and 0x4000 a half in format 2, bit 19 or not;
        // -0.0 stored 0
        assert_eq!(clear_word(0xbe80_0000), 0x3e80_0000);
        assert_eq!(clear_word(0x8000_0000), 0);
        assert_eq!(clear_word(0x3f80_0000), 0x3f80_0000);
        let never = |c: u32, clear: f32| {
            pass(&ctl(c), 64, 32, clear, 0.5, Test::Never, &|_, _| true, &|i| i, &|i| i).unwrap()
        };
        assert!(never(0x0017_110c, -0.25).depth.values().all(|&v| v == 0x3e80_0000));
        assert!(never(0x0017_110c | 1 << 19, -0.25).depth.values().all(|&v| v == 0xbe80_0000));
        assert!(never(0x0017_110c, -0.0).depth.values().all(|&v| v == 0));
        let z = f32::from_bits(clear_word(0xbe80_0000));
        for neg in [false, true] {
            assert_eq!(encode_depth(Format::U24, neg, z), Ok(0x40_0000));
            assert_eq!(encode_depth(Format::U16, neg, z), Ok(0x4000));
        }
    }

    #[test]
    fn a_pixels_stencil_byte_follows_the_depths_in_tile_order() {
        // E988: byte j of the tile slot's 512 is the depth's in-tile index y0 x0 y1 x1 y2 x2 y3
        // x3 x4, every lane and the edge tiles (E985 read lane 0 from E978's dumps)
        assert_eq!(stencil_byte(0, 0, 1), 0);
        assert_eq!(stencil_byte(0, 1, 1), 1);
        assert_eq!(stencil_byte(1, 0, 1), 2);
        assert_eq!(stencil_byte(1, 1, 1), 3);
        assert_eq!(stencil_byte(16, 0, 1), 256);
        assert_eq!(stencil_byte(32, 0, 1), 512);
        assert_eq!(stencil_byte(0, 16, 1), 1024);
        assert_eq!(stencil_byte(31, 15, 0), 511);
        let mut all: Vec<u32> = (0..32).flat_map(|y| (0..64).map(move |x| stencil_byte(x, y, 1))).collect();
        all.sort_unstable();
        assert_eq!(all, (0..2048).collect::<Vec<_>>());
    }

    #[test]
    fn the_stencil_test_compares_the_reference_with_the_masked_byte() {
        // E284's fields, E988's rows: EQUAL against reference 0 with mask m draws iff s & m == 0,
        // and the pass operation invert stores !s; a failing byte is kept (operation 0)
        for s in 0..=255u8 {
            let (p, v) = stencil_test(0x0405_01ff, 0, s, true);
            assert_eq!(p, s & 1 == 0, "{s}");
            assert_eq!(v, if p { !s } else { s });
            assert_eq!(stencil_test(0x0e05_ffff, 0, s, true), (true, !s), "always");
            assert_eq!(stencil_test(0x0005_ffff, 0, s, true), (false, s), "never");
        }
        // E284: replace writes the reference through the write mask; bits 31:28 change nothing;
        // the depth-fail operation (bits 21:19) acts when the stencil passes and the depth fails
        assert_eq!(stencil_test(0x0e02_ff0f, 0x55, 0xf0, true), (true, 0xf5));
        assert_eq!(stencil_test(0xfe02_ff0f, 0x55, 0xf0, true), (true, 0xf5));
        assert_eq!(stencil_test(0x0e10_ffff, 0x55, 0xf0, false), (true, 0x55));
        assert_eq!(stencil_test(0x0e03_ffff, 0, 0xff, true), (true, 0xff), "increment clamps");
        assert_eq!(stencil_test(0x0e06_ffff, 0, 0xff, true), (true, 0), "increment wraps");
        assert_eq!(stencil_test(0x0e04_ffff, 0, 0, true), (true, 0), "decrement clamps");
        assert_eq!(stencil_test(0x0e07_ffff, 0, 0, true), (true, 0xff), "decrement wraps");
    }

    #[test]
    fn the_inert_control_bits_flipped_together_make_the_test_read_zero() {
        // E988's control 0x0017300e reads the loaded stencil; E989: with bits 15, 21 to 23 and 27
        // to 31 set and 12, 16 and 20 cleared together it reads 0 (every EQUAL row drew all and
        // stored 0xff); which of the bits does it, or any other mix, is Q071's
        assert_eq!(stencil_source(&ctl(0x0017_300e)), Ok(StencilSource::Loaded));
        // the word decodes to a refusal since E997 (bits 12, 16 and 20 cleared store a linear image)
        assert!(Ctl::decode(0xf8e6_a00e).is_err());
        assert_eq!(stencil_source(&Ctl { word: 0xf8e6_a00e }), Ok(StencilSource::Zero));
        assert_eq!(stencil_source(&ctl(0x0017_300e | 1 << 15)), Ok(StencilSource::Fail), "E1053");
        assert_eq!(stencil_source(&ctl(0x0017_300e | 1 << 21)), Ok(StencilSource::Loaded), "E1042");
        assert_eq!(ids(stencil_source(&ctl(0x0017_300e | 1 << 15 | 1 << 27))), ["Q071"], "not run");
        assert_eq!(ids(stencil_source(&ctl(0x0017_100e))), ["Q071"], "no stencil load");
    }

    #[test]
    fn the_set_half_alone_makes_the_test_read_zero_and_bits_16_20_keep_the_loaded_byte() {
        // E1030 (r13-zls zbits, Z-SET 7 of 7 held out): bits 15, 21 to 23 and 27 to 31 set with 12,
        // 16 and 20 kept set read 0 (2048 drawn, every stored byte 0xff)
        assert_eq!(stencil_source(&ctl(0xf8f7_b00e)), Ok(StencilSource::Zero));
        // 16, 20 or both cleared: E988's 1024 drawn and its image, the loaded byte
        for w in [0x0016_300eu32, 0x0007_300e, 0x0006_300e] {
            assert_eq!(stencil_source(&Ctl { word: w }), Ok(StencilSource::Loaded), "{w:#x}");
        }
        // 12 cleared: 1024 drawn but another byte order (post hoc: a linear image of 64-byte
        // rows), not modelled
        for w in [0x0017_200eu32, 0x0016_200e, 0x0007_200e] {
            assert_eq!(ids(stencil_source(&Ctl { word: w })), ["Q071"], "{w:#x}");
        }
    }

    /// bit:K's fill of the r15-zls rows: 0.75 where bit K of the dword index is set, else 0.25
    fn bit_fill(k: u32) -> impl Fn(u32) -> u32 {
        move |i| if i >> k & 1 == 1 { 0.75f32.to_bits() } else { 0.25f32.to_bits() }
    }

    #[test]
    fn a_pass_over_edge_tiles_tests_the_band_and_keeps_the_load_past_it_e1050() {
        // E1050's zp-e-dp: 34 x 18, the load and store enables at G 1, bit:3 (x bit 1), less at
        // 0.5: in E831's band the pass tests the loaded depth, past it the loaded depth is kept
        let ld = bit_fill(3);
        let p = pass(&ctl(0x0017_500e), 34, 18, 1.0, 0.5, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
        assert_eq!((p.depth.len(), p.drawn), (2048, 288));
        for y in 0..32 {
            for x in 0..64 {
                let i = store_dword(x, y, 1);
                let l = ld(i);
                let want = if in_band(x, y, 34, 18) && l == 0.75f32.to_bits() { 0.5f32.to_bits() } else { l };
                assert_eq!(p.depth[&i], want, "({x}, {y})");
            }
        }
        // without the load: the band 0.5 and the background 1.0 past it (zp-c-band, E831)
        let p = pass(&ctl(0x0017_100c), 34, 18, 1.0, 0.5, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
        assert_eq!(p.drawn, 612);
        assert_eq!(p.depth.values().filter(|&&v| v == 0.5f32.to_bits()).count(), 42 * 22);
    }

    #[test]
    fn a_pass_with_bit_19_and_a_load_stores_every_depth_negated_e1050() {
        // E1050's zp-19-nv and zp-19-ls: the kept depth (sign cleared, E467) is stored negated,
        // as the drawn one is
        let ld = bit_fill(9);
        let c = ctl(0x0017_500e | 1 << 19);
        let p = pass(&c, 64, 32, 1.0, 0.5, Test::Never, &|_, _| true, &ld, &|i| i).unwrap();
        assert!(p.depth.iter().all(|(&i, &v)| v == ld(i) | 1 << 31));
        let p = pass(&c, 64, 32, 1.0, 0.5, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
        assert_eq!(p.drawn, 1024);
        let n = |v: u32| p.depth.values().filter(|&&d| d == v).count();
        assert_eq!((n(0xbf00_0000), n(0xbe80_0000)), (1024, 1024));
    }

    #[test]
    fn a_pass_in_an_integer_format_compares_the_loaded_float_and_stores_the_floor_e1050() {
        // E1050's zp-f1 and zp-f2 at 0.375 over bit:9: the loaded dword compares as a float
        // (E977, E1040) and the store takes the floor rule of the depth kept or drawn
        let ld = bit_fill(9);
        let p = pass(&ctl(0x0117_500e), 64, 32, 1.0, 0.375, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
        assert_eq!(p.drawn, 1024);
        let mut v: Vec<u32> = p.depth.values().copied().collect();
        v.dedup();
        assert_eq!(p.depth.len(), 2048);
        assert!(p.depth.values().all(|&d| d == 0x40_0000 || d == 0x60_0000));
        let p = pass(&ctl(0x0217_500e), 64, 32, 1.0, 0.375, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
        assert_eq!((p.depth.len(), p.drawn), (1024, 1024));
        assert!(p.depth.values().all(|&d| d == 0x4000_4000 || d == 0x6000_6000));
    }

    #[test]
    fn a_pass_takes_a_plane_at_any_depth_of_0_to_1_strictly_less_e1050() {
        // E1050's zp-z0, zp-z75, zp-z1 (and zp-z125's drawn count) over 0.25 / 0.75 halves:
        // the compare is strict (E995), the store holds the plane's depth where it drew
        let ld = bit_fill(9);
        for (z, drawn) in [(0.0f32, 2048u64), (0.125, 2048), (0.75, 0), (1.0, 0)] {
            let p = pass(&ctl(0x0017_500e), 64, 32, 1.0, z, Test::Less, &|_, _| true, &ld, &|i| i).unwrap();
            assert_eq!(p.drawn, drawn, "{z}");
        }
        // a plane given per pixel (zp-z125 stored 1 to 9 ulps below 0.125, Q200's dyadic error)
        let plane = |x: u32, _: u32| f32::from_bits(0.125f32.to_bits() - 1 - x / 8);
        let p = pass_plane(&ctl(0x0017_500e), 64, 32, 1.0, &plane, Test::Less, &|_, _| true, &ld, &|i| i)
            .unwrap();
        assert_eq!(p.depth[&store_dword(63, 0, 1)], 0.125f32.to_bits() - 8);
        for z in [-0.25f32, 1.25, f32::NAN] {
            let r = pass(&ctl(0x0017_500e), 64, 32, 1.0, z, Test::Less, &|_, _| true, &ld, &|i| i);
            assert_eq!(ids(r), ["Q069"], "{z}");
        }
    }

    #[test]
    fn the_integer_formats_clamp_above_1_and_store_0_below_0_e1051() {
        // E1051: the z offset at 1.25 stored 0xffffff and 0xffff, at -0.25 0 in both (E981)
        for neg in [false, true] {
            assert_eq!(encode_depth(Format::U24, neg, 1.25), Ok(0xff_ffff));
            assert_eq!(encode_depth(Format::U16, neg, 1.25), Ok(0xffff));
            assert_eq!(encode_depth(Format::U24, neg, -0.25), Ok(0));
            assert_eq!(encode_depth(Format::U16, neg, -0.25), Ok(0));
        }
        assert_eq!(encode_depth(Format::U24, false, f32::from_bits(0x7f80_0001)), Ok(0xff_ffff));
    }

    #[test]
    fn overlapping_integer_stores_keep_the_tile_visited_last_e1051() {
        // E1051: format 2 at 64 x 32 G 0 and 160 x 48 G 2, format 1 at 65 x 33 G 1 and 640 x 480
        // G 2 hold the last-visited tile's pixels by the floor rule
        for (word, w, h) in
            [(0x0217_1004u32, 64, 32), (0x0217_1014, 160, 48), (0x0117_100c, 65, 33), (0x0117_1014, 640, 480)]
        {
            assert!(store(&ctl(word), w, h, false, &plane).is_ok(), "{word:#x} {w} x {h}");
        }
        // 160 x 48 G 2 in format 2: slot 4 holds tile (4, 0), row pair (0, 1) of its pixel 0
        let s = store(&ctl(0x0217_1014), 160, 48, false, &plane).unwrap();
        let e = |x, y| encode_depth(Format::U16, false, plane(x, y)).unwrap();
        assert_eq!(s.words[&(256 * 4)], e(128, 0) | e(128, 1) << 16);
    }

    #[test]
    fn the_stencil_test_under_bits_15_and_23_and_their_pairs_e1053() {
        // E1053: bit 15 alone fails every pixel and keeps the loaded byte (96 x 32 G 2 and against
        // reference 1); bit 23 alone reads a byte of x mod 16 (96 x 32 and the index fill); 21 or
        // 22 with 23 read 0, as 21 to 23 together (E1042)
        assert_eq!(stencil_source(&ctl(0x0017_300e | 1 << 15)), Ok(StencilSource::Fail));
        assert_eq!(stencil_source(&ctl(0x0017_300e | 1 << 23)), Ok(StencilSource::Column));
        for w in [0x0017_300e | 5 << 21, 0x0017_300e | 6 << 21, 0x0017_300e | 7 << 21] {
            assert_eq!(stencil_source(&ctl(w)), Ok(StencilSource::Zero), "{w:#x}");
        }
        assert_eq!(column_byte(0), 0x3f);
        assert_eq!((0..16).filter(|&x| column_byte(x) & 1 == 0).count(), 12);
        assert_eq!(column_byte(17), column_byte(1));
    }
}
