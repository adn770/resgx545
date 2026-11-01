// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The job loader and sequencer: a scene's memory into the device address space, its register
//! writes through the register file, then the units in the order of the data dependencies
//! (plan 3.2). A transfer runs through `xfer` (12.1); a render is refused, naming the open
//! questions of the units it would go through, until 12.2 and 12.3 build them.

use crate::scene::{Kind, Scene, SceneResult};
use crate::{bif, dpm, isp, iter, mte, pbe, ta, vdm, vtx, zls};

/// The questions that block each unit a scene of this kind goes through, in order.
pub fn blockers(kind: Kind) -> Vec<&'static str> {
    let mut ids: Vec<&'static str> = vec![];
    let units: &[&[&str]] = match kind {
        // a transfer: the background object, the pixel side, the emit (12.1)
        Kind::Transfer => &[bif::OPEN, isp::OPEN, iter::OPEN, pbe::OPEN],
        Kind::Render => &[
            bif::OPEN,
            vdm::OPEN,
            vtx::OPEN,
            mte::OPEN,
            ta::OPEN,
            dpm::OPEN,
            isp::OPEN,
            zls::OPEN,
            iter::OPEN,
            pbe::OPEN,
        ],
    };
    for u in units {
        for id in *u {
            if !ids.contains(id) {
                ids.push(id);
            }
        }
    }
    ids
}

/// Run a scene: a transfer through the model of 12.1 (`xfer`); a render through the vertex side and
/// the TA (12.2: the parameter buffer and TA data) and the pixel side (12.3: the ISP, the pixel
/// programs, the PBE: an image). A pixel side that refuses leaves the buffers and says why in
/// `pixel_refusal`; a scene that expects an image is then a refusal, never a silent pass.
pub fn run(scene: &Scene) -> SceneResult {
    match scene.kind {
        Kind::Transfer => crate::xfer::run(scene),
        Kind::Render => match crate::render::run(scene) {
            Ok(r) => r,
            Err(o) => SceneResult::refusing(o),
        },
    }
}

/// Replay the scenes of one scene-vector file (`Scene::load_file`): each is run by the `Edm` and
/// compared with its `expect`. A scene that does not load is a skip with its reason.
pub fn replay_file(
    file: &sgx_sim::json::Json,
    unit: &str,
) -> Vec<Result<crate::unitvec::Replayed, (String, String)>> {
    use crate::edm::{Edm, ModelledEdm};
    let ids: Vec<String> =
        file.get("scenes").arr().iter().map(|s| s.get("id").str().unwrap_or("?").to_string()).collect();
    let mut edm = ModelledEdm;
    Scene::load_file(file)
        .into_iter()
        .zip(file.get("scenes").arr())
        .zip(ids)
        .map(|((sc, j), id)| match sc {
            Err(e) => Err((id, e)),
            Ok(sc) => {
                let r = edm.run(&sc);
                Ok(crate::unitvec::Replayed {
                    id: sc.id.clone(),
                    unit: unit.to_string(),
                    task: "scene".to_string(),
                    verdict: crate::scene::compare(j.get("expect"), &r),
                    seen: Default::default(),
                })
            }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Outcome;
    use sgx_sim::json::parse;

    fn scene(kind: &str) -> Scene {
        Scene::parse(&parse(&format!(r#"{{"id": "j", "kind": "{kind}", "target": {{"w": 64, "h": 32}}}}"#)))
            .unwrap()
    }

    #[test]
    fn a_transfer_is_refused_naming_its_units_questions_and_a_render_names_more() {
        let t = blockers(Kind::Transfer);
        let r = blockers(Kind::Render);
        assert!(t.contains(&"Q012") && t.contains(&"Q066") && !t.contains(&"Q047"));
        assert!(r.contains(&"Q047") && r.contains(&"Q045") && r.contains(&"Q107") && r.len() > t.len());
        assert!(!r.is_empty() && r.iter().all(|i| i.starts_with('Q')));
        let mut sorted = r.clone();
        sorted.sort();
        sorted.dedup();
        assert_eq!(sorted.len(), r.len(), "each question once");
    }

    /// The questions a refusal names exist: one file `questions/<unit>/Q###-*.md` each. A question
    /// of a draft that has not landed is listed in PENDING and must still be absent from the tree
    /// when listed (so the entry is removed once it lands).
    const PENDING: &[&str] = &[];

    #[test]
    fn every_question_a_stub_names_exists_in_the_tree_or_is_pending_in_the_draft() {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../questions");
        let have = |id: &str| {
            std::fs::read_dir(&root).unwrap().flatten().any(|d| {
                std::fs::read_dir(d.path())
                    .into_iter()
                    .flatten()
                    .flatten()
                    .any(|f| f.file_name().to_string_lossy().starts_with(&format!("{id}-")))
            })
        };
        let all: Vec<&str> = [
            bif::OPEN,
            dpm::OPEN,
            isp::OPEN,
            iter::OPEN,
            mte::OPEN,
            pbe::OPEN,
            ta::OPEN,
            vdm::OPEN,
            vtx::OPEN,
            zls::OPEN,
            crate::xfer::OPEN,
        ]
        .concat();
        assert!(all.len() > 40);
        for id in all {
            if PENDING.contains(&id) {
                assert!(!have(id), "{id} landed: drop it from PENDING");
            } else {
                assert!(have(id), "{id} is named by a stub but no question file has it");
            }
        }
    }

    #[test]
    fn running_a_render_scene_without_command_words_refuses_and_says_which_scene() {
        match run(&scene("render")).outcome {
            Outcome::Unsupported { why, ids } => {
                assert!(why.starts_with("j:"));
                assert_eq!(ids, ["Q206"]);
            }
            o => panic!("{o:?}"),
        }
    }
}
