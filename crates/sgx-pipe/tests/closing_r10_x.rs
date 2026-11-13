// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! r10-x's kept rows (`render/closing-r10-x` in `$RESGX545_DATA`; the tests skip, saying so,
//! without it and fail with `RESGX545_REQUIRE_DATA`), replayed on the models they measured:
//! stage zov (E996), every overlapping store equal to `zls::store` fed the full-pitch control's
//! floats, dword for dword; stage win0 (E1010), every decodable pixel of the mode-0 identity maps
//! at `isp::msaa_source`'s source and the rest the background; stage dcmp (E995), the drawn counts
//! of its less rows over a loaded depth equal to `zls::pass`'s.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::{isp, zls};

const ATTEMPT: &str = "render/closing-r10-x/out/20261113-101116";
const BACKGROUND: u32 = 0xff20_3040;

fn ctx() -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(ATTEMPT).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {ATTEMPT} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {ATTEMPT} (set RESGX545_DATA)");
    None
}

fn text(c: &Ctx, stage: &str, name: &str) -> String {
    String::from_utf8(c.read_gz(&format!("{ATTEMPT}/{stage}/{name}.txt.gz"), "").unwrap()).unwrap()
}

fn dump(c: &Ctx, stage: &str, name: &str) -> Vec<u32> {
    dwords(&c.read_gz(&format!("{ATTEMPT}/{stage}/{name}.depth.1.bin.gz"), "").unwrap())
}

#[test]
fn zov_every_overlapping_store_is_the_models() {
    let Some(c) = ctx() else { return };
    let rows = [
        (64u32, 32u32, 0u32, 0u32),
        (128, 32, 1, 0),
        (96, 48, 1, 0),
        (160, 48, 2, 0),
        (256, 64, 3, 0),
        (64, 32, 0, 1),
    ];
    for (w, h, g, fmt) in rows {
        let full = dump(&c, "zov", &format!("zov-{w}x{h}-ctl"));
        let gfull = w.div_ceil(32) - 1;
        let depth = |x: u32, y: u32| f32::from_bits(full[zls::store_dword(x, y, gfull) as usize]);
        let name = format!("zov-{w}x{h}-g{g}{}", if fmt == 1 { "-f1" } else { "" });
        let kept = dump(&c, "zov", &name);
        let ctl = zls::Ctl::decode(0x0017_1004 | g << 3 | fmt << 24).unwrap();
        let s = zls::store(&ctl, w, h, false, &depth).unwrap();
        let same = s.words.iter().filter(|&(&i, &v)| kept[i as usize] == v).count();
        assert_eq!(same, s.words.len(), "{name}");
        // and nothing else of the buffer changed from the fill
        let other =
            kept.iter().enumerate().filter(|&(i, &v)| v != 0xdead_beef && !s.words.contains_key(&(i as u32)));
        assert_eq!(other.count(), 0, "{name}");
    }
}

#[test]
fn win0_mode_0_stores_each_pixels_own_position_under_every_window() {
    let Some(c) = ctx() else { return };
    // (size, TE, background pixels E1010 counted: the region model's holes)
    for ((w, h), te, holes) in [
        ((64u32, 64u32), 0x6000_0000u32, 0u64),
        ((64, 64), 0xa000_0000, 0),
        ((64, 64), 0xe000_0000, 136),
        ((128, 96), 0x6000_0000, 26),
        ((128, 96), 0xa000_0000, 74),
        ((128, 96), 0xe000_0000, 514),
    ] {
        let n = |ax: &str| format!("w0-te{:02x}-{w}x{h}-{ax}", te >> 24);
        let (x, y) =
            (isp::parse_rows(&text(&c, "win0", &n("x"))), isp::parse_rows(&text(&c, "win0", &n("y"))));
        let k = isp::check_windows(0, te, &x, &y).unwrap();
        assert_eq!((k.stored, k.wrong), ((w * h) as u64, 0), "{}", n("x"));
        assert_eq!(k.stored - k.decodable, holes, "{}", n("x"));
        assert_eq!(x.iter().filter(|p| p.2 == BACKGROUND).count() as u64, holes, "{}", n("x"));
    }
}

#[test]
fn dcmp_the_less_rows_drawn_counts_are_the_passs() {
    let Some(c) = ctx() else { return };
    // E995's less rows at t = 0.5 (the pass models less and never): the loaded fill and the count
    for (name, fill) in [
        ("z243-ctl", 0x3f40_0000u32),
        ("eq-m1", 0x3f00_0000),
        ("neg25-m1", 0xbe80_0000),
        ("neg75-m1", 0xbf40_0000),
        ("eq-m0", 0x3f00_0000),
    ] {
        let t = text(&c, "dcmp", name);
        let drawn: u64 = t
            .lines()
            .find_map(|l| l.strip_prefix("tri 64x32 #1: ").and_then(|r| r.split(' ').next()?.parse().ok()))
            .unwrap();
        let test = if name == "eq-m0" { zls::Test::Never } else { zls::Test::Less };
        let ctl = zls::Ctl::decode(0x0017_500e).unwrap();
        match zls::pass(&ctl, 64, 32, 1.0, 0.5, test, &|_, _| true, &|_| fill, &|_| 0) {
            Ok(p) => assert_eq!(p.drawn, drawn, "{name}"),
            // a loaded 0.5 against the triangle's 0.5 is inside the planes' tolerance (Q200)
            Err(sgx_pipe::Outcome::Unsupported { ids, .. }) => {
                assert_eq!((name, ids), ("eq-m1", vec!["Q200".to_string()]))
            }
            Err(o) => panic!("{name}: {o:?}"),
        }
    }
}
