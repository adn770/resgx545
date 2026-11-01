// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The transfer model against the hardware: the builder's baselines (a fixture, so that it runs
//! without the data repository) and every scene vector of `scene-vectors/` (doc/specs/vectors.md
//! section 6; `$RESGX545_DATA`, or `$RESGX545_SCENE_VECTORS` for a set not yet landed). Skips,
//! saying so, without them; with `RESGX545_REQUIRE_DATA` set it fails instead. The gate is zero
//! mismatches (D5); refusals are counted by question, fitted results apart.

use sgx_pipe::Verdict;
use sgx_pipe::data::{Ctx, files};
use sgx_pipe::job::replay_file;
use sgx_pipe::report::Report;
use sgx_sim::json::{Json, parse};

fn fixture() -> Json {
    parse(include_str!("fixtures/transfer-baselines.scene.json"))
}

fn verdicts(file: &Json) -> Vec<(String, Verdict)> {
    replay_file(file, "transfer").into_iter().map(|r| r.map(|r| (r.id, r.verdict)).unwrap()).collect()
}

#[test]
fn the_builders_fill_and_copy_replay_matched_pixel_for_pixel() {
    let v = verdicts(&fixture());
    assert_eq!(v.len(), 2);
    for (id, v) in &v {
        assert_eq!(*v, Verdict::Matched, "{id}");
    }
}

/// A scene of the fixture's fill with `delta` on its command words, against `expect`.
fn fill_with(delta: &str, expect: &str) -> Verdict {
    scene_with(0, delta, expect)
}

/// A scene of the fixture's base `base` (0 the fill, 1 the copy) with `delta`, against `expect`.
fn scene_with(base: usize, delta: &str, expect: &str) -> Verdict {
    let mut f = fixture();
    let sc = format!(r#"{{"id": "d", "base": {base}, "delta": {delta}, "expect": {expect}}}"#);
    let Json::Obj(m) = &mut f else { panic!() };
    for (k, v) in m.iter_mut() {
        if k == "scenes" {
            *v = Json::Arr(vec![parse(&sc)]);
        }
    }
    verdicts(&f).remove(0).1
}

#[test]
fn a_smaller_render_box_leaves_the_other_tiles_unwritten() {
    // the box 0..=1 x 0..=0 (word 13 = 0x10000): the first row of 32 x 16 tiles, 1024 pixels
    let one_row = fill_with(
        r#"{"xfer": {"13": "0x10000"}}"#,
        r#"{"image": {"mixed": [["0xff336699", 1024], ["0xdeadbeef", 1024]]}, "outside": 0}"#,
    );
    assert_eq!(one_row, Verdict::Matched);
}

#[test]
fn a_larger_render_box_is_clipped_by_the_pbe_rectangle() {
    let bigger =
        fill_with(r#"{"xfer": {"13": "0x30003"}}"#, r#"{"image": {"o0": "0xff336699"}, "outside": 0}"#);
    assert_eq!(bigger, Verdict::Matched);
}

#[test]
fn pixel_event_data_dword_8_decides_which_tiles_run_the_end_of_tile_task() {
    // E265: 0 and 2 write no tile, 4 leaves the last tile (32, 16) unwritten, 0x8 changes nothing
    let at = |v: &str| {
        fill_with(
            &format!(r#"{{"memory": [{{"base": "0x2e000000", "at": {{"24": "{v}"}}}}]}}"#),
            r#"{"image": {"o0": "0xff336699"}}"#,
        )
    };
    // dword 8 of the data segment at 0x2e000040 is dword 24 of the page
    assert_eq!(at("0x100"), Verdict::Matched);
    let none = fill_with(
        r#"{"memory": [{"base": "0x2e000000", "at": {"24": "0x0"}}]}"#,
        r#"{"image": {"o0": "0xdeadbeef"}}"#,
    );
    assert_eq!(none, Verdict::Matched);
    let last = fill_with(
        r#"{"memory": [{"base": "0x2e000000", "at": {"24": "0x4"}}]}"#,
        r#"{"image": {"mixed": [["0xff336699", 1536], ["0xdeadbeef", 512]]}}"#,
    );
    assert_eq!(last, Verdict::Matched);
}

#[test]
fn a_word_no_record_explains_refuses_under_q206_and_a_wrong_expectation_is_a_mismatch() {
    let r = fill_with(r#"{"xfer": {"4": "0x1"}}"#, r#"{"image": {"o0": "0xff336699"}, "refuse": ["Q206"]}"#);
    assert_eq!(r, Verdict::Refused(vec!["Q206".into()]));
    let unexpected = fill_with(r#"{"xfer": {"4": "0x1"}}"#, r#"{"image": {"o0": "0xff336699"}}"#);
    assert!(matches!(unexpected, Verdict::Unsupported(_)));
    let wrong = fill_with(r#"{}"#, r#"{"image": {"o0": "0xff336698"}}"#);
    assert!(matches!(wrong, Verdict::Mismatch(_)));
    let hung = fill_with(r#"{}"#, r#"{"outcome": "hang"}"#);
    assert!(matches!(hung, Verdict::Mismatch(_)), "the model computes where the hardware hung");
}

fn refused(v: Verdict, ids: &[&str]) {
    assert_eq!(v, Verdict::Refused(ids.iter().map(|s| s.to_string()).collect::<Vec<_>>()));
}

#[test]
fn what_no_record_explains_is_refused_under_the_question_that_covers_it() {
    let any = r#"{"image": {"o0": "0xff336699"}, "refuse": ["Q011", "Q074", "Q076", "Q003", "Q205", "Q206", "Q207", "Q021", "Q078"]}"#;
    // the copy's tag with bit 24 set or at 0 reads the source's last texel (E272): Q011
    refused(scene_with(1, r#"{"xfer": {"0": "0x3000000"}}"#, any), &["Q011"]);
    refused(scene_with(1, r#"{"xfer": {"0": "0x0"}}"#, any), &["Q011"]);
    // which tile an end-of-tile U1 names is not resolvable from the records (E044, E126): Q074
    refused(fill_with(r#"{"memory": [{"base": "0x2e000000", "at": {"28": "0x800008"}}]}"#, any), &["Q074"]);
    refused(fill_with(r#"{"memory": [{"base": "0x2e000000", "at": {"25": "0xfe8"}}]}"#, any), &["Q074"]);
    // the pixel-event program moved by 16 bytes: not the program the records ran (a PDS program)
    refused(fill_with(r#"{"xfer": {"9": "0x2e000050"}}"#, any), &["Q207"]);
    // a tile whose event starts no task: whether the job completes is not known (Q003), not predicted
    refused(fill_with(r#"{"memory": [{"base": "0x2e000000", "at": {"23": "0x0"}}]}"#, any), &["Q003"]);
    // the copy's source address moved off the source buffer reads memory the scene does not hold
    // (the target's pages are not the source): the flat memory's refusal
    refused(
        scene_with(1, r#"{"memory": [{"base": "0x2e000000", "at": {"6": "0x3e00a000"}}]}"#, any),
        &["Q076", "Q003"],
    );
    // a copy's vertices that are not the target's rectangle are the iterators' arithmetic
    refused(scene_with(1, r#"{"memory": [{"base": "0x3e000000", "at": {"16": "0x1001"}}]}"#, any), &["Q205"]);
}

fn replay_all() -> Option<Report> {
    let ctx = Ctx::from_env();
    let Some(dir) = ctx.scenes.clone() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no scene-vectors (RESGX545_DATA)");
        eprintln!("SKIPPED: no scene-vectors (set RESGX545_DATA or RESGX545_SCENE_VECTORS)");
        return None;
    };
    let mut rep = Report::default();
    for f in files(&dir, ".scene.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        assert_eq!(d.get("format").str(), Some("sgx545-scene-vectors"), "{}", f.display());
        // the unit is the directory the file is in (`transfer/`, `ta/`)
        let unit = f
            .strip_prefix(&dir)
            .ok()
            .and_then(|p| p.components().next())
            .map_or("transfer".to_string(), |c| c.as_os_str().to_string_lossy().to_string());
        // 12.2 models the transfer and the TA's output: the scenes of the ISP are not run yet
        if !["transfer", "ta"].contains(&unit.as_str()) {
            continue;
        }
        for r in replay_file(&d, &unit) {
            match r {
                Ok(r) => rep.add(&r),
                Err((id, why)) => rep.skip(&id, &why),
            }
        }
    }
    Some(rep)
}

#[test]
fn scene_vectors_replay_with_no_mismatch() {
    let Some(rep) = replay_all() else { return };
    eprintln!("{}", rep.render());
    for (id, why) in rep.mismatches.iter() {
        eprintln!("MISMATCH {id}: {why}");
    }
    for (id, why) in &rep.skipped {
        eprintln!("SKIPPED {id}: {why}");
    }
    assert!(rep.gate(), "{} mismatches", rep.mismatches.len());
    assert!(rep.skipped.is_empty(), "scenes that could not be replayed: {:?}", rep.skipped.len());
}
