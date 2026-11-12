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
//! 5. The end of a tick pass (E817, E830): kept if and only if the pass executes the `phas`
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
//! (E835's row KP kept the tick 2 of 2 and is not taken here yet; the slot 3 pass, E836, is not a
//! [`PassKind`] here: [`skipped_render`] gives its later stop), sa64 and sa65 written together, any sa64 or sa65 write with another end, a
//! timer store of another word, with another end or with an sa64 or sa65 write, and a count byte
//! other than 2. Which of dword
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
            "a kick pass ending {:?}: not modelled (E813 B3 ran idf, wdf, nop.end; E835 the phas end, not taken yet)",
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

/// TA3DCtl dword 58 (`+0xe8`) at every marked stop read: E849's and the 10 of E855 to E857.
pub const SIGNATURE_3D_READ: u32 = 0xaac2_67c2;

/// What the host did between the slot 3 entry and the stop (round 5's r5-events).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HostBeforeStop {
    /// No host write and no command (stages h1 and h2).
    Nothing,
    /// `CR_EVENT_HOST_CLEAR` bit 15, then bit 18, at the slot 3 entry, then one GETMISCINFO,
    /// answered (stage h3).
    ClearsThenMiscinfo,
}

/// A fill whose slot 3 end-of-render pass our task skipped once and ended with the `phas` end
/// (`ring_skip3p.s`, E836), the knob `timer_clock` giving HostCtl dword 6.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SkippedRender {
    /// HostCtl dword 6 (`host_ctl.ukernel_timer_clock`; the knob 0 gives 400000).
    pub timer_clock: u32,
    /// HostCtl dword 5 (`host_ctl.hw_recovery_sample_rate`).
    pub hw_recovery_sample_rate: u32,
    pub host: HostBeforeStop,
}

/// The stop after a [`SkippedRender`], as the stop dumps read it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Lockup {
    /// Slot 0 passes from the fill's kick entry to the stop.
    pub passes_after_kick: u32,
    /// HostCtl dword 3 at the stop less at the arm (`host_ctl.ukernel_detected_lockups`).
    pub lockups: u32,
    /// HostCtl dword 8 (`host_ctl.interrupt_flags`).
    pub interrupt_flags: u32,
    /// The kernel's count of `SW_EVENT` interrupts.
    pub sw_events: u32,
    /// TA3DCtl dword 57 (`ta3d_ctl.kick_clear_3d`).
    pub kick_clear_3d: u32,
    /// TA3DCtl dword 58.
    pub signature_3d: u32,
    /// `CR_EVENT_STATUS` at the stop.
    pub event_status: u32,
    /// `CR_DPM_TASK_STATE` (0x0694) read at the stop, where it was read: 0 at 400000 with no
    /// host write before the stop (E890, the r6 kernel's peek), not the 2 R-6 reads stored
    /// [RE]; `None` where it was not read (E856, E857: the rgn4 kernel never reads it).
    pub dpm_task_state: Option<u32>,
    pub ccb_read_minus_write: i32,
    pub after: AfterPass,
}

/// One tick in `CR_TIMER` units at HostCtl dword 6, for the clocks whose grid was read (E084,
/// E855, E856: 25000, 50000, 100000); others `None`.
pub fn tick_units(timer_clock: u32) -> Option<u32> {
    matches!(timer_clock, 400_000 | 800_000 | 1_600_000).then_some(timer_clock / 16)
}

/// The stop after slot 3's end-of-render pass skipped and ended with the `phas` end: the EDM's
/// 3D lockup check, 20 slot 0 passes after the fill's kick entry (2 x dword 5) at the three
/// clocks run, with the marks (E855: 3 of 3 at 400000; E856: 2 of 2 at 800000 and at 1600000,
/// the count in passes and not in time; E857: 3 of 3 at 1600000 with the host's clears of
/// bits 15 and 18 and one answered GETMISCINFO before it). [RE] (R-6, E855) the check is armed
/// while sa9 bit 0 is set, which the skipped handler would have cleared; the sim models the
/// measured outcome, not the firmware. Refused: another dword 5, another clock, the clears at
/// another clock (not run), a skip without the `phas` end (E823: a stop at once, no marks).
/// `CR_DPM_TASK_STATE` read 0 at the stop (E890, 2 of 2 at 400000): R-6's store of 2 before
/// the poll is not seen on the hardware.
pub fn skipped_render(s: &SkippedRender) -> Result<Lockup, Error> {
    if s.hw_recovery_sample_rate != 10 {
        return Err(no(format!(
            "hw_recovery_sample_rate {}: only 10 was run (E855, E856)",
            s.hw_recovery_sample_rate
        )));
    }
    if tick_units(s.timer_clock).is_none() {
        return Err(no(format!(
            "timer_clock {}: only 400000, 800000 and 1600000 were run (E855, E856)",
            s.timer_clock
        )));
    }
    let event_status = match (s.host, s.timer_clock) {
        (HostBeforeStop::Nothing, _) => 0x2004_0000,
        (HostBeforeStop::ClearsThenMiscinfo, 1_600_000) => 0x2000_0000,
        (HostBeforeStop::ClearsThenMiscinfo, c) => {
            return Err(no(format!(
                "the clears before the stop at timer_clock {c}: run at 1600000 only (E857)"
            )));
        }
    };
    Ok(Lockup {
        passes_after_kick: 2 * s.hw_recovery_sample_rate,
        lockups: 1,
        interrupt_flags: 1,
        sw_events: 1,
        kick_clear_3d: 0,
        signature_3d: SIGNATURE_3D_READ,
        event_status,
        dpm_task_state: (s.timer_clock == 400_000 && s.host == HostBeforeStop::Nothing).then_some(0),
        ccb_read_minus_write: 0,
        after: AfterPass {
            tick: Tick::Stalled,
            ccb_read_minus_write: 0,
            hostctl_dword14: 0,
            dword12_advances: None,
            next_pclink: None,
            next_on_grid: false,
            next_gap: None,
        },
    })
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
        // row KP (E835: the phas end kept the tick, 2 of 2) is not taken here yet, and the exit
        // and cfi.global on a kick pass did not run (E813 B3 had no cfi)
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

    fn skipped(timer_clock: u32, host: HostBeforeStop) -> SkippedRender {
        SkippedRender { timer_clock, hw_recovery_sample_rate: 10, host }
    }

    #[test]
    fn a_skipped_slot_3_pass_ended_with_the_phas_end_stops_after_twenty_tick_passes_with_the_marks() {
        // E855 (h1, 3 of 3 at 400000), E856 (h2, 2 of 2 at 800000 and 2 of 2 at 1600000): the
        // count is in tick passes, 2 x hw_recovery_sample_rate, whatever the clock
        for clock in [400_000, 800_000, 1_600_000] {
            let l = skipped_render(&skipped(clock, HostBeforeStop::Nothing)).unwrap();
            assert_eq!(l.passes_after_kick, 20, "{clock}");
            assert_eq!((l.lockups, l.interrupt_flags, l.sw_events), (1, 1, 1), "{clock}");
            assert_eq!((l.kick_clear_3d, l.signature_3d), (0, SIGNATURE_3D_READ), "{clock}");
            assert_eq!(l.event_status, 0x2004_0000, "{clock}: bit 18 a level, bit 6 clear");
            assert_eq!(l.ccb_read_minus_write, 0);
            assert_eq!(l.after.tick, Tick::Stalled);
            assert!(deliver_after(&l.after).is_err(), "P3 was not answered, 0 of 10");
        }
        // so its time follows the tick: one tick is dword 6 / 16 CR_TIMER units (E084)
        assert_eq!(tick_units(400_000), Some(25_000));
        assert_eq!(tick_units(800_000), Some(50_000));
        assert_eq!(tick_units(1_600_000), Some(100_000));
    }

    #[test]
    fn cr_dpm_task_state_reads_zero_at_the_stop_where_it_was_read() {
        // E890 (r6-held part P, 2 of 2 at 400000, the r6 kernel's peek): 0x0694 read 0 at the
        // stop as at the arm; R-6's store of 2 is not seen. Not read at the other clocks or with
        // the clears before the stop (E856, E857 ran on the rgn4 kernel): None.
        let l = skipped_render(&skipped(400_000, HostBeforeStop::Nothing)).unwrap();
        assert_eq!(l.dpm_task_state, Some(0));
        for clock in [800_000, 1_600_000] {
            let l = skipped_render(&skipped(clock, HostBeforeStop::Nothing)).unwrap();
            assert_eq!(l.dpm_task_state, None, "{clock}");
        }
        let l = skipped_render(&skipped(1_600_000, HostBeforeStop::ClearsThenMiscinfo)).unwrap();
        assert_eq!(l.dpm_task_state, None);
    }

    #[test]
    fn the_host_clears_and_a_miscinfo_before_the_stop_change_nothing_but_bit_18() {
        // E857 (h3, 3 of 3 at 1600000): CLEAR of bit 15 then bit 18 at the slot 3 entry, one
        // GETMISCINFO answered after them; the stop still came at 20 passes from the fill's kick
        let l = skipped_render(&skipped(1_600_000, HostBeforeStop::ClearsThenMiscinfo)).unwrap();
        assert_eq!(l.passes_after_kick, 20);
        assert_eq!((l.lockups, l.interrupt_flags, l.sw_events), (1, 1, 1));
        assert_eq!(l.event_status, 0x2000_0000);
        assert_eq!(l.after.tick, Tick::Stalled);
    }

    #[test]
    fn what_the_session_did_not_run_is_refused() {
        // other clocks, another sample rate, the clears at the stock or 800000 clock
        for clock in [0, 200_000, 400_001, 1_200_000, 3_200_000] {
            assert!(skipped_render(&skipped(clock, HostBeforeStop::Nothing)).is_err(), "{clock}");
        }
        for clock in [400_000, 800_000] {
            let s = skipped(clock, HostBeforeStop::ClearsThenMiscinfo);
            assert!(skipped_render(&s).is_err(), "{clock}");
        }
        for rate in [0, 5, 20] {
            let s =
                SkippedRender { hw_recovery_sample_rate: rate, ..skipped(400_000, HostBeforeStop::Nothing) };
            assert!(skipped_render(&s).is_err(), "{rate}");
        }
        assert_eq!(tick_units(1_200_000), None);
    }

    #[test]
    fn sa64_and_sa65_writes_with_the_new_ends_are_refused() {
        for end in [PassEnd::OwnEnd { cfi: false, phas: true }, PassEnd::Exit] {
            assert!(refused(Inputs { sa64: Some(2), ..tick(end) }), "{end:?}");
            assert!(refused(Inputs { sa65: Some(K), ..tick(end) }), "{end:?}");
        }
    }
}
