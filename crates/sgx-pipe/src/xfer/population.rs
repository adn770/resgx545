// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! What a match of the transfer replay shows (review r121 item 2): of the scenes the model
//! matches, which are the unpoked baselines, which poke only words the model never reads
//! (model-inert: the matched image is the baseline's whatever the value, so the match says the
//! hardware ignored the word for the values tried, and is a regression statement), and which poke
//! at least one word the model reads (model-live: the result moves or the model refuses for some
//! value). The classification looks at the model alone, never at the recorded result.
//!
//! A poked word is probed on the unpoked base: 0, 0xffffffff and the word with each of its 32
//! bits flipped; it is model-inert when every probe gives the base's result (an `Ok` outcome,
//! the same image and the same count of dwords outside the target), and model-live otherwise, a
//! refusal counting as live (the model looked at the word). A scene is model-inert when each of
//! its poked words is, tried one at a time.

use crate::Outcome;
use crate::job;
use crate::scene::{Scene, SceneResult};
use sgx_sim::json::Json;
use std::collections::HashMap;

/// A word of a scene a poke can move: a command word or a dword of a memory segment.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Word {
    Xfer(usize),
    Memory(usize, usize),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Population {
    Unpoked,
    ModelInert,
    ModelLive,
}

fn get(sc: &Scene, w: Word) -> u32 {
    match w {
        Word::Xfer(i) => sc.xfer.get(i).copied().unwrap_or(0),
        Word::Memory(s, i) => sc.memory[s].dwords.as_ref().and_then(|d| d.get(i).copied()).unwrap_or(0),
    }
}

fn set(sc: &mut Scene, w: Word, v: u32) {
    match w {
        Word::Xfer(i) => sc.xfer[i] = v,
        Word::Memory(s, i) => {
            let d = sc.memory[s].dwords.as_mut().expect("a memory segment held inline");
            if i >= d.len() {
                d.resize(i + 1, 0);
            }
            d[i] = v;
        }
    }
}

/// The words in which `sc` differs from its unpoked `base`.
pub fn poked(base: &Scene, sc: &Scene) -> Vec<Word> {
    let mut out = vec![];
    for i in 0..sc.xfer.len() {
        if get(base, Word::Xfer(i)) != get(sc, Word::Xfer(i)) {
            out.push(Word::Xfer(i));
        }
    }
    for (s, seg) in sc.memory.iter().enumerate() {
        let n =
            seg.dwords.as_ref().map_or(0, Vec::len).max(base.memory[s].dwords.as_ref().map_or(0, Vec::len));
        for i in 0..n {
            if get(base, Word::Memory(s, i)) != get(sc, Word::Memory(s, i)) {
                out.push(Word::Memory(s, i));
            }
        }
    }
    out
}

/// The values a poked word is tried with.
pub fn probes(v: u32) -> Vec<u32> {
    let mut p = vec![0, u32::MAX];
    p.extend((0..32).map(|k| v ^ (1 << k)));
    p
}

fn same(a: &SceneResult, b: &SceneResult) -> bool {
    a.outcome == Outcome::Ok && b.outcome == Outcome::Ok && a.image == b.image && a.outside == b.outside
}

/// Whether no probe value of the word `w` moves the model's result off the base's.
pub fn word_is_inert(base: &Scene, base_result: &SceneResult, w: Word) -> bool {
    probes(get(base, w)).into_iter().all(|v| {
        let mut sc = base.clone();
        set(&mut sc, w, v);
        same(&job::run(&sc), base_result)
    })
}

/// The population of `sc`, a scene of the unpoked `base` (whose result is `base_result`); `cache`
/// holds the words already probed on this base.
pub fn classify(
    base: &Scene,
    base_result: &SceneResult,
    sc: &Scene,
    cache: &mut HashMap<Word, bool>,
) -> Population {
    let words = poked(base, sc);
    if words.is_empty() {
        return Population::Unpoked;
    }
    let inert =
        words.into_iter().all(|w| *cache.entry(w).or_insert_with(|| word_is_inert(base, base_result, w)));
    if inert { Population::ModelInert } else { Population::ModelLive }
}

/// The unpoked base scene of scene `s` of the compact scene-vector file `file`.
pub fn base_of(file: &Json, s: &Json) -> Option<Scene> {
    let base = s.get("base").num()?;
    let one = Json::Obj(vec![
        ("id".into(), Json::Str("base".into())),
        ("base".into(), Json::Num(base)),
        ("delta".into(), Json::Obj(vec![])),
        ("expect".into(), Json::Obj(vec![])),
    ]);
    let f =
        Json::Obj(vec![("bases".into(), file.get("bases").clone()), ("scenes".into(), Json::Arr(vec![one]))]);
    Scene::load_file(&f).into_iter().next()?.ok()
}

#[cfg(test)]
mod tests {
    use super::*;
    use sgx_sim::json::parse;

    fn fixture_base(kind: usize) -> Scene {
        let f = parse(include_str!("../../tests/fixtures/transfer-baselines.scene.json"));
        let s = parse(&format!(r#"{{"base": {kind}}}"#));
        base_of(&f, &s).unwrap()
    }

    fn population(base: &Scene, w: Word, v: u32) -> Population {
        let r = job::run(base);
        assert_eq!(r.outcome, Outcome::Ok);
        let mut sc = base.clone();
        set(&mut sc, w, v);
        classify(base, &r, &sc, &mut HashMap::new())
    }

    #[test]
    fn a_word_the_model_reads_is_live_and_one_it_never_reads_is_inert() {
        let fill = fixture_base(0);
        // the box's last tile (word 13): the image changes; a fill's background word 5 changes
        // nothing in the model (E069: a fill's words 3 to 16)
        assert_eq!(population(&fill, Word::Xfer(13), 0x0), Population::ModelLive);
        assert_eq!(population(&fill, Word::Memory(2, 5), 0x1234), Population::ModelInert);
        // the pixel-event program's data dword 9 (the tile mask) is read: a refusal is live
        assert_eq!(population(&fill, Word::Memory(0, 16 + 9), 0xfe8), Population::ModelLive);
    }

    #[test]
    fn an_unpoked_scene_is_its_own_population_and_a_poke_back_to_the_base_value_is_too() {
        let fill = fixture_base(0);
        let r = job::run(&fill);
        assert_eq!(classify(&fill, &r, &fill, &mut HashMap::new()), Population::Unpoked);
        assert_eq!(population(&fill, Word::Xfer(13), fill.xfer[13]), Population::Unpoked);
        assert_eq!(poked(&fill, &fill), vec![]);
    }

    #[test]
    fn the_probes_are_zero_all_ones_and_each_bit_flipped() {
        let p = probes(0x10);
        assert_eq!(p.len(), 34);
        assert!(p.contains(&0) && p.contains(&u32::MAX) && p.contains(&0x11) && p.contains(&0x8000_0010));
    }
}
