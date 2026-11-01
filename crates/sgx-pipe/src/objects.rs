// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! What the ISP reads of the TA's output (12.3): the region header of a 32 x 16 tile, the control
//! stream it points at, and the object that stream names (the inverse of `ta::write`, over the
//! forms E176, E177, E180, E306, E541, E651 and E652 record). Everything else refuses (Q070).

use crate::Outcome;
use crate::isp::Tri;
use crate::ta::{self, HEADERS_AT, OBJECT_AT};
use std::collections::BTreeMap;

fn open(why: impl AsRef<str>, id: &str) -> Outcome {
    Outcome::unsupported(why.as_ref(), &[id])
}

/// The ISP-visible object: its pixel PDS words (E306), its ISP words, its triangles in list order.
#[derive(Debug, Clone, PartialEq)]
pub struct Object {
    pub pds: [u32; 3],
    pub isp: [u32; 2],
    pub prims: Vec<Prim>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Prim {
    pub tri: Tri,
    /// the winding mark the TA wrote (bit 15 of the list entry): the area is negative
    pub negative: bool,
    pub rhw: [f32; 3],
}

/// Which primitives of an object a tile's two 16 x 16 halves are listed with (bit k = primitive k).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Listing {
    pub isp_addr: u32,
    pub nprims: u32,
    pub left: u32,
    pub right: u32,
}

fn word(m: &BTreeMap<u32, u32>, a: u32) -> u32 {
    m.get(&a).copied().unwrap_or(0)
}

/// The object whose ISP words are at dword address `isp` of the parameter slot and which holds
/// `n` triangles (position only, 1/w stored: `ta::object_layout(0, 0, 0)`).
pub fn read_object(param: &BTreeMap<u32, u32>, isp: u32, n: u32) -> Result<Object, Outcome> {
    let at = |i: i64| ((isp as i64 + i) * 4) as u32;
    let pds_at = -3 - 3 * n as i64; // relative to the ISP words
    if !(1..=5).contains(&n) || isp as i64 + pds_at < 0 {
        return Err(open(format!("an object of {n} primitives at {isp:#x}"), "Q070"));
    }
    let pds = [0, 1, 2].map(|k| word(param, at(pds_at + k)));
    let rhw: Vec<f32> = (0..3 * n as i64).map(|k| f32::from_bits(word(param, at(pds_at + 3 + k)))).collect();
    let isp_words = [word(param, at(0)), word(param, at(1))];
    let entries = n.div_ceil(2) as i64;
    let lay = ta::object_layout(0, 0, 0)?;
    let (lw, fmt) = (word(param, at(2 + entries)), word(param, at(3 + entries)));
    let masks = [0, 1, 2, 3].map(|k| word(param, at(4 + entries + k)));
    if fmt != lay.format_hi << 16 | lay.iterated << 8 | lay.stored || masks != lay.masks {
        return Err(open(
            format!(
                "an object format word {fmt:#x} with masks {masks:x?}: only position and 1/w are modelled (E541)"
            ),
            "Q070",
        ));
    }
    if lw != (isp_words[1] >> 8 & 0xff) * 0x101 {
        return Err(open("the line widths of an object are not ISP word 1's (E176)", "Q070"));
    }
    let vbase = 4 + entries + 4;
    let bit = |pos: u64, w: u32| -> u64 {
        (0..w as u64).fold(0, |a, i| {
            let b = pos + i;
            a | ((word(param, at(vbase + (b / 32) as i64)) as u64 >> (b % 32)) & 1) << i
        })
    };
    let mut prims = vec![];
    for p in 0..n {
        let e = word(param, at(2 + (p / 2) as i64)) >> (16 * (p % 2)) & 0xffff;
        let v0 = 16 + 3 * p;
        if e & 0x7fff != v0 | (v0 + 1) << 5 | (v0 + 2) << 10 {
            return Err(open(format!("primitive list entry {e:#x} of primitive {p}"), "Q070"));
        }
        let mut v = [(0i64, 0i64); 3];
        let mut z = [0f32; 3];
        for k in 0..3u64 {
            let o = 80 * (3 * p as u64 + k);
            // Y then X, 24 bits of (coordinate + 4096) * 256, then the depth float (E651)
            let (y, x) = (bit(o, 24) as i64 - 4096 * 256, bit(o + 24, 24) as i64 - 4096 * 256);
            v[k as usize] = (x, y);
            z[k as usize] = f32::from_bits(bit(o + 48, 32) as u32);
        }
        prims.push(Prim {
            tri: Tri { v, z },
            negative: e >> 15 != 0,
            rhw: [rhw[3 * p as usize], rhw[3 * p as usize + 1], rhw[3 * p as usize + 2]],
        });
    }
    Ok(Object { pds, isp: isp_words, prims })
}

/// The listing of tile (tx, ty) of a w x h target, or None when the region has no stream (flag
/// 0x08) or lies outside it. `param` and `tadata` are `ta::Written`'s maps.
pub fn listing(
    param: &BTreeMap<u32, u32>,
    tadata: &BTreeMap<u32, u32>,
    t: &ta::Tiling,
    tile: (u32, u32),
) -> Result<Option<Listing>, Outcome> {
    let (c, r) = tile;
    let m = (c / t.mx) * t.n + r / t.my;
    let i = (r % t.my) * t.mx + c % t.mx;
    let hdr = HEADERS_AT + 12 * (m * t.mx * t.my + i);
    let w0 = word(tadata, hdr);
    if w0 >> 24 & 0x02 != 0 {
        return Err(open("a region header marked outside the target for a tile of it", "Q231"));
    }
    if w0 >> 24 & 0x08 != 0 {
        return Ok(None);
    }
    let at = word(tadata, hdr + 4);
    let w = |k: u32| word(param, at + 4 * k);
    let (head, obj) = (w(0), w(1));
    let (form, low) = (head >> 16 & 0xff, head & 0xffff);
    let nprims = (head >> 25 & 0xf) + 1;
    if head >> 29 != 2 || nprims % 3 != 0 || obj >> 26 != 2 * (nprims / 3) - 1 {
        return Err(open(format!("a control stream starting {head:#x} {obj:#x}"), "Q231"));
    }
    let n = nprims / 3;
    let isp_addr = obj & 0x03ff_ffff;
    let (left, right, used) = match form {
        0x90 if low == 0xffff => ((1 << n) - 1, (1 << n) - 1, 2),
        0x80 => (low & 0xff, 0, 2),
        0x98 => (0, low & 0xff, 2),
        0x8a => (w(2), 0, 3),
        0x8c => (0, w(2), 3),
        0x88 => (w(2) & 0xffff, w(2) >> 16, 3),
        _ => return Err(open(format!("a control stream form {form:#x}"), "Q231")),
    };
    if (used..8).any(|k| w(k) != 0xc000_0000) {
        return Err(open("more than one object in a control stream block", "Q231"));
    }
    Ok(Some(Listing { isp_addr, nprims: n, left, right }))
}

/// `OBJECT_AT` as a dword address, for the callers that compute where the first object's ISP
/// words sit.
pub const OBJECT_DWORD: u32 = OBJECT_AT / 4;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::mte::{State, Vertex};

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

    fn written(tris: &[[Vertex; 3]], w: u32, h: u32) -> ta::Written {
        ta::write(&ta::Job { w, h, tris, state: &state(), no_object: false }).unwrap()
    }

    #[test]
    fn the_object_the_ta_wrote_reads_back_with_its_words_and_vertices() {
        let t = [
            [v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.25), v(20.0, 56.0, 0.75)],
            [v(1.5, 2.25, 0.5), v(9.0, 3.0, 0.5), v(4.0, 12.0, 0.5)],
        ];
        let w = written(&t, 64, 64);
        let o = read_object(&w.param, OBJECT_DWORD + 3 + 6, 2).unwrap();
        assert_eq!((o.pds, o.isp), (state().pds, state().isp));
        assert_eq!(o.prims.len(), 2);
        assert_eq!(o.prims[0].tri.v, [(8 * 256, 8 * 256), (56 * 256, 20 * 256), (20 * 256, 56 * 256)]);
        assert_eq!(o.prims[0].tri.z, [0.5, 0.25, 0.75]);
        assert_eq!(o.prims[1].tri.v[0], (384, 576), "1.5 and 2.25 pixels on the 1/256 grid");
        assert!(!o.prims[0].negative);
        assert_eq!(o.prims[0].rhw, [1.0; 3]);
    }

    #[test]
    fn the_winding_mark_reads_back() {
        let w = written(&[[v(8.0, 8.0, 0.5), v(20.0, 56.0, 0.5), v(56.0, 20.0, 0.5)]], 64, 64);
        assert!(read_object(&w.param, OBJECT_DWORD + 6, 1).unwrap().prims[0].negative);
    }

    #[test]
    fn a_format_word_the_model_does_not_know_refuses_naming_q070() {
        let mut w = written(&[[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]], 64, 64);
        w.param.insert(OBJECT_AT + 4 * 10, 0x0004_0201);
        match read_object(&w.param, OBJECT_DWORD + 6, 1) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q070"]),
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn a_tiles_listing_is_the_one_the_ta_wrote_for_its_region() {
        let tri = [[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]];
        let w = written(&tri, 64, 64);
        let t = ta::tiling(64, 64);
        // tile (0, 0): the triangle starts at x = 8: it meets the left 16 x 16 tile, and the right
        // one (x 16 to 31) too since it reaches x = 56
        let l = listing(&w.param, &w.tadata, &t, (0, 0)).unwrap().unwrap();
        assert_eq!((l.isp_addr, l.nprims), (0x406, 1));
        assert_eq!((l.left, l.right), (1, 1));
        // tile (1, 0): x 32 to 63, y 0 to 15: the triangle's top edge reaches (56, 20): meets it on the right half
        let some = listing(&w.param, &w.tadata, &t, (1, 0)).unwrap();
        assert!(some.is_some());
        // a region with no stream: tile (1, 3) lies beyond the hypotenuse of this triangle
        assert_eq!(listing(&w.param, &w.tadata, &t, (1, 3)).unwrap(), None);
    }

    #[test]
    fn a_stream_with_a_second_object_refuses() {
        let tri = [[v(8.0, 8.0, 0.5), v(56.0, 20.0, 0.5), v(20.0, 56.0, 0.5)]];
        let mut w = written(&tri, 64, 64);
        let t = ta::tiling(64, 64);
        let at = w.tadata[&(HEADERS_AT + 4)];
        w.param.insert(at + 4 * 3, 0x4400_0000);
        assert!(matches!(listing(&w.param, &w.tadata, &t, (0, 0)), Err(Outcome::Unsupported { .. })));
    }
}
