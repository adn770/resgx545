// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The ZLS store, load and control models against the hardware (12.4): the depth buffers of the
//! format runs (E466, E490), the load run (E467) and the control words (E337, E411, E467), from the
//! unit vectors `zls-format`, `zls-load` and `zls-ctl`. The stores rest on the fitted address rule
//! (E465), so they are `Fitted`, never matched; the control words are measured bit readings and
//! match; formats 3, 5 and 6 and bit 0 refuse by question. Skips without the vectors, and fails
//! with `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::unitvec::{Replayed, replay};
use sgx_pipe::{Verdict, unitvec};
use sgx_sim::json::{Json, parse};

fn vectors(kind: &str) -> Option<(Ctx, Vec<Json>)> {
    let ctx = Ctx::from_env();
    let Some(dir) = ctx.units.clone() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no unit-vectors");
        eprintln!("SKIPPED: no unit-vectors");
        return None;
    };
    let mut out = vec![];
    for f in files(&dir, ".vec.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        for v in d.get("vectors").arr() {
            if v.get("init").get("task").str() == Some(kind) {
                out.push(v.clone());
            }
        }
    }
    if out.is_empty() {
        eprintln!("SKIPPED: no {kind} vectors in the set");
        return None;
    }
    Some((ctx, out))
}

fn run(ctx: &Ctx, v: &Json) -> Replayed {
    replay(v, ctx).unwrap_or_else(|e| panic!("{}: {e}", v.get("id").str().unwrap()))
}

fn id_of(v: &Json) -> &str {
    v.get("id").str().unwrap()
}

#[test]
fn the_format_buffers_are_fitted_the_empty_ones_match_and_formats_3_5_6_refuse_q120() {
    let Some((ctx, vs)) = vectors("zls-format") else { return };
    assert_eq!(vs.len(), 11);
    for v in &vs {
        let r = run(&ctx, v);
        let id = id_of(v);
        match id.rsplit("__").next().unwrap() {
            "f3" | "f5" | "f6" => assert_eq!(r.verdict, Verdict::Refused(vec!["Q120".into()]), "{id}"),
            "f4" | "f7" => {
                // nothing is stored without a stencil buffer (E490): no item is compared, which
                // the report counts as empty, never as matched
                assert_eq!(r.verdict, Verdict::Matched, "{id}");
                assert_eq!(r.seen.matched, 0, "{id}");
                assert!(
                    matches!(v.get("init").get("stencil"), Json::Bool(false)),
                    "{id}: no stencil buffer, stated"
                );
            }
            c => {
                assert_eq!(r.verdict, Verdict::Fitted, "{id}: the address rule is a fit, never matched");
                let n = match c {
                    "f2" | "b19_2" => 2 * 393216,
                    _ => 2 * 786432,
                };
                assert_eq!(r.seen.matched, n, "{id}");
                assert_eq!(r.seen.mismatched, 0, "{id}: {:?}", r.seen.notes);
            }
        }
    }
}

#[test]
fn a_changed_expectation_or_buffer_is_a_mismatch_not_a_silent_pass() {
    let Some((ctx, vs)) = vectors("zls-format") else { return };
    let f1 = vs.iter().find(|v| id_of(v).ends_with("__f1")).unwrap();
    // the 24-bit buffer checked as if it held the 16-bit format: the control word differs
    let mut text = format!("{f1:?}");
    assert!(text.contains("0x"), "{text}");
    text.clear();
    let bad = swap_ctl(f1, 0x0017_110c | 2 << 24);
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
    // a stored count that is not the dump's
    let bad = swap_expect(f1, "stored", 1.0);
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
    // the sign flipped: bit 19 on a float buffer
    let f0 = vs.iter().find(|v| id_of(v).ends_with("__f0")).unwrap();
    let bad = swap_ctl(f0, 0x0017_110c | 1 << 19);
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
}

fn rebuild(v: &Json, f: &dyn Fn(&str, &Json) -> Json) -> Json {
    match v {
        Json::Obj(m) => Json::Obj(m.iter().map(|(k, x)| (k.clone(), f(k, &rebuild(x, f)))).collect()),
        Json::Arr(a) => Json::Arr(a.iter().map(|x| rebuild(x, f)).collect()),
        o => o.clone(),
    }
}

fn swap_ctl(v: &Json, ctl: u32) -> Json {
    rebuild(v, &|k, x| if k == "ctl" { Json::Str(format!("{ctl:#010x}")) } else { x.clone() })
}

fn swap_expect(v: &Json, key: &str, n: f64) -> Json {
    let mut v = v.clone();
    if let Json::Obj(m) = &mut v {
        for (k, e) in m.iter_mut() {
            if k == "expect" {
                *e = rebuild(e, &|kk, x| if kk == key { Json::Num(n) } else { x.clone() });
            }
        }
    }
    v
}

#[test]
fn the_load_cases_of_e467_reproduce_and_are_fitted() {
    let Some((ctx, vs)) = vectors("zls-load") else { return };
    assert_eq!(vs.len(), 30);
    let mut items = 0;
    for v in &vs {
        let r = run(&ctx, v);
        assert_eq!(r.verdict, Verdict::Fitted, "{}: {:?}", id_of(v), r.verdict);
        items += r.seen.matched;
    }
    assert_eq!(items, 8 * 40960 + 12 * 32768 + 8 * 32768);
    // the depth the triangle leaves: 16384 of 32768 pixels, not 32768 (E467)
    let b = vs.iter().find(|v| id_of(v).starts_with("zls-load__B") && id_of(v).ends_with("510e")).unwrap();
    let bad = swap_expect(b, "drawn", 32768.0);
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
}

#[test]
fn the_control_words_are_matched_fitted_or_refused_as_what_they_rest_on() {
    let Some((ctx, vs)) = vectors("zls-ctl") else { return };
    assert_eq!(vs.len(), 32 + 5 + 10);
    let (mut matched, mut fitted, mut refused, mut faulted) = (vec![], vec![], vec![], vec![]);
    for v in &vs {
        let r = run(&ctx, v);
        let id = id_of(v).trim_start_matches("zls-ctl__").to_string();
        match r.verdict {
            Verdict::Matched => {
                assert!(r.seen.matched > 0, "{id}");
                matched.push(id)
            }
            Verdict::Fitted => fitted.push(id),
            Verdict::Refused(q) => refused.push((id, q)),
            Verdict::PredictedFault => faulted.push(id),
            o => panic!("{id}: {o:?} {:?}", r.seen.notes),
        }
    }
    // bits 5 to 11 faulted the job in the scratch run: the model predicts each fault at the page
    // E411's kernel log names (its store's first unmapped page, E1070); format 4 with a stencil
    // buffer refuses (Q120); the 16-bit format at G = 1 (flip-25) replays since E977 held its
    // layout at other pitches
    assert_eq!(faulted, (5..=11).map(|b| format!("flip-{b:02}")).collect::<Vec<_>>());
    assert_eq!(refused, vec![("flip-26".to_string(), vec!["Q120".to_string()])]);
    // matched: bits that read as the records state with no address, no format and no inferred load;
    // fitted: every vector that compares stored pages (E465's rule), a pitch or a format (E465, E466)
    // or a load by bit 1 alone ([infer])
    assert!(matched.contains(&"flip-02".to_string()) && !matched.contains(&"flip-00".to_string()));
    assert!(fitted.contains(&"flip-00".to_string()), "bit 0 stores the control's pages: fitted");
    for id in ["flip-01", "flip-03", "flip-04", "flip-19", "flip-24", "flip-25", "load-0017110e"] {
        assert!(fitted.contains(&id.to_string()), "{id}");
    }
    assert_eq!((matched.len(), fitted.len(), refused.len(), faulted.len()), (15, 24, 1, 7));
    // a wrong reading of a bit is a mismatch
    let f = vs.iter().find(|v| id_of(v) == "zls-ctl__flip-19").unwrap();
    let bad = rebuild(f, &|k, x| if k == "negate" { Json::Bool(false) } else { x.clone() });
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
}

#[test]
fn the_stored_pages_of_e411_flips_are_compared_with_the_model() {
    let Some((ctx, vs)) = vectors("zls-ctl") else { return };
    // bit 3 cleared (G = 0, overlapping tiles): page 4 640, pages 12 and 13 1024, page 14 512
    let f = vs.iter().find(|v| id_of(v) == "zls-ctl__flip-03").unwrap();
    let r = run(&ctx, f);
    assert_eq!(r.verdict, Verdict::Fitted, "{:?}", r.seen.notes);
    assert!(r.seen.matched >= 640 + 1024 + 1024 + 512, "{}", r.seen.matched);
    // a page count that is not the run's is a mismatch
    let bad = rebuild(f, &|k, x| if k == "14" { Json::Num(1024.0) } else { x.clone() });
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
    // bit 0: the colour image is not written and the pages are the control's
    let f = vs.iter().find(|v| id_of(v) == "zls-ctl__flip-00").unwrap();
    assert_eq!(run(&ctx, f).verdict, Verdict::Fitted);
    let bad = rebuild(f, &|k, x| if k == "writes_pixels" { Json::Bool(true) } else { x.clone() });
    assert!(matches!(run(&ctx, &bad).verdict, Verdict::Mismatch(_)));
}

#[test]
fn a_misspelled_expectation_key_is_a_mismatch_in_the_three_kinds() {
    for (kind, from, to) in [
        ("zls-ctl", "store_depth", "stor_depth"),
        ("zls-ctl", "pages", "page"),
        ("zls-load", "drawn", "drwan"),
        ("zls-load", "stencil", "stencl"),
        ("zls-format", "stored", "stord"),
    ] {
        let Some((ctx, vs)) = vectors(kind) else { return };
        let v = vs
            .iter()
            .find(|v| v.get("expect").obj().iter().any(|(k, _)| k == from) && !id_of(v).ends_with("flip-02"))
            .unwrap_or_else(|| panic!("{kind} {from}"));
        assert!(!matches!(run(&ctx, v).verdict, Verdict::Mismatch(_)), "{kind} {from}");
        let bad = rename_key(v, from, to);
        let r = run(&ctx, &bad);
        assert!(matches!(r.verdict, Verdict::Mismatch(_)), "{kind} {from} -> {to}: {:?}", r.verdict);
    }
}

fn rename_key(v: &Json, from: &str, to: &str) -> Json {
    match v {
        Json::Obj(m) => Json::Obj(
            m.iter()
                .map(|(k, x)| (if k == from { to.to_string() } else { k.clone() }, rename_key(x, from, to)))
                .collect(),
        ),
        Json::Arr(a) => Json::Arr(a.iter().map(|x| rename_key(x, from, to)).collect()),
        o => o.clone(),
    }
}

#[test]
fn the_kinds_are_in_the_zls_unit() {
    for k in ["zls-store", "zls-load", "zls-format", "zls-ctl"] {
        assert_eq!(unitvec::unit_of(k), "zls");
    }
}
