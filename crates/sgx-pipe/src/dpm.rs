// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! DPM: parameter buffer pool, state page, overflow and partial render (12.7).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q045", "Q036", "Q038", "Q081", "Q103", "Q191", "Q192"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the DPM is not modelled (12.7)", OPEN)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_stub_refuses_and_names_its_questions() {
        match refuse() {
            Outcome::Unsupported { ids, why } => {
                assert!(!ids.is_empty() && !why.is_empty());
                assert_eq!(ids, OPEN);
            }
            o => panic!("{o:?}"),
        }
    }
}
