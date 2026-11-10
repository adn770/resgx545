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
/// one flip, 1350 as 1500). The limit is on the threshold the TA runs, not on the knob P: with P
/// at 0x422 and the threshold poked, the flip was at 0x351 / 0x352 (E786, 7 of 7). It is not the
/// same at another target (E785: 2048x2048 below), so this constant is the 4096x4096 one; what
/// makes it differ was not separated (Q210).
pub const RAISE_LIMIT_C: u32 = 0x371;

/// The bracket of C at 2048x2048 with 1500 vertices of the tool's triangle (E785): the threshold was
/// raised at thr0 0x80 and 0xc0 (thr0 + 0x20 = 0xe0 accepted) and not at 0x100 (0x120 refused),
/// the cells between not run. `C` is in `[lo, hi)`.
pub const RAISE_LIMIT_C_2048: (u32, u32) = (0xe0, 0x120);

/// Whether the raise limit admits a raise of `thr0` by 0x20 at a target: `Some(true)` or
/// `Some(false)` where the measured limit decides it, `None` where it does not (the bracket at
/// 2048x2048, and every other target, which no run measured). Necessary for a raise, not sufficient
/// (E625's second run must reach thr0).
pub fn raise_within_limit_at(width: u32, height: u32, thr0: u32) -> Option<bool> {
    let raised = thr0.saturating_add(0x20);
    match (width, height) {
        (4096, 4096) => Some(raised <= RAISE_LIMIT_C),
        (2048, 2048) if raised <= RAISE_LIMIT_C_2048.0 => Some(true),
        (2048, 2048) if raised >= RAISE_LIMIT_C_2048.1 => Some(false),
        _ => None,
    }
}

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
    fn the_limit_follows_the_threshold_the_ta_runs_over_the_poke_ladder_of_e786() {
        // E786 [HW, held out]: 1500 vertices at 4096x4096, P = 0x422, the threshold poked to V
        let ladder = [
            (0x300, true),
            (0x33e, true),
            (0x351, true),
            (0x352, false),
            (0x35e, false),
            (0x3a0, false),
            (0x3de, false),
        ];
        for (v, raised) in ladder {
            assert_eq!(raise_within_limit_at(4096, 4096, v), Some(raised), "{v:#x}");
            assert_eq!(raise_within_limit(v), raised, "{v:#x}");
        }
    }

    #[test]
    fn at_2048x2048_the_limit_is_bracketed_by_the_cells_of_e785() {
        // E785 [HW, held out]: thr0 0x80 and 0xc0 raised, 0x100 did not (the second run reached
        // thr0 in all three); the cells between were not run and every other target is unmeasured
        let at = |t| raise_within_limit_at(2048, 2048, t);
        assert_eq!((at(0x80), at(0xc0), at(0x100)), (Some(true), Some(true), Some(false)));
        assert_eq!((at(0xc1), at(0xff)), (None, None));
        assert_eq!(at(0x140), Some(false));
        // 4096x4096's limit does not hold here (H-same refuted): 0x100 + 0x20 is below 0x371
        assert!(raise_within_limit(0x100) && at(0x100) == Some(false));
        for (w, h) in [(2048, 1536), (4096, 3072), (1024, 768), (64, 64)] {
            assert_eq!(raise_within_limit_at(w, h, 0x100), None, "{w}x{h}");
        }
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
