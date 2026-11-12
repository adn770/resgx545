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
    /// shifts the object (E888): refused, as is any other bit.
    pub fn from_te_aa(te_aa: u32) -> Result<Grid, Outcome> {
        if te_aa & !0xe000_0000 != 0 || (te_aa & 0xc000_0000 != 0 && te_aa & 0x2000_0000 == 0) {
            return Err(refuse_ids(
                format!(
                    "CR_TE_AA {te_aa:#x}: only bits 31 and 30 with bit 29 are a region grid (E893); without bit 29 the triangle is removed (E281, E888)"
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

/// A macrotile's local region indices (`row * across + column`) in header order: raster on the
/// library's grid (E652), 4 x 4-region sub-blocks in raster order, raster inside one, on a halved
/// grid (E893, measured with library macrotiles of 4 x 4 regions).
pub fn header_order(t: &Tiling, grid: Grid) -> Vec<u32> {
    let (fx, fy) = grid.per_macrotile(t);
    let mut order: Vec<u32> = (0..fx * fy).collect();
    if grid != Grid::LIBRARY {
        order.sort_by_key(|&i| {
            let (c, r) = (i % fx, i / fx);
            (r / 4, c / 4, r % 4, c % 4)
        });
    }
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
            assert!(Grid::from_te_aa(te_aa).is_err(), "{te_aa:#x}");
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
