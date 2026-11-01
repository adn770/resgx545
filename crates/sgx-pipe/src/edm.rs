// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The line between the firmware and the hardware (plan 3.2). The units are reached only through
//! registers and memory, as the firmware does, so one set of unit models serves both
//! implementations: `ModelledEdm` (decision D1: the host-visible job level, first) and, in 12.9,
//! a `FirmwareEdm` that runs an EDM image on the simulated USSE and PDS through `sgx-sim`.

use crate::job;
use crate::scene::{Scene, SceneResult};

pub trait Edm {
    /// Run one job (pick, kick, finish) and return what the host would read.
    fn run(&mut self, scene: &Scene) -> SceneResult;
}

/// What 3d.md sections 3 to 6 say the firmware does, as Rust code starting the units.
#[derive(Debug, Default)]
pub struct ModelledEdm;

impl Edm for ModelledEdm {
    fn run(&mut self, scene: &Scene) -> SceneResult {
        job::run(scene)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Outcome;
    use sgx_sim::json::parse;

    #[test]
    fn the_modelled_edm_refuses_every_job_until_a_unit_exists() {
        let s =
            Scene::parse(&parse(r#"{"id": "x", "kind": "transfer", "target": {"w": 1, "h": 1}}"#)).unwrap();
        let mut e: Box<dyn Edm> = Box::new(ModelledEdm);
        assert!(matches!(e.run(&s).outcome, Outcome::Unsupported { .. }));
    }
}
