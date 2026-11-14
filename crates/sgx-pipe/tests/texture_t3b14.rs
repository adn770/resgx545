// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! `sgx-sim`'s texture unit under T3 bit 14 on a stride texture against the kept probe fills of
//! r10-tex's stage t3b (`render/closing-r10-tex`, E1003: six held-out geometries, each with its
//! bit-clear reference, E566's two controls and E975's b14-u01 replicated) and of r9-x's stage t3
//! (`render/closing-r9-x`, E975's six rows, where R-4096TX was formed post hoc) in `$RESGX545_DATA`
//! (the tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`). Each job's state
//! words and coordinates are its own program's (`bins/NAME.s`: the four `mov r20..r23` words and
//! the fmad K and C of u and v); the scratch dword i is 0xD0000000 | i; the first register the
//! sample writes must equal the kept o0 on every one of the 2048 pixels. And r14-flag's stage f1
//! (`render/closing-r14-flag`, E1047: bit 14 on E566's twiddled 32 x 32 texture with a 1 MiB
//! scratch, where E566 and E1033 faulted at 16 pages): its state words and coordinates are
//! gen/f1.py's (E566's tw32 map, u = x / 4096, u = 0), every pixel the read of column s +
//! floor(4096 frac(u)) in 16 x 16 tiles with a tile row of W + 4096 texels. And r15-tw's stage
//! tw14 (`render/closing-r15-tw`, E1049: the same rule held out at W 16, 64 and 128 by 32 with u
//! past 1 and 2, and on a u16 32 x 32 in texels): its state words and coordinates are gen/tw.py's
//! (u a ramp of x, v = (y + 1/2) / 32), every point row and reference read as kept; its two
//! bilinear rows (post hoc footprint) are refused on every pixel. And r16-tw's stage tw16
//! (`render/closing-r16-tw`, E1058: the rule held out at 32 and 128 by 8 and 16, 16 and 64 by 64,
//! E561's tile height): its state words and coordinates are gen/tw16.py's (u and v ramps of x
//! and y), every point row and both bit-clear references read as kept; its six bilinear rows and
//! E1049's tw-bl32 rerun are refused on every pixel (E1049's post hoc footprint failed 3 of 6).
//! Bit 14 at other sizes, filtered or with T3's offset stays refused.

use sgx_pipe::data::Ctx;
use sgx_sim::tex::{self, Lod, Sample, Srd};
use std::path::{Path, PathBuf};

const R10: &str = "render/closing-r10-tex";
const R10_ATT: &str = "out/20261113-102730/t3b";
const R9: &str = "render/closing-r9-x";
const R9_ATT: &str = "out/20261113-081821/t3";
const R14: &str = "render/closing-r14-flag";
const R14_ATT: &str = "out/20261114-060824/f1";
const R15: &str = "render/closing-r15-tw";
const R15_ATT: &str = "out/20261114-074356/tw14";
const R16: &str = "render/closing-r16-tw";
const R16_ATT: &str = "out/20261114-093404/tw16";
const SCRATCH: u32 = 0x5caf_0000;

fn base() -> Option<PathBuf> {
    let b = Ctx::from_env()
        .root
        .filter(|r| r.join(R10).join(R10_ATT).is_dir() && r.join(R9).join(R9_ATT).is_dir());
    if b.is_none() {
        assert!(
            std::env::var_os("RESGX545_REQUIRE_DATA").is_none(),
            "no r10-tex or r9-x t3 jobs (RESGX545_DATA)"
        );
        eprintln!("SKIPPED: no {R10}/{R10_ATT} or {R9}/{R9_ATT} (set RESGX545_DATA)");
    }
    b
}

/// A program's state words and its u and v rules: (axis is x, K, C) of each fmad, in order.
struct Prog {
    state: [u32; 4],
    uv: [(bool, f32, f32); 2],
}

fn imm(line: &str) -> u32 {
    let h = line.rsplit("#0x").next().unwrap();
    u32::from_str_radix(h.trim(), 16).unwrap()
}

fn program(text: &str) -> Prog {
    let (mut state, mut uv, mut axis, mut k) = ([0u32; 4], Vec::new(), true, 0u32);
    for l in text.lines().map(str::trim) {
        if l.starts_with("and.skipinv r1, pa0") {
            axis = true;
        } else if l.starts_with("shr.skipinv r1, pa0") {
            axis = false;
        } else if l.starts_with("mov.skipinv r2, #") {
            k = imm(l);
        } else if l.starts_with("mov.skipinv r3, #") {
            uv.push((axis, f32::from_bits(k), f32::from_bits(imm(l))));
        } else if let Some(r) = l.strip_prefix("mov r2") {
            let i = r[..1].parse::<usize>().unwrap();
            state[i] = imm(l);
        }
    }
    assert_eq!(uv.len(), 2, "two coordinates");
    Prog { state, uv: [uv[0], uv[1]] }
}

fn coord((ax, k, c): (bool, f32, f32), x: u32, y: u32) -> f32 {
    let r = if ax { 1.0 + x as f32 / 64.0 } else { 1.0 + y as f32 / 32.0 };
    r.mul_add(k, c)
}

/// The 64 x 32 o0 values of a probe's kept output ("probe NAME: row N: ...").
fn image(path: &Path) -> Vec<u32> {
    let raw = std::fs::read(path).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
    let text = String::from_utf8(sgx_pipe::gz::gunzip(&raw).unwrap()).unwrap();
    let mut img = vec![None; 64 * 32];
    for line in text.lines() {
        let Some(at) = line.find(": row ") else { continue };
        let rest = &line[at + 6..];
        let (y, vals) = rest.split_once(": ").unwrap();
        let y: usize = y.parse().unwrap();
        for (x, v) in vals.split_whitespace().enumerate() {
            img[y * 64 + x] = Some(u32::from_str_radix(v, 16).unwrap());
        }
    }
    img.into_iter().map(|v| v.expect("2048 pixels")).collect()
}

fn sample(p: &Prog, x: u32, y: u32) -> Result<u32, String> {
    let s = Sample {
        state: p.state,
        u: coord(p.uv[0], x, y),
        v: coord(p.uv[1], x, y),
        one_d: false,
        srd: Srd::None,
        pcf: None,
        lod: Lod::Flat,
    };
    let mut load = |a: u32| Ok(0xd000_0000 | (a.wrapping_sub(SCRATCH) / 4));
    tex::sample(&s, &mut load).map(|v| v[0]).map_err(|e| format!("{e:?}"))
}

/// (pixels equal, pixels the model refused) of one job.
fn replay(b: &Path, session: &str, att: &str, name: &str) -> (u32, u32) {
    let text = std::fs::read_to_string(b.join(session).join("bins").join(format!("{name}.s"))).unwrap();
    let p = program(&text);
    let img = image(&b.join(session).join(att).join(format!("{name}.txt.gz")));
    let (mut ok, mut open) = (0, 0);
    for y in 0..32 {
        for x in 0..64 {
            match sample(&p, x, y) {
                Ok(v) if v == img[(y * 64 + x) as usize] => ok += 1,
                Ok(_) => {}
                Err(_) => open += 1,
            }
        }
    }
    (ok, open)
}

#[test]
fn r10_tex_t3b_reads_the_bit_clear_texel_plus_4096_u_texels() {
    let Some(b) = base() else { return };
    let names = [
        "t3b-ctl",
        "t3b-b14ref",
        "t3b-u01",
        "t3b-s256",
        "t3b-s256-ref",
        "t3b-s16h64",
        "t3b-s16h64-ref",
        "t3b-offgrid",
        "t3b-offgrid-ref",
        "t3b-clamp",
        "t3b-clamp-ref",
        "t3b-vramp",
        "t3b-vramp-ref",
        "t3b-f16",
        "t3b-f16-ref",
    ];
    for n in names {
        assert_eq!(replay(&b, R10, R10_ATT, n), (2048, 0), "{n}");
    }
}

#[test]
fn r9_x_t3_bit_14_rows_read_the_same_rule() {
    let Some(b) = base() else { return };
    for n in ["b14-w16s64", "b14-w32s128", "b14-w32s32", "b14-w48s64", "b14-u01", "b14-u02w16"] {
        assert_eq!(replay(&b, R9, R9_ATT, n), (2048, 0), "{n}");
        let r = format!("{n}-ref");
        assert_eq!(replay(&b, R9, R9_ATT, &r), (2048, 0), "{r}");
    }
}

/// (u, v) of an r14-flag f1 pixel: E566's tw32 map (`map` x and y over 32: 1 + (2q + 1) / 64) or
/// gen/f1.py's u = x / 4096 and u = 0 with v = (y + 1/2) / 32.
fn r14_uv(name: &str, x: u32, y: u32) -> (f32, f32) {
    let map = |q: u32| 1.0 + (2 * (q & 31) + 1) as f32 / 64.0;
    match name {
        "f1-ref-a" | "f1-tw32" => (map(x), map(y)),
        "f1-ref-b" | "f1-small" => (x as f32 / 4096.0, (2 * y + 1) as f32 / 64.0),
        _ => (0.0, (2 * y + 1) as f32 / 64.0),
    }
}

#[test]
fn r14_flag_f1_bit_14_twiddled_reads_a_tile_row_of_w_plus_4096_texels() {
    let Some(b) = Ctx::from_env().root.filter(|r| r.join(R14).join(R14_ATT).is_dir()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {R14}/{R14_ATT}");
        eprintln!("SKIPPED: no {R14}/{R14_ATT} (set RESGX545_DATA)");
        return;
    };
    for (name, t3) in [
        ("f1-ref-a", 0x0080_0800),
        ("f1-tw32", 0x0080_4800),
        ("f1-ref-b", 0x0080_0800),
        ("f1-small", 0x0080_4800),
        ("f1-zero", 0x0080_4800),
    ] {
        let img = image(&b.join(R14).join(R14_ATT).join(format!("{name}.txt.gz")));
        let mut ok = 0;
        for y in 0..32 {
            for x in 0..64 {
                let (u, v) = r14_uv(name, x, y);
                let s = Sample {
                    state: [0x07fe_0000, 0x0c01_f01f, SCRATCH, t3],
                    u,
                    v,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                };
                let mut load = |a: u32| Ok(0xd000_0000 | (a.wrapping_sub(SCRATCH) / 4));
                let got = tex::sample(&s, &mut load).map(|v| v[0]);
                assert!(got.is_ok(), "{name} ({x}, {y}): {got:?}");
                ok += u32::from(got.unwrap() == img[(y * 64 + x) as usize]);
            }
        }
        assert_eq!(ok, 2048, "{name}");
    }
}

/// An r15-tw tw14 row: (name, W, format, T0, T3 bit 14, u = a + (x + c) / d).
const TW14: [(&str, u32, u32, u32, bool, f64, f64, f64); 14] = [
    ("tw-ref16", 16, 12, 0x07fe_0000, false, 0.0, 0.5, 64.0),
    ("tw-refu16", 32, 9, 0x07fe_0000, false, 0.0, 0.5, 64.0),
    ("tw-ref64", 64, 12, 0x07fe_0000, false, 0.0, 0.5, 64.0),
    ("tw-ref128", 128, 12, 0x07fe_0000, false, 0.0, 0.5, 128.0),
    ("tw-zero", 32, 12, 0x07fe_0000, true, 0.0, 0.0, f64::INFINITY),
    ("tw-u16", 32, 9, 0x07fe_0000, true, 0.0, 0.5, 64.0),
    ("tw16-u0", 16, 12, 0x07fe_0000, true, 0.0, 0.5, 64.0),
    ("tw-bl16", 16, 12, 0x07fe_1400, true, 1.96875, 0.0, 1024.0),
    ("tw16-u1", 16, 12, 0x07fe_0000, true, 1.0, 0.5, 64.0),
    ("tw-bl32", 32, 12, 0x07fe_1400, true, 0.984375, 0.0, 2048.0),
    ("tw64-u0", 64, 12, 0x07fe_0000, true, 0.0, 0.5, 64.0),
    ("tw128-u0", 128, 12, 0x07fe_0000, true, 0.0, 0.5, 128.0),
    ("tw64-u2", 64, 12, 0x07fe_0000, true, 2.0, 0.5, 64.0),
    ("tw128-u2", 128, 12, 0x07fe_0000, true, 2.0, 0.5, 128.0),
];

#[test]
fn r15_tw_tw14_bit_14_twiddled_reads_a_tile_row_of_w_plus_4096_texels_at_every_width() {
    let Some(b) = Ctx::from_env().root.filter(|r| r.join(R15).join(R15_ATT).is_dir()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {R15}/{R15_ATT}");
        eprintln!("SKIPPED: no {R15}/{R15_ATT} (set RESGX545_DATA)");
        return;
    };
    for (name, w, fmt, t0, b14, a, c, d) in TW14 {
        let img = image(&b.join(R15).join(R15_ATT).join(format!("{name}.txt.gz")));
        let bilinear = t0 & 0x1400 != 0;
        let (mut ok, mut open) = (0, 0);
        for y in 0..32 {
            for x in 0..64 {
                // the bilinear rows sample W u - 1/2 on 1/64 texel steps: v = (y + 3/4) / 32
                let v = if bilinear { (4 * y + 3) as f64 / 128.0 } else { (2 * y + 1) as f64 / 64.0 };
                let s = Sample {
                    state: [t0, fmt << 24 | (w - 1) << 12 | 31, SCRATCH, 0x0080_0800 | u32::from(b14) << 14],
                    u: (a + (x as f64 + c) / d) as f32,
                    v: v as f32,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                };
                let mut load = |a: u32| Ok(0xd000_0000 | (a.wrapping_sub(SCRATCH) / 4));
                match tex::sample(&s, &mut load) {
                    Ok(v) if v[0] == img[(y * 64 + x) as usize] => ok += 1,
                    Ok(_) => {}
                    Err(_) => open += 1,
                }
            }
        }
        let want = if bilinear { (0, 2048) } else { (2048, 0) };
        assert_eq!((ok, open), want, "{name}");
    }
}

/// An r16-tw tw16 row: (name, W, H, bilinear, T3 bit 14, u = u0 + x du, v = v0 + y dv).
const TW16: [(&str, u32, u32, bool, bool, f64, f64, f64, f64); 17] = [
    ("ref32h8", 32, 8, false, false, 1.0 + 1.0 / 128.0, 1.0 / 64.0, 1.0 / 64.0, 1.0 / 32.0),
    ("ref16h64", 16, 64, false, false, 1.0 / 1024.0, 3.0 / 512.0, 0.5 + 1.0 / 128.0, 1.0 / 64.0),
    ("pt128h8", 128, 8, false, true, 1.0 / 256.0, 1.0 / 128.0, 1.0 / 64.0, 1.0 / 32.0),
    ("pt128h16", 128, 16, false, true, 2.0 + 1.0 / 256.0, 1.0 / 128.0, 1.0 / 64.0, 1.0 / 32.0),
    ("pt32h8", 32, 8, false, true, 1.0 + 1.0 / 128.0, 1.0 / 64.0, 1.0 / 64.0, 1.0 / 32.0),
    ("pt32h16", 32, 16, false, true, 1.0 / 128.0, 1.0 / 64.0, 1.0 / 64.0, 1.0 / 32.0),
    ("bl16h16in", 16, 16, true, true, 0.25, 1.0 / 256.0, 1.0 / 32.0, 1.0 / 32.0),
    ("bl64left", 64, 32, true, true, 2.0 + 1.0 / 4096.0, 1.0 / 4096.0, 3.0 / 128.0, 1.0 / 32.0),
    ("bl128h16right", 128, 16, true, true, 2.0 - 32.0 / 8192.0, 1.0 / 8192.0, 1.0 / 32.0, 1.0 / 32.0),
    ("bl128vedge", 128, 32, true, true, 0.25, 1.0 / 512.0, 63.0 / 64.0, 1.0 / 2048.0),
    ("bl64in", 64, 32, true, true, 0.25, 1.0 / 256.0, 3.0 / 128.0, 1.0 / 32.0),
    ("bl32r", 32, 32, true, true, 63.0 / 64.0, 1.0 / 2048.0, 3.0 / 128.0, 1.0 / 32.0),
    ("bl128right", 128, 32, true, true, 2.0 - 32.0 / 8192.0, 1.0 / 8192.0, 3.0 / 128.0, 1.0 / 32.0),
    ("pt16h64u0", 16, 64, false, true, 1.0 / 1024.0, 3.0 / 512.0, 0.5 + 1.0 / 128.0, 1.0 / 64.0),
    ("pt16h64u1", 16, 64, false, true, 1.0 + 1.0 / 1024.0, 3.0 / 512.0, 0.5 + 1.0 / 128.0, 1.0 / 64.0),
    ("pt64h64u0", 64, 64, false, true, 1.0 / 1024.0, 3.0 / 512.0, 0.5 + 1.0 / 128.0, 1.0 / 64.0),
    ("pt64h64u1", 64, 64, false, true, 1.0 + 1.0 / 1024.0, 3.0 / 512.0, 0.5 + 1.0 / 128.0, 1.0 / 64.0),
];

#[test]
fn r16_tw_tw16_bit_14_twiddled_keeps_e561s_tile_height_at_h_8_16_64() {
    let Some(b) = Ctx::from_env().root.filter(|r| r.join(R16).join(R16_ATT).is_dir()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {R16}/{R16_ATT}");
        eprintln!("SKIPPED: no {R16}/{R16_ATT} (set RESGX545_DATA)");
        return;
    };
    for (name, w, h, bilinear, b14, u0, du, v0, dv) in TW16 {
        let img = image(&b.join(R16).join(R16_ATT).join(format!("{name}.txt.gz")));
        let t0 = if bilinear { 0x07fe_1400 } else { 0x07fe_0000 };
        let (mut ok, mut open) = (0, 0);
        for y in 0..32 {
            for x in 0..64 {
                let s = Sample {
                    state: [
                        t0,
                        12 << 24 | (w - 1) << 12 | (h - 1),
                        SCRATCH,
                        0x0080_0800 | u32::from(b14) << 14,
                    ],
                    u: (u0 + x as f64 * du) as f32,
                    v: (v0 + y as f64 * dv) as f32,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                };
                let mut load = |a: u32| Ok(0xd000_0000 | (a.wrapping_sub(SCRATCH) / 4));
                match tex::sample(&s, &mut load) {
                    Ok(v) if v[0] == img[(y * 64 + x) as usize] => ok += 1,
                    Ok(_) => {}
                    Err(_) => open += 1,
                }
            }
        }
        let want = if bilinear { (0, 2048) } else { (2048, 0) };
        assert_eq!((ok, open), want, "{name}");
    }
}
