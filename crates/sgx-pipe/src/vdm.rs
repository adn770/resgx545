// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! VDM: the stream parser and vertex task forming (12.2).

use crate::Outcome;
use crate::mem::Mem;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q047", "Q042", "Q112", "Q163", "Q231"];

/// A state block of the stream: the PDS program that fetches the MTE state, and whether it is the
/// stream's last (the end of scene).
#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub pds: u32,
    pub data_dwords: u32,
    pub last: bool,
    /// VDM_STATE1 bits 11:9 and 12 say the TA writes no object (E185, E191)
    pub no_object: bool,
}

/// The vertex task of an index list: the PDS program run for each vertex, and the vertices a task
/// holds at most (VDM_TASK0 bits 31:28 + 1).
#[derive(Debug, Clone, PartialEq)]
pub struct Task {
    pub pds: u32,
    pub data_dwords: u32,
    pub per_task: u32,
    /// The rows of four dwords each vertex writes (task word 1 bits 31:24): 1 in the library's
    /// stream, (7 + N) / 4 for the N outputs the tool's `--vtx-coords` declares (2 to 4).
    pub rows: u32,
}

#[derive(Debug, Clone, PartialEq)]
pub struct IndexList {
    pub indices: Vec<u16>,
    pub task: Task,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Block {
    State(State),
    Index(IndexList),
    Terminate,
}

/// The unit as a whole, for a vector kind the replay has no inputs for (`vdm-stream`).
pub fn refuse() -> Outcome {
    Outcome::unsupported("the VDM stream is only parsed for the library's block shapes", OPEN)
}

fn refuse_ids(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

/// VDM_STATE1 of the library's blocks: data rows in 31:26, bits 25, 17 and 13 set, the attribute
/// rows in 7:0, and the fields the records flipped in 12:9 (bit 12 and the field 11:9).
const STATE1_FIXED: u32 = 1 << 25 | 1 << 17 | 1 << 13;
const STATE1_FREE: u32 = 0xfc00_0000 | 0x1e00 | 0xff;
/// VDM_INDEX2 values that left the TA's output byte for byte the same (E414, five copies).
const INDEX2_SAME: [u32; 5] = [0, 0x1000_0000, 0x7000_0000, 0x8000_0000, 0xf000_0000];
const INDEX3_LIBRARY: u32 = 0x003f_ffff;

fn read_state(w0: u32, w1: u32) -> Result<State, Outcome> {
    if w0 >> 28 & 1 != 0 {
        return Err(refuse_ids(
            format!("state block word 0 {w0:#010x}: bit 28 is not the library's"),
            &["Q047"],
        ));
    }
    // the attribute rows (7:0) are read by nothing: the library writes 5 for a draw, 1 for the end of scene
    let rows = if w0 >> 29 & 1 != 0 { 1 } else { 5 };
    if w1 & 0xff != rows || w1 & !STATE1_FREE != STATE1_FIXED {
        return Err(refuse_ids(
            format!("VDM_STATE1 {w1:#010x} has bits set or clear that no record flipped (E185, E191, E545)"),
            &["Q047"],
        ));
    }
    let (field, bit12) = (w1 >> 9 & 7, w1 >> 12 & 1 != 0);
    // 2 is the library's value: the object is written. 0 and bit 12 remove it (E185, E191). 1 and
    // 3 to 7 leave the output the same but complete or hang by history (E413, E545): a counter c,
    // 0 after a hang's reset, a job adding v - 2 a block and hanging iff c + add > 8 (E700, 52 of
    // 52 predicted before the run; E1021, round 12 offline: 54 of 54 held-out jobs of E545's sweeps
    // with v 3 to 7). Below 2 the counter's clauses are fitted only (E701's M3, post hoc; E1021: its
    // block-2 v = 1 clause and the v = 0 reset fail on E545's sweeps; E1035: block-2 v = 1 hung at c = 0,
    // 2 and 5, and time, a fill or the health between jobs leave c; E1076: the step and the
    // threshold held on 24 and 48 vertices, one and two objects, 64 x 64 and 128 x 64, block 1
    // at v = 6 hanging the third job, 4 of 4 held out; E1113: a block-2 v = 1 job completes iff
    // the job right before it completed with a block at v 1 or 6, 3 of 3 held out). The model keeps no job
    // history, so it gives one answer only where the word alone decides
    let no_object = match field {
        _ if bit12 => true,
        0 => true,
        2 => false,
        f => {
            let why = format!(
                "VDM_STATE1 bits 11:9 = {f}: whether the job completes is a function of the word and a \
                 job-history counter (E700, E1021; {}), and the model keeps no history",
                match f {
                    0 | 1 => "below 2 fitted only, E701",
                    7 => "a series of 7s alternates, E413",
                    _ => "held out for 3 to 7",
                }
            );
            return Err(refuse_ids(why, &["Q163"]));
        }
    };
    Ok(State {
        pds: (w0 & 0x0fff_ffff) << 4,
        data_dwords: (w1 >> 26) * 4,
        last: w0 >> 29 & 1 != 0,
        no_object,
    })
}

/// An index list block. A header other than the library's refuses: bit 24 hangs the job, bit 25
/// faults it (E737) and is not a 32-bit index width (E756), lines and points are open (E543, E544).
fn read_index(mem: &Mem, w: &[u32; 6]) -> Result<IndexList, Outcome> {
    // bits 27:26 of the header are the topology: 1 lines (E543), 2 points (E544); the TA's rules for
    // their regions are Q159 (one line or several) and Q161
    if w[0] >> 22 == 0x213 || w[0] >> 22 == 0x223 {
        let (kind, ids): (_, &[&str]) =
            if w[0] >> 26 & 3 == 1 { ("lines", &["Q159"]) } else { ("points", &["Q161"]) };
        return Err(refuse_ids(
            format!(
                "index list header {:#010x}: {kind}: the regions of their objects are open (E543, E544)",
                w[0]
            ),
            ids,
        ));
    }
    // bits 25:24 among them: bit 25 faults 0xd0008 over 16- and 32-bit lists (E737, E756), bit 24
    // alone hangs over both (E737; E1075 over the 32-bit list, held out), a hang the model refuses
    if w[0] >> 22 != 0x203 {
        return Err(refuse_ids(
            format!(
                "index list header {:#010x}: only 'triangles, two trailing words and a task' was seen (E346)",
                w[0]
            ),
            &["Q112"],
        ));
    }
    let count = w[0] & 0x3f_ffff;
    if !INDEX2_SAME.contains(&w[2]) {
        return Err(refuse_ids(
            format!("VDM_INDEX2 {:#010x}: its low bits are an offset in indices (E414)", w[2]),
            &["Q042"],
        ));
    }
    if w[3] != INDEX3_LIBRARY {
        return Err(refuse_ids(
            format!("VDM_INDEX3 {:#010x}: other values wrap, remove or hang (E188)", w[3]),
            &["Q042"],
        ));
    }
    // task word 1: output rows (31:24), vertex size 4 (23:22 = 3), bit 7, the data rows. The rows
    // are the natural ones, 1 (the library's) or the 2 to 4 the tool writes for N = 1 to 11
    // outputs; any other value is a forced row (E703), which breaks the job (Q094, by decision).
    // The rows are the vertex's output stride: set to the natural value they leave the render
    // intact, one above it at R * V = 6 they break it (E933); the parser does not know N, so a
    // row in 1 to 4 that is not the vertex's own is not caught here. The attribute rows (bits 14:7)
    // are the library's 1 only: at R * V = 33 and 32 other values changed the render or lost a
    // vertex by no function of the words (E702; E738 repeated two events 3 of 3 and changed a
    // third; E755: a = 8 gave three images in three runs, state carry not ruled out)
    let rows = w[5] >> 24;
    if w[5] & 0x00ff_ff80 != 0x00c0_0080 || !(1..=4).contains(&rows) {
        return Err(refuse_ids(
            format!(
                "vertex task word 1 {:#010x}: the output rows are 1 to 4 and the vertex size the library's only (E189, E346, E546, E703)",
                w[5]
            ),
            &["Q094"],
        ));
    }
    let mut indices = Vec::with_capacity(count as usize);
    for i in 0..count {
        let word = mem.read32(w[1] + (i / 2) * 4)?;
        indices.push((word >> (16 * (i % 2))) as u16);
    }
    Ok(IndexList {
        indices,
        task: Task {
            pds: (w[4] & 0x0fff_ffff) << 4,
            data_dwords: (w[5] & 0x7f) * 4,
            per_task: (w[4] >> 28) + 1,
            rows,
        },
    })
}

/// Parse the stream at `base`: state blocks, index lists and the terminate, in order. A block type
/// or a word with no record refuses (the library's shapes only: E346, E349). The whole stream is
/// walked before a refusal is returned: the words that block it and, when the blocks are not state,
/// index list, state, terminate (a stream of two objects), the shape (Q112) are all named, so a
/// refusal does not hide the question that blocks the stream whatever its words are.
pub fn parse(mem: &Mem, base: u32) -> Result<Vec<Block>, Outcome> {
    fn keep(r: Result<Block, Outcome>, out: &mut Vec<Block>, errs: &mut Vec<Outcome>) {
        match r {
            Ok(b) => out.push(b),
            Err(e) => errs.push(e),
        }
    }
    let (mut at, mut out, mut errs) = (base, vec![], vec![]);
    // the kinds of block in order: 1 state, 2 index list, 3 terminate, 0 a type nobody saw
    let mut shape = vec![];
    while shape.len() < 64 {
        let w0 = mem.read32(at)?;
        match w0 >> 30 {
            1 => {
                shape.push(1);
                keep(read_state(w0, mem.read32(at + 4)?).map(Block::State), &mut out, &mut errs);
                at += 8;
            }
            2 => {
                // the header, the index base, VDM_INDEX2, VDM_INDEX3, then the task's two words
                let mut w = [w0; 6];
                for (i, v) in w.iter_mut().enumerate().skip(1) {
                    *v = mem.read32(at + 4 * i as u32)?;
                }
                shape.push(2);
                keep(read_index(mem, &w).map(Block::Index), &mut out, &mut errs);
                at += 24;
            }
            3 if w0 & 0x3fff_ffff == 0 => {
                shape.push(3);
                out.push(Block::Terminate);
                break;
            }
            t => {
                shape.push(0);
                errs.push(refuse_ids(
                    format!("VDM block type {t} (word {w0:#010x}) was not seen (E349)"),
                    &["Q112"],
                ));
                break;
            }
        }
    }
    if shape != [1, 2, 1, 3] && (!errs.is_empty() || shape.last() != Some(&3)) {
        errs.push(refuse_ids(
            format!(
                "a stream of {} blocks, not state, index list, end of scene, terminate: one object only",
                shape.len()
            ),
            &["Q112"],
        ));
    }
    if errs.is_empty() { Ok(out) } else { Err(merge(errs)) }
}

/// One refusal naming every reason and every question of the refusals given (each question once,
/// in order of first appearance).
fn merge(errs: Vec<Outcome>) -> Outcome {
    let (mut why, mut ids): (Vec<String>, Vec<String>) = (vec![], vec![]);
    for e in errs {
        if let Outcome::Unsupported { why: w, ids: i } = e {
            why.push(w);
            for q in i {
                if !ids.contains(&q) {
                    ids.push(q);
                }
            }
        }
    }
    Outcome::Unsupported { why: why.join("; "), ids }
}

/// The vertex numbers of each vertex task of an index list, each vertex writing `l.task.rows` rows
/// of four dwords (E546: R * V <= 32 keeps every vertex in the TA's objects; the model refuses
/// from 33, where some are lost or repeated by a rule no record states, and a limit between 33
/// and 36 no natural job can place: Q094 is closed by that decision).
pub fn tasks(l: &IndexList) -> Result<Vec<Vec<u32>>, Outcome> {
    let (per, rows) = (l.task.per_task, l.task.rows);
    if rows * per > 32 {
        return Err(refuse_ids(
            format!(
                "a vertex task of {per} vertices of {rows} output rows: more than 32 words of rows; this is the decided rule (Q094 decision on E546's measurements), not a measurement of what the hardware does from 33 up"
            ),
            &["Q094"],
        ));
    }
    if l.indices.iter().enumerate().any(|(i, &v)| v as usize != i) {
        return Err(refuse_ids(
            "an index list that is not 0, 1, 2, ...: shared vertices were not measured",
            &["Q112"],
        ));
    }
    Ok(l.indices.chunks(per as usize).map(|c| c.iter().map(|&v| v as u32).collect()).collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::scene::Scene;

    const FIXTURE: &str = include_str!("../tests/fixtures/tri-baselines.scene.json");

    fn stream(id: &str) -> (Scene, Mem, u32) {
        let sc = Scene::from_fixture(FIXTURE, id);
        let mem = sc.load_mem().unwrap();
        let base = sc.cmd[0];
        (sc, mem, base)
    }

    fn refused(r: Result<Vec<Block>, Outcome>, id: &str) {
        match r {
            Err(Outcome::Unsupported { ids, .. }) => {
                assert!(ids.iter().any(|i| i == id), "{ids:?} lacks {id}")
            }
            r => panic!("not refused under {id}: {r:?}"),
        }
    }

    /// The fixture's stream with the word `k` of it set to `v`, parsed.
    fn poked(k: u32, v: u32) -> Result<Vec<Block>, Outcome> {
        let (_, mut mem, base) = stream("tb-w128-k0-16-16");
        mem.write32(base + 4 * k, v).unwrap();
        parse(&mem, base)
    }

    #[test]
    fn the_librarys_stream_is_a_state_an_index_list_the_end_of_scene_and_a_terminate() {
        let (_, mem, base) = stream("tb-w128-k0-16-16");
        let b = parse(&mem, base).unwrap();
        assert_eq!(b.len(), 4, "{b:?}");
        let Block::State(s0) = &b[0] else { panic!("{b:?}") };
        assert_eq!((s0.pds, s0.data_dwords, s0.last, s0.no_object), (0x3040_0000 + 0x40, 8, false, false));
        let Block::Index(l) = &b[1] else { panic!("{b:?}") };
        assert_eq!(l.indices, (0..15).collect::<Vec<u16>>());
        assert_eq!((l.task.pds, l.task.data_dwords, l.task.per_task), (0x3040_0000, 8, 16));
        let Block::State(s1) = &b[2] else { panic!("{b:?}") };
        assert!(s1.last && s1.pds == 0x3040_0080);
        assert_eq!(b[3], Block::Terminate);
    }

    fn list(n: u16, per_task: u32, rows: u32) -> IndexList {
        IndexList { indices: (0..n).collect(), task: Task { pds: 0, data_dwords: 8, per_task, rows } }
    }

    #[test]
    fn a_task_holds_at_most_the_fields_vertices_and_the_tasks_follow_the_index_list() {
        assert_eq!(tasks(&list(15, 16, 1)).unwrap(), vec![(0..15).collect::<Vec<u32>>()]);
        let t = tasks(&list(40, 16, 1)).unwrap();
        assert_eq!(t.iter().map(Vec::len).collect::<Vec<_>>(), [16, 16, 8]);
        assert_eq!(t[2][0], 32);
    }

    #[test]
    fn a_task_of_too_many_output_words_is_refused_not_split_the_way_the_hardware_does() {
        // Q094, closed by decision on E546's measurements: with R output rows and V vertices a
        // task is accepted when R * V <= 32 and refused from 33 up (33 depends on the program,
        // 36 and more break the job)
        for (rows, per_task) in [(1, 16), (2, 16), (3, 10), (4, 8), (3, 1)] {
            assert!(tasks(&list(40, per_task, rows)).is_ok(), "R {rows} V {per_task}");
        }
        for (rows, per_task) in [(3, 11), (2, 17), (3, 12), (4, 9), (4, 11), (3, 16)] {
            match tasks(&list(40, per_task, rows)) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q094"], "R {rows} V {per_task}: {why}");
                    // the refusal states a decided rule, not a measurement
                    assert!(why.contains("decided rule") && why.contains("not a measurement"), "{why}");
                }
                r => panic!("R {rows} V {per_task}: {r:?}"),
            }
        }
    }

    #[test]
    fn the_output_rows_of_the_task_word_are_the_natural_ones_and_other_values_are_forced_rows() {
        // task word 1 of the library is 0x01c00082 (1 row, vertex size 4, 2 data rows); the tool
        // writes (7 + N) / 4 rows for N outputs, 2 to 4 for the N of --vtx-coords 1 to 11
        let Block::Index(l) = &poked(7, 0x01c0_0082).unwrap()[1] else { panic!() };
        assert_eq!((l.task.rows, l.task.data_dwords, l.task.per_task), (1, 8, 16));
        for rows in 2..=4u32 {
            let Block::Index(l) = &poked(7, rows << 24 | 0x00c0_0082).unwrap()[1] else { panic!() };
            assert_eq!(l.task.rows, rows);
        }
        // no row, or more than the tool writes for any N (forced rows, E703): refused under Q094
        for rows in [0u32, 5, 8, 0x20, 0xff] {
            refused(poked(7, rows << 24 | 0x00c0_0082), "Q094");
        }
        // the vertex size field and the other bits of the word are still the library's
        for w in [0x02c0_0182, 0x0240_0082, 0x0280_0082, 0x02c0_0002] {
            refused(poked(7, w), "Q094");
        }
    }

    #[test]
    fn the_state_words_bits_11_to_9_and_12_say_no_object_and_other_values_are_refused() {
        // word 1 of the first state block: 0x0a022405; bit 12 set, or bits 11:9 = 0: no object (E185, E191)
        for w in [0x0a02_3405, 0x0a02_2005] {
            let Block::State(s) = &poked(1, w).unwrap()[0] else { panic!() };
            assert!(s.no_object, "{w:#x}");
        }
        let Block::State(s) = &poked(1, 0x0a02_2405).unwrap()[0] else { panic!() };
        assert!(!s.no_object);
        // 1 and 3 to 7 leave the output the same but complete or hang by the word and a job-history
        // counter (E545, E413; E700, held out again for 3 to 7 by E1021; below 2 fitted, E701):
        // the model keeps no history, so it refuses under Q163 and says why
        for (w, v) in [
            (0x0a02_2205, 1),
            (0x0a02_2605, 3),
            (0x0a02_2805, 4),
            (0x0a02_2a05, 5),
            (0x0a02_2c05, 6),
            (0x0a02_2e05, 7),
        ] {
            match poked(1, w) {
                Err(Outcome::Unsupported { ids, why }) => {
                    assert_eq!(ids, ["Q163"], "{w:#x}: {why}");
                    assert!(why.contains(&format!("= {v}")) && why.contains("counter"), "{why}");
                    assert!(why.contains("E700") && why.contains("E1021"), "{why}");
                }
                r => panic!("{w:#x}: {r:?}"),
            }
        }
        match poked(1, 0x0a02_2205) {
            Err(Outcome::Unsupported { why, .. }) => assert!(why.contains("E701"), "{why}"),
            r => panic!("{r:?}"),
        }
        // a bit nobody flipped (bit 20) is not the library's word
        refused(poked(1, 0x0a12_2405), "Q047");
    }

    #[test]
    fn the_attribute_rows_of_a_state_block_are_the_librarys_5_for_the_draw_and_1_for_the_end_of_scene() {
        // bits 7:0 are read by nothing in the model: a changed value refuses (Q047)
        for w in [0x0a02_2404, 0x0a02_2406, 0x0a02_2401, 0x0a02_2485] {
            refused(poked(1, w), "Q047");
        }
        let (_, mem, base) = stream("tb-w128-k0-16-16");
        let eos = mem.read32(base + 4 * 9).unwrap();
        assert_eq!(eos & 0xff, 1, "{eos:#x}");
        assert!(poked(9, eos).is_ok());
        for v in [0, 2, 5] {
            refused(poked(9, eos & !0xff | v), "Q047");
        }
        // a draw's rows on the end of scene block, and the reverse, are not the library's either
        refused(poked(1, 0x0a02_2401), "Q047");
    }

    /// The fixture's stream with a second draw (a state block, an index list) written before the end
    /// of scene: two objects, six blocks. The words of the second draw are `state1`.
    fn two_objects(state1: u32) -> Result<Vec<Block>, Outcome> {
        let (_, mut mem, base) = stream("tb-w128-k0-16-16");
        let w: Vec<u32> = (0..11).map(|k| mem.read32(base + 4 * k).unwrap()).collect();
        let mut out = w[..8].to_vec(); // the draw and the index list
        out.extend([w[0], state1]);
        out.extend(&w[2..8]);
        out.extend(&w[8..]); // the end of scene and the terminate
        for (k, v) in out.iter().enumerate() {
            mem.write32(base + 4 * k as u32, *v).unwrap();
        }
        parse(&mem, base)
    }

    #[test]
    fn a_stream_of_two_objects_is_refused_by_its_shape_and_by_each_word_that_also_blocks_it() {
        let (_, mem, base) = stream("tb-w128-k0-16-16");
        let lib = mem.read32(base + 4).unwrap();
        // a clean second draw: only the stream's shape blocks it (the render checks the shape)
        let b = two_objects(lib).unwrap();
        assert_eq!(b.len(), 6, "{b:?}");
        // a state word of the second draw nobody flipped: both questions are named
        match two_objects(lib | 1 << 20) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q047", "Q112"], "{why}");
                assert!(why.contains("VDM_STATE1") && why.contains("6 blocks"), "{why}");
            }
            r => panic!("{r:?}"),
        }
        // the one-object stream keeps its single question
        match poked(1, 0x0a12_2405) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q047"]),
            r => panic!("{r:?}"),
        }
    }

    #[test]
    fn index_list_words_no_record_explains_are_refused_by_question() {
        refused(poked(2, 0x8040_000f), "Q112"); // the header: a trailing-word bit missing
        refused(poked(0, 0x0), "Q112"); // a block type nobody saw
        refused(poked(4, 0xf000_0003), "Q042"); // VDM_INDEX2 low bits: an offset in indices (E414)
        refused(poked(5, 0x1), "Q042"); // VDM_INDEX3 other than 0x003fffff
        // under the trailing words' question alone (bits 31:28 of the first folded into Q042)
        match poked(5, 0x1) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q042"]),
            r => panic!("{r:?}"),
        }
        refused(poked(7, 0x01c0_0100 | 2), "Q094"); // the vertex task's output size and data
        // VDM_INDEX2 values that left the TA's output byte for byte the same (E414) are accepted
        for w in [0, 0x1000_0000, 0x7000_0000, 0x8000_0000, 0xf000_0000] {
            assert!(poked(4, w).is_ok(), "{w:#x}");
        }
    }

    #[test]
    fn a_lines_or_points_header_is_refused_under_the_questions_of_their_regions() {
        // E543: topology 1 runs lines; E544: points
        for (hdr, ids) in [(0x84c0_0002u32, vec!["Q159"]), (0x88c0_0003, vec!["Q161"])] {
            match poked(2, hdr) {
                Err(Outcome::Unsupported { ids: got, .. }) => assert_eq!(got, ids, "{hdr:#x}"),
                r => panic!("{r:?}"),
            }
        }
    }

    #[test]
    fn a_repeated_or_reordered_index_is_refused_the_model_knows_identity_lists_only() {
        let (_, mut mem, base) = stream("tb-w128-k0-16-16");
        let idx = mem.read32(base + 12).unwrap(); // index base
        mem.write32(idx, 0x0000_0000).unwrap(); // indices 0, 0
        let Block::Index(l) = &parse(&mem, base).unwrap()[1] else { panic!() };
        match tasks(l) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q112"]),
            r => panic!("{r:?}"),
        }
    }
}
