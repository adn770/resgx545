// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! DPM: parameter buffer pool, state page, overflow and partial render (12.7).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q045", "Q036", "Q038", "Q081", "Q103", "Q191", "Q192", "Q210", "Q211", "Q273"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the DPM is not modelled (12.7)", OPEN)
}

/// The limit C on the raised threshold (E774): at 4096x4096, with 1350 or 1500 vertices of the
/// tool's triangle, the TA's threshold was raised by 0x20 after the first abort at every cell of the
/// ladder with a first threshold thr0 from 0x33e to 0x351 and at none from 0x352 to 0x35e (23 jobs,
/// one flip, 1350 as 1500). Whether C is a constant of the core or follows the knob P, the target
/// or the scene, was not separated (Q210).
pub const RAISE_LIMIT_C: u32 = 0x371;

/// Whether the raise limit C admits a raise of `thr0` by 0x20 (E774). Necessary for a raise at the
/// measured scene and target and not sufficient anywhere else: whether the second run reaches thr0
/// (E625's rule, Q210) is not part of it.
pub fn raise_within_limit(thr0: u32) -> bool {
    thr0.saturating_add(0x20) <= RAISE_LIMIT_C
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_open_list_holds_the_threshold_and_page_need_questions() {
        // Q210 the threshold raise rule, Q211 the page need of a scene, Q273 the 1500-vertex scene
        for id in ["Q210", "Q211", "Q273"] {
            assert!(OPEN.contains(&id), "{id}");
        }
    }

    #[test]
    fn the_raise_limit_splits_the_ladder_of_e774_at_one_flip() {
        // the first thresholds P - 0x22 of E774's cells that raised (P = 0x360 to 0x373: 0x33e to
        // 0x351) and of those that did not (P = 0x374 to 0x380: 0x352 to 0x35e), 1350 and 1500 alike
        for thr0 in 0x33e..=0x351 {
            assert!(raise_within_limit(thr0), "{thr0:#x}");
        }
        for thr0 in 0x352..=0x35e {
            assert!(!raise_within_limit(thr0), "{thr0:#x}");
        }
        // E625's default triangle (thr0 at most 0x100) and E753's raises at 0x2fe are inside, the
        // clamp of E704 (thr0 0x400) is outside
        assert!(raise_within_limit(0x100) && raise_within_limit(0x2fe));
        assert!(!raise_within_limit(0x400) && !raise_within_limit(u32::MAX));
    }

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
