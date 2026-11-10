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
/// same at other targets (E799, E801) nor in another scene (E802), so this constant is the
/// 4096x4096 one of the tool's triangle; why it differs is open (Q210).
pub const RAISE_LIMIT_C: u32 = 0x371;

/// C at 2048x2048 with 1500 vertices of the tool's triangle (E799): last raise at thr0 0xe2, first
/// silent 0xe3, inside E785's bracket [0xe0, 0x120). A 2048x2048 target in a 4096x4096 context
/// flipped at the same place (E800).
pub const RAISE_LIMIT_C_2048: u32 = 0x102;

/// The scene of a measured limit: the tool's triangle with 1500 vertices (`--tri pixel
/// --vertices 1500`; 1350 too at 4096x4096, E774), or the same with `--tri-full` (E802).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Scene {
    ToolTriangle,
    ToolTriangleFull,
}

/// The exact limit C of the tool's triangle at each target where a run found one flip (E774,
/// E799, E801). No law in the target's size fits them (E801: 4096x2048 and 2048x4096 differ), so
/// nothing is interpolated.
const RAISE_LIMITS: &[((u32, u32), u32)] = &[
    ((4096, 4096), RAISE_LIMIT_C),
    ((2048, 2048), RAISE_LIMIT_C_2048),
    ((4096, 2048), 0x1d2),
    ((2048, 4096), 0x1d6),
    ((3072, 3072), 0x208),
];

/// The highest raised threshold of `--tri-full` at 2048x2048 (E802: thr0 0xf3 raised, no silent
/// cell run): C is at least this, its value unmeasured.
const RAISED_TRI_FULL_2048: u32 = 0x113;

/// Whether the raise limit admits a raise of `thr0` by 0x20 for a target of the scene (the
/// render target's size, not the context's: E800): `Some(true)` or `Some(false)` where a measured
/// limit decides it, `None` where none does (other targets, other scenes, `--tri-full` above its
/// highest raise). Necessary for a raise, not sufficient (E625's second run must reach thr0).
pub fn raise_within_limit_at(scene: Scene, width: u32, height: u32, thr0: u32) -> Option<bool> {
    let raised = thr0.saturating_add(0x20);
    match scene {
        Scene::ToolTriangle => {
            RAISE_LIMITS.iter().find(|(t, _)| *t == (width, height)).map(|(_, c)| raised <= *c)
        }
        Scene::ToolTriangleFull => {
            ((width, height) == (2048, 2048) && raised <= RAISED_TRI_FULL_2048).then_some(true)
        }
    }
}

/// Dword 36 of the TA/3D control block from the page counts of CR_DPM_GLOBAL_PAGE_STATUS (0x072c,
/// low half) in the sample before each abort of a job: the count before the last abort less 2,
/// floor 0, and 0 without an abort (E803: held out, 6 of 6 in g-d36 with all 3 separating jobs,
/// and 54 of 54 in the side tables of four more stages; the tool's triangle at five targets and
/// `--tri-full`). The model has no such counts of its own: this reads them, it does not make them.
pub fn dword36_from_abort_counts(counts: &[u32]) -> u32 {
    counts.last().map_or(0, |c| c.saturating_sub(2))
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
            assert_eq!(raise_within_limit_at(Scene::ToolTriangle, 4096, 4096, v), Some(raised), "{v:#x}");
            assert_eq!(raise_within_limit(v), raised, "{v:#x}");
        }
    }

    #[test]
    fn at_2048x2048_the_limit_is_exact_0x102_inside_the_bracket_of_e785() {
        // E799 [HW, held out]: last raise at thr0 0xe2, first silent 0xe3 (C = 0x102); E785's cells
        // 0x80 and 0xc0 raised, 0x100 did not
        let at = |t| raise_within_limit_at(Scene::ToolTriangle, 2048, 2048, t);
        for t in [0x80, 0xc0, 0xe0, 0xe2] {
            assert_eq!(at(t), Some(true), "{t:#x}");
        }
        for t in [0xe3, 0xe4, 0xe8, 0xf0, 0x100, 0x140] {
            assert_eq!(at(t), Some(false), "{t:#x}");
        }
        assert!(at(0xe2) == Some(true) && 0xe2 + 0x20 == RAISE_LIMIT_C_2048);
        // 4096x4096's limit does not hold here (H-same refuted): 0x100 + 0x20 is below 0x371
        assert!(raise_within_limit(0x100) && at(0x100) == Some(false));
    }

    #[test]
    fn the_limit_follows_the_target_with_one_value_at_each_measured_target() {
        // E801 [HW, held out]: exact flips at three more targets of the same scene; 4096x2048 and
        // 2048x4096 have as many regions and different limits
        let at = |w, h, t| raise_within_limit_at(Scene::ToolTriangle, w, h, t);
        for (w, h, last) in
            [(4096, 2048, 0x1b2), (2048, 4096, 0x1b6), (3072, 3072, 0x1e8), (4096, 4096, 0x351)]
        {
            assert_eq!(at(w, h, last), Some(true), "{w}x{h}");
            assert_eq!(at(w, h, last + 1), Some(false), "{w}x{h}");
        }
        assert_ne!(at(4096, 2048, 0x1b4), at(2048, 4096, 0x1b4));
        // E800 [HW, held out]: a 2048x2048 target in a 4096x4096 context flipped where g-c4's did,
        // so the function takes the target's size and no context; every other target stays
        // unmeasured
        for (w, h) in [(2048, 1536), (4096, 3072), (1024, 768), (64, 64), (4096, 1024), (1024, 4096)] {
            assert_eq!(at(w, h, 0x100), None, "{w}x{h}");
        }
    }

    #[test]
    fn another_scene_at_2048x2048_raises_beyond_the_tool_triangles_limit() {
        // E802 [HW, held out]: the --tri-full scene raised at thr0 0xd2, 0xde, 0xe2, 0xe3, 0xe7 and
        // 0xf3, with no silent cell; the tool triangle's 0xe3 did not raise (E799)
        let full = |t| raise_within_limit_at(Scene::ToolTriangleFull, 2048, 2048, t);
        for t in [0xd2, 0xde, 0xe2, 0xe3, 0xe7, 0xf3] {
            assert_eq!(full(t), Some(true), "{t:#x}");
        }
        assert_eq!(raise_within_limit_at(Scene::ToolTriangle, 2048, 2048, 0xe3), Some(false));
        // no silent cell was run: above 0xf3 the limit is unmeasured, and no other target ran
        assert_eq!((full(0xf4), full(0x100)), (None, None));
        assert_eq!(raise_within_limit_at(Scene::ToolTriangleFull, 4096, 4096, 0x300), None);
    }

    #[test]
    fn dword_36_is_the_count_before_the_last_abort_less_2_e803() {
        // E803 [HW, held out]: g-d36's six jobs (three separate this reading from the peak and the
        // second-abort readings), counts of 0x072c's low half in the sample before each abort
        let rows: [(&[u32], u32); 6] = [
            (&[2, 3, 3, 3, 3, 3], 1),
            (&[2, 3, 3, 2, 2, 3], 1),
            (&[2, 4, 3], 1),
            (&[3, 4, 4], 2),
            (&[3, 4, 3], 1),
            (&[3, 4, 3], 1),
        ];
        for (counts, d36) in rows {
            assert_eq!(dword36_from_abort_counts(counts), d36, "{counts:?}");
        }
        // side tables: a job without an abort reads 0; one abort at the count 7 reads 5 (c5b-cal);
        // the floor at 0 (g-c7's counts of 1 and 2)
        assert_eq!(dword36_from_abort_counts(&[]), 0);
        assert_eq!(dword36_from_abort_counts(&[7]), 5);
        assert_eq!(dword36_from_abort_counts(&[1, 1, 2, 2, 2]), 0);
        assert_eq!(dword36_from_abort_counts(&[1, 2, 1]), 0);
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
