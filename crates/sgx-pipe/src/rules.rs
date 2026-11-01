// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The status of each rule a unit function implements: measured, or fitted as a record states.
//!
//! D6 of the phase-12 plan: a rule is `Fitted` only where a record states the fit, and every
//! result that uses it is reported fitted, never matched. The table below is the one place to
//! change a rule's status. All four rules of 12.0 are marked fitted because their records
//! state a post hoc fit (E465: "fitted on the 1024 x 768 runs and the small targets"; E503:
//! "read post hoc from the 64 x 64 runs"; E542: "fitted post hoc to E180's 472 regions"; E541:
//! H70-F2 "written from the first run's 42 held-out jobs"); each was then checked on data it
//! was not fitted to, which the vector counts show, but the records call them fits.

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Status {
    Measured,
    /// fitted, as this record states
    Fitted(&'static str),
}

pub const ZLS_ADDRESS: Status = Status::Fitted("E465");
pub const TA_REGION_TEST: Status = Status::Fitted("E542");
pub const TA_OBJECT_FORMAT: Status = Status::Fitted("E541");
pub const ISP_MSAA_WINDOW: Status = Status::Fitted("E503");
/// The object's packed vertex block: 24-bit Y then X as (v + 4096) * 256, then the depth float
/// (12.2; E651, decoded from the dumps and held out)
pub const TA_PACKED_VERTICES: Status = Status::Fitted("E651");
/// Region headers' flags, the stream forms and where each stream block lands (12.2; E652)
pub const TA_STREAMS: Status = Status::Fitted("E652");
/// Triangle coverage: the exact centre-sample test with the left and top edges owning ties, over
/// vertices on the 1/256 pixel grid (12.3; E606 states the cell of its grid was fitted on 692
/// triangles and held out on 814; E607 the half-up rounding of the grid)
pub const ISP_COVERAGE: Status = Status::Fitted("E606");
/// The vertex grid of 1/256 pixel and its half-up rounding (12.3; E607). The scene path meets
/// vertices already on the grid (the TA packs them so, Q230), so the rounding itself runs only in
/// `arith`; the status is marked with the coverage because the grid is E607's finding (r123 D6).
pub const ISP_VERTEX_GRID: Status = Status::Fitted("E607");
/// The depth store's layout, when a job stores depth and the model reports it (E465, fitted):
/// the `depth` of a scene result rests on it.
pub const ISP_DEPTH_STORE: Status = Status::Fitted("E465");
/// The integer depth formats' value rules: round(z * 0xffffff) and its >> 8 for the 16-bit
/// format, fitted on the dumps of the run (E466 states the 16-bit one is in-sample; floor(z *
/// 2^24) clamped is a fourth candidate no dump separates from the 24-bit one, E663), answered
/// only over the ramp's 0.25 to 0.4166 and 1.0, and the 16-bit layout derived at G = 33 only
/// (12.4; E466, E490)
pub const ZLS_INT_FORMATS: Status = Status::Fitted("E466");
/// The 1/w the TA stores: kept above the minimum, the clamp value otherwise (E197, [infer])
pub const MTE_RHW: Status = Status::Fitted("E197");

impl Status {
    /// The model outcome of a computation made with this rule.
    pub fn outcome(self) -> crate::Outcome {
        match self {
            Status::Measured => crate::Outcome::Ok,
            Status::Fitted(r) => crate::Outcome::Fitted { record: r.to_string() },
        }
    }
}
