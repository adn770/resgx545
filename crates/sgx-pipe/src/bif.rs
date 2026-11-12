// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! BIF: the MMU, directory lists, banks, requestors, fault fields (12.5).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q076", "Q108", "Q109", "Q110", "Q003"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the BIF is not modelled (12.5)", OPEN)
}

/// The `BIF_FAULT` word of the first render that runs the TA after a held TA write fault
/// (`BIF_INT_STAT` `int`, `BIF_FAULT` `held`) and the debugfs reset: the held job's page and
/// `SB`, through `list`, the directory list current at that TA run (`CID`, bits 3:0). E848 (h1,
/// h2, h4) and E891 (a0 to a2; H-LIST 2 of 2, H-WORD refuted); `flushed`, a BIF invalidate
/// (`CR_BIF_CTRL.INVAL_DC` set and cleared) while the fault was held, changes nothing (E892:
/// H-FLUSH refuted, H-PEND 3 of 3). Only the measured faults (0x90004, pages 0x20006 and
/// 0x2000a, `SB` 6, list 1) and lists are modelled; how many replays come before a render passes,
/// what ends them and the -110 boots after some resets are refused (Q003).
pub fn replay_word(int: u32, held: u32, list: u32, flushed: bool) -> Result<u32, Outcome> {
    const RUN: &[(u32, u32, bool)] = &[
        (0x2000_a061, 1, false),
        (0x2000_a061, 2, false),
        (0x2000_6061, 1, false),
        (0x2000_6061, 2, false),
        (0x2000_a061, 1, true),
        (0x2000_a061, 2, true),
        (0x2000_6061, 1, true),
    ];
    if int != 0x90004 || !RUN.contains(&(held, list, flushed)) {
        return Err(Outcome::unsupported(
            &format!(
                "a replay after BIF_INT_STAT {int:#x}, BIF_FAULT {held:#x}, list {list}, flushed {flushed}: not run (E848, E891, E892)"
            ),
            &["Q003"],
        ));
    }
    Ok((held & !0xf) | list)
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

    #[test]
    fn the_replay_goes_through_the_list_of_the_next_ta_run() {
        // E848 h1, h2, h4; E891 a0, a1, a2: the job's page and SB, the list current at the next
        // TA run (2 after a fill took list 1)
        for (held, list, want) in [
            (0x2000_a061, 1, 0x2000_a061),
            (0x2000_a061, 2, 0x2000_a062),
            (0x2000_6061, 1, 0x2000_6061),
            (0x2000_6061, 2, 0x2000_6062),
        ] {
            assert_eq!(replay_word(0x90004, held, list, false), Ok(want), "{held:#x} {list}");
        }
    }

    #[test]
    fn a_bif_flush_while_the_fault_is_held_does_not_drop_the_replay() {
        // E892 b0, b1, b2: INVAL_DC set and cleared while held, then the reset; the replay as
        // without it (H-FLUSH refuted, H-PEND 3 of 3)
        assert_eq!(replay_word(0x90004, 0x2000_a061, 1, true), Ok(0x2000_a061));
        assert_eq!(replay_word(0x90004, 0x2000_a061, 2, true), Ok(0x2000_a062));
        assert_eq!(replay_word(0x90004, 0x2000_6061, 1, true), Ok(0x2000_6061));
    }

    #[test]
    fn what_no_replay_measured_is_refused() {
        let refused = |i, w, l, f| matches!(replay_word(i, w, l, f), Err(Outcome::Unsupported { .. }));
        assert!(refused(0x90100, 0x1000_0011, 1, false), "another requestor (E845: no replay)");
        assert!(refused(0x90004, 0x2000_8061, 1, false), "a page no replay was read at");
        assert!(refused(0x90004, 0x2000_a051, 1, false), "another SB");
        assert!(refused(0x90004, 0x2000_a062, 1, false), "a fault through list 2");
        assert!(refused(0x90004, 0x2000_a061, 3, false), "list 3 never ran");
        assert!(refused(0x90004, 0x2000_6061, 2, true), "flushed, list 2 at 288 x 144: not run");
    }
}
