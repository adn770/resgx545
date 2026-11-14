// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r16-zls's kept rows (`render/closing-r16-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured:
//! stage zpass2's load passes through `zls::pass_plane` fed their no-load twins' planes (E1059),
//! stage zovp's passes over overlapping tiles from the kept full-pitch references and its kept
//! NaN loads in formats 1 and 2 (E1064), stage zbits4's stencil passes over overlapping tiles,
//! bit 23 under another reference, compare mask and background stencil and bit 0 with a loaded
//! stencil (E1063, E1064), and stage zoff's z offsets below 0.5 refused by `mte::triangle`
//! (E1066), each dword or byte with nothing else changed.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::{mte, zls};

const ATTEMPT: &str = "render/closing-r16-zls/out/20261114-092344";
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

fn text(c: &Ctx, stage: &str, name: &str) -> String {
    String::from_utf8(gz(c, &format!("{ATTEMPT}/{stage}/{name}.txt.gz"))).unwrap()
}

fn drawn(c: &Ctx, stage: &str, name: &str) -> u64 {
    text(c, stage, name)
        .lines()
        .find_map(|l| {
            let r = l.strip_prefix("tri ")?;
            r.split_once(" #1: ")?.1.split(' ').next()?.parse().ok()
        })
        .unwrap()
}

/// the pixels of the `row Y:` lines in the triangle's colour
fn pixels(c: &Ctx, stage: &str, name: &str) -> std::collections::BTreeSet<(u32, u32)> {
    let mut out = std::collections::BTreeSet::new();
    for l in text(c, stage, name).lines() {
        let Some((y, vals)) = l.strip_prefix("row ").and_then(|r| r.split_once(": ")) else { continue };
        let y: u32 = y.parse().unwrap();
        for (x, v) in vals.split(' ').enumerate() {
            if v == "0xff00ff00" {
                out.insert((x as u32, y));
            }
        }
    }
    out
}

/// bit:K of t10: 0.75f where bit K of the dword index is set, else 0.25f
fn bit_fill(k: u32) -> impl Fn(u32) -> u32 {
    move |i| if i >> k & 1 == 1 { 0.75f32.to_bits() } else { 0.25f32.to_bits() }
}

fn same(name: &str, kept: &[u32], words: &std::collections::BTreeMap<u32, u32>) {
    let hit = words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
    assert_eq!(hit, words.len(), "{name}");
    let other =
        kept.iter().enumerate().filter(|&(i, &v)| v != FILL && !words.contains_key(&(i as u32))).count();
    assert_eq!(other, 0, "{name}");
}

#[test]
fn zpass2_every_pass_stores_its_twin_s_plane_against_the_load() {
    let Some(c) = ctx() else { return };
    let ctl = zls::Ctl::decode(0x0017_500e).unwrap();
    for k in ["z125", "z0625", "z1", "z3", "z375", "z625", "z5e20"] {
        let pass = if k == "z125" { format!("zp2-c-{k}") } else { format!("zp2-p-{k}") };
        let twin = dump(&c, "zpass2", &format!("zp2-t-{k}"), "depth-store");
        let plane = |x: u32, y: u32| f32::from_bits(twin[zls::store_dword(x, y, 1) as usize]);
        let p =
            zls::pass_plane(&ctl, 64, 32, 1.0, &plane, zls::Test::Less, &|_, _| true, &bit_fill(9), &|i| i)
                .unwrap();
        same(&pass, &dump(&c, "zpass2", &pass, "depth-store"), &p.depth);
        assert_eq!(p.drawn, drawn(&c, "zpass2", &pass), "{pass}");
    }
}

#[test]
fn zovp_a_pass_over_overlapping_tiles_keeps_the_tile_visited_last_and_a_kept_nan_saturates() {
    let Some(c) = ctx() else { return };
    let r10x = "render/closing-r10-x/out/20261113-101116/zov";
    let fill = |_: u32| 0x3e4c_cccd;
    for (name, word, w, h, reference, g_full) in [
        ("zo-c-64", 0x0017_1004u32, 64u32, 32u32, "zov-64x32-ctl", 1u32),
        ("zo-p-64", 0x0017_5006, 64, 32, "zov-64x32-ctl", 1),
        ("zo-p-160", 0x0017_5016, 160, 48, "zov-160x48-ctl", 4),
    ] {
        let full = dwords(&gz(&c, &format!("{r10x}/{reference}.depth.1.bin.gz")));
        let plane = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, g_full) as usize]);
        let ctl = zls::Ctl::decode(word).unwrap();
        let p =
            zls::pass_plane(&ctl, w, h, 1.0, &plane, zls::Test::Less, &|_, _| true, &fill, &|i| i).unwrap();
        same(name, &dump(&c, "zovp", name, "depth-store"), &p.depth);
        assert_eq!(p.drawn, drawn(&c, "zovp", name), "{name}");
    }
    for (name, word, v) in [
        ("zo-n1-7fc", 0x0117_500eu32, 0x7fc0_0000u32),
        ("zo-n2-7fc", 0x0217_500e, 0x7fc0_0000),
        ("zo-n1-ffc", 0x0117_500e, 0xffc0_0000),
        ("zo-n1-7f8", 0x0117_500e, 0x7f80_0001),
        ("zo-n2-7f8", 0x0217_500e, 0x7f80_0001),
    ] {
        let ctl = zls::Ctl::decode(word).unwrap();
        let p = zls::pass(&ctl, 64, 32, 1.0, 0.5, zls::Test::Never, &|_, _| true, &|_| v, &|i| i).unwrap();
        same(name, &dump(&c, "zovp", name, "depth-store"), &p.depth);
        assert_eq!(p.drawn, 0, "{name}");
    }
}

#[test]
fn zbits4_stencil_rows_read_as_the_stencil_source_says_and_bit_0_stores_its_twin() {
    let Some(c) = ctx() else { return };
    let bytes = |i: u32| (i & 0xff) as u8;
    // (name, control, width, height, ISP word 2, reference)
    for (name, word, w, h, isp2, reference) in [
        ("zo-s-64", 0x0017_3006u32, 64u32, 32u32, 0x0405_01ffu32, 0u8),
        ("zo-s-160", 0x0017_3016, 160, 48, 0x0405_01ff, 0),
        ("zb4-23-ref", 0x0097_300e, 64, 32, 0x0405_01ff, 0x80),
        ("zb4-23-msk", 0x0097_300e, 64, 32, 0x0405_ffff, 0),
        ("zb4-23-bg", 0x0097_300e, 64, 32, 0x0405_01ff, 0),
    ] {
        let ctl = zls::Ctl::decode(word).unwrap();
        let src = zls::stencil_source(&ctl).unwrap();
        let st = gz(&c, &format!("{ATTEMPT}/zbits4/{name}.stencil-store.1.bin.gz"));
        let px = pixels(&c, "zbits4", name);
        // a slot shared by overlapping tiles holds the last tile's bytes (zls::visit_order)
        let mut want = std::collections::BTreeMap::new();
        let mut n = 0;
        for (tx, ty) in zls::visit_order(w, h) {
            for k in 0..512 {
                let (xx, yy) = zls::in_tile_pixel(k);
                let (x, y) = (32 * tx + xx, 16 * ty + yy);
                let p = zls::stencil_byte(x, y, ctl.g());
                let read = match src {
                    zls::StencilSource::Loaded => bytes(p),
                    zls::StencilSource::Column => zls::column_byte(x),
                    s => panic!("{name}: {s:?}"),
                };
                let (pass, new) = zls::stencil_test(isp2, reference, read, true);
                n += u64::from(pass);
                assert_eq!(pass, px.contains(&(x, y)), "{name} ({x}, {y})");
                want.insert(p, new);
            }
        }
        for (i, &b) in st.iter().enumerate() {
            let e = want.get(&(i as u32)).copied().unwrap_or((FILL >> (8 * (i % 4))) as u8);
            assert_eq!(b, e, "{name} byte {i}");
        }
        assert_eq!(n, drawn(&c, "zbits4", name), "{name}");
    }
    // bit 0 with a loaded stencil: decoded (it stores what the control without it stores), no
    // colour pixel, the dumps the kept twin's (the scorer's H-B0, 4 of 4)
    for word in [0x0017_300fu32, 0x0016_300f, 0x0617_300f, 0x0717_300f] {
        let ctl = zls::Ctl::decode(word).unwrap();
        assert!(!ctl.writes_pixels() && ctl.load_stencil(), "{word:#x}");
    }
    for name in ["zb4-b0-st", "zb4-b0-f6", "zb4-b0-f7", "zb4-b0-c16"] {
        assert_eq!(drawn(&c, "zbits4", name), 0, "{name}");
    }
}

#[test]
fn zbits4_bit_20_cleared_moves_the_format_6_and_7_records_and_refuses() {
    let Some(c) = ctx() else { return };
    // post hoc (fold/look.out): the twin's per-tile records packed one after another from dword
    // 2048; the formats 5 to 7 refuse (Q120) and bit 20 cleared with them names Q071
    for (name, word, n) in [("zb4-20-f6", 0x0607_300eu32, 176usize), ("zb4-20-f7", 0x0707_300e, 48)] {
        let d = dump(&c, "zbits4", name, "depth");
        let idx: Vec<usize> = d.iter().enumerate().filter(|&(_, &v)| v != FILL).map(|(i, _)| i).collect();
        assert_eq!(idx, (2048..2048 + n).collect::<Vec<_>>(), "{name}");
        let o = zls::Ctl::decode(word).unwrap_err();
        assert!(format!("{o:?}").contains("Q071"), "{name}: {o:?}");
    }
}

#[test]
fn zoff_a_viewport_depth_below_0_is_refused() {
    let Some(c) = ctx() else { return };
    // E1066: with the z offset w and scale s a vertex at w - s < 0 does not store w + s (2 t - 1):
    // the plane was (1.6 w + 0.4 s) t outside 912 pixels on E987's triangle (H-LIN 6 of 6, H-LIN-S
    // 2 of 2), so the model refuses it
    assert_eq!(drawn(&c, "zoff", "zw2-w0"), 32768);
    // the library's state block at 256 x 128 (render.c: vp 128, 128, 64, 64; z 0.5, 0.5)
    let f = |v: f32| v.to_bits();
    let mut b = vec![
        0xdf43,
        0x01d0_0200,
        0x10f0,
        0x0400_0004,
        0x0003_0001,
        0x0400_0000,
        f(128.0),
        f(128.0),
        f(64.0),
        f(64.0),
        f(0.5),
        f(0.5),
        0,
        0x43000,
        0x3727_c5ac,
        0x0155_5620,
        0,
        0,
    ];
    b[10] = 0.125f32.to_bits();
    let s = mte::state(&b).unwrap();
    let v = |x: f32, y: f32, z: f32| [x, y, z, 1.0].map(f32::to_bits);
    let t = [v(-1.0, -1.0, -1.0), v(3.0, -1.0, 1.0), v(-1.0, 3.0, -1.0)];
    let o = mte::triangle(&s, t, 0, 0).unwrap_err();
    assert!(format!("{o:?}").contains("Q069"), "{o:?}");
    b[10] = 0.5f32.to_bits();
    assert!(mte::triangle(&mte::state(&b).unwrap(), t, 0, 0).is_ok());
}
