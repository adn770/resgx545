// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The coverage report: per unit, how many vectors matched, were fitted, were refused by
//! question, unsupported, predicted hangs or faults, or mismatched. D5: the gate is zero
//! mismatches; there is no percentage gate. D6: fitted is a column of its own.

use crate::outcome::{Counts, Verdict};
use crate::unitvec::Replayed;
use std::collections::BTreeMap;

#[derive(Debug, Default)]
pub struct Report {
    pub units: BTreeMap<String, Counts>,
    /// items (dwords, pairs, tiles) matched and refused by question, per unit: what a vector
    /// counted inside itself
    pub items_matched: BTreeMap<String, u64>,
    /// items of vectors whose result rests on a fitted rule (D6: never counted as matched)
    pub items_fitted: BTreeMap<String, u64>,
    /// of the items matched or fitted, those checked by presence only
    pub items_weak: BTreeMap<String, u64>,
    pub items_refused: BTreeMap<String, BTreeMap<String, u64>>,
    pub skipped: Vec<(String, String)>,
    pub mismatches: Vec<(String, String)>,
}

impl Report {
    pub fn add(&mut self, r: &Replayed) {
        let c = self.units.entry(r.unit.clone()).or_default();
        // a vector that matched with no item compared (a store that wrote nothing, an expectation
        // that names nothing the model checks) is not a match: it is counted empty
        if r.verdict == Verdict::Matched
            && r.seen.matched == 0
            && r.seen.weak == 0
            && r.seen.refused.is_empty()
        {
            c.empty += 1;
        } else {
            c.add(&r.verdict);
        }
        *self.items_weak.entry(r.unit.clone()).or_default() += r.seen.weak;
        let col = if r.verdict == Verdict::Fitted { &mut self.items_fitted } else { &mut self.items_matched };
        *col.entry(r.unit.clone()).or_default() += r.seen.matched;
        for (q, n) in &r.seen.refused {
            *self.items_refused.entry(r.unit.clone()).or_default().entry(q.clone()).or_default() += n;
        }
        if let Verdict::Mismatch(why) = &r.verdict {
            self.mismatches.push((r.id.clone(), why.clone()));
        }
    }

    pub fn skip(&mut self, id: &str, why: &str) {
        self.skipped.push((id.to_string(), why.to_string()));
    }

    /// The gate of D5: no mismatch anywhere.
    pub fn gate(&self) -> bool {
        self.units.values().all(|c| c.mismatch == 0)
    }

    pub fn render(&self) -> String {
        let mut s = String::from(
            "unit  vectors matched either hang fault near fitted unsupported mismatch refused-by-question\n",
        );
        for (u, c) in &self.units {
            let refused: Vec<String> = c.refused.iter().map(|(q, n)| format!("{q}={n}")).collect();
            s += &format!(
                "{u:<5} {:>7} {:>7} {:>6} {:>4} {:>5} {:>4} {:>6} {:>11} {:>8} {}\n",
                c.total(),
                c.matched,
                c.either,
                c.hang,
                c.fault,
                c.near,
                c.fitted,
                c.unsupported,
                c.mismatch,
                refused.join(",")
            );
            if c.empty > 0 {
                s += &format!("      empty, not compared {}\n", c.empty);
            }
            if let Some(n) = self.items_weak.get(u).filter(|n| **n > 0) {
                s += &format!("      of which by presence only {n}\n");
            }
            if let Some(n) = self.items_fitted.get(u).filter(|n| **n > 0) {
                s += &format!("      items fitted {n}\n");
            }
            if let Some(n) = self.items_matched.get(u)
                && *n > 0
            {
                let ir: Vec<String> = self
                    .items_refused
                    .get(u)
                    .into_iter()
                    .flatten()
                    .map(|(q, n)| format!("{q}={n}"))
                    .collect();
                s += &format!("      items matched {n}, items refused {}\n", ir.join(","));
            }
        }
        s
    }
}

/// The verdict of a job whose result is built from its units' results.
pub fn job_verdict(units: &[Verdict]) -> Verdict {
    units.iter().cloned().fold(Verdict::Matched, Verdict::combine)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::unitvec::Seen;

    fn rep(unit: &str, v: Verdict) -> Replayed {
        Replayed {
            id: format!("{unit}-v"),
            unit: unit.into(),
            task: "t".into(),
            verdict: v,
            seen: Seen::default(),
        }
    }

    #[test]
    fn the_report_counts_per_unit_and_keeps_fitted_out_of_matched() {
        let mut r = Report::default();
        r.add(&rep("zls", Verdict::Fitted));
        r.add(&rep("zls", Verdict::Fitted));
        let mut m = rep("ta", Verdict::Matched);
        m.seen.matched = 2; // a matched vector compared items (none: counted empty, below)
        r.add(&m);
        r.add(&rep("ta", Verdict::PredictedHang));
        r.add(&rep("ta", Verdict::Refused(vec!["Q165".into()])));
        assert_eq!((r.units["zls"].matched, r.units["zls"].fitted), (0, 2));
        assert_eq!((r.units["ta"].matched, r.units["ta"].hang), (1, 1));
        assert!(r.gate());
        let text = r.render();
        assert!(text.contains("Q165=1") && text.contains("zls"));
    }

    #[test]
    fn items_of_a_fitted_vector_are_counted_fitted_never_matched() {
        let mut r = Report::default();
        let mut f = rep("zls", Verdict::Fitted);
        f.seen.matched = 100;
        let mut m = rep("zls", Verdict::Matched);
        m.seen.matched = 7;
        r.add(&f);
        r.add(&m);
        assert_eq!(r.items_matched["zls"], 7);
        assert_eq!(r.items_fitted["zls"], 100);
        let t = r.render();
        assert!(t.contains("items matched 7") && t.contains("items fitted 100"), "{t}");
    }

    #[test]
    fn a_matched_vector_that_compared_no_item_is_counted_empty_never_matched() {
        let mut r = Report::default();
        r.add(&rep("zls", Verdict::Matched));
        let mut m = rep("zls", Verdict::Matched);
        m.seen.matched = 3;
        r.add(&m);
        let c = &r.units["zls"];
        assert_eq!((c.matched, c.empty, c.total()), (1, 1, 2));
        assert_eq!(r.items_matched["zls"], 3);
        let t = r.render();
        assert!(t.contains("empty, not compared 1"), "{t}");
        // a refused vector or a predicted hang compares no item and is not empty
        r.add(&rep("ta", Verdict::PredictedHang));
        assert_eq!((r.units["ta"].hang, r.units["ta"].empty), (1, 0));
    }

    #[test]
    fn items_checked_by_presence_only_are_reported_apart() {
        let mut r = Report::default();
        let mut v = rep("ta", Verdict::Fitted);
        (v.seen.matched, v.seen.weak) = (10, 4);
        r.add(&v);
        assert_eq!(r.items_weak["ta"], 4);
        assert!(r.render().contains("by presence only 4"));
    }

    #[test]
    fn a_refused_vector_counts_once_in_the_vectors_column() {
        let mut r = Report::default();
        r.add(&rep("pbe", Verdict::Refused(vec!["Q012".into(), "Q040".into(), "Q302".into()])));
        let line = r.render().lines().nth(1).unwrap().to_string();
        assert!(line.split_whitespace().nth(1) == Some("1"), "{line}");
        assert_eq!(r.units["pbe"].refused_vectors, 1);
    }

    #[test]
    fn one_mismatch_fails_the_gate_and_is_listed_with_its_reason() {
        let mut r = Report::default();
        r.add(&rep("isp", Verdict::Matched));
        assert!(r.gate());
        r.add(&rep("isp", Verdict::Mismatch("tile 3".into())));
        assert!(!r.gate());
        assert_eq!(r.mismatches, [("isp-v".to_string(), "tile 3".to_string())]);
    }

    #[test]
    fn a_job_built_on_one_fitted_unit_is_fitted_not_matched() {
        let all_matched = [Verdict::Matched, Verdict::Either, Verdict::PredictedHang];
        assert_eq!(job_verdict(&all_matched), Verdict::PredictedHang);
        let with_fitted = [Verdict::Matched, Verdict::Fitted, Verdict::Matched];
        assert_eq!(job_verdict(&with_fitted), Verdict::Fitted);
        assert_eq!(job_verdict(&[]), Verdict::Matched);
    }
}
