// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! A render job's vertex side and the TA (12.2): the VDM stream is parsed, its state blocks and
//! vertex tasks run on `sgx-sim` (`vtx`), the MTE puts the vertices in the window (`mte`) and the
//! TA writes the parameter buffer and TA data (`ta`); the pixel side (`pixel`, 12.3) goes on from
//! them to an image. Every word of the command that the vertex side or the TA reads is checked
//! against the library's value and refused by question when it differs.

use crate::Outcome;
use crate::scene::{Scene, SceneResult};
use crate::{mte, rules, ta, vdm, vtx};

fn refuse(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

/// The render command's words the vertex side and the TA read (`drm_sgxfive_render_cmd` order).
const CMD_VDM: usize = 0;
const CMD_TE_AA: usize = 1;
const CMD_MTILE1: usize = 2;
const CMD_MTILE2: usize = 3;
const CMD_SCREEN: usize = 4;
const CMD_STRIDE: usize = 5;
const CMD_MTE_CTRL: usize = 6;
const CMD_RHW_MIN: usize = 7;
const CMD_RHW_CLAMP: usize = 8;
const CMD_MTE_SCREEN: usize = 9;
/// What the library writes where no record explains another value.
const TE_AA: u32 = 0x2000_0000;
const MTE_CTRL: u32 = 0xa2;
/// The command words 10 to 25 (what follows CR_MTE_SCREEN: multisample, pixel back end, the ISP and
/// 3D words): no stage of the vertex side or the TA reads them, and all 355 dumped scenes carry the
/// same value in each, so the model refuses any other (Q231) rather than ignore a changed word.
/// The words the pixel side reads (`pixel::READS`, 12.3) are left to it: it recognises what it
/// models (the gate bits of CR_ISP_CTL, the background depth, the event program's place) and
/// refuses the rest by its own question, so a refusal here would hide the words it reads.
const CMD_UNREAD: [u32; 16] = [
    0x88,
    0x80,
    0xf0100,
    0x8000_0000,
    0x3f80_0000,
    0x300,
    0x88,
    0x30,
    0x2e00_0080,
    0x5,
    0x1,
    0x1,
    0x100,
    0x0400_0004,
    0x3_0000,
    0x0400_0002,
];
/// The words of a version 1 command (`struct drm_sgxfive_render_cmd` is 0x68 bytes).
const CMD_WORDS: usize = 26;

fn layout(sc: &Scene, k: &str) -> Result<u32, Outcome> {
    sc.layout
        .iter()
        .find(|(n, _)| n == k)
        .map(|p| p.1)
        .ok_or_else(|| refuse(format!("{}: the scene's layout has no `{k}`", sc.id), &["Q206"]))
}

fn check_cmd(sc: &Scene) -> Result<(), Outcome> {
    let (w, h) = (sc.target.w, sc.target.h);
    let c = &sc.cmd;
    if c.len() < CMD_WORDS {
        return Err(refuse(
            format!(
                "{}: a render scene needs its {CMD_WORDS} command words (a rebuilt scene has them)",
                sc.id
            ),
            &["Q206"],
        ));
    }
    let t = ta::tiling(w, h);
    if [c[CMD_MTILE1], c[CMD_MTILE2], c[CMD_SCREEN], c[CMD_STRIDE]]
        != [t.mtile1, t.mtile2, t.te_screen, t.stride]
    {
        return Err(refuse(
            format!(
                "{w} x {h}: the TE words {:#x} {:#x} {:#x} {:#x} are not the library's rule (E407, E505, E506: other words draw or fault by fields no record settles)",
                c[CMD_MTILE1], c[CMD_MTILE2], c[CMD_SCREEN], c[CMD_STRIDE]
            ),
            &["Q100", "Q139", "Q086"],
        ));
    }
    if c[CMD_TE_AA] != TE_AA {
        return Err(refuse(
            format!(
                "CR_TE_AA {:#x}: the dwords that change with its bits 30 and 31 are not modelled",
                c[CMD_TE_AA]
            ),
            &["Q142"],
        ));
    }
    if c[CMD_MTE_CTRL] != MTE_CTRL || c[CMD_MTE_SCREEN] != (w - 1) | (h - 1) << 16 {
        return Err(refuse(
            format!(
                "MTE control {:#x} / screen {:#x}: not the library's words, no record reads them",
                c[CMD_MTE_CTRL], c[CMD_MTE_SCREEN]
            ),
            &["Q231"],
        ));
    }
    let unread = |k: usize| !crate::pixel::READS.contains(&(10 + k));
    if let Some(k) = (0..CMD_UNREAD.len()).find(|&k| unread(k) && c[10 + k] != CMD_UNREAD[k]) {
        return Err(refuse(
            format!(
                "command word {} is {:#x}, the library's is {:#x}: no stage of the vertex side or the TA reads it and no record says a change leaves the object alone",
                10 + k,
                c[10 + k],
                CMD_UNREAD[k]
            ),
            &["Q231"],
        ));
    }
    Ok(())
}

pub fn run(sc: &Scene) -> Result<SceneResult, Outcome> {
    check_cmd(sc)?;
    let mem = sc.load_mem()?;
    let usev = layout(sc, "usev_base")?;
    let blocks = vdm::parse(&mem, sc.cmd[CMD_VDM])?;
    let [vdm::Block::State(draw), vdm::Block::Index(list), vdm::Block::State(eos), vdm::Block::Terminate] =
        &blocks[..]
    else {
        return Err(refuse(
            format!(
                "{}: a stream other than state, index list, end of scene, terminate ({} blocks)",
                sc.id,
                blocks.len()
            ),
            &["Q112"],
        ));
    };
    if draw.last || !eos.last {
        return Err(refuse("the state blocks are not (draw, end of scene) in that order", &["Q112"]));
    }
    // the draw's state block and the end of scene's, through their PDS programs and USSE tasks
    let st = mte::state(&vtx::state_outputs(&mem, draw.pds, draw.data_dwords, usev)?)?;
    let term = mte::term(&vtx::state_outputs(&mem, eos.pds, eos.data_dwords, usev)?)?;
    let (w, h) = (sc.target.w, sc.target.h);
    if term != (((w - 1) / 32) << 16) | ((h - 1) / 32) {
        return Err(refuse(
            format!(
                "the end-of-scene term word {term:#x} is not the target's last 32 x 32 block (E059): its effect is not modelled"
            ),
            &["Q231"],
        ));
    }
    if list.indices.len() % 3 != 0 {
        return Err(refuse(format!("{} indices: triangles of three only", list.indices.len()), &["Q112"]));
    }
    // the output rows the vertex task declares are natural when they hold the state's vertex size
    // (the tool writes (7 + N) / 4 for N outputs): the library's OUTSEL, the only one the state
    // accepts above, is one row, so another R is a forced row (E703, Q094)
    if list.task.rows != 1 {
        return Err(refuse(
            format!(
                "a vertex task of {} output rows with the library's OUTSEL of one: a forced row breaks the job (E703)",
                list.task.rows
            ),
            &["Q094"],
        ));
    }
    let total = list.indices.len() as u32;
    let mut clip = vec![];
    for task in vdm::tasks(list)? {
        let v = vtx::vertex_outputs(
            &mem,
            list.task.pds,
            list.task.data_dwords,
            usev,
            &task,
            list.task.per_task,
            total,
        )?;
        clip.extend(v);
    }
    let mut r = SceneResult::refusing(Outcome::Ok);
    let mut visible = vec![];
    for t in clip.chunks(3) {
        let (tri, used) = mte::triangle(&st, [t[0], t[1], t[2]], sc.cmd[CMD_RHW_MIN], sc.cmd[CMD_RHW_CLAMP])?;
        if used {
            r.use_rule(rules::MTE_RHW);
        }
        visible.push(tri);
    }
    let out = ta::write(&ta::Job { w, h, tris: &visible, state: &st, no_object: draw.no_object })?;
    for rec in &out.rules {
        r.use_rule(match *rec {
            "E541" => rules::TA_OBJECT_FORMAT,
            "E542" => rules::TA_REGION_TEST,
            "E651" => rules::TA_PACKED_VERTICES,
            _ => rules::TA_STREAMS,
        });
    }
    match crate::pixel::image(sc, &out) {
        Ok(img) => {
            r.image = Some(img.pixels);
            r.outside = Some(img.outside);
            r.depth = img.depth;
            r.use_rule(rules::ISP_COVERAGE);
            r.use_rule(rules::ISP_VERTEX_GRID);
            if r.depth.is_some() {
                r.use_rule(rules::ISP_DEPTH_STORE);
            }
        }
        Err(o) => r.pixel_refusal = Some(o),
    }
    r.buffers.insert("param".into(), out.param);
    r.buffers.insert("tadata".into(), out.tadata);
    Ok(r)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Verdict;
    use crate::scene::compare;

    const FIXTURE: &str = include_str!("../tests/fixtures/tri-baselines.scene.json");
    const IDS: [&str; 3] = ["tb-w128-k0-16-16", "tb-w64-k0-16-16", "tc-16-16"];

    fn expect_of(id: &str) -> sgx_sim::json::Json {
        let j = sgx_sim::json::parse(FIXTURE);
        j.get("scenes")
            .arr()
            .iter()
            .find(|s| s.get("id").str().unwrap().ends_with(id))
            .unwrap()
            .get("expect")
            .clone()
    }

    #[test]
    fn the_dumped_triangle_jobs_reproduce_byte_for_byte_and_are_reported_fitted() {
        for id in IDS {
            let sc = Scene::from_fixture(FIXTURE, id);
            let r = run(&sc).unwrap_or_else(|o| panic!("{id}: {o:?}"));
            assert!(!r.fitted.is_empty(), "{id}: the TA's rules are fitted: never matched");
            assert_eq!(compare(&expect_of(id), &r), Verdict::Fitted, "{id}");
        }
    }

    #[test]
    fn a_scene_poked_to_a_different_viewport_changes_the_object_and_no_longer_equals_the_dump() {
        let mut sc = Scene::from_fixture(FIXTURE, "tb-w128-k0-16-16");
        // viewport x offset 63.875 -> 63.75: the packed vertices move, the regions may too
        let blk = sc.layout.iter().find(|(n, _)| n == "pdsv").unwrap().1 + 0x100 + 4 * 6;
        let seg = sc.memory.iter_mut().find(|s| s.role == "pdsv").unwrap();
        let (i, _) = (((blk - seg.base) / 4) as usize, ());
        seg.dwords.as_mut().unwrap()[i] = 0x427f_0000;
        let r = run(&sc).unwrap();
        assert!(matches!(compare(&expect_of("tb-w128-k0-16-16"), &r), Verdict::Mismatch(_)));
    }

    #[test]
    fn output_rows_that_do_not_match_the_librarys_vertex_size_are_refused_as_forced_rows_under_q094() {
        // task word 1 is word 7 of the stream; 2 rows is a natural value for the tool's vertex
        // programs with outputs, but the library's OUTSEL (4 dwords) declares 1: a forced row
        let id = "tb-w128-k0-16-16";
        let mut sc = Scene::from_fixture(FIXTURE, id);
        let at = sc.cmd[CMD_VDM] + 4 * 7;
        let seg = sc
            .memory
            .iter_mut()
            .find(|s| s.base <= at && at < s.base + 4 * s.dwords.as_ref().unwrap().len() as u32);
        let seg = seg.unwrap();
        let k = ((at - seg.base) / 4) as usize;
        assert_eq!(seg.dwords.as_ref().unwrap()[k] >> 24, 1);
        seg.dwords.as_mut().unwrap()[k] = 0x02c0_0082;
        match run(&sc) {
            Err(Outcome::Unsupported { ids, why }) => assert_eq!(ids, ["Q094"], "{why}"),
            r => panic!("{r:?}"),
        }
    }

    #[test]
    fn command_words_no_record_reads_are_refused_by_question() {
        let id = "tb-w128-k0-16-16";
        let cases = [
            (CMD_MTILE1, 0x0100_4005u32, "Q100"),
            (CMD_TE_AA, 0x6000_0000, "Q142"),
            (CMD_MTE_CTRL, 0xa3, "Q231"),
        ];
        for (k, v, q) in cases {
            let mut sc = Scene::from_fixture(FIXTURE, id);
            sc.cmd[k] = v;
            match run(&sc) {
                Err(Outcome::Unsupported { ids, .. }) => assert!(ids.iter().any(|i| i == q), "{k}: {ids:?}"),
                r => panic!("{k}: {r:?}"),
            }
        }
        // no command words: refused naming the scene
        let mut sc = Scene::from_fixture(FIXTURE, id);
        sc.cmd.clear();
        assert!(matches!(run(&sc), Err(Outcome::Unsupported { why, .. }) if why.contains(id)));
    }

    #[test]
    fn the_command_words_of_a_target_that_is_not_square_are_the_librarys_with_the_width_in_the_low_half() {
        // render.c: mte_screen = (w - 1) | (h - 1) << 16 (the squares could not tell the halves apart)
        let t = ta::tiling(64, 32);
        let mut w = vec![0, TE_AA, t.mtile1, t.mtile2, t.te_screen, t.stride, MTE_CTRL, 0, 0, 63 | 31 << 16];
        w.extend(CMD_UNREAD);
        let words: Vec<String> = w.iter().map(|x| format!("\"{x:#x}\"")).collect();
        let j = sgx_sim::json::parse(&format!(
            r#"{{"id": "n", "kind": "render", "target": {{"w": 64, "h": 32}}, "cmd": [{}]}}"#,
            words.join(",")
        ));
        let mut sc = Scene::parse(&j).unwrap();
        assert!(check_cmd(&sc).is_ok());
        sc.cmd[CMD_MTE_SCREEN] = 31 | 63 << 16;
        assert!(matches!(check_cmd(&sc), Err(Outcome::Unsupported { ids, .. }) if ids == ["Q231"]));
    }

    #[test]
    fn every_command_word_from_10_to_25_is_the_librarys_or_refused_under_q231() {
        let id = "tb-w128-k0-16-16";
        let sc = Scene::from_fixture(FIXTURE, id);
        assert_eq!(&sc.cmd[10..26], &CMD_UNREAD, "the table is the fixture's words");
        assert!(check_cmd(&sc).is_ok());
        for k in 10..26 {
            for v in [sc.cmd[k] ^ 1, sc.cmd[k] ^ 0x8000_0000, 0] {
                let mut sc = Scene::from_fixture(FIXTURE, id);
                sc.cmd[k] = v;
                if crate::pixel::READS.contains(&k) {
                    // the pixel side reads the word (12.3): a recognised or a refused value is its
                    // verdict, in `pixel_refusal`, and the vertex side's job still runs
                    assert!(check_cmd(&sc).is_ok(), "word {k} = {v:#x}");
                    let r = run(&sc).unwrap_or_else(|e| panic!("word {k} = {v:#x}: {e:?}"));
                    assert!(r.pixel_refusal.is_some() && r.image.is_none(), "word {k} = {v:#x}");
                    continue;
                }
                match run(&sc) {
                    Err(Outcome::Unsupported { ids, why }) => {
                        assert_eq!(ids, ["Q231"], "word {k} = {v:#x}");
                        assert!(why.contains(&format!("command word {k} ")), "{why}");
                    }
                    r => panic!("word {k} = {v:#x}: {r:?}"),
                }
            }
        }
        // a command shorter than a version 1 command is refused naming the scene
        let mut sc = Scene::from_fixture(FIXTURE, id);
        sc.cmd.truncate(25);
        assert!(matches!(run(&sc), Err(Outcome::Unsupported { ids, .. }) if ids == ["Q206"]));
    }

    #[test]
    fn an_end_of_scene_term_word_that_is_not_the_targets_last_block_is_refused() {
        // the 128 x 128 job re-targeted to 96 x 128 with the library's words for it: the term word
        // the stream carries (3, 3) is no longer the last 32 x 32 block (2, 3)
        let mut sc = Scene::from_fixture(FIXTURE, "tb-w128-k0-16-16");
        let t = ta::tiling(96, 128);
        sc.target.w = 96;
        sc.cmd[CMD_MTILE1..=CMD_STRIDE].copy_from_slice(&[t.mtile1, t.mtile2, t.te_screen, t.stride]);
        sc.cmd[CMD_MTE_SCREEN] = 95 | 127 << 16;
        match run(&sc) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q231"]);
                assert!(why.contains("term word"), "{why}");
            }
            r => panic!("{:?}", r.map(|_| ())),
        }
    }

    #[test]
    fn a_stream_of_two_objects_is_refused_naming_its_shape_and_not_only_its_state_words() {
        // one more object written into the stream before the end of scene, its state word a value
        // nobody flipped: the stream's shape is named with the word
        let mut sc = Scene::from_fixture(FIXTURE, "tb-w128-k0-16-16");
        let base = sc.cmd[0];
        let seg = sc.memory.iter_mut().find(|s| s.role == "gen").unwrap();
        let at = ((base - seg.base) / 4) as usize;
        let d = seg.dwords.as_mut().unwrap();
        let w: Vec<u32> = d[at..at + 11].to_vec();
        let mut out = w[..8].to_vec();
        out.extend([w[0], w[1] | 1 << 20]);
        out.extend(&w[2..8]);
        out.extend(&w[8..]);
        d[at..at + out.len()].copy_from_slice(&out);
        match run(&sc) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q047", "Q112"]),
            r => panic!("{:?}", r.map(|_| ())),
        }
    }

    #[test]
    fn a_state_word_that_removes_the_object_writes_empty_headers_and_no_stream() {
        let mut sc = Scene::from_fixture(FIXTURE, "tb-w64-k0-16-16");
        let at = sc.cmd[0] + 4; // VDM_STATE1 of the first block, bit 12: no object (E185)
        let seg = sc.memory.iter_mut().find(|s| s.role == "gen").unwrap();
        seg.dwords.as_mut().unwrap()[((at - seg.base) / 4) as usize] |= 1 << 12;
        let r = run(&sc).unwrap();
        assert!(r.buffers["param"].is_empty());
        // 8 target regions: every header empty; macrotile 0's first and last still flagged
        let flags: Vec<u32> = r.buffers["tadata"].values().map(|w| w >> 24).collect();
        assert!(
            flags
                .iter()
                .all(|f| matches!(f, 0x02 | 0x04 | 0x08 | 0x0c | 0x98 | 0x90 | 0x18 | 0x10 | 0x88 | 0x80)),
            "{flags:x?}"
        );
    }

    /// Toggle bit 42 (.twopart) of the first instruction of the vertex program whose text starts
    /// with `prefix`.
    fn toggle_twopart(sc: &mut Scene, prefix: &str) {
        let seg = sc.memory.iter_mut().find(|s| s.role == "usev").unwrap();
        let d = seg.dwords.as_mut().unwrap();
        let at = (0..d.len() / 2)
            .find(|&i| {
                let w = d[2 * i] as u64 | (d[2 * i + 1] as u64) << 32;
                usse_isa::decode(w, usse_isa::Core::Sgx545).text.starts_with(prefix)
            })
            .unwrap_or_else(|| panic!("no {prefix}"));
        d[2 * at + 1] ^= 1 << 10;
    }

    #[test]
    fn e102_the_vertex_emits_without_twopart_hang_or_draw_nothing_as_recorded() {
        let id = "tb-w64-k0-16-16";
        // emitvcbvtx without .twopart, emitmtevtx with: the job hangs (a predicted hang, no refusal)
        let mut sc = Scene::from_fixture(FIXTURE, id);
        toggle_twopart(&mut sc, "emitvcbvtx");
        assert!(matches!(run(&sc), Err(Outcome::Hang { record }) if record == "E102"));
        // neither with: the job completes with no triangle, what the TA writes then was not dumped
        toggle_twopart(&mut sc, "emitmtevtx");
        match run(&sc) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q230"]);
                assert!(why.contains("E102"), "{why}");
            }
            r => panic!("{r:?}"),
        }
        // emitmtevtx alone without it: the triangle is exact
        let mut sc = Scene::from_fixture(FIXTURE, id);
        toggle_twopart(&mut sc, "emitmtevtx");
        assert!(run(&sc).is_ok());
    }
}
