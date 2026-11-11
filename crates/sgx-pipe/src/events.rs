// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Events: EVENT_STATUS bits, host events, ticks (12.6), and the STATUS2 latches over measured
//! timings: sgx-pipe has no clock, so a latch is a rule over a duration the caller measured.

use crate::Outcome;

/// Open questions that block the unit. Q082: of the STATUS2 latches only bit 6 of a 64 x 32 fill
/// without a load has a rule that held (`status2_bit6`); bit 6 with a load or in a triangle and bit
/// 7 stay refused (E805, E806, E807).
pub const OPEN: &[&str] = &["Q111", "Q033", "Q082", "Q166", "Q290"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("events are not modelled (12.6)", OPEN)
}

/// The work whose STATUS2 latch is asked about.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Work {
    /// A fill of a w x h target; `load`: its pixel program loads from memory.
    Fill { w: u32, h: u32, load: bool },
    /// A triangle's pixel programs.
    Triangle,
    /// A vertex program's loop.
    VertexLoop,
}

/// A measured timing: the burst, the time the job kept the units busy, in microseconds.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Timing {
    pub work: Work,
    pub burst_us: f64,
}

/// The time of one tile of a 64 x 32 fill (four tiles) from its burst: (B - 60.2) / 4 (round 3's
/// H-WD, E805).
pub fn tile_time_us(burst_us: f64) -> f64 {
    (burst_us - 60.2) / 4.0
}

/// The tile time below which bit 6 of a fill without a load stays clear, and above which it
/// sets; between them the edge, refused.
pub const BIT6_EDGE_US: (f64, f64) = (118.0, 132.0);

/// STATUS2 bit 6 after the work. A 64 x 32 fill without a load: clear for a tile time below 118
/// us, set above 132, refused between (Q082). This is H-WD of round 3 counted on the fills it
/// held on: E805 refuted it by the load body alone, and read after its run every no-load fill
/// set had a burst of at least 535.9 us and every clear one at most 539.3 us (tile times 118.9
/// and 119.8 us, inside the edge); the rule with this edge, frozen before the older timelines
/// were scored, held on 187 of 187 fills without a load (R3-pixel's 106 of E805 and 81 of the
/// platform timelines of E431 and E357, the round 4 reading of the kept timings). A fill with a
/// load (E805 ld8: never set), other targets, a triangle (E806, post hoc) and a vertex loop are
/// refused.
pub fn status2_bit6(t: &Timing) -> Result<bool, Outcome> {
    let no = |why: String| Err(Outcome::unsupported(&why, &["Q082"]));
    match t.work {
        Work::Fill { w: 64, h: 32, load: false } => {}
        Work::Fill { load: true, .. } => {
            return no("STATUS2 bit 6 of a fill with a load: no rule held (E805 ld8)".into());
        }
        w => {
            return no(format!(
                "STATUS2 bit 6 of {w:?}: only 64 x 32 fills without a load have a rule that held"
            ));
        }
    }
    if !t.burst_us.is_finite() || t.burst_us < 60.2 {
        return no(format!("a burst of {} us", t.burst_us));
    }
    let tau = tile_time_us(t.burst_us);
    match tau {
        _ if tau < BIT6_EDGE_US.0 => Ok(false),
        _ if tau > BIT6_EDGE_US.1 => Ok(true),
        _ => no(format!("a tile time of {tau:.1} us: inside the edge of 118 to 132 us")),
    }
}

/// STATUS2 bit 7: refused. The vertex loop's rule (the TA's run of busy clocks reaching about 125
/// us) is post hoc until a held-out run (E807; Q082).
pub fn status2_bit7(t: &Timing) -> Result<bool, Outcome> {
    Err(Outcome::unsupported(&format!("STATUS2 bit 7 of {:?}: no rule held (E807)", t.work), &["Q082"]))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_open_list_holds_the_questions_still_open_not_the_ones_e746_answered() {
        // E746 answered Q153 (the host-kick event) and Q157; the clear (Q166) stays open, and
        // so does Q290, narrowed by E768 to whether the hardware counts the EVENT_KICK writes or
        // reads the kernel's kicker word (sgx-sim's `event_count` counts the host kicks mod 256)
        assert!(OPEN.contains(&"Q166") && OPEN.contains(&"Q290"));
        assert!(!OPEN.contains(&"Q153") && !OPEN.contains(&"Q157"));
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

    fn fill(load: bool, burst_us: f64) -> Timing {
        Timing { work: Work::Fill { w: 64, h: 32, load }, burst_us }
    }

    /// The burst of a 64 x 32 fill whose tile time is `tau`.
    fn burst(tau: f64) -> f64 {
        60.2 + 4.0 * tau
    }

    fn refused_q082(r: Result<bool, Outcome>) -> bool {
        matches!(r, Err(Outcome::Unsupported { ref ids, .. }) if ids.iter().any(|i| i == "Q082"))
    }

    #[test]
    fn bit_6_of_a_fill_without_a_load_follows_its_tile_time_outside_the_edge() {
        // E805 read after the run: in the 106 fills without a load of q-f0, q-f1a and q-f1b every
        // set job had a burst of at least 535.9 us and every clear one at most 539.3 us; the rule
        // frozen with the edge 118 to 132 us of tile time held on 187 of 187 such fills
        assert!((tile_time_us(burst(125.0)) - 125.0).abs() < 1e-9);
        for tau in [0.0, 20.0, 100.0, 117.9] {
            assert_eq!(status2_bit6(&fill(false, burst(tau))), Ok(false), "{tau}");
        }
        for tau in [132.1, 140.0, 667.0, 3000.0] {
            assert_eq!(status2_bit6(&fill(false, burst(tau))), Ok(true), "{tau}");
        }
        // the edge: refused, with E805's two nearest bursts inside it
        for tau in [118.0, 118.9, 119.8, 125.0, 132.0] {
            assert!(refused_q082(status2_bit6(&fill(false, burst(tau)))), "{tau}");
        }
        for b in [535.9, 539.3] {
            assert!(refused_q082(status2_bit6(&fill(false, b))), "{b}");
        }
    }

    #[test]
    fn every_other_latch_is_refused() {
        // a fill with a load (E805 ld8: never set, H-WD refuted by it alone), other targets, a
        // triangle (E806, post hoc until q4-t), bit 7 (E807, post hoc until q4-v), bad timings
        assert!(refused_q082(status2_bit6(&fill(true, burst(200.0)))));
        assert!(refused_q082(status2_bit6(&fill(true, burst(50.0)))));
        for (w, h) in [(64, 64), (32, 32), (128, 32)] {
            let t = Timing { work: Work::Fill { w, h, load: false }, burst_us: burst(200.0) };
            assert!(refused_q082(status2_bit6(&t)), "{w} x {h}");
        }
        assert!(refused_q082(status2_bit6(&Timing { work: Work::Triangle, burst_us: burst(200.0) })));
        assert!(refused_q082(status2_bit6(&Timing { work: Work::VertexLoop, burst_us: burst(200.0) })));
        for b in [f64::NAN, f64::INFINITY, -1.0, 50.0] {
            assert!(refused_q082(status2_bit6(&fill(false, b))), "{b}");
        }
        for w in [fill(false, burst(200.0)), Timing { work: Work::VertexLoop, burst_us: 1000.0 }] {
            assert!(refused_q082(status2_bit7(&w)));
        }
    }
}
