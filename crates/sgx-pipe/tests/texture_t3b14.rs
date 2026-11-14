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
//! floor(4096 frac(u)) in 16 x 16 tiles with a tile row of W + 4096 texels. Bit 14 on another
//! twiddled size, filtered or with T3's offset stays refused.

use sgx_pipe::data::Ctx;
use sgx_sim::tex::{self, Lod, Sample, Srd};
use std::path::{Path, PathBuf};

const R10: &str = "render/closing-r10-tex";
const R10_ATT: &str = "out/20261113-102730/t3b";
const R9: &str = "render/closing-r9-x";
const R9_ATT: &str = "out/20261113-081821/t3";
const R14: &str = "render/closing-r14-flag";
const R14_ATT: &str = "out/20261114-060824/f1";
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
