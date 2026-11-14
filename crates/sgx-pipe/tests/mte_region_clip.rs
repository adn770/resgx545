// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The r16-mte rclip table (`vectors/closing/r16-mte/pixels/rclip.table.json`, E1060: the MTE
//! state's region clip, presence bit 7, added to the probe triangle's block by `--blk-add 7=C0,C1`
//! at 64 x 64, 128 x 128, 256 x 256 and 100 x 60, 15 jobs) replayed with `mte::region_clip`: each
//! row's image is its object (`--tri-full`: every pixel; else the library's default triangle,
//! (8, 8), (56, 20), (20, 56) of 64 scaled to the target, covered by `isp::Tri::covers`, E606)
//! clipped by the row's words (`mte::clipped`), 0xff00ff00 where drawn and the background's
//! 0xff203040 elsewhere; its digest (the words `%08x` joined by spaces, one row a line) and its
//! value counts must be the row's. The table's `replay` names this test. Skips without the data,
//! and fails with `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::data::Ctx;
use sgx_pipe::isp::Tri;
use sgx_pipe::mte::{RegionClip, clipped, region_clip};
use sgx_pipe::sha256::hex_digest;
use sgx_sim::json::{Json, parse};

const TABLE: &str = "vectors/closing/r16-mte/pixels/rclip.table.json";
const NAME: &str = "r16_mte_rclip_the_region_clip_keeps_whole_tiles_on_every_pixel";
const GREEN: u32 = 0xff00_ff00;
const BG: u32 = 0xff20_3040;

fn load() -> Option<Json> {
    let ctx = Ctx::from_env();
    let Some(root) = ctx.root.as_ref().filter(|r| r.join(TABLE).is_file()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {TABLE}");
        eprintln!("SKIPPED: no {TABLE}");
        return None;
    };
    Some(parse(&std::fs::read_to_string(root.join(TABLE)).unwrap()))
}

fn opt<'a>(args: &'a [&'a str], name: &str) -> Option<&'a str> {
    args.iter().position(|a| *a == name).map(|i| args[i + 1])
}

/// The row's target, object and clip from its args.
fn job(args: &str) -> (u32, u32, bool, Option<RegionClip>) {
    let a: Vec<&str> = args.split_whitespace().collect();
    let w = opt(&a, "--width").unwrap().parse().unwrap();
    let h = opt(&a, "--height").unwrap().parse().unwrap();
    let clip = opt(&a, "--blk-add").map(|v| {
        let (bit, words) = v.split_once('=').unwrap();
        assert_eq!(bit, "7", "only the region clip");
        let (c0, c1) = words.split_once(',').unwrap();
        let hex = |s: &str| u32::from_str_radix(s.trim_start_matches("0x"), 16).unwrap();
        region_clip(hex(c0), hex(c1))
    });
    (w, h, a.contains(&"--tri-full"), clip)
}

/// The modelled image's words.
fn image(w: u32, h: u32, full: bool, clip: Option<RegionClip>) -> Vec<u32> {
    let covered: Vec<bool> = if full {
        vec![true; (w * h) as usize]
    } else {
        // render.c sgxfive_tri_default: v64 * W / 64 pixels, here in 1/256 pixel
        let s = |v: i64, n: u32| v * 256 * n as i64 / 64;
        let t = Tri { v: [(s(8, w), s(8, h)), (s(56, w), s(20, h)), (s(20, w), s(56, h))], z: [0.0; 3] };
        (0..h).flat_map(|y| (0..w).map(move |x| (x, y))).map(|(x, y)| t.covers(x, y)).collect()
    };
    let drawn = match clip {
        Some(c) => clipped(w, h, &covered, c),
        None => covered,
    };
    drawn.iter().map(|&d| if d { GREEN } else { BG }).collect()
}

fn digest(w: u32, img: &[u32]) -> String {
    let mut s = String::new();
    for row in img.chunks(w as usize) {
        s += &row.iter().map(|v| format!("{v:08x}")).collect::<Vec<_>>().join(" ");
        s.push('\n');
    }
    hex_digest(s.as_bytes())
}

#[test]
fn r16_mte_rclip_the_region_clip_keeps_whole_tiles_on_every_pixel() {
    let Some(t) = load() else { return };
    assert_eq!(
        t.get("replay").get("test").str(),
        Some(format!("crates/sgx-pipe/tests/mte_region_clip.rs::{NAME}").as_str())
    );
    let rows = t.get("rows").arr();
    assert_eq!(rows.len(), 15, "E1060's 15 jobs");
    let mut clipped_rows = 0;
    for r in rows {
        let id = r.get("id").str().unwrap();
        let (w, h, full, clip) = job(r.get("args").str().unwrap());
        let img = image(w, h, full, clip);
        let p = r.get("pixels");
        assert_eq!((p.get("width").num(), p.get("height").num()), (Some(w as f64), Some(h as f64)), "{id}");
        let green = img.iter().filter(|&&v| v == GREEN).count();
        let counts: Vec<(u64, f64)> = p
            .get("values")
            .arr()
            .iter()
            .map(|v| (v.arr()[0].hex().unwrap(), v.arr()[1].num().unwrap()))
            .collect();
        for (v, n) in &counts {
            let want = match *v as u32 {
                GREEN => green,
                BG => img.len() - green,
                other => panic!("{id}: a value {other:#x} no model writes"),
            };
            assert_eq!(*n as usize, want, "{id}: count of {v:#x}");
        }
        assert_eq!(p.get("sha256").str(), Some(digest(w, &img).as_str()), "{id}: the image");
        if clip.is_some_and(|c| c.enable) && green > 0 && green < img.len() {
            clipped_rows += 1;
        }
    }
    assert_eq!(clipped_rows, 10, "the ten partial rows of E1060");
}

#[test]
fn a_rival_form_of_the_clip_does_not_replay_the_table() {
    let Some(t) = load() else { return };
    // the rows counted from the target's last tile row (the plan's literal reading of E348's
    // "from the bottom") give another image on E1060's vp64-e348 row
    let r = t.get("rows").arr().iter().find(|r| r.get("id").str() == Some("vp64-e348")).unwrap();
    let (w, h, full, clip) = job(r.get("args").str().unwrap());
    let c = clip.unwrap();
    let flip = RegionClip { rows: (h / 16 - 1 - c.rows.1, h / 16 - 1 - c.rows.0), ..c };
    let img = image(w, h, full, Some(flip));
    assert_ne!(r.get("pixels").get("sha256").str(), Some(digest(w, &img).as_str()));
}
