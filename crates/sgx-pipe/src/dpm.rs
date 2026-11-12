// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! DPM: parameter buffer pool, state page, overflow and partial render (12.7).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q045", "Q036", "Q038", "Q081", "Q103", "Q191", "Q192", "Q210", "Q211"];

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

/// The guard of the firmware's raise of the first threshold by 0x20, from the global page counts
/// (the high half of CR_DPM_GLOBAL_PAGE_STATUS) at the first abort, at the resume after the partial
/// render and at the next out-of-memory entry: the abort saves dword 36 as its count less 2 (floor
/// 0, E803), the resume sets `sa8` bits 7 and 8 when its count is above dword 36, and the entry
/// raises when bit 7 is set and its count is above dword 36 again (R-5 [RE], 3d.md section 6.4).
/// Held on the hardware: `sa8` read by our own task, 6 of 6, and c4-b3, the guard's one miss on
/// the timelines, silent because its resume compared one global page (E864); the raising-side step
/// cells raised after a grow (E861). The resume's count is the one the firmware read: after a grow
/// the timeline's last sample in the partial render can read one page more (E860).
pub fn guard_raises(abort_global: u32, resume_global: u32, entry_global: u32) -> bool {
    let d36 = dword36_from_abort_counts(&[abort_global]);
    resume_global > d36 && entry_global > d36
}

/// The first threshold steps S_k of the global page count of the tool's triangle with 1500
/// vertices, measured held out where a grow was tested at and around them (E852's table, repeated
/// by the calibrations of E860, the cells of E861). The steps of 4096x2048, 2048x4096 and 3072x3072
/// are left out: their only held-out stage is gated (E861's d-a2b).
const GLOBAL_STEPS: &[((u32, u32), &[u32])] =
    &[((2048, 2048), &[0x51, 0x9d, 0xe8, 0x132]), ((4096, 4096), &[0x125, 0x240, 0x35b])];

/// Whether the first out-of-memory entry grows the TA's share of the global list
/// (`CR_DPM_TA_GLOBAL_LIST`, the list-kind branch of 3d.md section 6.4): exactly when the first
/// threshold is a step S_k (H-GREQ, E860 5 of 5 repeats, E861 16 of 16 held-out rows). `None` past
/// the page after the last measured step, at other targets and for other scenes.
pub fn grows_at_first_abort(scene: Scene, width: u32, height: u32, thr0: u32) -> Option<bool> {
    if scene != Scene::ToolTriangle {
        return None;
    }
    let steps = GLOBAL_STEPS.iter().find(|(t, _)| *t == (width, height))?.1;
    (thr0 <= steps.last()? + 1).then(|| steps.contains(&thr0))
}

/// Whether the raise limit C admits a raise of `thr0` by 0x20 (E774). Necessary for a raise at the
/// measured scene and target and not sufficient anywhere else: whether the second run reaches thr0
/// (E625's rule, Q210) is not part of it, nor is the count of partial renders: E625's formula for it
/// is refuted at U = 287 (E832: 9 down to 2 over 19 buffer sizes, none of the 20 fitting pairs).
pub fn raise_within_limit(thr0: u32) -> bool {
    thr0.saturating_add(0x20) <= RAISE_LIMIT_C
}

/// The parameter buffer's default size in pages (debugfs `render_pb_pages`); a scene overflows when
/// P - 0x22 is below its page need (E625, E735, E773).
pub const PB_PAGES_DEFAULT: u32 = 0x422;
const PB_FIXED_RESERVE: u32 = 0x22;

/// How a 4x job of the tool's full-screen triangle (`--tri-full --aa4`, `CR_TE_AA` 0xe0000000) on a
/// context made for 4x targets (four region-header arrays) ends.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ending4x {
    /// Completes with every pixel right.
    Complete,
    /// The scene overflows the parameter buffer: -ENOSPC with no BIF fault, as at 1x (E866).
    Enospc,
    /// The job faults on the 3D side at the request base (`BIF_INT_STAT` 0x90100, `BIF_FAULT`
    /// 0x10000011), no pixel right below 4096 wide (E845, E868).
    Fault,
}

/// U4, the scene pages of that job, page 0 included: 1 + ceil(2 tiles16 / 32), the doubled grid
/// (E845's fit on E824's dumps; E866 at three boundaries one page apart, two held out; E867, E868,
/// E887, E889). Two cells used two pages more, 992 x 1280 (313) and 1184 x 768 (225), both with an
/// odd count of 32-pixel tile columns on four macrotiles a side, a shape no cell matched U4 in
/// (E887, E889); `four_array_4x_ending` refuses that band.
pub fn full_triangle_4x_pages(w: u32, h: u32) -> u32 {
    1 + (2 * w.div_ceil(16) * h.div_ceil(16)).div_ceil(32)
}

/// The 32 x 16 tiles, the macrotiles a side and the tail side of a context made for `mw` x `mh`
/// (the fork's single-sampled layout, `sgx_render.c`): (tiles x, tiles y, macrotiles a side, side).
fn render_grid(mw: u32, mh: u32) -> (u32, u32, u32, u32) {
    let (tx, ty) = (mw.div_ceil(32), mh.div_ceil(16));
    let n = if mw * mh >= 640 * 480 { 4 } else { 2 };
    let (mx, my) = (tx.div_ceil(n).next_multiple_of(4), ty.div_ceil(n).next_multiple_of(4));
    (tx, ty, n, (n * mx).max(n * my).next_power_of_two())
}

/// The Z-order index of tile (x, y) of a 4x job's doubled grid (16 x 8 pixel tiles): y on the even
/// bits, x on the odd bits. The TA keeps the tile's tail pointer, one dword, at TA-data offset 4
/// times this (H-TPM: E870's fit on E869's dump, held out by E887 and E889).
pub fn tail_index_4x(x: u32, y: u32) -> u32 {
    let spread = |v: u32| (0..16).fold(0, |r, b| r | ((v >> b) & 1) << (2 * b));
    spread(y) | spread(x) << 1
}

/// The end in bytes of a `w` x `h` 4x target's tail-pointer entries: 4 x (Z(2tx - 1, 2ty - 1) + 1),
/// tx and ty its 32 x 16 tile counts (Z grows in each coordinate, so the far corner is the last).
pub fn tail_entries_end_4x(w: u32, h: u32) -> u32 {
    let (tx, ty) = (w.div_ceil(32), h.div_ceil(16));
    4 * (tail_index_4x(2 * tx - 1, 2 * ty - 1) + 1)
}

/// The tail-pointer room our kernel gives a context made for 4x targets: the rgn4 module's 4 side^2
/// bytes (fork resgx545 a2788bd8, srcversion 99CD90DA26E3AFF9C450517), the r6-kernel module's four
/// times that (fork r6-kernel 3f0b3e74, srcversion 41E2F5C756F96D20F7109A4) or its debugfs
/// `render_tail_room` (a whole number of pages).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TailRoom {
    Rgn4,
    Quad,
    Set(u32),
}

/// `td.rgn`, the region headers' offset from the TA-data base (the tail-pointer base), of a 4x
/// context made for `mw` x `mh`: the room rounded to a page, then the control, OTPM and state pages.
pub fn region_headers_4x(mw: u32, mh: u32, room: TailRoom) -> u32 {
    let (.., side) = render_grid(mw, mh);
    let bytes = match room {
        TailRoom::Rgn4 => 4 * side * side,
        TailRoom::Quad => 16 * side * side,
        TailRoom::Set(r) => r,
    };
    bytes.next_multiple_of(0x1000) + 0x3000
}

/// How the job ends at target `w` x `h` on a context made for `mw` x `mh` by the rgn4 module with
/// `p` parameter-buffer pages (`four_array_4x_ending_on` with `TailRoom::Rgn4`).
pub fn four_array_4x_ending(w: u32, h: u32, mw: u32, mh: u32, p: u32) -> Option<Ending4x> {
    four_array_4x_ending_on(w, h, mw, mh, p, TailRoom::Rgn4)
}

/// How the job ends: a fault where the target's tail-pointer entries pass the region headers of the
/// context (H-TPM: 26 of 26 recorded cells, E870; 11 of 11 held out, E887; through the kernel's
/// room and one page either side of its limit, E889), else complete when its scene fits the buffer
/// and -ENOSPC when it does not (H-ENOSPC4, E866; E889's 4096 x 1152). `None` for a target larger
/// than its maximum or a maximum past 4096 (not run), a faulting cell at a P other than 0x422
/// (every 4x fault on record ran there) and the band where the page need is not U4's (above).
pub fn four_array_4x_ending_on(w: u32, h: u32, mw: u32, mh: u32, p: u32, room: TailRoom) -> Option<Ending4x> {
    if w == 0 || h == 0 || w > mw || h > mh || mw > 4096 || mh > 4096 {
        return None;
    }
    if tail_entries_end_4x(w, h) > region_headers_4x(mw, mh, room) {
        return (p == PB_PAGES_DEFAULT).then_some(Ending4x::Fault);
    }
    let (tx, _, n, _) = render_grid(w, h);
    let need = full_triangle_4x_pages(w, h);
    let slack = if tx % 2 == 1 && n == 4 { 2 } else { 0 };
    let usable = p.saturating_sub(PB_FIXED_RESERVE);
    if usable >= need + slack {
        Some(Ending4x::Complete)
    } else if usable < need {
        Some(Ending4x::Enospc)
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_open_list_holds_the_threshold_and_page_need_questions() {
        // Q210 the threshold raise rule, Q211 the page need of a scene; Q273 (dword 36) is answered
        // by E803, so it no longer blocks the unit
        for id in ["Q210", "Q211"] {
            assert!(OPEN.contains(&id), "{id}");
        }
        assert!(!OPEN.contains(&"Q273"));
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
    fn the_guard_raises_when_the_resume_and_the_entry_count_above_dword_36_e864() {
        // R-5 [RE] held on the hardware (E864: sa8 bits 7 and 8 set by the resume, read by our own
        // task), counts of global pages at the first abort, at the resume, at the next entry
        assert!(guard_raises(3, 2, 4)); // E799's c4-b5, the last raise at 2048x2048
        assert!(!guard_raises(3, 1, 3)); // c4-b6, the first silent cell
        assert!(guard_raises(1, 1, 1)); // E802's raised cells: dword 36 floors at 0
        // E861 [HW, held out]: the raising-side step cells grew and raised (1 or 2 at the abort)
        assert!(guard_raises(1, 1, 2) && guard_raises(2, 1, 2));
        // E864 [HW, held out]: c4-b3's resume compared one global page (sa8 bits 7 to 9 clear
        // at its decision entry), so it is silent, as are the 4096x4096 S4 cells of E861
        assert!(!guard_raises(3, 1, 4));
        // E862: 4 global pages at the abort below S5 make dword 36 = 2, silent with 1 or 2 left
        assert!(!guard_raises(4, 2, 4) && !guard_raises(4, 1, 4));
        // the entry must see the count above dword 36 again
        assert!(!guard_raises(3, 2, 1));
    }

    #[test]
    fn the_first_abort_grows_the_global_list_exactly_on_a_step_e861() {
        // E860, E861 [HW, held out]: the tool's triangle with 1500 vertices; grow at every first
        // threshold on a step and at none one page either side, at 2048x2048 and 4096x4096
        let grows = |w, h, t| grows_at_first_abort(Scene::ToolTriangle, w, h, t);
        for t in [0x51, 0x9d, 0xe8, 0x132] {
            assert_eq!(grows(2048, 2048, t), Some(true), "{t:#x}");
            assert_eq!(grows(2048, 2048, t - 1), Some(false), "{t:#x}");
            assert_eq!(grows(2048, 2048, t + 1), Some(false), "{t:#x}");
        }
        for t in [0x240, 0x35b] {
            assert_eq!(grows(4096, 4096, t), Some(true), "{t:#x}");
        }
        assert_eq!(grows(4096, 4096, 0x23f), Some(false));
        assert_eq!(grows(4096, 4096, 0x35a), Some(false));
        // E852's kept jobs: no grow off a step (the default c4 cells)
        assert_eq!(grows(2048, 2048, 0xe2), Some(false));
        // above the last measured step, at the gated targets (E861's d-a2b) and for other
        // scenes the model refuses
        assert_eq!(grows(2048, 2048, 0x140), None);
        assert_eq!(grows(4096, 2048, 0x1b9), None);
        assert_eq!(grows_at_first_abort(Scene::ToolTriangleFull, 2048, 2048, 0xe8), None);
    }

    #[test]
    fn the_4x_full_triangle_needs_u4_pages_at_every_measured_size() {
        // E824's dumps, E845's s0, E866's boundaries and E867's, E868's completed rows
        let needs = [
            ((288, 144), 12),
            ((512, 384), 49),
            ((640, 480), 76),
            ((256, 1536), 97),
            ((1024, 512), 129),
            ((1024, 768), 193),
            ((1280, 1024), 321),
            ((2048, 1536), 769),
        ];
        for ((w, h), u) in needs {
            assert_eq!(full_triangle_4x_pages(w, h), u, "{w}x{h}");
        }
    }

    #[test]
    fn a_4x_overflow_ends_in_enospc_one_page_short_of_the_need_e866() {
        // E866 [HW]: H-ENOSPC4 held, 6 of 6 (o4, o5 replicate E846; o6 to o9 held out)
        let rows = [
            ((1024, 768), 0xe3, Ending4x::Complete),
            ((1024, 768), 0xe2, Ending4x::Enospc),
            ((288, 144), 0x23, Ending4x::Enospc),
            ((640, 480), 0x6e, Ending4x::Complete),
            ((640, 480), 0x6d, Ending4x::Enospc),
            ((512, 384), 0x53, Ending4x::Complete),
            ((512, 384), 0x52, Ending4x::Enospc),
        ];
        for ((w, h), p, end) in rows {
            assert_eq!(four_array_4x_ending(w, h, w, h, p), Some(end), "{w}x{h} at {p:#x}");
        }
    }

    #[test]
    fn the_4x_fault_follows_the_contexts_maximum_and_no_size_rule_e867_e868() {
        // E867 [HW]: the faulting 1280x1024 completes on a context made for a larger maximum with
        // more tail room (m1, m2, m4) and faults when only the region buffer grows (m3)
        let m = [
            ((1024, 768), (2048, 2048), Ending4x::Complete),
            ((1280, 1024), (1280, 1040), Ending4x::Complete),
            ((1280, 1024), (2048, 2048), Ending4x::Complete),
            ((1280, 1024), (2048, 1024), Ending4x::Fault),
            ((2048, 1536), (4096, 4096), Ending4x::Complete),
        ];
        for ((w, h), (mw, mh), end) in m {
            assert_eq!(
                four_array_4x_ending(w, h, mw, mh, PB_PAGES_DEFAULT),
                Some(end),
                "{w}x{h} on {mw}x{mh}"
            );
        }
        // E868 [HW]: on its own maximum; E845, E869: 1280 x 1024 and 2048 x 1536 fault
        let own = [
            ((2048, 240), true),
            ((256, 1536), false),
            ((768, 2048), true),
            ((1280, 768), true),
            ((1024, 1024), true),
            ((1024, 512), false),
            ((1184, 768), true),
            ((1024, 800), true),
            ((1280, 1024), true),
            ((2048, 1536), true),
        ];
        for ((w, h), fault) in own {
            let end = if fault { Ending4x::Fault } else { Ending4x::Complete };
            assert_eq!(four_array_4x_ending(w, h, w, h, PB_PAGES_DEFAULT), Some(end), "{w}x{h}");
        }
    }

    #[test]
    fn the_4x_tail_pointers_are_z_ordered_with_y_on_the_even_bits_e870() {
        // E870's fit on E869's dump, held out by E887 and E889: one dword a tile of the doubled
        // grid at 4 x Z(x, y), y on the even bits, x on the odd bits
        assert_eq!(tail_index_4x(0, 0), 0);
        assert_eq!(tail_index_4x(0, 1), 1);
        assert_eq!(tail_index_4x(1, 0), 2);
        assert_eq!(tail_index_4x(3, 5), 27);
        // the end of a target's entries, 4 x (Z(2tx - 1, 2ty - 1) + 1) (E870's table, E887, E889)
        let ends = [
            ((64, 64), 0x80),
            ((1024, 768), 0x7000),
            ((1024, 512), 0x4000),
            ((1024, 800), 0x7ac0),
            ((1280, 768), 0xc800),
            ((1280, 1024), 0xd800),
            ((2048, 240), 0xaff0),
            ((768, 2048), 0x17800),
            ((992, 1280), 0x12fe0),
            ((1024, 1280), 0x13000),
            ((1024, 1296), 0x13ab0),
            ((2048, 2032), 0x1fff0),
            ((4096, 1152), 0x3ac00),
            ((4096, 4096), 0x80000),
        ];
        for ((w, h), end) in ends {
            assert_eq!(tail_entries_end_4x(w, h), end, "{w}x{h}");
        }
    }

    #[test]
    fn the_region_headers_follow_the_kernels_tail_room() {
        // the rgn4 module (fork a2788bd8): room 4 side^2 bytes, then the control, OTPM and state
        // pages; the r6-kernel module (fork r6-kernel 3f0b3e74): four times that room for a
        // context made for 4x targets, or the debugfs render_tail_room
        let rgn4 = [
            ((64, 64), 0x4000),
            ((1024, 768), 0x7000),
            ((2048, 1024), 0x7000),
            ((1024, 1280), 0x13000),
            ((4096, 4096), 0x43000),
        ];
        for ((mw, mh), rgn) in rgn4 {
            assert_eq!(region_headers_4x(mw, mh, TailRoom::Rgn4), rgn, "{mw}x{mh}");
        }
        let auto = [
            ((1024, 768), 0x13000),
            ((1280, 1024), 0x13000),
            ((2048, 1536), 0x43000),
            ((4096, 1152), 0x43000),
        ];
        for ((mw, mh), rgn) in auto {
            assert_eq!(region_headers_4x(mw, mh, TailRoom::Quad), rgn, "{mw}x{mh}");
        }
        for (room, rgn) in [(0x3000, 0x6000), (0x4000, 0x7000), (0xa000, 0xd000), (0xb000, 0xe000)] {
            assert_eq!(region_headers_4x(1280, 1024, TailRoom::Set(room)), rgn, "{room:#x}");
        }
    }

    #[test]
    fn the_rule_gives_every_four_array_outcome_on_record_and_the_held_out_rows_e887() {
        // (target, maximum, fault) on the rgn4 module at P 0x422: E824, E828, E845, E846, E867,
        // E868, E869 (E870's 26 cells), then E887's held-out rows a1-a14, h1, h2 and its control a4
        // (target, maximum, faulted)
        type Cell = ((u32, u32), (u32, u32), bool);
        let cells: &[Cell] = &[
            ((64, 64), (64, 64), false),
            ((288, 144), (288, 144), false),
            ((256, 288), (256, 288), false),
            ((384, 384), (384, 384), false),
            ((320, 160), (320, 160), false),
            ((512, 384), (512, 384), false),
            ((640, 480), (640, 480), false),
            ((320, 400), (320, 400), false),
            ((1024, 768), (1024, 768), false),
            ((1280, 1024), (1280, 1024), true),
            ((2048, 1536), (2048, 1536), true),
            ((4096, 1152), (4096, 1152), true),
            ((4096, 4096), (4096, 4096), true),
            ((1024, 768), (2048, 2048), false),
            ((1280, 1024), (1280, 1040), false),
            ((1280, 1024), (2048, 2048), false),
            ((1280, 1024), (2048, 1024), true),
            ((2048, 1536), (4096, 4096), false),
            ((2048, 240), (2048, 240), true),
            ((256, 1536), (256, 1536), false),
            ((768, 2048), (768, 2048), true),
            ((1280, 768), (1280, 768), true),
            ((1024, 1024), (1024, 1024), true),
            ((1024, 512), (1024, 512), false),
            ((1184, 768), (1184, 768), true),
            ((1024, 800), (1024, 800), true),
            // E887 [HW, held out]
            ((1024, 768), (2048, 1024), false),
            ((1024, 1280), (1024, 1280), false),
            ((992, 1280), (992, 1280), false),
            ((512, 1536), (512, 1536), false),
            ((1024, 1024), (1024, 1280), false),
            ((1024, 800), (1024, 1280), false),
            ((1024, 1296), (1024, 1296), true),
            ((1040, 1280), (1040, 1280), true),
            ((1024, 800), (2048, 1024), true),
            ((1024, 1536), (1024, 1536), true),
        ];
        for &((w, h), (mw, mh), fault) in cells {
            let end = if fault { Ending4x::Fault } else { Ending4x::Complete };
            assert_eq!(
                four_array_4x_ending(w, h, mw, mh, PB_PAGES_DEFAULT),
                Some(end),
                "{w}x{h} on {mw}x{mh}"
            );
        }
    }

    #[test]
    fn the_quadrupled_tail_room_ends_the_fault_and_the_knob_moves_the_limit_e889() {
        // E889 [HW]: on the r6-kernel module every own-maximum cell that faulted completes
        // (b1-b8, b9 the control), the largest targets complete or overflow without a fault
        let quad = [
            ((1024, 768), Ending4x::Complete),
            ((1280, 1024), Ending4x::Complete),
            ((1184, 768), Ending4x::Complete),
            ((1024, 800), Ending4x::Complete),
            ((2048, 240), Ending4x::Complete),
            ((768, 2048), Ending4x::Complete),
            ((2048, 1536), Ending4x::Complete),
            ((1280, 768), Ending4x::Complete),
            ((1024, 1024), Ending4x::Complete),
            ((2048, 2032), Ending4x::Complete),
            ((4096, 960), Ending4x::Complete),
            ((4096, 1152), Ending4x::Enospc),
        ];
        for ((w, h), end) in quad {
            assert_eq!(
                four_array_4x_ending_on(w, h, w, h, PB_PAGES_DEFAULT, TailRoom::Quad),
                Some(end),
                "{w}x{h}"
            );
        }
        // the knob one page apart: k1, k5, k2, k4, k3
        let knob = [
            ((1280, 1024), 0x4000, Ending4x::Fault),
            ((1024, 768), 0x4000, Ending4x::Complete),
            ((1280, 1024), 0xb000, Ending4x::Complete),
            ((1024, 768), 0x3000, Ending4x::Fault),
            ((1280, 1024), 0xa000, Ending4x::Fault),
        ];
        for ((w, h), room, end) in knob {
            assert_eq!(
                four_array_4x_ending_on(w, h, w, h, PB_PAGES_DEFAULT, TailRoom::Set(room)),
                Some(end),
                "{w}x{h} at {room:#x}"
            );
        }
    }

    #[test]
    fn a_4x_cell_outside_what_was_run_is_refused() {
        // a target larger than its context's maximum, a maximum past 4096, a faulting cell at
        // another P (every 4x fault on record ran at P 0x422)
        assert_eq!(four_array_4x_ending(1280, 1024, 1024, 768, PB_PAGES_DEFAULT), None);
        assert_eq!(four_array_4x_ending(64, 64, 8192, 64, PB_PAGES_DEFAULT), None);
        assert_eq!(four_array_4x_ending(1280, 1024, 1280, 1024, 0x200), None);
        // a completing cell at another P follows its page need (H-ENOSPC4, E866)
        assert_eq!(four_array_4x_ending(1088, 768, 1088, 768, PB_PAGES_DEFAULT), Some(Ending4x::Fault));
        assert_eq!(four_array_4x_ending(64, 64, 128, 128, 0x23), Some(Ending4x::Enospc));
    }

    #[test]
    fn the_page_need_of_odd_32_pixel_columns_on_four_macrotiles_is_refused_near_the_buffer() {
        // E887 a12 (992 x 1280) and E889 b2 (1184 x 768) used 313 and 225 pages, U4 + 2: no
        // measured cell of that shape (an odd count of 32-pixel tile columns, four macrotiles a
        // side) matched U4, so within two pages above U4 neither ending is given
        assert_eq!(full_triangle_4x_pages(992, 1280), 311);
        assert_eq!(full_triangle_4x_pages(1184, 768), 223);
        let at = |p| four_array_4x_ending(992, 1280, 992, 1280, p);
        assert_eq!(at(0x22 + 313), Some(Ending4x::Complete));
        assert_eq!(at(0x22 + 312), None);
        assert_eq!(at(0x22 + 311), None);
        assert_eq!(at(0x22 + 310), Some(Ending4x::Enospc));
        // a shape that matched U4 keeps its exact boundary (E866: 1024 x 768 at 0xe3 and 0xe2)
        assert_eq!(four_array_4x_ending(1024, 768, 1024, 768, 0xe3), Some(Ending4x::Complete));
        assert_eq!(four_array_4x_ending(1024, 768, 1024, 768, 0xe2), Some(Ending4x::Enospc));
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
