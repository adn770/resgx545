// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Review r121 item 9: every refusal of the transfer model that only the data-backed replay
//! exercised, as an inline scene of the builder's fixture, so that dropping one fails a test
//! without the data repository; and the replay's gate that nothing is `unsupported` (a refusal
//! under a question the vector's `refuse` list lacks). Each scene names a question that depends
//! on the words alone: the `expect` has no recorded result of the hardware to select it.

use sgx_pipe::Verdict;
use sgx_pipe::data::{Ctx, files};
use sgx_pipe::job::replay_file;
use sgx_pipe::report::Report;
use sgx_sim::json::{Json, parse};

fn fixture() -> Json {
    parse(include_str!("fixtures/transfer-baselines.scene.json"))
}

/// The fixture's base `base` (0 the fill, 1 the copy) with `delta`, against a vector that lists
/// every question the model may refuse under, as the generator's lists do for a poked space.
fn with(base: usize, delta: &str) -> Verdict {
    let any = r#"["Q003", "Q011", "Q066", "Q074", "Q076", "Q078", "Q180", "Q205", "Q206", "Q207"]"#;
    // the baselines' images: the fill's one colour, the copy's source pattern (the fixture's hashes)
    let image =
        if base == 0 { r#"{"hash": "0xb60c6095080bd325"}"# } else { r#"{"hash": "0x9b1c0be484ac0d25"}"# };
    let sc = format!(
        r#"{{"id": "d", "base": {base}, "delta": {delta}, "expect": {{"image": {image}, "outside": 0, "refuse": {any}}}}}"#
    );
    let mut f = fixture();
    let Json::Obj(m) = &mut f else { panic!() };
    for (k, v) in m.iter_mut() {
        if k == "scenes" {
            *v = Json::Arr(vec![parse(&sc)]);
        }
    }
    replay_file(&f, "transfer").remove(0).map(|r| r.verdict).unwrap()
}

fn refused(v: Verdict, ids: &[&str]) {
    assert_eq!(v, Verdict::Refused(ids.iter().map(|s| s.to_string()).collect::<Vec<_>>()));
}

fn pds_at(i: usize, v: &str) -> String {
    format!(r#"{{"memory": [{{"base": "0x2e000000", "at": {{"{i}": "{v}"}}}}]}}"#)
}

fn bg_at(i: usize, v: &str) -> String {
    format!(r#"{{"memory": [{{"base": "0x3e000000", "at": {{"{i}": "{v}"}}}}]}}"#)
}

#[test]
fn a_copys_background_word_10_above_bit_15_refuses_as_e069_swept_the_two_low_bytes_only() {
    refused(with(1, &bg_at(10, "0x10000202")), &["Q066"]);
    // inside the swept bytes the word changes nothing
    assert_eq!(with(1, &bg_at(10, "0x0000ff02")), Verdict::Matched);
}

#[test]
fn a_nan_or_infinite_coordinate_and_a_triangle_off_the_targets_rectangle_refuse() {
    // the iterated plane's u0 is NaN: the texture unit returns a texel for it, the model does not
    refused(with(1, &bg_at(3, "0x7fc00000")), &["Q205"]);
    refused(with(1, &bg_at(6, "0x7f800000")), &["Q205"]);
    refused(with(1, &bg_at(16, "0x1001")), &["Q205"]);
}

#[test]
fn a_source_address_inside_the_targets_pages_refuses_whatever_the_tile_order_wrote() {
    // the copy's texture address (the primary program's data dword 6, page dword 6) moved onto the
    // target at 0x3e004000: the page holds the sentinel and the tiles' stores so far
    refused(with(1, &pds_at(6, "0x3e004000")), &["Q076", "Q003"]);
}

#[test]
fn the_last_tile_that_does_not_end_the_render_and_a_tile_with_no_task_refuse_naming_q003() {
    // pixel-event data dword 16 (page dword 32 of the fill) is the U1 flag with bit 22
    refused(with(0, &pds_at(32, "0x0")), &["Q003"]);
    // dword 7 (page dword 23) is a tile's ir1 mask: at 0 no tile starts a task
    refused(with(0, &pds_at(23, "0x0")), &["Q003"]);
}

#[test]
fn a_pds_program_that_is_not_a_template_the_records_ran_refuses_under_q207() {
    // the secondary program's code (page dword 12 of the fill) and the primary's (page dword 4)
    refused(with(0, &pds_at(12, "0x7000304")), &["Q207"]);
    refused(with(0, &pds_at(4, "0x7000304")), &["Q207"]);
    // the pixel-event program's code starts at page dword 16 + 20
    refused(with(0, &pds_at(36, "0xcf820871")), &["Q207"]);
}

#[test]
fn the_tile_masks_that_build_u1_from_ir0_are_pinned() {
    // data dwords 9 and 13 (page dwords 25 and 29) with bit 4 of the x mask cleared: E620's fact
    refused(with(0, &pds_at(25, "0xfe8")), &["Q206"]);
    refused(with(0, &pds_at(29, "0x3fe000")), &["Q206"]);
}

#[test]
fn a_command_word_with_no_record_and_a_set_coefficient_group_refuse_under_q206() {
    refused(with(0, r#"{"xfer": {"4": "0x1"}}"#), &["Q206"]);
    refused(with(0, r#"{"xfer": {"17": "0x1"}}"#), &["Q206"]);
}

#[test]
fn the_replay_of_the_scene_vectors_has_no_unsupported_scene() {
    let ctx = Ctx::from_env();
    let Some(dir) = ctx.scenes.clone() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no scene-vectors (RESGX545_DATA)");
        eprintln!("SKIPPED: no scene-vectors (set RESGX545_DATA or RESGX545_SCENE_VECTORS)");
        return;
    };
    let mut rep = Report::default();
    // the transfer scenes only: the render scenes of the later sub-phases sit beside them and refuse by
    // their own lists (render_scenes.rs, isp_scenes.rs replay those)
    for f in files(&dir.join("transfer"), ".scene.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        for r in replay_file(&d, "transfer") {
            rep.add(&r.unwrap());
        }
    }
    let c = &rep.units["transfer"];
    assert_eq!(c.mismatch, 0, "mismatches");
    assert_eq!(c.unsupported, 0, "a refusal under a question the vector's refuse list lacks");
    assert_eq!(c.fitted, 0, "the transfer model uses no fitted rule");
}
