// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The unit-vector replay on vectors written inline, so that it is tested without the data
//! repository: a model's result against `expect` through `replay`, kind by kind.

use sgx_pipe::Verdict;
use sgx_pipe::data::Ctx;
use sgx_pipe::unitvec::replay;
use sgx_sim::json::parse;

fn ctx() -> Ctx {
    Ctx { root: None, units: None, scenes: None }
}

fn verdict(v: &str) -> Verdict {
    replay(&parse(v), &ctx()).unwrap().verdict
}

#[test]
fn te_region_of_a_triangle_in_one_tile_and_the_tiles_listed() {
    // the triangle sits in tile (16, 0) of a 32 x 16 region; the TA listed that tile only
    let v = |listed: &str, matched: u32| {
        format!(
            r#"{{"id": "t", "init": {{"task": "te-region", "w": 32, "h": 16, "prims": [[[18,2],[26,3],[20,12]]]}},
                "expect": {{"matched": {matched}, "listed": {listed}}}}}"#
        )
    };
    assert_eq!(verdict(&v(r#"[[16, 0, "any"]]"#, 2)), Verdict::Fitted);
    assert_eq!(verdict(&v(r#"[[16, 0, [0]]]"#, 2)), Verdict::Fitted);
    // the TA listed the other tile instead: two pairs differ
    assert!(matches!(verdict(&v(r#"[[0, 0, [0]]]"#, 2)), Verdict::Mismatch(_)));
    // a tile listed that the rule does not list, and one the rule lists that is not
    assert!(matches!(verdict(&v(r#"[[0, 0, "any"], [16, 0, "any"]]"#, 2)), Verdict::Mismatch(_)));
    assert!(matches!(verdict(&v("[]", 2)), Verdict::Mismatch(_)));
    // the vector's pair count must be the model's
    assert!(matches!(verdict(&v(r#"[[16, 0, "any"]]"#, 3)), Verdict::Mismatch(_)));
}

#[test]
fn ta_object_vectors_compare_the_layout_and_predict_the_recorded_failures() {
    let ok = r#"{"id": "o", "init": {"task": "ta-object", "n": 4, "sizes": 5, "fmts": 1},
                 "expect": {"stored": 3, "iterated": 5, "format_hi": "0x0004", "masks": [2, 0, 2, 2]}}"#;
    assert_eq!(verdict(ok), Verdict::Fitted);
    let wrong = ok.replace("\"stored\": 3", "\"stored\": 4");
    assert!(matches!(verdict(&wrong), Verdict::Mismatch(_)));
    let hang = r#"{"id": "h", "init": {"task": "ta-object", "n": 8, "sizes": 29, "fmts": 5}, "expect": {"outcome": "hang", "refuse": ["Q165"]}}"#;
    // E541's hang is recalled, not predicted: a refusal naming Q165, not a predicted hang
    assert_eq!(verdict(hang), Verdict::Refused(vec!["Q165".into()]));
    let unexpected = hang.replace(", \"refuse\": [\"Q165\"]", "");
    assert!(matches!(verdict(&unexpected), Verdict::Unsupported(_)));
    // computing an input the hardware hung on is a mismatch; a code the records never saw refuses
    let hung_elsewhere = r#"{"id": "h", "init": {"task": "ta-object", "n": 4, "sizes": 1, "fmts": 0}, "expect": {"outcome": "hang"}}"#;
    assert!(matches!(verdict(hung_elsewhere), Verdict::Mismatch(_)));
    let seven = r#"{"id": "s", "init": {"task": "ta-object", "n": 4, "sizes": 7, "fmts": 0}, "expect": {"refuse": ["Q070"]}}"#;
    assert_eq!(verdict(seven), Verdict::Refused(vec!["Q070".into()]));
}

#[test]
fn the_other_planned_kinds_refuse_naming_their_questions() {
    for (task, q) in [("pbe-emit", "Q012"), ("vdm-stream", "Q047"), ("bif-walk", "Q076")] {
        let v = format!(r#"{{"id": "x", "init": {{"task": "{task}"}}, "expect": {{"refuse": ["{q}"]}}}}"#);
        assert!(matches!(verdict(&v), Verdict::Unsupported(_)), "{task}: all its questions must be listed");
    }
    // listing every question of the unit makes it a refused vector
    let all = r#"{"id": "x", "init": {"task": "pbe-emit"},
                  "expect": {"refuse": ["Q012", "Q040", "Q044", "Q046", "Q074", "Q054", "Q183"]}}"#;
    assert!(matches!(verdict(all), Verdict::Refused(_)));
    assert!(replay(&parse(r#"{"id": "x", "init": {"task": "no-such-kind"}}"#), &ctx()).is_err());
    // zls-load models the load (12.4): a vector without a control word is malformed, not refused
    assert!(replay(&parse(r#"{"id": "x", "init": {"task": "zls-load"}}"#), &ctx()).is_err());
}

#[test]
fn pbe_emit_vectors_check_the_value_stored_for_each_colour() {
    let v = |sb: &str, reg: &str, stored: &str, extra: &str| {
        format!(
            r#"{{"id": "p", "init": {{"task": "pbe-emit", "sideband": "{sb}", "reg0400": "{reg}",
                 "colours": ["0xff203040", "0x80ff8040"]}}, "expect": {{"stored": {stored}{extra}}}}}"#
        )
    };
    // E031: modes 0 to 3 as the pack-modes dumps stored the background and the shader colour
    assert_eq!(verdict(&v("0x200", "0x80", r#"["0xff203040", "0x80ff8040"]"#, "")), Verdict::Matched);
    assert_eq!(verdict(&v("0x201", "0x80", r#"["0xff403020", "0x804080ff"]"#, "")), Verdict::Matched);
    assert_eq!(verdict(&v("0x202", "0x80", r#"["0x403020ff", "0x4080ff80"]"#, "")), Verdict::Matched);
    assert_eq!(verdict(&v("0x203", "0x80", r#"["0x2188", "0xfc08"]"#, "")), Verdict::Matched);
    // E268: bit 25 of the word that loads CR_REG_0400 inverts the alpha, not in RGB565
    assert_eq!(verdict(&v("0x200", "0x2000080", r#"["0x00203040", "0x7fff8040"]"#, "")), Verdict::Matched);
    assert_eq!(verdict(&v("0x203", "0x2000080", r#"["0x2188", "0xfc08"]"#, "")), Verdict::Matched);
    // a value the hardware did not store is a mismatch, one colour each
    assert!(matches!(verdict(&v("0x203", "0x80", r#"["0x2188", "0xfc09"]"#, "")), Verdict::Mismatch(_)));
    // modes the records do not give are refused under their questions, and 22 and 34 under Q012
    assert_eq!(
        verdict(&v("0x216", "0x80", r#"["0x0", "0x0"]"#, r#", "refuse": ["Q012"]"#)),
        Verdict::Refused(vec!["Q012".into()])
    );
    assert_eq!(
        verdict(&v("0x204", "0x80", r#"["0x0", "0x0"]"#, r#", "refuse": ["Q044"]"#)),
        Verdict::Refused(vec!["Q044".into()])
    );
}
