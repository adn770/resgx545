// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! What the EDM does after a firmware task's pass ends (closing pass rounds 3 and 4, "sim in
//! sync"): a small pure model that lands only the rows the hardware measured and refuses the rest
//! with [`Error::Unsupported`].
//!
//! A pass ends one of three ways: our task tail-calls the closed task of a PDS #13 slot through a
//! continue patch ([`PassEnd::Closed`]; slot 0 is the general task, the normal continue), it
//! tail-calls the closed tasks' shared exit through the `cont4` patch ([`PassEnd::Exit`]), or it
//! ends the pass itself with `idf`, `wdf` and `nop.end`, with or without a `cfi.global` before
//! them and a `phas #0, #0, pixel, end, parallel` before the `nop.end` ([`PassEnd::OwnEnd`]). The
//! measured rows, all on one laptop, the pass being a plain tick pass or a kick pass made by one
//! host command (pa0 = 0):
//!
//! 1. `Closed{0}` on a tick pass, no sa64 or sa65 write: tick kept, CCB read = write, dword 14 0,
//!    dword 12 advances, next entry pclink 0x98 (E791 A0 and A6, E792: 19 of 19 kept).
//! 2. sa64 written = pa0 with the tick bit (bit 1) clear, then `Closed{0}`: kept, pclink left at 6
//!    at the next entry, dword 12 does not advance on that pass (E792 A4, 3 of 3; E812 C5, 50
//!    passes in each of 2 jobs). sa64 = pa0: kept, pclink 0x98 (E792 A5). Any other value: refused.
//! 3. An sa65 word left in place, `Closed{0}`, tick pass, K the count byte of bits 31:24 (K = 2 in
//!    every run): kept for K<<24 (E791 A2), K<<24 | 1<<23 (E812 C1), 0xb0000000 (E812 C2),
//!    K<<24 | 0x1c04c (E812 C3), K<<24 | 1<<19 (E812 C4). Stalled with the assert marks (read =
//!    write + 1, dword 14 0xad002600) for K<<24 | 0x100 (E814 D2) and for 0xb009c5dc (E537, one
//!    run, which also wrote sa63, sa64 and others). Stalled without the marks for 0xb009c4dc (E814
//!    D1). Any other word is refused (bits 4, 7 and 10 were not tried).
//! 4. `Closed{2}` on a tick pass: kept, next entry on the 25000-unit grid, dword 12 does not
//!    advance (E813 X1, 2 of 2; X20, 20 passes in each of 2 jobs, dword 12 less passes about -20).
//! 5. The end of a tick pass (Q152's first half): kept if and only if the pass executes the `phas`
//!    end before its `nop.end`. `OwnEnd { phas: true }`, with the `cfi.global` (E817 FB 2 of 2,
//!    E830 fb 6 of 6) or without it (E817 FPH 2 of 2, E830 fk 3 of 3), and `Exit` (E817 FC4 2 of
//!    2, E830 fc4 6 of 6): kept, CCB read = write, dword 14 0, the next entry 24994 or 24995
//!    `CR_TIMER` units after the acted pass ([`PHAS_END_GAP`]). `OwnEnd { phas: false }`, with
//!    the `cfi.global` (E817 FCF, E830 fcf1 to fcf3: 4 of 4) or without it (E793 B1, 2 of 2):
//!    stalled, read = write, dword 14 0. 13 of 13 kept, 7 of 7 stopped.
//! 6. `OwnEnd { cfi: false, phas: false }` on a kick pass: stalled, the kick's command written and
//!    not read (read = write - 1), dword 14 0 (E813 B3, 1 job).
//! 7. A `str` of the closed tick handler's own reload word [`TIMER_WORD_RUN`] to `CR_EVENT_TIMER`
//!    ([`Inputs::timer_store`]), then `Closed{0}` on a tick pass: kept, CCB read = write, dword 14
//!    0, the next entry 25114 units after the acted pass (E818 T1, 2 of 2). The same store, then
//!    `OwnEnd { cfi: false, phas: false }`: stalled (E818 T2, 1 job). [infer] The store restarts
//!    the countdown where it executes; the sim gives the measured gap and nothing of later ones.
//!
//! Everything else is refused: `Closed{2}` on a kick pass, `Closed{1}` and `Closed{3}` anywhere
//! (not run), `Closed{0}` on a kick pass, the `phas` end, a `cfi.global` or `Exit` on a kick pass
//! (row KP of round 4 has not run; the slot 3 pass, row B1P, is not a [`PassKind`] here), sa64 and
//! sa65 written together, any sa64 or sa65 write with another end, a timer store of another word,
//! with another end or with an sa64 or sa65 write, and a count byte other than 2. Which of dword
//! 12 and the next pclink the rows of 5 and 7 left was not read, so both are `None` there. A
//! stalled EDM delivers no later event until a debugfs reset (E793, E537, E817, E830), and one
//! host command sent into it was not answered (E814 P3 2 of 2, E817 1, E818 1, E830 3: 0 of 7);
//! [`deliver_after`] refuses on that ground. Whether the stalled pass itself was counted was not
//! measured (E811's D instrument never read), so no count is modelled, and dword 12 after a stall
//! is `None`.

use crate::Error;

/// Count byte (bits 31:24 of sa65 at entry) of every run that left a `K<<24` word.
pub const K_MEASURED: u8 = 2;
/// The assert marks of the stalls that read them: HostCtl dword 14.
pub const MARKS_DWORD14: u32 = 0xad00_2600;
/// The next entry after a tick pass ended by the `phas` end or by the closed exit, in `CR_TIMER`
/// units from the acted pass's entry, the least and the most read (E817, E830: 24994 to 24995).
pub const PHAS_END_GAP: (u32, u32) = (24994, 24995);
/// The one word a task of ours stored to `CR_EVENT_TIMER`: the closed tick handler's own reload,
/// `0x01000000 | HostCtl dword 6` (E818, E155).
pub const TIMER_WORD_RUN: u32 = 0x0106_1a80;
/// The next entry after [`TIMER_WORD_RUN`] then the closed task (E818 T1, 2 of 2).
pub const TIMER_STORE_GAP: (u32, u32) = (25114, 25114);

/// A plain tick pass, or a kick pass made by one host command (pa0 = 0).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PassKind {
    Tick,
    Kick,
}

/// How our task ends the pass.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PassEnd {
    /// Tail call of the closed task of this PDS #13 slot (0 = the general task).
    Closed { slot: u8 },
    /// Tail call of the closed tasks' shared exit (the kernel's `cont4` patch).
    Exit,
    /// Our own end, no closed task called: `cfi.global` first if `cfi`, then `idf`, `wdf`, then
    /// `phas #0, #0, pixel, end, parallel` if `phas`, then `nop.end`.
    OwnEnd { cfi: bool, phas: bool },
}

/// What the task did and found before the end of the pass.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Inputs {
    pub kind: PassKind,
    pub end: PassEnd,
    /// pa0 of the pass (the tick pass has bit 1 set; a kick pass has 0).
    pub pa0: u32,
    /// The value our task wrote to sa64, if it did.
    pub sa64: Option<u32>,
    /// The word left in sa65, if the task wrote it (else the entry value stays).
    pub sa65: Option<u32>,
    /// The count byte (bits 31:24) of sa65 at entry; only [`K_MEASURED`] was run.
    pub sa65_count: u8,
    /// The word our task stored to `CR_EVENT_TIMER` (0x0acc) before the end, if it did; only
    /// [`TIMER_WORD_RUN`] was run.
    pub timer_store: Option<u32>,
}

impl Inputs {
    /// A pass that writes neither sa64 nor sa65 and stores nothing to the timer.
    pub fn plain(kind: PassKind, end: PassEnd) -> Inputs {
        let pa0 = if kind == PassKind::Tick { 2 } else { 0 };
        Inputs { kind, end, pa0, sa64: None, sa65: None, sa65_count: K_MEASURED, timer_store: None }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tick {
    Kept,
    Stalled,
}

/// The state the host sees after the pass, and at the next entry.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct AfterPass {
    pub tick: Tick,
    /// CCB read offset minus write offset.
    pub ccb_read_minus_write: i32,
    pub hostctl_dword14: u32,
    /// Whether HostCtl dword 12 advances on this pass; `None` after a stall and where no run read
    /// it.
    pub dword12_advances: Option<bool>,
    /// pclink at the next entry (kept tick only; `None` where no run read it).
    pub next_pclink: Option<u32>,
    /// The next entry falls on the 25000-unit grid (slot 2 rows).
    pub next_on_grid: bool,
    /// The next entry's distance from the acted pass's, in `CR_TIMER` units, the least and the
    /// most read; `None` where the rows did not give it.
    pub next_gap: Option<(u32, u32)>,
}

fn no(what: String) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: what }
}

/// The model: the measured rows, or a refusal.
pub fn end_of_pass(i: &Inputs) -> Result<AfterPass, Error> {
    let kept = |pclink, advances, grid| AfterPass {
        tick: Tick::Kept,
        ccb_read_minus_write: 0,
        hostctl_dword14: 0,
        dword12_advances: Some(advances),
        next_pclink: pclink,
        next_on_grid: grid,
        next_gap: None,
    };
    // the rows of round 3's stages f and t, which read the gap and the CCB, not dword 12 or pclink
    let kept_gap = |gap| AfterPass {
        tick: Tick::Kept,
        ccb_read_minus_write: 0,
        hostctl_dword14: 0,
        dword12_advances: None,
        next_pclink: None,
        next_on_grid: false,
        next_gap: Some(gap),
    };
    let stalled = |read_minus_write, dword14| AfterPass {
        tick: Tick::Stalled,
        ccb_read_minus_write: read_minus_write,
        hostctl_dword14: dword14,
        dword12_advances: None,
        next_pclink: None,
        next_on_grid: false,
        next_gap: None,
    };
    let writes = i.sa64.is_some() || i.sa65.is_some();
    if let Some(w) = i.timer_store {
        // E818: the handler's own word, on a plain tick pass, nothing else written
        return match (i.kind, i.end) {
            _ if w != TIMER_WORD_RUN => Err(no(format!(
                "a timer store of {w:#x}: only the handler's own word {TIMER_WORD_RUN:#x} was run (E818)"
            ))),
            _ if writes => Err(no("a timer store with an sa64 or sa65 write: not run (E818)".into())),
            (PassKind::Tick, PassEnd::Closed { slot: 0 }) => Ok(kept_gap(TIMER_STORE_GAP)),
            (PassKind::Tick, PassEnd::OwnEnd { cfi: false, phas: false }) => Ok(stalled(0, 0)),
            _ => Err(no(format!("{:?} pass ending {:?} after a timer store: not run (E818)", i.kind, i.end))),
        };
    }
    match (i.kind, i.end) {
        // E817, E830 (and E793 for the end without either word): the phas end decides
        (PassKind::Tick, PassEnd::OwnEnd { phas: true, .. } | PassEnd::Exit) if !writes => {
            Ok(kept_gap(PHAS_END_GAP))
        }
        (PassKind::Tick, PassEnd::OwnEnd { phas: false, .. }) if !writes => Ok(stalled(0, 0)),
        // E813 B3: the kick pass ended without either word
        (PassKind::Kick, PassEnd::OwnEnd { cfi: false, phas: false }) if !writes => Ok(stalled(-1, 0)),
        (PassKind::Tick, PassEnd::Closed { slot: 2 }) if !writes => Ok(kept(None, false, true)),
        (PassKind::Tick, PassEnd::Closed { slot: 0 }) => match (i.sa64, i.sa65) {
            (None, None) => Ok(kept(Some(0x98), true, false)),
            (Some(v), None) if i.pa0 & 2 != 0 && v == i.pa0 => Ok(kept(Some(0x98), true, false)),
            (Some(v), None) if i.pa0 & 2 != 0 && v == i.pa0 & !2 => Ok(kept(Some(6), false, false)),
            (Some(v), None) => Err(no(format!(
                "sa64 = {v:#x} at pa0 {:#x}: only pa0 and pa0 with bit 1 clear were run (E792 A4, A5)",
                i.pa0
            ))),
            (None, Some(w)) => sa65_row(i, w, kept(Some(0x98), true, false), stalled),
            (Some(_), Some(_)) => Err(no("sa64 and sa65 written together: not run".into())),
        },
        (PassKind::Kick, PassEnd::OwnEnd { .. } | PassEnd::Exit) if !writes => Err(no(format!(
            "a kick pass ending {:?}: not run (E813 B3 ran idf, wdf, nop.end only; row KP of round 4, Q152)",
            i.end
        ))),
        _ => Err(no(format!(
            "{:?} pass ending {:?}{}: not measured (E791 to E793, E812 to E814, E817, E830)",
            i.kind,
            i.end,
            if writes { " with an sa64 or sa65 write" } else { "" }
        ))),
    }
}

fn sa65_row(
    i: &Inputs,
    w: u32,
    ok: AfterPass,
    stalled: impl Fn(i32, u32) -> AfterPass,
) -> Result<AfterPass, Error> {
    let k = u32::from(K_MEASURED) << 24;
    if i.sa65_count != K_MEASURED {
        return Err(no(format!("sa65 count byte {}: only {K_MEASURED} was run", i.sa65_count)));
    }
    match w {
        // kept: E791 A2 (the entry value), E812 C1 to C4
        _ if w == k || w == k | 1 << 23 || w == k | 0x0001_c04c || w == k | 1 << 19 => Ok(ok),
        0xb000_0000 => Ok(ok),
        // stalled with the marks: E814 D2 (bit 8 alone), E537 (one run; it also wrote sa63, sa64
        // and others, so the word is not the only difference there)
        _ if w == k | 0x100 => Ok(stalled(1, MARKS_DWORD14)),
        0xb009_c5dc => Ok(stalled(1, MARKS_DWORD14)),
        // stalled without them: E814 D1
        0xb009_c4dc => Ok(stalled(0, 0)),
        _ => Err(no(format!("sa65 = {w:#x}: not run (bits 4, 7 and 10 are untried)"))),
    }
}

/// Whether a later event is delivered after this pass: refused once stalled (E793, E537, E817,
/// E830), and a host command sent into the stall was not answered (E814 P3, E817, E818, E830).
pub fn deliver_after(a: &AfterPass) -> Result<(), Error> {
    match a.tick {
        Tick::Kept => Ok(()),
        Tick::Stalled => Err(no(
            "stalled EDM: no later event is delivered until a debugfs reset (E793, E537, E817, E830) \
             and a host command sent into it was not answered (E814 P3, E817, E818, E830: 0 of 7)"
                .into(),
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const K: u32 = (K_MEASURED as u32) << 24;
    /// E793's end: `idf`, `wdf`, `nop.end`.
    const OWN: PassEnd = PassEnd::OwnEnd { cfi: false, phas: false };

    fn tick(end: PassEnd) -> Inputs {
        Inputs::plain(PassKind::Tick, end)
    }

    fn with65(w: u32) -> Inputs {
        Inputs { sa65: Some(w), ..tick(PassEnd::Closed { slot: 0 }) }
    }

    fn refused(i: Inputs) -> bool {
        matches!(end_of_pass(&i), Err(Error::Unsupported { .. }))
    }

    #[test]
    fn closed_general_task_keeps_the_tick() {
        // E791 A0/A6, E792: 19 of 19 kept.
        let a = end_of_pass(&tick(PassEnd::Closed { slot: 0 })).unwrap();
        assert_eq!(a.tick, Tick::Kept);
        assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (0, 0));
        assert_eq!(a.dword12_advances, Some(true));
        assert_eq!(a.next_pclink, Some(0x98));
        assert!(!a.next_on_grid);
    }

    #[test]
    fn sa64_with_tick_bit_clear_leaves_pclink_6() {
        // E792 A4 3 of 3, E812 C5.
        let i = Inputs { sa64: Some(2 & !2), ..tick(PassEnd::Closed { slot: 0 }) };
        let a = end_of_pass(&i).unwrap();
        assert_eq!(a.tick, Tick::Kept);
        assert_eq!(a.next_pclink, Some(6));
        assert_eq!(a.dword12_advances, Some(false));
        let i = Inputs { pa0: 0x1002, sa64: Some(0x1000), ..i };
        assert_eq!(end_of_pass(&i).unwrap().next_pclink, Some(6));
    }

    #[test]
    fn sa64_equal_pa0_is_an_ordinary_tick() {
        // E792 A5.
        let i = Inputs { sa64: Some(2), ..tick(PassEnd::Closed { slot: 0 }) };
        let a = end_of_pass(&i).unwrap();
        assert_eq!((a.tick, a.next_pclink, a.dword12_advances), (Tick::Kept, Some(0x98), Some(true)));
    }

    #[test]
    fn other_sa64_values_are_refused() {
        for v in [1, 3, 4, 0x10, 0xffff_ffff] {
            assert!(refused(Inputs { sa64: Some(v), ..tick(PassEnd::Closed { slot: 0 }) }), "{v:#x}");
        }
        // pa0 without the tick bit makes "pa0 & !2" indistinguishable from pa0.
        let i = Inputs { pa0: 0, sa64: Some(0), ..tick(PassEnd::Closed { slot: 0 }) };
        assert!(refused(i));
    }

    #[test]
    fn sa65_words_that_kept_the_tick() {
        // E791 A2, E812 C1 to C4.
        for w in [K, K | 1 << 23, 0xb000_0000, K | 0x0001_c04c, K | 1 << 19] {
            let a = end_of_pass(&with65(w)).unwrap();
            assert_eq!(a.tick, Tick::Kept, "{w:#x}");
            assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (0, 0), "{w:#x}");
            assert_eq!(a.dword12_advances, Some(true), "{w:#x}");
        }
    }

    #[test]
    fn sa65_bit_8_alone_stalls_with_the_marks() {
        // E814 D2 and E537.
        for w in [K | 0x100, 0xb009_c5dc] {
            let a = end_of_pass(&with65(w)).unwrap();
            assert_eq!(a.tick, Tick::Stalled, "{w:#x}");
            assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (1, MARKS_DWORD14), "{w:#x}");
            assert_eq!(a.dword12_advances, None);
        }
    }

    #[test]
    fn sa65_e537_word_without_bit_8_stalls_without_the_marks() {
        // E814 D1.
        let a = end_of_pass(&with65(0xb009_c4dc)).unwrap();
        assert_eq!(a.tick, Tick::Stalled);
        assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (0, 0));
    }

    #[test]
    fn other_sa65_words_are_refused() {
        for bit in [4, 7, 10] {
            assert!(refused(with65(K | 1 << bit)), "bit {bit} untried");
        }
        assert!(refused(with65(0)));
        // a count byte other than the one the runs had
        let i = Inputs { sa65_count: 3, ..with65(3 << 24) };
        assert!(refused(i));
        // sa65 words only measured on a tick pass with the general task
        assert!(refused(Inputs { end: OWN, ..with65(K) }));
        assert!(refused(Inputs { kind: PassKind::Kick, pa0: 0, ..with65(K) }));
    }

    #[test]
    fn slot_2_on_a_tick_pass_keeps_the_tick_on_the_grid() {
        // E813 X1, X20.
        let a = end_of_pass(&tick(PassEnd::Closed { slot: 2 })).unwrap();
        assert_eq!(a.tick, Tick::Kept);
        assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (0, 0));
        assert!(a.next_on_grid);
        assert_eq!(a.dword12_advances, Some(false));
    }

    #[test]
    fn other_slots_are_not_run() {
        assert!(refused(Inputs::plain(PassKind::Kick, PassEnd::Closed { slot: 2 })));
        for slot in [1, 3, 4, 255] {
            assert!(refused(tick(PassEnd::Closed { slot })), "tick {slot}");
            assert!(refused(Inputs::plain(PassKind::Kick, PassEnd::Closed { slot })), "kick {slot}");
        }
    }

    #[test]
    fn own_end_stalls() {
        // E793 B1 (tick), E813 B3 (kick).
        let a = end_of_pass(&tick(OWN)).unwrap();
        assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Stalled, 0, 0));
        let a = end_of_pass(&Inputs::plain(PassKind::Kick, OWN)).unwrap();
        assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Stalled, -1, 0));
        assert_eq!(a.dword12_advances, None);
    }

    #[test]
    fn unlisted_combinations_are_refused() {
        let both = Inputs { sa64: Some(0), sa65: Some(K), ..tick(PassEnd::Closed { slot: 0 }) };
        assert!(refused(both));
        assert!(refused(Inputs::plain(PassKind::Kick, PassEnd::Closed { slot: 0 })));
        assert!(refused(Inputs { sa64: Some(2), ..tick(OWN) }));
        assert!(refused(Inputs { sa64: Some(2), ..tick(PassEnd::Closed { slot: 2 }) }));
    }

    #[test]
    fn a_stalled_edm_delivers_nothing_and_answers_no_command() {
        // E793, E537; E814 P3.
        let kept = end_of_pass(&tick(PassEnd::Closed { slot: 0 })).unwrap();
        assert!(deliver_after(&kept).is_ok());
        let stalled = end_of_pass(&tick(OWN)).unwrap();
        assert!(matches!(deliver_after(&stalled), Err(Error::Unsupported { .. })));
    }

    #[test]
    fn a_tick_pass_ended_with_the_phas_end_keeps_the_tick() {
        // E817 FB 2 of 2 and FPH 2 of 2, E830 fb 6 of 6 and fk 3 of 3: with or without the
        // cfi.global, the next entry 24994 or 24995 units after the acted pass
        for cfi in [true, false] {
            let a = end_of_pass(&tick(PassEnd::OwnEnd { cfi, phas: true })).unwrap();
            assert_eq!(a.tick, Tick::Kept, "cfi {cfi}");
            assert_eq!((a.ccb_read_minus_write, a.hostctl_dword14), (0, 0));
            assert_eq!(a.next_gap, Some(PHAS_END_GAP));
            assert!(deliver_after(&a).is_ok());
            // what the runs did not read is not given
            assert_eq!((a.dword12_advances, a.next_pclink), (None, None));
        }
        assert_eq!(PHAS_END_GAP, (24994, 24995));
    }

    #[test]
    fn a_tick_pass_ended_without_the_phas_end_stalls() {
        // E817 FCF and E830 fcf1 to fcf3 (cfi.global, idf, wdf, nop.end: 4 of 4), E793 B1 (2 of 2)
        for cfi in [true, false] {
            let a = end_of_pass(&tick(PassEnd::OwnEnd { cfi, phas: false })).unwrap();
            assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Stalled, 0, 0));
            assert_eq!((a.dword12_advances, a.next_gap), (None, None));
        }
    }

    #[test]
    fn the_closed_exit_reached_by_cont4_keeps_the_tick() {
        // E817 FC4 2 of 2, E830 fc4 6 of 6
        let a = end_of_pass(&tick(PassEnd::Exit)).unwrap();
        assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Kept, 0, 0));
        assert_eq!(a.next_gap, Some(PHAS_END_GAP));
    }

    #[test]
    fn the_phas_end_and_the_exit_on_a_kick_pass_are_refused() {
        // rows KP (H-PHAS-ANY against H-KICK-MORE) and the exit on a kick pass did not run; a
        // kick pass ended with cfi.global and no phas did not run either (E813 B3 had no cfi)
        for end in [
            PassEnd::OwnEnd { cfi: false, phas: true },
            PassEnd::OwnEnd { cfi: true, phas: true },
            PassEnd::OwnEnd { cfi: true, phas: false },
            PassEnd::Exit,
        ] {
            assert!(refused(Inputs::plain(PassKind::Kick, end)), "{end:?}");
        }
    }

    #[test]
    fn the_handlers_timer_word_then_the_closed_task_keeps_the_tick_and_moves_the_next_entry() {
        // E818 T1, 2 of 2: str of 0x01061a80 to CR_EVENT_TIMER, then the closed task; the next
        // entry 25114 units after the acted pass in both
        let i = Inputs { timer_store: Some(TIMER_WORD_RUN), ..tick(PassEnd::Closed { slot: 0 }) };
        let a = end_of_pass(&i).unwrap();
        assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Kept, 0, 0));
        assert_eq!(a.next_gap, Some((25114, 25114)));
        assert_eq!((a.dword12_advances, a.next_pclink), (None, None));
        assert_eq!(TIMER_WORD_RUN, 0x0106_1a80);
    }

    #[test]
    fn the_timer_word_then_our_own_end_stalls() {
        // E818 T2, 1 job: the store does not replace the phas end
        let i = Inputs { timer_store: Some(TIMER_WORD_RUN), ..tick(OWN) };
        let a = end_of_pass(&i).unwrap();
        assert_eq!((a.tick, a.ccb_read_minus_write, a.hostctl_dword14), (Tick::Stalled, 0, 0));
    }

    #[test]
    fn other_timer_stores_are_refused() {
        // another word, another end, a kick pass, or with an sa64 or sa65 write: not run
        let with = |w: u32, end: PassEnd| Inputs { timer_store: Some(w), ..tick(end) };
        for w in [0, 0x0106_1a70, 0x0100_0000, 0x0106_1a81] {
            assert!(refused(with(w, PassEnd::Closed { slot: 0 })), "{w:#x}");
        }
        for end in [
            PassEnd::Closed { slot: 2 },
            PassEnd::OwnEnd { cfi: false, phas: true },
            PassEnd::OwnEnd { cfi: true, phas: false },
            PassEnd::Exit,
        ] {
            assert!(refused(with(TIMER_WORD_RUN, end)), "{end:?}");
        }
        let kick = Inputs { timer_store: Some(TIMER_WORD_RUN), ..Inputs::plain(PassKind::Kick, OWN) };
        assert!(refused(kick));
        let both = Inputs { sa64: Some(2), ..with(TIMER_WORD_RUN, PassEnd::Closed { slot: 0 }) };
        assert!(refused(both));
    }

    #[test]
    fn sa64_and_sa65_writes_with_the_new_ends_are_refused() {
        for end in [PassEnd::OwnEnd { cfi: false, phas: true }, PassEnd::Exit] {
            assert!(refused(Inputs { sa64: Some(2), ..tick(end) }), "{end:?}");
            assert!(refused(Inputs { sa65: Some(K), ..tick(end) }), "{end:?}");
        }
    }
}
