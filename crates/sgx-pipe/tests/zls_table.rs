// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The closing pass's ZLS table (`vectors/closing/r3-geo-c/zls-extents/g-z.table.json`, E831)
//! replayed with the store band of `zls.rs`: for each job the pixels of the target's tile area
//! that the triangle covers inside the band (`in_band`, rule A) are the stored ones, and their
//! count and extent are compared with the row's. An odd size is a refused row (Q287: rule A and
//! FLOOR differ there), never a pass; a triangle the model cannot read is refused too. The
//! table's `replay` names `the_band_replays_every_modelled_row_of_the_g_z_table` once every
//! modelled row matched. Skips without the data, and fails with `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::data::Ctx;
use sgx_pipe::isp::{GRID, Tri};
use sgx_pipe::zls::in_band;
use sgx_sim::json::{Json, parse};

const TABLE: &str = "vectors/closing/r3-geo-c/zls-extents/g-z.table.json";
const CASES: &str = "render/closing-r3-geo-c/out/g-z/cases.tsv";
const NAME: &str = "the_band_replays_every_modelled_row_of_the_g_z_table";

#[derive(Debug, PartialEq)]
enum Row {
    Matched,
    Refused(&'static str),
    Mismatched(String),
}

fn load() -> Option<(Json, String)> {
    let ctx = Ctx::from_env();
    let root = ctx.root.as_ref().filter(|r| r.join(TABLE).is_file() && r.join(CASES).is_file());
    let Some(root) = root else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no g-z table or cases");
        eprintln!("SKIPPED: no g-z table or cases");
        return None;
    };
    let t = parse(&std::fs::read_to_string(root.join(TABLE)).unwrap());
    Some((t, std::fs::read_to_string(root.join(CASES)).unwrap()))
}

/// The triangle of a job: the full-screen one (0,0), (3W,0), (0,3H) or the `--tri-v` pixels (1/256).
fn triangle(args: &str, w: i64, h: i64) -> Option<Tri> {
    let opt = |name: &str| args.split(name).nth(1)?.split_whitespace().next().map(str::to_string);
    let z: Vec<f32> = opt("--tri-z ")?.split(',').map(|s| s.parse().unwrap()).collect();
    let v = if args.contains("--tri-full") {
        vec![0, 0, 3 * w * GRID, 0, 0, 3 * h * GRID]
    } else {
        opt("--tri-v ")?.split(',').map(|s| s.parse().unwrap()).collect()
    };
    (z.len() == 3 && v.len() == 6)
        .then(|| Tri { v: [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])], z: [z[0], z[1], z[2]] })
}

/// What the model stores for a `w` x `h` target: the count and the extent of the covered pixels
/// inside the band, in the tile area of 32 x 16 tiles.
fn model(t: &Tri, w: u32, h: u32) -> (u64, [u32; 2]) {
    let (mut n, mut ext) = (0, [0, 0]);
    for y in 0..h.div_ceil(16) * 16 {
        for x in 0..w.div_ceil(32) * 32 {
            if in_band(x, y, w, h) && t.covers(x, y) {
                n += 1;
                ext = [ext[0].max(x + 1), ext[1].max(y + 1)];
            }
        }
    }
    (n, ext)
}

fn replay(row: &Json, cases: &str) -> Row {
    let (w, h) = (row.get("width").num().unwrap() as u32, row.get("height").num().unwrap() as u32);
    if w % 2 == 1 || h % 2 == 1 {
        return Row::Refused("Q287");
    }
    let id = row.get("id").str().unwrap();
    let line = cases.lines().find(|l| l.split('\t').next() == Some(id));
    let Some(tri) = line.and_then(|l| triangle(l, w.into(), h.into())) else {
        return Row::Refused("no triangle for the job in cases.tsv");
    };
    let (n, ext) = model(&tri, w, h);
    let want = row.get("extent").arr();
    let got = (
        row.get("stored").num().unwrap() as u64,
        [want[0].num().unwrap() as u32, want[1].num().unwrap() as u32],
    );
    if (n, ext) == got {
        Row::Matched
    } else {
        Row::Mismatched(format!("{id}: model {n} stored, extent {ext:?}; table {got:?}"))
    }
}

#[test]
fn the_band_replays_every_modelled_row_of_the_g_z_table() {
    let Some((t, cases)) = load() else { return };
    let rows = t.get("rows").arr();
    assert_eq!(rows.len(), 15);
    let res: Vec<Row> = rows.iter().map(|r| replay(r, &cases)).collect();
    let m = res.iter().filter(|x| **x == Row::Matched).count();
    let r = res.iter().filter(|x| matches!(x, Row::Refused(_))).count();
    let bad: Vec<_> =
        res.iter().filter_map(|x| if let Row::Mismatched(s) = x { Some(s) } else { None }).collect();
    eprintln!("g-z: {m} matched, {r} refused, {} mismatched", bad.len());
    assert!(bad.is_empty(), "mismatched rows: {bad:?}");
    assert_eq!((m, r), (15, 0), "E831's cells are all at even sizes");
}

#[test]
fn an_odd_size_is_a_refused_row_and_a_wrong_extent_a_mismatch() {
    let Some((_, cases)) = load() else { return };
    let edit = |w: &str, ext: &str| {
        parse(&format!(r#"{{"id":"z-ctl-34x18-x","width":{w},"height":18,"stored":924,"extent":{ext}}}"#))
    };
    assert_eq!(replay(&edit("33", "[42,22]"), &cases), Row::Refused("Q287"));
    assert!(matches!(replay(&edit("34", "[43,22]"), &cases), Row::Mismatched(_)));
}

#[test]
fn the_table_names_this_test_as_its_replay() {
    let Some((t, _)) = load() else { return };
    let r = t.get("replay");
    assert_eq!(r.get("status").str(), Some("replayed"));
    assert!(r.get("test").str().unwrap().ends_with(NAME), "{:?}", r.get("test").str());
}
