// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! What a unit model says (`Outcome`) and how that compares with the hardware (`Verdict`).
//!
//! Three results are never blurred (the firm rule of phase 12): matched, fitted (a rule a
//! record states as a fit), unsupported; the fourth is a predicted hang or fault. A result
//! that depends on a fitted rule is fitted downstream, whatever else it was built from
//! ([`Verdict::combine`]).

use std::collections::BTreeMap;

/// What a unit model returns for an input.
#[derive(Debug, Clone, PartialEq)]
pub enum Outcome {
    /// computed from a measured rule
    Ok,
    /// computed, equal only within a recorded bound
    Near { ulps: u32 },
    /// computed from a rule a record states as a fit (`record` names it)
    Fitted { record: String },
    /// the hardware hangs on this input (a record says so)
    Hang { record: String },
    /// the hardware faults on this input
    Fault { addr: u32, record: String },
    /// no record settles this input: the model refuses, naming the open questions
    Unsupported { why: String, ids: Vec<String> },
}

impl Outcome {
    pub fn unsupported(why: &str, ids: &[&str]) -> Outcome {
        Outcome::Unsupported { why: why.to_string(), ids: ids.iter().map(|s| s.to_string()).collect() }
    }
}

/// How a replay of one vector ended, against the hardware's recorded result.
#[derive(Debug, Clone, PartialEq)]
pub enum Verdict {
    /// the model's result equals the hardware's, by a measured rule
    Matched,
    /// the hardware's result is non-repeatable (`expect.either`) and the model gave one of them
    Either,
    PredictedHang,
    PredictedFault,
    /// equal within a recorded bound
    Near,
    /// equal by a rule a record states as a fit: reported apart, never as matched
    Fitted,
    /// the model refused, and the vector names that question as open (`expect.refuse`)
    Refused(Vec<String>),
    /// the model refused, and the vector did not expect it
    Unsupported(String),
    /// the model's result differs from the hardware's
    Mismatch(String),
}

impl Verdict {
    fn rank(&self) -> u8 {
        match self {
            Verdict::Matched => 0,
            Verdict::Either => 1,
            Verdict::PredictedHang | Verdict::PredictedFault => 2,
            Verdict::Near => 3,
            Verdict::Fitted => 4,
            Verdict::Refused(_) => 5,
            Verdict::Unsupported(_) => 6,
            Verdict::Mismatch(_) => 7,
        }
    }

    /// The verdict of a result built from two dependent results: the weaker of the two. A
    /// matched result with a fitted one is fitted, a near one is near; a refusal or a mismatch
    /// anywhere is the whole result's.
    pub fn combine(self, other: Verdict) -> Verdict {
        if other.rank() > self.rank() { other } else { self }
    }

    /// Counts as a match for the gate (D5: zero mismatches; a predicted hang is a match).
    /// A fitted verdict does not: it is reported apart.
    pub fn is_match(&self) -> bool {
        matches!(self, Verdict::Matched | Verdict::Either | Verdict::PredictedHang | Verdict::PredictedFault)
    }
}

/// Counts of verdicts, one line of the coverage report.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Counts {
    pub matched: u64,
    pub either: u64,
    pub hang: u64,
    pub fault: u64,
    pub near: u64,
    pub fitted: u64,
    pub refused: BTreeMap<String, u64>,
    /// vectors refused (each once, whatever the number of questions it names)
    pub refused_vectors: u64,
    pub unsupported: u64,
    pub mismatch: u64,
    /// matched vectors that compared no item: counted here, never as matched
    pub empty: u64,
}

impl Counts {
    pub fn add(&mut self, v: &Verdict) {
        match v {
            Verdict::Matched => self.matched += 1,
            Verdict::Either => self.either += 1,
            Verdict::PredictedHang => self.hang += 1,
            Verdict::PredictedFault => self.fault += 1,
            Verdict::Near => self.near += 1,
            Verdict::Fitted => self.fitted += 1,
            Verdict::Refused(ids) => {
                self.refused_vectors += 1;
                for id in ids {
                    *self.refused.entry(id.clone()).or_default() += 1;
                }
            }
            Verdict::Unsupported(_) => self.unsupported += 1,
            Verdict::Mismatch(_) => self.mismatch += 1,
        }
    }

    pub fn total(&self) -> u64 {
        self.matched
            + self.either
            + self.hang
            + self.fault
            + self.near
            + self.fitted
            + self.unsupported
            + self.mismatch
            + self.empty
            + self.refused_vectors
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_result_built_on_a_fitted_one_is_never_matched() {
        assert_eq!(Verdict::Matched.combine(Verdict::Fitted), Verdict::Fitted);
        assert_eq!(Verdict::Fitted.combine(Verdict::Matched), Verdict::Fitted);
        assert_eq!(Verdict::Either.combine(Verdict::Fitted), Verdict::Fitted);
        assert_eq!(Verdict::PredictedHang.combine(Verdict::Fitted), Verdict::Fitted);
        assert_eq!(Verdict::Near.combine(Verdict::Fitted), Verdict::Fitted);
        assert!(!Verdict::Matched.combine(Verdict::Fitted).is_match());
    }

    #[test]
    fn combine_is_the_weaker_verdict_and_order_free() {
        let all = [
            Verdict::Matched,
            Verdict::Either,
            Verdict::PredictedHang,
            Verdict::Near,
            Verdict::Fitted,
            Verdict::Refused(vec!["Q1".into()]),
            Verdict::Unsupported("x".into()),
            Verdict::Mismatch("y".into()),
        ];
        for a in &all {
            for b in &all {
                let (ab, ba) = (a.clone().combine(b.clone()), b.clone().combine(a.clone()));
                assert_eq!(std::mem::discriminant(&ab), std::mem::discriminant(&ba));
                assert!(ab.rank() >= a.rank() && ab.rank() >= b.rank());
            }
        }
        assert!(matches!(Verdict::Matched.combine(Verdict::Mismatch("m".into())), Verdict::Mismatch(_)));
        assert!(matches!(Verdict::Matched.combine(Verdict::Refused(vec![])), Verdict::Refused(_)));
    }

    #[test]
    fn only_matched_like_verdicts_count_as_matches() {
        assert!(Verdict::Matched.is_match());
        assert!(Verdict::Either.is_match());
        assert!(Verdict::PredictedHang.is_match());
        assert!(Verdict::PredictedFault.is_match());
        assert!(!Verdict::Fitted.is_match());
        assert!(!Verdict::Near.is_match());
        assert!(!Verdict::Refused(vec![]).is_match());
    }

    #[test]
    fn counts_keep_fitted_apart_and_refusals_by_question() {
        let mut c = Counts::default();
        c.add(&Verdict::Matched);
        c.add(&Verdict::Fitted);
        c.add(&Verdict::Fitted);
        c.add(&Verdict::Refused(vec!["Q165".into()]));
        c.add(&Verdict::Refused(vec!["Q165".into(), "Q299".into()]));
        assert_eq!((c.matched, c.fitted), (1, 2));
        assert_eq!(c.refused["Q165"], 2);
        assert_eq!(c.refused["Q299"], 1);
        assert_eq!(c.total(), 5, "a refused vector counts once");
    }
}
