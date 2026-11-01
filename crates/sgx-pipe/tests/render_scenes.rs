// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The vertex side and the TA against the hardware's parameter buffer dumps (12.2): three dumped
//! jobs as a fixture, so the byte-for-byte check runs without the data repository, and every render
//! scene of `scene-vectors/ta/` (`$RESGX545_DATA`, or `$RESGX545_SCENE_VECTORS` for a set not yet
//! landed; the data tests skip, saying so, without it, and fail with `RESGX545_REQUIRE_DATA`).
//! Every result rests on a fitted rule, so none is `matched`: the gate is zero mismatches.

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::job::replay_file;
use sgx_pipe::{Outcome, Verdict};
use sgx_sim::json::{Json, parse};
use std::collections::BTreeMap;

fn fixture() -> Json {
    parse(include_str!("fixtures/tri-baselines.scene.json"))
}

#[test]
fn the_fixture_jobs_reproduce_the_dumped_buffers_and_are_fitted_never_matched() {
    let r = replay_file(&fixture(), "ta");
    assert_eq!(r.len(), 3);
    for r in r {
        let r = r.unwrap();
        assert_eq!(r.verdict, Verdict::Fitted, "{}", r.id);
    }
}

#[test]
fn a_word_of_the_dump_changed_is_a_mismatch_so_the_comparison_is_not_vacuous() {
    let mut f = fixture();
    // change one expected stream dword of the first scene
    let Json::Obj(top) = &mut f else { panic!() };
    let scenes = top.iter_mut().find(|(k, _)| k == "scenes").unwrap();
    let Json::Arr(list) = &mut scenes.1 else { panic!() };
    let text = format!("{:?}", list[0].get("expect").get("buffers").get("param").get("sparse"));
    assert!(text.contains("0x5c88003f"), "the fixture's first stream word");
    let mut s = include_str!("fixtures/tri-baselines.scene.json").to_string();
    s = s.replacen("\"0x5c88003f\"", "\"0x5c88003e\"", 1);
    let r = replay_file(&parse(&s), "ta");
    assert!(matches!(r[0].as_ref().unwrap().verdict, Verdict::Mismatch(_)));
}

fn dir() -> Option<std::path::PathBuf> {
    let ctx = Ctx::from_env();
    let d = ctx.scenes.map(|d| d.join("ta")).filter(|d| d.is_dir());
    if d.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no scene-vectors/ta (RESGX545_DATA)");
        eprintln!("SKIPPED: no scene-vectors/ta (set RESGX545_DATA or RESGX545_SCENE_VECTORS)");
    }
    d
}

/// Replay every scene of every file: verdict counts and, for the refusals, the questions.
fn replay_all(d: &std::path::Path) -> (BTreeMap<String, u64>, BTreeMap<String, u64>) {
    let (mut verdicts, mut refused) = (BTreeMap::new(), BTreeMap::new());
    for f in files(d, ".scene.json") {
        let doc = parse(&std::fs::read_to_string(&f).unwrap());
        let scenes = sgx_pipe::scene::Scene::load_file(&doc);
        for (sc, r) in scenes.into_iter().zip(replay_file(&doc, "ta")) {
            let r = r.unwrap_or_else(|e| panic!("{}: {:?}", f.display(), e));
            let sc = sc.unwrap();
            let key = match &r.verdict {
                Verdict::Mismatch(m) => panic!("MISMATCH {}: {m}", r.id),
                Verdict::Unsupported(_) => {
                    let Outcome::Unsupported { ids, .. } = sgx_pipe::job::run(&sc).outcome else {
                        panic!("{}", r.id)
                    };
                    *refused.entry(ids.join("+")).or_default() += 1;
                    "unsupported".to_string()
                }
                v => format!("{v:?}"),
            };
            *verdicts.entry(key).or_default() += 1;
        }
    }
    (verdicts, refused)
}

#[test]
fn every_dumped_render_scene_is_fitted_or_refused_by_question_and_none_differs() {
    let Some(d) = dir() else { return };
    let (verdicts, refused) = replay_all(&d);
    eprintln!("{verdicts:?}\nrefused by question: {refused:?}");
    assert_eq!(verdicts.get("Matched"), None, "a fitted rule is never reported matched");
    // the 89 dumped jobs of the draft's nine files: a scene lost from the set fails here
    assert!(verdicts.get("Fitted").copied().unwrap_or(0) >= 89, "{verdicts:?}");
    assert!(refused.keys().all(|k| k.split('+').all(|q| q.starts_with('Q'))), "{refused:?}");
}
