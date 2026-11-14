// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r13-zls's kept rows (`render/closing-r13-zls` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured (E1030):
//! stage zbits, every ramp row's depth dump equal to `zls::store` of its control fed the tiled
//! control's floats (linear exactly when bit 16 is clear), dword for dword with nothing else
//! changed; every stencil row's drawn count as `zls::stencil_source` says (the loaded byte: E988's
//! 1024; 0: all 2048), the rows with bit 12 cleared refused (Q071).

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::{Outcome, zls};

const ATTEMPT: &str = "render/closing-r13-zls/out/20261113-213117";

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(ATTEMPT).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATTEMPT} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {ATTEMPT} (set RESGX545_DATA)");
    None
}

fn text(c: &Ctx, name: &str) -> String {
    String::from_utf8(c.read_gz(&format!("{ATTEMPT}/zbits/{name}.txt.gz"), "").unwrap()).unwrap()
}

fn dump(c: &Ctx, name: &str) -> Vec<u32> {
    dwords(&c.read_gz(&format!("{ATTEMPT}/zbits/{name}.depth.1.bin.gz"), "").unwrap())
}

fn drawn(t: &str) -> u64 {
    t.lines()
        .find_map(|l| l.strip_prefix("tri 64x32 #1: ").and_then(|r| r.split(' ').next()?.parse().ok()))
        .unwrap()
}

#[test]
fn zbits_every_ramp_store_is_the_models() {
    let Some(c) = ctx() else { return };
    let full = dump(&c, "zbr-ctl");
    let depth = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, 2) as usize]);
    for (name, word) in [
        ("zbr-ctl", 0x0017_1014u32),
        ("zbr-c12", 0x0017_0014),
        ("zbr-c16", 0x0016_1014),
        ("zbr-c20", 0x0007_1014),
        ("zbr-c12-16", 0x0016_0014),
        ("zbr-c12-20", 0x0007_0014),
        ("zbr-c16-20", 0x0006_1014),
    ] {
        let ctl = zls::Ctl::decode(word).unwrap();
        let s = zls::store(&ctl, 80, 40, false, &depth).unwrap();
        let kept = dump(&c, name);
        let same = s.words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
        assert_eq!((same, s.words.len()), (4608, 4608), "{name}");
        let other =
            kept.iter().enumerate().filter(|&(i, &v)| v != 0xdead_beef && !s.words.contains_key(&(i as u32)));
        assert_eq!(other.count(), 0, "{name}");
        assert_eq!(ctl.linear_store(), word & 1 << 16 == 0, "{name}");
    }
}

#[test]
fn zbits_every_stencil_rows_count_is_its_sources() {
    let Some(c) = ctx() else { return };
    for (name, word) in [
        ("zbs-base", 0x0017_300eu32),
        ("zbs-q071", 0xf8e6_a00e),
        ("zbs-c12", 0x0017_200e),
        ("zbs-c16", 0x0016_300e),
        ("zbs-c20", 0x0007_300e),
        ("zbs-c12-16", 0x0016_200e),
        ("zbs-c12-20", 0x0007_200e),
        ("zbs-c16-20", 0x0006_300e),
        ("zbs-set", 0xf8f7_b00e),
    ] {
        let t = text(&c, name);
        assert!(t.contains(&format!("control {word:#010x}")), "{name}");
        match zls::stencil_source(&zls::Ctl { word }) {
            Ok(zls::StencilSource::Loaded) => assert_eq!(drawn(&t), 1024, "{name}"),
            Ok(zls::StencilSource::Zero) => assert_eq!(drawn(&t), 2048, "{name}"),
            Ok(s) => panic!("{name}: {s:?}, no row of r13-zls set bit 15 or 23 alone"),
            Err(Outcome::Unsupported { ids, .. }) => {
                assert!(word & 1 << 12 == 0 && ids == ["Q071"], "{name}");
                assert_eq!(drawn(&t), 1024, "{name}: refused, counted apart");
            }
            Err(o) => panic!("{name}: {o:?}"),
        }
    }
}
