// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The r10-geo q139c table (`vectors/closing/r10-geo/ta-slots/q139c.table.json`, E1007: the TA
//! region headers of the 256 x 256 and 640 x 480 baselines and of four poked `CR_TE_MTILE2`
//! words) replayed with `ta::macrotile_slots`: each row's words (the rule's, or its `ta:144`
//! poke), every target tile's modelled slot against the slots the row's dump holds for it, and
//! the modelled wrong tiles (no surviving header at or before the last-region flag) against the
//! image's. A row whose words the model refuses is counted refused, never a pass. The table's
//! `replay` names `the_model_replays_every_row_of_the_q139c_slots_table`. Skips without the data,
//! and fails with `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::data::Ctx;
use sgx_pipe::ta::{macrotile_slots, tiling};
use sgx_sim::json::{Json, parse};
use std::collections::BTreeSet;

const TABLE: &str = "vectors/closing/r10-geo/ta-slots/q139c.table.json";
const NAME: &str = "the_model_replays_every_row_of_the_q139c_slots_table";

fn load() -> Option<Json> {
    let ctx = Ctx::from_env();
    let Some(root) = ctx.root.as_ref().filter(|r| r.join(TABLE).is_file()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {TABLE}");
        eprintln!("SKIPPED: no {TABLE}");
        return None;
    };
    Some(parse(&std::fs::read_to_string(root.join(TABLE)).unwrap()))
}

fn tile(s: &str) -> (u32, u32) {
    let (c, r) = s.split_once('.').unwrap();
    (c.parse().unwrap(), r.parse().unwrap())
}

/// Ok(tiles compared) or Err(why the row is not the model's).
fn replay(row: &Json) -> Result<usize, String> {
    let id = row.get("id").str().unwrap_or("?");
    let (w, h) = (row.get("width").num().unwrap() as u32, row.get("height").num().unwrap() as u32);
    let t = tiling(w, h);
    let mut m2 = t.mtile2;
    for p in row.get("kpokes").arr() {
        let p = p.str().unwrap();
        let v = p.strip_prefix("1:ta:144=0x").ok_or(format!("{id}: a poke other than ta:144: {p}"))?;
        m2 = u32::from_str_radix(v, 16).unwrap();
    }
    let (model, _) = macrotile_slots(w, h, t.mtile1, m2).map_err(|e| format!("{id}: refused {e:?}"))?;
    let wrong: BTreeSet<(u32, u32)> = match row.get("wrong_tiles").str().unwrap() {
        "none" => BTreeSet::new(),
        s => s.split(',').map(tile).collect(),
    };
    let seen: Vec<((u32, u32), Vec<u32>)> = row
        .get("slots")
        .obj()
        .iter()
        .map(|(k, v)| (tile(k), v.arr().iter().map(|s| s.num().unwrap() as u32).collect()))
        .collect();
    for (&tl, sl) in &model {
        if sl.is_none() != wrong.contains(&tl) {
            return Err(format!("{id}: tile {tl:?} model {sl:?}, the image's wrong {}", wrong.contains(&tl)));
        }
        if let Some(s) = sl {
            let got = seen.iter().find(|(k, _)| *k == tl).map(|(_, v)| v.clone()).unwrap_or_default();
            if !got.contains(s) {
                return Err(format!("{id}: tile {tl:?} model slot {s}, the dump {got:?}"));
            }
        }
    }
    Ok(model.len())
}

#[test]
fn the_model_replays_every_row_of_the_q139c_slots_table() {
    let Some(t) = load() else { return };
    let rows = t.get("rows").arr();
    assert_eq!(rows.len(), 6);
    for r in rows {
        assert_eq!(r.get("header_base").num(), Some(16384.0), "{:?}", r.get("id").str());
    }
    let out: Vec<Result<usize, String>> = rows.iter().map(replay).collect();
    assert!(out.iter().all(Result::is_ok), "{out:?}");
    // two 256 x 256 and 640 x 480 baselines, three poked 256 x 256 rows, one 640 x 480
    assert_eq!(out.iter().map(|r| *r.as_ref().unwrap()).sum::<usize>(), 4 * 128 + 2 * 600);
}

#[test]
fn a_wrong_slot_or_tile_is_a_mismatch() {
    let row = |wrong: &str, slot: u32| {
        let slots: Vec<String> = (0..16u32)
            .flat_map(|r| (0..8u32).map(move |c| (c, r)))
            .map(|(c, r)| {
                let s = macrotile_slots(256, 256, tiling(256, 256).mtile1, tiling(256, 256).mtile2)
                    .unwrap()
                    .0[&(c, r)]
                    .unwrap();
                format!("\"{c}.{r}\": [{}]", if (c, r) == (0, 0) { slot } else { s })
            })
            .collect();
        parse(&format!(
            r#"{{"id": "x", "width": 256, "height": 256, "kpokes": [], "wrong_tiles": "{wrong}", "slots": {{{}}}}}"#,
            slots.join(", ")
        ))
    };
    assert_eq!(replay(&row("none", 0)), Ok(128));
    assert!(replay(&row("none", 5)).is_err());
    assert!(replay(&row("0.0", 0)).is_err());
}

#[test]
fn the_table_names_this_test_as_its_replay() {
    let Some(t) = load() else { return };
    let r = t.get("replay");
    assert_eq!(r.get("status").str(), Some("replayed"));
    assert!(r.get("test").str().unwrap().ends_with(NAME), "{:?}", r.get("test").str());
}
