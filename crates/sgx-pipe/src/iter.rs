// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Iterators and the pixel PDS launch (12.3).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q021", "Q027", "Q093", "Q098", "Q180"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the iterators are not modelled (12.3)", OPEN)
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
