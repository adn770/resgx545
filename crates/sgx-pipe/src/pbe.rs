// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! PBE: end-of-tile emit, pack modes, sideband, tile windows (12.1).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q012", "Q040", "Q044", "Q046", "Q074", "Q054", "Q183"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the pixel back end is not modelled (12.1)", OPEN)
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
