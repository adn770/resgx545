// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r14-zls's kept rows (`render/closing-r14-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured: stage
//! zgran's five granule rows through `zls::load_base` (E1040: the store dword k holds the depth
//! buffer's dword k + d, the `index` fill naming each address), stage zodd's integer rows at 63 x
//! 31 and 65 x 33 and its overlapping rows at 65 x 33 G 1 and 640 x 480 G 2 equal to `zls::store`
//! fed the floats of the same size's full-pitch format-0 row (E1041), dword for dword with nothing
//! else changed.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::zls;

const ATTEMPT: &str = "render/closing-r14-zls/out/20261114-054846";

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(ATTEMPT).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATTEMPT} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {ATTEMPT} (set RESGX545_DATA)");
    None
}

fn dump(c: &Ctx, stage: &str, name: &str, suffix: &str) -> Vec<u32> {
    dwords(&c.read_gz(&format!("{ATTEMPT}/{stage}/{name}.{suffix}.1.bin.gz"), "").unwrap())
}

#[test]
fn zgran_every_granule_row_loads_from_the_16_byte_base() {
    let Some(c) = ctx() else { return };
    for (name, m) in
        [("zg-m8", 0x8u32), ("zg-m10", 0x10), ("zg-m20", 0x20), ("zg-m1008", 0x1008), ("zg-m1020", 0x1020)]
    {
        let st = dump(&c, "zgran", name, "depth-store");
        let d = (zls::load_base(0x1000 + m) - 0x1000) as usize;
        assert!((0..2048).all(|k| st[k] as usize == k + d / 4), "{name}");
        assert!(st[2048..].iter().all(|&v| v == 0x3e80_0000), "{name}");
    }
}

fn replay(c: &Ctx, name: &str, word: u32, w: u32, h: u32, reference: &str, g_full: u32) {
    let full = dump(c, "zodd", reference, "depth");
    let depth = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, g_full) as usize]);
    let ctl = zls::Ctl::decode(word).unwrap();
    let s = zls::store(&ctl, w, h, false, &depth).unwrap();
    let kept = dump(c, "zodd", name, "depth");
    let same = s.words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
    assert_eq!((same, s.words.len()), (s.words.len(), s.words.len()), "{name}");
    let other =
        kept.iter().enumerate().filter(|&(i, &v)| v != 0xdead_beef && !s.words.contains_key(&(i as u32)));
    assert_eq!(other.count(), 0, "{name}");
}

#[test]
fn zodd_integer_rows_at_odd_sizes_are_the_floor_rule_past_the_target() {
    let Some(c) = ctx() else { return };
    replay(&c, "zo-63-f1", 0x0117_100c, 63, 31, "zo-63-f0", 1);
    replay(&c, "zo-63-f2", 0x0217_100c, 63, 31, "zo-63-f0", 1);
    replay(&c, "zo-65-f1", 0x0117_1014, 65, 33, "zo-65-f0", 2);
    replay(&c, "zo-65-f2", 0x0217_1014, 65, 33, "zo-65-f0", 2);
}

#[test]
fn zodd_overlapping_rows_hold_the_tile_visited_last() {
    let Some(c) = ctx() else { return };
    replay(&c, "zo-65-ov", 0x0017_100c, 65, 33, "zo-65-f0", 2);
    replay(&c, "zo-640-ov", 0x0017_1014, 640, 480, "zo-640-f0", 19);
}
