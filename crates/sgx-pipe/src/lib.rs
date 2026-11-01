// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! SGX545 pipeline simulator, phase 12: the fixed-function units over `sgx-sim`.
//!
//! One module per hardware unit, each a refusing stub until its sub-phase lands
//! (every refusal names the open question that blocks it), plus the machinery that
//! holds a model to the hardware: outcomes and verdicts ([`outcome`]), unit vectors
//! ([`unitvec`]), scene vectors ([`scene`]), the coverage report ([`report`]). The firm
//! rule of the phase: a model covers only what a record states, every model is checked
//! against hardware vectors, and a result that depends on a fitted rule is never reported
//! "matched" ([`outcome::Verdict::combine`]). Not cycle accurate. See doc/specs/vectors.md
//! sections 5 and 6.

pub mod bif;
pub mod data;
pub mod dpm;
pub mod edm;
pub mod events;
pub mod gz;
pub mod isp;
pub mod iter;
pub mod job;
pub mod mem;
pub mod mte;
pub mod outcome;
pub mod pbe;
pub mod regs;
pub mod render;
pub mod report;
pub mod rules;
pub mod scene;
pub mod sha256;
pub mod ta;
pub mod unitvec;
pub mod vdm;
pub mod vtx;
pub mod xfer;
pub mod zls;

pub use outcome::{Outcome, Verdict};
