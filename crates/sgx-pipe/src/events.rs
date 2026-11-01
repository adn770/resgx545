// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Events: EVENT_STATUS bits, host events, ticks (12.6).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q111", "Q033", "Q082", "Q153", "Q157"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("events are not modelled (12.6)", OPEN)
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
