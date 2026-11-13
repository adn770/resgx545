// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r10-zls's kept rows (`render/closing-r10-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the model they measured: stage
//! zst2 (E986), every format-3 and format-4 store equal to `zls::store_packed` fed the row's
//! format-0 reference floats and its own loaded stencil, dword for dword, and nothing else of the
//! buffer changed from the fill; no stencil store written; formats 5 to 7 refused (Q120).

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::zls;

const ATTEMPT: &str = "render/closing-r10-zls/out/20261113-102039";
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

fn bin(c: &Ctx, name: &str, buf: &str) -> Vec<u8> {
    c.read_gz(&format!("{ATTEMPT}/zst2/{name}.{buf}.1.bin.gz"), "").unwrap()
}

/// The row's size and control as tables/zst2.txt runs it: G = tiles across - 1, the stencil
/// loaded (bits 1 and 13) and stored (bit 17), the format in bits 26:24.
fn row(name: &str) -> (u32, u32, zls::Ctl) {
    let (w, h) = if name.starts_with("z2e") { (40, 20) } else { (64, 32) };
    let fmt: u32 = name.split('-').nth(1).unwrap()[1..].parse().unwrap();
    (w, h, zls::Ctl::decode(0x0017_3006 | (w.div_ceil(32) - 1) << 3 | fmt << 24).unwrap())
}

/// The format-3 and format-4 rows E986 held out byte for byte, and z2x-f4 (E978's replicate).
const PACKED: &[&str] = &[
    "z2x-f4",
    "z2x-f3-s00",
    "z2x-f4-s00",
    "z2x-f3-sff",
    "z2x-f4-sff",
    "z2x-f3-sa5",
    "z2x-f4-sa5",
    "z2y-f3",
    "z2y-f4",
    "z2d-f3",
    "z2d-f4",
    "z2e-f3",
];

#[test]
fn zst2_formats_3_and_4_store_e985s_layouts_dword_for_dword() {
    let Some(c) = ctx() else { return };
    for &name in PACKED {
        let (w, h, ctl) = row(name);
        let g = ctl.g();
        assert_eq!(ctl.word & !(7 << 24), 0x0017_300e, "{name}: tables/zst2.txt's control");
        let reference = dwords(&bin(&c, &format!("{}-f0", &name[..3]), "depth"));
        let depth = |x: u32, y: u32| f32::from_bits(reference[zls::store_dword(x, y, g) as usize]);
        let loaded = bin(&c, name, "stencil");
        let stencil = |x: u32, y: u32| loaded[zls::stencil_byte(x, y, g) as usize];
        let s = zls::store_packed(&ctl, w, h, &depth, &stencil).unwrap();
        let kept = dwords(&bin(&c, name, "depth"));
        let want = if ctl.format_code() == 3 { 640 } else { 160 } * w.div_ceil(32) * h.div_ceil(16);
        assert_eq!(s.words.len() as u32, want, "{name}");
        let same = s.words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
        assert_eq!(same, s.words.len(), "{name}");
        let other =
            kept.iter().enumerate().filter(|&(i, &v)| v != FILL && !s.words.contains_key(&(i as u32)));
        assert_eq!(other.count(), 0, "{name}");
        // the stencil store is not written (E978, E986: 21 of 21)
        let (d, st) = zls::dword_sets(&ctl, w, h, true).unwrap();
        assert_eq!((d.len(), st.len()), (s.words.len(), 0), "{name}");
        assert!(dwords(&bin(&c, name, "stencil-store")).iter().all(|&v| v == FILL), "{name}");
    }
}

#[test]
fn zst2_a_changed_byte_is_a_mismatch() {
    let Some(c) = ctx() else { return };
    // the control that can fail: the stencil bytes of another fill do not reproduce the row
    let (w, h, ctl) = row("z2x-f3-sa5");
    let reference = dwords(&bin(&c, "z2x-f0", "depth"));
    let depth = |x: u32, y: u32| f32::from_bits(reference[zls::store_dword(x, y, 1) as usize]);
    let s = zls::store_packed(&ctl, w, h, &depth, &|_, _| 0x5a).unwrap();
    let kept = dwords(&bin(&c, "z2x-f3-sa5", "depth"));
    assert!(s.words.iter().any(|(&i, &v)| kept[i as usize] != v));
}

#[test]
fn zst2_formats_5_to_7_refuse_by_q120() {
    let Some(_c) = ctx() else { return };
    for name in ["z2y-f5", "z2y-f6", "z2y-f7", "z2d-f5", "z2d-f6", "z2d-f7", "z2e-f6"] {
        let (w, h, ctl) = row(name);
        match zls::store_packed(&ctl, w, h, &|_, _| 0.5, &|_, _| 0) {
            Err(sgx_pipe::Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q120"], "{name}"),
            o => panic!("{name}: {o:?}"),
        }
    }
}
