// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Unit vectors (doc/specs/vectors.md section 5) and the replay that holds a unit model to them.
//!
//! A unit vector is a vector of the `sgx545-vectors` container whose `init.task` names a unit
//! kind (`zls-store`, `te-region`, `ta-object`, `isp-tile`, ...), with `expect` instead of
//! `readback`. A replay runs the kind's model over `init` and judges the result against
//! `expect` ([`judge`]): matched, fitted (D6: reported apart, never matched), near, a
//! predicted hang or fault, a refusal the vector expects (`expect.refuse`), an unsupported
//! kind, a mismatch, or (D5) one of the results of a non-repeatable hardware outcome
//! (`expect.outcome = "either"`).

use crate::data::Ctx;
use crate::outcome::{Outcome, Verdict};
use crate::{bif, isp, pbe, ta, vdm, zls};
use sgx_sim::json::Json;
use std::collections::BTreeMap;

/// What a model saw over one vector, item by item (dwords, pairs, tiles, objects).
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Seen {
    pub matched: u64,
    pub mismatched: u64,
    /// of `matched`, items checked by presence only (the tile lists some primitive), not per
    /// primitive: a weaker check, reported apart
    pub weak: u64,
    /// items the model refuses, by open question
    pub refused: BTreeMap<String, u64>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Modelled {
    pub outcome: Outcome,
    pub seen: Seen,
}

impl Modelled {
    pub fn refusing(o: Outcome) -> Modelled {
        Modelled { outcome: o, seen: Seen::default() }
    }
}

/// How a vector replayed, with its item counts.
#[derive(Debug, Clone, PartialEq)]
pub struct Replayed {
    pub id: String,
    pub unit: String,
    pub task: String,
    pub verdict: Verdict,
    pub seen: Seen,
}

fn ids_of(j: &Json) -> Vec<String> {
    j.arr().iter().filter_map(|s| s.str().map(str::to_string)).collect()
}

/// Judge a model's result against a vector's `expect`.
pub fn judge(expect: &Json, m: &Modelled) -> Verdict {
    let refuse = ids_of(expect.get("refuse"));
    if expect.get("outcome").str() != Some("either") {
        return judge_one(expect, &refuse, m);
    }
    // D5: an `either` lists the results the hardware gave: at least two, each of which checks
    // something (an alternative with no check would match any computed result)
    let alts = expect.get("either").arr();
    if alts.len() < 2 || alts.iter().any(is_empty) {
        return Verdict::Mismatch(
            "a malformed either: it needs two or more alternatives that each check something".into(),
        );
    }
    let vs: Vec<Verdict> = expect.get("either").arr().iter().map(|a| judge_one(a, &refuse, m)).collect();
    if vs.iter().any(Verdict::is_match) {
        Verdict::Either
    } else if let Some(v) = vs.iter().find(|v| matches!(v, Verdict::Fitted | Verdict::Near)) {
        v.clone() // a result that rests on a fitted rule stays fitted (D6)
    } else if let Some(v) = vs.iter().find(|v| matches!(v, Verdict::Refused(_) | Verdict::Unsupported(_))) {
        v.clone()
    } else {
        Verdict::Mismatch(format!("none of the {} recorded outcomes: {:?}", vs.len(), vs))
    }
}

/// An expectation that names no outcome and compares no item.
pub(crate) fn is_empty(e: &Json) -> bool {
    e.obj().is_empty()
}

pub(crate) fn judge_one(expect: &Json, refuse: &[String], m: &Modelled) -> Verdict {
    let want = expect.get("outcome").str().unwrap_or("ok");
    match &m.outcome {
        Outcome::Unsupported { ids, why } => {
            if !ids.is_empty() && ids.iter().all(|i| refuse.contains(i)) {
                Verdict::Refused(ids.clone())
            } else {
                Verdict::Unsupported(why.clone())
            }
        }
        Outcome::Hang { .. } if want == "hang" => Verdict::PredictedHang,
        Outcome::Hang { record } => {
            Verdict::Mismatch(format!("model predicts a hang ({record}); recorded {want}"))
        }
        Outcome::Fault { addr, .. } if want == "fault" => match expect.get("addr").hex() {
            Some(a) if a != *addr as u64 => Verdict::Mismatch(format!("fault at {addr:#x}, recorded {a:#x}")),
            _ => Verdict::PredictedFault,
        },
        Outcome::Fault { addr, .. } => {
            Verdict::Mismatch(format!("model predicts a fault at {addr:#x}; recorded {want}"))
        }
        computed => {
            if want == "hang" || want == "fault" {
                return Verdict::Mismatch(format!(
                    "the model computes a result where the hardware gave a {want}"
                ));
            }
            if is_empty(expect) {
                return Verdict::Mismatch("the vector's expect compares nothing".into());
            }
            if m.seen.mismatched > 0 {
                return Verdict::Mismatch(format!(
                    "{} items differ: {}",
                    m.seen.mismatched,
                    m.seen.notes.join("; ")
                ));
            }
            if let Some(n) = expect.get("matched").num()
                && n as u64 != m.seen.matched
            {
                return Verdict::Mismatch(format!(
                    "{} items matched, the vector has {}",
                    m.seen.matched, n as u64
                ));
            }
            let exp_ref: BTreeMap<String, u64> = expect
                .get("refused")
                .obj()
                .iter()
                .map(|(k, v)| (k.clone(), v.num().unwrap_or(0.0) as u64))
                .collect();
            if exp_ref != m.seen.refused {
                return Verdict::Mismatch(format!(
                    "refused items {:?}, the vector has {:?}",
                    m.seen.refused, exp_ref
                ));
            }
            match computed {
                Outcome::Ok => Verdict::Matched,
                Outcome::Near { .. } => Verdict::Near,
                _ => Verdict::Fitted,
            }
        }
    }
}

/// The model of each unit kind, over the whole vector (it compares its result with `expect`
/// item by item and counts; [`judge`] classifies). `Err` is a vector that cannot be replayed here (a dump of the
/// data repository is missing, the vector is malformed): the caller skips it and says so.
pub fn model(task: &str, v: &Json, ctx: &Ctx) -> Result<Modelled, String> {
    match task {
        "zls-store" => kind_zls_store(v, ctx),
        "te-region" => kind_te_region(v),
        "ta-object" => Ok(kind_ta_object(v)),
        "isp-tile" => kind_isp_tile(v, ctx),
        "zls-load" => Ok(Modelled::refusing(zls::refuse())),
        "pbe-emit" => Ok(kind_pbe_emit(v)),
        "vdm-stream" => Ok(Modelled::refusing(vdm::refuse())),
        "bif-walk" => Ok(Modelled::refusing(bif::refuse())),
        _ => Err(format!("unknown unit kind {task}")),
    }
}

fn u(j: &Json) -> u32 {
    j.num().map_or_else(|| j.hex().unwrap_or(0) as u32, |n| n as u32)
}

fn file(ctx: &Ctx, j: &Json) -> Result<Vec<u8>, String> {
    ctx.read_gz(j.get("path").str().ok_or("no dump path")?, j.get("sha256").str().unwrap_or(""))
}

/// zls-store: the E465 address rule over a pair of stored depth dumps (E489's recompute).
fn kind_zls_store(v: &Json, ctx: &Ctx) -> Result<Modelled, String> {
    let i = v.get("init");
    let (w, h, g) = (u(i.get("w")), u(i.get("h")), u(i.get("g")));
    let ax = crate::data::dwords(&file(ctx, i.get("x"))?);
    let ay = crate::data::dwords(&file(ctx, i.get("y"))?);
    let c = zls::check_store(w, h, g, &ax, &ay);
    let e = v.get("expect");
    let mut seen = Seen { matched: c.at_rule, mismatched: c.other, ..Seen::default() };
    // pixels past the target: what the store holds there is open (Q122); the overflowed jobs'
    // zero tiles and the background tiles after them are Q107's
    if c.background_outside + c.at_rule_outside > 0 {
        seen.refused.insert("Q122".into(), c.background_outside + c.at_rule_outside);
    }
    if c.zero + c.background_tiles > 0 {
        seen.refused.insert("Q107".into(), c.zero + c.background_tiles);
    }
    let mut bad = |what: &str| {
        seen.mismatched += 1;
        seen.notes.push(what.to_string());
    };
    if !c.slots_equal {
        bad("the slots touched are not the rule's");
    }
    if let Some(n) = e.get("stored").num()
        && n as u64 != c.stored
    {
        bad("dwords stored differ from the vector");
    }
    if let (Some((ok, nb)), Some(want)) = (c.back, e.get("back_ok").num())
        && (nb != 0 || want as u64 != ok)
    {
        bad("the pixel-to-address walk differs");
    }
    Ok(Modelled { outcome: zls::STORE_STATUS.outcome(), seen })
}

/// te-region: the E542 region test over a job's primitives and the tiles the TA listed.
fn kind_te_region(v: &Json) -> Result<Modelled, String> {
    let i = v.get("init");
    let (w, h) = (u(i.get("w")), u(i.get("h")));
    let tris: Vec<ta::Tri> = i
        .get("prims")
        .arr()
        .iter()
        .map(|t| {
            let p = |k: usize| {
                (t.arr()[k].arr()[0].num().unwrap_or(0.0), t.arr()[k].arr()[1].num().unwrap_or(0.0))
            };
            [p(0), p(1), p(2)]
        })
        .collect();
    // observed: tile (x0, y0) -> "any" or the primitives listed
    let mut obs = BTreeMap::<(u32, u32), Option<Vec<usize>>>::new();
    for t in v.get("expect").get("listed").arr() {
        let a = t.arr();
        let list = match &a[2] {
            Json::Str(_) => None,
            l => Some(l.arr().iter().map(|n| n.num().unwrap_or(0.0) as usize).collect()),
        };
        obs.insert((u(&a[0]), u(&a[1])), list);
    }
    let (mut pairs, mut mism, mut weak) = (0u64, 0u64, 0u64);
    for y0 in (0..h).step_by(16) {
        for x0 in (0..w).step_by(16) {
            let pred: Vec<usize> =
                (0..tris.len()).filter(|&p| ta::tile_lists(&tris[p], x0 as f64, y0 as f64)).collect();
            pairs += tris.len() as u64;
            mism += match obs.get(&(x0, y0)) {
                None => pred.len() as u64,
                Some(None) => {
                    weak += tris.len() as u64;
                    pred.is_empty() as u64
                }
                Some(Some(o)) => {
                    (pred.iter().filter(|p| !o.contains(p)).count()
                        + o.iter().filter(|p| !pred.contains(p)).count()) as u64
                }
            };
        }
    }
    Ok(Modelled {
        outcome: crate::rules::TA_REGION_TEST.outcome(),
        seen: Seen { matched: pairs - mism.min(pairs), mismatched: mism, weak, ..Seen::default() },
    })
}

/// ta-object: the E541 vertex layout for an input, or the hang or fault the record measured.
fn kind_ta_object(v: &Json) -> Modelled {
    let (i, e) = (v.get("init"), v.get("expect"));
    match ta::object_layout(u(i.get("n")), u(i.get("sizes")), u(i.get("fmts"))) {
        Err(o) => Modelled::refusing(o),
        Ok(l) => {
            let mut seen = Seen::default();
            let masks: Vec<u32> = e.get("masks").arr().iter().map(u).collect();
            let same = e.get("stored").num().map(|n| n as u32) == Some(l.stored)
                && e.get("iterated").num().map(|n| n as u32) == Some(l.iterated)
                && e.get("format_hi").hex() == Some(l.format_hi as u64)
                && masks == l.masks;
            if same {
                seen.matched = 1;
            } else if matches!(e.get("outcome").str(), None | Some("ok")) {
                seen.mismatched = 1;
                seen.notes.push(format!("{} differs: {l:?}", v.get("id").str().unwrap_or("")));
            }
            Modelled { outcome: crate::rules::TA_OBJECT_FORMAT.outcome(), seen }
        }
    }
}

/// pbe-emit (E031, E268): the value the end-of-tile emit stores for each shader colour in a pack
/// mode of 0 to 3. A vector without a sideband is the stub's (the whole unit refuses).
fn kind_pbe_emit(v: &Json) -> Modelled {
    let (i, e) = (v.get("init"), v.get("expect"));
    let Some(sb) = i.get("sideband").hex() else { return Modelled::refusing(pbe::refuse()) };
    let reg = i.get("reg0400").hex().unwrap_or(0x80) as u32;
    let pack = match pbe::pack_of(sb as u32) {
        Ok(p) => p,
        Err(o) => return Modelled::refusing(o),
    };
    let mut seen = Seen::default();
    let want: Vec<Option<u64>> = e.get("stored").arr().iter().map(|j| j.hex()).collect();
    for (k, c) in i.get("colours").arr().iter().enumerate() {
        let o0 = c.hex().unwrap_or(0) as u32;
        if pack == pbe::Pack::Rgb565 && !pbe::rgb565_known(o0) {
            return Modelled::refusing(pbe::rgb565_unknown());
        }
        let got = pbe::pack_pixel(pack, o0, reg >> 25 & 1 != 0) as u64;
        if want.get(k).copied().flatten() == Some(got) {
            seen.matched += 1;
        } else {
            seen.mismatched += 1;
            seen.notes.push(format!("colour {k} stored {got:#x}"));
        }
    }
    Modelled { outcome: crate::Outcome::Ok, seen }
}

/// isp-tile (the multisample window, E503): tiles of a pair of position dumps against the rule.
fn kind_isp_tile(v: &Json, ctx: &Ctx) -> Result<Modelled, String> {
    let i = v.get("init");
    let (mode, te) = (u(i.get("mode")), i.get("te_aa").hex().unwrap_or(0) as u32);
    let parse =
        |j: &Json| -> Result<_, String> { Ok(isp::parse_rows(&String::from_utf8_lossy(&file(ctx, j)?))) };
    let (x, y) = (parse(i.get("x"))?, parse(i.get("y"))?);
    match isp::check_windows(mode, te, &x, &y) {
        Err(o) => Ok(Modelled::refusing(o)),
        Ok(c) => {
            let mut seen = Seen { matched: c.equal_full, mismatched: c.tiles - c.equal, ..Seen::default() };
            if c.equal > c.equal_full {
                seen.refused.insert("Q141".into(), c.equal - c.equal_full);
            }
            Ok(Modelled { outcome: crate::rules::ISP_MSAA_WINDOW.outcome(), seen })
        }
    }
}

pub fn unit_of(task: &str) -> &str {
    match task {
        "zls-store" | "zls-load" => "zls",
        "te-region" | "ta-object" => "ta",
        "isp-tile" => "isp",
        "pbe-emit" => "pbe",
        "vdm-stream" => "vdm",
        "bif-walk" => "bif",
        _ => "other",
    }
}

/// Replay one unit vector with a model function (tests inject one).
pub fn replay_with(
    v: &Json,
    ctx: &Ctx,
    model: &dyn Fn(&str, &Json, &Ctx) -> Result<Modelled, String>, // (task, the whole vector, data)
) -> Result<Replayed, String> {
    let task = v.get("init").get("task").str().ok_or("no init.task")?.to_string();
    let m = model(&task, v, ctx)?;
    Ok(Replayed {
        id: v.get("id").str().unwrap_or("").to_string(),
        unit: unit_of(&task).to_string(),
        verdict: judge(v.get("expect"), &m),
        task,
        seen: m.seen,
    })
}

pub fn replay(v: &Json, ctx: &Ctx) -> Result<Replayed, String> {
    replay_with(v, ctx, &model)
}

#[cfg(test)]
mod tests {
    use super::*;
    use sgx_sim::json::parse;

    fn m(outcome: Outcome, matched: u64, mismatched: u64) -> Modelled {
        Modelled { outcome, seen: Seen { matched, mismatched, ..Seen::default() } }
    }

    fn fitted() -> Outcome {
        Outcome::Fitted { record: "E000".into() }
    }

    #[test]
    fn equal_counts_by_a_measured_rule_are_matched() {
        let e = parse(r#"{"matched": 10}"#);
        assert_eq!(judge(&e, &m(Outcome::Ok, 10, 0)), Verdict::Matched);
    }

    #[test]
    fn the_same_counts_by_a_fitted_rule_are_fitted_never_matched() {
        let e = parse(r#"{"matched": 10}"#);
        assert_eq!(judge(&e, &m(fitted(), 10, 0)), Verdict::Fitted);
    }

    #[test]
    fn a_count_or_a_mismatched_item_is_a_mismatch_even_for_a_fitted_rule() {
        let e = parse(r#"{"matched": 10}"#);
        assert!(matches!(judge(&e, &m(Outcome::Ok, 9, 0)), Verdict::Mismatch(_)));
        assert!(matches!(judge(&e, &m(Outcome::Ok, 10, 1)), Verdict::Mismatch(_)));
        assert!(matches!(judge(&e, &m(fitted(), 9, 1)), Verdict::Mismatch(_)));
    }

    #[test]
    fn refused_items_must_equal_the_vectors_by_question() {
        let e = parse(r#"{"matched": 8, "refused": {"Q107": 2}}"#);
        let mut got = m(Outcome::Ok, 8, 0);
        got.seen.refused.insert("Q107".into(), 2);
        assert_eq!(judge(&e, &got), Verdict::Matched);
        got.seen.refused.insert("Q107".into(), 3);
        assert!(matches!(judge(&e, &got), Verdict::Mismatch(_)));
        let mut other = m(Outcome::Ok, 8, 0);
        other.seen.refused.insert("Q122".into(), 2);
        assert!(matches!(judge(&e, &other), Verdict::Mismatch(_)));
    }

    #[test]
    fn a_refusal_the_vector_expects_is_refused_and_one_it_does_not_is_unsupported() {
        let e = parse(r#"{"refuse": ["Q165", "Q070"]}"#);
        let r = Modelled::refusing(Outcome::unsupported("x", &["Q165"]));
        assert_eq!(judge(&e, &r), Verdict::Refused(vec!["Q165".into()]));
        let r = Modelled::refusing(Outcome::unsupported("x", &["Q165", "Q999"]));
        assert!(matches!(judge(&e, &r), Verdict::Unsupported(_)));
        assert!(matches!(judge(&parse("{}"), &r), Verdict::Unsupported(_)));
    }

    #[test]
    fn a_predicted_hang_or_fault_matches_a_recorded_one() {
        let hang = parse(r#"{"outcome": "hang"}"#);
        let fault = parse(r#"{"outcome": "fault", "addr": "0x1000"}"#);
        let h = Modelled::refusing(Outcome::Hang { record: "E519".into() });
        assert_eq!(judge(&hang, &h), Verdict::PredictedHang);
        let f = Modelled::refusing(Outcome::Fault { addr: 0x1000, record: "E021".into() });
        assert_eq!(judge(&fault, &f), Verdict::PredictedFault);
        let g = Modelled::refusing(Outcome::Fault { addr: 0x2000, record: "E021".into() });
        assert!(matches!(judge(&fault, &g), Verdict::Mismatch(_)));
        assert!(matches!(judge(&hang, &f), Verdict::Mismatch(_)));
        assert!(
            matches!(judge(&hang, &m(Outcome::Ok, 1, 0)), Verdict::Mismatch(_)),
            "computed where it hung"
        );
        assert!(
            matches!(judge(&parse(r#"{"matched": 1}"#), &h), Verdict::Mismatch(_)),
            "predicted a hang that did not happen"
        );
    }

    #[test]
    fn a_hang_the_model_cannot_predict_is_unsupported_or_refused_not_a_match() {
        let hang = parse(r#"{"outcome": "hang"}"#);
        let r = Modelled::refusing(Outcome::unsupported("x", &["Q163"]));
        assert!(matches!(judge(&hang, &r), Verdict::Unsupported(_)));
        let hang = parse(r#"{"outcome": "hang", "refuse": ["Q163"]}"#);
        assert_eq!(judge(&hang, &r), Verdict::Refused(vec!["Q163".into()]));
    }

    #[test]
    fn a_non_repeatable_outcome_lists_either_of_these() {
        let e = parse(r#"{"outcome": "either", "either": [{"outcome": "hang"}, {"matched": 3}]}"#);
        let h = Modelled::refusing(Outcome::Hang { record: "Q163".into() });
        assert_eq!(judge(&e, &h), Verdict::Either);
        assert_eq!(judge(&e, &m(Outcome::Ok, 3, 0)), Verdict::Either);
        assert!(matches!(judge(&e, &m(Outcome::Ok, 4, 0)), Verdict::Mismatch(_)));
        // a fitted rule that gives one of the alternatives is fitted, not either
        assert_eq!(judge(&e, &m(fitted(), 3, 0)), Verdict::Fitted);
    }

    #[test]
    fn an_either_needs_two_alternatives_that_each_check_something() {
        let h = Modelled::refusing(Outcome::Hang { record: "Q163".into() });
        for bad in [
            r#"{"outcome": "either", "either": [{}]}"#,
            r#"{"outcome": "either", "either": [{"outcome": "hang"}]}"#,
            r#"{"outcome": "either", "either": [{"outcome": "hang"}, {}]}"#,
            r#"{"outcome": "either"}"#,
        ] {
            assert!(matches!(judge(&parse(bad), &h), Verdict::Mismatch(_)), "{bad}");
            assert!(matches!(judge(&parse(bad), &m(Outcome::Ok, 3, 0)), Verdict::Mismatch(_)), "{bad}");
        }
    }

    #[test]
    fn an_expect_that_compares_nothing_is_not_a_match() {
        assert!(matches!(judge(&parse("{}"), &m(Outcome::Ok, 0, 0)), Verdict::Mismatch(_)));
        assert!(matches!(judge(&parse("{}"), &m(fitted(), 5, 0)), Verdict::Mismatch(_)));
        assert!(matches!(judge(&Json::Null, &m(Outcome::Ok, 5, 0)), Verdict::Mismatch(_)));
    }

    #[test]
    fn near_results_are_near() {
        let e = parse(r#"{"matched": 2}"#);
        assert_eq!(judge(&e, &m(Outcome::Near { ulps: 1 }, 2, 0)), Verdict::Near);
    }

    #[test]
    fn replay_runs_the_injected_model_and_names_the_unit() {
        let v = parse(r#"{"id": "t", "init": {"task": "zls-store"}, "expect": {"matched": 1}}"#);
        let ctx = Ctx { root: None, units: None, scenes: None };
        let r = replay_with(&v, &ctx, &|_, _, _| Ok(m(fitted(), 1, 0))).unwrap();
        assert_eq!((r.unit.as_str(), r.verdict), ("zls", Verdict::Fitted));
        assert!(replay_with(&parse(r#"{"init": {}}"#), &ctx, &|_, _, _| unreachable!()).is_err());
        assert!(replay(&v, &ctx).is_err(), "a kind with no model is not a silent pass");
    }
}
