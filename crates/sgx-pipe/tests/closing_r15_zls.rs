// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r15-zls's kept rows (`render/closing-r15-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured:
//! stage zpass's load-pass rows through `zls::pass` (E1050: edge tiles, bit 19, formats 1 and 2,
//! other depths; zp-z125's plane is the store's own floats, Q200), stage zovl's overlapping and
//! integer rows through `zls::store` from the kept full-pitch references and its sized rows at
//! page 12 of the buffer (E1051), and stage zbits3's set-half rows through `zls::stencil_source`
//! (E1053), each dword or byte with nothing else changed.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::zls;

const ATTEMPT: &str = "render/closing-r15-zls/out/20261114-073826";
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

/// bit:K of t10: 0.75f where bit K of the dword index is set, else 0.25f
fn bit_fill(k: u32) -> impl Fn(u32) -> u32 {
    move |i| if i >> k & 1 == 1 { 0.75f32.to_bits() } else { 0.25f32.to_bits() }
}

fn same(name: &str, kept: &[u32], words: &std::collections::BTreeMap<u32, u32>, base: usize) {
    let hit = words.iter().filter(|&(&i, &v)| kept[base + i as usize] == v).count();
    assert_eq!(hit, words.len(), "{name}");
    let other = kept
        .iter()
        .enumerate()
        .filter(|&(i, &v)| v != FILL && (i < base || !words.contains_key(&((i - base) as u32))))
        .count();
    assert_eq!(other, 0, "{name}");
}

#[test]
fn zpass_every_load_pass_row_is_the_pass_model() {
    let Some(c) = ctx() else { return };
    let less = zls::Test::Less;
    for (name, word, w, h, k, z, test) in [
        ("zp-c-467", 0x0017_503eu32, 256u32, 128u32, 9u32, 0.5f32, less),
        ("zp-c-band", 0x0017_100c, 34, 18, 3, 0.5, less),
        ("zp-e-dp", 0x0017_500e, 34, 18, 3, 0.5, less),
        ("zp-19-nv", 0x001f_500e, 64, 32, 9, 0.5, zls::Test::Never),
        ("zp-19-ls", 0x001f_500e, 64, 32, 9, 0.5, less),
        ("zp-f1", 0x0117_500e, 64, 32, 9, 0.375, less),
        ("zp-f2", 0x0217_500e, 64, 32, 9, 0.375, less),
        ("zp-z0", 0x0017_500e, 64, 32, 9, 0.0, less),
        ("zp-z75", 0x0017_500e, 64, 32, 9, 0.75, less),
        ("zp-z1", 0x0017_500e, 64, 32, 9, 1.0, less),
    ] {
        let ctl = zls::Ctl::decode(word).unwrap();
        let p = zls::pass(&ctl, w, h, 1.0, z, test, &|_, _| true, &bit_fill(k), &|i| i).unwrap();
        same(name, &dump(&c, "zpass", name, "depth-store"), &p.depth, 0);
        assert_eq!(p.drawn, drawn(&c, "zpass", name), "{name}");
    }
    // zp-z125: the flat 0.125 plane stored 1 to 9 ulps below 0.125 (Q200's dyadic error); fed
    // those floats as the plane the pass reproduces the store and draws every pixel
    let st = dump(&c, "zpass", "zp-z125", "depth-store");
    let plane = |x: u32, y: u32| f32::from_bits(st[zls::store_dword(x, y, 1) as usize]);
    let ctl = zls::Ctl::decode(0x0017_500e).unwrap();
    let p = zls::pass_plane(&ctl, 64, 32, 1.0, &plane, less, &|_, _| true, &bit_fill(9), &|i| i).unwrap();
    same("zp-z125", &st, &p.depth, 0);
    assert_eq!((p.drawn, drawn(&c, "zpass", "zp-z125")), (2048, 2048));
    assert!(st[..2048].iter().all(|&v| (0x3dff_fff7..=0x3dff_ffff).contains(&v)));
}

#[test]
fn zovl_overlapping_integer_and_sized_stores_are_the_store_model() {
    let Some(c) = ctx() else { return };
    let r10x = "render/closing-r10-x/out/20261113-101116/zov";
    let r14z = "render/closing-r14-zls/out/20261114-054846/zodd";
    for (name, word, w, h, reference, g_full) in [
        ("zv-ov-64-f2", 0x0217_1004u32, 64u32, 32u32, format!("{r10x}/zov-64x32-ctl"), 1u32),
        ("zv-ov-160-f2", 0x0217_1014, 160, 48, format!("{r10x}/zov-160x48-ctl"), 4),
        ("zv-ov-65-f1", 0x0117_100c, 65, 33, format!("{r14z}/zo-65-f0"), 2),
        ("zv-ov-640-f1", 0x0117_1014, 640, 480, format!("{r14z}/zo-640-f0"), 19),
    ] {
        let full = dwords(&gz(&c, &format!("{reference}.depth.1.bin.gz")));
        let depth = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, g_full) as usize]);
        let s = zls::store(&zls::Ctl::decode(word).unwrap(), w, h, false, &depth).unwrap();
        same(name, &dump(&c, "zovl", name, "depth"), &s.words, 0);
    }
    for (name, word, z) in [
        ("zv-c-075", 0x0117_100cu32, 0.75f32),
        ("zv-r-hi", 0x0017_100c, 1.25),
        ("zv-i125-f1", 0x0117_100c, 1.25),
        ("zv-i125-f2", 0x0217_100c, 1.25),
        ("zv-im25-f1", 0x0117_100c, -0.25),
        ("zv-im25-f2", 0x0217_100c, -0.25),
    ] {
        let s = zls::store(&zls::Ctl::decode(word).unwrap(), 64, 32, false, &|_, _| z).unwrap();
        same(name, &dump(&c, "zovl", name, "depth"), &s.words, 0);
    }
    // E411's arrangement: the store base at page 12 of the depth buffer, buffers sized
    for (name, word) in [
        ("zv-c-g3", 0x0017_101cu32),
        ("zv-b25", 0x0217_100c),
        ("zv-g5", 0x0017_102c),
        ("zv-g9", 0x0017_104c),
        ("zv-g17", 0x0017_108c),
    ] {
        let s = zls::store(&zls::Ctl::decode(word).unwrap(), 64, 64, false, &|_, _| 0.5).unwrap();
        same(name, &dump(&c, "zovl", name, "depth"), &s.words, 12 * 1024);
    }
}

#[test]
fn zbits3_every_set_half_row_reads_as_the_stencil_source_says() {
    let Some(c) = ctx() else { return };
    let bytes = |i: u32| (i & 0xff) as u8;
    let index = |i: u32| ((i / 4) >> (8 * (i % 4))) as u8;
    for (name, word, w, reference, fill) in [
        ("zb3-b15-96", 0x0017_b016u32, 96u32, 0u8, &bytes as &dyn Fn(u32) -> u8),
        ("zb3-b15-r1", 0x0017_b00e, 64, 1, &bytes),
        ("zb3-b23-96", 0x0097_3016, 96, 0, &bytes),
        ("zb3-b23-idx", 0x0097_300e, 64, 0, &index),
        ("zb3-p21-23", 0x00b7_300e, 64, 0, &bytes),
        ("zb3-p22-23", 0x00d7_300e, 64, 0, &bytes),
    ] {
        let ctl = zls::Ctl { word };
        let src = zls::stencil_source(&ctl).unwrap();
        let st = gz(&c, &format!("{ATTEMPT}/zbits3/{name}.stencil-store.1.bin.gz"));
        let mut n = 0;
        for y in 0..32 {
            for x in 0..w {
                let p = zls::stencil_byte(x, y, ctl.g());
                let loaded = fill(p);
                let (read, can) = match src {
                    zls::StencilSource::Loaded => (loaded, true),
                    zls::StencilSource::Zero => (0, true),
                    zls::StencilSource::Fail => (loaded, false),
                    zls::StencilSource::Column => (zls::column_byte(x), true),
                };
                // ISP word 2 0x040501ff: EQUAL against the reference, mask 0x01, invert on pass
                let pass = can && read & 1 == reference;
                n += u64::from(pass);
                assert_eq!(st[p as usize], if pass { !read } else { read }, "{name} ({x}, {y})");
            }
        }
        assert_eq!(n, drawn(&c, "zbits3", name), "{name}");
    }
}
