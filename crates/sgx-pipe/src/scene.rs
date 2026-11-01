// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Scene vectors (doc/specs/vectors.md section 6): the whole job as the hardware ran it, and
//! the comparer of a simulated job's result with the recorded one.
//!
//! `"format": "sgx545-scene-vectors"`, version 1, one file per run of the scenes it lists. A
//! scene's `regs` and `memory` are what the kick submitted; `expect` is what the host read
//! back. The comparer shares [`crate::unitvec::judge_one`]'s classification, so a scene whose
//! result rests on a fitted rule is `Fitted`, never `Matched` (D6), and a non-repeatable
//! hardware outcome is `expect.outcome = "either"` (D5).

use crate::outcome::{Outcome, Verdict};
use crate::unitvec::{Modelled, Seen, judge_one};
use sgx_sim::json::Json;
use std::collections::BTreeMap;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Kind {
    Render,
    Transfer,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Target {
    pub w: u32,
    pub h: u32,
    pub format: String,
    pub base: u32,
}

/// A run of device memory the job reads.
#[derive(Debug, Clone, PartialEq)]
pub struct Segment {
    pub base: u32,
    /// the dwords, inline, or the file (relative to the data repository) and its sha256
    pub dwords: Option<Vec<u32>>,
    pub file: Option<(String, String)>,
    /// `recorded` (captured at submission by the run itself) or `rebuilt` (D4: offline)
    pub source: String,
}

#[derive(Debug, Clone)]
pub struct Scene {
    pub id: String,
    pub kind: Kind,
    pub target: Target,
    pub regs: Vec<(u32, u32)>,
    /// the host's register writes in order, where order matters
    pub regs_log: Vec<(u32, u32)>,
    pub memory: Vec<Segment>,
    pub expect: Json,
    pub provenance: Json,
}

fn hex(j: &Json) -> Option<u32> {
    j.hex().map(|v| v as u32)
}

impl Scene {
    pub fn parse(s: &Json) -> Result<Scene, String> {
        let id = s.get("id").str().ok_or("scene without id")?.to_string();
        const KEYS: &[&str] = &["id", "kind", "target", "regs", "regs_log", "memory", "expect", "provenance"];
        for (k, _) in s.obj() {
            if k == "vm" {
                return Err(format!("{id}: a `vm` is not modelled before 12.5 (memory is flat): refused"));
            }
            if !KEYS.contains(&k.as_str()) {
                return Err(format!("{id}: unknown key `{k}`"));
            }
        }
        for (k, _) in s.get("target").obj() {
            if !["w", "h", "format", "base"].contains(&k.as_str()) {
                return Err(format!("{id}: unknown target key `{k}`"));
            }
        }
        let kind = match s.get("kind").str() {
            Some("render") => Kind::Render,
            Some("transfer") => Kind::Transfer,
            k => return Err(format!("{id}: unknown scene kind {k:?}")),
        };
        let t = s.get("target");
        let target = Target {
            w: t.get("w").num().ok_or(format!("{id}: no target.w"))? as u32,
            h: t.get("h").num().ok_or(format!("{id}: no target.h"))? as u32,
            format: t.get("format").str().unwrap_or("").to_string(),
            base: hex(t.get("base")).unwrap_or(0),
        };
        let mut regs = vec![];
        for (k, v) in s.get("regs").obj() {
            let off = u32::from_str_radix(k.trim_start_matches("0x"), 16)
                .map_err(|_| format!("{id}: register {k}"))?;
            regs.push((off, hex(v).ok_or(format!("{id}: value of {k}"))?));
        }
        let mut regs_log = vec![];
        for w in s.get("regs_log").arr() {
            let a = w.arr();
            let off = a.first().and_then(hex).ok_or(format!("{id}: regs_log offset"))?;
            regs_log.push((off, a.get(1).and_then(hex).ok_or(format!("{id}: regs_log value"))?));
        }
        let mut memory = vec![];
        for m in s.get("memory").arr() {
            let base = hex(m.get("base")).ok_or(format!("{id}: memory without base"))?;
            let dwords = match m.get("dwords") {
                Json::Arr(a) => Some(
                    a.iter().map(|d| hex(d).ok_or(format!("{id}: dword"))).collect::<Result<Vec<_>, _>>()?,
                ),
                _ => None,
            };
            let file =
                m.get("file").str().map(|f| (f.to_string(), m.get("sha256").str().unwrap_or("").to_string()));
            if dwords.is_none() && file.is_none() {
                return Err(format!("{id}: memory at {base:#x} has neither dwords nor file"));
            }
            let source = m.get("source").str().unwrap_or("rebuilt").to_string();
            memory.push(Segment { base, dwords, file, source });
        }
        Ok(Scene {
            id,
            kind,
            target,
            regs,
            regs_log,
            memory,
            expect: s.get("expect").clone(),
            provenance: s.get("provenance").clone(),
        })
    }
}

/// What a simulated job produced, in the shape of `expect`.
#[derive(Debug, Clone, PartialEq)]
pub struct SceneResult {
    pub outcome: Outcome,
    pub image: Option<Vec<u32>>,
    /// name -> sparse dwords by byte address
    pub buffers: BTreeMap<String, BTreeMap<u32, u32>>,
    pub regs: BTreeMap<u32, u32>,
    pub counters: BTreeMap<String, Vec<u32>>,
    /// the fitted rules (records) the result rests on: a result with any is never matched
    pub fitted: Vec<String>,
}

impl SceneResult {
    /// Record that the result used a rule (D6): a fitted one marks the whole result fitted. A
    /// model calls this for every rule it applies, so the mark follows from the units used and
    /// not from a convention.
    pub fn use_rule(&mut self, st: crate::rules::Status) {
        if let crate::rules::Status::Fitted(r) = st
            && !self.fitted.iter().any(|f| f == r)
        {
            self.fitted.push(r.to_string());
        }
    }

    pub fn refusing(o: Outcome) -> SceneResult {
        SceneResult {
            outcome: o,
            image: None,
            buffers: BTreeMap::new(),
            regs: BTreeMap::new(),
            counters: BTreeMap::new(),
            fitted: vec![],
        }
    }
}

/// Compare the items of one alternative of `expect` with the result.
fn seen(expect: &Json, r: &SceneResult, near_used: &mut Option<u32>) -> Seen {
    let mut s = Seen::default();
    let mut item = |ok: bool, what: String| {
        if ok {
            s.matched += 1;
        } else {
            s.mismatched += 1;
            s.notes.push(what);
        }
    };
    let img = expect.get("image");
    if !matches!(img, Json::Null) {
        let near = img.get("near").num().map(|n| n as u32);
        match (&r.image, img.get("pixels"), img.get("mixed"), img.get("o0")) {
            (None, _, _, _) => item(false, "no image".into()),
            (Some(got), Json::Arr(px), _, _) => {
                for (i, e) in px.iter().enumerate() {
                    let e = e.hex().unwrap_or(0) as u32;
                    let g = got.get(i).copied();
                    let ok = g == Some(e);
                    let within = !ok
                        && near.is_some_and(|n| {
                            g.is_some_and(|g| {
                                (0..4).all(|c| ((g >> (8 * c)) & 255).abs_diff((e >> (8 * c)) & 255) <= n)
                            })
                        });
                    if within {
                        *near_used = near;
                    }
                    item(ok || within, format!("pixel {i}"));
                }
                item(got.len() == px.len(), "image size".into());
            }
            (Some(got), _, Json::Arr(m), _) => {
                let mut have = BTreeMap::<u32, u64>::new();
                for &p in got {
                    *have.entry(p).or_default() += 1;
                }
                let want: BTreeMap<u32, u64> = m
                    .iter()
                    .map(|c| (hex(&c.arr()[0]).unwrap_or(0), c.arr()[1].num().unwrap_or(0.0) as u64))
                    .collect();
                item(have == want, "pixel value counts".into());
            }
            (Some(got), _, _, o0) if o0.hex().is_some() => {
                let e = o0.hex().unwrap() as u32;
                item(!got.is_empty() && got.iter().all(|&p| p == e), "uniform o0".into());
            }
            _ => item(false, "image expectation not understood".into()),
        }
    }
    for (name, b) in expect.get("buffers").obj() {
        let have = r.buffers.get(name);
        let mut want = BTreeMap::new();
        for (a, v) in b.get("sparse").obj() {
            want.insert(
                u32::from_str_radix(a.trim_start_matches("0x"), 16).unwrap_or(0),
                hex(v).unwrap_or(0),
            );
        }
        for (i, d) in b.get("dwords").arr().iter().enumerate() {
            want.insert(4 * i as u32, hex(d).unwrap_or(0));
        }
        for (a, v) in want {
            item(have.and_then(|h| h.get(&a)) == Some(&v), format!("{name}[{a:#x}]"));
        }
    }
    for (k, v) in expect.get("regs").obj() {
        let off = u32::from_str_radix(k.trim_start_matches("0x"), 16).unwrap_or(0);
        item(r.regs.get(&off).copied() == hex(v), format!("register {k}"));
    }
    for (k, v) in expect.get("counters").obj() {
        let want: Vec<u32> = v.arr().iter().filter_map(hex).collect();
        item(r.counters.get(k) == Some(&want), format!("counter {k}"));
    }
    s
}

/// The verdict of a simulated job against a scene's `expect`. A result that rests on a fitted
/// rule (`r.fitted`) is `Fitted` whatever it would have been (matched, near, a predicted hang or
/// fault, either); a mismatch, a refusal and an unsupported stay what they are (D6).
pub fn compare(expect: &Json, r: &SceneResult) -> Verdict {
    let refuse: Vec<String> =
        expect.get("refuse").arr().iter().filter_map(|s| s.str().map(str::to_string)).collect();
    let one = |alt: &Json| {
        let mut near = None;
        let s = seen(alt, r, &mut near);
        let o = match (&r.outcome, near) {
            (Outcome::Ok, Some(n)) => Outcome::Near { ulps: n },
            (o, _) => o.clone(),
        };
        let computed =
            !matches!(o, Outcome::Unsupported { .. } | Outcome::Hang { .. } | Outcome::Fault { .. });
        if computed && alt.get("outcome").str().is_none() && s.matched + s.mismatched == 0 {
            return Verdict::Mismatch("the scene's expect compares nothing".into());
        }
        judge_one(alt, &refuse, &Modelled { outcome: o, seen: s })
    };
    let v = if expect.get("outcome").str() != Some("either") {
        one(expect)
    } else {
        let alts = expect.get("either").arr();
        if alts.len() < 2 || alts.iter().any(crate::unitvec::is_empty) {
            return Verdict::Mismatch(
                "a malformed either: it needs two or more alternatives that each check something".into(),
            );
        }
        let vs: Vec<Verdict> = alts.iter().map(one).collect();
        if vs.iter().any(Verdict::is_match) {
            Verdict::Either
        } else if let Some(v) = vs.iter().find(|v| !matches!(v, Verdict::Mismatch(_))) {
            v.clone()
        } else {
            Verdict::Mismatch(format!("none of the recorded outcomes: {vs:?}"))
        }
    };
    match v {
        Verdict::Matched
        | Verdict::Either
        | Verdict::PredictedHang
        | Verdict::PredictedFault
        | Verdict::Near
            if !r.fitted.is_empty() =>
        {
            Verdict::Fitted
        }
        v => v,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sgx_sim::json::parse;

    fn ok(image: Vec<u32>) -> SceneResult {
        let mut r = SceneResult::refusing(Outcome::Ok);
        r.image = Some(image);
        r
    }

    #[test]
    fn a_scene_parses_its_registers_memory_and_target() {
        let j = parse(
            r#"{"id": "s1", "kind": "transfer", "target": {"w": 64, "h": 32, "format": "ARGB8888", "base": "0x10000000"},
                "regs": {"0x0420": "0x1234"},
                "memory": [{"base": "0x20000000", "dwords": ["0x1", "0x2"], "source": "recorded"},
                           {"base": "0x30000000", "file": "x.bin", "sha256": "ab"}],
                "expect": {"image": {"o0": "0xff00ff00"}}}"#,
        );
        let s = Scene::parse(&j).unwrap();
        assert_eq!(
            (s.id.as_str(), s.kind, s.target.w, s.target.base),
            ("s1", Kind::Transfer, 64, 0x1000_0000)
        );
        assert_eq!(s.regs, [(0x420, 0x1234)]);
        assert_eq!(s.memory[0].dwords, Some(vec![1, 2]));
        assert_eq!(s.memory[0].source, "recorded");
        assert_eq!(s.memory[1].file, Some(("x.bin".into(), "ab".into())));
        assert_eq!(s.memory[1].source, "rebuilt", "a segment is rebuilt unless the run recorded it");
    }

    #[test]
    fn unknown_keys_and_the_unparsed_vm_are_errors_not_silently_ignored() {
        let base = |extra: &str| {
            parse(&format!(r#"{{"id": "a", "kind": "render", "target": {{"w": 1, "h": 1}}{extra}}}"#))
        };
        assert!(Scene::parse(&base("")).is_ok());
        let e = Scene::parse(&base(r#", "frobnicate": 1"#)).unwrap_err();
        assert!(e.contains("frobnicate"), "{e}");
        // a vm would run as flat memory: refused until 12.5 models it
        let e = Scene::parse(&base(r#", "vm": {"lists": []}"#)).unwrap_err();
        assert!(e.contains("vm"), "{e}");
        // regs_log is parsed (kept in order); an unknown target key is an error too
        assert!(Scene::parse(&base(r#", "regs_log": [["0x0420", "0x1"]]"#)).is_ok());
        let t = parse(r#"{"id": "a", "kind": "render", "target": {"w": 1, "h": 1, "colour": 2}}"#);
        assert!(Scene::parse(&t).unwrap_err().contains("colour"));
    }

    #[test]
    fn a_malformed_scene_is_an_error() {
        assert!(Scene::parse(&parse(r#"{"kind": "render"}"#)).is_err());
        assert!(Scene::parse(&parse(r#"{"id": "a", "kind": "blit", "target": {"w": 1, "h": 1}}"#)).is_err());
        let no_data =
            r#"{"id": "a", "kind": "render", "target": {"w": 1, "h": 1}, "memory": [{"base": "0x0"}]}"#;
        assert!(Scene::parse(&parse(no_data)).is_err());
    }

    #[test]
    fn an_exact_image_is_matched_and_one_wrong_pixel_is_a_mismatch() {
        let e = parse(r#"{"image": {"pixels": ["0x1", "0x2", "0x3"]}}"#);
        assert_eq!(compare(&e, &ok(vec![1, 2, 3])), Verdict::Matched);
        assert!(matches!(compare(&e, &ok(vec![1, 9, 3])), Verdict::Mismatch(_)));
        assert!(matches!(compare(&e, &ok(vec![1, 2])), Verdict::Mismatch(_)));
        assert!(matches!(compare(&e, &SceneResult::refusing(Outcome::Ok)), Verdict::Mismatch(_)));
    }

    #[test]
    fn a_mixed_image_compares_value_counts_and_a_uniform_one_o0() {
        let e = parse(r#"{"image": {"mixed": [["0xff", 3], ["0x0", 1]]}}"#);
        assert_eq!(compare(&e, &ok(vec![0, 0xff, 0xff, 0xff])), Verdict::Matched);
        assert!(matches!(compare(&e, &ok(vec![0, 0, 0xff, 0xff])), Verdict::Mismatch(_)));
        let e = parse(r#"{"image": {"o0": "0xff00ff00"}}"#);
        assert_eq!(compare(&e, &ok(vec![0xff00ff00; 4])), Verdict::Matched);
    }

    #[test]
    fn a_near_image_within_the_bound_is_near_and_beyond_it_a_mismatch() {
        let e = parse(r#"{"image": {"pixels": ["0x10203040"], "near": 1}}"#);
        assert_eq!(compare(&e, &ok(vec![0x10213040])), Verdict::Near);
        assert!(matches!(compare(&e, &ok(vec![0x10223040])), Verdict::Mismatch(_)));
        assert_eq!(compare(&e, &ok(vec![0x10203040])), Verdict::Matched);
    }

    #[test]
    fn buffers_registers_and_counters_are_compared() {
        let e = parse(
            r#"{"buffers": {"depth": {"sparse": {"0x200": "0x3f800000"}}}, "regs": {"0x0100": "0x5"},
                "counters": {"vis": ["0x1", "0x2"]}}"#,
        );
        let mut r = SceneResult::refusing(Outcome::Ok);
        r.buffers.insert("depth".into(), BTreeMap::from([(0x200, 0x3f800000)]));
        r.regs.insert(0x100, 5);
        r.counters.insert("vis".into(), vec![1, 2]);
        assert_eq!(compare(&e, &r), Verdict::Matched);
        r.regs.insert(0x100, 6);
        assert!(matches!(compare(&e, &r), Verdict::Mismatch(_)));
    }

    #[test]
    fn a_result_resting_on_a_fitted_rule_is_fitted_though_every_pixel_is_exact() {
        let e = parse(r#"{"image": {"pixels": ["0x1"]}}"#);
        let mut r = ok(vec![1]);
        r.fitted.push("E503".into());
        assert_eq!(compare(&e, &r), Verdict::Fitted);
        assert!(!compare(&e, &r).is_match());
        // and a fitted result that differs is a mismatch, not hidden by being fitted
        r.image = Some(vec![2]);
        assert!(matches!(compare(&e, &r), Verdict::Mismatch(_)));
    }

    #[test]
    fn near_hang_and_fault_resting_on_a_fitted_rule_are_fitted_never_matched() {
        let mut r = ok(vec![0x10213040]);
        r.fitted.push("E503".into());
        let e = parse(r#"{"image": {"pixels": ["0x10203040"], "near": 1}}"#);
        assert_eq!(compare(&e, &r), Verdict::Fitted);
        let mut h = SceneResult::refusing(Outcome::Hang { record: "E519".into() });
        h.fitted.push("E541".into());
        assert_eq!(compare(&parse(r#"{"outcome": "hang"}"#), &h), Verdict::Fitted);
        let mut f = SceneResult::refusing(Outcome::Fault { addr: 4, record: "E021".into() });
        f.fitted.push("E541".into());
        assert_eq!(compare(&parse(r#"{"outcome": "fault"}"#), &f), Verdict::Fitted);
        // and the fitted hang that the hardware did not give is still a mismatch
        assert!(matches!(compare(&parse(r#"{"outcome": "fault"}"#), &h), Verdict::Mismatch(_)));
        // either with a fitted result stays fitted
        let e = parse(r#"{"outcome": "either", "either": [{"outcome": "hang"}, {"outcome": "fault"}]}"#);
        assert_eq!(compare(&e, &h), Verdict::Fitted);
    }

    #[test]
    fn a_scene_that_compares_nothing_is_not_matched() {
        assert!(matches!(compare(&parse("{}"), &ok(vec![1])), Verdict::Mismatch(_)));
        assert!(matches!(compare(&parse(r#"{"image": {}}"#), &ok(vec![1])), Verdict::Mismatch(_)));
        assert!(matches!(compare(&parse(r#"{"buffers": {}}"#), &ok(vec![1])), Verdict::Mismatch(_)));
    }

    #[test]
    fn fitted_is_derived_from_the_rules_a_result_used() {
        use crate::rules::Status;
        let mut r = ok(vec![1]);
        r.use_rule(Status::Measured);
        assert!(r.fitted.is_empty());
        r.use_rule(Status::Fitted("E503"));
        r.use_rule(Status::Fitted("E503"));
        assert_eq!(r.fitted, ["E503"]);
    }

    #[test]
    fn a_job_refused_by_the_model_is_refused_when_the_vector_names_the_question() {
        let e = parse(r#"{"image": {"o0": "0x0"}, "refuse": ["Q066"]}"#);
        let r = SceneResult::refusing(Outcome::unsupported("bg object", &["Q066"]));
        assert_eq!(compare(&e, &r), Verdict::Refused(vec!["Q066".into()]));
        assert!(matches!(compare(&parse(r#"{"image": {"o0": "0x0"}}"#), &r), Verdict::Unsupported(_)));
    }

    #[test]
    fn a_recorded_hang_is_predicted_and_either_of_two_outcomes_is_either() {
        let e = parse(r#"{"outcome": "hang"}"#);
        assert_eq!(
            compare(&e, &SceneResult::refusing(Outcome::Hang { record: "E519".into() })),
            Verdict::PredictedHang
        );
        let e = parse(r#"{"outcome": "either", "either": [{"outcome": "hang"}, {"image": {"o0": "0x7"}}]}"#);
        assert_eq!(
            compare(&e, &SceneResult::refusing(Outcome::Hang { record: "Q163".into() })),
            Verdict::Either
        );
        assert_eq!(compare(&e, &ok(vec![7, 7])), Verdict::Either);
        assert!(matches!(compare(&e, &ok(vec![8])), Verdict::Mismatch(_)));
    }
}
