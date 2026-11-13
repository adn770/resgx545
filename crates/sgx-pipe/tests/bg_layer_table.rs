// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The closing pass's r9-k1 rows (render/closing-r9-k1, E970 to E974: Q190's one-layer background
//! object in a 64 x 64 render) replayed with `bglayer.rs`: for every layered tri job of the
//! attempt, the object's 23 words as the kept render_param dump holds them after the job (at
//! 0x463000, E590's place) and the copy's texture over the tool's 64 x 64 source at 0x3e800000
//! (texel (x, y) = check byte, y, x) give each background pixel's texel; every pixel that is not
//! the triangle's colour is compared, except where 64 u or 64 v lies within 1/64 of a texel edge
//! (the f32 iteration's side is not recorded there). A row the model refuses (E973's changed
//! words, Q066) is counted refused, never a pass. The vectors tables of `vectors/closing/r9-k1/
//! pixels/` name `the_layer_model_replays_every_modelled_row_of_r9_k1` once every modelled row
//! matched; their layerless controls (c-off, c-off2) are E590's image, held by its hash, not by
//! this model. The r10-geo bgw rows (render/closing-r10-geo, E1006: finite values in words 9 and
//! 11 to 14) replay the same way, the tables of `vectors/closing/r10-geo/pixels/bgw` naming
//! `the_layer_model_replays_every_modelled_row_of_r10_geo`. Skips without the data, and fails with
//! `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::bglayer;
use sgx_pipe::data::Ctx;
use sgx_pipe::gz::gunzip;

const SESSION: &str = "render/closing-r9-k1/out/20261113-083450";
const STAGES: &[&str] = &["s0t", "s1", "s2", "s3", "s4"];
const R10: &str = "render/closing-r10-geo/out/20261113-103256";
const OBJ: usize = 0x46_3000;
const TRI: u32 = 0xff00_ff00;
const STATE: [u32; 4] =
    [(63 & 7) << 9 | (63 >> 3) << 17, 0xcc00_0000 | 63 << 12 | 63, 0x3e80_0000, 0xa080_0000];

fn texel(x: u32, y: u32) -> u32 {
    ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x
}

fn near_edge(t: f32) -> bool {
    let t = t as f64 * 64.0;
    (t - t.round()).abs() < 1.0 / 64.0
}

/// (matched rows, refused rows, mismatches as text, pixels compared)
fn replay(root: &std::path::Path, session: &str, stages: &[&str]) -> (usize, Vec<String>, Vec<String>, u64) {
    let (mut matched, mut refused, mut bad, mut pixels) = (0, vec![], vec![], 0u64);
    for st in stages {
        let dir = root.join(session).join(st);
        let cases = std::fs::read_to_string(dir.join("cases.tsv")).unwrap();
        for line in cases.lines().skip(1) {
            let f: Vec<&str> = line.split('\t').collect();
            let (name, args) = (f[0], f[6]);
            if !args.contains("--bg-layer") {
                continue;
            }
            let param =
                gunzip(&std::fs::read(dir.join(format!("{name}.tri.param.bin.gz"))).unwrap()).unwrap();
            let bg: Vec<u32> = (0..23)
                .map(|i| u32::from_le_bytes(param[OBJ + 4 * i..OBJ + 4 * i + 4].try_into().unwrap()))
                .collect();
            let out = String::from_utf8(
                gunzip(&std::fs::read(dir.join(format!("{name}.txt.gz"))).unwrap()).unwrap(),
            )
            .unwrap();
            if let Err(e) = bglayer::check(&bg) {
                refused.push(format!("{st} {name}: {e:?}"));
                continue;
            }
            let mut miss = 0;
            for l in out.lines().filter(|l| l.starts_with("row ")) {
                let (y, rest) = l[4..].split_once(": ").unwrap();
                let y: u32 = y.parse().unwrap();
                for (x, w) in rest.split_whitespace().enumerate() {
                    let (x, got) = (x as u32, u32::from_str_radix(w.trim_start_matches("0x"), 16).unwrap());
                    if got == TRI {
                        continue;
                    }
                    let (u, v) = bglayer::coords(&bg, x, y).unwrap();
                    if near_edge(u) || near_edge(v) {
                        continue;
                    }
                    let mut load = |a: u32| {
                        let i = (a - 0x3e80_0000) / 4;
                        Ok(texel(i % 64, i / 64))
                    };
                    pixels += 1;
                    if bglayer::sample(&bg, STATE, x, y, &mut load) != Ok(got) {
                        miss += 1;
                    }
                }
            }
            if miss == 0 {
                matched += 1;
            } else {
                bad.push(format!("{st} {name}: {miss} pixels differ"));
            }
        }
    }
    (matched, refused, bad, pixels)
}

#[test]
fn the_layer_model_replays_every_modelled_row_of_r9_k1() {
    let ctx = Ctx::from_env();
    let Some(root) = ctx.root.as_ref().filter(|r| r.join(SESSION).is_dir()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {SESSION}");
        eprintln!("SKIPPED: no {SESSION}");
        return;
    };
    let (matched, refused, bad, pixels) = replay(root, SESSION, STAGES);
    assert!(bad.is_empty(), "{bad:#?}");
    // c-tex, c-noop, c-tex2, s1's 44, s2's 20 and s3's 16 unchanged rows; E973's five refused
    assert_eq!(matched, 83, "refused: {refused:#?}");
    assert_eq!(refused.len(), 5, "{refused:#?}");
    assert!(refused.iter().all(|r| r.contains("Q066")));
    assert!(pixels > 200_000, "{pixels} pixels compared");
}

#[test]
fn the_layer_model_replays_every_modelled_row_of_r10_geo() {
    let ctx = Ctx::from_env();
    let Some(root) = ctx.root.as_ref().filter(|r| r.join(R10).is_dir()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {R10}");
        eprintln!("SKIPPED: no {R10}");
        return;
    };
    let (matched, refused, bad, pixels) = replay(root, R10, &["bgw"]);
    assert!(bad.is_empty(), "{bad:#?}");
    // the two controls and the 16 poked rows (E1006: H-INERT 16 of 16)
    assert_eq!(matched, 18, "refused: {refused:#?}");
    assert!(refused.is_empty(), "{refused:#?}");
    assert!(pixels > 50_000, "{pixels} pixels compared");
}
