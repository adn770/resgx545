// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! TA (tiling engine and object writer): the region test (E542), the object's vertex layout (E541)
//! and, from 12.2, the writer: one object for up to five triangles at the start of the parameter
//! buffer, the region headers in the TA data and one control-stream block per region the object
//! meets, byte for byte as the dumps hold them (E176, E177, E180, E651, E652). The target sizes
//! are those the library's tiling rule gives with two macrotiles in a row (E174, E331); lines,
//! points, several objects and the other TE words refuse.

use crate::Outcome;
use crate::mte::{State, Vertex};
use std::collections::BTreeMap;

pub const OPEN: &[&str] =
    &["Q070", "Q100", "Q139", "Q086", "Q159", "Q160", "Q161", "Q164", "Q165", "Q068", "Q230", "Q231"];

/// The unit as a whole, for a vector kind the replay has no inputs for.
pub fn refuse() -> Outcome {
    Outcome::unsupported(
        "the tiling engine writes one object of up to five triangles on the library's tiling only",
        OPEN,
    )
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

/// The library's tiling for a w x h target (sgxfive_tiling; E174, E331: it renders exactly at
/// 222 sizes): the TE words and the macrotile geometry. `n` macrotiles across and down.
#[derive(Debug, Clone, PartialEq)]
pub struct Tiling {
    pub tx: u32,
    pub ty: u32,
    pub n: u32,
    pub mx: u32,
    pub my: u32,
    pub te_screen: u32,
    pub mtile1: u32,
    pub mtile2: u32,
    pub stride: u32,
}

pub fn tiling(w: u32, h: u32) -> Tiling {
    let (tx, ty) = (w.div_ceil(32), h.div_ceil(16));
    let n = if w as u64 * h as u64 >= 640 * 480 { 4 } else { 2 };
    let (mx, my) = ((tx.div_ceil(n) + 3) & !3, (ty.div_ceil(n) + 3) & !3);
    let mtile =
        |m: u32| (m / 4) << 24 | (if n == 4 { 2 * m } else { m }) << 12 | if n == 4 { 3 * m } else { m };
    Tiling {
        tx,
        ty,
        n,
        mx,
        my,
        te_screen: (ty - 1) << 12 | (tx - 1),
        mtile1: mtile(mx) | if n == 4 { 1 << 31 } else { 0 },
        mtile2: mtile(my),
        stride: 16 * (mx / 4) * (my / 4),
    }
}

fn refuse_ids(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

/// Where the object starts in the parameter slot (the dump's first dword is at this offset) and the
/// dword address its ISP address is counted in (E177: 0x406 for one triangle).
pub const OBJECT_AT: u32 = 0x1000;
/// The first control-stream page and the TA data dump's offset of the first region header.
pub const STREAM_AT: u32 = 0x2000;
pub const HEADERS_AT: u32 = 0x4000;
const STREAM_STEP: u32 = 0x80;
const PAGE: u32 = 0x1000;

/// The 24-bit field of a window coordinate: (c + 4096) * 256. A multiple of 1/256 is exact; one on
/// the 1/1024 grid is rounded to the nearest 1/256 (E778: 18 of 18 coordinates of three held-out
/// triangles, truncation refuted 3 of 3). What E778 did not run stays refused: a tie (an exact half
/// step), a grid finer than 1/1024 and anything the field cannot hold.
fn pack_coordinate(c: f32) -> Option<u64> {
    let q = (c as f64 + 4096.0) * 256.0;
    let frac = q.fract();
    let r = match frac {
        0.0 => q,
        0.25 | 0.75 => q.round(),
        _ => return None,
    };
    (0.0..16777216.0).contains(&r).then_some(r as u64)
}

/// The object's dwords for the triangles (window coordinates), at the start of the parameter buffer:
/// three PDS words, the 1/w of each vertex, ISP words, primitive list, line widths, format word,
/// four masks, packed vertices (E176, E181, E308, E541, E651).
pub fn object_words(tris: &[[Vertex; 3]], st: &State) -> Result<Vec<u32>, Outcome> {
    if tris.is_empty() || tris.len() > 5 {
        return Err(refuse_ids(
            format!(
                "an object of {} triangles: the 5-bit vertex numbers 16 to 31 hold 15 vertices, the splitting of longer lists is Q070 (E546)",
                tris.len()
            ),
            &["Q070"],
        ));
    }
    let nv = 3 * tris.len();
    let lay = object_layout(0, 0, 0)?; // position only: the 1/w alone is stored
    let mut w = st.pds.to_vec();
    w.extend(tris.iter().flatten().map(|v| v.rhw.to_bits()));
    w.extend(st.isp);
    let mut entries = vec![];
    for (p, t) in tris.iter().enumerate() {
        let area = (t[1].x - t[0].x) as f64 * (t[2].y - t[0].y) as f64
            - (t[2].x - t[0].x) as f64 * (t[1].y - t[0].y) as f64;
        if area == 0.0 {
            return Err(refuse_ids(
                "a triangle with no area: the winding mark has no record for it",
                &["Q230"],
            ));
        }
        let n = 16 + 3 * p as u32;
        entries.push(n | (n + 1) << 5 | (n + 2) << 10 | u32::from(area < 0.0) << 15);
    }
    for pair in entries.chunks(2) {
        w.push(pair[0] | pair.get(1).unwrap_or(&pair[0]) << 16);
    }
    // line widths: ISP word 1 bits 15:8 in both bytes (E176)
    let lw = st.isp[1] >> 8 & 0xff;
    w.push(lw | lw << 8);
    w.push(lay.format_hi << 16 | lay.iterated << 8 | lay.stored);
    w.extend(lay.masks);
    // the packed vertices: Y then X as 24-bit (v + 4096) * 256, then the depth float, 80 bits a vertex
    let mut bits: Vec<bool> = vec![];
    let mut push = |v: u64, n: u32| bits.extend((0..n).map(|i| v >> i & 1 != 0));
    for v in tris.iter().flatten() {
        for c in [v.y, v.x] {
            let Some(q) = pack_coordinate(c) else {
                return Err(refuse_ids(
                    format!(
                        "window coordinate {c}: off the 1/1024 grid, a tie of the rounding to 1/256 or past the 24-bit field: how the TA rounds it was not dumped (E778)"
                    ),
                    &["Q230"],
                ));
            };
            push(q, 24);
        }
        push(v.z.to_bits() as u64, 32);
    }
    debug_assert_eq!(bits.len(), 80 * nv);
    for chunk in bits.chunks(32) {
        w.push(chunk.iter().enumerate().fold(0u32, |a, (i, &b)| a | u32::from(b) << i));
    }
    Ok(w)
}

fn vmask(set: u32) -> u32 {
    (0..5).filter(|k| set >> k & 1 != 0).fold(0, |a, k| a | 7 << (3 * k))
}

/// The control-stream words of a region for the primitives that meet its left and right 16 x 16
/// tiles (bit k = primitive k) of an object of `nprims` triangles whose ISP words are at dword
/// address `isp`: the primitive word, the object word, and a further dword for the wide forms
/// (E177, E180, E652).
pub fn stream_words(nprims: u32, left: u32, right: u32, isp: u32) -> Result<Vec<u32>, Outcome> {
    if !(1..=5).contains(&nprims) {
        return Err(refuse_ids(format!("a stream for an object of {nprims} primitives"), &["Q070"]));
    }
    let all = (1 << nprims) - 1;
    if (left | right) & !all != 0 || left | right == 0 {
        return Err(refuse_ids(
            "a region with no primitive, or a primitive the object does not have",
            &["Q231"],
        ));
    }
    let head = 2 << 29 | (3 * nprims - 1) << 25;
    let obj = (2 * nprims - 1) << 26 | isp;
    let word = |form: u32, low: u32| head | form << 16 | low;
    if left == all && right == all {
        return Ok(vec![word(0x90, 0xffff), obj]);
    }
    // one tile: the narrow form (primitive mask 7:0, vertex mask 15:8) while the vertex mask fits a
    // byte, else the wide one with the primitive mask in a further dword; both tiles with different
    // masks: always the wide 0x88 with both masks in the further dword (E180, E652)
    Ok(match (left, right) {
        (l, 0) if vmask(l) <= 0xff => vec![word(0x80, vmask(l) << 8 | l), obj],
        (0, r) if vmask(r) <= 0xff => vec![word(0x98, vmask(r) << 8 | r), obj],
        (l, 0) => vec![word(0x8a, vmask(l)), obj, l],
        (0, r) => vec![word(0x8c, vmask(r)), obj, r],
        (l, r) => vec![word(0x88, vmask(l | r)), obj, r << 16 | l],
    })
}

/// The region grid of the TA: the library's 32 x 16 regions, or with `CR_TE_AA` bit 29 set, bit 31
/// halving a region's width and bit 30 its height (E893, held out at 128 x 128; fitted on E504's
/// 64 x 64 dumps). A macrotile keeps its pixel area and number, so it holds twice the regions
/// along a halved axis.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Grid {
    pub half_width: bool,
    pub half_height: bool,
}

impl Grid {
    pub const LIBRARY: Grid = Grid { half_width: false, half_height: false };

    /// The grid of a `CR_TE_AA` word: bits 31 and 30 with bit 29 (E893); 0 and bit 29 alone are
    /// the library's (E504, E281). Bit 30 or 31 without bit 29 removes the triangle (E281) and
    /// shifts the object (E888): the TA data as with bit 29, the parameter buffer's dwords 11 to
    /// 26 one dword on and an empty image (E728, E825, E827), a zero dword inserted before the
    /// object's format word (E847, E865), which the 3D reads in the old layout, render 2's object
    /// as render 1's (E829, E897, E906): refused (Q142), as is any other bit.
    pub fn from_te_aa(te_aa: u32) -> Result<Grid, Outcome> {
        if te_aa & !0xe000_0000 != 0 || (te_aa & 0xc000_0000 != 0 && te_aa & 0x2000_0000 == 0) {
            return Err(refuse_ids(
                format!(
                    "CR_TE_AA {te_aa:#x}: only bits 31 and 30 with bit 29 are a region grid (E893); without bit 29 the triangle is removed (E281, E888) and the object stored with a zero before its format word (E728, E825, E827, E847, E865), read by the 3D in that layout (E829, E897, E906)"
                ),
                &["Q142"],
            ));
        }
        Ok(Grid { half_width: te_aa >> 31 & 1 != 0, half_height: te_aa >> 30 & 1 != 0 })
    }

    /// A region's width and height in pixels.
    pub fn region(&self) -> (u32, u32) {
        (32 >> u32::from(self.half_width), 16 >> u32::from(self.half_height))
    }

    /// The regions of a macrotile across and down.
    pub fn per_macrotile(&self, t: &Tiling) -> (u32, u32) {
        (t.mx << u32::from(self.half_width), t.my << u32::from(self.half_height))
    }
}

/// A region header's word 0 (position and flags) for every region of every macrotile, in header
/// order, and whether the region has a stream (`has_stream(macrotile, local index)`, the local
/// index `row * across + column` in the grid's regions): bit 25 outside the target, 26 the first
/// and 28 the last header of a macrotile with target regions, 27 a target region without a
/// stream, 31 the last header of the scene's last such macrotile (E177, E178, E652). The position
/// fields count 16 pixels in x (bits 23:16) and 8 in y (bits 11:0) on every grid, and a
/// macrotile's headers are written in 4 x 4-region sub-blocks, raster order across them and
/// inside one (E893; a library macrotile is one sub-block).
pub fn headers(
    t: &Tiling,
    w: u32,
    h: u32,
    grid: Grid,
    has_stream: &dyn Fn(u32, u32) -> bool,
) -> Vec<(u32, bool)> {
    let (fx, fy) = grid.per_macrotile(t);
    let (rw, rh) = grid.region();
    let at = |m: u32, i: u32| ((m / t.n) * fx + i % fx, (m % t.n) * fy + i / fx);
    let inside = |m: u32, i: u32| {
        let (c, r) = at(m, i);
        rw * c < w && rh * r < h
    };
    let order = header_order(t, grid);
    let last_macro = (0..t.n * t.n).rev().find(|&m| order.iter().any(|&i| inside(m, i)));
    let mut out = vec![];
    for m in 0..t.n * t.n {
        let ins: Vec<u32> = order.iter().copied().filter(|&i| inside(m, i)).collect();
        for &i in &order {
            let (c, r) = at(m, i);
            let stream = inside(m, i) && has_stream(m, i);
            let mut f = 0u32;
            if !inside(m, i) {
                f |= 0x02;
            } else if !stream {
                f |= 0x08;
            }
            if ins.first() == Some(&i) {
                f |= 0x04;
            }
            if ins.last() == Some(&i) {
                f |= 0x10;
                if last_macro == Some(m) {
                    f |= 0x80;
                }
            }
            out.push(((f << 24) | ((c * rw / 16) << 16) | ((r * rh / 8) & 0xfff) | (m << 12), stream));
        }
    }
    out
}

/// The stream block of every region with a stream (`has_stream(macrotile, local index)`): the
/// macrotiles with streams in raster order (rows outer), each from a new page and taking as many
/// pages as its streams fill, 128 bytes a stream in the order of `walk` over the grid's regions
/// (E652; two pages for one macrotile's 64 streams, E893).
pub fn stream_blocks(
    t: &Tiling,
    grid: Grid,
    has_stream: &dyn Fn(u32, u32) -> bool,
) -> BTreeMap<(u32, u32), u32> {
    let (fx, fy) = grid.per_macrotile(t);
    let mut addr = BTreeMap::new();
    let mut page = STREAM_AT;
    for my in 0..t.n {
        for mxi in 0..t.n {
            let m = mxi * t.n + my;
            let mut k = 0;
            for i in walk(fx, fy) {
                if has_stream(m, i) {
                    addr.insert((m, i), page + STREAM_STEP * k);
                    k += 1;
                }
            }
            page += PAGE * k.div_ceil(PAGE / STREAM_STEP);
        }
    }
    addr
}

/// A macrotile's local region indices (`row * across + column`) in header order: 4 x 4-region
/// blocks in raster order, raster inside one, on every grid: a 4 x 4 library macrotile is one
/// block (E652), the 8 x 8 ones of 640 x 480 hold four (E907's and E944's baselines, 600 of 600
/// headers at R7-BLK's slots), a halved grid's too (E893).
pub fn header_order(t: &Tiling, grid: Grid) -> Vec<u32> {
    let (fx, fy) = grid.per_macrotile(t);
    let mut order: Vec<u32> = (0..fx * fy).collect();
    order.sort_by_key(|&i| {
        let (c, r) = (i % fx, i / fx);
        (r / 4, c / 4, r % 4, c % 4)
    });
    order
}

/// The TA data's region headers (word 0 and the stream word) by dump offset, for the target
/// regions with a stream (`has_stream(macrotile, local index)`; a region outside the target has
/// none). A halved grid on macrotiles other than 4 x 4 regions refuses: E893 measured 4 x 4 only.
pub fn region_data(
    t: &Tiling,
    w: u32,
    h: u32,
    grid: Grid,
    has_stream: &dyn Fn(u32, u32) -> bool,
) -> Result<BTreeMap<u32, u32>, Outcome> {
    if grid != Grid::LIBRARY && (t.mx, t.my) != (4, 4) {
        return Err(refuse_ids(
            format!(
                "{w} x {h}: a halved region grid on macrotiles of {} x {} regions; E893's dumps had 4 x 4",
                t.mx, t.my
            ),
            &["Q142"],
        ));
    }
    let (fx, fy) = grid.per_macrotile(t);
    let (rw, rh) = grid.region();
    let inside = |m: u32, i: u32| {
        let (c, r) = ((m / t.n) * fx + i % fx, (m % t.n) * fy + i / fx);
        rw * c < w && rh * r < h
    };
    let streamed = |m: u32, i: u32| inside(m, i) && has_stream(m, i);
    let addr = stream_blocks(t, grid, &streamed);
    let order = header_order(t, grid);
    let mut out = BTreeMap::new();
    for (idx, (w0, has)) in headers(t, w, h, grid, &streamed).into_iter().enumerate() {
        let at = HEADERS_AT + 12 * idx as u32;
        if w0 != 0 {
            out.insert(at, w0);
        }
        if has {
            let per = order.len();
            out.insert(at + 4, addr[&(idx as u32 / per as u32, order[idx % per])]);
        }
    }
    Ok(out)
}

/// The order a macrotile's streams are allocated in, as local region indices: 64 x 64 pixel
/// blocks (two regions across, four down) in raster order, regions in raster order within one.
pub fn walk(mx: u32, my: u32) -> Vec<u32> {
    let mut o = vec![];
    for br in 0..my.div_ceil(4) {
        for bc in 0..mx.div_ceil(2) {
            for r in 4 * br..(4 * br + 4).min(my) {
                for c in 2 * bc..(2 * bc + 2).min(mx) {
                    o.push(r * mx + c);
                }
            }
        }
    }
    o
}

/// What the TA wrote: the parameter buffer's dwords by slot byte address and the TA data's by
/// dump offset.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct Written {
    pub param: BTreeMap<u32, u32>,
    pub tadata: BTreeMap<u32, u32>,
    /// the rules (records) the result rests on
    pub rules: Vec<&'static str>,
}

pub struct Job<'a> {
    pub w: u32,
    pub h: u32,
    pub tris: &'a [[Vertex; 3]],
    pub state: &'a State,
    /// VDM_STATE1 or a visibility decision says no object is written
    pub no_object: bool,
}

/// The triangle's bounding box is one whose listing a record measured, or the refusal (Q230):
/// a box ending at or before the target's low edge (max x or max y at most 0) lists in the first
/// region by E542's closed low side, but the hardware wrote no object at max x 0.0 (E776; y
/// alike [infer]); a box under one pixel both ways about the tile corner (32, 32) wrote none from
/// 0.30 to 0.98 pixel (E780) while E736's 0.96-pixel square there (through a clamp) wrote one: no
/// rule, so a sub-pixel box about a 16 x 16 tile's corner refuses. Other sub-pixel boxes stay the
/// tile rule's: arith-1138's small class (E606, E607) replays its images and depth with them, at
/// pixel corners too (no kept dump says whether those objects were written).
fn check_extent(tri: &[Vertex; 3]) -> Result<(), Outcome> {
    let span = |f: fn(&Vertex) -> f32| {
        let c = tri.map(|v| f(&v) as f64);
        (c.iter().cloned().fold(f64::MAX, f64::min), c.iter().cloned().fold(f64::MIN, f64::max))
    };
    let ((x0, x1), (y0, y1)) = (span(|v| v.x), span(|v| v.y));
    if x1 <= 0.0 || y1 <= 0.0 {
        return Err(refuse_ids(
            format!(
                "a triangle whose box ends at x {x1} and y {y1}: E542's closed low side lists it at the target's edge, the hardware wrote no object at max x 0.0 (E776)"
            ),
            &["Q230"],
        ));
    }
    // a multiple of 16 strictly inside the box's span on both axes: a tile corner
    let corner = |a: f64, b: f64| 16.0 * (a / 16.0).floor() + 16.0 < b;
    if x1 - x0 < 1.0 && y1 - y0 < 1.0 && corner(x0, x1) && corner(y0, y1) {
        return Err(refuse_ids(
            format!(
                "a triangle of {} x {} pixels about a tile corner: none was written from 0.30 to 0.98 pixel (E780) and a 0.96-pixel square was (E736): no rule",
                x1 - x0,
                y1 - y0
            ),
            &["Q230"],
        ));
    }
    Ok(())
}

/// Write the object, region headers and control streams of a job.
pub fn write(job: &Job) -> Result<Written, Outcome> {
    let t = tiling(job.w, job.h);
    if t.n != 2 {
        return Err(refuse_ids(
            format!(
                "{} x {}: four macrotiles in a row (E506): the headers' layout was dumped for two only",
                job.w, job.h
            ),
            &["Q139", "Q100", "Q086"],
        ));
    }
    let mut out = Written::default();
    let objects = !job.no_object && !job.tris.is_empty();
    // per region: the primitives that meet its left and right tiles
    let mut masks: BTreeMap<(u32, u32), (u32, u32)> = BTreeMap::new();
    let mut isp = 0;
    if objects {
        for tri in job.tris {
            check_extent(tri)?;
        }
        let words = object_words(job.tris, job.state)?;
        isp = OBJECT_AT / 4 + 3 + 3 * job.tris.len() as u32;
        for (i, w) in words.iter().enumerate() {
            if *w != 0 {
                out.param.insert(OBJECT_AT + 4 * i as u32, *w);
            }
        }
        out.rules.extend(["E541", "E651"]);
        for m in 0..t.n * t.n {
            for i in 0..t.mx * t.my {
                let (c, r) = ((m / t.n) * t.mx + i % t.mx, (m % t.n) * t.my + i / t.mx);
                if 32 * c >= job.w || 16 * r >= job.h {
                    continue;
                }
                let (x0, y0) = (32.0 * c as f64, 16.0 * r as f64);
                let (mut l, mut rr) = (0u32, 0u32);
                for (k, tri) in job.tris.iter().enumerate() {
                    let p = tri.map(|v| (v.x as f64, v.y as f64));
                    l |= u32::from(tile_lists(&p, x0, y0)) << k;
                    rr |= u32::from(tile_lists(&p, x0 + 16.0, y0)) << k;
                }
                if l | rr != 0 {
                    masks.insert((m, i), (l, rr));
                }
            }
        }
        out.rules.push("E542");
        if masks.is_empty() {
            return Err(refuse_ids(
                "no target region lists a primitive: the hardware wrote no object for a triangle 1000 pixels off the target (E182's baseline), and nothing is recorded for one near the target's edge",
                &["Q230"],
            ));
        }
    }
    let has = |m: u32, i: u32| masks.contains_key(&(m, i));
    let addr = stream_blocks(&t, Grid::LIBRARY, &has);
    for (&(m, i), &(l, r)) in &masks {
        let mut w = stream_words(job.tris.len() as u32, l, r, isp)?;
        w.resize(8, 0xc000_0000);
        for (k, v) in w.iter().enumerate() {
            out.param.insert(addr[&(m, i)] + 4 * k as u32, *v);
        }
    }
    out.tadata.extend(region_data(&t, job.w, job.h, Grid::LIBRARY, &has)?);
    out.rules.push("E652");
    Ok(out)
}

/// R7-BLK's region header slots (E907) under a poked `CR_TE_MACROTILE_STRIDE` with the rule's
/// macrotile words: every region of the rule's macrotiles writes its header at (mcol n + mrow)
/// stride + (block index) 16 + (r & 3) 4 + (c & 3), the blocks 4 x 4 regions counted across the
/// macrotile, in block order (block rows across the target, raster inside a block; E944, 11 of
/// 11 held-out strides with every slot); a later header overwrites an earlier one, and a target
/// tile draws iff its own header survives (E907). Returns each target tile's slot, None for a
/// wrong tile. Held out at 256 x 256 and 640 x 480 only, at strides that drew without a fault
/// (E505, E509: 0 to 31 and 4 to 63, besides the rule's), and at the rule's own stride at 1280 x
/// 720 and 768 x 640 (E959: the baselines' 1800 and 960 headers); the rest refuses (Q139), as do
/// poked macrotile words (E944's residue: E950 fits a first-macrotile block row of 8 floor(fx /
/// 2) slots on its three readable dumps, in sample only, the same as the rule's when fx is 0 or 1
/// mod 4). The list ends at the scene's last-region flag (E1007, `macrotile_slots`): with the
/// rule's words it is on the highest surviving slot, so nothing past it is lost here.
pub fn stride_slots(w: u32, h: u32, stride: u32) -> Result<BTreeMap<(u32, u32), Option<u32>>, Outcome> {
    let t = tiling(w, h);
    let ok = match (w, h) {
        (256, 256) => stride <= 31 || stride == t.stride,
        (640, 480) => (4..=63).contains(&stride) || stride == t.stride,
        (1280, 720) | (768, 640) => stride == t.stride,
        _ => false,
    };
    if !ok {
        return Err(refuse_ids(
            format!(
                "{w} x {h}, stride {stride}: the header write order is held out at 256 x 256 and 640 x 480 at strides that drew without a fault (E944, E505, E509) and at the rule's stride at 1280 x 720 and 768 x 640 (E959)"
            ),
            &["Q139"],
        ));
    }
    Ok(slots(&t, t.mtile1, t.mtile2, stride).0)
}

/// Poked macrotile words measured to draw a whole image, each at its size with the rule's
/// `CR_TE_MTILE1` and stride: `CR_TE_MTILE2` words whose first macrotile is 0 or 1 mod 4 tiles
/// wide, where E950's H-EVEN and R7-BLK agree (E907 and E1007: 0x0200a008 and 0x0280a00a at fy 10;
/// E1007 held out: 0x0200b008 at fy 11, 0x05c10018 at fy 23 with n 4; E959: 0x03018025 at 768 x
/// 640, held out, and at 1280 x 720, whose 12 tiles past the flag E1007 held out the rule of;
/// E1011: r7-rp's dumps of 0x0200c008 at 256 x 256 and 0x04410018, 0x02018018, 0x05010018 and
/// 0x0201c018 at 640 x 480, every slot and the flag, E907's run, read offline).
pub const MEASURED_MTILE2: [(u32, u32, u32); 11] = [
    (256, 256, 0x0200_a008),
    (256, 256, 0x0280_a00a),
    (256, 256, 0x0200_b008),
    (256, 256, 0x0200_c008),
    (640, 480, 0x05c1_0018),
    (640, 480, 0x0441_0018),
    (640, 480, 0x0201_8018),
    (640, 480, 0x0501_0018),
    (640, 480, 0x0201_c018),
    (768, 640, 0x0301_8025),
    (1280, 720, 0x0301_8025),
];

/// Poked `CR_TE_MTILE1` words measured to draw (wrong in whole tiles) with every header at R7-BLK's
/// slot and the list ending at the flag, each at its size with the rule's `CR_TE_MTILE2` and
/// stride: r7-rp's dumped rows (E907: slots and wrong tiles, 9 of 10 held out; E1011, offline on
/// the same dumps: every slot at H-EVEN's, which is R7-BLK's at these first macrotiles, 4, 5, 8,
/// 12, 16, 20 and 28 tiles wide (0x02010018 clears bit 31: two macrotiles), and the one flagged
/// header at the last target tile in block order, 21 of 21 rows never read for the flag).
///
/// E1048 (r14-flag f2, held out): four words whose first macrotile is 2 or 3 mod 4 tiles wide and
/// covers the target, where E950's H-EVEN (8 floor(fx / 2) slots a block row) and R7-BLK part:
/// fx 14 and 15 at 256 x 256, 26 and 27 at 768 x 640 (n 4, B1 past B2 and B3); every slot at
/// H-EVEN's and the flag on the last target tile in block order, which at 768 x 640 is not the
/// highest target slot (E1011's rival failed).
pub const MEASURED_MTILE1: [(u32, u32, u32); 14] = [
    (256, 256, 0x0100_e004),
    (256, 256, 0x0100_f004),
    (768, 640, 0x8681_0018),
    (768, 640, 0x86c1_0018),
    (256, 256, 0x0140_4004),
    (256, 256, 0x0100_8004),
    (256, 256, 0x0100_5004),
    (256, 256, 0x0200_8008),
    (256, 256, 0x0100_c004),
    (640, 480, 0x8501_0018),
    (640, 480, 0x8201_4018),
    (640, 480, 0x8701_0018),
    (640, 480, 0x8202_0018),
    (640, 480, 0x0201_0018),
];

/// R7-BLK's region header slots under poked macrotile words (`CR_TE_MTILE1`, `CR_TE_MTILE2`, the
/// rule's stride), and the slot of the scene's last-region flag. A tile's macrotile is found by
/// comparing the words' bounds in order of use (E877; n 4 with `CR_TE_MTILE1` bit 31: bounds 0,
/// B1, B2, B3 per axis; else 0, B2), the first macrotile's width and height being the axis's first
/// bound; the TA writes every tile up to the last bound plus that width, past the target too, in
/// block order (E944), at (mcol n + mrow) stride + (ly >> 2) 8 floor(fx / 2) + (lx >> 2) 16 + (r
/// & 3) 4 + (c & 3) (E907; the block row's width E950's H-EVEN, held out by E1048, R7-BLK's 16
/// floor(fx / 4) whenever fx is 0 or 1 mod 4), a later header overwriting an earlier one. Flag bit 7 marks the header of
/// the last target tile written whose header survives, and the 3D reads the list up to it: a
/// target tile draws iff its header survives at or before that slot (E1007, held out on four
/// dumps; E959 post hoc on 24; E1011, offline on r7-rp's 21 poked dumps of another module build,
/// where the highest slot written lies past the flag on 17). Only `MEASURED_MTILE2`,
/// `MEASURED_MTILE1` and the rule's own words are admitted;
/// other words refuse (Q139: most poked words whose first macrotile ends inside the target
/// faulted, E505 and E509; E1048's four drew, H-COVER [infer]). Which fault such a word gives is
/// fitted on E509's 162 faulting cases (E1073, post hoc, 162 of 162) and held out at 384 x 256
/// (E1074, 2 of 2): an axis whose bounds are all 0 faults the TA's header write (0x90004), the
/// other faulting words the 3D's read at the parameter heap's first page (0x90100); held out again
/// on an empty x and an empty y axis at 512 x 512 (E1109, both 0x90004 at TA data page 0x20008,
/// the first page past that size's 0x8000 bytes); the faults and their pages stay refused (Q139).
pub fn macrotile_slots(
    w: u32,
    h: u32,
    mtile1: u32,
    mtile2: u32,
) -> Result<(BTreeMap<(u32, u32), Option<u32>>, u32), Outcome> {
    let t = tiling(w, h);
    let rule = mtile1 == t.mtile1
        && mtile2 == t.mtile2
        && [(256, 256), (640, 480), (768, 640), (1280, 720)].contains(&(w, h));
    let poked = (mtile1 == t.mtile1 && MEASURED_MTILE2.contains(&(w, h, mtile2)))
        || (mtile2 == t.mtile2 && MEASURED_MTILE1.contains(&(w, h, mtile1)));
    if !rule && !poked {
        return Err(refuse_ids(
            format!(
                "{w} x {h}, CR_TE_MTILE1 {mtile1:#x}, CR_TE_MTILE2 {mtile2:#x}: not a macrotile word measured with R7-BLK's slots and the list end held out (E907, E959, E1007, E1011)"
            ),
            &["Q139"],
        ));
    }
    Ok(slots(&t, mtile1, mtile2, t.stride))
}

/// The bounds of one axis of a macrotile word (n 4: 0, B1, B2, B3; n 2: 0, B2).
fn word_bounds(n: u32, word: u32, mask: u32) -> Vec<u32> {
    let b = [(word >> 22) & mask, (word >> 12) & mask, word & mask];
    if n == 4 { vec![0, b[0], b[1], b[2]] } else { vec![0, b[1]] }
}

/// A tile's macrotile index along one axis and its offset in it: the bounds compared in order.
fn place(v: u32, bs: &[u32]) -> (u32, u32) {
    let mut k = 0;
    while k + 1 < bs.len() && v >= bs[k + 1] {
        k += 1;
    }
    (k as u32, v - bs[k])
}

/// Every target tile's surviving slot at or before the flag (None: wrong), and the flag's slot.
fn slots(t: &Tiling, mtile1: u32, mtile2: u32, stride: u32) -> (BTreeMap<(u32, u32), Option<u32>>, u32) {
    let n = if mtile1 >> 31 & 1 == 1 { 4 } else { 2 };
    let (bx, by) = (word_bounds(n, mtile1, 0xff), word_bounds(n, mtile2, 0x1ff));
    let (fx, fy) = (bx[1], by[1]);
    let mut ws = vec![];
    for r in 0..t.ty.max(by[by.len() - 1] + fy) {
        for c in 0..t.tx.max(bx[bx.len() - 1] + fx) {
            let ((mc, lx), (mr, ly)) = (place(c, &bx), place(r, &by));
            // a block row of the first macrotile's width: 8 floor(fx / 2) slots (E950's H-EVEN,
            // held out by E1048 at fx 14, 15, 26, 27), R7-BLK's 16 floor(fx / 4) at fx 0 or 1 mod 4
            let sl =
                (mc * n + mr) * stride + (ly >> 2) * 8 * (fx >> 1) + (lx >> 2) * 16 + (r & 3) * 4 + (c & 3);
            ws.push(((r >> 2, c >> 2, r, c), sl, (c, r)));
        }
    }
    ws.sort_by_key(|w| w.0);
    let mut own = BTreeMap::new();
    for (_, sl, tile) in ws {
        own.insert(sl, tile);
    }
    let mut out: BTreeMap<(u32, u32), Option<u32>> =
        (0..t.ty).flat_map(|r| (0..t.tx).map(move |c| ((c, r), None))).collect();
    for (sl, tile) in own {
        if let Some(v) = out.get_mut(&tile) {
            *v = Some(sl);
        }
    }
    // the flag: on the surviving header of the target tile last in block order
    let flag = out
        .iter()
        .filter_map(|(&(c, r), v)| v.map(|s| ((r >> 2, c >> 2, r, c), s)))
        .max()
        .map_or(0, |(_, s)| s);
    for v in out.values_mut() {
        if v.is_some_and(|s| s > flag) {
            *v = None;
        }
    }
    (out, flag)
}

/// The tiles (across, down) a pair of macrotile words covers: the last bound plus one more
/// macrotile of the first's size, B3 + B1 per axis (H-COV's extent, E886; `CR_TE_MTILE1`'s fields
/// 29:22 and 7:0, `CR_TE_MTILE2`'s 30:22 and 8:0).
pub fn macrotile_cover(mtile1: u32, mtile2: u32) -> (u32, u32) {
    ((mtile1 >> 22 & 0xff) + (mtile1 & 0xff), (mtile2 >> 22 & 0x1ff) + (mtile2 & 0x1ff))
}

/// The region-header arrays the TA writes for a `CR_TE_AA` word, each the size of the target's
/// own 1x array (`rgn_size`): one at the library's grid (E763 and E788's a4 at 0x20000000: one
/// array of the target's layout from 0x4000 and nothing past it, in a context made for a larger
/// target), four at 0xe0000000 (E788: four written and the fifth slot empty at 256 x 160 and 320 x
/// 128, four written and enough at 320 x 400; E729 alone bounded the count at 4 or 5, its
/// correction and E824 hold 4). The arrays are the halved grid's headers (`Grid`, E893): four
/// times the regions. One halved axis (0x60000000, 0xa0000000) was never dumped for its arrays nor
/// run against the layout's end: refused (Q140), as are the words `Grid::from_te_aa` refuses.
pub fn header_arrays(te_aa: u32) -> Result<u32, Outcome> {
    match Grid::from_te_aa(te_aa)? {
        Grid::LIBRARY => Ok(1),
        Grid { half_width: true, half_height: true } => Ok(4),
        _ => Err(refuse_ids(
            format!(
                "CR_TE_AA {te_aa:#x}: one halved axis; the arrays the TA writes were dumped and run against the TA data's end at 0x20000000 and 0xe0000000 only (E763, E729, E788)"
            ),
            &["Q140"],
        )),
    }
}

/// The size of one region-header array of a `w` x `h` target: 12 bytes a region of its 1x grid,
/// the library's macrotiles (`sgx_render_layout`'s `rgn_size`; E763: 0x1800 at 320 x 400).
pub fn rgn_size(w: u32, h: u32) -> u32 {
    let t = tiling(w, h);
    12 * t.n * t.n * t.mx * t.my
}

/// Non-zero dwords in each region-header array a full-screen triangle (`--tri-full`, every target
/// region with a stream) leaves at `CR_TE_AA` `te_aa`, the arrays read as slots of the target's
/// `rgn_size` from the first header: every header's word 0 and the stream word of each target
/// region (E788: 256, 160, 256, 160 at 256 x 160; 256, 256, 160, 160 at 320 x 128; 1024, 800,
/// 640 and 584 at 320 x 400; E763 and E788's a4: 762 in one array at 0x20000000). At 0xe0000000
/// the arrays were dumped on two macrotiles a side only: four refuses (Q139).
pub fn array_dwords(w: u32, h: u32, te_aa: u32) -> Result<Vec<u32>, Outcome> {
    let f = header_arrays(te_aa)?;
    let grid = Grid::from_te_aa(te_aa)?;
    let t = tiling(w, h);
    if f > 1 && t.n != 2 {
        return Err(refuse_ids(
            format!("{w} x {h}: four macrotiles a side; E788 read the four arrays at two macrotiles a side"),
            &["Q139"],
        ));
    }
    let per = (rgn_size(w, h) / 12) as usize;
    let hs = headers(&t, w, h, grid, &|_, _| true);
    Ok(hs
        .chunks(per)
        .map(|c| c.iter().map(|&(w0, stream)| u32::from(w0 != 0) + u32::from(stream)).sum())
        .collect())
}

/// Where our kernel puts the TA data of a context made for `mw` x `mh` with `arrays`
/// region-header arrays (fork `sgx_render_tadata_layout`): the tail pointers (4 side^2 bytes) to
/// a page, the control, OTPM and state pages, then `rgn`, the arrays (`arrays` x the maximum's
/// `rgn_size`, to a page) and a ZLS area of one array (to a page). One array is module B21FDA82's
/// layout (E763 and E788: 0xa000 at 544 x 400, 0x6000 at 256 x 160 and 320 x 128), four is E824's
/// `render_rgn_arrays` 4 (the eight sizes it read, 0x8000 to 0x1e000, and 0x6000 at 64 x 64 under
/// both); other counts were never laid out.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TaDataLayout {
    pub rgn: u32,
    pub size: u32,
}

/// The kernel's TA data of a context made for `mw` x `mh` with `arrays` arrays (above).
pub fn tadata_layout(mw: u32, mh: u32, arrays: u32) -> Result<TaDataLayout, Outcome> {
    if ![1, 4].contains(&arrays) || mw == 0 || mh == 0 || mw > 4096 || mh > 4096 {
        return Err(refuse_ids(
            format!("{mw} x {mh} with {arrays} arrays: the kernel laid out one or four (E763, E788, E824)"),
            &["Q140"],
        ));
    }
    let rgn = crate::dpm::region_headers_4x(mw, mh, crate::dpm::TailRoom::Rgn4);
    let r = rgn_size(mw, mh);
    Ok(TaDataLayout { rgn, size: rgn + (arrays * r).next_multiple_of(PAGE) + r.next_multiple_of(PAGE) })
}

/// How the TA's header writes of a `w` x `h` job at `CR_TE_AA` `te_aa` end in the TA data of a
/// context made for `mw` x `mh` with `arrays` arrays.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HeaderEnding {
    /// The arrays fit (the image is the other units' to say).
    Complete,
    /// The job faults on the TA side (`BIF_INT_STAT` 0x90004) at TA-data page `page`, its end:
    /// E729's 0x20006, 0x20006 and 0x20008 (TA data at 0x20000000), E788's a6 at 0x20008.
    Fault { page: u32 },
}

/// Contexts where a target's four arrays fit and a fifth would not, run and completed: E788's a5
/// (320 x 400 in a context made for 544 x 400, four arrays ending at 0xa000, 0 wrong pixels).
pub const MEASURED_FOUR_EXACT: [(u32, u32, u32, u32, u32); 1] = [(320, 400, 544, 400, 1)];

/// The header arrays against the layout's end (E729's rule, rgn + f rgn_size <= size completes,
/// else a fault at page size >> 12, with f from `header_arrays` and the target's own `rgn_size`,
/// E763): E729's five sizes, E788's a4, a5 and a6 and E824's eight four-array sizes and its
/// one-array control. Where room for four arrays is not room for five, only f = 4 against 5
/// decides, which E729 left open: the ending is held only where it was run
/// (`MEASURED_FOUR_EXACT`), else refused (Q140).
pub fn header_layout_ending(
    w: u32,
    h: u32,
    mw: u32,
    mh: u32,
    te_aa: u32,
    arrays: u32,
) -> Result<HeaderEnding, Outcome> {
    if w == 0 || h == 0 || w > mw || h > mh {
        return Err(refuse_ids(format!("{w} x {h} in a context made for {mw} x {mh}"), &["Q140"]));
    }
    let f = header_arrays(te_aa)?;
    let td = tadata_layout(mw, mh, arrays)?;
    let r = rgn_size(w, h);
    if td.rgn + f * r > td.size {
        return Ok(HeaderEnding::Fault { page: td.size >> 12 });
    }
    if f == 4 && td.rgn + 5 * r > td.size && !MEASURED_FOUR_EXACT.contains(&(w, h, mw, mh, arrays)) {
        return Err(refuse_ids(
            format!(
                "{w} x {h} in {mw} x {mh} with {arrays} arrays: room for four arrays and not five, where E729 left f at 4 or 5 and E788 completed 320 x 400 in 544 x 400 only"
            ),
            &["Q140"],
        ));
    }
    Ok(HeaderEnding::Complete)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn library_headers_are_4x4_region_blocks_on_every_macrotile() {
        // E944's and E907's 640 x 480 baselines (8 x 8 regions a macrotile): every one of the
        // 600 headers at R7-BLK's slot, block rows across the macrotile, raster inside a block
        let t = tiling(640, 480);
        assert_eq!((t.mx, t.my), (8, 8));
        let o = header_order(&t, Grid::LIBRARY);
        assert_eq!(&o[..5], &[0, 1, 2, 3, 8]);
        assert_eq!((o[16], o[32], o[63]), (4, 32, 63));
        // a macrotile 4 regions wide is raster order (E652: 256 x 256, 4 x 8 regions)
        let t = tiling(256, 256);
        assert_eq!(header_order(&t, Grid::LIBRARY), (0..32).collect::<Vec<u32>>());
    }

    #[test]
    fn a_poked_stride_keeps_the_last_header_of_each_slot_in_block_order() {
        // E944 (11 of 11 held out, wrong-tile sets and every slot), E907's stride rows and the
        // fit rows: the wrong tiles (no surviving header) per stride
        for (w, h, s, wrong) in [
            (256, 256, 1, 93),
            (256, 256, 2, 90),
            (256, 256, 3, 87),
            (256, 256, 4, 84),
            (256, 256, 5, 81),
            (256, 256, 6, 78),
            (256, 256, 7, 75),
            (256, 256, 8, 72),
            (256, 256, 12, 60),
            (256, 256, 20, 36),
            (256, 256, 24, 24),
            (640, 480, 5, 521),
            (640, 480, 6, 510),
            (640, 480, 7, 507),
            (640, 480, 8, 504),
            (640, 480, 12, 476),
        ] {
            let sl = stride_slots(w, h, s).unwrap();
            assert_eq!(sl.values().filter(|v| v.is_none()).count(), wrong, "{w}x{h} stride {s}");
        }
        // stride 4 at 256 x 256: block order, not row order (E907's miss): tile (4, 8) keeps slot
        // 12 and (0, 10) loses it, where row order gives the reverse
        let sl = stride_slots(256, 256, 4).unwrap();
        assert_eq!(sl[&(0, 0)], Some(0));
        assert_eq!((sl[&(4, 8)], sl[&(0, 10)], sl[&(5, 9)]), (Some(12), None, Some(17)));
        // the rule's own stride draws every tile at the library's header slots
        let t = tiling(640, 480);
        let base = stride_slots(640, 480, t.stride).unwrap();
        assert!(base.values().all(|v| v.is_some()));
        let order = header_order(&t, Grid::LIBRARY);
        let pos = |c: u32, r: u32| {
            let m = (c / t.mx) * t.n + r / t.my;
            let i = (r % t.my) * t.mx + c % t.mx;
            m * t.stride + order.iter().position(|&k| k == i).unwrap() as u32
        };
        for (&(c, r), v) in &base {
            assert_eq!(*v, Some(pos(c, r)), "({c}, {r})");
        }
    }

    #[test]
    fn the_baselines_of_1280x720_and_768x640_hold_their_headers_in_the_same_blocks() {
        // E959: the unpoked 1280 x 720 and 768 x 640 baselines (n 4, the first macrotile 12 and
        // 8 regions wide) hold every one of their 1800 and 960 headers at R7-BLK's slot, block
        // rows across the macrotile
        for (w, h, n) in [(1280, 720, 1800), (768, 640, 960)] {
            let t = tiling(w, h);
            let base = stride_slots(w, h, t.stride).unwrap();
            assert_eq!(base.len(), n);
            let order = header_order(&t, Grid::LIBRARY);
            for (&(c, r), v) in &base {
                let m = (c / t.mx) * t.n + r / t.my;
                let i = (r % t.my) * t.mx + c % t.mx;
                let want = m * t.stride + order.iter().position(|&k| k == i).unwrap() as u32;
                assert_eq!(*v, Some(want), "{w}x{h} ({c}, {r})");
            }
        }
        // 1280 x 720's last macrotile column starts at region 36: tile (36, 0) is slot 12 x 144
        let sl = stride_slots(1280, 720, tiling(1280, 720).stride).unwrap();
        assert_eq!((tiling(1280, 720).stride, sl[&(36, 0)], sl[&(13, 1)]), (144, Some(1728), Some(581)));
    }

    #[test]
    fn poked_y_macrotile_words_keep_r7_blk_slots_and_the_list_ends_at_the_flag() {
        // E1007 (r10-geo q139c, held out: fy 11 and 23; replicates of E907's fy-10 dumps) and
        // E959 (768 x 640 m2-B3p1 held out; the 1280 x 720 residue): every target tile's slot is
        // R7-BLK's, the scene's last-region flag (bit 7) sits on the last target tile the TA
        // writes in block order, and a tile whose surviving header lies past it does not draw
        for (w, h, m2, wrong, flag) in [
            (256, 256, 0x0200_a008, 24, 127),
            (256, 256, 0x0280_a00a, 24, 127),
            (256, 256, 0x0200_b008, 36, 127),
            (640, 480, 0x05c1_0018, 180, 743),
            (768, 640, 0x0301_8025, 24, 1087),
            (1280, 720, 0x0301_8025, 52, 2211),
        ] {
            let (sl, last) = macrotile_slots(w, h, tiling(w, h).mtile1, m2).unwrap();
            assert_eq!(sl.values().filter(|v| v.is_none()).count(), wrong, "{w}x{h} {m2:#x}");
            assert_eq!(last, flag, "{w}x{h} {m2:#x}");
            assert!(sl.values().flatten().all(|&s| s <= last));
        }
        // the residue: row 36 has no header (40 tiles) and columns 36 to 39 of rows 41 to 43
        // keep theirs at 2212 to 2223, past the flag on tile (39, 44) (E959)
        let (sl, _) = macrotile_slots(1280, 720, tiling(1280, 720).mtile1, 0x0301_8025).unwrap();
        assert!((0..40).all(|c| sl[&(c, 36)].is_none()));
        assert!((41..44).all(|r| (36..40).all(|c| sl[&(c, r)].is_none())));
        assert_eq!(sl[&(39, 44)], Some(2211));
        // the unpoked words are the rule's: the same slots as stride_slots, nothing past the flag
        for (w, h) in [(256, 256), (640, 480), (768, 640), (1280, 720)] {
            let t = tiling(w, h);
            let (sl, _) = macrotile_slots(w, h, t.mtile1, t.mtile2).unwrap();
            assert_eq!(sl, stride_slots(w, h, t.stride).unwrap(), "{w}x{h}");
        }
    }

    #[test]
    fn r7_rp_s_poked_dumps_end_the_list_at_the_last_target_tile_in_block_order_e1011() {
        // E1011 (round 11 offline, r7-rp q139's 21 poked dumps and the poked control, E907's run
        // on module 41E2..., never read for the flag): one header with flag bit 7, at H-EVEN's
        // (here R7-BLK's: fx 0 or 1 mod 4) slot of the last target tile in block order, the wrong
        // tiles those whose surviving header is missing or past it; the highest slot written lies
        // past the flag on 17 of them (non-target headers past the target)
        for (w, h, m1, m2, wrong, flag) in [
            (256, 256, 0x0140_4004, 0, 0, 127),
            (256, 256, 0x0100_8004, 0, 32, 95),
            (256, 256, 0x0100_5004, 0, 12, 127),
            (256, 256, 0, 0x0200_a008, 24, 127),
            (256, 256, 0x0200_8008, 0, 32, 95),
            (640, 480, 0x8501_0018, 0, 288, 343),
            (640, 480, 0x8201_4018, 0, 112, 519),
            (640, 480, 0, 0x0441_0018, 108, 743),
            (640, 480, 0, 0x0201_8018, 0, 743),
            (256, 256, 0x0100_c004, 0, 32, 111),
            (256, 256, 0, 0x0200_c008, 48, 111),
            (256, 256, 0, 0x0280_a00a, 24, 127),
            (640, 480, 0x8701_0018, 0, 288, 375),
            (640, 480, 0x8202_0018, 0, 112, 519),
            (640, 480, 0, 0x0501_0018, 144, 743),
            (640, 480, 0, 0x0201_c018, 0, 743),
            (640, 480, 0x0201_0018, 0, 288, 391),
        ] {
            let t = tiling(w, h);
            let (m1, m2) = (if m1 == 0 { t.mtile1 } else { m1 }, if m2 == 0 { t.mtile2 } else { m2 });
            let (sl, last) = macrotile_slots(w, h, m1, m2).unwrap();
            assert_eq!(sl.values().filter(|v| v.is_none()).count(), wrong, "{w}x{h} {m1:#x} {m2:#x}");
            assert_eq!(last, flag, "{w}x{h} {m1:#x} {m2:#x}");
        }
        // the poked strides (stride_slots' wrong tiles, E944): the flag on the last target tile
        for (s, wrong, flag) in [(8, 72, 55), (16, 48, 79), (4, 84, 43), (24, 24, 103)] {
            let t = tiling(256, 256);
            let (sl, last) = slots(&t, t.mtile1, t.mtile2, s);
            assert_eq!((sl.values().filter(|v| v.is_none()).count(), last), (wrong, flag), "stride {s}");
            assert_eq!(sl, stride_slots(256, 256, s).unwrap(), "stride {s}");
        }
    }

    #[test]
    fn macrotile_words_that_were_not_held_out_are_refused() {
        // E944's residue m1-B2-10 (fx 10: E950's H-EVEN fitted, not held out), a word that
        // faulted (E509: m2-B2-0), and a held-out word at another size
        let t = tiling(256, 256);
        for (w, h, m1, m2) in [
            (256, 256, 0x0100_a004, t.mtile2),
            (256, 256, t.mtile1, 0x0200_0008),
            (512, 512, tiling(512, 512).mtile1, 0x0200_a008),
        ] {
            assert!(
                matches!(macrotile_slots(w, h, m1, m2), Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q139"]),
                "{w}x{h} {m1:#x} {m2:#x}"
            );
        }
    }

    #[test]
    fn strides_and_sizes_that_did_not_draw_or_did_not_run_are_refused() {
        // E505/E509: 640 x 480 strides 0 and 1 faulted, 256 x 256 strides of 33 and more faulted;
        // the order is held out at 256 x 256 and 640 x 480 only (E944)
        for (w, h, s) in
            [(640, 480, 0), (640, 480, 1), (256, 256, 33), (256, 256, 64), (512, 384, 4), (1280, 720, 8)]
        {
            assert!(stride_slots(w, h, s).is_err(), "{w}x{h} stride {s}");
        }
    }

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

    fn v(x: f32, y: f32, z: f32) -> Vertex {
        Vertex { x, y, z, rhw: 1.0 }
    }

    fn state() -> State {
        State {
            isp: [0x01d0_0200, 0x10f0],
            pds: [0x0400_0004, 0x0003_0001, 0x0400_0000],
            vp: [32.0, 32.0, 32.0, 32.0, 0.5, 0.5],
        }
    }

    #[test]
    fn the_librarys_tiling_words_for_the_sizes_the_records_give() {
        // doc/specs/3d.md 7.1: 64 x 64 and 256 x 256; the 128 x 128 words of the dumps
        let t = tiling(64, 64);
        assert_eq!((t.te_screen, t.mtile2, t.stride, t.n, t.mx, t.my), (0x3001, 0x0100_4004, 0x10, 2, 4, 4));
        let t = tiling(256, 256);
        assert_eq!((t.te_screen, t.mtile2, t.stride, t.mx, t.my), (0xf007, 0x0200_8008, 0x20, 4, 8));
        let t = tiling(128, 128);
        assert_eq!(
            (t.te_screen, t.mtile1, t.mtile2, t.stride, t.tx, t.ty),
            (0x7003, 0x0100_4004, 0x0100_4004, 0x10, 4, 8)
        );
        assert_eq!(tiling(640, 480).n, 4);
    }

    #[test]
    fn one_triangle_writes_the_23_dwords_e176_lists() {
        // E176's plain probe (64 x 64): (8, 8), (56, 20), (20, 56) at depth 0.5
        let t = [[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]];
        let w = object_words(&t, &state()).unwrap();
        let want = [
            0x0400_0004,
            0x0003_0001,
            0x0400_0000,
            0x3f80_0000,
            0x3f80_0000,
            0x3f80_0000,
            0x01d0_0200,
            0x10f0,
            0x4a30_4a30,
            0x1010,
            0x0004_0101,
            0,
            0,
            0,
            0,
            0x0010_0800,
            0x0000_1008,
            0x1400_3f00,
            0x1038_0010,
            0x3f00_0000,
            0x0010_3800,
            0x0000_1014,
            0x0000_3f00,
        ];
        assert_eq!(w, want);
    }

    #[test]
    fn the_viewport_z_moves_three_packed_dwords_and_nothing_else_e176() {
        let t = [[v(8.0, 8.0, 0.75), v(56.0, 20.0, 0.75), v(20.0, 56.0, 0.75)]];
        let w = object_words(&t, &state()).unwrap();
        let base =
            object_words(&[[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]], &state()).unwrap();
        let diff: Vec<usize> = (0..w.len()).filter(|&i| w[i] != base[i]).collect();
        assert_eq!(diff.len(), 3);
        assert_eq!((w[17], w[19], w[22]), (0x1400_3f40, 0x3f40_0000, 0x0000_3f40));
    }

    #[test]
    fn a_negative_signed_area_sets_bit_15_of_the_primitive_list_entry_e308() {
        let t = [[v(8.0, 8.0, 0.5), v(20.0, 56.0, 0.5), v(56.0, 20.0, 0.5)]];
        assert_eq!(object_words(&t, &state()).unwrap()[8], 0xca30_ca30);
        // a triangle with no area has no winding: refused
        let d = [[v(8.0, 8.0, 0.5), v(20.0, 20.0, 0.5), v(32.0, 32.0, 0.5)]];
        assert!(matches!(object_words(&d, &state()), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn five_triangles_make_one_object_of_15_vertices_and_more_are_refused() {
        let tri = [v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)];
        let w = object_words(&[tri; 5], &state()).unwrap();
        // 3 + 15 rhw + 2 ISP, then the list 0x56934a30 0x6f5962f6 0x7bbc7bbc (E181's five copies)
        assert_eq!(w[20..23], [0x5693_4a30, 0x6f59_62f6, 0x7bbc_7bbc]);
        match object_words(&[tri; 6], &state()) {
            Err(Outcome::Unsupported { ids, .. }) => assert!(ids.iter().any(|i| i == "Q070")),
            r => panic!("{r:?}"),
        }
    }

    #[test]
    fn stream_words_take_the_forms_e180_lists() {
        let isp = 0x406;
        // one triangle (3 vertices): left only, right only, both
        assert_eq!(stream_words(1, 1, 0, isp).unwrap(), [0x4480_0701, 0x0400_0406]);
        assert_eq!(stream_words(1, 0, 1, isp).unwrap(), [0x4498_0701, 0x0400_0406]);
        assert_eq!(stream_words(1, 1, 1, isp).unwrap(), [0x4490_ffff, 0x0400_0406]);
        // two copies: 0x4a803f03 and 0x4a983f03
        assert_eq!(stream_words(2, 3, 0, 0x409).unwrap()[0], 0x4a80_3f03);
        assert_eq!(stream_words(2, 0, 3, 0x409).unwrap()[0], 0x4a98_3f03);
    }

    #[test]
    fn five_copies_use_the_wide_forms_with_a_further_dword_e177() {
        let isp = 0x412;
        let obj = 9 << 26 | isp;
        // the dump's regions: (L, R) = (3, 3), (3, 0x1f), (0, 0x1f), (0x1f, 0), (1f, 1f), (0x1c, 0), (0, 7)
        assert_eq!(stream_words(5, 3, 3, isp).unwrap(), [0x5c88_003f, obj, 0x0003_0003]);
        assert_eq!(stream_words(5, 3, 0x1f, isp).unwrap(), [0x5c88_7fff, obj, 0x001f_0003]);
        assert_eq!(stream_words(5, 0, 0x1f, isp).unwrap(), [0x5c8c_7fff, obj, 0x1f]);
        assert_eq!(stream_words(5, 0x1f, 0, isp).unwrap(), [0x5c8a_7fff, obj, 0x1f]);
        assert_eq!(stream_words(5, 0x1f, 0x1f, isp).unwrap(), [0x5c90_ffff, obj]);
        assert_eq!(stream_words(5, 0x1c, 0, isp).unwrap(), [0x5c8a_7fc0, obj, 0x1c]);
        assert_eq!(stream_words(5, 0, 7, isp).unwrap(), [0x5c8c_01ff, obj, 7]);
    }

    #[test]
    fn two_primitives_in_both_tiles_with_different_masks_take_the_wide_form_and_none_refuses() {
        // tc-16-16 region 0: left 3, right 1: 0x4a88003f with the masks in the further dword
        assert_eq!(stream_words(2, 3, 1, 0x409).unwrap(), [0x4a88_003f, 0x0c00_0409, 0x0001_0003]);
        assert!(matches!(stream_words(2, 0, 0, 0x409), Err(Outcome::Unsupported { .. })));
        assert!(
            matches!(stream_words(2, 4, 0, 0x409), Err(Outcome::Unsupported { .. })),
            "a primitive the object lacks"
        );
    }

    #[test]
    fn a_one_tile_region_is_narrow_while_the_vertex_mask_fits_a_byte_and_wide_after_that() {
        // five copies: the first two primitives (vertex mask 0x3f) narrow, the last one (0x7000) wide
        assert_eq!(stream_words(5, 3, 0, 0x412).unwrap()[0], 0x5c80_3f03);
        assert_eq!(stream_words(5, 0x10, 0, 0x412).unwrap()[..1], [0x5c8a_7000]);
        assert_eq!(stream_words(5, 0, 3, 0x412).unwrap()[0], 0x5c98_3f03);
    }

    #[test]
    fn the_streams_of_a_macrotile_are_allocated_by_64_x_64_blocks() {
        // the 128 x 128 dump's macrotile 0: addresses 0x2000.. go to regions 0, 4, 5, 8, 9, 12, 13, 6, 10, 11, 14, 15
        let order = walk(4, 4);
        let streamed = [0u32, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15];
        let got: Vec<u32> = order.into_iter().filter(|r| streamed.contains(r)).collect();
        assert_eq!(got, [0, 4, 5, 8, 9, 12, 13, 6, 10, 11, 14, 15]);
        // 256 x 256: eight rows: the lower blocks (rows 4 to 7) follow both upper ones
        let o = walk(4, 8);
        assert_eq!(o.len(), 32);
        assert_eq!(o[..4], [0, 1, 4, 5]);
        assert!(o.iter().position(|&r| r == 6) < o.iter().position(|&r| r == 16));
    }

    #[test]
    fn region_header_flags_mark_first_last_empty_and_outside_regions() {
        // 64 x 64 (two regions across, four down) with streams in regions (c0..1, r0..3) except c1 r0:
        // the dump of tb-w64: 0 first, 1 empty, 2 and 3 outside, 13 last of the macrotile and of the scene
        let t = tiling(64, 64);
        let has = |m: u32, i: u32| m == 0 && [0, 4, 5, 8, 9, 12, 13].contains(&i);
        let h = headers(&t, 64, 64, Grid::LIBRARY, &has);
        assert_eq!(h.len(), 64);
        let flags = |i: usize| h[i].0 >> 24;
        assert_eq!(
            [flags(0), flags(1), flags(2), flags(3), flags(4), flags(13), flags(14)],
            [0x04, 0x08, 0x02, 0x02, 0, 0x90, 0x02]
        );
        assert!(h[16..].iter().all(|x| x.0 >> 24 == 0x02), "the other macrotiles lie outside the target");
        // positions: column 2 per region column, row 2 per region row, the macrotile number in 15:12
        assert_eq!(h[5].0 & 0x00ff_ffff, 2 << 16 | 2);
        assert_eq!(h[16].0 & 0xffff, 0x1008);
    }

    /// The TA data of a job whose every target region has a stream, at CR_TE_AA `te_aa`.
    fn full(w: u32, h: u32, te_aa: u32) -> BTreeMap<u32, u32> {
        let grid = Grid::from_te_aa(te_aa).unwrap();
        region_data(&tiling(w, h), w, h, grid, &|_, _| true).unwrap()
    }

    /// Dump dword `k` of the TA data (the dump starts at offset 0; the headers at HEADERS_AT).
    fn dw(d: &BTreeMap<u32, u32>, k: u32) -> u32 {
        d.get(&(4 * k)).copied().unwrap_or(0)
    }

    #[test]
    fn cr_te_aa_bit_31_halves_the_region_width_and_bit_30_its_height_e893() {
        // E504's 64 x 64 dumps (fit): 0x20000000 72 non-zero dwords, 0x60000000 and 0xa0000000
        // 144, 0xe0000000 288; the 0xa0000000 macrotile is written in two 4 x 4 sub-blocks
        let n = |d: &BTreeMap<u32, u32>| d.values().filter(|&&v| v != 0).count();
        let (d20, d60, da0, de0) = (
            full(64, 64, 0x2000_0000),
            full(64, 64, 0x6000_0000),
            full(64, 64, 0xa000_0000),
            full(64, 64, 0xe000_0000),
        );
        assert_eq!([n(&d20), n(&d60), n(&da0), n(&de0)], [72, 144, 144, 288]);
        assert_eq!([dw(&da0, 4096), dw(&da0, 4097)], [0x0400_0000, 0x2000]);
        assert_eq!([dw(&da0, 4099), dw(&da0, 4100), dw(&da0, 4102)], [0x0001_0000, 0x2080, 0x0002_0000]);
        assert_eq!(dw(&da0, 4103), 0x2400, "the walk takes blocks of 2 regions across, 4 down");
        assert_eq!([dw(&da0, 4096 + 3 * 15), dw(&da0, 4096 + 3 * 16)], [0x9003_0006, 0x0204_0000]);
        assert_eq!([dw(&d60, 4096 + 3 * 16), dw(&d60, 4097 + 3 * 16)], [0x0000_0004, 0x2400]);
        assert_eq!(dw(&d60, 4096 + 3 * 29), 0x9002_0007);
        // a CR_TE_AA of 0 is the library's word for the TA (E504: 0 of 6144 dwords differ)
        assert_eq!(full(64, 64, 0), d20);
    }

    #[test]
    fn at_128_x_128_both_bits_give_64_streams_a_macrotile_over_two_pages_e893() {
        // E893 [HW, held out]: te-m2-e0-128x128's TA data, 384 non-zero dwords, 0 of 6144 off
        let d = full(128, 128, 0xe000_0000);
        assert_eq!(d.values().filter(|&&v| v != 0).count(), 384);
        let hdr = |k: u32| [dw(&d, 4096 + 3 * k), dw(&d, 4097 + 3 * k)];
        assert_eq!(hdr(0), [0x0400_0000, 0x2000]);
        assert_eq!(hdr(16), [0x0004_0000, 0x2800]);
        assert_eq!(hdr(31), [0x0007_0003, 0x2f80]);
        assert_eq!(hdr(32), [0x0000_0004, 0x3000], "the 33rd stream opens the next page");
        assert_eq!(hdr(63), [0x1007_0007, 0x3f80]);
        assert_eq!(hdr(64), [0x0400_1008, 0x4000]);
        assert_eq!(hdr(127), [0x9007_100f, 0x5f80]);
        assert_eq!(hdr(128), [0x0208_2000, 0]);
    }

    #[test]
    fn a_te_aa_word_with_bit_30_or_31_and_not_bit_29_is_refused() {
        // E281, E888: without bit 29 the triangle is removed and the object shifted
        for te_aa in [0x4000_0000, 0x8000_0000, 0xc000_0000] {
            match Grid::from_te_aa(te_aa) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q142"], "{why}");
                    // the records of that layout: the empty image and the shifted dwords, the
                    // inserted zero before the format word, render 2's object read as render 1's
                    for e in ["E728", "E825", "E827", "E829", "E847", "E865", "E897", "E906"] {
                        assert!(why.contains(e), "{te_aa:#x}: {e} not in {why}");
                    }
                }
                r => panic!("{te_aa:#x}: {r:?}"),
            }
        }
    }

    #[test]
    fn an_object_no_target_region_lists_is_refused_the_hardware_wrote_none_for_one_1000_pixels_off() {
        // zero-words baseline: x offset 1000 on a 64 x 64 target, no object and empty headers (E182);
        // nothing is recorded between that and a triangle partly on the target (E307)
        let far = [[v(1000.0, 8.0, 0.5), v(1048.0, 20.0, 0.5), v(1020.0, 56.0, 0.5)]];
        let job = Job { w: 64, h: 64, tris: &far, state: &state(), no_object: false };
        match write(&job) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q230"]);
                assert!(why.contains("no target region"), "{why}");
            }
            r => panic!("{r:?}"),
        }
        // the same triangle inside the target is written
        let near = [[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]];
        assert!(write(&Job { w: 64, h: 64, tris: &near, state: &state(), no_object: false }).is_ok());
    }

    #[test]
    fn a_triangle_whose_box_ends_on_the_targets_low_edge_is_refused_the_hardware_listed_none() {
        // E776: the tool's triangle at x offset -24.0 (x from -48 to 0.0) wrote no object, where
        // E542's tile rule (low sides closed) lists it in the first region; y alike [infer]
        let refused = |tri: [Vertex; 3]| match write(&Job {
            w: 64,
            h: 64,
            tris: &[tri],
            state: &state(),
            no_object: false,
        }) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q230"], "{why}");
                assert!(why.contains("E776"), "{why}");
            }
            r => panic!("{:?}", r.map(|_| ())),
        };
        refused([v(-48.0, 8.0, 0.5), v(0.0, 20.0, 0.5), v(-36.0, 56.0, 0.5)]);
        refused([v(8.0, -48.0, 0.5), v(20.0, 0.0, 0.5), v(56.0, -36.0, 0.5)]);
        // E776's x offset 87.5 (min x 63.5) and E736's offsets 8 and 64 are written
        let at = |dx: f32| [v(8.0 + dx, 8.0, 0.5), v(56.0 + dx, 20.0, 0.5), v(20.0 + dx, 56.0, 0.5)];
        // (the triangle spans offset - 24 to offset + 24: dx = offset - 32)
        for dx in [55.5, -24.0, 32.0] {
            assert!(
                write(&Job { w: 64, h: 64, tris: &[at(dx)], state: &state(), no_object: false }).is_ok(),
                "{dx}"
            );
        }
    }

    #[test]
    fn a_triangle_under_one_pixel_about_a_tile_corner_is_refused_no_rule_says_when_the_ta_keeps_it() {
        // E780: six triangles about the tile corner (32, 32) with boxes 0.30 to 0.98 pixel and a
        // 0.30 x 0.98 one wrote no object; E736's 0.96-pixel square (through a clamp) wrote one
        for (wx, wy) in [(0.30, 0.30), (0.98, 0.98), (0.30, 0.98), (0.5, 0.25)] {
            let tri = [
                v(32.0 - wx / 2.0, 32.0 - wy / 2.0, 0.5),
                v(32.0 + wx / 2.0, 32.0, 0.5),
                v(32.0, 32.0 + wy / 2.0, 0.5),
            ];
            match write(&Job { w: 64, h: 64, tris: &[tri], state: &state(), no_object: false }) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q230"], "{why}");
                    assert!(why.contains("E780"), "{why}");
                }
                r => panic!("{wx} x {wy}: {:?}", r.map(|_| ())),
            }
        }
        // a box of one pixel or more on either axis is the tile rule's (E542), and so are the
        // sub-pixel boxes of arith-1138's small class (E606, E607: their images and depth replay),
        // case 272 (0.65 x 0.64 pixel, no corner) and case 336 (about the pixel corner (53, 11))
        for t in [[11962, 5516, 12105, 5618, 12128, 5456], [13569, 2785, 13478, 2852, 13467, 2814]] {
            let p = |i: usize| v(t[i] as f32 / 256.0, t[i + 1] as f32 / 256.0, 0.5);
            let small = [p(0), p(2), p(4)];
            assert!(write(&Job { w: 64, h: 64, tris: &[small], state: &state(), no_object: false }).is_ok());
        }
        let thin = [v(32.0, 8.0, 0.5), v(32.5, 8.0, 0.5), v(32.25, 40.0, 0.5)];
        assert!(write(&Job { w: 64, h: 64, tris: &[thin], state: &state(), no_object: false }).is_ok());
    }

    #[test]
    fn a_window_coordinate_with_more_than_8_fraction_bits_or_past_the_field_is_refused() {
        let at = |x: f32, y: f32| {
            object_words(&[[v(x, y, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]], &state())
        };
        // multiples of 1/256 (8 + 1/256) are exact in the packed field
        assert!(at(8.0 + 1.0 / 256.0, 8.0).is_ok());
        assert!(at(8.0, 8.0 + 1.0 / 256.0).is_ok());
        for (x, y) in [(8.001, 8.0), (8.0, 8.001), (8.0, 61440.0), (-4097.0, 8.0)] {
            match at(x, y) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q230"], "({x}, {y})"),
                r => panic!("({x}, {y}): {r:?}"),
            }
        }
    }

    #[test]
    fn a_coordinate_on_the_1_over_1024_grid_is_packed_rounded_to_nearest_e778() {
        // E778's three held-out triangles (odd multiples of 1/1024, no ties) and the
        // 24-bit fields the hardware stored, x then y per vertex
        let cases: [([f32; 6], [u64; 6]); 3] = [
            (
                [8239.0, 8341.0, 57367.0, 20727.0, 20573.0, 57373.0],
                [1050636, 1050661, 1062918, 1053758, 1053719, 1062919],
            ),
            (
                [8309.0, 8207.0, 57535.0, 20533.0, 20559.0, 57559.0],
                [1050653, 1050628, 1062960, 1053709, 1053716, 1062966],
            ),
            (
                [8359.0, 8263.0, 57469.0, 20519.0, 20717.0, 57447.0],
                [1050666, 1050642, 1062943, 1053706, 1053755, 1062938],
            ),
        ];
        for (nums, fields) in cases {
            for (n, f) in nums.iter().zip(fields) {
                assert_eq!(pack_coordinate(n / 1024.0), Some(f), "{n} / 1024");
            }
        }
        // the grid of 1/256 stays exact (E651), and the cases E778 did not run stay refused: a tie
        // (a numerator 2 mod 4), a finer grid, and a field past 24 bits
        assert_eq!(pack_coordinate(8.0), Some(1050624));
        assert_eq!(pack_coordinate(8.0 + 1.0 / 256.0), Some(1050625));
        for c in [8.0 + 2.0 / 1024.0, 8.0 + 1.0 / 2048.0, 8.001, 61440.0, -4097.0] {
            assert_eq!(pack_coordinate(c), None, "{c}");
        }
    }

    #[test]
    fn the_ta_writes_one_header_array_at_te_0x20_and_four_at_te_0xe0_e763_e788() {
        // E763 (and E788's a4): one array of the target's own layout at 0x20000000; E788: four at
        // 0xe0000000 (E729 alone left 4 or 5, its correction: E788 and E824 hold 4)
        assert_eq!(header_arrays(0x2000_0000), Ok(1));
        assert_eq!(header_arrays(0), Ok(1));
        assert_eq!(header_arrays(0xe000_0000), Ok(4));
        // one halved axis: no record dumped or faulted its layout of arrays
        for te_aa in [0x6000_0000, 0xa000_0000, 0x4000_0000] {
            assert!(matches!(header_arrays(te_aa), Err(Outcome::Unsupported { .. })), "{te_aa:#x}");
        }
        // the target's own array size: 12 bytes a region of its 1x grid
        assert_eq!(rgn_size(256, 160), 0x600);
        assert_eq!(rgn_size(320, 400), 0x1800);
        assert_eq!(rgn_size(544, 400), 0x2400);
    }

    #[test]
    fn a_full_triangle_fills_each_array_as_e788_counted_and_nothing_past_the_fourth() {
        // E788: non-zero dwords per slot of the target's rgn_size from 0x4000 (a1, a2, a5); E763's
        // a4 at TE 0x20: 512 headers and 250 streams in one array
        let te = 0xe000_0000;
        assert_eq!(array_dwords(256, 160, te), Ok(vec![256, 160, 256, 160]));
        assert_eq!(array_dwords(320, 128, te), Ok(vec![256, 256, 160, 160]));
        assert_eq!(array_dwords(320, 400, te), Ok(vec![1024, 800, 640, 584]));
        assert_eq!(array_dwords(320, 400, 0x2000_0000), Ok(vec![762]));
        // four macrotiles a side at TE 0xe0: no dump read its arrays
        assert!(matches!(array_dwords(640, 480, te), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn the_kernels_ta_data_layout_is_e763_e788_and_e824s_sizes() {
        // one array (module B21FDA82): E763's and E788's 0xa000 for 544 x 400, E788's dumps of
        // 0x6000 at 256 x 160 and 320 x 128
        let one = |w, h| tadata_layout(w, h, 1).unwrap();
        assert_eq!((one(544, 400).rgn, one(544, 400).size), (0x4000, 0xa000));
        assert_eq!(one(256, 160).size, 0x6000);
        assert_eq!(one(320, 128).size, 0x6000);
        // four arrays (E824, render_rgn_arrays 4): the TA data sizes it read, and 64 x 64 at both
        for ((w, h), size) in [
            ((288, 144), 0x8000),
            ((256, 288), 0x8000),
            ((384, 384), 0xb000),
            ((320, 160), 0x8000),
            ((512, 384), 0xb000),
            ((640, 480), 0x13000),
            ((320, 400), 0xc000),
            ((1024, 768), 0x1e000),
            ((64, 64), 0x6000),
        ] {
            assert_eq!(tadata_layout(w, h, 4).unwrap().size, size, "{w}x{h}");
        }
        assert_eq!(one(64, 64).size, 0x6000);
        assert!(tadata_layout(64, 64, 2).is_err());
    }

    #[test]
    fn a_4x_layout_faults_at_the_end_of_the_ta_data_when_four_arrays_pass_it_e729_e788() {
        use HeaderEnding::*;
        let te = 0xe000_0000;
        // E729 (own contexts, one array): two complete, three fault at pages 6, 6 and 8
        for ((w, h), end) in [
            ((256, 160), Complete),
            ((320, 128), Complete),
            ((288, 144), Fault { page: 6 }),
            ((256, 288), Fault { page: 6 }),
            ((384, 384), Fault { page: 8 }),
        ] {
            assert_eq!(header_layout_ending(w, h, w, h, te, 1), Ok(end), "{w}x{h}");
        }
        // E788: a4 (TE 0x20 in 544 x 400) and a5 (TE 0xe0, room for exactly four arrays)
        // complete, a6 (its own 320 x 400 context) faults at page 8
        assert_eq!(header_layout_ending(320, 400, 544, 400, 0x2000_0000, 1), Ok(Complete));
        assert_eq!(header_layout_ending(320, 400, 544, 400, te, 1), Ok(Complete));
        assert_eq!(header_layout_ending(320, 400, 320, 400, te, 1), Ok(Fault { page: 8 }));
        // E824: four arrays complete every held-out size; its control at one array faults
        for (w, h) in
            [(288, 144), (256, 288), (384, 384), (320, 160), (512, 384), (640, 480), (320, 400), (1024, 768)]
        {
            assert_eq!(header_layout_ending(w, h, w, h, te, 4), Ok(Complete), "{w}x{h}");
        }
        assert_eq!(header_layout_ending(288, 144, 288, 144, te, 1), Ok(Fault { page: 6 }));
    }

    #[test]
    fn where_only_f_4_against_5_decides_the_ending_is_refused_unless_measured() {
        // room for four arrays and not five: E729 alone leaves f at 4 or 5; E788's a5 measured
        // 320 x 400 in 544 x 400, the same room at 288 x 400 was never run
        let te = 0xe000_0000;
        assert_eq!(header_layout_ending(320, 400, 544, 400, te, 1), Ok(HeaderEnding::Complete));
        match header_layout_ending(288, 400, 544, 400, te, 1) {
            Err(Outcome::Unsupported { why, ids }) => {
                assert_eq!(ids, ["Q140"]);
                assert!(why.contains("E729") && why.contains("E788"), "{why}");
            }
            r => panic!("{r:?}"),
        }
        // a target past its context, and a TE word whose arrays are not measured
        assert!(header_layout_ending(544, 400, 320, 400, te, 1).is_err());
        assert!(header_layout_ending(64, 64, 64, 64, 0x6000_0000, 1).is_err());
    }

    #[test]
    fn four_macrotiles_in_a_row_are_refused_the_headers_were_dumped_for_two_only() {
        let near = [[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]];
        // n = 4 from 640 x 480 pixels in area (E506, the library's rule); 576 x 480 and 640 x 416 stay at two
        for (w, h, ok) in [(640, 480, false), (1024, 768, false), (576, 480, true), (640, 416, true)] {
            let r = write(&Job { w, h, tris: &near, state: &state(), no_object: false });
            match (ok, r) {
                (true, Ok(_)) => {}
                (false, Err(Outcome::Unsupported { ids, .. })) => assert!(ids.contains(&"Q139".to_string())),
                (_, r) => panic!("{w} x {h}: {:?}", r.map(|_| ())),
            }
        }
    }
}
