// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r17-zls's kept rows (`render/closing-r17-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured: stage
//! zovp2's depth load passes over overlapping tiles with edge tiles through `zls::pass_plane` fed
//! the kept full-pitch references' planes (E1068), stage zovs2's stencil passes over the same
//! tiles with the pixels beyond E831's band keeping their load (E1068), and stage zb20's bit 20
//! cleared records packed from dword 2048 (E1069), each dword or byte with nothing else changed.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::zls;

const ATTEMPT: &str = "render/closing-r17-zls/out/20261114-104614";
const R14: &str = "render/closing-r14-zls/out/20261114-054846/zodd";
const FILL: u32 = 0xdead_beef;

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(ATTEMPT).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATTEMPT} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {ATTEMPT} (set RESGX545_DATA)");
    None
}

fn gz(c: &Ctx, rel: &str) -> Vec<u8> {
    c.read_gz(rel, "").unwrap()
}

fn dump(c: &Ctx, stage: &str, name: &str, suffix: &str) -> Vec<u32> {
    dwords(&gz(c, &format!("{ATTEMPT}/{stage}/{name}.{suffix}.1.bin.gz")))
}

fn drawn(c: &Ctx, stage: &str, name: &str) -> u64 {
    let t = String::from_utf8(gz(c, &format!("{ATTEMPT}/{stage}/{name}.txt.gz"))).unwrap();
    t.lines()
        .find_map(|l| {
            let r = l.strip_prefix("tri ")?;
            r.split_once(" #1: ")?.1.split(' ').next()?.parse().ok()
        })
        .unwrap()
}

fn same(name: &str, kept: &[u32], words: &std::collections::BTreeMap<u32, u32>) {
    let hit = words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
    assert_eq!(hit, words.len(), "{name}");
    let other =
        kept.iter().enumerate().filter(|&(i, &v)| v != FILL && !words.contains_key(&(i as u32))).count();
    assert_eq!(other, 0, "{name}");
}

#[test]
fn zovp2_a_load_pass_over_overlapping_tiles_with_edge_tiles_keeps_the_tile_visited_last() {
    let Some(c) = ctx() else { return };
    let fill = |_: u32| 0x3e4c_cccd;
    // (name, control, width, height, E1041's kept full-pitch reference, its pitch)
    for (name, word, w, h, reference, g_full) in [
        ("zo2-c-65", 0x0017_100cu32, 65u32, 33u32, "zo-65-f0", 2u32),
        ("zo2-c-63", 0x0017_1004, 63, 31, "zo-63-f0", 1),
        ("zo2-p-65", 0x0017_500e, 65, 33, "zo-65-f0", 2),
        ("zo2-p-63", 0x0017_5006, 63, 31, "zo-63-f0", 1),
    ] {
        let full = dwords(&gz(&c, &format!("{R14}/{reference}.depth.1.bin.gz")));
        let plane = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, g_full) as usize]);
        let ctl = zls::Ctl::decode(word).unwrap();
        let p =
            zls::pass_plane(&ctl, w, h, 1.0, &plane, zls::Test::Less, &|_, _| true, &fill, &|i| i).unwrap();
        same(name, &dump(&c, "zovp2", name, "depth-store"), &p.depth);
        assert_eq!(p.drawn, drawn(&c, "zovp2", name), "{name}");
    }
}

#[test]
fn zovs2_a_stencil_pass_over_overlapping_edge_tiles_tests_the_band_and_keeps_the_load_past_it() {
    let Some(c) = ctx() else { return };
    let bytes = |i: u32| (i & 0xff) as u8;
    for (name, word, w, h) in [("zo2-s-65", 0x0017_300eu32, 65u32, 33u32), ("zo2-s-63", 0x0017_3006, 63, 31)]
    {
        let ctl = zls::Ctl::decode(word).unwrap();
        assert_eq!(zls::stencil_source(&ctl).unwrap(), zls::StencilSource::Loaded);
        let st = gz(&c, &format!("{ATTEMPT}/zovs2/{name}.stencil-store.1.bin.gz"));
        // a slot shared by overlapping tiles holds the last tile's bytes (zls::visit_order); a
        // pixel beyond the target is tested inside E831's band and keeps its load past it
        let mut want = std::collections::BTreeMap::new();
        let mut n = 0;
        for (tx, ty) in zls::visit_order(w, h) {
            for k in 0..512 {
                let (xx, yy) = zls::in_tile_pixel(k);
                let (x, y) = (32 * tx + xx, 16 * ty + yy);
                let p = zls::stencil_byte(x, y, ctl.g());
                let read = bytes(p);
                let tested = (x < w && y < h) || zls::in_band(x, y, w, h);
                let (pass, new) =
                    if tested { zls::stencil_test(0x0405_01ff, 0, read, true) } else { (false, read) };
                n += u64::from(pass && x < w && y < h);
                want.insert(p, new);
            }
        }
        for (i, &b) in st.iter().enumerate() {
            let e = want.get(&(i as u32)).copied().unwrap_or((FILL >> (8 * (i % 4))) as u8);
            assert_eq!(b, e, "{name} byte {i}");
        }
        assert_eq!(n, drawn(&c, "zovs2", name), "{name}");
    }
}

#[test]
fn zb20_bit_20_cleared_packs_the_format_6_and_7_records_from_dword_2048_and_refuses() {
    let Some(c) = ctx() else { return };
    // (cleared row, its bit-20-set twin, the control word of the row)
    for (name, twin, word) in [
        ("zb20-b-6-96", "zb20-t-6-96", 0x0607_3016u32),
        ("zb20-b-7-96", "zb20-t-7-96", 0x0707_3016),
        ("zb20-b-6-128", "zb20-t-6-128", 0x0607_301e),
        ("zb20-b-7-128", "zb20-t-7-128", 0x0707_301e),
    ] {
        let row = dump(&c, "zb20", name, "depth");
        let tw = dump(&c, "zb20", twin, "depth");
        let recs: Vec<u32> = tw.iter().copied().filter(|&v| v != FILL).collect();
        let idx: Vec<usize> = row.iter().enumerate().filter(|&(_, &v)| v != FILL).map(|(i, _)| i).collect();
        assert_eq!(idx, (2048..2048 + recs.len()).collect::<Vec<_>>(), "{name}");
        let got: Vec<u32> = idx.iter().map(|&i| row[i]).collect();
        assert_eq!(got, recs, "{name}: the twin's dwords in address order");
        let o = zls::Ctl::decode(word).unwrap_err();
        assert!(format!("{o:?}").contains("Q071"), "{name}: {o:?}");
    }
}
