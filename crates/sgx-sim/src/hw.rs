// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The hardware as the firmware's register reads see it, for the firmware-in-sim track
//! (fwsim): every read is answered by exactly one source, or the run stops.
//!
//! The sources, in the order they are asked (`Source`):
//! 1. a landed rule that claims the register (a value that moves with the events served, E009;
//!    the idle words of CR_EVENT_STATUS and CR_CACHE_CTRL until a kick, E1115, E1120;
//!    CR_CACHE_CTRL after a kick, E1122);
//! 2. a value the run wrote (the firmware's `str`, the host's writes);
//! 3. a seed, each citing the record whose reading gives it (an E-number, refused without one);
//! 4. a reset value from a kept snapshot (the caller passes only the registers the kept
//!    snapshots agree on, so a value the hardware moves is never answered from it).
//!
//! Anything else stops the run with `Error::Unsupported` naming the register, and the open
//! questions the caller noted for it. No default 0, no "last seen". The model knows nothing
//! of the firmware: which registers it reads is what a run finds out.

use crate::Error;
use std::collections::BTreeMap;

/// What answered a register read.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    /// A rule landed in the simulator (its record in the name).
    Rule(&'static str),
    /// A value the run wrote.
    Written,
    /// A seed (the caller's value; under a `HwModel`, a cited one).
    Seed,
    /// The kept snapshot's reset value.
    Reset,
}

impl Source {
    pub fn name(&self) -> String {
        match self {
            Source::Rule(r) => format!("rule:{r}"),
            Source::Written => "written".into(),
            Source::Seed => "seed".into(),
            Source::Reset => "reset".into(),
        }
    }
}

/// `CR_USE0_SERV_EVENT` (0x0b14): bit 16 always set, bits 15:0 counting once a tick, 3 ahead of
/// HostCtl dword 12 (E009, 186 of 200 snapshots; the after-boot snapshot of `platform/boot-
/// registers` too). Only a run of ticks was measured: once anything else is served (a kick) the
/// count is not known and a read of it is refused.
pub const USE0_SERV_EVENT: u32 = 0x0b14 / 4;

/// `CR_EVENT_STATUS` (0x012c): 0x20000000 (TIMER) in every sample outside a plain triangle, through
/// the ticks of the lead (E1115, 14 of 14 rows; E547's idle controls). Inside a job the word moves:
/// bit 26 shows as 0x24000000 before the render end, not in every job, at a time after the
/// CR_CACHE_CTRL write that no kept reading gives (E1115), so after a served event other than a
/// tick a read is refused.
pub const EVENT_STATUS: u32 = 0x012c / 4;

/// `CR_CACHE_CTRL` (0x0804): 0x0000ffff after a reset, through the ticks (E1120: the first sample
/// of 24 of 24 rows; the kit's snapshots after its reset). From one change that comes before every
/// event of the job to the reset it reads 0x1000ffff (E1120 24 of 24 rows, E1122 and E1123 52 of
/// 52, a fill's kick as a triangle's). In the two rows that order it against the firmware's first
/// response, the kick pass's BIF write (E1122, E1123: CR_BIF_CTRL 0x8 for 4 to 8 us, gone in the
/// change's sample), the change comes after it, so the hardware does not set the bit at the kick
/// [infer: it is the firmware's own `| 0x10000000`, E013]. After a kick a read answers the reset
/// word until the run writes the register, and the run's write after it; whether the read itself
/// came before the change is not measured, but E013 gives the value read no test, only the `|`
/// and the write, so either answer writes 0x1000ffff. A write after the kick of any other word is
/// not measured, and a read is refused.
pub const CACHE_CTRL: u32 = 0x0804 / 4;

#[derive(Clone, Debug)]
struct Counted {
    value: u32,
    cite: String,
    /// Why the count is no longer known, once it is not.
    lost: Option<String>,
}

/// The hardware model: reset values, cited seeds, the landed read rules and the refusals.
#[derive(Clone, Debug, Default)]
pub struct HwModel {
    reset: BTreeMap<u32, u32>,
    reset_cite: String,
    seeds: BTreeMap<u32, (u32, String)>,
    serv_event: Option<Counted>,
    event_idle: Option<Counted>,
    cache_idle: Option<Counted>,
    /// What the run wrote to CR_CACHE_CTRL after the kick that ended `cache_idle`, if anything.
    cache_written: Option<u32>,
    open: BTreeMap<u32, String>,
    /// The reads refused, by register: what a run lists (offsets and counts).
    pub refused: BTreeMap<u32, u32>,
    /// The reads answered, by source name (counts).
    pub answered: BTreeMap<String, u64>,
}

/// An E-number (E followed by three or four digits) somewhere in `cite`.
fn cites_a_record(cite: &str) -> bool {
    let b = cite.as_bytes();
    (0..b.len()).any(|i| {
        b[i] == b'E' && (i == 0 || !b[i - 1].is_ascii_alphanumeric()) && {
            let n = b[i + 1..].iter().take_while(|c| c.is_ascii_digit()).count();
            (3..=4).contains(&n)
        }
    })
}

impl HwModel {
    /// The kept snapshot the reset values come from (a record or a dataset), named in refusals.
    pub fn reset_from(&mut self, cite: &str) {
        self.reset_cite = cite.to_string();
    }

    /// A reset value: the register as the kept snapshots read it before the run touched it.
    pub fn reset(&mut self, index: u32, value: u32) {
        self.reset.insert(index, value);
    }

    /// A seed: a value a record's reading gives. Refused without an E-number in `cite`.
    pub fn seed(&mut self, index: u32, value: u32, cite: &str) -> Result<(), String> {
        if !cites_a_record(cite) {
            return Err(format!("seed of register 0x{:04x} cites no record: {cite:?}", index * 4));
        }
        self.seeds.insert(index, (value, cite.to_string()));
        Ok(())
    }

    /// The E009 rule for `CR_USE0_SERV_EVENT`: `value` now (bit 16 and the count), one count a
    /// tick from here on. Refused without an E-number.
    pub fn count_serv_events(&mut self, value: u32, cite: &str) -> Result<(), String> {
        if !cites_a_record(cite) {
            return Err(format!("the served-event count cites no record: {cite:?}"));
        }
        self.serv_event = Some(Counted { value, cite: cite.to_string(), lost: None });
        Ok(())
    }

    /// The E1115 rule for `CR_EVENT_STATUS`: `value` (the idle word) until a served event other
    /// than a tick. Refused without an E-number.
    pub fn idle_event_status(&mut self, value: u32, cite: &str) -> Result<(), String> {
        if !cites_a_record(cite) {
            return Err(format!("the idle event status cites no record: {cite:?}"));
        }
        self.event_idle = Some(Counted { value, cite: cite.to_string(), lost: None });
        Ok(())
    }

    /// The E1120 rule for `CR_CACHE_CTRL`: `value` (the word after a reset) until a served event
    /// other than a tick. Refused without an E-number.
    pub fn idle_cache_ctrl(&mut self, value: u32, cite: &str) -> Result<(), String> {
        if !cites_a_record(cite) {
            return Err(format!("the cache control word cites no record: {cite:?}"));
        }
        self.cache_idle = Some(Counted { value, cite: cite.to_string(), lost: None });
        Ok(())
    }

    /// A register write of the run (the firmware's `str`, the host's): CR_CACHE_CTRL's after a
    /// kick is what a later read answers (E1122); before the kick a write changes nothing the rule
    /// answers (the reset word, E1120).
    pub fn on_write(&mut self, index: u32, value: u32) {
        if index == CACHE_CTRL && self.cache_idle.as_ref().is_some_and(|c| c.lost.is_some()) {
            self.cache_written = Some(value);
        }
    }

    /// What a refusal of `index` says beside the register (the open questions that block it).
    pub fn note_open(&mut self, index: u32, note: &str) {
        self.open.insert(index, note.to_string());
    }

    /// An event the hardware delivers: a timer tick (ir0 bit 1, nothing in ir1's bits 23:0)
    /// advances the served-event count; anything else makes it unknown (E009 ran ticks only).
    pub fn on_event(&mut self, ir0: Option<u32>, ir1: u32) {
        let tick = ir0.is_some_and(|v| v & 2 != 0) && ir1 & 0x00ff_ffff == 0;
        if let Some(c) = &mut self.event_idle
            && c.lost.is_none()
            && !tick
        {
            c.lost = Some(format!(
                "a job is running (ir0 {}, ir1 {ir1:#010x} served): {} gives the idle word outside a job only; \
                 in a plain triangle bit 26 shows as 0x24000000 (once 0xa4004000, with SW_EVENT; E1120) \
                 before the render end, not in every job, and when it shows after the CR_CACHE_CTRL \
                 write is not measured",
                ir0.map_or("unknown".to_string(), |v| format!("{v:#x}")),
                c.cite
            ));
        }
        if let Some(c) = &mut self.cache_idle
            && c.lost.is_none()
            && !tick
        {
            c.lost = Some(format!(
                "a kick was served (ir0 {}, ir1 {ir1:#010x}): {} gives 0x0000ffff after a reset; E1122: the reset word \
                 until the run writes it after the kick, then 0x1000ffff (held to the reset, E1120, E1122, E1123); \
                 no other written word is measured",
                ir0.map_or("unknown".to_string(), |v| format!("{v:#x}")),
                c.cite
            ));
        }
        if let Some(c) = &mut self.serv_event
            && c.lost.is_none()
        {
            if tick {
                c.value = 0x0001_0000 | (c.value.wrapping_add(1) & 0xffff);
            } else {
                c.lost = Some(format!(
                    "an event other than a tick was served (ir0 {}, ir1 {ir1:#010x}): whether it counts is \
                     not measured ({} ran ticks only; E1120: a plain triangle adds 9 to 11 counts beyond \
                     the ticks, which events count is not measured)",
                    ir0.map_or("unknown".to_string(), |v| format!("{v:#x}")),
                    c.cite
                ));
            }
        }
    }

    /// Answer a read of `index`; `written` is what the run wrote there, if anything.
    pub fn read(&mut self, index: u32, written: Option<u32>) -> Result<(u32, Source), Error> {
        let r = self.answer(index, written);
        match &r {
            Ok((_, s)) => *self.answered.entry(s.name()).or_default() += 1,
            Err(_) => *self.refused.entry(index).or_default() += 1,
        }
        r
    }

    fn answer(&self, index: u32, written: Option<u32>) -> Result<(u32, Source), Error> {
        let refuse = |why: String| {
            let open = self.open.get(&index).map_or(String::new(), |o| format!(" ({o})"));
            Err(Error::Unsupported { pc: 0, text: String::new(), why: format!("{why}{open}") })
        };
        if index == USE0_SERV_EVENT
            && let Some(c) = &self.serv_event
        {
            return match &c.lost {
                None => Ok((c.value, Source::Rule("E009"))),
                Some(why) => refuse(format!("reads register 0x{:04x}: {why}", index * 4)),
            };
        }
        if index == EVENT_STATUS
            && let Some(c) = &self.event_idle
        {
            return match &c.lost {
                None => Ok((c.value, Source::Rule("E1115"))),
                Some(why) => refuse(format!("reads register 0x{:04x}: {why}", index * 4)),
            };
        }
        if index == CACHE_CTRL
            && let Some(c) = &self.cache_idle
        {
            return match (&c.lost, self.cache_written) {
                (None, _) => Ok((c.value, Source::Rule("E1120"))),
                (Some(_), None) => Ok((c.value, Source::Rule("E1122"))),
                (Some(_), Some(v)) if v == c.value | 0x1000_0000 => Ok((v, Source::Rule("E1122"))),
                (Some(why), Some(v)) => refuse(format!(
                    "reads register 0x{:04x} after the run wrote {v:#010x} to it: {why}",
                    index * 4
                )),
            };
        }
        if let Some(v) = written {
            return Ok((v, Source::Written));
        }
        if let Some((v, _)) = self.seeds.get(&index) {
            return Ok((*v, Source::Seed));
        }
        if let Some(v) = self.reset.get(&index) {
            return Ok((*v, Source::Reset));
        }
        refuse(format!(
            "reads register 0x{:04x}: no run write, cited seed, landed rule or kept snapshot ({}) answers it",
            index * 4,
            if self.reset_cite.is_empty() { "none" } else { &self.reset_cite }
        ))
    }

    /// The seeds, with their citations (for a run's facts).
    pub fn seeds(&self) -> impl Iterator<Item = (u32, u32, &str)> {
        self.seeds.iter().map(|(i, (v, c))| (*i, *v, c.as_str()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn refused_naming(r: Result<(u32, Source), Error>, reg: &str) -> bool {
        matches!(r, Err(Error::Unsupported { ref why, .. }) if why.contains(reg))
    }

    #[test]
    fn a_read_is_answered_by_a_write_a_seed_a_reset_value_or_a_rule() {
        let mut hw = HwModel::default();
        hw.reset_from("platform/boot-registers before load");
        hw.reset(0x40 / 4, 0x1e00);
        hw.seed(0x1c / 4, 0x0115_0000, "E007: CORE_ID").unwrap();
        hw.count_serv_events(0x0001_0003, "E009").unwrap();
        assert_eq!(hw.read(0x100 / 4, Some(5)).unwrap(), (5, Source::Written));
        assert_eq!(hw.read(0x1c / 4, None).unwrap(), (0x0115_0000, Source::Seed));
        assert_eq!(hw.read(0x40 / 4, None).unwrap(), (0x1e00, Source::Reset));
        // a run's write wins over the seed and the snapshot
        assert_eq!(hw.read(0x40 / 4, Some(0x1ff)).unwrap(), (0x1ff, Source::Written));
        assert_eq!(hw.read(USE0_SERV_EVENT, None).unwrap(), (0x0001_0003, Source::Rule("E009")));
        // and the rule wins over the snapshot and a write: the hardware moves the count
        hw.reset(USE0_SERV_EVENT, 0x0001_0000);
        assert_eq!(hw.read(USE0_SERV_EVENT, Some(7)).unwrap().0, 0x0001_0003);
        assert_eq!(hw.answered["written"], 2);
    }

    #[test]
    fn anything_else_is_refused_naming_the_register_and_its_open_questions() {
        let mut hw = HwModel::default();
        hw.note_open(0x12c / 4, "Q111");
        assert!(refused_naming(hw.read(0x0a00 / 4, None), "0x0a00"));
        let r = hw.read(0x12c / 4, None);
        assert!(refused_naming(r.clone(), "0x012c") && refused_naming(r, "Q111"));
        assert_eq!(hw.refused.get(&(0x0a00 / 4)), Some(&1));
        assert_eq!(hw.refused.get(&(0x012c / 4)), Some(&1));
    }

    #[test]
    fn a_seed_without_an_e_number_is_refused_at_load() {
        let mut hw = HwModel::default();
        for cite in ["", "the laptop", "CORE_ID", "E12", "E12345", "XE007"] {
            assert!(hw.seed(7, 1, cite).is_err(), "{cite}");
        }
        assert!(hw.count_serv_events(0x0001_0003, "measured").is_err());
        hw.seed(7, 1, "E007").unwrap();
        hw.seed(8, 1, "CORE_REVISION (E007)").unwrap();
        assert_eq!(hw.seeds().count(), 2);
    }

    #[test]
    fn event_status_reads_the_idle_word_through_ticks_and_is_refused_after_a_kick() {
        // E1115 (with E547): 0x20000000 in every sample outside a plain triangle, through the
        // ticks of a 0.5 s lead; in the job the word moves (bit 26 as 0x24000000 at a time
        // after the CR_CACHE_CTRL write that no kept reading gives), so a read is refused
        let mut hw = HwModel::default();
        hw.idle_event_status(0x2000_0000, "E1115, E547").unwrap();
        assert_eq!(hw.read(EVENT_STATUS, None).unwrap(), (0x2000_0000, Source::Rule("E1115")));
        hw.on_event(Some(2), 0x0200_0000);
        assert_eq!(hw.read(EVENT_STATUS, None).unwrap().0, 0x2000_0000);
        hw.on_event(Some(0), 0x0200_0100);
        let r = hw.read(EVENT_STATUS, None);
        assert!(refused_naming(r.clone(), "0x012c") && refused_naming(r, "E1115"));
        // a later tick does not bring the idle word back: the job's end is not modelled
        hw.on_event(Some(2), 0x0300_0000);
        assert!(refused_naming(hw.read(EVENT_STATUS, None), "0x012c"));
        assert!(hw.idle_event_status(0x2000_0000, "the idle word").is_err());
    }

    #[test]
    fn cache_ctrl_reads_its_reset_word_until_the_runs_write_after_a_kick_then_that_write() {
        // E1120: 0x0000ffff after the reset through the ticks of the lead (24 of 24 rows' first
        // samples), 0x1000ffff from one change to the reset. E1122, E1123: the change follows the
        // firmware's BIF write of the kick pass (2 of 2 decided rows) and the word written is the
        // only one the hardware then reads, so after a kick the read before the run's own write
        // answers the reset word, the run's write after it, and only 0x1000ffff
        let mut hw = HwModel::default();
        hw.idle_cache_ctrl(0x0000_ffff, "E1120").unwrap();
        assert_eq!(hw.read(CACHE_CTRL, None).unwrap(), (0x0000_ffff, Source::Rule("E1120")));
        // a write before the kick (the boot's) is not what a read after the kick sees
        hw.on_write(CACHE_CTRL, 0x0000_1234);
        hw.on_event(Some(2), 0x0200_0000);
        assert_eq!(hw.read(CACHE_CTRL, Some(0x1234)).unwrap().0, 0x0000_ffff);
        hw.on_event(Some(0), 0x0200_0100);
        assert_eq!(hw.read(CACHE_CTRL, Some(0x1234)).unwrap(), (0x0000_ffff, Source::Rule("E1122")));
        hw.on_write(CACHE_CTRL, 0x1000_ffff);
        assert_eq!(hw.read(CACHE_CTRL, Some(0x1000_ffff)).unwrap(), (0x1000_ffff, Source::Rule("E1122")));
        // a later kick and tick keep it (held to the reset, E1120, E1122)
        hw.on_event(Some(0), 0x0300_0100);
        hw.on_event(Some(2), 0x0300_0000);
        assert_eq!(hw.read(CACHE_CTRL, Some(0x1000_ffff)).unwrap().0, 0x1000_ffff);
        // any other word written after the kick is not measured: refused
        hw.on_write(CACHE_CTRL, 0x0000_0008);
        let r = hw.read(CACHE_CTRL, Some(0x0000_0008));
        assert!(refused_naming(r.clone(), "0x0804") && refused_naming(r, "0x1000ffff"));
        assert!(hw.idle_cache_ctrl(0xffff, "after the reset").is_err());
    }

    #[test]
    fn the_served_event_count_is_refused_after_a_kick_naming_the_triangle_counts() {
        let mut hw = HwModel::default();
        hw.count_serv_events(0x0001_0003, "E009, E1120").unwrap();
        hw.on_event(Some(0), 0x0200_0100);
        assert!(refused_naming(hw.read(USE0_SERV_EVENT, None), "9 to 11"));
    }

    #[test]
    fn the_served_event_count_moves_once_a_tick_and_is_refused_after_a_kick() {
        // E009: bit 16 always set, bits 15:0 one count a tick; nothing else was measured
        let mut hw = HwModel::default();
        hw.count_serv_events(0x0001_fffe, "E009").unwrap();
        hw.on_event(Some(2), 0x0200_0000);
        assert_eq!(hw.read(USE0_SERV_EVENT, None).unwrap().0, 0x0001_ffff);
        hw.on_event(Some(2), 0x0200_0000);
        assert_eq!(hw.read(USE0_SERV_EVENT, None).unwrap().0, 0x0001_0000);
        hw.on_event(Some(0), 0x0200_0100);
        assert!(refused_naming(hw.read(USE0_SERV_EVENT, None), "0x0b14"));
        hw.on_event(Some(2), 0x0300_0000);
        assert!(refused_naming(hw.read(USE0_SERV_EVENT, None), "E009"));
    }
}
