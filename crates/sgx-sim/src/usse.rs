// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The USSE interpreter.

use crate::func::{self, Bound};
use crate::tex;
use std::cell::Cell;
use std::collections::BTreeMap;
use std::fmt;
use usse_isa::{Core, Ctx, Form, decode_fields};

/// Memory and the SGX registers, as the program sees them.
pub trait Bus {
    fn load32(&mut self, addr: u32) -> Result<u32, Error>;
    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error>;

    /// ldr: read SGX register `index` (dword index; its MMIO offset is index * 4).
    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        Err(why(format!("ldr #{index}: no SGX registers on this bus")))
    }

    /// str: write SGX register `index`.
    fn reg_write(&mut self, index: u32, _v: u32) -> Result<(), Error> {
        Err(why(format!("str #{index}: no SGX registers on this bus")))
    }

    /// Whether `ldr` and `str` may take their index from a register (`ldr rD, rI`, `str rI, rS`)
    /// and not only as the 14-bit immediate. A bus that models only what ran says no.
    fn register_index_forms(&self) -> bool {
        true
    }

    /// emitpds and its kin: the instruction and its three source values.
    fn emit(&mut self, text: &str, _srcs: [u32; 3]) -> Result<(), Error> {
        Err(why(format!("{text}: no task emission on this bus")))
    }

    /// smp: the registers a texture sample writes (see tex).
    fn sample(&mut self, _s: &tex::Sample) -> Result<Vec<u32>, Error> {
        Err(why("no texture unit on this bus"))
    }

    /// A PDS movs/movsa: the four words to a port (crate::pds).
    fn port(&mut self, port: crate::pds::Port, _words: [u32; 4]) -> Result<(), Error> {
        Err(why(format!("movs to {port:?}: no such port on this bus")))
    }
}

/// A flat memory window: `bytes` at `base`, little endian. Anything else faults.
pub struct Memory {
    pub base: u32,
    pub words: Vec<u32>,
}

impl Bus for Memory {
    /// An unaligned load reads the four bytes at addr (hardware: a register
    /// offset of 1 byte returns the bytes across two dwords).
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        let mut v = 0;
        for k in (0..4).rev() {
            let a = addr.wrapping_add(k);
            v = v << 8 | (self.words[self.index(a & !3, addr)?] >> (8 * (a & 3)) & 0xff);
        }
        Ok(v)
    }

    /// An unaligned store is dropped (hardware: the buffer stays unchanged).
    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        let i = self.index(addr & !3, addr)?;
        if addr.is_multiple_of(4) {
            self.words[i] = v;
        }
        Ok(())
    }

    /// The texture unit's model over this memory.
    /// The two id registers our SGX545 reads back (usse-memory-mem-forms, E090); the others are
    /// state this bus does not have.
    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        match index {
            7 => Ok(0x0115_0000),
            8 => Ok(0x0001_000d),
            _ => Err(why(format!("ldr #{index}: no SGX registers on this bus"))),
        }
    }

    fn sample(&mut self, s: &tex::Sample) -> Result<Vec<u32>, Error> {
        tex::sample(s, &mut |a| self.load32(a)).map_err(|f| match f {
            tex::Fail::Open(w) => why(w),
            tex::Fail::Load(e) => e,
        })
    }
}

impl Memory {
    fn index(&self, aligned: u32, addr: u32) -> Result<usize, Error> {
        let off = aligned.wrapping_sub(self.base);
        if off as usize >= self.words.len() * 4 {
            return Err(Error::Fault(addr));
        }
        Ok(off as usize / 4)
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Error {
    /// What the simulator does not model (yet): the instruction and why.
    Unsupported { pc: usize, text: String, why: String },
    /// A memory access outside the bus's memory.
    Fault(u32),
    /// The program counter left the program.
    PcOutOfRange(usize),
    /// No `.end` within the step limit.
    StepLimit,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Error::Unsupported { pc, text, why } => write!(f, "{pc}: {text}: {why}"),
            Error::Fault(a) => write!(f, "fault at 0x{a:08X}"),
            Error::PcOutOfRange(pc) => write!(f, "pc {pc} out of range"),
            Error::StepLimit => write!(f, "step limit"),
        }
    }
}

/// A decoded instruction: its form and field values, and the text of the
/// fields read by name (flags, operation selectors).
#[derive(Clone)]
struct Insn {
    form: &'static Form,
    v: [u32; 10],
    /// The word, for the bits outside every field (READ_BITS).
    word: u64,
    text: String,
    /// A firh runs after this one with two or more instructions before it since this one or
    /// the firh before (or anywhere, in a program that branches): the firh latch this
    /// instruction reads may then hold its byte early.
    firh_later: bool,
}

impl Insn {
    fn get(&self, role: &str) -> Option<u32> {
        self.form.role(role).map(|i| self.v[i])
    }

    /// The text a field prints (an enumeration or flags).
    fn name(&self, role: &str, core: Core) -> Option<String> {
        let i = self.form.role(role)?;
        let mut s = String::new();
        self.form.f[i].k.print(self.v[i], &Ctx { core, resolve: None }, &mut s);
        Some(s)
    }
}

/// The word of a class 9 test whose test field enc[43:40] the table has no text for, with the
/// field that means the same. Hardware (E499, usse-rawcond, usse-rawcond2: 540 of 540 cases on
/// `and`, `or`, `xor` and `rol`, with the join `a` (enc[39]) and chan0, enc[50] clear; the join `o`: E529, 360 of 360;
/// E1062: `shl`, `shr`, `asr`, `iadd32`, `iaddu32` and `or`/`rol` with #7 under both joins, 1344 of 1344): the
/// field is two parts ANDed, a zero part (tanz if bit 41, else taz if bit 40) and a sign part (pat
/// if bit 43, else nat if bit 42), so that field 3 reads as 2, 7 as 6, 0xb as 0xa, 0xc as 8, 0xd
/// as 9 and 0xe and 0xf as 0xa. Any other word is returned as it is.
pub fn canonical_test_word(w: u64) -> u64 {
    let field = (w >> 40 & 0xf) as u32;
    // class 9, enc[50] clear, chan0, either join (E529: with the join `o` the parts are ORed and an
    // absent part is true, which the text forms' test_one gives for the canonical field)
    if w >> 59 != 9 || w >> 50 & 1 != 0 || w >> 36 & 7 != 0 {
        return w;
    }
    let zero = if field & 2 != 0 { 2 } else { field & 1 };
    let sign = if field & 8 != 0 { 2 } else { field >> 2 & 1 };
    let canon = (sign << 2 | zero) as u64;
    w & !(0xf << 40) | canon << 40
}

/// A program, decoded once.
pub struct Program {
    insns: Vec<Result<Insn, String>>,
}

impl Program {
    pub fn new(words: &[u64], core: Core) -> Program {
        let mut insns: Vec<Result<Insn, String>> = words
            .iter()
            .map(|&w| {
                let text = usse_isa::decode(w, core).text;
                match decode_fields(w, core) {
                    Some(f) => {
                        let form = video_form(&usse_isa::table().forms[f.form]);
                        Ok(Insn { form, v: f.v, word: w, text, firh_later: false })
                    }
                    // a test field the table has no text for (E499), read as the field that
                    // carries the same two parts
                    None => match decode_fields(canonical_test_word(w), core) {
                        Some(f) if canonical_test_word(w) != w => {
                            let form = video_form(&usse_isa::table().forms[f.form]);
                            let i =
                                Insn { form, v: f.v, word: canonical_test_word(w), text, firh_later: false };
                            match i.name("op", core).as_deref() {
                                // E1062: the shifts and the 32-bit sums as well (chan0)
                                Some(
                                    "and" | "or" | "xor" | "rol" | "shl" | "shr" | "asr" | "iadd32"
                                    | "iaddu32",
                                ) => Ok(i),
                                _ => Err(i.text),
                            }
                        }
                        _ => Err(text),
                    },
                }
            })
            .collect();
        // hardware (usse-video-filters-c11-latch-merge): a firh's destination, whose other bytes are the
        // latch's, caught the byte of a later firh where two to five instructions came
        // between firhs, never in runs of firhs one or no instruction apart (and once not
        // with eight between): the latch an instruction reads is known only while the
        // firhs after it keep that close
        let op = |i: &Result<Insn, String>| i.as_ref().map_or("", |i| i.form.op);
        let firh: Vec<bool> = insns.iter().map(|i| op(i) == "firh").collect();
        let branches = insns.iter().any(|i| matches!(op(i), "br" | "ba" | "lapc"));
        for (n, i) in insns.iter_mut().enumerate() {
            let Ok(i) = i else { continue };
            i.firh_later = if branches {
                firh.iter().enumerate().any(|(j, &f)| f && j != n)
            } else {
                let mut gap = 0;
                firh[n + 1..].iter().any(|&f| {
                    let far = f && gap >= 2;
                    gap = if f { 0 } else { gap + 1 };
                    far
                })
            };
        }
        Program { insns }
    }
}

/// Bits outside every field that the hardware was seen to read (usse_bits.py, the encoding-bit
/// probes), by mnemonic (read_bit): a word with one set stops the run, as their meaning is open,
/// whether or not the form has semantics.
const READ_BITS: &[(&str, u32, &str)] = &[
    // usse-encoding-bits-state (E296): the job hangs
    ("setfc", 51, "the job hangs, E296"),
    ("imo", 51, "the job hangs, E296"),
    ("depthf", 44, "the job hangs, E296"),
];

/// The bit of READ_BITS a word sets: the form's mnemonic, the bit and why.
fn read_bit(form: &Form, word: u64) -> Option<(&'static str, u32, &'static str)> {
    let name = mnemonic(form)?;
    READ_BITS.iter().find(|(o, b, _)| *o == name && word >> b & 1 != 0).map(|&(o, b, q)| (o, b, q))
}

/// A form's op, or where it has none (imo) the mnemonic its pattern starts with, after the
/// predicate's placeholder.
fn mnemonic(form: &Form) -> Option<&'static str> {
    if !form.op.is_empty() {
        return Some(form.op);
    }
    let pat = form.pat?;
    pat.strip_prefix("{0}").unwrap_or(pat).split('{').next().filter(|m| !m.is_empty())
}

/// The operations and field roles, by position, of the forms the ISA table leaves without
/// them: the video filters (isa/usse/forms/classes-22-and-23-adif-adifsum-bilin-firv-firh.toml),
/// the visibility tests (class-31-visibility-test.toml) and the MOE state and mask forms
/// (class-31-moe-group.toml, class-31-other-group.toml) whose effect in a fill is measured.
const VIDEO_ROLES: [(&str, &str, &[&str]); 9] = [
    (
        "{0}bilin{1}",
        "bilin",
        &["pred", "flags", "dst", "src0", "src1", "src2", "fmt", "layout", "sel", "rnd"],
    ),
    ("{0}firv{1}", "firv", &["pred", "flags", "write", "dst", "pair", "src2", "fmt", "firv"]),
    ("{0}firh{1}", "firh", &["pred", "flags", "dst", "pair", "src2", "fmt", "firh", "s", "k"]),
    (
        "{0}atst8{1}",
        "atst8",
        &["pred", "flags", "dst", "pwrite", "p", "src0", "src1", "src2", "twosided", "vismode"],
    ),
    ("{0}depthf{1}", "depthf", &["pred", "flags", "src0", "src1", "src2", "twosided", "vismode"]),
    ("pcoeff{0}{1}", "pcoeff", &["nosched", "end", "src0", "src1", "src2"]),
    ("setfc{0}", "setfc", &["nosched", "fc0", "fc1"]),
    ("moest{0}{1}", "moest", &["skipinv", "nosched", "dst", "sel"]),
    ("setm{0}", "setm", &["nosched", "samples"]),
];

/// What a form does to the simulator: its operation, "" if none.
pub fn sim_op(form: &'static Form) -> &'static str {
    video_form(form).op
}

/// The form, or for a video filter the table has no operation for, a copy with its
/// operation and field roles.
fn video_form(form: &'static Form) -> &'static Form {
    static NAMED: std::sync::OnceLock<Vec<(&'static str, &'static Form)>> = std::sync::OnceLock::new();
    if !form.op.is_empty() {
        return form;
    }
    let named = NAMED.get_or_init(|| {
        VIDEO_ROLES
            .iter()
            .filter_map(|&(pat, op, roles)| {
                let f = usse_isa::table()
                    .forms
                    .iter()
                    .find(|f| f.op.is_empty() && f.pat.is_some_and(|p| p.starts_with(pat)))?;
                if f.f.len() != roles.len() {
                    return None;
                }
                let fields: Vec<usse_isa::form::Field> =
                    f.f.iter().zip(roles).map(|(x, &r)| usse_isa::form::Field { r, ..*x }).collect();
                let named = Form { f: Box::leak(fields.into_boxed_slice()), op, ..*f };
                Some((f.pat.unwrap(), &*Box::leak(Box::new(named))))
            })
            .collect()
    });
    named.iter().find(|(p, _)| Some(*p) == form.pat).map_or(form, |&(_, f)| f)
}

/// The state of one instance.
#[derive(Clone)]
pub struct Machine {
    pub core: Core,
    /// The instance's pixel (x, y) in a fill, when the run knows it: the g bank's tile and
    /// quad registers depend on it (E086).
    pub pixel: Option<(u32, u32)>,
    /// The instance is a pixel of a triangle object in a render, not of a fill: the g bank was read
    /// there for g23, g24 and g25 only (E808), so every other global is refused.
    pub tri_pixel: bool,
    /// A vertex task's instance (11.33, q053-vtx): (the vertex's sequence number in the draw, the
    /// vertices a task holds, the vertices of the draw); the g bank's per-vertex registers depend on it.
    pub vertex: Option<(u32, u32, u32)>,
    pub r: [u32; 128],
    pub i: [u32; 4],
    pub o: [u32; 128],
    pub pa: [u32; 128],
    pub sa: [u32; 128],
    pub p: [bool; 4],
    /// The predicates the task has set (a bit each): p0-p3 are not reset between jobs, so one the
    /// task reads before it sets it holds what the job before left (E477, E484) and stops it.
    pub p_set: u8,
    pub pc: usize,
    pub link: u32,
    /// Whether the task has written pclink (a call, taken or not, or a move into it): it is not
    /// reset between jobs, so a read before that is the job before's value and stops (E475).
    pub link_set: bool,
    pub steps: usize,
    /// What the task has written, per bank (a bit per register): a read of
    /// anything else is the environment's (stale or set up by the job), not the
    /// ISA's, and stops the program.
    pub written: Written,
    /// Results of DRC operations (loads, idiv) not yet visible: (drc, temp or
    /// pa register, value). They land at a wdf on their DRC; reading such a
    /// register before is timing-dependent on the hardware (x-misc: a store
    /// right after idiv saw the old value), so it stops the program.
    pub pending: Vec<(u32, Reg, u32)>,
    /// Registers a DRC operation writes with a value not known (drc, register, why): at the wdf
    /// on their DRC they become `unknown` (an sRGB sample's second register, tex::unknown_after).
    pub pending_unknown: Vec<(u32, Reg, &'static str)>,
    /// The MOE increments smlsi set, in its operand order; None until a
    /// program sets them. Before that, repeats and fetches step every operand by
    /// one (hardware: repeat probes, usse-numbered-modifiers-family-repeat, usse-numbered-modifiers-family-fetch).
    pub moe_inc: Option<[i32; 4]>,
    /// The operands smlsi put in swizzle mode: iteration k's register offset is component
    /// k of the swizzle (E097), in smlsi's operand order.
    pub moe_swizzle: [Option<[i32; 4]>; 4],
    /// smbo's base offsets of the destination and sources 0-2 (E087), for the rest of the task.
    pub moe_base: [u32; 4],
    /// smoa's register offsets and address modes (0 none, 1 repeat, 2 clamp, 3 mirror) of
    /// the destination and sources 0-2 (E097, E105).
    pub moe_addr: ([i32; 4], [u32; 4]),
    /// smr's ranges, in the same operand order (E105).
    pub moe_range: [u32; 4],
    /// The index registers i.l and i.h.
    pub index: [u32; 2],
    /// Set while the machine runs as one instance of a 2x2 quad (run_quad):
    /// its position and the four instances' i0-i2 before the instruction.
    pub quad: Option<QuadView>,
    /// efo.gpiext's write of i1, which run_quad delivers to the top-right i0.
    pub quad_i1: Option<u32>,
    /// The temporaries allocated to the task: those past it are other
    /// instances' and stop the program.
    pub temps: usize,
    /// Whether the float functions the hardware gives only to a bound (see
    /// func) give their nearest value; without it they stop the program.
    pub near: bool,
    /// Whether every instance of the task runs as this one, from the same
    /// inputs (a probe fill whose readback is one o0): fdsx/fdsy then give
    /// a - b, and a sample without a LOD of its own sees zero derivatives.
    pub uniform: bool,
    /// The registers holding a near value (bank, number), with its bound:
    /// a move keeps it, anything else computed from one is Bound::Derived.
    pub bounds: BTreeMap<(&'static str, usize), Bound>,
    /// The addresses a near value was stored at.
    pub near_mem: BTreeMap<u32, Bound>,
    /// The current operation, for bounds.
    pub now: Now,
    /// The firh latch (probes/usse/video-filters.toml), a byte at a time: None where the
    /// task has not written it (it belongs to the instance slot and holds what the slot's
    /// last task left, garbage at power-up) or where it wrote a value the run cannot compute.
    pub firh_latch: [Option<u8>; 4],
    /// The latch bytes the task wrote (or a firh it skipped may have): only those not written
    /// are taken as any value; a written byte the run could not compute is not known.
    pub firh_written: [bool; 4],
    /// Set once a firh result comes from fixed bank 1 or 2, whose tap families are fitted to
    /// the vectors (FIXED_BANKS): a match is then Outcome::Fitted, not a hardware check.
    pub fitted: bool,
    /// The job's USE filter coefficients (E078), which firh reads; None where the run does
    /// not know them.
    pub coeffs: Option<FilterBlock>,
    /// The job's colour-space set is known not to be loaded (the vector's job pokes do not set
    /// the load flag, xfer:17 bit 0), so the YUV formats read opaque black (E037); where it is
    /// not known the YUV formats stop.
    pub csc_unloaded: bool,
    /// The registers holding a value the hardware may not have (bank, number), with why:
    /// reading one stops the program.
    pub unknown: BTreeMap<(&'static str, usize), &'static str>,
    /// The phase a `phas` with the wait `none` named: its first instruction and the temporaries
    /// it asks for. It starts where the phase that is running ends (E487, E519).
    pub phase: Option<(usize, usize)>,
    /// Whether the task is a vertex task (sgx-sim --task vertex): the wait `vcull` of its phas
    /// then names a phase that the MTE's cull decision starts, which is not modelled.
    pub vertex_task: bool,
    /// The instruction index of the program's first word inside its code base, for a program
    /// placed in the code heap: the code base is the placement rounded down to 0x80000 bytes, so
    /// this is (offset mod 0x80000) / 8 (E476, E492: 10 of 10 placements fit; [infer] as a rule).
    /// pclink and the absolute `ba` count from the code base, `br` from the instruction.
    pub code_index: u32,
    /// Whether the task is one of the firmware's EDM tasks (Sgx::run_task) and not a fill's: its
    /// pa0 to pa4 are sa64 to sa68 (E748), and a mov to pa2 to pa4 follows E820 (write_dst).
    pub edm_task: bool,
    /// Set while a `mov` writes its destination: E380 measured `mov` to pa1 to pa7 in a fill,
    /// and no other instruction (E496 did ima32 to pa0 only).
    pub mov_dest: bool,
    /// The mutexes this instance holds (bit n: `lock #n` taken and not released).
    pub locks: u8,
}

/// What the current operation read and writes, for Machine::bounds.
#[derive(Clone, Default)]
pub struct Now {
    /// The bound of what it read (Derived if two).
    read: Cell<Option<Bound>>,
    out: Out,
    /// Why what it writes is not known (Machine::unknown), if it is not.
    unknown: Option<&'static str>,
}

#[derive(Clone, Copy, Default)]
enum Out {
    #[default]
    /// A value computed from what it read.
    Reads,
    /// What it read, unchanged.
    Move,
    /// A float function's result, with its bound if near.
    Fn(Option<Bound>),
}

/// What an instance of a quad sees of the others (see Machine::quad).
#[derive(Clone, Debug, Default)]
pub struct QuadView {
    /// TL, TR, BL, BR = 0-3
    pub pos: usize,
    pub i: [[u32; 3]; 4],
    pub written: [u8; 4],
}

/// Run a 2x2 quad of instances (TL, TR, BL, BR) of one program in lockstep:
/// what i3, the bank-7 numbers past it and fdsx/fdsy read of the others.
/// Instances that would take different paths stop the quad.
pub fn run_quad(
    quad: &mut [Machine; 4],
    prog: &Program,
    bus: &mut dyn Bus,
    max_steps: usize,
) -> Result<(), Error> {
    loop {
        let pc = quad[0].pc;
        if quad.iter().any(|m| m.pc != pc) {
            return Err(unsupported(pc, "", "the quad's instances diverged"));
        }
        if quad[0].steps >= max_steps {
            return Err(Error::StepLimit);
        }
        let insn = match prog.insns.get(pc) {
            None => return Err(Error::PcOutOfRange(pc)),
            Some(Err(text)) => return Err(unsupported(pc, text, "undecoded")),
            Some(Ok(i)) => i,
        };
        let view = QuadView {
            pos: 0,
            i: [0, 1, 2, 3].map(|k| [quad[k].i[0], quad[k].i[1], quad[k].i[2]]),
            written: [0, 1, 2, 3].map(|k| quad[k].written.i & 7),
        };
        for (k, m) in quad.iter_mut().enumerate() {
            m.steps += 1;
            m.quad = Some(QuadView { pos: k, ..view.clone() });
        }
        let at = |e: Error| match e {
            Error::Unsupported { why, .. } => unsupported(pc, &insn.text, &why),
            e => e,
        };
        let mut nexts = Vec::with_capacity(4);
        if insn.form.op == "fds" {
            // hardware (usse-gradients-fds-quad): fdsx = a(TR) - b(TL), fdsy = a(BL) - b(TL),
            // the same for all four; a repeat's iterations one after another
            // (usse-gradients-fds-incs)
            if quad.iter().any(|m| m.moe_base != [0; 4] || m.moe_addr != ([0; 4], [0; 4])) {
                return Err(unsupported(pc, &insn.text, "fds after smbo or smoa"));
            }
            let its = quad[0].iterations(insn).map_err(at)?;
            for it in its.as_deref().unwrap_or(std::slice::from_ref(insn)) {
                let mut ab = Vec::with_capacity(4);
                for m in quad.iter_mut() {
                    m.now = Now::default();
                    ab.push(m.fds_sources(it).map_err(at)?);
                }
                let y = insn.name("op", quad[0].core).as_deref() == Some("fdsy");
                let v = flt::sub(ab[if y { 2 } else { 1 }].0, Ok(ab[0].1)).map_err(at)?;
                for m in quad.iter_mut() {
                    m.write(it, v).map_err(at)?;
                }
            }
            for m in quad.iter_mut() {
                nexts.push(if m.ends(insn) { Next::End } else { Next::Step });
            }
        } else {
            for m in quad.iter_mut() {
                nexts.push(m.exec(insn, bus).map_err(at)?);
            }
        }
        for m in quad.iter_mut() {
            m.quad = None;
        }
        // efo.gpiext's i1 writes: the top-right i0 holds the bottom-right's
        // (usse-internal-registers-efo-gpiext-quad; whether the others land first is not settled)
        let i1: Vec<Option<u32>> = quad.iter_mut().map(|m| m.quad_i1.take()).collect();
        if i1.iter().any(|w| w.is_some()) {
            let Some(v) = i1[3] else {
                return Err(unsupported(pc, &insn.text, "efo.gpiext i1 writes without the bottom-right's"));
            };
            quad[1].i[0] = v;
            quad[1].written.i |= 1;
        }
        let next = &nexts[0];
        // a predicated branch the instances disagree on: the whole quad goes where its top-left
        // instance goes (hardware: usse-branch-divergent, E089)
        let branch = matches!(insn.form.op, "br" | "ba");
        if nexts.iter().any(|n| n != next)
            && !(branch && nexts.iter().all(|n| matches!(n, Next::Step | Next::Jump(_))))
        {
            return Err(unsupported(pc, &insn.text, "the quad's instances diverged"));
        }
        match *next {
            Next::Step => quad.iter_mut().for_each(|m| m.pc += 1),
            Next::Jump(t) => quad.iter_mut().for_each(|m| m.pc = t),
            Next::End => return Ok(()),
        }
    }
}

/// The USE filter coefficients of a job (E078, transfer.md 3.2): CR_USE_COEFFS_MODE (only
/// bits 1:0 count) and the three loaded groups of three words (sets 0, 1 and 2), None where
/// the job loads none. A job that loads none runs with mode 0 and every group zero, as a
/// load-free job after a loading one shows (usse-filter-sets load0).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub struct FilterBlock {
    pub mode: u32,
    pub groups: Option<[u32; 9]>,
}

/// firh's fixed sets in banks 1 and 2 (CR_USE_COEFFS_MODE 1 and 2, E079, and bank 2's sets 2
/// and 3 on a lifted line, E293): (bank, set, first tap's position, shift, the tap vectors with
/// the bias range each allows). tools/usse-asm/firh_banks.py writes the table: every tap vector
/// within 5 per tap (in 128ths, [infer] choice) of E079's changes times 4 or E293's taps that
/// some bias fits on all of the set's cases in usse-filter-banks, usse-filter-control and
/// usse-filter-bank2. A result counts only where all agree, and as fitted (Machine::fitted), not
/// as a hardware check: the families come from the vectors they are compared with. Taps outside
/// the window are zero, as the impulse cases show no change there.
type Family = (u32, u32, i32, u32, &'static [(&'static [i64], i64, i64)]);
// firh_banks.py: begin
#[rustfmt::skip]
const FIXED_BANKS: &[Family] = &[
    // bank 1 set 2: 130 cases, 18 members
    (1, 2, -1, 7, &[
        (&[-10, 73, 72, -7], 64, 95),
        (&[-9, 72, 72, -7], 64, 95),
        (&[-9, 73, 71, -7], 64, 95),
        (&[-9, 73, 72, -8], 32, 95),
        (&[-9, 73, 73, -9], 32, 63),
        (&[-9, 74, 72, -9], 32, 63),
        (&[-8, 71, 72, -7], 64, 95),
        (&[-8, 72, 71, -7], 64, 95),
        (&[-8, 72, 72, -8], 0, 127),
        (&[-8, 72, 73, -9], 32, 63),
        (&[-8, 73, 72, -9], 32, 63),
        (&[-8, 73, 73, -9], -64, -33),
        (&[-7, 70, 72, -7], 64, 95),
        (&[-7, 71, 71, -7], 64, 95),
        (&[-7, 71, 72, -8], 32, 95),
        (&[-7, 71, 73, -9], 32, 63),
        (&[-7, 72, 72, -9], 32, 63),
        (&[-6, 71, 72, -9], 32, 63),
    ]),
    // bank 1 set 3: 130 cases, 18 members
    (1, 3, -1, 7, &[
        (&[-10, 73, 72, -7], 64, 95),
        (&[-9, 72, 72, -7], 64, 95),
        (&[-9, 73, 71, -7], 64, 95),
        (&[-9, 73, 72, -8], 32, 95),
        (&[-9, 73, 73, -9], 32, 63),
        (&[-9, 74, 72, -9], 32, 63),
        (&[-8, 71, 72, -7], 64, 95),
        (&[-8, 72, 71, -7], 64, 95),
        (&[-8, 72, 72, -8], 0, 127),
        (&[-8, 72, 73, -9], 32, 63),
        (&[-8, 73, 72, -9], 32, 63),
        (&[-8, 73, 73, -9], -64, -33),
        (&[-7, 70, 72, -7], 64, 95),
        (&[-7, 71, 71, -7], 64, 95),
        (&[-7, 71, 72, -8], 32, 95),
        (&[-7, 71, 73, -9], 32, 63),
        (&[-7, 72, 72, -9], 32, 63),
        (&[-6, 71, 72, -9], 32, 63),
    ]),
    // bank 1 set 4: 130 cases, 13 members
    (1, 4, -1, 7, &[
        (&[-11, 108, 36, -5], 96, 127),
        (&[-10, 107, 35, -4], 96, 127),
        (&[-10, 107, 36, -5], 96, 127),
        (&[-10, 108, 35, -5], 96, 127),
        (&[-10, 108, 36, -6], 64, 127),
        (&[-9, 106, 35, -4], 96, 127),
        (&[-9, 106, 36, -5], 96, 127),
        (&[-9, 107, 35, -5], 64, 127),
        (&[-9, 107, 36, -6], 64, 127),
        (&[-8, 105, 35, -4], 96, 127),
        (&[-8, 105, 36, -5], 96, 127),
        (&[-8, 106, 35, -5], 64, 127),
        (&[-8, 106, 36, -6], 64, 127),
    ]),
    // bank 1 set 5: 130 cases, 13 members
    (1, 5, -1, 7, &[
        (&[-8, 106, 36, -6], 0, 63),
        (&[-8, 106, 37, -7], 0, 63),
        (&[-8, 107, 36, -7], 0, 31),
        (&[-8, 107, 37, -8], 0, 31),
        (&[-7, 105, 36, -6], 0, 63),
        (&[-7, 105, 37, -7], 0, 63),
        (&[-7, 106, 36, -7], 0, 31),
        (&[-7, 106, 37, -8], 0, 31),
        (&[-6, 104, 36, -6], 0, 63),
        (&[-6, 104, 37, -7], 0, 31),
        (&[-6, 105, 36, -7], 0, 31),
        (&[-6, 105, 37, -8], 0, 31),
        (&[-5, 104, 36, -7], 0, 31),
    ]),
    // bank 2 set 2: 166 cases, 7 members
    (2, 2, -1, 7, &[
        (&[15, -64, 64, -15], 32, 95),
        (&[15, -63, 64, -16], 32, 95),
        (&[16, -65, 64, -15], 32, 95),
        (&[16, -64, 64, -16], 0, 127),
        (&[16, -63, 64, -17], 32, 95),
        (&[17, -65, 64, -16], 32, 95),
        (&[17, -64, 64, -17], 32, 95),
    ]),
    // bank 2 set 3: 166 cases, 7 members
    (2, 3, -2, 7, &[
        (&[128, -257, 64, 65], 32, 63),
        (&[128, -257, 65, 64], 32, 95),
        (&[128, -256, 63, 65], 32, 63),
        (&[128, -256, 64, 64], 0, 127),
        (&[128, -256, 65, 63], 64, 95),
        (&[128, -255, 63, 64], 32, 95),
        (&[128, -255, 64, 63], 64, 95),
    ]),
    // bank 2 set 4: 130 cases, 11 members
    (2, 4, -2, 7, &[
        (&[15, 31, 34, 32, 16], 32, 63),
        (&[15, 32, 33, 32, 16], 32, 95),
        (&[15, 33, 32, 32, 16], 32, 95),
        (&[15, 34, 31, 32, 16], 32, 63),
        (&[16, 31, 33, 32, 16], 32, 95),
        (&[16, 32, 32, 32, 16], 0, 127),
        (&[16, 33, 31, 32, 16], 32, 95),
        (&[17, 30, 33, 32, 16], 64, 95),
        (&[17, 31, 32, 32, 16], 32, 95),
        (&[17, 32, 31, 32, 16], 32, 95),
        (&[17, 33, 30, 32, 16], 64, 95),
    ]),
    // bank 2 set 5: 130 cases, 11 members
    (2, 5, -2, 7, &[
        (&[31, 31, 34, 32], 32, 63),
        (&[31, 32, 33, 32], 32, 95),
        (&[31, 33, 32, 32], 32, 95),
        (&[31, 34, 31, 32], 32, 63),
        (&[32, 31, 33, 32], 32, 95),
        (&[32, 32, 32, 32], 0, 127),
        (&[32, 33, 31, 32], 32, 95),
        (&[33, 30, 33, 32], 64, 95),
        (&[33, 31, 32, 32], 32, 95),
        (&[33, 32, 31, 32], 32, 95),
        (&[33, 33, 30, 32], 64, 95),
    ]),
];
// firh_banks.py: end

/// The constant bank, c0-c63 (source bank 5, numbers below 64), as the hardware
/// reads it (the constant-bank vectors, probe usse-constant-banks-cbank: the same through a store's and a
/// mov's source). Rogue's special constants in the same order up to c39: 0, 1.0,
/// powers of two up and down, e, 1/e, sqrt 2, 1/sqrt 2, pi multiples, 1/65536;
/// then SGX's own (series coefficients, f16 pairs of 1.0, 1.0 x4, ~0 x4, 0x7fff7fff x4).
pub const CONST_BANK: [u32; 64] = [
    0x00000000, 0x00000000, 0x00000000, 0x3f800000, // c0-c3
    0x40000000, 0x40800000, 0x41000000, 0x41800000, // c4-c7
    0x42000000, 0x42800000, 0x43000000, 0x43800000, // c8-c11
    0x44000000, 0x44800000, 0x3f000000, 0x3e800000, // c12-c15
    0x3e000000, 0x3d800000, 0x3d000000, 0x3c800000, // c16-c19
    0x3c000000, 0x3b800000, 0x3b000000, 0x3a800000, // c20-c23
    0x3a000000, 0x39800000, 0x39000000, 0x38800000, // c24-c27
    0x402df854, 0x3ebc5ab2, 0x3fb504f3, 0x3f3504f3, // c28-c31
    0x3f490fdb, 0x3fc90fdb, 0x40490fdb, 0x3ea2f983, // c32-c35
    0x3f22f983, 0x3fa2f983, 0x40c90fdb, 0x37800000, // c36-c39
    0x35d00d01, 0x37b60b61, 0x39888889, 0x3b2aaaab, // c40-c43
    0x3caaaaab, 0x3c003c00, 0x3c003c00, 0x3c003c00, // c44-c47
    0x00000000, 0x00000000, 0x00000000, 0x00000000, // c48-c51
    0x3f800000, 0x3f800000, 0x3f800000, 0x3f800000, // c52-c55
    0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, // c56-c59
    0x7fff7fff, 0x7fff7fff, 0x7fff7fff, 0x7fff7fff, // c60-c63
];

/// A register a pending result goes to.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reg {
    R(usize),
    Pa(usize),
}

/// A bit per register of each bank.
#[derive(Clone, Copy, Default)]
pub struct Written {
    pub r: u128,
    pub i: u8,
    pub index: u8,
    pub o: u128,
    pub pa: u128,
    pub sa: u128,
}

impl Default for Machine {
    fn default() -> Self {
        Machine {
            core: Core::Sgx545,
            pixel: None,
            tri_pixel: false,
            vertex: None,
            r: [0; 128],
            i: [0; 4],
            o: [0; 128],
            pa: [0; 128],
            sa: [0; 128],
            p: [false; 4],
            p_set: 0,
            pc: 0,
            link: 0,
            link_set: false,
            steps: 0,
            written: Written::default(),
            pending: Vec::new(),
            pending_unknown: Vec::new(),
            moe_inc: None,
            moe_swizzle: [None; 4],
            moe_base: [0; 4],
            moe_addr: ([0; 4], [0; 4]),
            moe_range: [0; 4],
            index: [0; 2],
            quad: None,
            quad_i1: None,
            temps: 124,
            near: false,
            uniform: false,
            bounds: BTreeMap::new(),
            near_mem: BTreeMap::new(),
            now: Now::default(),
            firh_latch: [None; 4],
            firh_written: [false; 4],
            fitted: false,
            coeffs: None,
            csc_unloaded: false,
            unknown: BTreeMap::new(),
            phase: None,
            vertex_task: false,
            code_index: 0,
            edm_task: false,
            mov_dest: false,
            locks: 0,
        }
    }
}

/// The bits pclink holds (E475): a move into it keeps bits 17:0.
const PCLINK_MASK: u32 = 0x3ffff;

/// What an instruction asks the loop to do next.
#[derive(PartialEq, Eq)]
enum Next {
    Step,
    Jump(usize),
    End,
}

impl Machine {
    /// A host preset of predicate `n` (0-3): the task has set it, as a test would.
    pub fn set_pred(&mut self, n: usize, v: bool) -> bool {
        let Some(p) = self.p.get_mut(n) else { return false };
        *p = v;
        self.p_set |= 1 << n;
        true
    }

    /// A host preset of pclink (18 bits): the task has written it.
    pub fn set_link(&mut self, v: u32) {
        self.link = v & PCLINK_MASK;
        self.link_set = true;
    }

    /// Run from `pc` until an instruction with `.end` retires.
    pub fn run(&mut self, prog: &Program, bus: &mut dyn Bus, max_steps: usize) -> Result<(), Error> {
        loop {
            if self.steps >= max_steps {
                return Err(Error::StepLimit);
            }
            if self.step(prog, bus)? {
                return Ok(());
            }
        }
    }

    /// Run the instruction at `pc`: true when it ends the program.
    pub fn step(&mut self, prog: &Program, bus: &mut dyn Bus) -> Result<bool, Error> {
        self.steps += 1;
        let pc = self.pc;
        let insn = match prog.insns.get(pc) {
            None => return Err(Error::PcOutOfRange(pc)),
            Some(Err(text)) => return Err(unsupported(pc, text, "undecoded")),
            Some(Ok(i)) => i,
        };
        match self.exec(insn, bus).map_err(|e| match e {
            Error::Unsupported { why, .. } => unsupported(pc, &insn.text, &why),
            e => e,
        })? {
            Next::Step => self.pc += 1,
            Next::Jump(t) => self.pc = t,
            Next::End => match self.phase.take() {
                None => return Ok(true),
                Some((next, request)) => {
                    // hardware (E487, E519): the next phase has the allocation its phas asked
                    // for, the request modulo 256; a request whose remainder is 0 or 196 to 252
                    // hung the job (27 of 27 run); the registers the first phase wrote are not
                    // the second's (E119: carried in most instances only)
                    // [infer] the allocation is the request modulo 256 (E519): no record states it,
                    // it is the rule that fits the runs of 4 to 192 and the hangs of 0 and 196 to 252
                    let alloc = request % 256;
                    if !(4..=192).contains(&alloc) {
                        return Err(unsupported(
                            pc,
                            &insn.text,
                            &format!("phas request {request} hangs the job (E519)"),
                        ));
                    }
                    self.temps = alloc;
                    self.written.r = 0;
                    self.pending.retain(|p| !matches!(p.1, Reg::R(_)));
                    self.pending_unknown.retain(|p| !matches!(p.1, Reg::R(_)));
                    self.pc = next;
                }
            },
        }
        Ok(false)
    }

    /// The text of the instruction at `pc` (for traces).
    pub fn text(prog: &Program, pc: usize) -> Option<&str> {
        prog.insns.get(pc).map(|i| match i {
            Ok(i) => i.text.as_str(),
            Err(t) => t.as_str(),
        })
    }

    fn pred(&self, insn: &Insn) -> Result<bool, Error> {
        let Some(p) = insn.name("pred", self.core) else { return Ok(true) };
        if let Some(n) = p.trim().trim_start_matches('!').strip_prefix('p').and_then(|n| n.parse::<u8>().ok())
            && self.p_set >> n & 1 == 0
        {
            return Err(why(format!(
                "reads p{n} before the program sets it (left over from the job before, E477)"
            )));
        }
        Ok(match p.trim() {
            "" => true,
            "p0" => self.p[0],
            "p1" => self.p[1],
            "p2" => self.p[2],
            "p3" => self.p[3],
            "!p0" => !self.p[0],
            "!p1" => !self.p[1],
            // hardware (usse-predicates-predicate-pn): never runs
            "Pn" => false,
            other => return Err(why(format!("predicate {other}"))),
        })
    }

    fn exec(&mut self, insn: &Insn, bus: &mut dyn Bus) -> Result<Next, Error> {
        if self.moe_base != [0; 4] && half_form(insn.form) {
            return Err(why("smbo's base offsets on a half-float form (not measured)"));
        }
        let based;
        let insn = if self.moe_base != [0; 4] && !matches!(insn.form.op, "smbo" | "smlsi") {
            based = self.based(insn)?;
            &based
        } else {
            insn
        };
        let addressed;
        let insn = if self.moe_addr != ([0; 4], [0; 4])
            && !matches!(insn.form.op, "smbo" | "smlsi" | "smoa" | "smr")
        {
            if self.moe_base != [0; 4] || half_form(insn.form) {
                return Err(why("smoa with smbo or on a half-float form (not measured)"));
            }
            addressed = self.addressed(insn)?;
            &addressed
        } else {
            insn
        };
        let op = insn.form.op;
        if let Some((name, b, q)) = read_bit(insn.form, insn.word) {
            return Err(why(format!("{name} with enc[{b}] set, a bit the hardware reads ({q})")));
        }
        if op.is_empty() {
            return Err(why("no semantics for this form yet"));
        }
        let end = self.ends(insn);
        if !matches!(op, "br" | "ba" | "lapc" | "cache" | "eld")
            && !op.starts_with("ld")
            && !op.starts_with("st")
        {
            // flags whose effect is not modelled stop the program
            if let Some(f) = insn.name("flags", self.core) {
                for t in f.split('.').filter(|t| !t.is_empty()) {
                    // fpma.sat: its 8-bit results saturate anyway (usse-colour-ops-fpma-sat)
                    // hardware (usse-flags-other): .tpres and .partial change nothing
                    // a pixel sees
                    if !(matches!(t, "skipinv" | "syncs" | "nosched" | "end" | "tpres" | "partial")
                        || op == "fpma" && t == "sat"
                        || (COLOUR_REPEATS.contains(&op) || op == "idiv") && t.starts_with("repeat")
                        || op == "efo" && t == "gpiext"
                        || op == "smp" && matches!(t, "pcf" | "pcff16" | "sinf" | "rsd"))
                    {
                        return Err(why(format!("flag .{t}")));
                    }
                }
            }
        }
        if !self.pred(insn)? {
            // hardware (E491: 16 + 3 not-taken calls of usse-callfalse2 and 10 placed jobs of
            // usse-place-more, 29 of 29): a call that is not taken still
            // writes pclink, the index after it; whether it does for lapc, a repeat or the
            // predicate Pn was not run
            if matches!(op, "br" | "ba")
                && insn.name("flags", self.core).is_some_and(|f| f.split('.').any(|t| t == "savelink"))
            {
                if insn.name("pred", self.core).is_some_and(|p| p.trim() == "Pn") {
                    return Err(why("a call under Pn (not measured)"));
                }
                self.link = (self.pc as u32 + 1 + self.code_index) & PCLINK_MASK;
                self.link_set = true;
            }
            if op == "firh" {
                // whether a firh that does not run leaves the latch alone is not measured
                let k = insn.get("k").unwrap() as usize;
                self.firh_latch[k] = None;
                self.firh_written[k] = true;
            }
            return Ok(if end { Next::End } else { Next::Step });
        }
        let its = self.iterations(insn)?;
        let its = its.as_deref().unwrap_or(std::slice::from_ref(insn));
        let mut next = None;
        if matches!(op, "fdp" | "fdpc" | "fddp" | "fddpc") {
            self.now = Now::default();
            self.dot(its)?;
        } else {
            for it in its {
                self.now = Now::default();
                next = self.op(it, bus)?;
            }
            // E1061 read the registers of an iaddu32 test under a write mask, not the predicate it
            // leaves: a later read of it is refused as not set
            if op == "test" && its.len() > 1 {
                self.p_set &= !(1 << insn.get("p").unwrap());
            }
        }
        Ok(match (next, end) {
            (_, true) => Next::End,
            (Some(t), false) => Next::Jump(t),
            (None, false) => Next::Step,
        })
    }

    /// The iterations of a repeated instruction, each with its register
    /// operands advanced, or None when it does not repeat. Hardware
    /// (usse-repeat-order, usse-repeat-pred): the iterations run one after another, under
    /// the instance's one predicate; every register operand advances by 1 per
    /// iteration, .incsXYZ (usse-write-masks-incs-fmad) leaves sources 0, 1, 2 in place where its
    /// bit is clear; after smlsi (usse-repeat-smlsi) the destination advances by its
    /// increment 0 and source 1 by its increment 2. movc, movmsk, pack, rlp
    /// and fsc repeat the same way (usse-form-coverage-movc-movmsk-repeat,
    /// usse-form-coverage-pack-repeat, usse-form-coverage-rlp-repeat: rlp's carry runs through its
    /// predicate, usse-form-coverage-fsc-repeat), and a bitwise immediate source stays in
    /// place (usse-form-coverage-bitwise-repeat).
    fn iterations(&self, insn: &Insn) -> Result<Option<Vec<Insn>>, Error> {
        // hardware (usse-moe-swizzle, E097): after a swizzle-mode smlsi an instruction that does
        // not repeat takes component x's offset on its swizzled operands; with a write mask or
        // a colour operation's repeat the swizzle is not measured
        let swizzled = self.moe_swizzle.iter().any(Option::is_some) && insn.form.op != "smlsi";
        if swizzled
            && (insn.form.role("mask").is_some_and(|i| insn.v[i] != 1)
                || COLOUR_REPEATS.contains(&insn.form.op))
        {
            return Err(why("smlsi swizzle mode with a write mask or a colour operation (not measured)"));
        }
        match self.iterations_of(insn)? {
            None if swizzled => Ok(Some(vec![self.swizzled_once(insn)?])),
            r => Ok(r),
        }
    }

    /// A plain instruction under smlsi's swizzle mode: component x's offset added to its
    /// swizzled destination and sources (registers only; immediates and a load's or store's
    /// address operands stay).
    fn swizzled_once(&self, insn: &Insn) -> Result<Insn, Error> {
        let mut it = insn.clone();
        for (role, swz) in ["dst", "src0", "src1", "src2"].into_iter().zip(self.moe_swizzle) {
            let (Some(c), Some(i)) = (swz, insn.form.role(role)) else { continue };
            let v = insn.v[i];
            let bank = if role == "src0" { v >> 7 & 1 } else { v >> 7 & 7 };
            if insn.form.f[i].width() == 21 || bank >= 6 {
                continue;
            }
            let r = (v & 0x7f) as i32 + c[0];
            if !(0..124).contains(&r) {
                return Err(why(format!("swizzle takes {role} past its bank")));
            }
            it.v[i] = v & !0x7f | r as u32;
        }
        Ok(it)
    }

    fn iterations_of(&self, insn: &Insn) -> Result<Option<Vec<Insn>>, Error> {
        let op = insn.form.op;
        // The colour and dot products (and adif) carry the repeat in their
        // flags: the multiply flags' bits 3 and up, fpma's bits 3-5
        // (hardware, usse-colour-ops-dot-repeats, usse-video-ops-adif: every operand advances by
        // one, the colour ones in their six-bit numbering).
        if let Some(fi) = insn.form.role("flags")
            && COLOUR_REPEATS.contains(&op)
        {
            let v = insn.v[fi];
            let (n, plain) =
                if op == "fpma" { ((v >> 3 & 7) + 1, v & !(7 << 3)) } else { ((v >> 3) + 1, v & 7) };
            if n > 1 {
                let comps: Vec<i32> = (0..n as i32).collect();
                let bits = if op.starts_with("adif") { 7 } else { 6 };
                return self.steps_in(insn, fi, plain, &comps, 1, false, bits).map(Some);
            }
            return Ok(None);
        }
        // idiv's flags carry a four-bit repeat count, enc[47:44] (hardware, usse-idiv-enc47-grid:
        // iteration k divides src1 + k by src2 + k into dst + k and dst + k + 1)
        if let Some(fi) = insn.form.role("flags")
            && op == "idiv"
        {
            let v = insn.v[fi];
            if v >> 3 == 0 {
                return Ok(None);
            }
            // E367 ran the repeats into temporaries only
            if insn.get("dst").is_some_and(|d| d >> 7 != 0) {
                return Err(why("idiv repeated into pa"));
            }
            let comps: Vec<i32> = (0..=(v >> 3) as i32).collect();
            return self.steps(insn, fi, v & 7, &comps, 1, false).map(Some);
        }
        // A write mask other than .x (hardware, usse-write-masks-wmask-mov, usse-write-masks-wmask-or,
        // usse-write-masks-wmask-and-imm, usse-write-masks-wmask-other, usse-write-masks-wmask-frcp): component k writes d + k
        // from sources advanced by k, as iteration k of a repeat; immediates
        // stay.
        if let Some(mi) = insn.form.role("mask").filter(|&i| insn.v[i] != 1) {
            // E1061 (r16-usse urpt): the mask of an iaddu32 test into temporaries (.xy, .xyzw) repeats
            // it the same way; the masks of the other tests were not run
            let iaddu32_test = op == "test"
                && insn.name("op", self.core).as_deref() == Some("iaddu32")
                && insn.get("dst").is_some_and(|d| d >> 7 == 0);
            if !matches!(op, "mov" | "bitwise" | "movc" | "pack" | "fsc") && !iaddu32_test {
                let m = insn.name("mask", self.core).unwrap();
                let ran = if op == "test" { " (E1061 ran it on iaddu32 only)" } else { "" };
                return Err(why(format!("write mask {m} on {op}{ran}")));
            }
            let comps: Vec<i32> = (0..4).filter(|k| insn.v[mi] >> k & 1 != 0).collect();
            return self.steps(insn, mi, 1, &comps, 1, true).map(Some);
        }
        let Some(rep) = ["repeat", "rep", "rep16"].into_iter().find_map(|r| insn.form.role(r)) else {
            return Ok(None);
        };
        // fmad16's field is repeat2[0] | incs[3:1], always with the .incs bits
        let rep16 = insn.form.role("rep16") == Some(rep);
        let n = if rep16 { 1 + (insn.v[rep] & 1) } else { insn.v[rep] + 1 };
        if n == 1 {
            return Ok(None);
        }
        if !REPEATS.contains(&op) {
            return Err(why(format!("{op} repeated")));
        }
        if half_form(insn.form) {
            return Err(why(format!("{op} repeated on half-float sources (not measured)")));
        }
        // the incs field: enc[53] set advances every source, else bits 3-1
        // advance sources 0-2; fddpc has none and its sources stay (fddpc)
        let incs = if rep16 {
            insn.v[rep] & !1
        } else {
            insn.get("incs").unwrap_or(if op == "fddpc" { 0 } else { 1 })
        };
        let comps: Vec<i32> = (0..n as i32).collect();
        // an internal register source of a repeated bitwise is not measured
        let internal = |r: &str| {
            insn.form.role(r).is_some_and(|i| insn.form.f[i].width() != 21 && insn.v[i] >> 7 & 7 == 7)
        };
        if op == "bitwise" && ["src1", "src2"].into_iter().any(internal) {
            return Err(why("bitwise repeated with an internal register source"));
        }
        self.steps(insn, rep, 0, &comps, incs, op == "bitwise").map(Some)
    }

    /// The iterations `comps` of a repeat or write mask, with the field `rep`
    /// set to `plain` in each and the register operands advanced (see
    /// iterations); `fixed_imm`: immediates stay instead of stopping.
    fn steps(
        &self,
        insn: &Insn,
        rep: usize,
        plain: u32,
        comps: &[i32],
        incs: u32,
        fixed_imm: bool,
    ) -> Result<Vec<Insn>, Error> {
        self.steps_in(insn, rep, plain, comps, incs, fixed_imm, 7)
    }

    /// steps, with register numbers of `bits` bits (6 for the colour
    /// operands: r0-r59, then i0-i3; 7 for the others).
    #[allow(clippy::too_many_arguments)]
    fn steps_in(
        &self,
        insn: &Insn,
        rep: usize,
        plain: u32,
        comps: &[i32],
        incs: u32,
        fixed_imm: bool,
        bits: u32,
    ) -> Result<Vec<Insn>, Error> {
        let mask = (1u32 << bits) - 1;
        let advances = |k: u32| incs & 1 != 0 || incs >> (4 - k) & 1 != 0;
        let mut step = [("dst", 1), ("src0", 1), ("src1", 1), ("src2", 1)];
        if let Some(inc) = self.moe_inc {
            // hardware (usse-repeat-smlsi, usse-moe-smlsi-three-sources): increments 0-3 are
            // the destination's and sources 0-2's
            (step[0].1, step[1].1, step[2].1, step[3].1) = (inc[0], inc[1], inc[2], inc[3]);
        }
        let mut its = Vec::with_capacity(comps.len());
        for &k in comps {
            let mut it = insn.clone();
            it.v[rep] = plain;
            for (s, &(role, inc)) in step.iter().enumerate() {
                let Some(i) = insn.form.role(role) else { continue };
                let swz = self.moe_swizzle[s];
                if swz.is_none() && (k == 0 || (s > 0 && !advances(s as u32)) || inc == 0) {
                    continue;
                }
                let v = insn.v[i];
                let f = &insn.form.f[i];
                // register banks only: an immediate, the rotated immediate or
                // an internal register does not step (not measured)
                let bank = if role == "src0" { v >> 7 & 1 } else { v >> 7 & 7 };
                if f.width() == 21 || bank >= 6 {
                    if fixed_imm {
                        continue;
                    }
                    return Err(why(format!("{role} immediate repeated")));
                }
                let r = (v & mask) as i32 + swz.map_or(k * inc, |c| c[k as usize % 4]);
                let top = match bits {
                    6 if bank == 0 && v & 63 < 60 => 60,
                    6 => 64,
                    _ if bank == 0 && v & 0x7f < 124 => 124,
                    _ => 128,
                };
                if !(0..top).contains(&r) {
                    return Err(why(format!("{role} repeated past its bank")));
                }
                it.v[i] = v & !mask | r as u32;
            }
            its.push(it);
        }
        Ok(its)
    }

    /// The dot products over their iterations. Hardware: fdp (usse-dot-products-fdp-count,
    /// usse-dot-products-fdp-rounding) sums the products in turn, each product and each sum
    /// rounded, into the last iteration's destination only; fdpc (fdpc,
    /// usse-dot-products-fdpc-clip) gives fdp's value and leaves p0-p3 and i0-i2 alone (its clip
    /// result is not visible); fddp and fddpc (fddp, fddpc) sum s0 * s1 into
    /// the destination and s0 * s2 into i<n>. The rounding of all but fdp is
    /// not measured (their probes are exact), so an inexact step stops.
    fn dot(&mut self, its: &[Insn]) -> Result<(), Error> {
        let op = its[0].form.op;
        let double = op.starts_with("fddp");
        let mut acc: [Option<u32>; 2] = [None, None];
        for it in its {
            let pairs: &[(&str, &str)] =
                if double { &[("src0", "src1"), ("src0", "src2")] } else { &[("src1", "src2")] };
            for (k, &(x, y)) in pairs.iter().enumerate() {
                let read = |r: &str| self.fval(it, r);
                let (a, b) = (read(x)?, read(y)?);
                let p = flt::mul(a, b)?;
                let s = match acc[k] {
                    None => p,
                    Some(s) => flt::add(Ok(s), p)?,
                };
                if op != "fdp" {
                    let exact = |r: u32, e: f64| f32::from_bits(r) as f64 == e;
                    let pe = f32::from_bits(a) as f64 * f32::from_bits(b) as f64;
                    let se = acc[k].map_or(0.0, |s| f32::from_bits(s) as f64) + f32::from_bits(p) as f64;
                    if !exact(p, pe) || !exact(s, se) {
                        return Err(why(format!("{op} rounding (not measured)")));
                    }
                }
                acc[k] = Some(s);
            }
        }
        let last = its.last().unwrap();
        if double {
            self.set_i(last.get("idst").unwrap() as usize, acc[1].unwrap())?;
        }
        self.write(last, acc[0].unwrap())
    }

    /// The pack group: the packs of f32 to 8- and 16-bit components and the
    /// unpacks back to f32.
    fn pack(&mut self, insn: &Insn) -> Result<(), Error> {
        let text = insn.name("op", self.core).unwrap();
        let mut parts = text.split('.');
        let fmt = parts.next().unwrap();
        let (mut scale, mut renable) = (false, false);
        for f in parts {
            match f {
                "skipinv" | "syncs" | "nosched" | "end" => {}
                "scale" => scale = true,
                "renable" => renable = true,
                _ => return Err(why(format!("{fmt} flag .{f}"))),
            }
        }
        let round = insn.name("round", self.core).unwrap();
        if let Some(from) = fmt.strip_prefix("unpckf32") {
            if insn.get("bytemask") != Some(15) {
                return Err(why(format!("{fmt} with a byte mask")));
            }
            if round != "nearest" {
                return Err(why(format!("{fmt} rounding {round}")));
            }
            if renable {
                return Err(why(format!("{fmt}.renable")));
            }
            return self.unpack_f32(insn, fmt, from, scale);
        }
        if fmt == "pckf16f32" {
            return self.pack_f16(insn, renable, &round);
        }
        if fmt == "pckc10f32" {
            return self.pack_c10(insn, &round);
        }
        if let Some(r) = self.unpack_int(insn, fmt, scale)? {
            return self.write(insn, r);
        }
        if fmt == "statomic" {
            // hardware (statomic): bytes s1.c, s2.c, s1.c, s2.c, each read as
            // signed and clamped at 0, whatever the mode and .scale
            if insn.get("bytemask") != Some(15) {
                return Err(why("statomic with a byte mask"));
            }
            let byte = |m: &Self, role: &str| -> Result<u32, Error> {
                let v = insn.get(role).unwrap();
                let x = m.src(v & 0x3ff, 6)? >> (8 * (v >> 10 & 3)) & 0xff;
                Ok(if x < 128 { x } else { 0 })
            };
            let (x, y) = (byte(self, "src1")?, byte(self, "src2")?);
            return self.write(insn, x | y << 8 | x << 16 | y << 24);
        }
        match fmt.strip_prefix("pck").and_then(|f| f.strip_suffix("f32")) {
            Some(to @ ("u8" | "s8" | "o8" | "u16" | "s16")) => self.pack_f32(insn, fmt, to, scale, &round),
            _ => Err(why(fmt.to_string())),
        }
    }

    /// An unpack to f32. A source is operand[9:0] | select[11:10]: byte
    /// `select`, or the 16 bits at that byte (hardware, usse-pack-unpack-select). With
    /// .scale (unpack-*-scale) a u8 is divided by 255, an s8 by 127 clamped at
    /// -1, an o8 is the s8 of the byte ^ 0x80, a u16 divided by 65535 and an
    /// s16 by 32767 clamped at -1, each rounded once to nearest.
    fn unpack_f32(&mut self, insn: &Insn, fmt: &str, from: &str, scale: bool) -> Result<(), Error> {
        let v = insn.get("src1").unwrap();
        let (w, sel) = (self.src(v & 0x3ff, 6)?, v >> 10 & 3);
        if from == "c10" {
            // hardware (usse-pack-unpack-c10): lane c / 255 (.3 is 0), lanes clamped to
            // +/-510
            let lane = if sel == 3 { 0 } else { chans(w, true)[sel as usize] };
            return self.write(insn, ((lane as f64 / 255.0) as f32).to_bits());
        }
        if from == "f16" {
            // hardware (usse-pack-unpack-f16): exact, infinities kept, a NaN 0x7fffffff;
            // (usse-pack-unpack-select) .3 of a 16-bit format reads nothing
            if sel == 3 {
                return self.write(insn, 0);
            }
            let h = w >> (8 * sel) & 0xffff;
            let (sign, e, f) = (h >> 15, h >> 10 & 31, h & 1023);
            let v = match (e, f) {
                (31, 0) => sign << 31 | 0x7f80_0000,
                (31, _) => 0x7fff_ffff,
                _ => {
                    let mag = if e == 0 {
                        f as f32 * 2f32.powi(-24)
                    } else {
                        (1024 + f) as f32 * 2f32.powi(e as i32 - 25)
                    };
                    (if sign != 0 { -mag } else { mag }).to_bits()
                }
            };
            return self.write(insn, v);
        }
        let x = match from {
            "u8" | "s8" | "o8" => w >> (8 * sel) & 0xff,
            "u16" | "s16" if sel < 3 => w >> (8 * sel) & 0xffff,
            // hardware (usse-pack-unpack-select): .3 of a 16-bit format reads nothing
            "u16" | "s16" => 0,
            _ => return Err(why(format!("{fmt} of component {sel}"))),
        };
        // The quotients of an integer by 255, 127, 65535 or 32767 are never
        // f32 ties, and f64 holds them closely enough to round once.
        let f = match (from, scale) {
            ("u8" | "u16", false) => x as f64,
            ("u8", true) => x as f64 / 255.0,
            ("s8", true) => (x as u8 as i8 as f64 / 127.0).max(-1.0),
            ("o8", true) => ((x ^ 0x80) as u8 as i8 as f64 / 127.0).max(-1.0),
            ("u16", true) => x as f64 / 65535.0,
            ("s16", true) => (x as u16 as i16 as f64 / 32767.0).max(-1.0),
            _ => return Err(why(format!("{fmt} without .scale"))),
        };
        self.write(insn, (f as f32).to_bits())
    }

    /// pckf16f32: s1 to the low half, s2 to the high one. Hardware
    /// (usse-pack-f16): without .renable truncated toward zero whatever the mode
    /// (nearest and up measured), saturated at 65504, half denormals kept;
    /// .renable first rounds to an integer by the mode.
    fn pack_f16(&mut self, insn: &Insn, renable: bool, round: &str) -> Result<(), Error> {
        if !renable && round != "nearest" && round != "up" {
            return Err(why(format!("pckf16f32 rounding {round} (not measured)")));
        }
        let conv = |role: &str| -> Result<u32, Error> {
            let v = insn.get(role).unwrap();
            if v >> 10 != 0 {
                return Err(why("pckf16f32 of a component select"));
            }
            let b = self.src(v & 0x3ff, 6)?;
            if b >> 23 & 0xff == 0xff || (b >> 23 & 0xff == 0 && b & 0x7f_ffff != 0) {
                return Err(why("pckf16f32 of an infinity, NaN or denormal"));
            }
            let mut x = f32::from_bits(b) as f64;
            if renable {
                x = match round {
                    "nearest" => x.round_ties_even(),
                    "down" => x.floor(),
                    "up" => x.ceil(),
                    _ => x.trunc(),
                };
            }
            let (sign, a) = ((b >> 31) << 15, x.abs());
            if a >= 65504.0 {
                return Ok(sign | 0x7bff);
            }
            if a < 2f64.powi(-14) {
                return Ok(sign | (a * 2f64.powi(24)).floor() as u32);
            }
            let e = a.log2().floor() as i32;
            let e = if 2f64.powi(e) > a {
                e - 1
            } else if 2f64.powi(e + 1) <= a {
                e + 1
            } else {
                e
            };
            let n = (a * 2f64.powi(10 - e)).floor() as u32;
            if renable && n as f64 != a * 2f64.powi(10 - e) {
                return Err(why("pckf16f32.renable of an integer a half cannot hold"));
            }
            Ok(sign | ((e + 15) as u32) << 10 | (n - 1024))
        };
        let (lo, hi) = (conv("src1")?, conv("src2")?);
        self.write(insn, lo | hi << 16)
    }

    /// pckc10f32 (hardware, usse-pack-c10): x * 255 to nearest even, clamped to
    /// +/-510, in 10-bit lanes taking s1, s2, s1; bits 30-31 are 0.
    fn pack_c10(&mut self, insn: &Insn, round: &str) -> Result<(), Error> {
        if round != "nearest" {
            return Err(why(format!("pckc10f32 rounding {round} (not measured)")));
        }
        let lane = |role: &str| -> Result<u32, Error> {
            let v = insn.get(role).unwrap();
            let b = self.src(v & 0x3ff, 6)?;
            if b >> 23 & 0xff == 0xff || (b >> 23 & 0xff == 0 && b & 0x7f_ffff != 0) {
                return Err(why("pckc10f32 of an infinity, NaN or denormal"));
            }
            let x = (f32::from_bits(b) as f64 * 255.0).round_ties_even().clamp(-510.0, 510.0);
            Ok(x as i32 as u32 & 0x3ff)
        };
        let (a, b) = (lane("src1")?, lane("src2")?);
        self.write(insn, a | b << 10 | a << 20)
    }

    /// The unpacks that convert no float (hardware, usse-pack-unpack-u8s8, usse-pack-unpack-s16u8,
    /// usse-pack-unpack-u16s8, usse-pack-unpack-s16s8, usse-pack-unpack-u16u8, usse-pack-unpack-c10-16), or None for
    /// another format: unpcks16s8 sign-extends, unpcks16u8 and unpcku16u8
    /// zero-extend, unpcku16s8 makes a negative 0 and unpcku8s8 0x7f, laid
    /// out as packs (bytes s1, s2, s1, s2 or halves s1, s2); unpcku16c10 and
    /// unpcks16c10 copy bits 4, 6 and 8 of lane 0 of source 1 into bits 15,
    /// 1-14 and 0, whatever the selects.
    fn unpack_int(&self, insn: &Insn, fmt: &str, scale: bool) -> Result<Option<u32>, Error> {
        if !matches!(
            fmt,
            "unpcku8s8"
                | "unpcks16u8"
                | "unpcku16u8"
                | "unpcks16s8"
                | "unpcku16s8"
                | "unpcku16c10"
                | "unpcks16c10"
        ) {
            return Ok(None);
        }
        if insn.get("bytemask") != Some(15) {
            return Err(why(format!("{fmt} with a byte mask")));
        }
        let byte = |role: &str| -> Result<u32, Error> {
            let v = insn.get(role).unwrap();
            Ok(self.src(v & 0x3ff, 6)? >> (8 * (v >> 10 & 3)) & 0xff)
        };
        if fmt.ends_with("c10") {
            let w = self.src(insn.get("src1").unwrap() & 0x3ff, 6)?;
            let bit = |n: u32| w >> n & 1;
            return Ok(Some(bit(4) << 15 | if bit(6) != 0 { 0x7ffe } else { 0 } | bit(8)));
        }
        if scale {
            return Err(why(format!("{fmt}.scale (not measured)")));
        }
        let conv = |x: u32| -> u32 {
            let neg = x >= 128;
            match fmt {
                "unpcku8s8" if neg => 0x7f,
                "unpcku16s8" if neg => 0,
                "unpcks16s8" if neg => (x | 0xff00) & 0xffff,
                _ => x,
            }
        };
        let (a, b) = (conv(byte("src1")?), conv(byte("src2")?));
        Ok(Some(if fmt == "unpcku8s8" { a | b << 8 | a << 16 | b << 24 } else { a | b << 16 }))
    }

    /// A pack of two f32 sources to 8- or 16-bit values. Hardware:
    /// - pack-*-int: rounded by the mode (nearest even, down, up, zero) and
    ///   saturated; o8 is the s8 value + 128;
    /// - pack-*-scale: with .scale, x * 255, 127, 65535 or 32767 exactly,
    ///   rounded to nearest whatever the mode, saturated (s8/s16 at -K);
    /// - 8-bit values go to bytes 0-3 as s1, s2, s1, s2, 16-bit ones to the
    ///   low and high halves; usse-pack-u8-bytemask and usse-pack-u16-bytemask show
    ///   which value each enabled byte takes under every byte mask.
    fn pack_f32(&mut self, insn: &Insn, fmt: &str, to: &str, scale: bool, round: &str) -> Result<(), Error> {
        let (k, wide) = match to {
            "u8" => (255.0, false),
            "s8" | "o8" => (127.0, false),
            "u16" => (65535.0, true),
            _ => (32767.0, true),
        };
        let (mut lo, hi) = match to {
            "u8" | "u16" => (0.0, k),
            "s8" | "o8" => (-128.0, 127.0),
            _ => (-32768.0, 32767.0),
        };
        if scale && lo < 0.0 {
            lo = -k;
        }
        let conv = |role: &str| -> Result<u32, Error> {
            let v = insn.get(role).unwrap();
            if v >> 10 != 0 {
                return Err(why(format!("{fmt} of a component select")));
            }
            let b = self.src(v & 0x3ff, 6)?;
            if b >> 23 & 0xff == 0xff || (b >> 23 & 0xff == 0 && b & 0x7f_ffff != 0) {
                return Err(why(format!("{fmt} of an infinity, NaN or denormal")));
            }
            let x = f32::from_bits(b) as f64;
            let n = if scale {
                // x * k is exact in f64, rounded to nearest even
                // (pack-conversions: 96 random values agree)
                (x * k).round_ties_even()
            } else {
                match round {
                    "nearest" => x.round_ties_even(),
                    "down" => x.floor(),
                    "up" => x.ceil(),
                    _ => x.trunc(),
                }
            };
            let n = n.clamp(lo, hi) as i32 + if to == "o8" { 128 } else { 0 };
            Ok(n as u32)
        };
        let (a, b) = (conv("src1")?, conv("src2")?);
        let m = insn.get("bytemask").unwrap();
        if m != 15 && to != "u8" && to != "u16" {
            return Err(why(format!("{fmt} with a byte mask")));
        }
        let en = |i: u32| m >> i & 1 != 0;
        let bytes = if wide {
            // the upper half takes s2 where byte 0 is enabled, else s1
            let up = if en(0) { b } else { a };
            [a & 0xff, a >> 8 & 0xff, up & 0xff, up >> 8 & 0xff]
        } else {
            let pick = |second: bool| if second { b } else { a } & 0xff;
            [a & 0xff, pick(en(0)), pick((en(0) as u8 + en(1) as u8) % 2 == 1), pick(en(0) || en(1) || en(2))]
        };
        let mut w = 0;
        for (i, &x) in bytes.iter().enumerate() {
            w |= x << (8 * i);
        }
        if m != 15 {
            if m == 0 {
                return Ok(());
            }
            let d = insn.get("dst").unwrap();
            if d >> 7 != 0 || d & 0x7f >= 124 {
                return Err(why(format!("{fmt} byte mask on a non-temporary")));
            }
            let keep = (0..4).filter(|&i| !en(i)).fold(0u32, |k, i| k | 0xff << (8 * i));
            w = self.temp(d as usize)? & keep | w & !keep;
        }
        self.write(insn, w)
    }

    /// A colour operand (six-bit registers, a .c10 bit and the bank above:
    /// usse_isa's C10 kind) as an ordinary one, number[6:0] | bank[9:7], and
    /// its .c10 bit. Indexed operands and immediates stop.
    fn colour_operand(v: u32, dst: bool) -> Result<(u32, bool), Error> {
        let (bank, r) = (v >> 7 & 7, v & 63);
        if v >> 10 != 0 || bank == 5 || bank == 6 || bank == if dst { 3 } else { 4 } {
            return Err(why("colour operand (indexed, immediate or modified)"));
        }
        let reg = match bank {
            0 if r >= 60 => 7 << 7 | (r - 60),
            b => b << 7 | r,
        };
        Ok((reg, v >> 6 & 1 != 0))
    }

    /// A colour source's channels (see chans).
    fn colour_src(&self, v: u32) -> Result<Chans, Error> {
        let (reg, c10) = Self::colour_operand(v, false)?;
        Ok(chans(self.src(reg, 6)?, c10))
    }
    /// sop2, per byte: bytes 0-2 by the colour selection, byte 3 by the alpha
    /// one. Hardware (usse-colour-ops-sop2-selectors, usse-colour-ops-sop2-ops, usse-colour-ops-sop2-random):
    /// - add/sub: round((x1 * f1 +/- x2 * f2) / 255) once, half up, clamped
    ///   to 0-255; min/max compare x1 and x2 themselves, whatever the factors;
    /// - factors: zero, s1, s2 (this byte), s1a, s2a (the alpha bytes), asat =
    ///   min(s1a, 1 - s2a), and .comp = 1 - factor, except asat.comp =
    ///   min(1 - s1a, s2a);
    /// - s2scale (first factor) is s2 and doubles the result; zeros (second
    ///   factor) is 0, or 1 with .comp, and for add/sub reads x2 as x2 - 128;
    /// - for add/sub a leading comp complements x1, and neg (alpha) negates.
    ///
    /// sop2wm (sop2wm) takes one selector pair for all four bytes, the colour
    /// operation for bytes 0-2 and the alpha one for byte 3, and writes the
    /// bytes its mask enables (bit n, byte n).
    fn sop2(&mut self, insn: &Insn) -> Result<(), Error> {
        let s1 = self.colour_src(insn.get("src1").unwrap())?;
        let s2 = self.colour_src(insn.get("src2").unwrap())?;
        let (d, dc10) = Self::colour_operand(insn.get("dst").unwrap(), true)?;
        let (csel, asel, mask) = match insn.name("sel", self.core) {
            None => (insn.name("csel", self.core).unwrap(), insn.name("asel", self.core).unwrap(), 15),
            Some(sel) => {
                // "f1, f2, colour op, alpha op"
                let (pair, aop) = sel.rsplit_once(", ").unwrap();
                let (f12, cop) = pair.rsplit_once(", ").unwrap();
                (format!("{f12}, {cop}"), format!("{f12}, {aop}"), insn.get("bytemask").unwrap())
            }
        };
        let mut v = [0; 4];
        for ch in 0..4 {
            v[ch as usize] = blend(if ch == 3 { &asel } else { &csel }, s1, s2, ch)?;
        }
        let mut w = colour_out(v, dc10);
        if mask != 15 {
            if d >> 7 != 0 || d & 0x7f >= 124 || dc10 {
                return Err(why("sop2wm byte mask on a non-temporary"));
            }
            let keep = (0..4).filter(|&i| mask >> i & 1 == 0).fold(0u32, |k, i| k | 0xff << (8 * i));
            w = self.temp(d as usize)? & keep | w & !keep;
        }
        self.write_dst(d, w)
    }

    /// A colour source 0 (six-bit registers, .c10 bit 6, pa bit 7, a
    /// modifier bit 8) as an ordinary source 0, number[6:0] | pa[7], and its
    /// .c10 bit.
    fn colour_operand0(v: u32) -> Result<(u32, bool), Error> {
        let (pa, r) = (v >> 7 & 1, v & 63);
        if v >> 8 != 0 {
            return Err(why("modified colour source 0"));
        }
        Ok((if pa == 0 && r >= 60 { 124 + r - 60 } else { pa << 7 | r }, v >> 6 & 1 != 0))
    }

    fn colour_src0(&self, v: u32) -> Result<Chans, Error> {
        let (reg, c10) = Self::colour_operand0(v)?;
        Ok(chans(self.src0(reg)?, c10))
    }
    /// sop3, lrp and sop3c on three sources, per byte, with sop2's rounding:
    /// round(sum / 255) half up, clamped. Hardware (usse-colour-ops-sop3-lrp, usse-colour-ops-sop3-random,
    /// x-sop3, x-arsop):
    /// - sop3's colour is sop2's add/sub of s1 * f1 and s2 * f2, the factors
    ///   including s0 and s0a; lrp's colour is f1 * (1 - w) + f2 * w, w being
    ///   s0 or s0a; sop3c's is x1 * f1 + x2 * f2, x1 and x2 named by its third
    ///   selection (s1, s1.comp or one; s2 or s2.comp);
    /// - alpha: asop as sop2's; arsop sub is s2a * g - s1a * (the second
    ///   colour factor), arsop add 0; alrp is g1 * (1 - s0a) + g2 * s0a.
    ///
    /// The colour neg of the alrp form fits no reading yet and stops.
    fn sop3(&mut self, insn: &Insn) -> Result<(), Error> {
        let s = [
            self.colour_src0(insn.get("src0").unwrap())?,
            self.colour_src(insn.get("src1").unwrap())?,
            self.colour_src(insn.get("src2").unwrap())?,
        ];
        let (d, dc10) = Self::colour_operand(insn.get("dst").unwrap(), true)?;
        if insn.form.op == "sop3c"
            && (dc10 || ["src0", "src1", "src2"].iter().any(|r| insn.get(r).unwrap() >> 6 & 1 != 0))
        {
            return Err(why("sop3c on .c10 operands (not measured)"));
        }
        let csel = insn.name("csel", self.core).unwrap();
        let alpha =
            ["asop", "arsop", "alrp"].into_iter().find_map(|r| Some((r, insn.name(r, self.core)?))).unwrap();
        let v = blend3(insn.form.op, &csel, (alpha.0, &alpha.1), s)?;
        self.write_dst(d, colour_out(v, dc10))
    }

    /// movmsk d, s1, s2.c (and .smsk d, s0, s1, s2.c): s1 into d where
    /// component c of s2 passes, else d stays. Hardware (usse-movc-movmsk-mask, -u8,
    /// -flt, -flt16): .mask tests bit 0 of byte c, .u8 bit 7 of byte c, .flt
    /// s2 >= 0.5 (a NaN fails), .flt16 the half at bits 0-15, 8-23, 16-31
    /// or 16-31 for c = 0-3 >= 0.5; .smsk (usse-movc-movmsk-smsk, -smsk2) also needs bit 0 of s0
    /// for .u8 and .flt, while .mask ignores it.
    fn movmsk(&mut self, insn: &Insn) -> Result<(), Error> {
        let fmt = insn.name("fmt", self.core).unwrap_or(".u8".into());
        let c = insn.get("comp").unwrap();
        let s2 = self.src(insn.get("src2").unwrap(), 6)?;
        let mut pass = match fmt.as_str() {
            ".mask" => s2 >> (8 * c) & 1 != 0,
            ".u8" => s2 >> (8 * c + 7) & 1 != 0,
            ".flt" if c == 0 => flt::at_least_half(s2, false)?,
            // the half at bits 0-15, 8-23, 16-31, 16-31 (conditional-moves)
            ".flt16" => flt::at_least_half(s2 >> [0, 8, 16, 16][c as usize] & 0xffff, true)?,
            f => return Err(why(format!("movmsk{f} of component {c}"))),
        };
        if let Some(v) = insn.get("src0")
            && fmt != ".mask"
        {
            pass &= self.src0(v)? & 1 != 0;
        }
        let s1 = self.src(insn.get("src1").unwrap(), 6)?;
        if pass { self.write(insn, s1) } else { Ok(()) }
    }

    /// The integer dot products. Hardware (usse-integer-dot-intdot-lanes, usse-integer-dot-intdot-alpha):
    /// - a source byte is x, 255 - x with .comp, and with off x - 128; S is
    ///   the sum of the products of the first three (dot3) or four bytes;
    /// - u8: bytes 0-2 are round(S * Cx / 255), half up, saturated, and the
    ///   alpha byte round(S * Ax / 255); u8dot3's alpha operations take the
    ///   raw source alphas: aadd/asub round((f1 f2 +/- f3 f4) * Ax / 255),
    ///   alrp lerps g1 to g2 by s0a, alrpc lerps 1 - g1 to g2;
    /// - u16: round(S * Cx * 32767 / 65025), saturated at +/-32767, in both
    ///   halves.
    fn idot(&mut self, insn: &Insn) -> Result<(), Error> {
        let op = insn.form.op;
        let byte = |w: u32, c: u32| (w >> (8 * c) & 0xff) as i64;
        let read = |m: &mut Self, role: &str| -> Result<(u32, bool), Error> {
            let v = insn.get(role).unwrap();
            let (reg, c10) = Self::colour_operand(v & 0x3ff, false)?;
            if c10 {
                return Err(why("integer dot product of a .c10 operand"));
            }
            Ok((m.src(reg, 6)?, v >> 10 & 1 != 0))
        };
        let ((s1, c1), (s2, c2)) = (read(self, "src1")?, read(self, "src2")?);
        let off = insn.name("off", self.core).as_deref() == Some("off");
        let lanes = |w: u32, comp: bool| {
            (0..4).map(move |c| {
                let x = if comp { 255 - byte(w, c) } else { byte(w, c) };
                if off { x - 128 } else { x }
            })
        };
        let p: Vec<i64> = lanes(s1, c1).zip(lanes(s2, c2)).map(|(a, b)| a * b).collect();
        let s = if op == "idot4" { p.iter().sum() } else { p[..3].iter().sum::<i64>() };
        let scale = |r: &str| 1i64 << insn.get(r).unwrap();
        let wide = op == "u16dot3" || insn.name("fmt", self.core).as_deref() == Some("u16");
        let (d, dc10) = Self::colour_operand(insn.get("dst").unwrap(), true)?;
        if dc10 {
            return Err(why("integer dot product into a .c10 destination"));
        }
        if wide {
            let t = 2 * s * scale("cx") * 32767;
            let v = (t + 65025).div_euclid(2 * 65025).clamp(-32767, 32767) as u32 & 0xffff;
            return self.write_dst(d, v | v << 16);
        }
        let c = colour_round(s * scale("cx"));
        let alpha = match insn.name("aop", self.core).as_deref() {
            None => colour_round(s * scale("ax")),
            Some(aop) => {
                let sel = insn.name("asel", self.core).unwrap();
                let g: Vec<&str> = sel.split(", ").collect();
                let s0 = match insn.get("src0") {
                    Some(v) => match Self::colour_operand0(v)? {
                        (reg, false) => self.src0(reg)?,
                        _ => return Err(why("integer dot product of a .c10 source 0")),
                    },
                    None => 0,
                };
                let f =
                    |k: usize| colour_factor(g[k], 3, [chans(s0, false), chans(s1, false), chans(s2, false)]);
                let a0 = byte(s0, 3);
                colour_round(match (aop, &g[..]) {
                    ("aadd", [_, _, _, _]) => (f(0)? * f(1)? + f(2)? * f(3)?) * scale("ax"),
                    ("asub", [_, _, _, _]) => (f(0)? * f(1)? - f(2)? * f(3)?) * scale("ax"),
                    ("alrp", [_, _]) => f(0)? * (255 - a0) + f(1)? * a0,
                    ("alrpc", [_, _]) => (255 - f(0)?) * (255 - a0) + f(1)? * a0,
                    _ => return Err(why(format!("u8dot3 alpha {aop} {sel}"))),
                })
            }
        };
        self.write_dst(d, colour_out([c, c, c, alpha], false))
    }

    /// efo: two multipliers, two adders, the destination one of i0, i1, a0, a1
    /// and optional writes of i0/i1. Hardware (usse-efo-dataflow, usse-efo-rounding):
    /// each product and sum is rounded (fmad's arithmetic), and the
    /// destination reads i0/i1 as they were before this instruction's writes.
    fn efo(&mut self, insn: &Insn) -> Result<(), Error> {
        let gp = insn.name("flags", self.core).is_some_and(|f| f.contains(".gpiext"));
        if gp && self.quad.is_none() {
            return Err(why("efo.gpiext reaches the other instances of the quad"));
        }
        let read_i0 = Cell::new(false);
        // its infinite and NaN inputs are not measured
        for r in ["src0", "src1", "src2", "i0", "i1"] {
            if let Ok(v) = self.efo_value(insn, r, false, &Cell::new(false))
                && flt::special(v)
            {
                return Err(why("efo of an infinity or NaN"));
            }
        }
        let dsel = ["i0", "i1", "a0", "a1"][insn.get("dsel").unwrap() as usize];
        let iw = insn.get("iw").unwrap();
        let w = [["a0", "a1"], ["a1", "a0"], ["m0", "m1"], ["a0", "m1"]][(iw & 3) as usize];
        let d = self.efo_value(insn, dsel, gp, &read_i0)?;
        let w0 = if iw & 4 != 0 { Some(self.efo_value(insn, w[0], gp, &read_i0)?) } else { None };
        let w1 = if iw & 8 != 0 { Some(self.efo_value(insn, w[1], gp, &read_i0)?) } else { None };
        if gp {
            // hardware (usse-internal-registers-efo-gpiext-quad, usse-internal-registers-efo-gpiext-race): a write of i0 goes
            // to the instance's own i2; the four writes of i1 end in the
            // top-right i0 (run_quad), whose reads of i0 meanwhile race
            let q = self.quad.as_ref().unwrap();
            if w1.is_some() && q.pos == 1 && read_i0.get() {
                return Err(why("efo.gpiext: the top-right i0 read races the i1 writes"));
            }
            if let Some(v) = w0 {
                self.set_i(2, v)?;
            }
            self.quad_i1 = w1;
        } else {
            if let Some(v) = w0 {
                self.set_i(0, v)?;
            }
            if let Some(v) = w1 {
                self.set_i(1, v)?;
            }
        }
        self.write(insn, d)
    }

    /// A value of efo's dataflow, computed from what it reads (so that a
    /// source or internal register it does not use is never read).
    fn efo_value(&self, insn: &Insn, name: &str, gp: bool, read_i0: &Cell<bool>) -> Result<u32, Error> {
        let neg = |x: u32, n: bool| if n { x ^ 0x8000_0000 } else { x };
        let add = insn.get("add").unwrap();
        let a = [
            ["m0", "m1", "i1", "i0"],
            ["m0", "src0", "i1", "i0"],
            ["m0", "i0", "i1", "m1"],
            ["src0", "src2", "src1", "src2"],
        ][(add & 3) as usize];
        let m = [
            [["src0", "src2"], ["src1", "src2"]],
            [["src2", "src1"], ["src2", "src2"]],
            [["src1", "src0"], ["src2", "src2"]],
            [["src1", "i0"], ["src2", "i1"]],
        ][insn.get("msel").unwrap() as usize];
        let v = |n: &str| self.efo_value(insn, n, gp, read_i0);
        // .gpiext: the multipliers read own i2 for i0 and own i0 for i1
        let mul = |n: &str| match (gp, n) {
            (true, "i0") => v("i2"),
            (true, "i1") => v("i0"),
            _ => v(n),
        };
        Ok(match name {
            "src0" | "src1" => {
                let x = insn.get(name).unwrap();
                // source 0 numbers its banks r, pa, o, sa
                let bank = if name == "src0" { [0, 2, 1, 3][(x >> 7 & 3) as usize] } else { x >> 7 & 3 };
                neg(self.src(bank << 7 | x & 0x7f, 6)?, x >> 9 & 1 != 0)
            }
            "src2" => {
                let x = insn.get(name).unwrap();
                neg(self.src(x & 0x3ff, 6)?, x >> 10 & 1 != 0)
            }
            "i0" | "i1" | "i2" => {
                let k = ["i0", "i1", "i2"].iter().position(|&x| x == name).unwrap();
                if k == 0 {
                    read_i0.set(true);
                }
                self.internal(k)?
            }
            "m0" => flt::mul(mul(m[0][0])?, mul(m[0][1])?)?,
            "m1" => flt::mul(mul(m[1][0])?, mul(m[1][1])?)?,
            "a0" => flt::add(v(a[0]), neg(v(a[1])?, add & 8 != 0))?,
            _ => flt::add(Ok(neg(v(a[2])?, add & 4 != 0)), v(a[3])?)?,
        })
    }

    /// fpma per byte: a + b * c / 255 of its three selections (the alpha byte
    /// by the alpha ones), rounded half up and saturated; .neg on source 0
    /// subtracts a (hardware: fpma, usse-colour-ops-fpma-sat, x-fpma, every non-c10 byte).
    /// Where a selects s1 the probes cannot tell whether .neg applies.
    fn fpma(&mut self, insn: &Insn) -> Result<(), Error> {
        let v0 = insn.get("src0").unwrap();
        let s = [
            self.colour_src0(v0 & 0xff)?,
            self.colour_src(insn.get("src1").unwrap())?,
            self.colour_src(insn.get("src2").unwrap())?,
        ];
        let neg = v0 >> 8 & 1 != 0;
        let (d, dc10) = Self::colour_operand(insn.get("dst").unwrap(), true)?;
        let (csel, asel) = (insn.name("csel", self.core).unwrap(), insn.name("asel", self.core).unwrap());
        let mut v = [0; 4];
        for ch in 0..4 {
            let sel: Vec<&str> = if ch == 3 { &asel } else { &csel }.split(", ").collect();
            if neg && sel[0].starts_with("s1") {
                return Err(why("fpma .neg with s1 added"));
            }
            let f = |k: usize| colour_factor(sel[k], ch, s);
            let a = if neg { -f(0)? } else { f(0)? };
            v[ch as usize] = colour_round(a * 255 + f(1)? * f(2)?);
        }
        self.write_dst(d, colour_out(v, dc10))
    }

    /// The dual-issue group. Hardware (dual-issue, usse-dual-issue-predicates,
    /// usse-dual-issue-ima32): the primary computes as alone, the secondary on
    /// i0-i2 or, for a register operand, the primary's source in that position
    /// without its .neg; both read before either writes, and the secondary
    /// wins a shared destination. The pairs that share a unit
    /// (usse-dual-issue-shared): a multiplying secondary of a two-product primary
    /// gets its second product (fmad adding its own c), an fmsa secondary of
    /// fmad, fadm or fmsa (and ima32 of ima32) the primary's result, the
    /// add-type and fmad secondaries of fminmax max(a, b) - c, and fmad +
    /// fmaxmin gives a*b - c and b - c, fmad + fmad16 a primary 0 and the
    /// secondary as alone. .repeat2 repeats both: the primary's
    /// operands advance, the secondary runs again on the internal registers
    /// (a secondary register operand stops). An fddp primary (usse-form-coverage-dual,
    /// x-dual, usse-dual-issue-conflicts) writes d = s0 * s1 and i0 = s0 * s2, its
    /// i0 winning over the secondary's: a mov or function secondary runs as
    /// alone, an arithmetic one writes s0 * s2 to its destination (seen for
    /// fadd and fmul; the others only with destination i0). The undecided
    /// pairs, fddp's rounding and fddp under .repeat2 stop.
    fn dual(&mut self, insn: &Insn) -> Result<(), Error> {
        let pi = insn.form.role("pop").unwrap();
        if insn.v[pi] & 64 == 0 {
            return self.dual_once(insn);
        }
        if insn.name("pop", self.core).unwrap().starts_with("fddp") {
            return Err(why("dual issue fddp.repeat2 (not measured)"));
        }
        if half_form(insn.form) {
            return Err(why("dual issue .repeat2 on half-float sources (not measured)"));
        }
        for (r, top) in [("r0", 3), ("r1", 3), ("r2", 3), ("rm0", 1), ("rm1", 1), ("rm2", 1)] {
            if let Some(i) = insn.form.role(r) {
                let w = insn.form.f[i].width() - if top == 3 { 2 } else { 1 };
                if insn.v[i] >> w == top {
                    return Err(why("dual issue .repeat2 with a secondary register operand"));
                }
            }
        }
        for it in self.steps(insn, pi, insn.v[pi] & !64, &[0, 1], 1, false)? {
            self.dual_once(&it)?;
        }
        Ok(())
    }

    fn dual_once(&mut self, insn: &Insn) -> Result<(), Error> {
        let pop = insn.name("pop", self.core).unwrap();
        let mut parts = pop.split('.');
        let p = parts.next().unwrap();
        for f in parts {
            if !matches!(f, "skipinv" | "syncs" | "nosched") {
                return Err(why(format!("dual issue .{f}")));
            }
        }
        let sop = insn.name("sop", self.core).unwrap();
        let func = matches!(sop.as_str(), "frcp" | "frsq" | "fexp" | "flog" | "fsin" | "fcos");
        // how the secondary runs: as alone, or on a value the shared unit gives
        #[derive(PartialEq)]
        enum Pair {
            Alone,
            SecondProduct,
            Result,
            MaxMinusC,
            MaxMin,
            NoPrimary,
            FddpSecond,
        }
        // half-float primary sources (usse-form-coverage-form2-dual-flt16): the primaries fmad,
        // ima32, mov, fddp and fssq with the secondaries fmsa, ima32, fmul,
        // fexp and mov, paired as on f32 but for fddp + ima32 (as alone, into
        // i1) and fssq + fmsa (the primary's result)
        let half = half_form(insn.form);
        if half
            && !(matches!(p, "fmad" | "ima32" | "mov" | "fddp" | "fssq")
                && matches!(sop.as_str(), "fmsa" | "ima32" | "fmul" | "fexp" | "mov"))
        {
            return Err(why(format!("dual issue {p} + {sop} on half-float sources (not measured)")));
        }
        let pair = match (p, sop.as_str()) {
            (_, "mov") => Pair::Alone,
            ("fddp", "ima32") if half => Pair::Alone,
            ("fssq", "fmsa") if half => Pair::Result,
            (_, _) if func => Pair::Alone,
            ("mov", _) => Pair::Alone,
            ("ima32", "fmad16") => Pair::Alone,
            ("fmad", "fmad16") => Pair::NoPrimary,
            ("fmad", "fmad" | "fadd" | "fsub" | "fmul" | "fsubflr" | "ima32") => Pair::Alone,
            ("ima32", "fmad" | "fadd" | "fsub" | "fmul" | "fsubflr" | "fmsa") => Pair::Alone,
            ("fadm" | "fmsa" | "fssq", "fadd" | "fsub" | "ima32") => Pair::Alone,
            ("fadm" | "fmsa" | "fssq", "fmul" | "fmad") => Pair::SecondProduct,
            ("fmad" | "fadm" | "fmsa", "fmsa") | ("ima32", "ima32") => Pair::Result,
            ("fminmax", "fmul") => Pair::Alone,
            ("fminmax", "fadd" | "fsub" | "fmad") => Pair::MaxMinusC,
            ("fmad", "fmaxmin") => Pair::MaxMin,
            ("fddp", "fadd" | "fsub" | "fmul" | "fsubflr" | "fmad" | "fmsa" | "fmaxmin" | "ima32") => {
                Pair::FddpSecond
            }
            _ => return Err(why(format!("dual issue {p} + {sop}"))),
        };
        // a register operand without modifiers, whole (on half-float sources,
        // the register whose half it names)
        let whole = |m: &Self, k: usize, v: u32| -> Result<u32, Error> {
            if half {
                Ok(m.half_reg(if k == 0 { v & 0xff } else { v & 0x3ff }, k == 0)?.0)
            } else if k == 0 {
                m.src0(v & 0xff)
            } else {
                m.src(v & 0x3ff, 6)
            }
        };
        // the primary's sources, as values without modifiers and with them
        let plain = |m: &Self, k: usize| -> Result<u32, Error> {
            let v = insn.get(["src0", "src1", "src2"][k]).unwrap();
            let abs = if k == 0 { v >> 8 & 1 } else { v >> 11 & 1 };
            if abs != 0 {
                return Err(why("dual issue with .abs on a primary source"));
            }
            if half && k != 0 && v >> 10 & 1 != 0 {
                return Err(why("a modifier on a half-float source (not measured)"));
            }
            whole(m, k, v)
        };
        let fs = |m: &Self, k: usize| -> Result<u32, Error> { m.fval(insn, ["src0", "src1", "src2"][k]) };
        let primary = match p {
            "mov" => {
                let v = insn.get("src1").unwrap();
                if v >> 10 != 0 {
                    return Err(why("dual issue mov with a modifier"));
                }
                whole(self, 1, v)?
            }
            _ if pair == Pair::NoPrimary => 0,
            "fmad" if pair == Pair::MaxMin => {
                flt::sub(flt::mul(fs(self, 0)?, fs(self, 1)?)?, Ok(fs(self, 2)?))?
            }
            "fmad" => flt::add(flt::mul(fs(self, 0)?, fs(self, 1)?), fs(self, 2)?)?,
            "fadm" => flt::add(flt::mul(fs(self, 0)?, fs(self, 2)?), flt::mul(fs(self, 1)?, fs(self, 2)?)?)?,
            "fmsa" => flt::add(flt::mul(fs(self, 0)?, fs(self, 0)?), flt::mul(fs(self, 1)?, fs(self, 2)?)?)?,
            "fssq" => flt::add(flt::mul(fs(self, 1)?, fs(self, 1)?), flt::mul(fs(self, 2)?, fs(self, 2)?)?)?,
            "fminmax" => flt::min(flt::max(fs(self, 0)?, fs(self, 1)?)?, fs(self, 2)?)?,
            "ima32" => plain(self, 0)?.wrapping_mul(plain(self, 1)?).wrapping_add(plain(self, 2)?),
            "fddp" => exact_mul(fs(self, 0)?, fs(self, 1)?)?,
            _ => return Err(why(format!("dual issue {p} + {sop}"))),
        };
        // fddp's second product, for i0 (and the shared unit's secondaries)
        let second = if p == "fddp" { Some(exact_mul(fs(self, 0)?, fs(self, 2)?)?) } else { None };
        // the secondary's operand k: i<sel>, or the register its field shares
        // with the primary's source k (read without modifiers)
        let shared = |m: &Self, k: usize, reg: u32| -> Result<u32, Error> {
            if insn.get(["src0", "src1", "src2"][k]).is_some() { plain(m, k) } else { whole(m, k, reg) }
        };
        let operand = |m: &Self, k: usize| -> Result<u32, Error> {
            if let Some(i) = insn.form.role(["rm0", "rm1", "rm2"][k]) {
                let w = insn.form.f[i].width() - 1;
                let v = insn.v[i];
                return if v >> w == 0 { m.internal(k) } else { shared(m, k, v & ((1 << w) - 1)) };
            }
            let i = insn.form.role(["r0", "r1", "r2"][k]).unwrap();
            let w = insn.form.f[i].width() - 2;
            let v = insn.v[i];
            match v >> w {
                3 => shared(m, k, v & ((1 << w) - 1)),
                sel => m.internal(sel as usize),
            }
        };
        // the destination of the three-operand secondaries shares source
        // 0's selection (i0 for a register source 0)
        let sel0 = || {
            let i = insn.form.role("r0").unwrap();
            let sel = insn.v[i] >> (insn.form.f[i].width() - 2);
            if sel == 3 { 0 } else { sel }
        };
        let mut bound = None;
        let (sdst, value) = match sop.as_str() {
            _ if pair == Pair::Result => (sel0(), primary),
            _ if pair == Pair::FddpSecond => {
                let d = if matches!(sop.as_str(), "fadd" | "fsub" | "fmul" | "fsubflr") {
                    insn.get("sdst").unwrap()
                } else {
                    sel0()
                };
                if d != 0 && !matches!(sop.as_str(), "fadd" | "fmul") {
                    return Err(why(format!("dual issue fddp + {sop} into i{d} (not measured)")));
                }
                (d, second.unwrap())
            }
            _ if pair == Pair::SecondProduct => {
                let second = match p {
                    "fssq" => flt::mul(fs(self, 2)?, fs(self, 2)?)?,
                    _ => flt::mul(fs(self, 1)?, fs(self, 2)?)?,
                };
                if sop == "fmad" {
                    (sel0(), flt::add(Ok(second), operand(self, 2)?)?)
                } else {
                    (insn.get("sdst").unwrap(), second)
                }
            }
            _ if pair == Pair::MaxMinusC => {
                let v = flt::sub(flt::max(fs(self, 0)?, fs(self, 1)?)?, Ok(fs(self, 2)?))?;
                (if sop == "fmad" { sel0() } else { insn.get("sdst").unwrap() }, v)
            }
            "fmaxmin" => {
                let (a, b, c) = (operand(self, 0)?, operand(self, 1)?, operand(self, 2)?);
                // hardware (usse-float-minmax-fmaxmin-roles): max(min(a, c), b) alone
                (
                    sel0(),
                    if pair == Pair::MaxMin { flt::sub(b, Ok(c))? } else { flt::max(flt::min(a, c)?, b)? },
                )
            }
            "fmad16" => {
                // a * b + c per half lane, as fmad16 alone
                let lanes = |v: u32| -> Result<[half::Exact; 2], Error> {
                    Ok([half::from_half(v as u16)?, half::from_half((v >> 16) as u16)?])
                };
                let (a, b, c) =
                    (lanes(operand(self, 0)?)?, lanes(operand(self, 1)?)?, lanes(operand(self, 2)?)?);
                let (lo, hi) = (half::fma(a[0], b[0], c[0])?, half::fma(a[1], b[1], c[1])?);
                (sel0(), lo as u32 | (hi as u32) << 16)
            }
            "ima32" => {
                // two 16-bit lanes, a * b + c each, wrapping; b is the primary's
                // source 1 next to a float primary
                let a = operand(self, 0)?;
                let b = if p == "mov" { operand(self, 1)? } else { plain(self, 1)? };
                let c = operand(self, 2)?;
                let lane = |k: u32| {
                    (a >> k & 0xffff).wrapping_mul(b >> k & 0xffff).wrapping_add(c >> k & 0xffff) & 0xffff
                };
                (sel0(), lane(0) | lane(16) << 16)
            }
            _ if func => {
                let (v, b) = func::eval(&sop, operand(self, 1)?).map_err(why)?;
                if let Some(b) = b {
                    if !self.near {
                        return Err(why(format!("{sop} is near on the hardware ({b:?}): a near value")));
                    }
                    if self.quad.is_some() {
                        return Err(why(format!("{sop}: a near value in a quad")));
                    }
                }
                bound = Some(b);
                (insn.get("sdst").unwrap(), v)
            }
            "mov" => {
                let k = (0..3).find(|&k| insn.form.role(["rm0", "rm1", "rm2"][k]).is_some()).unwrap();
                (insn.get("sdst").unwrap(), operand(self, k)?)
            }
            "fadd" | "fsub" | "fmul" | "fsubflr" => {
                let (a, b) = (operand(self, 1)?, operand(self, 2)?);
                let v = match sop.as_str() {
                    "fadd" => flt::add(Ok(a), b)?,
                    "fsub" => flt::sub(a, Ok(b))?,
                    "fmul" => flt::mul(a, b)?,
                    _ => flt::sub(a, flt::floor(b))?,
                };
                (insn.get("sdst").unwrap(), v)
            }
            "fmad" | "fmsa" => {
                let (a, b, c) = (operand(self, 0)?, operand(self, 1)?, operand(self, 2)?);
                let v = if sop == "fmad" {
                    flt::add(flt::mul(a, b), c)?
                } else {
                    flt::add(flt::mul(a, a), flt::mul(b, c)?)?
                };
                (sel0(), v)
            }
            s => return Err(why(format!("dual issue secondary {s}"))),
        };
        let sdst = [0, 1, 2, 0][sdst as usize] as usize;
        self.write(insn, primary)?;
        if let Some(b) = bound {
            self.now.out = Out::Fn(b);
        }
        self.set_i(sdst, value)?;
        match second {
            Some(v) => self.set_i(0, v),
            None => Ok(()),
        }
    }

    /// fdsx/fdsy's sources in this instance (the quad combines them), of
    /// one iteration (see Machine::iterations); a predicate that leaves the
    /// instance out and flags stop.
    fn fds_sources(&self, insn: &Insn) -> Result<(u32, u32), Error> {
        if let Some(f) = insn.name("flags", self.core)
            && f.split('.').any(|t| !t.is_empty() && !matches!(t, "skipinv" | "syncs" | "nosched" | "end"))
        {
            return Err(why(format!("fds flags {f}")));
        }
        if !self.pred(insn)? {
            return Err(why("fds with an instance predicated off"));
        }
        Ok((self.fval(insn, "src1")?, self.fval(insn, "src2")?))
    }

    /// One iteration of an instruction: where it jumps, if it does.
    fn op(&mut self, insn: &Insn, bus: &mut dyn Bus) -> Result<Option<usize>, Error> {
        let op = insn.form.op;
        Ok(match op {
            "nop" | "idf" => None,
            "phas" => {
                self.phas(insn)?;
                None
            }
            // what a fill shows of them: nothing; their effect is on the ISP's feedback, the MOE
            // state a context switch keeps, and the sample mask. pcoeff and depthf (E083, on r1-r3
            // only; depthf with nfb, fb and optdwd), setfc (E097, E109), setm (E099); moest
            // leaves its destination and every register (E087's moest-state, selectors 0-15,
            // and moest-dest; E097's moest-store; E109's moest-load, selectors 0-8; E296)
            "pcoeff" | "setfc" | "setm" | "moest" => None,
            "depthf" => {
                if insn.get("twosided") == Some(1) {
                    return Err(why("depthf twosided (not measured)"));
                }
                None
            }
            "atst8" => {
                self.atst8(insn)?;
                None
            }
            "wdf" => {
                let drc = insn.get("drc").unwrap();
                let (land, keep): (Vec<_>, Vec<_>) = self.pending.drain(..).partition(|p| p.0 == drc);
                self.pending = keep;
                for (_, reg, v) in land {
                    match reg {
                        Reg::R(n) => self.set_r(n, v)?,
                        Reg::Pa(n) => self.set_pa(n, v),
                    }
                }
                let (land, keep): (Vec<_>, Vec<_>) = self.pending_unknown.drain(..).partition(|p| p.0 == drc);
                self.pending_unknown = keep;
                for (_, reg, w) in land {
                    match reg {
                        Reg::R(n) => self.unknown.insert(("r", n), w),
                        Reg::Pa(n) => self.unknown.insert(("pa", n), w),
                    };
                }
                None
            }
            "mov_imm" => {
                self.write(insn, insn.get("imm").unwrap())?;
                None
            }
            "mov" => {
                let v = self.src(insn.get("src1").unwrap(), 6)?;
                self.now.out = Out::Move;
                self.mov_dest = true;
                let w = self.write(insn, v);
                self.mov_dest = false;
                w?;
                None
            }
            "fsc" => {
                self.fsc(insn)?;
                None
            }
            "smp" => {
                self.smp(insn, bus)?;
                None
            }
            "br" | "ba" => {
                let t = insn.get("target").unwrap();
                let flags = insn.name("flags", self.core).unwrap_or_default();
                for f in flags.split('.').filter(|f| !f.is_empty()) {
                    match f {
                        "nosched" => {}
                        // the return address, as an instruction index: the
                        // firmware only saves and restores it (not measured)
                        "savelink" => {
                            self.link = (self.pc as u32 + 1 + self.code_index) & PCLINK_MASK;
                            self.link_set = true;
                        }
                        _ => return Err(why(format!("branch flag .{f}"))),
                    }
                }
                Some(if op == "ba" {
                    (t as usize)
                        .checked_sub(self.code_index as usize)
                        .ok_or_else(|| why("a ba to an index before the program in its code base"))?
                } else {
                    let off = ((t << 14) as i32 >> 14) as isize;
                    (self.pc as isize + off) as usize
                })
            }
            "bitwise" => {
                let name = insn.name("op", self.core).unwrap();
                let a = self.src(insn.get("src1").unwrap(), 6)?;
                let mut b = self.src2_or_rot(insn)?;
                if insn.name("inv", self.core).as_deref() == Some("~") {
                    b = !b;
                }
                let v = bitwise(&name, a, b)?;
                self.write(insn, v)?;
                None
            }
            "ima8" => {
                self.ima8(insn)?;
                None
            }
            "ima16" if insn.form.role("fmt").is_some() => {
                self.ima16_formats(insn)?;
                None
            }
            "imae" if insn.form.role("carry").is_some() => {
                self.imae_carry(insn)?;
                None
            }
            "ima32" => {
                self.ima32(insn)?;
                None
            }
            "ima16" => {
                if let Some(t) = insn.name("sign", self.core)
                    && t != "u"
                    && t != "s"
                {
                    return Err(why(format!("{op}.{t}")));
                }
                // hardware (ima16): .neg on source 2 subtracts it, per lane
                let neg = insn.name("neg", self.core).is_some_and(|t| !t.is_empty());
                for r in ["rs", "abs", "neg", "neg1", "neg2"] {
                    if let Some(t) = insn.name(r, self.core)
                        && !t.is_empty()
                        && !(r == "neg" && neg)
                    {
                        return Err(why(format!("{op} modifier {t}")));
                    }
                }
                let a = self.src0(insn.get("src0").unwrap())?;
                let (bv, cv) = (insn.get("src1").unwrap(), insn.get("src2").unwrap());
                let (mut b, mut c) = (self.src(bv, 6)?, self.src(cv, 6)?);
                (b, c) = (lane_imm(bv, b), lane_imm(cv, c));
                if neg {
                    // two's complement per lane
                    c = (0x1_0000 - (c & 0xffff)) & 0xffff | ((0x1_0000 - (c >> 16)) & 0xffff) << 16;
                }
                // Hardware: a multiply-add per 16-bit lane, mod 2^16
                // (0x80000000 * 0xffffffff + 0x5a5a5a5a = 0xda5a5a5a).
                let lane =
                    |s: u32| (a >> s & 0xffff).wrapping_mul(b >> s & 0xffff).wrapping_add(c >> s) & 0xffff;
                self.write(insn, lane(0) | lane(16) << 16)?;
                None
            }
            "imae" => {
                // Hardware (usse-integer-imae-modes): the selected halves multiplied, signed
                // for .s/.ssat, unsigned for .u/.usat; source 2 added at full
                // precision; .rsN shifts that sum right; then it wraps or
                // saturates to 32 bits.
                let sign = insn.name("sign", self.core).unwrap();
                let rs: u32 =
                    insn.name("rs", self.core).unwrap().strip_prefix(".rs").map_or(0, |n| n.parse().unwrap());
                let sat = sign.ends_with("sat");
                if rs != 0 && sat {
                    return Err(why("imae with both .rsN and saturation"));
                }
                let half = |v: u32, h: &str| if h == "high" { v >> 16 } else { v & 0xffff };
                let a = half(self.src0(insn.get("src0").unwrap())?, &insn.name("half0", self.core).unwrap());
                let b =
                    half(self.src(insn.get("src1").unwrap(), 6)?, &insn.name("half1", self.core).unwrap());
                let c = self.src(insn.get("src2").unwrap(), 6)?;
                let v = if sign.starts_with('s') {
                    let sum = (sext16(a) * sext16(b) + c as i32 as i64) >> rs;
                    if sat { sum.clamp(i32::MIN as i64, i32::MAX as i64) as u32 } else { sum as u32 }
                } else {
                    let sum = ((a as u64) * (b as u64) + c as u64) >> rs;
                    if sat { sum.min(u32::MAX as u64) as u32 } else { sum as u32 }
                };
                self.write(insn, v)?;
                None
            }
            "fminmax" => {
                let a = self.fval(insn, "src0")?;
                let b = self.fval(insn, "src1")?;
                let c = self.fval(insn, "src2")?;
                // hardware (usse-float-minmax-fminmax-roles, usse-float-minmax-fmaxmin-roles): fminmax is
                // min(max(a, b), c), fmaxmin max(min(a, c), b); a NaN operand is
                // ignored (usse-float-minmax-fminmax-specials)
                let v = match insn.name("op", self.core).unwrap().as_str() {
                    "fminmax" => flt::min(flt::max(a, b)?, c),
                    _ => flt::max(flt::min(a, c)?, b),
                };
                self.write(insn, v?)?;
                None
            }
            "fmad" | "fsubflr" => {
                let b = self.fval(insn, "src1")?;
                let c = self.fval(insn, "src2")?;
                let v = if op == "fsubflr" {
                    // hardware (usse-float-misc-fadm-fmsa-fsubflr): a - floor(b)
                    flt::sub(b, flt::floor(c))
                } else {
                    let a = self.fval(insn, "src0")?;
                    match insn.name("op", self.core).unwrap().as_str() {
                        // hardware (usse-float-functions-sweep-fmad, usse-fmad-fused): the product rounded,
                        // then the sum, both to nearest even
                        "fmad" => flt::add(flt::mul(a, b), c),
                        // hardware: a * a + b * c, each product rounded
                        "fmsa" => flt::add(flt::mul(a, a), flt::mul(b, c)?),
                        // hardware (usse-float-misc-fadm-fmsa-fsubflr): a * c + b * c, each
                        // product rounded, then the sum
                        "fadm" => flt::add(flt::mul(a, c), flt::mul(b, c)?),
                        o => return Err(why(format!("fmad-group op {o}"))),
                    }
                };
                self.write(insn, v?)?;
                None
            }
            "idiv" => {
                // Hardware: unsigned; the quotient to the destination and the
                // remainder to the next register; by zero both are 0xffffffff.
                let a = self.src(insn.get("src1").unwrap(), 6)?;
                let b = self.src(insn.get("src2").unwrap(), 6)?;
                let (q, r) = a.checked_div(b).zip(a.checked_rem(b)).unwrap_or((u32::MAX, u32::MAX));
                let d = insn.get("dst").unwrap();
                let n = (d & 0x7f) as usize;
                if n + 1 >= 124 {
                    return Err(why("idiv into the last temporaries"));
                }
                let drc = insn.get("drc").unwrap();
                let reg = |k| if d >> 7 != 0 { Reg::Pa(n + k) } else { Reg::R(n + k) };
                self.pending.push((drc, reg(0), q));
                self.pending.push((drc, reg(1), r));
                None
            }
            "test" => {
                self.test(insn)?;
                None
            }
            "lapc" => {
                let flags = insn.name("flags", self.core).unwrap_or_default();
                if !flags.is_empty() && flags != ".nosched" {
                    return Err(why(format!("lapc flags {flags}")));
                }
                self.link_known()?;
                Some(
                    (self.link as usize)
                        .checked_sub(self.code_index as usize)
                        .ok_or_else(|| why("a lapc to an index before the program in its code base"))?,
                )
            }
            "mov_to_link" => {
                let v = insn.get("src").unwrap();
                let x = if self.width(insn, "src") == 7 { self.temp(v as usize)? } else { self.src(v, 6)? };
                // hardware (E475, usse-link-pclink-roundtrip, 19 of 19): pclink holds 18 bits
                self.link = x & PCLINK_MASK;
                self.link_set = true;
                None
            }
            "mov_from_link" => {
                self.link_known()?;
                let link = self.link;
                if self.width(insn, "dst") == 7 {
                    let r = insn.get("dst").unwrap() as usize;
                    if r < 124 { self.set_r(r, link)? } else { self.set_i(r - 124, link)? }
                } else {
                    self.write(insn, link)?;
                }
                None
            }
            "ldr" | "str" => {
                let iv = insn.get("index").unwrap();
                let index = if self.width(insn, "index") == 14 {
                    iv
                } else if bus.register_index_forms() {
                    self.src(iv, 6)?
                } else {
                    return Err(why(format!("{op} with a register index: no run used the form")));
                };
                if op == "str" {
                    let v = self.src(insn.get("src").unwrap(), 6)?;
                    bus.reg_write(index, v)?;
                } else {
                    let v = bus.reg_read(index)?;
                    let d = insn.get("dst").unwrap();
                    let r = (d & 0x7f) as usize;
                    let drc = insn.get("drc").unwrap();
                    self.pending.push((drc, if d >> 7 != 0 { Reg::Pa(r) } else { Reg::R(r) }, v));
                }
                None
            }
            "smlsi" => {
                if ["l0", "l1", "l2"].iter().any(|r| insn.get(r) != Some(0)) {
                    return Err(why("smlsi with non-zero limits"));
                }
                // hardware (usse-moe-swizzle, E097): bit 8 of an operand selects swizzle mode,
                // its byte then four 2-bit register offsets, x first
                let ops = ["inc0", "inc1", "inc2", "inc3"].map(|r| insn.get(r).unwrap());
                let inc = |v: u32| v as u8 as i8 as i32;
                self.moe_inc = Some(ops.map(|v| if v >> 8 != 0 { 1 } else { inc(v) }));
                self.moe_swizzle =
                    ops.map(|v| (v >> 8 != 0).then(|| [0, 2, 4, 6].map(|s| (v >> s & 3) as i32)));
                None
            }
            // hardware (usse-moe-smbo-operands, E087): offsets for the rest of the task
            "smbo" => {
                self.moe_base = ["base0", "base1", "base2", "base3"].map(|r| insn.get(r).unwrap());
                None
            }
            // hardware (usse-moe-window, x-smoa-*, E097, E105): per-operand offsets and address
            // modes, and the modes' ranges, for the rest of the task
            "smoa" => {
                let off = ["off0", "off1", "off2", "off3"].map(|r| (insn.get(r).unwrap() << 22) as i32 >> 22);
                self.moe_addr = (off, ["mode0", "mode1", "mode2", "mode3"].map(|r| insn.get(r).unwrap()));
                None
            }
            "smr" => {
                self.moe_range = ["range0", "range1", "range2", "range3"].map(|r| insn.get(r).unwrap());
                None
            }
            // one instance holds every mutex it takes: no other quad is modelled to wait for it;
            // hardware (r7-faults stage L, E921): a second `lock` of a mutex its holder still
            // holds blocks the holder (the fill hung with no quad's update stored); no caches
            "lock" => {
                let bit = 1u8 << (insn.get("mutex").unwrap() & 7);
                if insn.name("op", self.core).as_deref() == Some("release") {
                    self.locks &= !bit;
                } else if self.locks & bit != 0 {
                    return Err(why(if self.edm_task {
                        "a second lock of a held mutex in an EDM task: it blocks a pixel program's \
                         holder (E921), not measured in an EDM task"
                    } else {
                        "a second lock of a held mutex hangs the job (E921)"
                    }));
                } else {
                    self.locks |= bit;
                }
                None
            }
            "cache" => None,
            // the emits hand the instruction and its sources (0 where it has
            // none) to the unit behind the bus; what that unit does is not
            // the USSE's
            "emitpds" | "emit" => {
                let srcs = [
                    insn.get("src0").map_or(Ok(0), |v| self.src0(v))?,
                    insn.get("src1").map_or(Ok(0), |v| self.src(v, 6))?,
                    insn.get("src2").map_or(Ok(0), |v| self.src(v, 6))?,
                ];
                bus.emit(&insn.text, srcs)?;
                None
            }
            "ld" | "ld.pre" | "ld.post" | "st" | "st.pre" | "st.post" => {
                self.load_store(insn, op, bus)?;
                None
            }
            "eld" => {
                self.eld(insn, bus)?;
                None
            }
            "pack" => {
                self.pack(insn)?;
                None
            }
            "sop2" | "sop2wm" => {
                self.sop2(insn)?;
                None
            }
            "movc" => {
                let (s0, s1, s2) = (
                    self.src0(insn.get("src0").unwrap())?,
                    self.src(insn.get("src1").unwrap(), 6)?,
                    self.src(insn.get("src2").unwrap(), 6)?,
                );
                let ty = insn.name("type", self.core).unwrap_or(".i8".into());
                let test = insn.name("test", self.core).unwrap();
                self.write(insn, movc(&ty, &test, s0, s1, s2)?)?;
                None
            }
            "idot4" | "idot3" | "u16dot3" | "u8dot3a" => {
                self.idot(insn)?;
                None
            }
            "fmad16" => {
                let lanes =
                    |m: &Self, role: &str, mods: &str, src0: bool| -> Result<[half::Exact; 2], Error> {
                        let v = insn.get(role).unwrap();
                        let w = if src0 { m.src0(v & 0xff)? } else { m.src(v, 6)? };
                        // neg[0] | abs[1] | swizzle[3:2]; source 0 has no neg bit
                        let k = insn.get(mods).unwrap() << src0 as u32;
                        let (lo, hi) = (w as u16, (w >> 16) as u16);
                        let modify = |h: u16| {
                            let h = if k & 2 != 0 { h & 0x7fff } else { h };
                            if k & 1 != 0 { h ^ 0x8000 } else { h }
                        };
                        let [a, b] = match k >> 2 & 3 {
                            0 => [lo, hi],
                            1 => [lo, lo],
                            2 => [hi, hi],
                            _ => {
                                // .swzf32: the whole register as a binary32, in both lanes
                                let w = if k & 2 != 0 { w & 0x7fff_ffff } else { w };
                                let x = half::from_f32(if k & 1 != 0 { w ^ 0x8000_0000 } else { w })?;
                                return Ok([x, x]);
                            }
                        };
                        Ok([half::from_half(modify(a))?, half::from_half(modify(b))?])
                    };
                let (a, b, c) = (
                    lanes(self, "src0", "m0", true)?,
                    lanes(self, "src1", "m1", false)?,
                    lanes(self, "src2", "m2", false)?,
                );
                let lo = half::fma(a[0], b[0], c[0])?;
                let hi = half::fma(a[1], b[1], c[1])?;
                self.write(insn, lo as u32 | (hi as u32) << 16)?;
                None
            }
            "fpma" => {
                self.fpma(insn)?;
                None
            }
            "rlp" => {
                // hardware (rlp): d = s << 1 | pN, then pN = bit 31 of s
                // usse-rlp-high-predicates: numbers from 4 up alias p0-p3 (mod 4)
                let n = insn.get("p").unwrap() as usize % 4;
                let s = self.src(insn.get("src1").unwrap(), 6)?;
                self.decide()?;
                if self.p_set >> n & 1 == 0 {
                    return Err(why(format!(
                        "reads p{n} before the program sets it (left over from the job before, E477)"
                    )));
                }
                self.write(insn, s << 1 | self.p[n] as u32)?;
                self.p[n] = s >> 31 != 0;
                None
            }
            "adif" | "adifsum" => {
                // hardware (usse-video-ops-adif): |a - b| per byte; adifsum sums the
                // four and adds a 16-bit half of s0
                let (a, b) =
                    (self.src(insn.get("src1").unwrap(), 6)?, self.src(insn.get("src2").unwrap(), 6)?);
                let d = |k: u32| (a >> (8 * k) & 0xff).abs_diff(b >> (8 * k) & 0xff);
                let v = if op == "adif" {
                    (0..4).fold(0, |w, k| w | d(k) << (8 * k))
                } else {
                    let s0 = self.src0(insn.get("src0").unwrap())?;
                    let half = if insn.name("half", self.core).as_deref() == Some("high") {
                        s0 >> 16
                    } else {
                        s0 & 0xffff
                    };
                    (0..4).map(d).sum::<u32>() + half
                };
                self.write(insn, v)?;
                None
            }
            "bilin" => {
                self.bilin(insn)?;
                None
            }
            "firv" => {
                self.firv(insn)?;
                None
            }
            "firh" => {
                self.firh(insn)?;
                None
            }
            "dual" => {
                self.dual(insn)?;
                None
            }
            // in a uniform fill the other instances hold the same a
            // (usse-gradients-fds-incs: fdsx and fdsy alike give a - b)
            "fds" if self.uniform && self.quad.is_none() => {
                let (a, b) = self.fds_sources(insn)?;
                let v = flt::sub(a, Ok(b))?;
                self.write(insn, v)?;
                None
            }
            "fds" => return Err(why("fdsx/fdsy read the other instances of the quad")),
            "efo" => {
                self.efo(insn)?;
                None
            }
            "movmsk" => {
                self.movmsk(insn)?;
                None
            }
            "sop3" | "lrp" | "sop3c" => {
                self.sop3(insn)?;
                None
            }
            _ => return Err(why(format!("op {op} not modelled yet"))),
        })
    }

    /// The format of a video filter's data bytes: u8, s8 or o8 (*Video*: results are
    /// unsigned bytes whatever the format).
    fn video_format(insn: &Insn) -> Result<u32, Error> {
        match insn.get("fmt").unwrap() {
            f @ 0..=2 => Ok(f),
            f => Err(why(format!("video data format {f}"))),
        }
    }

    /// firv's and firh's first two sources: two numbers in one bank.
    fn video_pair(&self, insn: &Insn) -> Result<(u32, u32), Error> {
        if self.moe_base != [0; 4] || self.moe_addr != ([0; 4], [0; 4]) {
            return Err(why("smbo or smoa offsets on firv/firh's source pair (not measured)"));
        }
        let v = insn.get("pair").unwrap();
        let bank = v >> 14 << 7;
        Ok((self.src(bank | v & 0x7f, 6)?, self.src(bank | v >> 7 & 0x7f, 6)?))
    }

    /// bilin d, w, a, b: hardware (x-video, x-bilin-*, x-c7-bilin-*,
    /// probes/usse/video-filters.toml): with fx = (w.bP & 7) / 8 and fy = (w.bP+1 & 7) / 8 (P 0, or 2 for src23),
    /// v_k = a.bk + fy (b.bk - a.bk), result byte j (0, 1) = v_j + fx (v_n - v_j), n = j + 1
    /// (planar) or j + 2 (interleaved), truncated or (rnd) rounded half up, saturated, in
    /// bytes 0-1 (or 2-3 for dst23) of d, the others zero.
    fn bilin(&mut self, insn: &Insn) -> Result<(), Error> {
        let fmt = Self::video_format(insn)?;
        let w = self.src0(insn.get("src0").unwrap())?;
        let (a, b) = (self.src(insn.get("src1").unwrap(), 6)?, self.src(insn.get("src2").unwrap(), 6)?);
        let sel = insn.get("sel").unwrap();
        let p = if sel & 1 != 0 { 16 } else { 0 };
        let (fx, fy) = ((w >> p & 7) as i64, (w >> (p + 8) & 7) as i64);
        // in eighths, then 64ths
        let v: Vec<i64> = (0..4)
            .map(|k| {
                let (ak, bk) = (video_byte(a, k, fmt), video_byte(b, k, fmt));
                8 * ak + fy * (bk - ak)
            })
            .collect();
        let n = if insn.get("layout") == Some(1) { 2 } else { 1 };
        let half = if insn.get("rnd") == Some(1) { 32 } else { 0 };
        let r = (0..2).fold(0, |r, j| {
            let t = 8 * v[j] + fx * (v[j + n] - v[j]);
            r | sat_u8((t + half) >> 6) << (8 * j)
        });
        self.write(insn, if sel & 2 != 0 { r << 16 } else { r })
    }

    /// firv d, a, b, c: hardware (x-video, x-firv-*, x-amp-*, x-cross-*,
    /// probes/usse/video-filters.toml): result byte k = a.bk * c.b0 + b.bk * c.b1, the taps signed bytes; +src2.2 adds
    /// c.b2 (signed: usse-video-filters-amp-l40-firv-src2 case 40), latch adds byte k of the firh latch, scale
    /// shifts right by c.b3; saturated. latch and scale together: their order is not
    /// measured.
    fn firv(&mut self, insn: &Insn) -> Result<(), Error> {
        let fmt = Self::video_format(insn)?;
        let (a, b) = self.video_pair(insn)?;
        let c = self.src(insn.get("src2").unwrap(), 6)?;
        let fl = insn.get("firv").unwrap();
        let (src2, latch, scale) = (fl & 1 != 0, fl & 2 != 0, fl & 4 != 0);
        let tap = |n: u32| (c >> (8 * n)) as u8 as i8 as i64;
        let shift = c >> 24;
        if latch {
            self.now.unknown = self.latch_unknown(insn);
            if scale && shift != 0 && self.firh_latch.iter().any(|&l| l.is_some_and(|l| l != 0)) {
                self.now.unknown = Some("firv's latch with scale, whose order is not measured");
            }
        }
        let r = (0..4).fold(0, |r, k| {
            let mut s = video_byte(a, k, fmt) * tap(0) + video_byte(b, k, fmt) * tap(1);
            if src2 {
                s += tap(2);
            }
            if latch {
                s += self.firh_latch[k as usize].unwrap_or(0) as i64;
            }
            if scale {
                s >>= shift.min(63);
            }
            r | sat_u8(s) << (8 * k)
        });
        if insn.get("write") == Some(0) {
            return Ok(()); // "!": no destination
        }
        self.write(insn, r)
    }

    /// atst8 d, pN, a, b, c, mode: hardware (E083, usse-alpha-test, 687 fill cases): alpha
    /// a.b3 against the reference c.b3 by the function in c bits 15:13 (never, less, equal,
    /// lequal, greater, notequal, gequal, always); a pass writes a to d and sets pN, a fail
    /// leaves d and clears pN. b, c's other bits, twosided and the feedback mode change nothing
    /// a fill shows; "!pN" (enc[38] clear) is not measured.
    fn atst8(&mut self, insn: &Insn) -> Result<(), Error> {
        if insn.get("pwrite") == Some(0) {
            return Err(why("atst8 with !pN (not measured)"));
        }
        let a = self.src0(insn.get("src0").unwrap())?;
        let c = self.src(insn.get("src2").unwrap(), 6)?;
        let (alpha, reference) = (a >> 24, c >> 24);
        let pass = match c >> 13 & 7 {
            0 => false,
            1 => alpha < reference,
            2 => alpha == reference,
            3 => alpha <= reference,
            4 => alpha > reference,
            5 => alpha != reference,
            6 => alpha >= reference,
            _ => true,
        };
        if self.now.read.get().is_some() {
            return Err(why("atst8 of a near value"));
        }
        if pass {
            self.now.out = Out::Move;
            self.write(insn, a)?;
        }
        self.p[insn.get("p").unwrap() as usize] = pass;
        self.p_set |= 1 << insn.get("p").unwrap();
        Ok(())
    }

    /// Why the firh latch, as this instruction reads it, is not known (None if it is).
    fn latch_unknown(&self, insn: &Insn) -> Option<&'static str> {
        if (0..4).any(|j| self.firh_written[j] && self.firh_latch[j].is_none()) {
            Some("a byte of the firh latch the task wrote but the run could not compute")
        } else if self.firh_latch.contains(&None) {
            Some("bytes of the firh latch the task did not write")
        } else if insn.firh_later {
            Some("the firh latch, which a later firh may reach first")
        } else if !self.uniform {
            Some("the firh latch, which the instances of a slot share")
        } else {
            None
        }
    }

    /// firh d, a, b, c, fmt, edge, fcsN, #s, #k: hardware (x-firh-*, x-c7..x-c11,
    /// probes/usse/video-filters.toml, E078, E079): along the line a.b0-a.b3, b.b0-b.b3, c.b0-c.b3, set N's
    /// kernel centred on position s, positions off the line by the edge mode (rep repeats
    /// the end sample, msc mirrors without it, mdc with it); sat((sum + bias) >> shift) is
    /// byte k of the firh latch, and d the whole latch.
    fn firh(&mut self, insn: &Insn) -> Result<(), Error> {
        let fmt = Self::video_format(insn)?;
        let (a, b) = self.video_pair(insn)?;
        let c = self.src(insn.get("src2").unwrap(), 6)?;
        let sel = insn.get("firh").unwrap();
        let (edge, set) = (sel & 3, sel >> 2);
        let s = (insn.get("s").unwrap() as i32) << 27 >> 27;
        let k = insn.get("k").unwrap() as usize;
        if edge == 3 {
            return Err(why("firh edge mode 3"));
        }
        // the centre field's values 16-27 (written #-16 to #-5) are centres 16 to 27, past the
        // line (usse-video-filters-c9-*, c10-*): -4 to 27
        let s = if s < -4 { s + 32 } else { s };
        let line: Vec<i64> =
            [a, b, c].iter().flat_map(|&x| (0..4).map(move |j| video_byte(x, j, fmt))).collect();
        // a position off the line by the edge mode, to 18; from 19 every mode reads 0
        // (c9-*, c10-*, usse-filter-edges)
        let at = |i: i32| -> Option<i64> {
            let i = match (edge, i) {
                (_, 0..=11) => i,
                (_, 19..) => return Some(0),
                (0, ..0) => 0,
                (0, _) => 11,
                (1, ..0) => -i,
                (1, _) => 22 - i,
                (_, ..0) => -1 - i,
                (_, _) => 23 - i,
            };
            Some(line[i as usize])
        };
        let byte = match self.coeffs {
            None => Err(
                "firh's result, from the job's coefficients (CR_USE_COEFFS_MODE, load), unknown to the run",
            ),
            Some(c) => firh_byte(c, set, s, &at),
        };
        self.firh_latch[k] = byte.ok();
        self.firh_written[k] = true;
        if byte.is_ok() && matches!(self.coeffs.map(|c| c.mode & 3), Some(1 | 2)) && (2..=5).contains(&set) {
            self.fitted = true;
        }
        // bytes of the latch the task did not write hold what the slot's last task left: any
        // value, the rest exact (Bound::Mask); a byte it wrote but the run could not compute,
        // a later firh or other instances are not known
        let gap = (0..4).filter(|&j| !self.firh_written[j]).fold(0, |m, j| m | 0xff << (8 * j));
        let lost = (0..4).any(|j| self.firh_written[j] && self.firh_latch[j].is_none());
        let other = if lost {
            Some("a byte of the firh latch the task wrote but the run could not compute")
        } else if insn.firh_later || !self.uniform {
            self.latch_unknown(insn)
        } else {
            None
        };
        self.now.unknown = byte.err().or(other);
        if self.now.unknown.is_none() && gap != 0 {
            self.now.out = Out::Fn(Some(Bound::Mask(gap)));
        }
        let d = (0..4).fold(0, |d, j| d | (self.firh_latch[j].unwrap_or(0) as u32) << (8 * j));
        self.write(insn, d)
    }

    /// The test group: an ALU operation whose result (unless the destination is
    /// "!") is written and tested into p<n>.
    /// frcp, frsq, flog, fexp, fsqrt, fsin, fcos (see func): the source with
    /// its .neg and .abs; half-float and c10 sources are not measured.
    fn fsc(&mut self, insn: &Insn) -> Result<(), Error> {
        let name = insn.name("op", self.core).unwrap();
        let mods = insn.get("mods").unwrap();
        if mods >> 2 & 3 != 0 {
            return Err(why(format!(
                "{name} of a {} source",
                if mods >> 2 & 3 == 1 { "half" } else { "c10" }
            )));
        }
        let x = flt::modify(self.src(insn.get("src1").unwrap(), 6)?, mods & 1 != 0, mods >> 1 & 1 != 0);
        let (v, b) = func::eval(&name, x).map_err(why)?;
        if let Some(b) = b {
            if !self.near {
                return Err(why(format!("{name} is near on the hardware ({b:?}): a near value")));
            }
            if self.quad.is_some() {
                return Err(why(format!("{name}: a near value in a quad")));
            }
        }
        self.now.out = Out::Fn(b);
        self.write(insn, v)
    }

    /// smp1d/smp2d d, c, s, drcN (see tex): the state words in temporaries s
    /// to s + 3, the coordinates in c and c + 1 (.flt16: the halves of c, u
    /// low); the texels land in d, d + 1, ... at a wdf on drcN, as loads do.
    /// The LOD (tex::Lod, E041): replace's f32 value in src2, grad's four
    /// gradients from src2 on; without one (or with a bias) a uniform task's
    /// instances share the coordinates, so the derivatives are zero
    /// (texture-mipmaps-mip-bias: level 0 whatever the bias), while a quad's own
    /// derivatives are not modelled. Hardware (texture-sampler-smp-point, texture-sampler-smp-lod): a LOD
    /// operand of 0 samples as the plain forms.
    fn smp(&mut self, insn: &Insn, bus: &mut dyn Bus) -> Result<(), Error> {
        let dim = insn.name("dim", self.core).unwrap();
        let (d, lod) = dim.split_at(2);
        // smp3d (the form without a LOD operand) is read as smp2d where it ran and nowhere else
        // (tex::smp3d_as_2d, checked once the state words are read); with a LOD operand it did
        // not assemble in p1132
        let three_d = d == "3d";
        if three_d && !lod.is_empty() {
            return Err(why("smp3d with a LOD operand"));
        }
        let d = if three_d { "2d" } else { d };
        let f32_coords = insn.name("fmt", self.core).unwrap().is_empty();
        let implicit = match (self.quad.is_some(), self.uniform) {
            (true, _) => tex::Lod::Open("a LOD from the quad's derivatives"),
            (false, true) => tex::Lod::Flat,
            (false, false) => tex::Lod::Open("a LOD from the other instances' coordinates"),
        };
        let lod = match lod {
            "" | "bias" => {
                if !lod.is_empty() {
                    self.src(insn.get("src2").unwrap(), 6)?;
                }
                implicit
            }
            _ => {
                let s2 = insn.get("src2").unwrap();
                let l = self.src(s2, 6)?;
                if l == 0 && lod == "replace" {
                    tex::Lod::Value(0.0)
                } else if !f32_coords || !matches!(s2 >> 7, 0..=3) {
                    tex::Lod::Open("a LOD operand not in f32 registers")
                } else if lod == "replace" {
                    tex::Lod::Value(f32::from_bits(l))
                } else if lod == "grad" && d == "2d" && s2 & 0x7f <= 0x7f - 3 {
                    // texture-sampler-smp-point case 11 sets r26 = 0 alone and samples as
                    // smp2d (a stride texture); other gradients the program
                    // has not written matter only where the LOD does
                    let g: Result<Vec<u32>, Error> = (0..4).map(|k| self.src(s2 + k, 6)).collect();
                    match g {
                        Ok(g) => tex::Lod::Grad([0, 1, 2, 3].map(|k| f32::from_bits(g[k]))),
                        Err(_) if l == 0 => tex::Lod::Value(0.0),
                        Err(_) => tex::Lod::Open("gradients the program has not written"),
                    }
                } else {
                    tex::Lod::Open("a LOD form not modelled")
                }
            }
        };
        let c = insn.get("src0").unwrap();
        let (u, v) = match insn.name("fmt", self.core).unwrap().as_str() {
            "" => {
                if c & 0x7f == 0x7f && d == "2d" {
                    return Err(why("coordinates past the bank"));
                }
                (self.src0(c)?, if d == "1d" { 0 } else { self.src0(c + 1)? })
            }
            ".flt16" => {
                let w = self.src0(c)?;
                (half_f32(w & 0xffff)?, half_f32(w >> 16)?)
            }
            f => return Err(why(format!("smp with {f} coordinates"))),
        };
        // .pcf's reference: the f32 after the coordinates (.pcff16: a half,
        // the low one)
        let flags = insn.name("flags", self.core).unwrap_or_default();
        let pcf = if flags.contains(".pcf") {
            let fmt = insn.name("fmt", self.core).unwrap();
            if d != "2d" || !fmt.is_empty() || c & 0x7f > 0x7d {
                return Err(why(format!("smp{d}{fmt} with .pcf")));
            }
            let r = self.src0(c + 2)?;
            let r = if flags.contains(".pcff16") { half_f32(r & 0xffff)? } else { r };
            if !f32::from_bits(r).is_finite() {
                return Err(why("an infinite or NaN .pcf reference"));
            }
            Some(f32::from_bits(r))
        } else {
            None
        };
        let st = insn.get("src1").unwrap();
        if st >> 7 != 0 {
            return Err(why("texture state outside the temporaries"));
        }
        let mut state = [0; 4];
        for (k, w) in state.iter_mut().enumerate() {
            *w = self.temp((st & 0x7f) as usize + k)?;
        }
        if self.now.read.get().is_some() {
            return Err(why("a sample from a near value"));
        }
        if three_d {
            tex::smp3d_as_2d(state, pcf.is_some() || flags.contains(".sinf") || flags.contains(".rsd"))
                .map_err(why)?;
        }
        if matches!(state[1] >> 24 & 31, 28 | 29) && !self.csc_unloaded {
            return Err(why("YUV through a colour-space set the vector does not record"));
        }
        let (u, v) = (f32::from_bits(u), f32::from_bits(v));
        if !u.is_finite() || !v.is_finite() {
            return Err(why("smp at an infinite or NaN coordinate"));
        }
        // the SRD modes (E042): the sampling decision or the not filtered texels
        let srd = if flags.contains(".sinf") {
            tex::Srd::Info
        } else if flags.contains(".rsd") {
            tex::Srd::Raw
        } else {
            tex::Srd::None
        };
        let texels = bus.sample(&tex::Sample { state, u, v, one_d: d == "1d", srd, pcf, lod })?;
        let (dst, drc) = (insn.get("dst").unwrap(), insn.get("drc").unwrap());
        let reg = |r: usize| if dst >> 7 != 0 { Reg::Pa(r) } else { Reg::R(r) };
        let n = texels.len();
        for (k, t) in texels.into_iter().enumerate() {
            let r = (dst & 0x7f) as usize + k;
            if r >= 124 {
                return Err(why("a sample past the temporaries"));
            }
            self.pending.push((drc, reg(r), t));
        }
        // the registers the hardware writes after the modelled ones, with no model (E723)
        if let Some(w) = tex::unknown_after(state) {
            let r = (dst & 0x7f) as usize + n;
            if r < 124 {
                self.pending_unknown.push((drc, reg(r), w));
            }
        }
        Ok(())
    }

    /// ima8 d, a, b, c, x, y, z, xa, ya, za: x + y * z per byte, the colour
    /// selectors for bytes 0-2 and the alpha ones for byte 3 (s0-s2 = a-c, sNa
    /// the alpha byte, .comp 255 - the byte), wrapping, or clamped to 255 with
    /// .sat. Hardware (ima8).
    fn ima8(&mut self, insn: &Insn) -> Result<(), Error> {
        let (d, dc10) = Self::colour_operand(insn.get("dst").unwrap(), true)?;
        let (r0, c0) = Self::colour_operand0(insn.get("src0").unwrap())?;
        let (r1, c1) = Self::colour_operand(insn.get("src1").unwrap(), false)?;
        let (r2, c2) = Self::colour_operand(insn.get("src2").unwrap(), false)?;
        if dc10 || c0 || c1 || c2 {
            return Err(why("ima8 with c10 operands"));
        }
        let s = [self.src0(r0)?, self.src(r1, 6)?, self.src(r2, 6)?];
        let sat = insn.name("sat", self.core).is_some_and(|t| !t.is_empty());
        let sel = insn.name("sel", self.core).unwrap();
        let sel: Vec<&str> = sel.split(", ").collect();
        let byte = |name: &str, k: u32| -> u32 {
            let (name, comp) = name.strip_suffix(".comp").map_or((name, false), |n| (n, true));
            let src = (name.as_bytes()[1] - b'0') as usize;
            let k = if name.ends_with('a') { 3 } else { k };
            let b = s[src] >> (8 * k) & 0xff;
            if comp { 255 - b } else { b }
        };
        let mut v = 0;
        for k in 0..4 {
            let t = if k < 3 { &sel[0..3] } else { &sel[3..6] };
            let r = byte(t[0], k) + byte(t[1], k) * byte(t[2], k);
            v |= (if sat { r.min(255) } else { r & 0xff }) << (8 * k);
        }
        self.write_dst(d, v)
    }

    /// ima16 with its source formats (fmt: source 1's [1:0], source 2's
    /// [3:2]: u16, u8, s8, o8): a * b + c per 16-bit lane, wrapping; an 8-bit
    /// source is the byte .low or .high of that lane's half, u8 unsigned, s8
    /// signed, o8 the byte - 128. Hardware (ima16, usse-integer-ima16-8bit).
    fn ima16_formats(&mut self, insn: &Insn) -> Result<(), Error> {
        for r in ["rs", "abs"] {
            if let Some(t) = insn.name(r, self.core)
                && !t.is_empty()
            {
                return Err(why(format!("ima16 modifier {t}")));
            }
        }
        if let Some(t) = insn.name("sign", self.core)
            && t != "u"
            && t != "s"
        {
            return Err(why(format!("ima16.{t}")));
        }
        let fmt = insn.get("fmt").unwrap();
        let a = self.src0(insn.get("src0").unwrap())?;
        // (operand, .high, format)
        let (bv, bh) = match insn.get("src1") {
            Some(v) => (v, false),
            None => {
                let v = insn.get("src1x").unwrap();
                (v & 0x3ff, v >> 10 & 1 != 0)
            }
        };
        let cx = insn.get("src2x").unwrap();
        let (cv, neg, ch) = (cx & 0x3ff, cx >> 10 & 1 != 0, fmt >> 2 != 0 && cx >> 11 & 1 != 0);
        let mut ops = [(bv, bh, fmt & 3), (cv, ch, fmt >> 2 & 3)].map(|(v, h, f)| (v, h, f, 0u32));
        for o in ops.iter_mut() {
            if o.2 != 0 && o.0 >> 7 == 6 {
                return Err(why("ima16 with an 8-bit immediate"));
            }
            o.3 = lane_imm(o.0, self.src(o.0, 6)?);
        }
        let lane = |(_, high, f, x): (u32, bool, u32, u32), k: u32| -> i64 {
            let h = x >> (16 * k) & 0xffff;
            let b = if high { h >> 8 } else { h & 0xff };
            match f {
                0 => h as i64,
                1 => b as i64,
                2 => b as u8 as i8 as i64,
                _ => b as i64 - 128,
            }
        };
        let mut v = 0;
        for k in 0..2 {
            let (b, c) = (lane(ops[0], k), lane(ops[1], k));
            let r = (a >> (16 * k) & 0xffff) as i64 * b + if neg { -c } else { c };
            v |= (r as u32 & 0xffff) << (16 * k);
        }
        self.write(insn, v)
    }

    /// pclink as the task wrote it: it is hardware state, not reset between jobs, so a read of it
    /// before any write is what an earlier job left, for most instances (E475, E500).
    fn link_known(&self) -> Result<(), Error> {
        if self.link_set {
            Ok(())
        } else {
            Err(why("reads pclink before the program writes it (left over from the job before, E475)"))
        }
    }

    /// phas #next, #temps, rate, wait, mode (the form with immediates). Hardware: `end` closes
    /// the program (the usual first and last instruction of a one-phase program, no effect here);
    /// `none` makes the instruction index `next` the start of a second phase that runs at once
    /// when the first ends (`.end`), with `temps` temporaries (E487, E519). Not run in a fill, so
    /// refused: the rates `selective` and `sample` and the mode `perinstance` with a next phase, the
    /// register form, and a phas that names a phase while one is named. The wait `vcull` hangs a pixel
    /// task (refused); in a vertex task (`vertex_task`) it names no phase here, the program stopping
    /// where its first phase ends. `pt` is refused.
    fn phas(&mut self, insn: &Insn) -> Result<(), Error> {
        let text = insn.text.as_str();
        let args: Vec<&str> = text.split_once(' ').map_or(vec![], |(_, a)| a.split(", ").collect());
        let num = |s: &str| s.strip_prefix('#').and_then(|n| n.trim().parse::<usize>().ok());
        let [next, request, rate, wait, mode] = args[..] else {
            return Err(why("phas with registers (not measured)"));
        };
        let (Some(next), Some(request)) = (num(next), num(request)) else {
            return Err(why("phas with registers (not measured)"));
        };
        match wait {
            "end" => Ok(()),
            "none" if rate != "pixel" || mode != "parallel" => {
                Err(why(format!("phas {rate}, {mode} with a next phase (not measured)")))
            }
            "none" if self.phase.is_none() => {
                self.phase = Some((next, request));
                Ok(())
            }
            // hardware: vcull hangs a pixel task (usse-phases-phas-pix-vcull-*, 4 jobs, E121) and pt
            // hangs a vertex task (usse-phases-phas-vtx-pt-parallel); in a pixel task the pt phase
            // never writes its pixels. In a vertex task vcull starts its phase once the MTE has
            // culled, which is not modelled: the program stops where its first phase ends
            "vcull" if self.vertex_task => Ok(()),
            "vcull" => Err(why("phas wait vcull in a pixel task hangs the job (E121)")),
            "pt" => Err(why("phas wait pt hangs a vertex task and never writes a pixel task's pixels")),
            "none" => Err(why("a phas that names a phase while one is named (not measured)")),
            _ => Ok(()),
        }
    }

    /// ima32: the low 32 bits of a * b + c, on full 32-bit operands (E469, 826 of 826). Hardware:
    /// `.neg` on source 2 or 3 negates it in two's complement, `.u` and `.s` alike (E470, E495);
    /// `cie, iN` adds bit 0 of iN (E494, 24 of 24, with E470); the extra operand `iK` (enc[38],
    /// enc[37:36]) receives the high 32 bits of the product with the addend (E493, 15 of 15;
    /// E501, 75 of 75; `.s`: E526). Not run, so refused: the extra operand with `cie`, with a
    /// negated source, with an immediate or a constant other than c56 (the subtract of E501) in
    /// a source, with a source or a destination that is not an r-bank temporary or an iK that is
    /// also a source, with K = 3 (an i3 reads another instance), and a negated source with `cie`.
    fn ima32(&mut self, insn: &Insn) -> Result<(), Error> {
        let sign = insn.name("sign", self.core).unwrap();
        if sign != "u" && sign != "s" {
            return Err(why(format!("ima32.{sign}")));
        }
        for r in ["rs", "abs", "neg"] {
            if insn.name(r, self.core).is_some_and(|t| !t.is_empty()) {
                return Err(why(format!("ima32 modifier {r}")));
            }
        }
        // the source operands, with their negation bits: the plain form carries them as neg1
        // and neg2 (enc[40], enc[39]), the form with the carry and the extra operand in the
        // operands' bit 10
        let (bv, cv, nb, nc, cie, x) = if insn.form.role("cie").is_some() {
            let (b, c) = (insn.get("src1x").unwrap(), insn.get("src2x").unwrap());
            (
                b & 0x3ff,
                c & 0x3ff,
                b >> 10 & 1 != 0,
                c >> 10 & 1 != 0,
                insn.get("cie").unwrap(),
                insn.get("x").unwrap(),
            )
        } else {
            let neg = |r: &str| insn.name(r, self.core).is_some_and(|t| !t.is_empty());
            (insn.get("src1").unwrap(), insn.get("src2").unwrap(), neg("neg1"), neg("neg2"), 0, 0)
        };
        // a negated register of the r bank ran in every combination (E470, 90 of 90); a negated
        // immediate or constant only in the ones E470 and E495 ran: .s with #1 and #5, c3 and c56
        // in source 2 and #1, #127 and c56 in source 3; .u with #5, #127 and c56 in source 2 and
        // #1, #127 and c56 in source 3
        let ran = |neg: bool, v: u32, third: bool| {
            !neg || v >> 7 == 0 && (v & 0x7f) < 124 || {
                let (imm, c) = (v >> 7 == 6, v >> 7 == 5);
                let n = v & 0x7f;
                match (sign.as_str(), third) {
                    ("s", false) => imm && matches!(n, 1 | 5) || c && matches!(n, 3 | 56),
                    ("s", true) => imm && matches!(n, 1 | 127) || c && n == 56,
                    (_, false) => imm && matches!(n, 5 | 127) || c && n == 56,
                    (_, true) => imm && matches!(n, 1 | 127) || c && n == 56,
                }
            }
        };
        if !ran(nb, bv, false) || !ran(nc, cv, true) {
            return Err(why("ima32 negating an operand that was not run (E470, E495)"));
        }
        let av = insn.get("src0").unwrap();
        let (extra, k) = (x & 1 != 0, (x >> 1) as usize);
        if extra {
            let d = insn.get("dst").unwrap();
            let temp = |v: u32| v >> 7 == 0 && (v & 0x7f) < 124;
            // c56 is the constant bank's number 56 (bank 5)
            let reg_or_c56 = |v: u32| temp(v) || v == 5 << 7 | 56;
            let why_not = if cie != 0 {
                Some("ima32 with the extra operand and cie")
            } else if nb || nc {
                Some("ima32 with the extra operand and a negated source")
            } else if k == 3 {
                Some("ima32 with the extra operand i3")
            } else if !temp(av) || !temp(cv) || !reg_or_c56(bv) || !temp(d) {
                Some("ima32 with the extra operand on a source or destination other than the r bank or c56")
            } else {
                None
            };
            if let Some(w) = why_not {
                return Err(why(format!("{w} (not measured)")));
            }
        } else if (nb || nc) && cie != 0 {
            return Err(why("ima32 with a negated source and cie (not measured)"));
        }
        let a = self.src0(av)?;
        let (mut b, mut c) = (self.src(bv, 6)?, self.src(cv, 6)?);
        if nb {
            b = b.wrapping_neg();
        }
        if nc {
            c = c.wrapping_neg();
        }
        let cin = if cie == 0 { 0 } else { self.internal(cie as usize - 1)? & 1 };
        let p = (a as u64) * (b as u64) + c as u64 + cin as u64;
        // hardware (E526, usse-ima32hi-signed, 282 of 282): .s gives bits 63:32 of the signed 64-bit
        // sext(a) * sext(b) + sext(c); the low word is the same as .u's
        let hi = if sign == "s" {
            ((a as i32 as i64 * b as i32 as i64 + c as i32 as i64) >> 32) as u32
        } else {
            (p >> 32) as u32
        };
        self.write(insn, p as u32)?;
        if extra {
            self.set_i(k, hi)?;
        }
        Ok(())
    }

    /// imae with its source-2 type and carries (carry: type [1:0] z16, u16,
    /// u32 | coe | cie | register): the selected halves multiplied, source 2
    /// added (a u16 half sign-extended, z16 zero-extended), cie adding iN,
    /// .rsN shifting, saturating or wrapping as plain imae; coe writes the
    /// carry out to iN. Hardware (usse-integer-imae-modes).
    /// The carries (E471, E494): cie adds bit 0 of iN, coe writes the carry of the 32-bit add
    /// (0 or 1; a signed product taken as the number it wraps to), and both name one iN.
    fn imae_carry(&mut self, insn: &Insn) -> Result<(), Error> {
        let sign = insn.name("sign", self.core).unwrap();
        let rs: u32 =
            insn.name("rs", self.core).unwrap().strip_prefix(".rs").map_or(0, |n| n.parse().unwrap());
        let sat = sign.ends_with("sat");
        if rs != 0 && sat {
            return Err(why("imae with both .rsN and saturation"));
        }
        let half = |v: u32, high: bool| if high { v >> 16 } else { v & 0xffff };
        let (x0, x1) = (insn.get("src0x").unwrap(), insn.get("src1x").unwrap());
        let a = half(self.src0(x0 & 0xff)?, x0 >> 8 & 1 != 0);
        let b = half(self.src(x1 & 0x3ff, 6)?, x1 >> 10 & 1 != 0);
        let carry = insn.get("carry").unwrap();
        let c: i64 = match insn.get("src2") {
            Some(v) => self.src(v, 6)? as i64,
            None => {
                let x = insn.get("src2x").unwrap();
                let h = half(self.src(x & 0x3ff, 6)?, x >> 10 & 1 != 0);
                if carry & 3 == 0 { h as i64 } else { sext16(h) }
            }
        };
        let reg = (carry >> 4 & 1) as usize;
        let (coe, cie) = (carry & 4 != 0, carry & 8 != 0);
        // hardware (E471, usse-imae-neg-coe-cie, 14 of 14): coe and cie together name one iN (the
        // assembler takes no two): the sum includes bit 0 of the iN read and its carry goes back
        // hardware (E471, E494): the carry in is bit 0 of iN
        let cin = if cie { (self.internal(reg)? & 1) as i64 } else { 0 };
        let signed = sign.starts_with('s');
        let c = if signed && insn.get("src2").is_some() { c as u32 as i32 as i64 } else { c };
        let prod = if signed { sext16(a) * sext16(b) } else { a as i64 * b as i64 };
        let sum = prod + c + cin;
        let v = sum >> rs;
        let v = match (sat, signed) {
            (true, true) => v.clamp(i32::MIN as i64, i32::MAX as i64) as u32,
            (true, false) => v.clamp(0, u32::MAX as i64) as u32,
            _ => v as u32,
        };
        self.write(insn, v)?;
        if coe {
            // hardware (E471, E494; usse-imae-neg-coe-signed, 6 of 6 for .s): the carry out of the
            // 32-bit add, 0 or 1, the signed product taken as the 32-bit number it wraps to
            // and c as an unsigned one
            let carry = if signed {
                ((prod as u32 as u64) + (c as u32 as u64) + cin as u64) >> 32
            } else {
                (sum >> 32) as u64
            };
            self.set_i(reg, carry as u32)?;
        }
        Ok(())
    }

    /// The test group: class 9 tests into predicate p, class 15 (a test
    /// ending .bmsk, .wmsk or .dmsk) into a mask its destination gets.
    /// Hardware (usse-form-coverage-form2-test-mask): a .bmsk byte k is 0xff where
    /// channel k tests true, a .wmsk half k where channel 2k does, .dmsk all
    /// ones where chan0 does. enc[50] set (usse-form-coverage-form2-test-e50, forms 198-203 and
    /// 207-212): .sat on the 8-bit operations, the others as with it clear;
    /// only the operations its probes ran are taken.
    fn test(&mut self, insn: &Insn) -> Result<(), Error> {
        let name = insn.name("op", self.core).unwrap();
        let test = insn.name("test", self.core).unwrap();
        let e50 = insn.form.val >> 50 & 1 != 0;
        let sat = insn.form.pat.is_some_and(|p| p.contains(".sat."));
        if e50 {
            // measured with enc[50]
            const E50: [&str; 10] =
                ["iadd32", "isub16", "iadd16", "imul16", "fadd", "fmul", "fmax", "fmin", "frcp", "fpadd8"];
            if !(E50.contains(&name.as_str()) || sat && matches!(name.as_str(), "uadd8" | "iadd8" | "umul8"))
            {
                let s = if sat { ".sat" } else { "" };
                return Err(why(format!("test {name}{s} with enc[50] (not measured)")));
            }
            // a format bit (.flt16, .c10) or an i register past r59: not measured
            for r in ["dst", "src1", "src2"] {
                if let Some(v) = insn.get(r)
                    && (v & 0x7f) >= 60
                    && !(r != "dst" && matches!(v >> 7 & 7, 5 | 6))
                {
                    return Err(why(format!("test with enc[50]: {r} numbered {} (not measured)", v & 0x7f)));
                }
            }
        } else if matches!(name.as_str(), "fmax" | "fmin") {
            return Err(why(format!("test {name} with enc[50] clear (not measured)")));
        }
        let av = insn.get("src1").unwrap();
        let (value, tested) = match insn.get("src2") {
            None => {
                let (v, t) = self.test_fn(&name, &test, av)?;
                (Some(v), t)
            }
            Some(bv) => {
                let (mut a, mut b) = (self.src(av, 6)?, self.src(bv, 6)?);
                if name.ends_with("16") {
                    (a, b) = (lane_imm(av, a), lane_imm(bv, b));
                }
                if name.ends_with('8') && (av >> 7 == 6 || bv >> 7 == 6) {
                    return Err(why(format!("{name} with an immediate (its lanes not measured)")));
                }
                self.decide()?;
                // only the zero tests of usub16 (usse-decoder-vectors-usub16-taz) and of the
                // unsigned byte operations (usse-lane-integer-rogue-int) are measured
                if matches!(name.as_str(), "usub16" | "uadd8" | "usub8" | "umul8" | "fpsub8" | "fpmul8")
                    && !test.starts_with("testt")
                {
                    return Err(why(format!("{name} sign test {test}")));
                }
                if sat {
                    // the test sees each byte's result, which a saturation
                    // keeps the sign and zero of; uadd8.sat and umul8.sat
                    // write the bytes clamped to 255 (usse-form-coverage-form2-test-e50 3,
                    // usse-lane-integer-rogue-int 1, 3), iadd8.sat the wrapped bytes
                    // (usse-lane-integer-rogue-int 6)
                    let (w, t) = alu_test_value(&name, a, b)?;
                    let v = if name == "iadd8" { w } else { sat_bytes(&t) };
                    (Some(v), t)
                } else {
                    let (v, t) = alu_test_value(&name, a, b)?;
                    (Some(v), t)
                }
            }
        };
        // hardware (E529): the join `o` ran on and, or and xor; E1062 on rol, shl, shr, asr, iadd32,
        // iaddu32, and on iadd8 and iadd16 with every chan field (not on the other operations)
        if test.strip_prefix("test").and_then(|t| t.chars().nth(1)) == Some('o')
            && !test.contains("all")
            && !test.contains("02")
            && !matches!(
                name.as_str(),
                "and"
                    | "or"
                    | "xor"
                    | "rol"
                    | "shl"
                    | "shr"
                    | "asr"
                    | "iadd32"
                    | "iaddu32"
                    | "iadd8"
                    | "iadd16"
            )
        {
            return Err(why(format!("test {name} with the join o (not run, E529, E1062)")));
        }
        let write = insn.name("write", self.core).as_deref() != Some("!");
        if let Some(kind) =
            test.strip_suffix(".bmsk").or(test.strip_suffix(".wmsk")).or(test.strip_suffix(".dmsk"))
        {
            if !write {
                return Err(why(format!("{test} without its register write (not measured)")));
            }
            let at = |c: usize| predicate(&format!("{kind}.chan{c}"), Tested(tested.0));
            let mask = match &test[test.len() - 4..] {
                "bmsk" => (0..4).try_fold(0, |m, k| Ok::<_, Error>(m | (at(k)? as u32 * 0xff) << (8 * k)))?,
                "wmsk" => {
                    (0..2).try_fold(0, |m, k| Ok::<_, Error>(m | (at(2 * k)? as u32 * 0xffff) << (16 * k)))?
                }
                _ => at(0)? as u32 * 0xffff_ffff,
            };
            return self.write(insn, mask);
        }
        let p = predicate(&test, tested)?;
        if write {
            let v = value.ok_or_else(|| why(format!("{name}.sat's value (not measured)")))?;
            self.write(insn, v)?;
        }
        self.p[insn.get("p").unwrap() as usize] = p;
        self.p_set |= 1 << insn.get("p").unwrap();
        Ok(())
    }

    /// The test group with a one-source float function. Hardware
    /// (usse-form-coverage-test-fn): frcp, frsq, flog and fexp write their value, which
    /// tests as a float by its sign and zero at chan0, as fadd's does; a NaN
    /// (frsq of -4) does not test negative (the other tests of a NaN, and a
    /// near or infinite value, are not measured).
    fn test_fn(&mut self, name: &str, test: &str, av: u32) -> Result<(u32, Tested), Error> {
        if !matches!(name, "frcp" | "frsq" | "flog" | "fexp") {
            return Err(why(format!("one-source test op {name}")));
        }
        let (v, b) = func::eval(name, self.src(av, 6)?).map_err(why)?;
        if b.is_some() {
            return Err(why(format!("{name} test of a near value")));
        }
        self.decide()?;
        let t = if v & 0x7fff_ffff == 0 {
            if v != 0 {
                return Err(why(format!("{name} test of -0")));
            }
            0
        } else if flt::special(v) {
            let nan = v & 0x7f_ffff != 0;
            if !(nan && v >> 31 == 0 && test.starts_with("testnat.")) {
                return Err(why(format!("{name} {test} of an infinity or NaN")));
            }
            1
        } else if v >> 31 != 0 {
            -1
        } else {
            1
        };
        Ok((v, Tested([Some(t), None, None, None])))
    }

    /// eldd/eldq d, [base, index, #offset], limit: hardware (usse-cache-control-eld-address, usse-cache-control-eld-limit,
    /// E098): the dword (eldd) or the four (eldq) of element index + offset from the base when
    /// that element is below the limit, zeros otherwise. The cache modes change nothing a
    /// program sees (usse-cache-control-modes, usse-cache-control-cross); a fetch count, and an index, offset or
    /// limit with bit 31 set (signedness not settled), are not measured.
    fn eld(&mut self, insn: &Insn, bus: &mut dyn Bus) -> Result<(), Error> {
        let flags = insn.name("flags", self.core).unwrap();
        for f in flags.split('.').filter(|f| !f.is_empty()) {
            if !matches!(f, "skipinv" | "syncs" | "bpcache" | "fcfill" | "bypassl1") {
                return Err(why(format!("eld flag .{f}")));
            }
        }
        let n = if insn.name("type", self.core).as_deref() == Some("q") { 4 } else { 1 };
        let base = self.src(insn.get("base").unwrap(), 6)?;
        let index = self.src0(insn.get("index").unwrap())?;
        let limit = self.src(insn.get("limit").unwrap(), 6)?;
        let elem = index.wrapping_add(insn.get("offset").unwrap());
        if (index | limit | elem) >> 31 != 0 {
            return Err(why("eld with bit 31 set in its index, offset or limit (not measured)"));
        }
        if self.now.read.get().is_some() {
            return Err(why("an eld operand from a near value"));
        }
        let d = insn.get("dst").unwrap();
        let drc = insn.get("drc").unwrap();
        for k in 0..n {
            let v = if elem < limit { bus.load32(base.wrapping_add(4 * (n * elem + k)))? } else { 0 };
            let r = (d & 0x7f) as usize + k as usize;
            if r >= 124 {
                return Err(why("eld past the temporaries"));
            }
            self.pending.push((drc, if d >> 7 != 0 { Reg::Pa(r) } else { Reg::R(r) }, v));
        }
        Ok(())
    }

    /// ld/st: [base, +/-offset] with the offset in units of the data size; the
    /// .pre/.post forms write the moved base back before/after the access.
    ///
    /// Hardware, a repeat of N (E483, E515: stad N = 2 to 16, ldad N = 2 to 16, plain and
    /// post-increment forms, pre-increment for a store): iteration i is the access with the pointer
    /// register r(b + i * s1) and the data register r(d + i * s3), where s1 and s3 are the second and
    /// fourth smlsi increments (1 before any smlsi), each iteration reading its own pointer and
    /// moving it by the form's increment (after the access for `[rb,#k++]`, before for
    /// `[rb,++#k]`, not at all for `[rb,+#k]`); with a second increment of 0 the one pointer
    /// series of E483 stores N registers to N consecutive dwords. Hardware, a fetch store of N
    /// (E482, E516): N consecutive registers to N consecutive dwords, from b + k + 1 for `[rb,+#k]`
    /// and `[rb,++#k]`, from b + k for `[rb,#k++]`, and the two increment forms move rb by N,
    /// whatever k. Not run, so refused: a repeat with a fetch, with a register other than r, with
    /// a swizzled smlsi, with `.pre` on a load, a fetch store after smlsi, with a negative offset,
    /// or with a pa, sa or o pointer.
    fn load_store(&mut self, insn: &Insn, op: &str, bus: &mut dyn Bus) -> Result<(), Error> {
        let amdt = insn.name("amdt", self.core).unwrap();
        let size: u32 = if amdt == "ad" {
            4
        } else if amdt == "aw" {
            2
        } else if amdt == "ab" {
            1
        } else {
            return Err(why(format!("access {amdt}")));
        };
        let flags = insn.name("flags", self.core).unwrap();
        if size != 4 {
            return self.ls_narrow(insn, op, bus, size, &flags);
        }
        let (mut count, mut dst_inc, mut repeat) = (1u32, 1i32, 1u32);
        for f in flags.split('.').filter(|f| !f.is_empty()) {
            match f {
                "skipinv" | "syncs" | "nosched" | "bpcache" | "fcfill" | "bypassl1" => {}
                // A fetch of N dwords steps the destination by the MOE
                // increment smlsi set (the last of its four, inferred from the
                // firmware: it sets only that one, to 1, before its fetches;
                // not measured); before any smlsi by one (hardware:
                // usse-numbered-modifiers-family-fetch, N 2-16, and usse-numbered-modifiers-family-fetch-dst).
                _ if f.starts_with("fetch") && op.starts_with("ld") => {
                    count = f[5..].parse().unwrap();
                    dst_inc = self.moe_inc.map_or(1, |inc| inc[3]);
                }
                _ if f.starts_with("fetch") => {
                    count = f[5..].parse().unwrap();
                    if self.moe_inc.is_some() {
                        return Err(why("a fetch store after smlsi (not measured)"));
                    }
                }
                _ if f.starts_with("repeat") => repeat = f[6..].parse().unwrap(),
                _ => return Err(why(format!("flag .{f}"))),
            }
        }
        if insn.get("range").is_some_and(|r| r >> 10 != 0) {
            return Err(why("load range"));
        }
        if repeat == 1 {
            return self.ls_access(insn, op, bus, count, dst_inc);
        }
        if count > 1 {
            return Err(why("a repeat with a fetch (not measured)"));
        }
        if op == "ld.pre" {
            return Err(why("a pre-increment load with a repeat (not measured)"));
        }
        if self.moe_swizzle.iter().any(|s| s.is_some()) {
            return Err(why("a repeat of a load or store after a swizzled smlsi (not measured)"));
        }
        let store = op.starts_with("st");
        if !store && self.moe_inc.is_some() {
            return Err(why("an ldad repeat after smlsi (not measured: E483 ran it for stores)"));
        }
        let (bi, di) =
            (insn.form.role("base").unwrap(), insn.form.role(if store { "src" } else { "dst" }).unwrap());
        let (b, d) = (insn.v[bi], insn.v[di]);
        if b >> 7 != 0 || d >> 7 != 0 {
            return Err(why("a repeat of a load or store through a register other than r (not measured)"));
        }
        let (bstep, dstep) = self.moe_inc.map_or((1, 1), |inc| (inc[1], inc[3]));
        for it in 0..repeat as i32 {
            let (rb, rd) = (b as i32 + it * bstep, d as i32 + it * dstep);
            if !(0..124).contains(&rb) || !(0..124).contains(&rd) {
                return Err(why("a repeat past the temporaries"));
            }
            let mut one = insn.clone();
            (one.v[bi], one.v[di]) = (rb as u32, rd as u32);
            // a pointer register of the repeat that holds no address: the hardware's store to
            // 0xB1B1B1B1 did not fault in one case and the job faulted in 27 of 43 in another
            // (E483), so no fault is predicted
            match self.ls_access(&one, op, bus, 1, 1) {
                Err(Error::Fault(a)) => {
                    return Err(why(format!(
                        "a repeat through a pointer that is no address (0x{a:08X}): the fault is not predictable (E483)"
                    )));
                }
                r => r?,
            }
        }
        Ok(())
    }

    /// One access of load_store: `count` dwords (a fetch), the destination stepping by `dst_inc`.
    /// `ldab`/`ldaw` and `stab`/`staw` (E598, E599: 22 loads and 26 stores in a client pixel task, none in a
    /// firmware task). Hardware: an immediate offset counts elements of the access size, so the address is
    /// base + n (byte) or base + 2n (halfword); a load reads the bytes at the address, zero-extended (an odd
    /// halfword address reads the bytes there, across dwords too); a store puts the low byte or halfword of
    /// its source at the address and changes nothing else (a byte store at any address, a halfword store at
    /// an even one). Only the plain forms ran: no flag, drc0, and the r bank for the base, the destination
    /// and the store's source. Not measured, so refused: any flag, another drc or bank, a negative or
    /// register offset, the pre- and post-increment forms, a repeat or a fetch, a halfword store at an odd
    /// address. The immediate offset is accepted over its field (the jobs ran n = 0 to 7 for a load and 0 to 3
    /// for a store): that the unit rule holds beyond them is [infer].
    fn ls_narrow(
        &mut self,
        insn: &Insn,
        op: &str,
        bus: &mut dyn Bus,
        size: u32,
        flags: &str,
    ) -> Result<(), Error> {
        if let Some(f) = flags.split('.').find(|f| !f.is_empty()) {
            return Err(why(format!("flag .{f} on a narrow access (not measured)")));
        }
        if op != "ld" && op != "st" {
            return Err(why("an increment form of a narrow access (not measured)"));
        }
        let ov = insn.get("offset").unwrap();
        if insn.name("sign", self.core).is_some_and(|s| s.starts_with('-')) || ov >> 7 != 6 {
            return Err(why("a narrow access with a negative or register offset (not measured)"));
        }
        if insn.get("base").unwrap() >> 7 != 0 {
            return Err(why("a narrow access through a base outside the r bank (not measured)"));
        }
        let base = self.src0(insn.get("base").unwrap())?;
        let addr = base.wrapping_add(self.src(ov, 6)?.wrapping_mul(size));
        if self.now.read.get().is_some() {
            return Err(why("an address from a near value"));
        }
        let (first, last) = (addr & !3, addr.wrapping_add(size - 1) & !3);
        if op == "st" {
            if size == 2 && addr % 2 != 0 {
                return Err(why("a halfword store at an odd address (not measured)"));
            }
            if insn.get("src").unwrap() >> 7 != 0 {
                return Err(why("a narrow store of a source outside the r bank (not measured)"));
            }
            let v = self.src(insn.get("src").unwrap(), 6)?;
            let shift = 8 * (addr & 3);
            let mask = (if size == 1 { 0xff } else { 0xffff }) << shift;
            let old = bus.load32(first)?;
            match self.now.read.get() {
                Some(b) => self.near_mem.insert(first, b),
                None => self.near_mem.remove(&first),
            };
            return bus.store32(first, old & !mask | (v << shift) & mask);
        }
        if self.near_mem.contains_key(&first) || self.near_mem.contains_key(&last) {
            return Err(why("a load of a near value"));
        }
        let v = bus.load32(addr)? & if size == 1 { 0xff } else { 0xffff };
        let d = insn.get("dst").unwrap();
        let r = (d & 0x7f) as usize;
        if d >> 7 != 0 {
            return Err(why("a narrow load into a bank other than r (not measured)"));
        }
        if r >= 124 {
            return Err(why("fetch past the temporaries"));
        }
        let drc = insn.get("drc").unwrap();
        if drc != 0 {
            return Err(why("a narrow load on a drc other than drc0 (not measured)"));
        }
        self.pending.push((drc, Reg::R(r), v));
        Ok(())
    }

    fn ls_access(
        &mut self,
        insn: &Insn,
        op: &str,
        bus: &mut dyn Bus,
        count: u32,
        dst_inc: i32,
    ) -> Result<(), Error> {
        let neg = insn.name("sign", self.core).is_some_and(|s| s.starts_with('-'));
        // An immediate offset counts data-size units; a register one holds a
        // stride and an index, (high 16 bits) * (low 16 bits) bytes (hardware:
        // 0x00010001 moves by 1 byte, 0x00020002 and 0x00040001 by 4).
        let ov = insn.get("offset").unwrap();
        let o = self.src(ov, 6)?;
        let off = if ov >> 7 == 6 { o.wrapping_mul(4) } else { (o >> 16).wrapping_mul(o & 0xffff) };
        let base_v = insn.get("base").unwrap();
        let base = self.src0(base_v)?;
        let moved = if neg { base.wrapping_sub(off) } else { base.wrapping_add(off) };
        let fetch_store = op.starts_with("st") && count > 1;
        if fetch_store && (neg || ov >> 7 != 6) {
            return Err(why("a fetch store with a negative or register offset (not measured)"));
        }
        let addr = match op {
            // hardware (usse-numbered-modifiers-family-fetch, N 2-16, usse-numbered-modifiers-family-fetch-dst, usse-memory-ldad-reg-off-fetch): a
            // fetch by base plus offset, immediate or register, starts one dword after it
            "ld" if count > 1 => moved.wrapping_add(4),
            // a fetch store (E482, E516): one dword after for the plain and the pre-increment
            // form, at the offset for the post-increment one
            "st" | "st.pre" if count > 1 => moved.wrapping_add(4),
            "st.post" if count > 1 => moved,
            "ld" | "st" => moved,
            o if o.ends_with(".pre") => moved,
            _ => base,
        };
        if fetch_store {
            // the increment forms move rb by the fetch's N dwords, whatever the offset
            if op.contains('.') {
                self.write_src0(base_v, base.wrapping_add(4 * count))?;
            }
        } else if op.contains('.') {
            self.write_src0(base_v, moved)?;
        }
        if self.now.read.get().is_some() {
            return Err(why("an address from a near value"));
        }
        if op.starts_with("st") {
            let sv = insn.get("src").unwrap();
            // E516 ran the registers of a fetch up to r33
            if fetch_store && (sv >> 7 != 0 || (sv & 0x7f) + count > 34) {
                return Err(why("a fetch store of registers other than r or above r33 (not measured, E516)"));
            }
            for k in 0..count {
                let v = self.src(sv + k, 6)?;
                let at = addr.wrapping_add(4 * k);
                match self.now.read.get() {
                    Some(b) => self.near_mem.insert(at, b),
                    None => self.near_mem.remove(&at),
                };
                bus.store32(at, v)?;
            }
            return Ok(());
        }
        let d = insn.get("dst").unwrap();
        // hardware (usse-numbered-modifiers-family-fetch-edge): a fetch whose registers would run past the
        // task's temporaries writes none of them (vec1's ldad.fetch4 r30 with 32 left r31)
        let last = (d & 0x7f) as i32 + (count as i32 - 1) * dst_inc;
        if d >> 7 == 0 && count > 1 && dst_inc == 1 && last as usize >= self.temps {
            return Ok(());
        }
        for k in 0..count {
            if self.near_mem.contains_key(&addr.wrapping_add(4 * k)) {
                return Err(why("a load of a near value"));
            }
            let v = bus.load32(addr.wrapping_add(4 * k))?;
            let r = ((d & 0x7f) as i32 + k as i32 * dst_inc) as usize;
            if r >= 124 {
                return Err(why("fetch past the temporaries"));
            }
            let drc = insn.get("drc").unwrap();
            self.pending.push((drc, if d >> 7 != 0 { Reg::Pa(r) } else { Reg::R(r) }, v));
        }
        Ok(())
    }

    /// A source-0 operand: number[6:0] | bank (0 r, 1 pa, 2 o, 3 sa).
    fn src0(&self, v: u32) -> Result<u32, Error> {
        let r = (v & 0x7f) as usize;
        Ok(match v >> 7 {
            0 => self.temp(r)?,
            1 => {
                self.not_pending(Reg::Pa(r))?;
                self.read_pa(r)?
            }
            2 => self.read_o(r)?,
            3 => self.read(self.sa[r], self.written.sa, r, "sa")?,
            b => return Err(why(format!("source-0 bank {b}"))),
        })
    }

    fn write_src0(&mut self, v: u32, x: u32) -> Result<(), Error> {
        let r = (v & 0x7f) as usize;
        match v >> 7 {
            0 if r < 124 => self.set_r(r, x)?,
            1 => self.set_pa(r, x),
            2 => self.write_o(r, x)?,
            3 => {
                (self.sa[r], self.written.sa) = (x, self.written.sa | 1 << r);
                self.mark("sa", r);
            }
            b => return Err(why(format!("source-0 bank {b} written"))),
        }
        Ok(())
    }

    /// A float source 1/2: number[6:0] | bank[9:7] | neg[10] | abs[11].
    fn fsrc(&self, v: u32) -> Result<u32, Error> {
        Ok(flt::modify(self.src(v & 0x3ff, 6)?, v >> 10 & 1 != 0, v >> 11 & 1 != 0))
    }

    /// A float source 0: number[6:0] | pa[7] | abs[8].
    fn fsrc0(&self, v: u32) -> Result<u32, Error> {
        Ok(flt::modify(self.src0(v & 0xff)?, false, v >> 8 & 1 != 0))
    }

    /// A float source of the role, read as the form reads it: whole, or with
    /// enc[54] (half_form) a half (half_src).
    fn fval(&self, insn: &Insn, role: &str) -> Result<u32, Error> {
        let v = insn.get(role).unwrap();
        if half_form(insn.form) {
            let mods = if role == "src0" { v >> 8 } else { v >> 10 };
            if mods & 3 != 0 {
                return Err(why("a modifier on a half-float source (not measured)"));
            }
            let (w, h) = self.half_reg(v, role == "src0")?;
            return half_src(w >> (16 * h) & 0xffff);
        }
        if role == "src0" { self.fsrc0(v) } else { self.fsrc(v) }
    }

    /// The register a source of a half-float form names (v as fsrc/fsrc0
    /// take it): number n >= 64 of the r bank is half n & 1 of r((n - 64) >> 1),
    /// r0-r29 (usse-form-coverage-form2-flt16, usse-form-coverage-form2-dual-flt16); (the whole register,
    /// the half). The other numbers and banks (whole registers, i, constants,
    /// o, pa, sa, indexed) are not measured.
    fn half_reg(&self, v: u32, src0: bool) -> Result<(u32, u32), Error> {
        let bank = if src0 { v >> 7 & 1 } else { v >> 7 & 7 };
        let n = v & 0x7f;
        if bank != 0 || !(64..124).contains(&n) {
            return Err(why(format!(
                "a half-float form's source other than a temporary's half (bank {bank}, number {n}: not \
                 measured)"
            )));
        }
        Ok((self.temp(((n - 64) >> 1) as usize)?, n & 1))
    }

    fn width(&self, insn: &Insn, role: &str) -> u32 {
        insn.form.role(role).map_or(0, |i| insn.form.f[i].width())
    }

    /// Whether the instruction ends the program (its flags print .end).
    fn ends(&self, insn: &Insn) -> bool {
        // phas.end: the form names no field for enc[51], which is its .end
        if insn.form.op == "phas" && insn.word >> 51 & 1 != 0 {
            return true;
        }
        ["end", "flags", "op"].iter().any(|r| insn.name(r, self.core).is_some_and(|t| t.contains(".end")))
    }

    /// Source 2, or the rotated immediate of the bitwise group.
    fn src2_or_rot(&self, insn: &Insn) -> Result<u32, Error> {
        let i = insn.form.role("src2").unwrap();
        let f = &insn.form.f[i];
        if f.width() == 21 {
            // the rotated immediate: mantissa[15:0] | rotate[20:16]
            let v = insn.v[i];
            return Ok((v & 0xffff).rotate_left(v >> 16 & 31));
        }
        self.src(insn.v[i], 6)
    }

    /// A source-1/2 operand: number[6:0] | bank[9:7].
    fn src(&self, v: u32, _imm_bank: u32) -> Result<u32, Error> {
        let r = (v & 0x7f) as usize;
        Ok(match v >> 7 {
            0 => self.temp(r)?,
            1 => self.read_o(r)?,
            2 => {
                self.not_pending(Reg::Pa(r))?;
                self.read_pa(r)?
            }
            3 => self.read(self.sa[r], self.written.sa, r, "sa")?,
            6 => r as u32,
            7 => self.internal(r)?,
            5 if r < 64 => CONST_BANK[r],
            5 => self.global(r - 64)?,
            4 => return self.src(self.indexed(r as u32, [0, 1, 2, 3])?, 6),
            b => return Err(why(format!("source bank {b}"))),
        })
    }

    /// An indexed operand, bank[6:5] (r, o, pa, sa) | i.h[4] | offset[3:0],
    /// as an ordinary one with `banks` numbering r, o, pa and sa. Hardware
    /// (usse-indexing-index-unit, usse-indexing-index-width3): the index counts registers and only bits
    /// 0-9 of i.l count (i.h is assumed alike: its probes stay below 0x400).
    fn indexed(&self, r: u32, banks: [u32; 4]) -> Result<u32, Error> {
        let h = (r >> 4 & 1) as usize;
        if self.written.index >> h & 1 == 0 {
            return Err(why(format!(
                "reads i.{} before the program writes it",
                if h == 1 { "h" } else { "l" }
            )));
        }
        let n = (self.index[h] & 0x3ff) + (r & 15);
        if n > 127 {
            return Err(why("index past the bank"));
        }
        // r124-r127 through an index are not i0-i3 (usse-internal-registers-ireg-index: reads vary,
        // writes leave i0-i3 alone)
        if r >> 5 & 3 == 0 && n >= 124 {
            return Err(why("an index reaching r124-r127 (not i0-i3) is open"));
        }
        Ok(banks[(r >> 5 & 3) as usize] << 7 | n)
    }

    /// An instruction with smbo's base offsets added to the register numbers of its
    /// destination and source slots (hardware, E087, temporaries only): a store's stored
    /// register is its source-2 slot; immediates stay; the source-0 offset is not measured.
    fn based(&self, insn: &Insn) -> Result<Insn, Error> {
        const SLOTS: [&[&str]; 4] = [&["dst"], &["src0", "base"], &["src1", "offset"], &["src2", "src"]];
        let mut it = insn.clone();
        for (slot, (roles, &k)) in SLOTS.iter().zip(&self.moe_base).enumerate() {
            if k == 0 {
                continue;
            }
            for role in roles.iter() {
                let Some(i) = insn.form.role(role) else { continue };
                let v = insn.v[i];
                let bank = if slot == 1 { v >> 7 & 1 } else { v >> 7 & 7 };
                if insn.form.f[i].width() == 21 || (slot != 1 && bank >= 6) {
                    continue; // an immediate
                }
                if slot == 1 {
                    return Err(why("smbo source-0 offset (not measured)"));
                }
                if bank != 0 {
                    return Err(why(format!("smbo offset on a {role} that is not a temporary")));
                }
                let r = (v & 0x7f) + k;
                if r >= 124 {
                    return Err(why(format!("smbo offset takes {role} past the temporaries")));
                }
                it.v[i] = v & !0x7f | r;
            }
        }
        Ok(it)
    }

    /// An instruction with smoa's offsets and address modes applied to the register numbers
    /// of its destination and source slots (hardware, E097, E105, temporaries only): with
    /// i = the register + the offset and M = the slot's smr range - 1, none gives i, clamp
    /// min(i, M), mirror 2M - i and repeat i - (M + 1) when i is past M. Only the first
    /// register is mapped; a repeat's iterations step on from it.
    fn addressed(&self, insn: &Insn) -> Result<Insn, Error> {
        const SLOTS: [&[&str]; 4] = [&["dst"], &["src0", "base"], &["src1", "offset"], &["src2", "src"]];
        let (off, mode) = self.moe_addr;
        let mut it = insn.clone();
        for (slot, roles) in SLOTS.iter().enumerate() {
            if off[slot] == 0 && mode[slot] == 0 {
                continue;
            }
            for role in roles.iter() {
                let Some(i) = insn.form.role(role) else { continue };
                let v = insn.v[i];
                let bank = if slot == 1 { v >> 7 & 1 } else { v >> 7 & 7 };
                if insn.form.f[i].width() == 21 || (slot != 1 && bank >= 6) {
                    continue; // an immediate
                }
                if slot == 1 {
                    return Err(why("smoa on source 0 (not measured)"));
                }
                if bank != 0 {
                    return Err(why(format!("smoa on a {role} that is not a temporary")));
                }
                let r = (v & 0x7f) as i64 + off[slot] as i64;
                let m = self.moe_range[slot] as i64 - 1;
                let r = match mode[slot] {
                    2 => r.min(m),
                    3 if r > m => 2 * m - r,
                    1 if r > m => r - (m + 1),
                    _ => r,
                };
                if !(0..124).contains(&r) {
                    return Err(why(format!("smoa takes {role} to r{r} (not modelled)")));
                }
                it.v[i] = v & !0x7f | r as u32;
            }
        }
        Ok(it)
    }

    /// g0-g63 as a fill's instance reads them (hardware: usse-constant-banks-gbank-pixels, E086): the
    /// position in the 32x16 tile and the 2x2 quad from the pixel, the constant ones, and 0;
    /// the per-tile and scheduler-assigned ones (g18, g19, g21, g22) are not modelled.
    fn global(&self, g: usize) -> Result<u32, Error> {
        let unknown = || why(format!("g{g} (per-instance values, not modelled)"));
        if let Some((v, per, total)) = self.vertex {
            // A vertex task (11.33, q053-vtx and q053-vtx2): measured only in a draw of 126 vertices at 4, 6
            // and 8 vertices a task, on g16, g17, g20, g22 to g31 and g39 to g43; every other register, and
            // any other draw, is refused instead of answered.
            if total != 126 || !matches!(per, 4 | 6 | 8) || v >= total {
                return Err(why(format!(
                    "g{g} in a vertex task (vertex {v} of {total} at {per} a task; \
                     measured only for 126 vertices at 4, 6 and 8 a task)"
                )));
            }
            let (task, lane) = (v / per, v % per);
            // the vertices the task holds: the last of a draw may hold fewer (126 at 4 a task: 2; at 8: 6)
            let held = per.min(total - task * per);
            return Ok(match g {
                // per task and lane: read from the q053-vtx jobs at 8 a task (the fit) and held on the
                // jobs at 4 and 6; g23 was read from the data after all 12 jobs were in, so it is a fit too
                17 => task % 4,
                22 => lane / 4 % 2,
                23 => 0x10 * (task / 2 % 2),
                24 => 8 * (task % 2),
                25 => lane % 4,
                39 => 4 * (lane / 4 % 2),
                // constant on every readable vertex of the 12 jobs
                16 | 26..=31 | 40 => 0,
                20 => 1,
                42 => 0x3f80_0000,
                // measured with 2 vertices held (a last task of 4 a task) and with 4, 6 and 8 held; 1, 3, 5
                // and 7 held were not seen
                41 | 43 => match (held, g) {
                    (2, 41) => 3,
                    (2, 43) => 0x2000_0000,
                    (4 | 6 | 8, 41) => 0xf,
                    (4 | 6 | 8, 43) => 0xdf00_0000,
                    _ => {
                        return Err(why(format!(
                            "g{g} with {held} vertices held (measured with 2, 4, 6 and 8)"
                        )));
                    }
                },
                // g18 and g21 follow the task without a fitted rule; g19 reads by the instruction (E372) and
                // was measured through a mov only; g0 to g15, g32 to g38 and g44 to g63 were not read
                _ => return Err(unknown()),
            });
        }
        let pos = |f: fn(u32, u32) -> u32| self.pixel.map(|(x, y)| f(x, y)).ok_or_else(unknown);
        if self.tri_pixel {
            // a triangle's pixel task (R3-pixel p-c3, E808, held out at three triangles): the
            // fill's readings of g23, g24 and g25 hold; nothing else of the bank was read there
            return match g {
                23 => pos(|x, _| x % 32),
                24 => pos(|_, y| y % 16),
                25 => pos(|x, y| (x & 1) + 2 * (y & 1)),
                _ => Err(why(format!(
                    "g{g} in a triangle's pixel task (only g23, g24 and g25 were read there, E808)"
                ))),
            };
        }
        Ok(match g {
            17 => pos(|x, y| 2 * (x >> 4 & 1) + (y >> 3 & 1))?,
            23 => pos(|x, _| x % 32)?,
            24 => pos(|_, y| y % 16)?,
            25 => pos(|x, y| (x & 1) + 2 * (y & 1))?,
            39 => pos(|x, y| 4 * (x >> 1 & 1) + 8 * (y >> 1 & 1))?,
            20 | 41 => 1,
            42 => 0x3f80_0000,
            43 => 0xff00_0000,
            18 | 19 | 21 | 22 => return Err(unknown()),
            _ => 0,
        })
    }

    fn temp(&self, r: usize) -> Result<u32, Error> {
        if r >= 124 {
            return self.internal(r - 124);
        }
        self.own_temp(r)?;
        self.not_pending(Reg::R(r))?;
        self.read(self.r[r], self.written.r, r, "r")
    }

    /// A read of output register r. In a triangle's pixel task (Q276, Q023) a read of o4 to o7
    /// reads o(r mod 4) of the instance (E878, E905, held out): refused, with every o beyond.
    fn read_o(&self, r: usize) -> Result<u32, Error> {
        if self.tri_pixel && r >= 4 {
            return Err(why(format!(
                "a read of o{r} in a triangle's pixel task (o4 to o7 read o0 to o3, E878, E905: \
                 refused, Q276)"
            )));
        }
        self.read(self.o[r], self.written.o, r, "o")
    }

    /// A write of output register r. In a triangle's pixel task (Q276, Q023) only o0's word
    /// lands at its own pixel: o1 to o3's land at other pixels under g25 predicates (E742, E759,
    /// E772), o4's pixels hold OR(o0, o3) of a lane the job picks (E709, E838, E850, E858, E880)
    /// and o4 to o7's own words reach no pixel (E871): no per-pixel rule, so refused.
    fn write_o(&mut self, r: usize, v: u32) -> Result<(), Error> {
        if self.tri_pixel && r != 0 {
            return Err(why(format!(
                "a write of o{r} in a triangle's pixel task (its word lands at other pixels or \
                 none, E742, E871, E880: refused, Q276)"
            )));
        }
        (self.o[r], self.written.o) = (v, self.written.o | 1 << r);
        self.mark("o", r);
        Ok(())
    }

    /// A read of register n of a bank (see read), noting a near value's bound.
    fn read(&self, v: u32, written: u128, n: usize, bank: &'static str) -> Result<u32, Error> {
        let v = read(v, written, n, bank)?;
        if let Some(w) = self.unknown.get(&(bank, n)) {
            return Err(why(format!("{w} (read in {bank}{n})")));
        }
        if let Some(&b) = self.bounds.get(&(bank, n)) {
            self.now.read.set(Some(if self.now.read.get().is_some() { Bound::Derived } else { b }));
        }
        Ok(v)
    }

    /// Note what a write of register n of a bank holds (see Machine::bounds).
    fn mark(&mut self, bank: &'static str, n: usize) {
        let r = self.now.read.get();
        let b = match self.now.out {
            Out::Reads => r.map(|_| Bound::Derived),
            Out::Move => r,
            Out::Fn(b) => r.map(|_| Bound::Derived).or(b),
        };
        match b {
            Some(b) => self.bounds.insert((bank, n), b),
            None => self.bounds.remove(&(bank, n)),
        };
        match self.now.unknown {
            Some(w) => self.unknown.insert((bank, n), w),
            None => self.unknown.remove(&(bank, n)),
        };
    }

    /// A decision (a predicate) from what the operation read: one on a near
    /// value is not known.
    fn decide(&self) -> Result<(), Error> {
        if self.now.read.get().is_some() {
            return Err(why("a predicate from a near value"));
        }
        Ok(())
    }

    fn not_pending(&self, reg: Reg) -> Result<(), Error> {
        if self.pending.iter().any(|p| p.1 == reg) || self.pending_unknown.iter().any(|p| p.1 == reg) {
            return Err(why(format!("reads {reg:?} before its DRC result lands (wdf)")));
        }
        Ok(())
    }

    fn internal(&self, r: usize) -> Result<u32, Error> {
        if r < 3 {
            return self.read(self.i[r], self.written.i as u128, r, "i");
        }
        // hardware (usse-internal-registers-per-pixel, usse-internal-registers-bank7):
        // number n mod 16 is 4m + j, ij of the instance m places on (TL, TR,
        // BL, BR, round again), j = 3 being i2 there, but i3 itself the next
        // instance's i0
        let Some(q) = &self.quad else { return Err(why(format!("i{r} reads another instance of the quad"))) };
        let n = r % 16;
        let (m, j) = if n == 3 { (1, 0) } else { (n / 4, (n % 4).min(2)) };
        let k = (q.pos + m) % 4;
        read(q.i[k][j], q.written[k] as u128, j, "a quad neighbour's i")
    }

    /// Write the destination (number[6:0] | bank[9:7]), refusing a write mask.
    fn write(&mut self, insn: &Insn, v: u32) -> Result<(), Error> {
        if let Some(m) = insn.name("mask", self.core)
            && !m.is_empty()
        {
            return Err(why(format!("write mask {m}")));
        }
        self.write_dst(insn.get("dst").unwrap(), v)
    }

    /// Write a destination operand (number[6:0] | bank[9:7]).
    fn write_dst(&mut self, d: u32, v: u32) -> Result<(), Error> {
        let r = (d & 0x7f) as usize;
        match d >> 7 {
            0 if r < 124 => self.set_r(r, v)?,
            0 => self.set_i(r - 124, v)?,
            1 => self.write_o(r, v)?,
            // hardware (E496, Q098; usse-pa-dest, 3 of 3 jobs, and E380): in a fill a write to
            // pa0 by ima32 or mov is lost, pa0 reading what it read before; E380 (30 fill jobs):
            // a mov to pa1 to pa7 is lost the same way. ima32 to pa1 and up was not run. In an
            // EDM task (E820, 3 of 3 each, mov only): a mov to pa3 is sa67, kept to the next
            // pass; to pa2 is sa66, which the next event's program rewrites [infer]; to pa4 is
            // lost, sa68 and pa4 unchanged. pa0, pa1, pa5 up and other forms did not run
            2 if self.edm_task => match r {
                2 | 3 if self.mov_dest => {
                    (self.sa[64 + r], self.written.sa) = (v, self.written.sa | 1 << (64 + r));
                    self.mark("sa", 64 + r);
                }
                4 if self.mov_dest => {}
                _ => {
                    return Err(why(format!(
                        "a write to pa{r} in an EDM task (E820 measured mov to pa2, pa3 and pa4 only, Q098)"
                    )));
                }
            },
            2 if r == 0 => {}
            2 if self.mov_dest && r < 8 => {}
            2 => {
                return Err(why(format!(
                    "a write to pa{r} (lost in a fill for pa0 by ima32 or mov, E496, and for pa1 to pa7 \
                     by mov, E380; other forms not run, Q098)"
                )));
            }
            4 => {
                (self.sa[r], self.written.sa) = (v, self.written.sa | 1 << r);
                self.mark("sa", r);
            }
            7 => self.set_i(r, v)?,
            3 => return self.write_dst(self.indexed(r as u32, [0, 1, 2, 4])?, v),
            // i.l, i.h, i.lh: hardware (usse-indexing-index-high) i.lh takes i.l from the
            // low half and i.h from the high one
            6 if r & 3 != 0 => {
                let both = r & 3 == 3;
                if r & 1 != 0 {
                    self.index[0] = v & 0xffff;
                }
                if r & 2 != 0 {
                    self.index[1] = if both { v >> 16 } else { v & 0xffff };
                }
                self.written.index |= (r & 3) as u8;
            }
            // hardware (usse-destination-bank6-temps, -moved, -outputs): bank 6 with neither
            // index bit (printed i.) changes no register a fill reads, for the numbers run (0, 4,
            // 8, 16, 64 and 124; the attribute registers only for 0, 4 and 64); any other number
            // with the low two bits clear was not run and stops (E366)
            6 if matches!(r, 0 | 4 | 8 | 16 | 64 | 124) => {}
            6 => return Err(why(format!("destination bank 6 number {r}"))),
            b => return Err(why(format!("destination bank {b}"))),
        }
        Ok(())
    }

    fn set_r(&mut self, r: usize, v: u32) -> Result<(), Error> {
        self.own_temp(r)?;
        self.r[r] = v;
        self.written.r |= 1 << r;
        self.mark("r", r);
        Ok(())
    }

    /// Temporaries past the task's allocation are other instances' (hardware,
    /// usse-indexing-index-width: such reads return the next instances' registers).
    fn own_temp(&self, r: usize) -> Result<(), Error> {
        if r >= self.temps {
            return Err(why(format!("r{r} is past the task's {} temporaries", self.temps)));
        }
        Ok(())
    }

    /// Read pa<r>. In an EDM task pa0 to pa4 are sa64 to sa68 (hardware, S2 e2r/e2w: pa_n read
    /// sa_(64+n) for n = 0..4, 3 of 3 jobs, and a write to sa67 or sa68 showed through pa3 or
    /// pa4 in the same pass and the next); pa5 and up are not measured there (Q098).
    fn read_pa(&self, r: usize) -> Result<u32, Error> {
        if self.edm_task {
            if r >= 5 {
                return Err(why(format!("a read of pa{r} in an EDM task (only pa0 to pa4 measured, Q098)")));
            }
            return self.read(self.sa[64 + r], self.written.sa, 64 + r, "sa");
        }
        self.read(self.pa[r], self.written.pa, r, "pa")
    }

    fn set_pa(&mut self, r: usize, v: u32) {
        self.pa[r] = v;
        self.written.pa |= 1 << r;
        self.mark("pa", r);
    }

    fn set_i(&mut self, r: usize, v: u32) -> Result<(), Error> {
        if r >= 3 {
            // hardware (usse-internal-registers-per-pixel, -bank7): writes to i3-i7
            // are dropped, in no instance of the quad
            if r < 8 {
                return Ok(());
            }
            return Err(why(format!("a write of i{r}")));
        }
        self.i[r] = v;
        self.written.i |= 1 << r;
        self.mark("i", r);
        Ok(())
    }
}

/// The byte a colour factor selects for byte `ch` from sources s0-s2 (see
/// Machine::sop2): zero, s0-s2 (this byte), s0a-s2a (the alpha bytes), asat,
/// sop2's s2scale (s2) and zeros (0), and .comp for 1 - factor.
fn colour_factor(sel: &str, ch: u32, s: [Chans; 3]) -> Result<i64, Error> {
    let c = ch as usize;
    let (name, comp) = sel.strip_suffix(".comp").map_or((sel, false), |n| (n, true));
    let (a1, a2) = (s[1][3], s[2][3]);
    let f = match name {
        "zero" | "zeros" => 0,
        "s0" => s[0][c],
        "s1" => s[1][c],
        "s2" | "s2scale" => s[2][c],
        "s0a" => s[0][3],
        "s1a" => a1,
        "s2a" => a2,
        // hardware (sop2wm): on the alpha byte asat is 1, with or without
        // .comp (sop2's alpha selectors have no asat)
        "asat" if ch == 3 => return Ok(255),
        "asat" if comp => return Ok(a2.min(255 - a1)),
        "asat" => a1.min(255 - a2),
        _ => return Err(why(format!("colour factor {sel}"))),
    };
    Ok(if comp { 255 - f } else { f })
}

/// A sum of byte products over 255, rounded once (half up) and clamped.
fn colour_round(t: i64) -> i64 {
    (2 * t + 255).div_euclid(510)
}

/// A colour source's four channel values, 1.0 = 255: its bytes, or with .c10
/// (hardware, usse-colour-ops-c10) the signed 10-bit lanes at bits 0, 10 and 20 clamped
/// to +/-510, the alpha being lane 0.
type Chans = [i64; 4];

fn chans(w: u32, c10: bool) -> Chans {
    if !c10 {
        return [0, 1, 2, 3].map(|c| (w >> (8 * c) & 0xff) as i64);
    }
    let lane = |k: u32| {
        let x = (w >> (10 * k) & 0x3ff) as i64;
        (if x >= 512 { x - 1024 } else { x }).clamp(-510, 510)
    };
    [lane(0), lane(1), lane(2), lane(0)]
}

/// Channel results to a destination: saturated bytes, or with .c10 the
/// three colour results in 10-bit lanes clamped to +/-510, bits 30-31 clear
/// (the alpha result is dropped).
fn colour_out(v: Chans, c10: bool) -> u32 {
    if c10 {
        return (0..3).fold(0, |w, k| w | ((v[k].clamp(-510, 510) as u32) & 0x3ff) << (10 * k));
    }
    (0..4).fold(0, |w, k| w | (v[k].clamp(0, 255) as u32) << (8 * k))
}

/// sop3, lrp and sop3c, all four bytes (see Machine::sop3).
fn blend3(op: &str, csel: &str, alpha: (&str, &str), s: [Chans; 3]) -> Result<Chans, Error> {
    let f = |sel: &str, ch: u32| colour_factor(sel, ch, s);
    let mut c: Vec<&str> = csel.split(", ").collect();
    // sop3's alrp form: with neg, -op(s1 * f2, s2 * f1), the factors swapped
    let neg = c.last() == Some(&"neg");
    if neg {
        c.pop();
    }
    let sum = |op: &str, a: i64, b: i64| if op == "sub" { a - b } else { a + b };
    let mut out = [0; 4];
    for ch in 0..3 {
        let (x1, x2) = (s[1][ch as usize], s[2][ch as usize]);
        let t = match (op, &c[..]) {
            ("sop3", [f1, f2, o @ ("add" | "sub")]) if neg => -sum(o, x1 * f(f2, ch)?, x2 * f(f1, ch)?),
            ("sop3", [f1, f2, o @ ("add" | "sub")]) => sum(o, x1 * f(f1, ch)?, x2 * f(f2, ch)?),
            ("lrp", [f1, f2, t]) if !neg => {
                let w = if *t == "s0" { s[0][ch as usize] } else { s[0][3] };
                f(f1, ch)? * (255 - w) + f(f2, ch)? * w
            }
            ("sop3c", [f1, f2, a, b]) if !neg => {
                let x = |n: &str| match n {
                    "one" => 255,
                    "s1" => x1,
                    "s1.comp" => 255 - x1,
                    "s2" => x2,
                    _ => 255 - x2,
                };
                x(a) * f(f1, ch)? + x(b) * f(f2, ch)?
            }
            _ => return Err(why(format!("{op} colour {csel}"))),
        };
        out[ch as usize] = colour_round(t);
    }
    let (a0, a1, a2) = (s[0][3], s[1][3], s[2][3]);
    let a: Vec<&str> = alpha.1.split(", ").collect();
    let t = match (alpha.0, &a[..]) {
        ("asop", [g1, g2, o]) => sum(o, a1 * f(g1, 3)?, a2 * f(g2, 3)?),
        // arsop g, op: -op(s1a * (the second colour factor), s2a * g); so add
        // is never positive (usse-colour-ops-sop3-lrp, x-arsop)
        ("arsop", [g, o]) => -sum(o, a1 * f(c[1], 3)?, a2 * f(g, 3)?),
        ("alrp", [g1, g2]) => f(g1, 3)? * (255 - a0) + f(g2, 3)? * a0,
        _ => return Err(why(format!("{op} alpha {}", alpha.1))),
    };
    out[3] = colour_round(t);
    Ok(out)
}

/// movc: per lane of the type, s1 where the lane of s0 passes the test, else
/// s2. Hardware (usse-movc-i8, -i16, -i32, -i10, -flt): the lanes are signed; i10
/// has three 10-bit lanes and writes bits 30-31 as 0; flt compares as f32
/// with denormals as zero (a NaN is non-zero, neither negative nor positive).
fn movc(ty: &str, test: &str, s0: u32, s1: u32, s2: u32) -> Result<u32, Error> {
    let pass = |x: f64| match test {
        ".tz" => x == 0.0,
        ".tnz" => x != 0.0,
        ".tn" => x < 0.0,
        _ => x >= 0.0,
    };
    if ty == ".flt" {
        let x = if s0 >> 23 & 0xff == 0 { 0.0 } else { f32::from_bits(s0) as f64 };
        return Ok(if pass(x) { s1 } else { s2 });
    }
    let (w, n) = match ty {
        ".i8" => (8, 4),
        ".i16" => (16, 2),
        ".i32" => (32, 1),
        ".i10" => (10, 3),
        _ => return Err(why(format!("movc{ty}"))),
    };
    let mut r = 0;
    for k in 0..n {
        let m = (u64::MAX >> (64 - w)) << (w * k);
        let lane = ((s0 as u64 & m) >> (w * k)) as i64;
        let x = if lane >> (w - 1) & 1 != 0 { lane - (1 << w) } else { lane };
        r |= (if pass(x as f64) { s1 } else { s2 }) as u64 & m;
    }
    Ok(r as u32)
}

/// One byte of a sop2 blend: `spec` is the printed selection ("[comp, ]f1,
/// f2, op[, neg]"), see Machine::sop2.
fn blend(spec: &str, s1: Chans, s2: Chans, ch: u32) -> Result<i64, Error> {
    let mut parts: Vec<&str> = spec.split(", ").collect();
    let neg = parts.last() == Some(&"neg");
    if neg {
        parts.pop();
    }
    let pre = parts.first() == Some(&"comp");
    if pre {
        parts.remove(0);
    }
    let [f1, f2, op] = parts[..] else { return Err(why(format!("sop2 selection {spec}"))) };
    let factor = |sel: &str| colour_factor(sel, ch, [[0; 4], s1, s2]);
    let (g1, g2) = (factor(f1)?, factor(f2)?);
    let (mut x1, mut x2) = (s1[ch as usize], s2[ch as usize]);
    let k = if f1.starts_with("s2scale") { 2 } else { 1 };
    let mut t = match op {
        "min" => x1.min(x2) * 255,
        "max" => x1.max(x2) * 255,
        _ => {
            if pre {
                x1 = 255 - x1;
            }
            if f2.starts_with("zeros") {
                x2 -= 128;
            }
            if op == "add" { x1 * g1 + x2 * g2 } else { x1 * g1 - x2 * g2 }
        }
    };
    if neg {
        t = -t;
    }
    Ok(colour_round(k * t))
}

/// The groups whose repeat field runs iterations (see Machine::iterations);
/// fds's sources advance by .incs as fmad's (usse-gradients-fds-incs).
const REPEATS: [&str; 16] = [
    "mov", "bitwise", "fmad", "fsubflr", "fminmax", "fdp", "fdpc", "fddp", "fddpc", "fmad16", "movc",
    "movmsk", "pack", "rlp", "fsc", "fds",
];
/// The ops whose flags carry a repeat count (see Machine::iterations).
const COLOUR_REPEATS: [&str; 8] = ["sop2", "fpma", "idot4", "idot3", "u16dot3", "u8dot3a", "adif", "adifsum"];

/// Whether a float form reads its sources as half floats: enc[54] set in the
/// multiply-add, dot-product, min/max, fdsx/fdsy and dual-issue groups.
fn half_form(form: &Form) -> bool {
    matches!(form.op, "fmad" | "fsubflr" | "fdp" | "fdpc" | "fddp" | "fddpc" | "fminmax" | "fds" | "dual")
        && form.mask >> 54 & 1 != 0
        && form.val >> 54 & 1 != 0
}

/// A half-float source as the f32 of its value (hardware, usse-form-coverage-form2-flt16: the
/// operation then runs as on f32 sources); the halves no probe read
/// (denormals, infinities, NaNs) stop.
fn half_src(h: u32) -> Result<u32, Error> {
    let (e, f) = (h >> 10 & 31, h & 1023);
    if e == 31 || e == 0 && f != 0 {
        return Err(why(format!("a half-float source 0x{h:04x} (denormal, infinity or NaN: not measured)")));
    }
    let mag = if e == 0 { 0.0 } else { (1024 + f) as f32 * 2f32.powi(e as i32 - 25) };
    Ok(if h >> 15 != 0 { -mag } else { mag }.to_bits())
}

/// A half as the f32 of the same value (exact); infinities and NaNs stop.
fn half_f32(h: u32) -> Result<u32, Error> {
    let (e, f) = (h >> 10 & 31, h & 1023);
    if e == 31 {
        return Err(why("a half infinity or NaN coordinate"));
    }
    let mag = if e == 0 { f as f32 * 2f32.powi(-24) } else { (1024 + f) as f32 * 2f32.powi(e as i32 - 25) };
    Ok(if h >> 15 != 0 { -mag } else { mag }.to_bits())
}

/// One firh result byte from the job's coefficients (E078, E079, E080): set N's kernel centred
/// on position s of the line, `at` reading a position with the edge mode applied.
fn firh_byte(c: FilterBlock, set: u32, s: i32, at: &dyn Fn(i32) -> Option<i64>) -> Result<u8, &'static str> {
    let mode = c.mode & 3;
    let filter = |taps: &[i64], from: i32, bias: (i64, i64), shift: u32| {
        let mut sum = 0;
        for (n, t) in taps.iter().enumerate() {
            let x = at(s + from + n as i32).ok_or("firh's msc or mdc past the line's end (not measured)")?;
            sum += t * x;
        }
        Ok((sat_u8((sum + bias.0) >> shift), sat_u8((sum + bias.1) >> shift)))
    };
    // a loaded group: taps at -3..+4 in its first two words (highest byte first), the shift in
    // bits 3:0 and a signed 16-bit bias in bits 19:4 of its third
    let loaded = |g: usize, only: Option<[usize; 3]>| {
        let w = c.groups.map_or([0; 3], |gs| [gs[3 * g], gs[3 * g + 1], gs[3 * g + 2]]);
        let taps: Vec<i64> = (0..8)
            .map(|n| {
                let t = (w[n / 4] >> (8 * (3 - n % 4))) as u8 as i8 as i64;
                if only.is_none_or(|o| o.contains(&n)) { t } else { 0 }
            })
            .collect();
        let bias = (w[2] >> 4) as u16 as i16 as i64;
        Ok(filter(&taps, -3, (bias, bias), w[2] & 15)?.0 as u8)
    };
    match (set, mode) {
        (0 | 1, _) => loaded(set as usize, None),
        // set 2 of the loaded block reads three taps: -3, 0 and +3 (E078)
        (2, 3) => loaded(2, Some([0, 3, 6])),
        (3..=7, 3) => Ok(0),
        // bank 0's sets 6 and 7 give 0, with a load or not; banks 1 and 2 give values whose
        // taps are not measured (usse-filter-edges-fcs67-*)
        (6 | 7, 0) => Ok(0),
        (6 | 7, _) => Err("firh's set 6 or 7 under fixed bank 1 or 2 (not measured)"),
        (_, 0) => {
            // bank 0 (E079): taps from the first position, bias range, shift.
            // fcs3's bias: 64 to 95 (video-clean x-firh-fcs3 case 14, 12192 -> 95)
            let (taps, from, bias, shift): (&[i64], i32, (i64, i64), u32) = match set {
                2 => (&[4, -20, 80, 80, -20, 4], -2, (64, 79), 7),
                3 => (&[32, 64, 32], -1, (64, 95), 7),
                4 => (&[-4, 12, -24, 80, 80, -24, 12, -4], -3, (48, 63), 7),
                _ => (&[1, -5, 20, 20, -5, 1], -2, (0, 0), 0),
            };
            match filter(taps, from, bias, shift)? {
                (lo, hi) if lo == hi => Ok(lo as u8),
                _ => Err("firh's result, which its bias (known to a range) decides"),
            }
        }
        (_, bank) => {
            let Some(&(_, _, from, shift, fam)) = FIXED_BANKS.iter().find(|f| f.0 == bank && f.1 == set)
            else {
                return Err("firh's fixed set (not measured)");
            };
            let mut got = None;
            for &(taps, lo, hi) in fam {
                let (a, z) = filter(taps, from, (lo, hi), shift)?;
                for b in [a, z] {
                    match got {
                        None => got = Some(b),
                        Some(g) if g == b => {}
                        Some(_) => {
                            return Err("firh's result, which its taps and bias (known to a range) decide");
                        }
                    }
                }
            }
            Ok(got.unwrap() as u8)
        }
    }
}

/// Byte k of a video filter's data word, read as u8 (0), s8 (1) or o8 (2, the byte minus 0x80).
fn video_byte(x: u32, k: u32, fmt: u32) -> i64 {
    let b = x >> (8 * k) & 0xff;
    match fmt {
        1 => b as u8 as i8 as i64,
        2 => b as i64 - 0x80,
        _ => b as i64,
    }
}

/// Saturated to an unsigned byte.
fn sat_u8(x: i64) -> u32 {
    x.clamp(0, 255) as u32
}

/// A read of register n of a bank: only what the task wrote is defined.
fn read(v: u32, written: u128, n: usize, bank: &str) -> Result<u32, Error> {
    if written >> n & 1 == 0 {
        return Err(why(format!("reads {bank}{n} before the program writes it")));
    }
    Ok(v)
}

/// A 16-bit lane operation takes an immediate in both lanes (hardware:
/// isub16 r4, r1, #1 subtracts 1 from each half).
fn lane_imm(field: u32, v: u32) -> u32 {
    if field >> 7 == 6 { v | v << 16 } else { v }
}

fn why(s: impl Into<String>) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: s.into() }
}

fn unsupported(pc: usize, text: &str, why: &str) -> Error {
    Error::Unsupported { pc, text: text.to_string(), why: why.to_string() }
}

fn bitwise(op: &str, a: u32, b: u32) -> Result<u32, Error> {
    Ok(match op {
        "and" => a & b,
        "or" => a | b,
        "xor" => a ^ b,
        "shl" => a.checked_shl(b).unwrap_or(0),
        "shr" => a.checked_shr(b).unwrap_or(0),
        "asr" => ((a as i32).checked_shr(b).unwrap_or(if (a as i32) < 0 { -1 } else { 0 })) as u32,
        "rol" => a.rotate_left(b & 31),
        _ => return Err(why(format!("bitwise {op}"))),
    })
}

/// What a test-group operation tests: per channel, the value the test sees, or
/// None where the operation has no lane (hardware: a 16-bit operation tests its
/// lanes at chan0 and chan2, its unwrapped signed sum).
struct Tested([Option<i64>; 4]);

/// Four byte lanes' sums (Tested), each clamped to 0-255.
fn sat_bytes(t: &Tested) -> u32 {
    (0..4).fold(0, |r, k| r | (t.0[k].unwrap_or(0).clamp(0, 255) as u32) << (8 * k))
}

fn sext16(x: u32) -> i64 {
    x as u16 as i16 as i64
}

/// a * b where it is exact (fddp's rounding is not measured), else stop
fn exact_mul(a: u32, b: u32) -> Result<u32, Error> {
    let p = flt::mul(a, b)?;
    if f32::from_bits(p) as f64 != f32::from_bits(a) as f64 * f32::from_bits(b) as f64 {
        return Err(why("fddp rounding (not measured)"));
    }
    Ok(p)
}

fn alu_test_value(op: &str, a: u32, b: u32) -> Result<(u32, Tested), Error> {
    let lanes = |f: fn(i64, i64) -> i64, signed: bool| {
        let ext = |x: u32| if signed { sext16(x) } else { (x & 0xffff) as i64 };
        let lo = f(ext(a), ext(b));
        let hi = f(ext(a >> 16), ext(b >> 16));
        ((lo as u32 & 0xffff) | (hi as u32) << 16, Tested([Some(lo), None, Some(hi), None]))
    };
    // 8-bit: four byte lanes, chanN tests byte N's unwrapped sum (hardware:
    // iadd8 of 0x80 in byte 0 tests negative at chan0, 0xffffff00 zero)
    let bytes = |f: fn(i64, i64) -> i64, signed: bool| {
        let ext = |x: u32, k: u32| {
            let v = x >> (8 * k) & 0xff;
            if signed { v as u8 as i8 as i64 } else { v as i64 }
        };
        let mut r = 0u32;
        let mut t = [None; 4];
        for k in 0..4 {
            let v = f(ext(a, k), ext(b, k));
            r |= (v as u32 & 0xff) << (8 * k);
            t[k as usize] = Some(v);
        }
        (r, Tested(t))
    };
    // 32-bit: the full result, chan0 only
    let word = |r: u32| (r, Tested([Some(r as i32 as i64), None, None, None]));
    Ok(match op {
        "iadd8" => bytes(|x, y| x + y, true),
        "isub8" => bytes(|x, y| x - y, true),
        "iadd16" => lanes(|x, y| x + y, true),
        "isub16" => lanes(|x, y| x - y, true),
        "uadd16" => lanes(|x, y| x + y, false),
        // hardware (usse-test-channels-lanes-other): the multiplies test their full
        // products, before they are cut to the lane
        "imul16" => lanes(|x, y| x * y, true),
        "umul16" => lanes(|x, y| x * y, false),
        "imul8" => bytes(|x, y| x * y, true),
        // hardware (usse-lane-integer-rogue-int): unsigned bytes, each wrapping
        "uadd8" => bytes(|x, y| x + y, false),
        "usub8" => bytes(|x, y| x - y, false),
        "umul8" => bytes(|x, y| x * y, false),
        "usub16" => lanes(|x, y| x - y, false),
        // Hardware: iadd32 adds the sign-extended low half of source 1 to source 2 (0x337a70a2 +
        // 0xb01b9c1d = 0xb01c0cbf). Its n and p tests read the sign of the true sum with source 2
        // signed, which is not the wrapped sum's when the add overflows, and its z and nz the
        // zero of the sum with source 1 sign-extended (E472, E498: 16 of 16 pairs; the true and
        // the wrapped sum never differ in zero-ness, a 16-bit and a 32-bit value not reaching 2^32).
        "iadd32" => {
            let r = (sext16(a) as u32).wrapping_add(b);
            (r, Tested([Some(sext16(a) + b as i32 as i64), None, None, None]))
        }
        // unsigned: the sign tests read nothing of the sum (p is always true, n never) and the
        // zero test counts the carry out of bit 31, so only 0 + 0 is zero (E498, 16 of 16 pairs).
        // The value written zero-extends source 1: 0x8000 + 0x8000 writes 0x10000 and 0xffff + 1
        // 0x10000 (usse-decoder-vectors-iaddu32-taz, usse-integer-iaddu32-value), which a sign
        // extension would not give; no test of the sum tells the two apart (E498).
        "iaddu32" => {
            let r = (a & 0xffff).wrapping_add(b);
            (r, Tested([Some((a & 0xffff) as i64 + b as i64), None, None, None]))
        }
        "and" | "or" | "xor" | "shl" | "shr" | "asr" | "rol" => word(bitwise(op, a, b)?),
        // hardware (usse-form-coverage-form2-test-e50 9, usse-form-coverage-form2-test-mask 11): four unsigned
        // bytes, each sum saturated, each byte its channel
        "fpadd8" => {
            let (_, t) = bytes(|x, y| x + y, false);
            (sat_bytes(&t), t)
        }
        // hardware (usse-unorm8-add-sub-mul, usse-unorm8-mul): x - y clamped at 0, and round(x * y / 255),
        // per byte; only their zero tests are measured
        "fpsub8" => {
            let (_, t) = bytes(|x, y| x - y, false);
            (sat_bytes(&t), t)
        }
        "fpmul8" => bytes(|x, y| (2 * x * y + 255) / 510, false),
        // float: the result tests by its sign and zero at chan0 (usse-test-channels-chan-tests;
        // fmax, fmin: usse-form-coverage-form2-test-e50 6, 7, usse-form-coverage-form2-test-mask 9)
        "fadd" | "fsub" | "fmul" | "fmax" | "fmin" => {
            let mut r = match op {
                "fadd" => flt::add(Ok(a), b),
                "fsub" => flt::sub(a, Ok(b)),
                "fmax" => flt::max(a, b),
                "fmin" => flt::min(a, b),
                _ => flt::mul(a, b),
            }?;
            // hardware (x-misc): fmul of 0 and -3 is +0, not IEEE's -0 (the
            // only signed-zero case measured)
            if op == "fmul" && r == 0x8000_0000 {
                r = 0;
            }
            if r == 0x8000_0000 {
                return Err(why(format!("{op} test of -0")));
            }
            if flt::special(r) || flt::special(a) || flt::special(b) {
                return Err(why(format!("{op} test of an infinity or NaN")));
            }
            let t = if r == 0 {
                0
            } else if r >> 31 != 0 {
                -1
            } else {
                1
            };
            (r, Tested([Some(t), None, None, None]))
        }
        _ => return Err(why(format!("test op {op}"))),
    })
}

/// A test type: sign test t/n/p, all (a) or any (o), zero test t/z/nz, and the
/// channel.
fn predicate(test: &str, t: Tested) -> Result<bool, Error> {
    let bad = || why(format!("test {test}"));
    let (kind, sel) = test.split_once('.').ok_or_else(bad)?;
    let kind = kind.strip_prefix("test").ok_or_else(bad)?;
    let (sign, rest) = kind.split_at(1);
    let (all, zero) = rest.split_at(1);
    // the channel selection: one channel, or several combined (andall/orall:
    // all four; and02/or02: chan0 and chan2)
    let (chans, every): (Vec<usize>, bool) = match sel {
        "andall" => ((0..4).collect(), true),
        "orall" => ((0..4).collect(), false),
        "and02" => (vec![0, 2], true),
        "or02" => (vec![0, 2], false),
        c => (vec![c.strip_prefix("chan").and_then(|n| n.parse().ok()).ok_or_else(bad)?], true),
    };
    // A channel the operation has no lane for tests as a positive non-zero
    // value (hardware: chan1 of iadd16 fails taz; andall of iadd16/iadd32
    // fails taz and nat, orall passes pat and tanz).
    let one =
        |c: usize| -> Result<bool, Error> { test_one(sign, all, zero, t.0[c].unwrap_or(1)).ok_or_else(bad) };
    let mut r = every;
    for c in chans {
        let x = one(c)?;
        r = if every { r && x } else { r || x };
    }
    Ok(r)
}

fn test_one(sign: &str, all: &str, zero: &str, v: i64) -> Option<bool> {
    let s = match sign {
        "t" => true,
        "n" => v < 0,
        "p" => v >= 0, // hardware: a zero result tests positive
        _ => return None,
    };
    let z = match zero {
        "t" => true,
        "z" => v == 0,
        "nz" => v != 0,
        _ => return None,
    };
    Some(if all == "a" { s && z } else { s || z })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn prog(src: &[&str]) -> Program {
        let words: Vec<u64> =
            src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}"))).collect();
        Program::new(&words, Core::Sgx545)
    }

    fn run(src: &[&str]) -> (Machine, Result<(), Error>) {
        let mut m = Machine::default();
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        let r = m.run(&prog(src), &mut mem, 1000);
        (m, r)
    }

    #[test]
    fn a_second_lock_of_a_held_mutex_blocks_its_holder() {
        // hardware (r7-faults stage L, E921): the counter fill with `lock #0` twice hung with the
        // counter at 0, with two releases after it or one; `lock #0` then `lock #1` ran (512)
        let (_, r) = run(&["lock #0", "release #0", "nop.end"]);
        assert!(r.is_ok(), "{r:?}");
        let (_, r) = run(&["lock #0", "lock #1", "release #1", "release #0", "nop.end"]);
        assert!(r.is_ok(), "{r:?}");
        for src in [
            &["lock #0", "lock #0", "release #0", "release #0", "nop.end"][..],
            &["lock #0", "lock #0", "release #0", "nop.end"][..],
            &["lock #3", "lock #3", "release #3", "nop.end"][..],
        ] {
            let (_, r) = run(src);
            assert!(stops_on(&r, "a second lock of a held mutex hangs the job (E921)"), "{src:?}: {r:?}");
        }
        // a release gives the mutex back (E088: the next quad takes it)
        let (_, r) = run(&["lock #0", "release #0", "lock #0", "release #0", "nop.end"]);
        assert!(r.is_ok(), "{r:?}");
        // in an EDM task (the lockup path's two `lock #0`, E890) it was not measured: refused
        let mut m = Machine { edm_task: true, ..Machine::default() };
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        let r = m.run(&prog(&["lock #0", "lock #0", "nop.end"]), &mut mem, 100);
        assert!(stops_on(&r, "not measured in an EDM task"), "{r:?}");
        let mut m = Machine { edm_task: true, ..Machine::default() };
        let r = m.run(&prog(&["lock #0", "release #0", "nop.end"]), &mut mem, 100);
        assert!(r.is_ok(), "{r:?}");
    }

    #[test]
    fn the_constant_bank_reads_the_hardware_table() {
        // usse-constant-banks-cbank: c34 is pi, c3 1.0, c28 e (Rogue's special constants, same order)
        let (m, r) = run(&["mov r1, c34", "mov r2, c3", "mov r3, c28", "mov.end o0, r1"]);
        assert!(r.is_ok(), "{r:?}");
        assert_eq!((m.r[1], m.r[2], m.r[3]), (0x4049_0fdb, 0x3f80_0000, 0x402d_f854));
        assert_eq!(CONST_BANK.len(), 64);
    }

    #[test]
    fn the_global_bank_needs_the_pixel() {
        // without a pixel position the position registers are unknown
        let (_, r) = run(&["mov r1, g23", "mov.end o0, r1"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("g23")));
    }

    /// Run `src` as vertex `v` of a draw of `total` at `per` a task; the temporaries r1.. or the refusal.
    fn vertex_run(src: &[&str], v: u32, per: u32, total: u32) -> Result<Vec<u32>, Error> {
        let p = prog(src);
        let mut m = Machine { vertex: Some((v, per, total)), ..Machine::default() };
        let mut mem = Memory { base: 0, words: vec![] };
        m.run(&p, &mut mem, 100)?;
        Ok(m.r[1..9].to_vec())
    }

    fn refused(r: Result<Vec<u32>, Error>, text: &str) -> bool {
        matches!(r, Err(Error::Unsupported { why, .. }) if why.contains(text))
    }

    #[test]
    fn the_global_bank_follows_the_vertex() {
        // hardware (11.33 q053-vtx, 126 vertices at 8 a task): vertex 13 of the draw is lane 5 of task 1
        let a = [
            "mov r1, g17",
            "mov r2, g22",
            "mov r3, g24",
            "mov r4, g25",
            "mov r5, g39",
            "mov r6, g41",
            "mov r7, g43",
            "mov r8, g26",
            "nop.end",
        ];
        assert_eq!(vertex_run(&a, 13, 8, 126).unwrap(), [1, 1, 8, 1, 4, 0xf, 0xdf00_0000, 0]);
        assert_eq!(vertex_run(&a, 0, 8, 126).unwrap()[..5], [0, 0, 0, 0, 0]);
        // vertex 30: task 3, lane 6
        assert_eq!(vertex_run(&a, 30, 8, 126).unwrap()[..5], [3, 1, 8, 2, 4]);
        // the last task at 8 a task holds 6 (vertices 120 to 125): g41 and g43 as in a full one
        assert_eq!(vertex_run(&a, 125, 8, 126).unwrap()[5..7], [0xf, 0xdf00_0000]);
        // 4 a task (q053-vtx2, held out): vertex 37 is lane 1 of task 9
        assert_eq!(vertex_run(&a, 37, 4, 126).unwrap()[..5], [1, 0, 8, 1, 0]);
        // the last task of 126 vertices at 4 a task holds 2 (vertices 124 and 125): g41 0x3, g43 0x20000000
        assert_eq!(vertex_run(&a, 125, 4, 126).unwrap()[5..7], [3, 0x2000_0000]);
        assert_eq!(vertex_run(&a, 124, 4, 126).unwrap()[5..7], [3, 0x2000_0000]);
        assert_eq!(vertex_run(&a, 123, 4, 126).unwrap()[5..7], [0xf, 0xdf00_0000]);
        // 6 a task: vertex 70 is lane 4 of task 11
        assert_eq!(vertex_run(&a, 70, 6, 126).unwrap()[..5], [3, 1, 8, 0, 4]);
        // g23 = 0x10 * (task div 2 mod 2), read from the data after the fact
        let g = ["mov r1, g23", "mov r2, g20", "mov r3, g42", "nop.end"];
        assert_eq!(vertex_run(&g, 13, 8, 126).unwrap()[..3], [0, 1, 0x3f80_0000]);
        assert_eq!(vertex_run(&g, 30, 8, 126).unwrap()[..3], [0x10, 1, 0x3f80_0000]);
        assert_eq!(vertex_run(&g, 70, 6, 126).unwrap()[0], 0x10);
        assert_eq!(vertex_run(&g, 37, 4, 126).unwrap()[0], 0);
    }

    #[test]
    fn a_vertex_task_refuses_what_was_not_measured() {
        // g18 and g21 follow the task without a rule; g19 reads by the instruction (E372); g0 to g15, g32 to
        // g38 and g44 to g63 were not read in a vertex task
        for g in [0, 5, 18, 19, 21, 32, 38, 44, 63] {
            let src = [format!("mov r1, g{g}"), "nop.end".to_string()];
            let src: Vec<&str> = src.iter().map(String::as_str).collect();
            assert!(refused(vertex_run(&src, 3, 8, 126), &format!("g{g}")), "g{g}");
        }
        // 1, 3, 5 and 7 vertices held were not seen: a draw of 5 at 4 a task would be one, but a
        // draw other than 126 vertices is refused whole
        let g = ["mov r1, g41", "nop.end"];
        assert!(refused(vertex_run(&g, 4, 4, 5), "measured only for 126"));
        // a task of other than 4, 6 or 8 vertices, a vertex past the draw
        assert!(refused(vertex_run(&g, 3, 5, 126), "at 5 a task"));
        assert!(refused(vertex_run(&g, 3, 16, 126), "at 16 a task"));
        assert!(refused(vertex_run(&g, 126, 8, 126), "vertex 126"));
        // the pixel task's constants do not leak in: g41 is 0xf, not 1, in a full task
        assert_eq!(vertex_run(&g, 3, 8, 126).unwrap()[0], 0xf);
    }

    /// R3-pixel's loop (E804, E806): E431's eight-instruction body closed by a relative `br`, the
    /// prologue's MARK xored into o0 at the end, so o0 = MARK only where the counter reached zero.
    fn mark_loop(n: u32, closing: &str) -> Vec<String> {
        let mut v = vec![
            "phas #0, #0, pixel, end, parallel".to_string(),
            format!("mov.skipinv r1, #{n}"),
            "mov.skipinv r2, #0xFFFFFFFF".to_string(),
            "mov.skipinv r3, #0x00000003".to_string(),
            format!("mov.skipinv r30, #0x{:08X}", 0xC0DE_0000u32 | n),
        ];
        v.extend((4..10).map(|d| format!("imae.u r{d}, r3.low, r3.low, r3, u32")));
        v.push("iadd32.skipinv.testtanz.chan0 r1, p0, r1, r2".to_string());
        v.push(closing.to_string());
        v.push("xor.skipinv.end o0, r1, r30".to_string());
        v
    }

    #[test]
    fn a_relative_loop_ends_with_its_mark_wherever_the_program_is_placed() {
        // hardware (E804, E806): the relative loop wrote its MARK on every pixel of a fill (code
        // index 0) and of full-target triangles whose program sits in the --tri slot (index 0x20);
        // the simulator agrees at those indices and on a higher page
        for n in [4u32, 56] {
            let src = mark_loop(n, "p0 br -#0x00000007");
            let src: Vec<&str> = src.iter().map(String::as_str).collect();
            for code_index in [0u32, 0x20, 0x1020] {
                let mut m = Machine { pixel: Some((5, 3)), code_index, ..Machine::default() };
                let mut mem = Memory { base: 0, words: vec![] };
                assert_eq!(m.run(&prog(&src), &mut mem, 2000), Ok(()), "N {n} at {code_index:#x}");
                assert_eq!(m.o[0], 0xC0DE_0000 | n, "N {n} at {code_index:#x}");
            }
        }
        // E431's absolute loop ends at index 0 (a fill: o0 = 0, E804) and is refused in the slot:
        // its ba to index 4 lands before the program (E770's void, [infer] on hardware)
        let mut src = mark_loop(4, "p0 ba #0x00000004");
        src.remove(4);
        src.pop();
        src.push("mov.skipinv.end o0, r1".to_string());
        let src: Vec<&str> = src.iter().map(String::as_str).collect();
        let mut m = Machine { pixel: Some((5, 3)), ..Machine::default() };
        let mut mem = Memory { base: 0, words: vec![] };
        assert_eq!((m.run(&prog(&src), &mut mem, 2000), m.o[0]), (Ok(()), 0));
        let mut m = Machine { pixel: Some((5, 3)), code_index: 0x20, ..Machine::default() };
        let r = m.run(&prog(&src), &mut mem, 2000);
        assert!(
            matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("before the program")),
            "{r:?}"
        );
    }

    #[test]
    fn a_triangles_pixel_task_reads_g23_g24_and_g25_and_nothing_else_of_the_bank() {
        // hardware (E808, held out): in a triangle's pixel program g23 = x mod 32, g24 = y mod 16
        // and g25 = the lane in the 2x2 quad, at the default 64x64 triangle and the full 64x64 and
        // 128x128 ones (direct reads 1.000 of 1062, 4096 and 16384 written pixels)
        let p = prog(&["mov r1, g23", "mov r2, g24", "mov r3, g25", "nop.end"]);
        for (x, y) in [(53u32, 27u32), (127, 126), (0, 0), (96, 17)] {
            let mut m = Machine { pixel: Some((x, y)), tri_pixel: true, ..Machine::default() };
            let mut mem = Memory { base: 0, words: vec![] };
            assert_eq!(m.run(&p, &mut mem, 100), Ok(()));
            assert_eq!(&m.r[1..4], &[x % 32, y % 16, (x & 1) | (y & 1) << 1], "({x}, {y})");
        }
        // the rest of the bank was read in fills only (E086): refused in a triangle's task
        for g in [17, 20, 39, 42, 7] {
            let src = [format!("mov r1, g{g}"), "nop.end".to_string()];
            let src: Vec<&str> = src.iter().map(String::as_str).collect();
            let mut m = Machine { pixel: Some((5, 3)), tri_pixel: true, ..Machine::default() };
            let mut mem = Memory { base: 0, words: vec![] };
            let r = m.run(&prog(&src), &mut mem, 100);
            assert!(
                matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("triangle")),
                "g{g}: {r:?}"
            );
        }
    }

    #[test]
    fn a_triangles_pixel_task_writing_o1_or_reading_o4_up_is_refused_by_q276() {
        // hardware (Q276, Q023): in a triangle's pixel task the words of o1 to o3 land at other
        // pixels under g25 predicates (E742, E759, E772), o4 brings out OR(o0, o3) of a lane
        // chosen by the job (E709, E838, E850, E858, E880), o4 to o7's own words reach no pixel
        // (E871) and a read of o4 to o7 reads o(r mod 4) (E878, E905): no per-pixel machine
        // holds this, so only o0 is written and o0 to o3 read
        let run = |src: &[&str]| {
            let mut m = Machine { pixel: Some((5, 3)), tri_pixel: true, ..Machine::default() };
            let mut mem = Memory { base: 0, words: vec![] };
            let r = m.run(&prog(src), &mut mem, 100);
            (r, m.o[0])
        };
        for src in [
            &["mov r1, #7", "mov.skipinv o1, r1", "mov.skipinv.end o0, r1"][..],
            &["mov r1, #7", "mov o7, r1", "mov.skipinv.end o0, r1"],
            &["mov r1, #7", "mov.skipinv o0, r1", "mov r2, o5", "mov.skipinv.end o0, r2"],
            &["mov r1, #7", "mov.skipinv o0, r1", "or r2, r1, o6", "mov.skipinv.end o0, r2"],
        ] {
            let (r, _) = run(src);
            assert!(
                matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("Q276")),
                "{src:?}: {r:?}"
            );
        }
        // o0 is written and read back as before
        let ok = ["mov r1, #7", "mov.skipinv o0, r1", "mov r2, o0", "mov.skipinv.end o0, r2"];
        assert_eq!(run(&ok), (Ok(()), 7));
        // a fill's pixel task keeps every output (E570's output room is a triangle's)
        let mut m = Machine { pixel: Some((5, 3)), ..Machine::default() };
        let mut mem = Memory { base: 0, words: vec![] };
        let fill = ["mov r1, #7", "mov.skipinv o1, r1", "mov r2, o1", "mov.skipinv.end o0, r2"];
        assert_eq!((m.run(&prog(&fill), &mut mem, 100), m.o[0]), (Ok(()), 7));
    }

    #[test]
    fn the_global_bank_follows_the_pixel() {
        // hardware (usse-constant-banks-gbank-pixels, E086), at pixel (x, y) = (53, 27) of a fill
        let p = prog(&[
            "mov r1, g23",
            "mov r2, g24",
            "mov r3, g25",
            "mov r4, g39",
            "mov r5, g17",
            "mov r6, g20",
            "mov r7, g42",
            "mov r8, g7",
            "nop.end",
        ]);
        let mut m = Machine { pixel: Some((53, 27)), ..Machine::default() };
        let mut mem = Memory { base: 0, words: vec![] };
        assert!(m.run(&p, &mut mem, 100).is_ok());
        assert_eq!(&m.r[1..9], &[21, 11, 3, 8, 3, 1, 0x3f80_0000, 0]);
        let p = prog(&["mov r1, g21", "nop.end"]);
        let mut m = Machine { pixel: Some((1, 1)), ..Machine::default() };
        let r = m.run(&p, &mut mem, 100);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("g21")));
    }

    #[test]
    fn br_counts_from_the_branch_itself() {
        // br #1 is the next instruction: the or still runs
        let (m, r) =
            run(&["mov r1, #0x00000000", "br #0x00000001", "or r1, r1, #0x00000001", "mov.end o0, r1"]);
        assert_eq!((r, m.o[0]), (Ok(()), 1));
        let (m, r) =
            run(&["mov r1, #0x00000000", "br #0x00000002", "or r1, r1, #0x00000001", "mov.end o0, r1"]);
        assert_eq!((r, m.o[0]), (Ok(()), 0));
    }

    #[test]
    fn what_the_task_did_not_write_stops_it() {
        let (_, r) = run(&["mov.end o0, r5"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("r5 before")));
        let (_, r) = run(&["mov i3, r1"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })));
    }

    #[test]
    fn drc_results_land_at_wdf() {
        let div = ["mov r1, #0x00000064", "mov r2, #0x00000007", "idiv r10, r1, r2, drc0"];
        let (_, r) = run(&[div[0], div[1], div[2], "mov.end o0, r10"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("DRC")));
        let (m, r) = run(&[div[0], div[1], div[2], "wdf drc0", "mov.end o0, r11"]);
        assert_eq!((r, m.r[10], m.o[0]), (Ok(()), 14, 2));
    }

    /// SGX registers as a map, logging the accesses.
    struct Regs(std::collections::BTreeMap<u32, u32>, Vec<String>);

    impl Bus for Regs {
        fn load32(&mut self, a: u32) -> Result<u32, Error> {
            Err(Error::Fault(a))
        }
        fn store32(&mut self, a: u32, _: u32) -> Result<(), Error> {
            Err(Error::Fault(a))
        }
        fn reg_read(&mut self, i: u32) -> Result<u32, Error> {
            self.1.push(format!("ldr {i}"));
            Ok(*self.0.get(&i).unwrap_or(&0))
        }
        fn reg_write(&mut self, i: u32, v: u32) -> Result<(), Error> {
            self.1.push(format!("str {i} {v:#x}"));
            self.0.insert(i, v);
            Ok(())
        }
        fn emit(&mut self, text: &str, srcs: [u32; 3]) -> Result<(), Error> {
            self.1.push(format!("{text} {srcs:x?}"));
            Ok(())
        }
    }

    #[test]
    fn emits_hand_their_sources_to_the_bus() {
        let p = prog(&[
            "mov r0, #0x00000011",
            "mov r1, #0x00000022",
            "emitpix1.freep #0 /* incp */, r0, r1",
            "emitpix2.end.freep #0 /* incp */, r1, r0, r0, #0x00000200",
        ]);
        let mut bus = Regs(Default::default(), vec![]);
        let mut m = Machine::default();
        assert_eq!(m.run(&p, &mut bus, 100), Ok(()));
        assert_eq!(bus.1.len(), 2);
        assert!(bus.1[0].starts_with("emitpix1") && bus.1[0].ends_with("[11, 22, 0]"), "{:?}", bus.1);
        assert!(bus.1[1].ends_with("[22, 11, 11]"), "{:?}", bus.1);
    }

    #[test]
    fn calls_return_through_the_link() {
        // 0: call 3; 1: r1 |= 2; 2: end; 3: r1 = 1; 4: return
        let (m, r) = run(&[
            "ba.savelink #0x00000003",
            "or r1, r1, #0x00000002",
            "mov.end o0, r1",
            "mov r1, #0x00000001",
            "lapc",
        ]);
        assert_eq!((r, m.o[0]), (Ok(()), 3));
        // the link moves through a register and back
        let (m, r) = run(&[
            "ba.savelink #0x00000002",
            "mov.end o0, r1",
            "mov r5, pclink",
            "mov pclink, r5",
            "mov r1, #0x00000007",
            "lapc",
        ]);
        assert_eq!((r, m.o[0]), (Ok(()), 7));
    }

    #[test]
    fn bexception_branches_as_ba_and_br() {
        // hardware (bexc2, E108): its target jumps to that instruction, with bit 38 by
        // that offset, under the predicate; 0: target 3; 1-2: fall-through; 3: the target
        let (m, r) = run(&[
            "bexception #0x00000003",
            "mov r1, #0x0000000B",
            "mov.end o0, r1",
            "mov.end o0, #0x0000000D",
        ]);
        assert_eq!((r, m.o[0]), (Ok(()), 0x0d));
        let (m, r) = run(&[
            "bexception.rel #0x00000003",
            "mov r1, #0x0000000B",
            "mov.end o0, r1",
            "mov.end o0, #0x0000000D",
        ]);
        assert_eq!((r, m.o[0]), (Ok(()), 0x0d));
        // p0 false (set by a test, as the hardware's p0 must be): falls through
        let (m, r) = run(&[
            "mov r7, #0",
            "and.testtanz.chan0 !c0, p0, r7, r7",
            "p0 bexception #0x00000005",
            "mov r1, #0x0000000B",
            "mov.end o0, r1",
            "mov.end o0, #0x0000000D",
        ]);
        assert_eq!((r, m.o[0]), (Ok(()), 0x0b));
        // p0 not set by the program: its value is the job before's, so the program stops (E477)
        let (_, r) =
            run(&["p0 bexception #0x00000003", "mov.end o0, #0x0000000B", "mov.end o0, #0x0000000D"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
    }

    #[test]
    fn ldr_and_str_reach_the_sgx_registers() {
        let p =
            prog(&["mov r1, #0x00000005", "str #10, r1", "ldr r2, #10, drc0", "wdf drc0", "mov.end o0, r2"]);
        let mut bus = Regs(Default::default(), vec![]);
        let mut m = Machine::default();
        assert_eq!(m.run(&p, &mut bus, 100), Ok(()));
        assert_eq!((m.o[0], bus.1), (5, vec!["str 10 0x5".to_string(), "ldr 10".to_string()]));
    }

    const R1_R7: [&str; 7] = [
        "mov r1, #0x00000011",
        "mov r2, #0x00000022",
        "mov r3, #0x00000033",
        "mov r4, #0x00000044",
        "mov r5, #0x00000055",
        "mov r6, #0x00000066",
        "mov r7, #0x00000077",
    ];

    fn run_after(init: &[&str], src: &[&str]) -> (Machine, Result<(), Error>) {
        run(&[init, src, &["nop.end"]].concat())
    }

    #[test]
    fn smp_samples_through_the_bus_at_the_fence() {
        // a 4x4 B8G8R8A8 stride texture at 0x1000 whose dwords count up
        let src = |smp: &str| {
            prog(&[
                "mov r20, #0x00000600",
                "mov r21, #0xcc003003",
                "mov r22, #0x00001000",
                "mov r23, #0x00000000",
                "mov r24, #0x3f19999a",
                "mov r25, #0x3e99999a",
                smp,
                "wdf drc0",
                "mov.end o0, r10",
            ])
        };
        let mut mem = Memory { base: 0x1000, words: (0..64).map(|i| 0x100 + i).collect() };
        let mut m = Machine::default();
        // (0.6, 0.3): texel (2, 1), dword 4 + 2
        assert_eq!(m.run(&src("smp2d r10, r24, r20, drc0"), &mut mem, 100), Ok(()));
        assert_eq!(m.o[0], 0x106);
        // the result is not there before the fence
        let p = prog(&[
            "mov r20, #0x00000600",
            "mov r21, #0xcc003003",
            "mov r22, #0x00001000",
            "mov r23, #0x00000000",
            "mov r24, #0x3f19999a",
            "mov r25, #0x3e99999a",
            "smp2d r10, r24, r20, drc0",
            "mov.end o0, r10",
        ]);
        let r = Machine::default().run(&p, &mut mem, 100);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
        // a bus without a texture unit stops it
        struct NoTex;
        impl Bus for NoTex {
            fn load32(&mut self, _: u32) -> Result<u32, Error> {
                Ok(0)
            }
            fn store32(&mut self, _: u32, _: u32) -> Result<(), Error> {
                Ok(())
            }
        }
        let r = Machine::default().run(&src("smp2d r10, r24, r20, drc0"), &mut NoTex, 100);
        assert!(matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("texture unit")), "{r:?}");
    }

    #[test]
    fn an_srgb_sample_leaves_its_second_register_unknown() {
        // E723: the first register is the decode of bytes 0 and 1; the second (its r11 reads) has
        // no model, so a read of it after the fence stops; a twiddled 8 x 8 format 12 texture
        let st = [0x0ffe_0000u32, 0x0c00_7007, 0x1000, 0x0080_0800];
        let src = |last: &str| {
            let mut v: Vec<String> =
                st.iter().enumerate().map(|(k, w)| format!("mov r{}, #0x{w:08x}", 20 + k)).collect();
            v.extend(
                [
                    "mov r24, #0x3f19999a",
                    "mov r25, #0x3e99999a",
                    "mov r11, #1",
                    "smp2d r10, r24, r20, drc0",
                    "wdf drc0",
                    last,
                ]
                .map(String::from),
            );
            v
        };
        let mut mem = Memory { base: 0x1000, words: (0..64).map(|i| 0x100 + i).collect() };
        let want = tex::sample(
            &tex::Sample {
                state: st,
                u: f32::from_bits(0x3f19999a),
                v: f32::from_bits(0x3e99999a),
                one_d: false,
                srd: tex::Srd::None,
                pcf: None,
                lod: tex::Lod::Flat,
            },
            &mut |a| Ok(0x100 + (a - 0x1000) / 4),
        )
        .unwrap();
        assert_eq!(want.len(), 1);
        let first = src("mov.end o0, r10");
        let mut m = Machine::default();
        let r = m.run(&prog(&first.iter().map(|s| s.as_str()).collect::<Vec<_>>()), &mut mem, 100);
        assert_eq!((r, m.o[0]), (Ok(()), want[0]));
        let second = src("mov.end o0, r11");
        let r = Machine::default().run(
            &prog(&second.iter().map(|s| s.as_str()).collect::<Vec<_>>()),
            &mut mem,
            100,
        );
        assert!(matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("E723")), "{r:?}");
    }

    /// Run `smp` over a counting texture at 0x1000 with the state words `t` and a third
    /// coordinate `w`; o0 is the texel read.
    fn run_smp(t: [u32; 4], w: u32, smp: &str) -> Result<u32, Error> {
        let words = [
            format!("mov r20, #0x{:08x}", t[0]),
            format!("mov r21, #0x{:08x}", t[1]),
            format!("mov r22, #0x{:08x}", t[2]),
            format!("mov r23, #0x{:08x}", t[3]),
            "mov r24, #0x3f19999a".to_string(),
            "mov r25, #0x3e99999a".to_string(),
            format!("mov r26, #0x{w:08x}"),
            smp.to_string(),
            "wdf drc0".to_string(),
            "mov.end o0, r10".to_string(),
        ];
        let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
        let mut mem = Memory { base: 0x1000, words: (0..4096).map(|i| 0x100 + i).collect() };
        let mut m = Machine::default();
        m.run(&prog(&refs), &mut mem, 100).map(|()| m.o[0])
    }

    fn why_of(r: Result<u32, Error>) -> String {
        match r {
            Err(Error::Unsupported { why, .. }) => why,
            other => format!("not a stop: {other:?}"),
        }
    }

    /// The state words of the smp3d jobs that ran (p1132 tx-types, tx-types-risky): T0, T1, T2, T3.
    const TW16: [u32; 4] = [0x07fe_0000, 0x0c00_f00f, 0x1000, 0x0080_0800];
    const ST64X32: [u32; 4] = [0x000e_0e00, 0xcc03_f01f, 0x1000, 0xa080_0000];

    #[test]
    fn smp3d_reads_as_smp2d_only_where_it_ran() {
        // p1132 tx-types, tx-types-risky (cube maps E844, Q114): point sampled, level 0, a 16x16
        // twiddled texture (TEXTYPE 0 and 7) and a 64x32 stride one, format 12: smp3d at a third
        // coordinate of -0.5, 0, 0.5, 1, 1.5 and 4 gave the smp2d image (0 of 2048 pixels
        // differ in the 8 fit jobs, the 3 sweeps and rt7 at 0.5 and 1.5)
        let w3 = |w: f32| w.to_bits();
        // (0.6, 0.3): twiddled texel (9, 4), dword 0x92; stride texel (38, 9), dword 9 * 64 + 38
        for w in [-0.5, 0.0, 0.5, 1.0, 1.5, 4.0] {
            assert_eq!(run_smp(TW16, w3(w), "smp3d r10, r24, r20, drc0"), Ok(0x192), "twiddled w {w}");
            assert_eq!(run_smp(ST64X32, w3(w), "smp3d r10, r24, r20, drc0"), Ok(0x366), "stride w {w}");
        }
        let mut t7 = TW16;
        t7[1] |= 7 << 29;
        assert_eq!(run_smp(t7, w3(0.5), "smp3d r10, r24, r20, drc0"), Ok(0x192), "TEXTYPE 7");
        assert_eq!(run_smp(TW16, 0, "smp2d r10, r24, r20, drc0"), Ok(0x192));
    }

    #[test]
    fn smp3d_stops_off_what_ran() {
        let w = 0.5f32.to_bits();
        let go = |t: [u32; 4], smp: &str| why_of(run_smp(t, w, smp));
        // TEXTYPE 2 is the one type on which the third coordinate acts (E567): the smp3d rule
        // itself refuses it, as it does types 1, 3, 4 and 5 (not run with a model)
        for ty in [1u32, 2, 3, 4, 5] {
            let mut t = TW16;
            t[1] |= ty << 29;
            let why = go(t, "smp3d r10, r24, r20, drc0");
            assert!(why.contains("smp3d") && why.contains(&format!("TEXTYPE {ty}")), "type {ty}: {why}");
        }
        // another size, another format, a bilinear filter, a chain, another T3: not run
        let mut t = TW16;
        t[1] = 0x0c01_f00f; // 32x16
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "another size");
        let mut t = TW16;
        t[1] = 4 << 24 | 0xf00f; // format 4
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "another format");
        let mut t = TW16;
        t[0] |= 1 << 12; // magnifying filter 1: bilinear
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "bilinear");
        let mut t = TW16;
        t[0] = 0x07fc_0000; // the chain enabled
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "a chain");
        let mut t = TW16;
        t[3] ^= 1 << 8;
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "another T3");
        let mut t = ST64X32;
        t[1] = 0xcc00_f00f; // a 16x16 stride texture
        assert!(go(t, "smp3d r10, r24, r20, drc0").contains("smp3d"), "a stride texture of another size");
    }

    #[test]
    fn the_yuv_formats_stop_unless_the_set_is_known_to_be_unloaded() {
        // E037 measures the BT.601 conversion when a copy loads the set; the fills of p1132
        // read black (E568) through a dangling poke set; a fill's transfer command loads the set
        // too, and a job without the load reads the last loaded set (E1103). A vector that does
        // not say the set is unloaded is not modelled.
        let go = |unloaded: bool| {
            let words = [
                "mov r20, #0x000e0e00".to_string(),
                format!("mov r21, #0x{:08x}", 6u32 << 29 | 29 << 24 | 63 << 12 | 31),
                "mov r22, #0x00001000".to_string(),
                "mov r23, #0xa0800000".to_string(),
                "mov r24, #0x3f19999a".to_string(),
                "mov r25, #0x3e99999a".to_string(),
                "smp2d r10, r24, r20, drc0".to_string(),
                "wdf drc0".to_string(),
                "mov.end o0, r10".to_string(),
            ];
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let mut mem = Memory { base: 0x1000, words: (0..4096).map(|i| 0x100 + i).collect() };
            let mut m = Machine { csc_unloaded: unloaded, ..Machine::default() };
            m.run(&prog(&refs), &mut mem, 100).map(|()| m.o[0])
        };
        let why = why_of(go(false));
        assert!(why.contains("colour-space set"), "{why}");
        assert_eq!(go(true), Ok(0xff00_0000));
    }

    #[test]
    fn float_functions_give_near_values_only_when_asked() {
        use crate::func::Bound;
        let src = |x: &str| {
            prog(&[
                "mov r1, #0x40800000",
                "mov r3, #0x40400000",
                "mov r6, #0x00000000",
                "mov r7, #0x00001000",
                x,
                "mov r4, r2",
                "fmad r5, r2, r1, r6",
                "stad [r7,+#0], r4",
                "stad [r7,+#1], r5",
                "nop.end",
            ])
        };
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        // frcp of 4 is exact, of 3 within one ulp: refused unless near
        let mut m = Machine::default();
        assert_eq!(m.run(&src("frcp r2, r1"), &mut mem, 100), Ok(()));
        assert_eq!((m.r[4], mem.words[0]), (0x3e80_0000, 0x3e80_0000));
        assert!(m.bounds.is_empty() && m.near_mem.is_empty());
        let mut m = Machine::default();
        let r = m.run(&src("frcp r2, r3"), &mut mem, 100);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
        // near: the nearest value; a move keeps its bound, anything else
        // computed from it has none
        let mut m = Machine { near: true, ..Machine::default() };
        assert_eq!(m.run(&src("frcp r2, r3.neg"), &mut mem, 100), Ok(()));
        assert_eq!(m.r[2], 0xbeaa_aaab);
        assert_eq!(m.near_mem.get(&0x1000), Some(&Bound::Ulps(1)));
        assert_eq!(m.near_mem.get(&0x1004), Some(&Bound::Derived));
        assert_eq!(m.bounds.get(&("r", 2)), Some(&Bound::Ulps(1)));
        assert_eq!(m.bounds.get(&("r", 4)), Some(&Bound::Ulps(1)));
        assert_eq!(m.bounds.get(&("r", 5)), Some(&Bound::Derived));
        assert_eq!(m.bounds.get(&("r", 1)), None);
    }

    #[test]
    fn fadm_rounds_both_products_then_the_sum() {
        // hardware (usse-float-misc-fadm-fmsa-fsubflr): a*c + b*c; one rounding of (a + b)*c
        // would give 0x4070d8a5
        let (m, r) = run_after(
            &["mov r1, #0x3fd36766", "mov r2, #0x3fe4f4e3", "mov r3, #0x3f8c0397"],
            &["fadm r4, r1, r2, r3"],
        );
        assert_eq!((r, m.r[4]), (Ok(()), 0x4070_d8a4));
    }

    #[test]
    fn the_integer_multiply_add_formats_and_carries() {
        let m = |init: &[&str], src: &str| {
            let (m, r) = run_after(init, &[src]);
            assert_eq!(r, Ok(()), "{src}");
            m
        };
        // hardware (usse-integer-ima16-8bit): per lane a * b + c, b the high byte as s8,
        // c the low byte as o8
        let i = ["mov r1, #0x82ff0381", "mov r2, #0x7f05fe02", "mov r3, #0x00100020"];
        assert_eq!(m(&i, "ima16.u r10, r1, r2.high, r3.low, s8, o8").r[10], 0xfc11f89e);
        // hardware (ima8): x + y * z per byte, clamped with .sat
        let i = ["mov r1, #0x80ff10f0", "mov r2, #0x10200302", "mov r3, #0x10101080"];
        assert_eq!(m(&i, "ima8.sat r10, r1, r2, r3, s0, s1, s2, s0a, s1a, s2a").r[10], 0xffff40ff);
        let src = "ima8 r10, r1, r2, r3, s0.comp, s1, s2, s0a.comp, s1a, s2a";
        assert_eq!(m(&i, src).r[10], 0x7f001f0f);
        // hardware (usse-integer-imae-modes): z16 zero-extends; coe writes the carry out
        let i = ["mov r1, #0xffff0003", "mov r2, #0xffff0005", "mov r3, #0xfffffff0"];
        assert_eq!(m(&i, "imae.u r10, r1.low, r2.low, r3.high, z16").r[10], 0x0001000e);
        let x = m(&i, "imae.u r10, r1.high, r2.high, r3, u32, coe, i0");
        assert_eq!((x.r[10], x.i[0]), (0xfffdfff1, 1));
        // ima32's cie adds iN
        let i = ["mov r1, #0xfffffff0", "mov r2, #0xffff0005", "mov r3, #0xffffffff", "mov i0, #0x00000001"];
        assert_eq!(m(&i, "ima32.u r10, r1, r2, r3, cie, i0").r[10], 0x000fffb0);
    }

    #[test]
    fn writes_of_i3_to_i7_are_dropped() {
        // hardware (usse-internal-registers-mov-and-tasks, usse-internal-registers-bank7): no
        // instance's i0-i2 change, so one instance alone drops them too
        let (m, r) = run_after(&["mov i0, #0x00000005"], &["mov i3, #0x00000001", "mov i7, #0x00000002"]);
        assert_eq!((r, m.i[0], m.written.i), (Ok(()), 5, 1));
        assert!(run_after(&[], &["mov i8, #0x00000001"]).1.is_err());
    }

    #[test]
    fn pn_never_runs() {
        // hardware (usse-predicates-predicate-pn): whatever p0-p3 hold
        let (m, r) = run_after(&["mov r2, #0x00000005"], &["Pn mov r2, #0x00000001"]);
        assert_eq!((r, m.r[2]), (Ok(()), 5));
    }

    #[test]
    fn only_measured_tests_and_flags_run() {
        let i = ["mov r1, #0x00000005", "mov r2, #0x00000003"];
        // hardware (usse-decoder-vectors-usub16-taz, usse-lane-integer-rogue-int): the zero tests of usub16
        // and the unsigned 8-bit operations; their sign tests are not measured
        assert_eq!(run_after(&i, &["usub16.testtaz.chan0 r10, p0, r1, r2"]).1, Ok(()));
        assert_eq!(run_after(&i, &["uadd8.testtaz.chan0 r10, p0, r1, r2"]).1, Ok(()));
        for t in ["usub16.testnaz.chan0 r10, p0, r1, r2", "uadd8.testnaz.chan0 r10, p0, r1, r2"] {
            assert!(matches!(run_after(&i, &[t]).1, Err(Error::Unsupported { .. })), "{t}");
        }
        // hardware (usse-flags-other): .tpres and .partial change nothing a pixel sees
        let i = ["mov r1, #0x40800000"];
        let (m, r) = run_after(&i, &["frcp.tpres r2, r1", "and.partial r3, r1, r1"]);
        assert_eq!((r, m.r[2], m.r[3]), (Ok(()), 0x3e80_0000, 0x4080_0000));
    }

    #[test]
    fn repeats_run_one_iteration_after_another() {
        // hardware (usse-repeat-order): mov.repeat3 r2, r1 copies r1 into r2-r4
        let (m, r) = run_after(&R1_R7, &["mov.repeat3 r2, r1"]);
        assert_eq!((r, &m.r[1..5]), (Ok(()), &[0x11; 4][..]));
        let (m, r) = run_after(&R1_R7, &["mov.repeat3 r1, r2"]);
        assert_eq!((r, &m.r[1..5]), (Ok(()), &[0x22, 0x33, 0x44, 0x44][..]));
    }

    #[test]
    fn a_repeat_is_predicated_once() {
        // hardware (usse-repeat-pred): both iterations or neither
        let (m, r) = run_after(&R1_R7, &["mov r10, #0x00000001", "and.testtaz.chan0 !c0, p0, r10, r10"]);
        assert_eq!(r, Ok(()));
        let p = m.p;
        let (m, r) = run_after(
            &R1_R7,
            &["mov r10, #0x00000000", "and.testtaz.chan0 !c0, p0, r10, r10", "p0 mov.repeat2 r1, r5"],
        );
        assert_eq!((r, p[0], &m.r[1..4]), (Ok(()), false, &[0x55, 0x66, 0x33][..]));
    }

    const ABC: [&str; 6] = [
        "mov r1, #0x3f800000", // 1
        "mov r2, #0x40400000", // 3
        "mov r3, #0x40a00000", // 5
        "mov r4, #0x40e00000", // 7
        "mov r5, #0x42c80000", // 100
        "mov r6, #0x43480000", // 200
    ];

    #[test]
    fn incs_picks_the_sources_that_advance() {
        // hardware (usse-write-masks-incs-fmad): .incsXYZ advances source 0, 1, 2; the
        // destination always advances; no .incs advances every source
        for (incs, second) in [("", 221.0), (".incs000", 105.0), (".incs100", 115.0), (".incs010", 107.0)]
            .into_iter()
            .chain([(".incs001", 205.0), (".incs110", 121.0), (".incs111", 221.0)])
        {
            let (m, r) = run_after(&ABC, &[&format!("fmad.repeat2{incs} r10, r1, r3, r5")]);
            assert_eq!(
                (r, m.r[10], m.r[11]),
                (Ok(()), 105f32.to_bits(), (second as f32).to_bits()),
                "{incs}"
            );
        }
    }

    #[test]
    fn fdp_sums_its_products_in_turn() {
        // hardware (usse-dot-products-fdp-count): fdp.repeatN d, a, b sums a[k] * b[k] into
        // d + N - 1 only
        let (m, r) = run_after(&ABC, &["fdp.repeat3 r10, r1, r4"]);
        assert_eq!((r, m.r[12], m.written.r >> 10 & 7), (Ok(()), 1307f32.to_bits(), 0b100));
        let (m, r) = run_after(&ABC, &["fdp.repeat2.incs010 r10, r1, r4"]);
        assert_eq!((r, m.r[11]), (Ok(()), 28f32.to_bits()));
        // usse-dot-products-fdp-rounding: each product and each sum rounded, in order, so
        // 1 + 2^-24 - 1 + 2^-24 is 2^-24
        let (m, r) = run_after(
            &[
                "mov r1, #0x3f800000",
                "mov r2, #0x33800000",
                "mov r3, #0x3f800000",
                "mov r4, #0x33800000",
                "mov r5, #0x3f800000",
                "mov r6, #0x3f800000",
                "mov r7, #0xbf800000",
                "mov r8, #0x3f800000",
            ],
            &["fdp.repeat4 r10, r1, r5"],
        );
        assert_eq!((r, m.r[13]), (Ok(()), 0x33800000));
    }

    #[test]
    fn float_tests_read_the_result_as_a_float() {
        // hardware (usse-test-channels-chan-tests): fadd tests its float result at chan0;
        // other channels test as positive non-zero
        let t = |op: &str, a: &str, b: &str| {
            let (m, r) = run_after(&[&format!("mov r1, #{a}"), &format!("mov r2, #{b}")], &[op]);
            r.map(|_| m.p[0])
        };
        let (two, three, zero) = ("0x40000000", "0x40400000", "0x00000000");
        assert_eq!(t("fadd.testnat.chan0 !c0, p0, r1, r2", "0xc0000000", zero), Ok(true));
        assert_eq!(t("fadd.testnat.chan0 !c0, p0, r1, r2", three, zero), Ok(false));
        assert_eq!(t("fadd.testtaz.chan0 !c0, p0, r1, r2", zero, zero), Ok(true));
        assert_eq!(t("fadd.testpat.chan1 !c0, p0, r1, r2", "0xc0000000", zero), Ok(true));
        assert_eq!(t("fadd.testtaz.chan0 r3, p0, r1, r2", two, three), Ok(false));
        // x-misc: fmul of 0 and -3 is +0, and tests zero
        let (m, r) = run_after(
            &["mov r1, #0x00000000", "mov r2, #0xc0400000"],
            &["fmul.testtaz.chan0 r3, p0, r1, r2"],
        );
        assert_eq!((r, m.r[3], m.p[0]), (Ok(()), 0, true));
        // fadd's -0 is not measured
        assert!(t("fadd.testtaz.chan0 !c0, p0, r1, r2", "0x80000000", "0x80000000").is_err());
    }

    #[test]
    fn unpacks_to_f32_scale_each_component() {
        let u = |op: &str, w: &str| {
            let (m, r) = run_after(&[&format!("mov r1, #{w}")], &[&format!("{op}, r1.0, nearest")]);
            r.map(|_| m.r[10])
        };
        let f = |x: f32| Ok(x.to_bits());
        // hardware (unpack-*-scale): u8 / 255, s8 / 127 clamped at -1, o8 is
        // s8 of the byte ^ 0x80, each rounded once to nearest
        assert_eq!(u("unpckf32u8.scale r10, r1.1", "0x00000100"), Ok(0x3b808081));
        assert_eq!(u("unpckf32s8.scale r10, r1.0", "0x00000080"), f(-1.0));
        assert_eq!(u("unpckf32s8.scale r10, r1.0", "0x00000001"), Ok(0x3c010204));
        assert_eq!(u("unpckf32o8.scale r10, r1.0", "0x00000008"), f(-120.0 / 127.0));
        assert_eq!(u("unpckf32s16.scale r10, r1.2", "0x80000000"), f(-1.0));
        assert_eq!(u("unpckf32u16.scale r10, r1.2", "0x00010000"), Ok(0x37800080));
        // usse-pack-unpack-select: without .scale the integer; a 16-bit select is a
        // byte offset
        assert_eq!(u("unpckf32u8 r10, r1.3", "0x84838281"), f(132.0));
        assert_eq!(u("unpckf32u16 r10, r1.1", "0x84838281"), f(33666.0));
        // .3 of a 16-bit format reads nothing
        assert_eq!(u("unpckf32u16 r10, r1.3", "0x84838281"), f(0.0));
        assert_eq!(u("unpckf32s16.scale r10, r1.3", "0x84838281"), f(0.0));
        assert_eq!(u("unpckf32f16 r10, r1.3", "0x84838281"), f(0.0));
        assert!(u("unpckf32u8.scale r10.e0.e1, r1.0", "0x00000001").is_err());
    }

    #[test]
    fn packs_round_saturate_and_place_their_two_values() {
        let pk = |op: &str, a: f32, b: f32| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", a.to_bits()),
                    &format!("mov r2, #0x{:08x}", b.to_bits()),
                    "mov r10, #0xa0a1a2a3",
                ],
                &[op],
            );
            r.map(|_| m.r[10])
        };
        // pack-*-int: rounded by the mode, saturated; 8-bit values go to bytes
        // 0-3 as s1, s2, s1, s2, 16-bit ones to the low and high halves
        assert_eq!(pk("pcku8f32 r10, r1.0, r2.0, nearest", 300.0, -5.0), Ok(0x00ff00ff));
        assert_eq!(pk("pcko8f32 r10, r1.0, r2.0, nearest", 300.0, -5.0), Ok(0x7bff7bff));
        assert_eq!(pk("pcks16f32 r10, r1.0, r2.0, nearest", -300.0, 5.0), Ok(0x0005fed4));
        // pack-round-*: nearest even, down, up, zero
        assert_eq!(pk("pcks8f32 r10, r1.0, r2.0, nearest", 2.5, -3.5), Ok(0xfc02fc02));
        assert_eq!(pk("pcks8f32 r10, r1.0, r2.0, down", 2.5, -2.5), Ok(0xfd02fd02));
        assert_eq!(pk("pcks8f32 r10, r1.0, r2.0, up", 2.4, -2.6), Ok(0xfe03fe03));
        assert_eq!(pk("pcks8f32 r10, r1.0, r2.0, zero", 3.5, -3.5), Ok(0xfd03fd03));
        // pack-*-scale: x * K rounded once to nearest whatever the mode; s8
        // saturates at -127
        assert_eq!(pk("pcku8f32.scale r10, r1.0, r2.0, down", 0.5, 0.3), Ok(0x4d804d80));
        assert_eq!(pk("pcks8f32.scale r10, r1.0, r2.0, nearest", 0.75, -1.5), Ok(0x815f815f));
        assert_eq!(pk("pcku16f32.scale r10, r1.0, r2.0, nearest", 0.3, -1.0), Ok(0x00004ccd));
        // ties to even: -0.5 * 127 is -63.5, so -64
        assert_eq!(pk("pcks8f32.scale r10, r1.0, r2.0, nearest", -0.5, 0.0), Ok(0x00c000c0));
        // usse-pack-u8-bytemask / usse-pack-u16-bytemask
        assert_eq!(pk("pcku8f32 r10.e0.e2.e3, r1.0, r2.0, nearest", 1.0, 2.0), Ok(0x0202a201));
        assert_eq!(pk("pcku8f32 r10.e0.e1.e2, r1.0, r2.0, nearest", 1.0, 2.0), Ok(0xa0010201));
        assert_eq!(pk("pcku16f32 r10.e1.e2.e3, r1.0, r2.0, nearest", 258.0, 772.0), Ok(0x010201a3));
        assert_eq!(pk("pcku16f32 r10.e0.e3, r1.0, r2.0, nearest", 258.0, 772.0), Ok(0x03a1a202));
    }

    const POW2: [&str; 8] = [
        "mov r1, #0x3f800000", // 1
        "mov r2, #0x40000000", // 2
        "mov r3, #0x40800000", // 4
        "mov r4, #0x41000000", // 8
        "mov r5, #0x41800000", // 16
        "mov r6, #0x42000000", // 32
        "mov r7, #0x42800000", // 64
        "mov r8, #0x43000000", // 128
    ];

    #[test]
    fn the_double_dot_products_write_d_and_an_internal() {
        // hardware (fddp): s0 . s1 into d + N - 1, s0 . s2 into iN
        let (m, r) = run_after(&POW2, &["fddp.repeat2 r10, i1, r5, r1, r3"]);
        assert_eq!((r, m.r[11], m.i[1]), (Ok(()), 80f32.to_bits(), 320f32.to_bits()));
        // fddpc: its sources do not advance
        let (m, r) = run_after(&POW2, &["fddpc.repeat2 r10, i0, cp1, cp2, r1, r3, r5"]);
        assert_eq!((r, m.r[11], m.i[0]), (Ok(()), 8f32.to_bits(), 32f32.to_bits()));
        // fdpc (fdpc, usse-dot-products-fdpc-clip): fdp's value; p0-p3 and i0-i2 untouched
        let (m, r) = run_after(&POW2, &["fdpc.repeat3 r10, cp3, r1, r5"]);
        assert_eq!((r, m.r[12], m.written.i), (Ok(()), (16f32 + 64.0 + 256.0).to_bits(), 0));
        // their rounding is not measured
        let (_, r) = run_after(&ABC, &["mov r7, #0x3eaaaaab", "fdpc r10, cp0, r7, r7"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("rounding")));
    }

    #[test]
    fn sop2_blends_each_byte() {
        let blend = |a: u32, b: u32, ops: &str| {
            let (m, r) = run_after(
                &[&format!("mov r1, #0x{a:08x}"), &format!("mov r2, #0x{b:08x}")],
                &[&format!("sop2 r10, r1, r2, {ops}")],
            );
            r.map(|_| m.r[10])
        };
        // hardware (usse-colour-ops-sop2-selectors): a product of bytes over 255, rounded to
        // nearest; alpha from the alpha selectors
        assert_eq!(blend(0x864d3896, 0xc0e628e4, "s1, zero, add+asop2 s1a.comp, zero, add"), Ok(0x40170c58));
        // add rounds the sum of both products once: 64.25 + 63.25 is 128
        assert_eq!(blend(0x80808080, 0x7f7f7f7f, "s1, s2, add+asop2 s1a, s2a, add"), Ok(0x80808080));
        // min and max compare the sources themselves
        assert_eq!(
            blend(0xdd867ff1, 0x4e0bf742, "s1.comp, s1.comp, min+asop2 zero, zero, add"),
            Ok(0x000b7f42)
        );
        // asat is min(s1a, 1 - s2a), and .comp min(1 - s1a, s2a)
        assert_eq!(
            blend(0x01ff00fe, 0xff00ff01, "asat.comp, zero, add+asop2 zero, zero, add"),
            Ok(0x00fe00fd)
        );
        assert_eq!(blend(0xffffffff, 0x80808080, "asat, zero, add+asop2 zero, zero, add"), Ok(0x007f7f7f));
        // usse-colour-ops-sop2-ops: s2scale doubles the result; zeros reads s2 as s2 - 128
        assert_eq!(blend(0x7f7f7f7f, 0x01ff00fe, "s2scale, zero, add+asop2 zero, zero, add"), Ok(0x00fe00fd));
        assert_eq!(
            blend(0x0000560a, 0x00004f21, "zero.comp, zeros.comp, sub+asop2 zero, zero, add"),
            Ok(0x00808769)
        );
        // the leading comp complements s1 for add and sub; alpha neg negates
        assert_eq!(
            blend(0x00000040, 0, "comp, zero.comp, zero, add+asop2 zero.comp, zero, add, neg"),
            Ok(0x00ffffbf)
        );
    }

    #[test]
    fn sop2wm_blends_with_a_byte_mask() {
        let blend = |a: u32, b: u32, ops: &str| {
            let (m, r) = run_after(
                &[&format!("mov r1, #0x{a:08x}"), &format!("mov r2, #0x{b:08x}"), "mov r10, #0xa0a1a2a3"],
                &[&format!("sop2wm r10{ops}")],
            );
            r.map(|_| m.r[10])
        };
        // hardware (sop2wm): sop2's blend with one selector pair, the colour
        // operation on bytes 0-2, the alpha one on byte 3, masked bytes kept
        assert_eq!(
            blend(0x00000040, 0x00000020, ".e0, r1, r2, zero.comp, zero.comp, add, sub"),
            Ok(0xa0a1a260)
        );
        // on the alpha byte asat is 1, with or without .comp
        assert_eq!(
            blend(0xffffffff, 0x80808080, ".e0.e1.e2.e3, r1, r2, asat.comp, s2, sub, sub"),
            Ok(0xbf000000)
        );
    }

    #[test]
    fn sop3_and_the_lerps_blend_three_sources() {
        let blend = |s: [u32; 3], text: &str| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", s[0]),
                    &format!("mov r2, #0x{:08x}", s[1]),
                    &format!("mov r3, #0x{:08x}", s[2]),
                ],
                &[text],
            );
            r.map(|_| m.r[10])
        };
        let s = [0x80ff8040, 0xff80ff80, 0];
        // sop3 (usse-colour-ops-sop3-lrp): sop2's blend of s1 and s2, with s0 and s0a as factors
        assert_eq!(blend(s, "sop3 r10, r1, r2, r3, s0, zero, add+asop s0a, zero, add"), Ok(0x80808020));
        let s = [0x7f7f7f7f, 0x01ff00fe, 0xff00ff01];
        // arsop: sub is s2a * g - s1a * (the second colour factor); add is 0
        assert_eq!(
            blend(s, "sop3 r10, r1, r2, r3, zero, zero.comp, add+arsop zero.comp, sub"),
            Ok(0xfe00ff01)
        );
        assert_eq!(blend(s, "sop3 r10, r1, r2, r3, zero, zero.comp, add+arsop s1a, add"), Ok(0x0000ff01));
        // alrp: g1 * (1 - s0a) + g2 * s0a
        let s = [0x831d45d0, 0xeec09b5f, 0x62508640];
        assert_eq!(
            blend(s, "sop3 r10, r1, r2, r3, s2.comp, s0.comp, sub+alrp s1a.comp, s2a.comp"),
            Ok(0x593d003b)
        );
        // lrp: f1 * (1 - w) + f2 * w by s0 (or s0a); sop3c: x1 * f1 + x2 * f2
        let s = [0x80808080, 0x7f7f7f7f, 0x01ff00fe];
        assert_eq!(
            blend(s, "lrp r10, r1, r2, r3, zero.comp, zero, s0+asop s1.comp, s0a, add"),
            Ok(0x407f7f7f)
        );
        assert_eq!(
            blend(s, "sop3c r10, r1, r2, r3, s0, s0a.comp, s1, s2+alrp s1a, s2a.comp"),
            Ok(0xbfbf40be)
        );
        // the alrp form's neg: -op(s1 * f2, s2 * f1), the factors swapped
        let s = [0, 0xffffffff, 0x80808080];
        assert_eq!(blend(s, "sop3 r10, r1, r2, r3, s1, s2a.comp, sub, neg+alrp zero, zero"), Ok(0x00010101));
    }

    #[test]
    fn movc_selects_per_lane_and_movmsk_by_a_condition() {
        let run3 = |s: [u32; 3], text: &str| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", s[0]),
                    &format!("mov r2, #0x{:08x}", s[1]),
                    &format!("mov r3, #0x{:08x}", s[2]),
                    "mov r10, #0xa0a1a2a3",
                ],
                &[text],
            );
            r.map(|_| m.r[10])
        };
        let (a, b) = (0x62222222, 0xb3333333);
        // hardware (movc-*): s1 where the lane of s0 passes, else s2; i10
        // lanes are bits 0-9, 10-19, 20-29 and bits 30-31 come out 0
        assert_eq!(run3([0x8000, a, b], "movc.i16.tn r10, r1, r2, r3"), Ok(0xb3332222));
        assert_eq!(run3([0x8000, a, b], "movc.i32.tp|z r10, r1, r2, r3"), Ok(a));
        assert_eq!(run3([0x200, a, b], "movc.i10.tz r10, r1, r2, r3"), Ok(0x22222333));
        // floats: a denormal tests as zero
        assert_eq!(run3([1, a, b], "movc.flt.tz r10, r1, r2, r3"), Ok(a));
        // movmsk-*: s1 into d when bit 0 (mask) or bit 7 (u8) of byte c of s2
        // is set, or s2 >= 0.5 (flt); else d stays
        let v = 0x11223344;
        assert_eq!(run3([0x01ff8000, v, 0], "movmsk.u8 r10, r2, r1.1"), Ok(v));
        assert_eq!(run3([0x01ff8000, v, 0], "movmsk.mask r10, r2, r1.1"), Ok(0xa0a1a2a3));
        assert_eq!(run3([0x3f000000, v, 0], "movmsk.flt r10, r2, r1"), Ok(v));
        assert_eq!(run3([0x3effffff, v, 0], "movmsk.flt r10, r2, r1"), Ok(0xa0a1a2a3));
        assert_eq!(run3([0x3c000000, v, 0], "movmsk.flt16 r10, r2, r1.2"), Ok(v));
        // .1 is bits 8-23: 0x003c00 there is 1.0
        assert_eq!(run3([0x003c0000, v, 0], "movmsk.flt16 r10, r2, r1.1"), Ok(v));
        // usse-movc-movmsk-smsk: u8 and flt also need bit 0 of s0; mask ignores s0
        assert_eq!(run3([2, v, 0x8000], "movmsk.smsk.u8 r10, r1, r2, r3.1"), Ok(0xa0a1a2a3));
        assert_eq!(run3([3, v, 0x8000], "movmsk.smsk.u8 r10, r1, r2, r3.1"), Ok(v));
        assert_eq!(run3([2, v, 0x100], "movmsk.mask.smsk r10, r1, r2, r3.1"), Ok(v));
    }

    #[test]
    fn an_index_does_not_reach_the_internal_registers() {
        // hardware (usse-internal-registers-ireg-index): r[il + #n] at 124-127, the numbers i0-i3 have as
        // direct operands, reads varying values and a write there leaves i0-i3 as they
        // were; neither is modelled, so both stop as open
        for src in [
            &["mov r1, #0x0000007c", "mov i.l, r1", "mov r10, r[il + #1]"][..],
            &["mov r1, #0x0000007c", "mov r2, #5", "mov i.l, r1", "mov r[il + #0], r2"][..],
        ] {
            let (_, r) = run_after(&[], src);
            let e = r.expect_err("an index reaching 124-127");
            assert!(matches!(e, Error::Unsupported { .. }), "{e:?}");
        }
    }

    #[test]
    fn index_registers_offset_register_numbers() {
        let regs: Vec<String> = (0..8).map(|n| format!("mov r{}, #0x{:08x}", 30 + n, 0x30 + n)).collect();
        let regs: Vec<&str> = regs.iter().map(|s| s.as_str()).collect();
        let r10 = |src: &[&str]| {
            let (m, r) = run_after(&regs, src);
            r.map(|_| m.r[10])
        };
        // hardware (usse-indexing-index-unit, usse-indexing-index-width3): r[il + #n] is r(il + n), bits
        // 10 and up of i.l ignored
        assert_eq!(r10(&["mov r1, #0x0000001e", "mov i.l, r1", "mov r10, r[il + #3]"]), Ok(0x33));
        assert_eq!(r10(&["mov r1, #0xfffffc20", "mov i.l, r1", "mov r10, r[il + #0]"]), Ok(0x32));
        // usse-indexing-index-high: i.lh sets i.l from the low half and i.h from the high one
        assert_eq!(r10(&["mov r1, #0x001f001e", "mov i.lh, r1", "mov r10, r[ih + #0]"]), Ok(0x31));
        // usse-indexing-index-store: the destination form mirrors the source one
        assert_eq!(
            r10(&[
                "mov r1, #0x0000001e",
                "mov r2, #0x12345678",
                "mov i.h, r1",
                "mov r[ih + #1], r2",
                "mov r10, r31"
            ]),
            Ok(0x12345678)
        );
        // an index register the task has not written stops
        assert!(r10(&["mov r10, r[il + #0]"]).is_err());
        // registers past the task's temporaries belong to other instances
        let mut m = Machine { temps: 32, ..Machine::default() };
        let r =
            m.run(&prog(&["mov r33, #0x00000001", "nop.end"]), &mut Memory { base: 0, words: vec![] }, 10);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("temporaries")));
    }

    #[test]
    fn the_integer_dot_products() {
        let dot = |s: [u32; 3], text: &str| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", s[0]),
                    &format!("mov r2, #0x{:08x}", s[1]),
                    &format!("mov r9, #0x{:08x}", s[2]),
                ],
                &[text],
            );
            r.map(|_| m.r[10])
        };
        let (a, b) = (0x05060708, 0x10203040);
        // hardware (usse-integer-dot-intdot-lanes): sum(a * b) * Cx / 255 rounded, saturated,
        // in bytes 0-2, the alpha byte by Ax; off reads each byte as x - 128
        assert_eq!(dot([a, b, 0], "u8dot4 r10, Cx2, Ax8, r1, r2"), Ok(0x23090909));
        assert_eq!(dot([0x80808080, 0x7f7f7f7f, 0], "u8dot4 r10, Cx1, Ax1, r1.comp, r2"), Ok(0xfdfdfdfd));
        assert_eq!(dot([0x05060708, 0x10203040, 0], "u8dot4off r10, Cx1, Ax1, r1, r2"), Ok(0xa8a8a8a8));
        // the 16-bit result is x * 32767 / 65025, saturated at +/-32767, twice
        assert_eq!(dot([0, 0xffffffff, 0], "u16dot4off r10, Cx1, Ax1, r1, r2"), Ok(0x80028002));
        assert_eq!(dot([0, 0xffffffff, 0], "u16dot3off r10, Cx1, r1, r2"), Ok(0xa001a001));
        // usse-integer-dot-intdot-alpha: aadd/asub of two products of the source alphas, by Ax;
        // alrp lerps g1 to g2 by s0a, alrpc 1 - g1 to g2
        let (a, b) = (0xff000000, 0x80000000);
        assert_eq!(
            dot([a, b, 0], "u8dot3 r10, Cx1, r1, r2+aadd Ax2, s1a, s1a.comp, s2a.comp, s2a"),
            Ok(0x7f000000)
        );
        assert_eq!(dot([a, b, 0x40112233], "u8dot3 r10, Cx1, r1, r2+alrp r9, s1a, s2a"), Ok(0xdf000000));
        assert_eq!(dot([a, b, 0x40112233], "u8dot3 r10, Cx1, r1, r2+alrpc r9, s1a, s2a"), Ok(0x20000000));
    }

    #[test]
    fn efo_runs_its_dataflow() {
        let init = [
            "mov r1, #0x40400000", // 3
            "mov r2, #0x40a00000", // 5
            "mov r3, #0x40e00000", // 7
            "mov r4, #0x41300000", // 11
            "mov r5, #0x41500000", // 13
            "mov i0, r4",
            "mov i1, r5",
        ];
        let f = |x: f32| x.to_bits();
        // hardware (usse-efo-dataflow): m0 = 3 * 7, m1 = 5 * 7, a0 = m0 + m1,
        // a1 = i1 + i0; d reads the internals before this instruction's writes
        let (m, r) = run_after(
            &init,
            &[
                "efo r10= a0, i0 = a0, i1 = a1, a0=m0+m1, a1=i1+i0, m0=src0*src2, m1=src1*src2, r1, r2, r3",
                "efo r11= a1, !i0 = a0, !i1 = a1, a0=m0+m1, a1=i1+i0, m0=src0*src2, m1=src1*src2, r1, r2, r3",
                "efo r12= i0, i0 = a0, !i1 = a1, a0=m0-m1, a1=-i1+i0, m0=src0*src2, m1=src1*src2, r1, r2, r3",
            ],
        );
        assert_eq!((r, m.r[10], m.r[11], m.r[12]), (Ok(()), f(56.0), f(80.0), f(56.0)));
        assert_eq!((m.i[0], m.i[1]), (f(-14.0), f(24.0)));
    }

    #[test]
    fn fmad16_works_on_half_lanes() {
        let mad = |s: [u32; 3], text: &str| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", s[0]),
                    &format!("mov r2, #0x{:08x}", s[1]),
                    &format!("mov r3, #0x{:08x}", s[2]),
                ],
                &[text],
            );
            r.map(|_| m.r[10])
        };
        // hardware (usse-fmad16-specials): an infinity stays, an invalid result
        // is 0x7fff: (inf, 0) * (2, inf) + (1, 1), (NaN, -inf) * 1 + (1, inf)
        assert_eq!(mad([0x7c00_0000, 0x4000_7c00, 0x3c00_3c00], "fmad16 r10, r1, r2, r3"), Ok(0x7c00_7fff));
        assert_eq!(mad([0x7e00_fc00, 0x3c00_3c00, 0x3c00_7c00], "fmad16 r10, r1, r2, r3"), Ok(0x7fff_7fff));
        let s = [0x3c004000, 0x40004200, 0x3c003c00]; // (2, 1), (3, 2), (1, 1)
        // hardware (usse-fmad16-lanes): a * b + c per half; .swzll reads the low
        // half twice; .neg/.abs per source
        assert_eq!(mad(s, "fmad16 r10, r1, r2, r3"), Ok(0x42004700));
        assert_eq!(mad(s, "fmad16 r10, r1.swzll, r2, r3"), Ok(0x45004700));
        assert_eq!(mad(s, "fmad16 r10, r1, r2.neg, r3"), Ok(0xbc00c500));
        // usse-fmad16-rounding: one rounding of the exact a * b + c
        assert_eq!(mad([0x42c80000, 0xbf400000, 0x477fe000], "fmad16 r10, r1, r2, r3"), Ok(0x3d67e000));
        // .swzf32 (fmad16 page): the whole register as a binary32, exactly:
        // 1.5 + 2^-20 times (3, 2) plus (1, 1) rounds to (5.5, 4)
        assert_eq!(
            mad([0x3fc00008, 0x40004200, 0x3c003c00], "fmad16 r10, r1.swzf32, r2, r3"),
            Ok(0x44004580)
        );
    }

    #[test]
    fn write_masks_write_consecutive_registers() {
        let regs =
            ["mov r1, #0x11121314", "mov r2, #0x21222324", "mov r3, #0x31323334", "mov r4, #0x41424344"];
        let pre =
            ["mov r10, #0x000000a0", "mov r11, #0x000000a1", "mov r12, #0x000000a2", "mov r13, #0x000000a3"];
        let run4 = |op: &str| {
            let (m, r) = run_after(&[&regs[..], &pre[..]].concat(), &[op]);
            r.map(|_| [m.r[10], m.r[11], m.r[12], m.r[13]])
        };
        // hardware (usse-write-masks-wmask-mov, usse-write-masks-wmask-or): component k writes d + k from s + k
        assert_eq!(run4("mov r10.yw, r1"), Ok([0xa0, 0x21222324, 0xa2, 0x41424344]));
        assert_eq!(run4("and r10.xz, r1, #0x000000ff"), Ok([0x14, 0xa1, 0x34, 0xa3]));
        assert_eq!(run4("mov r10., r1"), Ok([0xa0, 0xa1, 0xa2, 0xa3]));
    }

    #[test]
    fn half_float_packs_and_unpacks() {
        let pk = |a: u32, b: u32, op: &str| {
            let (m, r) = run_after(&[&format!("mov r1, #0x{a:08x}"), &format!("mov r2, #0x{b:08x}")], &[op]);
            r.map(|_| m.r[10])
        };
        // hardware (usse-pack-f16): truncated toward zero whatever the mode,
        // saturated at 65504, half denormals kept; s1 low, s2 high
        assert_eq!(pk(0x3f801000, 0x3f803000, "pckf16f32 r10, r1.0, r2.0, nearest"), Ok(0x3c013c00));
        assert_eq!(pk(0x4788b800, 0x33d6bf95, "pckf16f32 r10, r1.0, r2.0, nearest"), Ok(0x00017bff));
        assert_eq!(pk(0xbfd9999a, 0x33000000, "pckf16f32 r10, r1.0, r2.0, up"), Ok(0x0000becc));
        // .renable rounds to an integer by the mode first
        assert_eq!(pk(0x40200000, 0xc0600000, "pckf16f32.renable r10, r1.0, r2.0, nearest"), Ok(0xc4004000));
        assert_eq!(pk(0xbfc00000, 0x3fc00000, "pckf16f32.renable r10, r1.0, r2.0, down"), Ok(0x3c00c000));
        // usse-pack-unpack-f16: exact, infinities kept, a NaN as 0x7fffffff
        assert_eq!(pk(0x7bff03ff, 0, "unpckf32f16 r10, r1.0, r1.0, nearest"), Ok(0x387fc000));
        assert_eq!(pk(0xfc007c00, 0, "unpckf32f16 r10, r1.2, r1.0, nearest"), Ok(0xff800000));
        assert_eq!(pk(0x00017e00, 0, "unpckf32f16 r10, r1.0, r1.0, nearest"), Ok(0x7fffffff));
    }

    #[test]
    fn fpma_adds_a_product_per_byte() {
        let pma = |s: [u32; 3], text: &str| {
            let (m, r) = run_after(
                &[
                    &format!("mov r1, #0x{:08x}", s[0]),
                    &format!("mov r2, #0x{:08x}", s[1]),
                    &format!("mov r3, #0x{:08x}", s[2]),
                ],
                &[text],
            );
            r.map(|_| m.r[10])
        };
        let s = [0x80808080, 0x7f7f7f7f, 0x01ff00fe];
        // hardware (fpma): the first selection plus the product of the other
        // two over 255, rounded half up, saturated; alpha by its own three
        assert_eq!(pma(s, "fpma r10, r1, r2, r3, s0, s1, s2, s0a, s1a, s2a"), Ok(0x80ff80ff));
        assert_eq!(pma(s, "fpma.sat r10, r1, r2, r3, s0.comp, s1, s2, s0a, s1a, s2a"), Ok(0x80fe7ffe));
        // .neg on source 0 subtracts the first selection
        assert_eq!(pma(s, "fpma r10, r1.neg, r2, r3, s0, s1, s2, s0a, s1a, s2a"), Ok(0x00000000));
        // fpma on .c10 lanes (usse-colour-ops-fpma-sat)
        assert_eq!(pma(s, "fpma r10.c10, r1.c10, r2.c10, r3.c10, s0, s1, s2, s0a, s1a, s2a"), Ok(0x0070a000));
    }

    #[test]
    fn rlp_rotates_through_a_predicate() {
        let clear = [
            "mov r7, #0x00000000",
            "and.testtanz.chan0 !c0, p0, r7, r7",
            "and.testtanz.chan0 !c0, p1, r7, r7",
        ];
        // hardware (rlp): d = s << 1 | pN, then pN = bit 31 of s
        let (m, r) = run_after(&[&clear[..], &["mov r1, #0x80000001"]].concat(), &["rlp r10, r1, p0"]);
        assert_eq!((r, m.r[10], m.p[0]), (Ok(()), 2, true));
        let (m, r) = run_after(
            &[&clear[..], &["mov r1, #0xffffffff"]].concat(),
            &["rlp r10, r1, p0", "rlp r11, r1, p0"],
        );
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0xfffffffe, 0xffffffff));
        // usse-rlp-high-predicates: numbers from 4 up alias p0-p3 (mod 4): p5 is p1
        let (m, r) = run_after(
            &[&clear[..], &["mov r1, #0x80000000", "mov r2, #0x00000000"]].concat(),
            &["rlp r10, r1, p5", "rlp r15, r2, p5"],
        );
        assert_eq!((r, m.r[10], m.r[15], m.p[1]), (Ok(()), 0, 1, false));
    }

    #[test]
    fn statomic_packs_clamped_signed_bytes() {
        let (m, r) = run_after(
            &["mov r1, #0xf14ed442", "mov r2, #0x65283b7d", "mov r3, #0x535b6075"],
            &["statomic r10, r1.1, r2.2, up", "statomic.scale r11, r3, r2, zero"],
        );
        // hardware (statomic): bytes s1.c, s2.c, s1.c, s2.c, each read as
        // signed and clamped at 0; the mode and .scale change nothing
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x28002800, 0x7d757d75));
    }

    #[test]
    fn c10_operands_are_signed_10_bit_lanes() {
        let op = |a: u32, b: u32, text: &str| {
            let (m, r) =
                run_after(&[&format!("mov r1, #0x{a:08x}"), &format!("mov r2, #0x{b:08x}")], &[text]);
            r.map(|_| m.r[10])
        };
        // hardware (usse-colour-ops-c10): lanes at bits 0, 10, 20, 1.0 = 255, clamped to
        // +/-510; the alpha of a c10 source is lane 0; a c10 destination
        // takes the three colour results, an 8-bit one saturates
        let plain = "zero.comp, zero, add+asop2 zero.comp, zero, add";
        assert_eq!(op(0x3fffffff, 0, &format!("sop2 r10.c10, r1, r2, {plain}")), Ok(0x0ff3fcff));
        assert_eq!(op(0x3fffffff, 0, &format!("sop2 r10, r1.c10, r2, {plain}")), Ok(0));
        let both = "zero.comp, zero.comp, add+asop2 zero.comp, zero.comp, add";
        assert_eq!(
            op(0x3fffffff, 0x00080200, &format!("sop2 r10.c10, r1.c10, r2.c10, {both}")),
            Ok(0x3ff80a02)
        );
    }

    #[test]
    fn c10_and_integer_packs() {
        let pk = |a: u32, b: u32, op: &str| {
            let (m, r) = run_after(&[&format!("mov r1, #0x{a:08x}"), &format!("mov r2, #0x{b:08x}")], &[op]);
            r.map(|_| m.r[10])
        };
        // hardware (usse-pack-c10): x * 255 to nearest even in lanes s1, s2, s1
        assert_eq!(pk(0x3f000000, 0xbf000000, "pckc10f32 r10, r1.0, r2.0, nearest"), Ok(0x080e0080));
        // usse-pack-unpack-c10: lane c / 255, the lanes clamped to +/-510
        assert_eq!(pk(0xe007f801, 0, "unpckf32c10 r10, r1.2, r1.0, nearest"), Ok(0xc0000000));
        // usse-pack-unpack-c10-16: three bits of lane 0 of source 1, nothing converted
        assert_eq!(pk(0x19a24d55, 0, "unpcku16c10 r10, r1.0, r1.1, nearest"), Ok(0x0000ffff));
        assert_eq!(pk(0x266fc109, 0, "unpcks16c10 r10, r1.0, r1.1, nearest"), Ok(0x00000001));
        // unpack-*: unpcku8s8 makes a negative 0x7f, unpcku16s8 0;
        // unpcks16s8 sign-extends; values laid out as packs do
        assert_eq!(pk(0x807f0100, 0, "unpcku8s8 r10, r1.3, r1.1, nearest"), Ok(0x017f017f));
        assert_eq!(pk(0x807f0100, 0, "unpcku16s8 r10, r1.3, r1.2, nearest"), Ok(0x007f0000));
        assert_eq!(pk(0x807f0100, 0, "unpcks16s8 r10, r1.3, r1.2, nearest"), Ok(0x007fff80));
    }

    #[test]
    fn float_specials() {
        let (inf, nan, one, max) = (0x7f800000, 0x7fc00001, 0x3f800000, 0x7f7fffff);
        // hardware (usse-fmad-move, usse-dot-products-fdp-specials): infinities stay, an invalid
        // result or a NaN input gives 0x7fc00000, an overflow +inf
        assert_eq!(flt::mul(inf, 0), Ok(0x7fc00000));
        assert_eq!(flt::add(Ok(nan), one), Ok(0x7fc00000));
        assert_eq!(flt::mul(max, 0x40000000), Ok(inf));
        // usse-float-minmax-fminmax-specials, usse-float-minmax-allnan: minNum/maxNum, -0 below +0, of two
        // NaNs the second
        assert_eq!(flt::min(nan, one), Ok(one));
        assert_eq!(flt::max(0x80000000, 0), Ok(0));
        assert_eq!(flt::min(nan, 0x7fc00002), Ok(0x7fc00002));
    }

    #[test]
    fn ima16_neg_subtracts_source_2() {
        // hardware (ima16): 0x00020005 * #3 - 0x00010007 is 0x00050008
        let (m, r) = run_after(
            &["mov r1, #0x00020005", "mov r2, #0x00010007"],
            &["ima16.s r10, r1, #3, r2.neg, u16, u16"],
        );
        assert_eq!((r, m.r[10]), (Ok(()), 0x00050008));
    }

    #[test]
    fn integer_multiply_tests_and_adif() {
        // hardware (usse-test-channels-lanes-other): imul16 tests the full product, so
        // 0x100 * 0x100 writes 0 but does not test as zero
        let (m, r) = run_after(&["mov r1, #0x00000100"], &["imul16.testtaz.chan0 r10, p0, r1, r1"]);
        assert_eq!((r, m.r[10] & 0xffff, m.p[0]), (Ok(()), 0, false));
        // usse-video-ops-adif: |a - b| per byte; adifsum adds the four and a half of s0
        let (m, r) = run_after(
            &["mov r1, #0x10203040", "mov r2, #0x30201008", "mov r3, #0x00050007"],
            &["adif r10, r1, r2", "adifsum r11, r3.high, r1, r2"],
        );
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x20002038, 0x20 + 0x20 + 0x38 + 5));
    }

    /// A uniform fill's instance with the job's filter coefficients (None: not known).
    fn run_video(coeffs: Option<FilterBlock>, src: &[&str]) -> (Machine, Result<(), Error>) {
        let mut m = Machine { uniform: true, coeffs, ..Machine::default() };
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        let r = m.run(&prog(&[src, &["nop.end"]].concat()), &mut mem, 1000);
        (m, r)
    }

    fn stops_on(r: &Result<(), Error>, text: &str) -> bool {
        matches!(r, Err(Error::Unsupported { why, .. }) if why.contains(text))
    }

    #[test]
    fn bilin_filters_bilinearly_in_eighths() {
        // hardware (x-video cases 13, 16, 19, 22, 25): weights (w.bP & 7) / 8 across,
        // (w.bP+1 & 7) / 8 down, truncated or (rnd) rounded, the other two bytes zero
        let set1 = ["mov r1, #0x11bd9805", "mov r2, #0x52fae253", "mov r3, #0xc122acf6"];
        for (op, want) in [
            ("bilin r10, r3, r1, r2, u8, planar, src01, dst01", 0x0000_d398),
            ("bilin r10, r3, r1, r2, u8, interleaved, src01, dst01", 0x0000_54af),
            ("bilin r10, r3, r1, r2, u8, planar, src23, dst23", 0xaa33_0000),
            ("bilin r10, r3, r1, r2, u8, planar, src01, dst01, rnd", 0x0000_d499),
            ("bilin r10, r3, r1, r2, s8, planar, src01, dst01", 0),
        ] {
            let (m, r) = run_video(None, &[&set1[..], &[op]].concat());
            assert_eq!((r, m.r[10]), (Ok(()), want), "{op}");
        }
        // x-video case 26: s8 reads signed bytes, the result saturates at 0
        let (m, r) = run_video(
            None,
            &[
                "mov r1, #0xfdf45f97",
                "mov r2, #0x2fba5bfe",
                "mov r3, #0x6b66c659",
                "bilin r10, r3, r1, r2, s8, planar, src01, dst01",
            ],
        );
        assert_eq!((r, m.r[10]), (Ok(()), 0x0000_4900));
        // usse-video-filters-bilin-o8 case 15: o8 reads the byte minus 0x80
        let (m, r) = run_video(
            None,
            &[
                "mov r1, #0x000000c0",
                "mov r2, #0",
                "mov r3, #0",
                "bilin r10, r3, r1, r2, o8, planar, src01, dst01",
            ],
        );
        assert_eq!((r, m.r[10]), (Ok(()), 0x40));
    }

    #[test]
    fn firv_sums_two_taps_per_byte_column() {
        let set2 = ["mov r1, #0xfdf45f97", "mov r2, #0x2fba5bfe", "mov r3, #0x6b66c659"];
        // hardware (x-video case 29): a.bk * c.b0 + b.bk * c.b1, signed taps, saturated
        let (m, r) = run_video(None, &[&set2[..], &["firv r10, r1, r2, r3, u8"]].concat());
        assert_eq!((r, m.r[10]), (Ok(()), 0xffff_ff00));
        // x-video case 35: scale shifts right by c.b3 (0x6b: nothing left)
        let (m, r) = run_video(None, &[&set2[..], &["firv r10, r1, r2, r3, u8, scale"]].concat());
        assert_eq!((r, m.r[10]), (Ok(()), 0));
        // usse-video-filters-cross-firv-scale case 9: (0 + 2) >> 1 per byte
        let (m, r) = run_video(
            None,
            &["mov r1, #0", "mov r2, #0x02020202", "mov r3, #0x01010101", "firv r10, r1, r2, r3, u8, scale"],
        );
        assert_eq!((r, m.r[10]), (Ok(()), 0x0101_0101));
        // usse-video-filters-amp-l40-firv-src2 case 40: +src2.2 adds c.b2 as a signed byte (-128)
        let (m, r) = run_video(
            None,
            &["mov r1, #0", "mov r2, #0", "mov r3, #0x80808080", "firv r10, r1, r2, r3, u8, +src2.2"],
        );
        assert_eq!((r, m.r[10]), (Ok(()), 0));
    }

    #[test]
    fn firv_latch_adds_the_firh_latch() {
        // hardware (usse-video-filters-amp-l40-firv-latch case 1): four firh fill the latch with 0x40s,
        // latch adds them to 1 * 1 + 1 * 1
        let (m, r) = run_video(
            bank(0),
            &[
                "mov r20, #0x40404040",
                "mov r21, #0x40404040",
                "mov r22, #0x40404040",
                "firh r11, r20, r21, r22, u8, rep, fcs2, #0, #0",
                "firh r11, r20, r21, r22, u8, rep, fcs2, #0, #1",
                "firh r11, r20, r21, r22, u8, rep, fcs2, #0, #2",
                "firh r11, r20, r21, r22, u8, rep, fcs2, #0, #3",
                "mov r1, #0x01010101",
                "mov r2, #0x01010101",
                "mov r3, #0x01010101",
                "firv r10, r1, r2, r3, u8, latch",
                "mov o0, r10",
            ],
        );
        assert_eq!((r, m.r[10], m.o[0]), (Ok(()), 0x4242_4242, 0x4242_4242));
        // x-video case 30: a latch the task did not write is not known
        let (_, r) = run_video(
            None,
            &[
                "mov r1, #0x10203040",
                "mov r2, #0x0f0e0d0c",
                "mov r3, #0x00800080",
                "firv r10, r1, r2, r3, u8, latch",
                "mov o0, r10",
            ],
        );
        assert!(stops_on(&r, "firh latch"), "{r:?}");
    }

    #[test]
    fn firh_filters_one_line_with_a_fixed_set() {
        // hardware (video-clean x-firh-*, video-ped x-ped-firh-fcs2-*): byte #k of the
        // result is sat((sum(tap * sample) + bias) >> 7), the line r1, r2, r3
        let ped = |op: &str, a: u32| {
            let (m, r) = run_video(
                bank(0),
                &[&format!("mov r1, #0x{a:08x}"), "mov r2, #0x80808080", "mov r3, #0x80808080", op],
            );
            assert_eq!(r, Ok(()), "{op}");
            m.firh_latch[0]
        };
        let zero = |op: &str, a: u32| {
            let (m, r) =
                run_video(bank(0), &[&format!("mov r1, #0x{a:08x}"), "mov r2, #0", "mov r3, #0", op]);
            assert_eq!(r, Ok(()), "{op}");
            m.firh_latch[0]
        };
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs2, #0, #0", 0x4000), Some(0x28)); // case 2
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs3, #0, #0", 0x40), Some(0x30)); // case 1
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs4, #0, #0", 0x4000), Some(0x28)); // case 2
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs5, #0, #0", 0x40), Some(0xff)); // case 1
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs0, #0, #0", 0x40), Some(0));
        // the edge modes at the start of the line (x-ped-firh-fcs2-msc/mdc case 4)
        assert_eq!(ped("firh r10, r1, r2, r3, u8, msc, fcs2, #0, #0", 0x80808040), Some(0x58));
        assert_eq!(ped("firh r10, r1, r2, r3, u8, mdc, fcs2, #0, #0", 0x80808040), Some(0x62));
        assert_eq!(ped("firh r10, r1, r2, r3, u8, rep, fcs2, #0, #0", 0x80808040), Some(0x60));
        // fcs2's bias is 64-79: 52 + bias may or may not reach 128
        assert_eq!(zero("firh r10, r1, r2, r3, u8, rep, fcs2, #2, #0", 0x0d), None);
    }

    #[test]
    fn firh_merges_its_byte_into_the_latch() {
        // hardware (video-c11-merge3 usse-video-filters-c11-latch-merge case 0): with the latch cleared,
        // each destination holds the bytes merged so far
        let (m, r) = run_video(
            bank(0),
            &[
                "mov r27, #0",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #0",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #1",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #2",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #3",
                "mov r20, #0x11111111",
                "mov r21, #0x22222222",
                "mov r22, #0x33333333",
                "mov r23, #0x44444444",
                "firh r10, r20, r20, r20, u8, rep, fcs3, #4, #0",
                "firh r11, r21, r21, r21, u8, rep, fcs3, #4, #1",
                "firh r12, r22, r22, r22, u8, rep, fcs3, #4, #2",
                "firh r13, r23, r23, r23, u8, rep, fcs3, #4, #3",
                "mov r1, r10",
                "mov r2, r11",
                "mov r3, r12",
                "mov r4, r13",
            ],
        );
        assert_eq!(r, Ok(()));
        assert_eq!(&m.r[1..5], &[0x11, 0x2211, 0x0033_2211, 0x4433_2211]);
        // the first four, with a firh four instructions on, may catch its byte (case 2 of the
        // same run, four instructions between firhs: a destination read 0x44332211), so they
        // are not known
        let (_, r) = run_video(
            bank(0),
            &[
                "mov r27, #0",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #0",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #1",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #2",
                "firh r15, r27, r27, r27, u8, rep, fcs3, #4, #3",
                "nop",
                "nop",
                "nop",
                "nop",
                "firh r10, r27, r27, r27, u8, rep, fcs3, #4, #0",
                "mov r1, r15",
            ],
        );
        assert!(stops_on(&r, "later firh"), "{r:?}");
    }

    #[test]
    fn firh_without_its_state_stops() {
        let line = ["mov r1, #0x00000040", "mov r2, #0", "mov r3, #0"];
        // a latch byte the task did not write: any value (Bound::Mask), not a stop
        let (m, r) = run_video(
            bank(0),
            &[&line[..], &["firh r10, r1, r2, r3, u8, rep, fcs2, #0, #0", "mov o0, r10"]].concat(),
        );
        assert_eq!((r, m.bounds.get(&("o", 0))), (Ok(()), Some(&Bound::Mask(0xffff_ff00))));
        // coefficient sets the run does not know (CR_USE_COEFFS_MODE and the job's load, E078)
        let (m, r) = run_video(None, &[&line[..], &["firh r10, r1, r2, r3, u8, rep, fcs2, #0, #0"]].concat());
        assert_eq!((r, m.firh_latch[0]), (Ok(()), None));
        // a set 6 or 7 with a load under a fixed bank
        let c = Some(FilterBlock { mode: 2, groups: Some([0; 9]) });
        let (m, r) = run_video(c, &[&line[..], &["firh r10, r1, r2, r3, u8, rep, fcs7, #0, #0"]].concat());
        assert_eq!((r, m.firh_latch[0]), (Ok(()), None));
        // sets 6 and 7 under fixed bank 1 or 2: not measured
        let (m, r) =
            run_video(bank(1), &[&line[..], &["firh r10, r1, r2, r3, u8, msc, fcs6, #4, #0"]].concat());
        assert_eq!((r, m.firh_latch[0]), (Ok(()), None));
    }

    /// A job that loads no coefficients with 0x0a9c at `mode` (E078's load0: the reset state).
    fn bank(mode: u32) -> Option<FilterBlock> {
        Some(FilterBlock { mode, groups: None })
    }

    /// One firh on the line r1-r3 (byte 0 of r1 first) with the job's coefficients: byte k.
    fn firh_on(c: Option<FilterBlock>, line: [u32; 3], op: &str) -> (Option<u8>, Result<(), Error>) {
        let set = [
            format!("mov r1, #0x{:08x}", line[0]),
            format!("mov r2, #0x{:08x}", line[1]),
            format!("mov r3, #0x{:08x}", line[2]),
        ];
        let src: Vec<&str> = set.iter().map(String::as_str).chain([op]).collect();
        let (m, r) = run_video(c, &src);
        (m.firh_latch[0], r)
    }

    #[test]
    fn firh_reads_a_loaded_set() {
        // E078 (usse-filter-taps, usse-filter-gain): a group's first word holds the taps at
        // -3..0 (bytes 3..0), its second +1..+4, its third the shift (3:0) and a signed 16-bit
        // bias (19:4); sat((sum + bias) >> shift)
        let mut g = [0u32; 9];
        g[0] = 0x0000_0040; // tap 64 at the centre
        g[2] = 6; // shift 6, bias 0
        let loaded = Some(FilterBlock { mode: 3, groups: Some(g) });
        let op = "firh r10, r1, r2, r3, u8, rep, fcs0, #0, #0";
        assert_eq!(firh_on(loaded, [0x40, 0, 0], op), (Some(0x40), Ok(())));
        // the bias, signed: -32 << 4 in bits 19:4
        g[2] = 6 | (0xffe0 << 4);
        let loaded = Some(FilterBlock { mode: 3, groups: Some(g) });
        assert_eq!(firh_on(loaded, [0x40, 0, 0], op), (Some(0x3f), Ok(())));
        // set 1 reads the second group; mode 0-2 keeps sets 0 and 1 loaded
        let mut g = [0u32; 9];
        g[4] = 0x0100_0000; // tap 1 at +1
        let op1 = "firh r10, r1, r2, r3, u8, rep, fcs1, #0, #0";
        for mode in [0, 1, 3] {
            let c = Some(FilterBlock { mode, groups: Some(g) });
            assert_eq!(firh_on(c, [0x7700, 0, 0], op1), (Some(0x77), Ok(())), "{mode}");
        }
        // with 0x0a9c at 3, set 2 is the third group but reads only the taps at -3, 0 and +3
        let mut g = [0u32; 9];
        g[6] = 0x0102_0304;
        g[7] = 0x0506_0708;
        let c = Some(FilterBlock { mode: 3, groups: Some(g) });
        let op2 = "firh r10, r1, r2, r3, u8, rep, fcs2, #4, #0";
        // line bytes 1..12 at positions 0..11: the taps at -3 (1), 0 (4) and +3 (7)
        let line = [0x0403_0201, 0x0807_0605, 0x0c0b_0a09];
        assert_eq!(firh_on(c, line, op2), (Some(2 + 4 * 5 + 7 * 8), Ok(())));
        // and sets 3 to 7 give 0
        for set in 3..8 {
            let op = format!("firh r10, r1, r2, r3, u8, rep, fcs{set}, #4, #0");
            assert_eq!(firh_on(c, line, &op), (Some(0), Ok(())), "{set}");
        }
    }

    #[test]
    fn firh_without_a_load_has_the_fixed_sets_only() {
        // E078 (usse-filter-sets load0): sets 0, 1, 6 and 7 give 0, sets 2 to 5 bank 0's
        for set in [0, 1, 6, 7] {
            let op = format!("firh r10, r1, r2, r3, u8, rep, fcs{set}, #4, #0");
            assert_eq!(firh_on(bank(0), [0x8080_8080; 3], &op), (Some(0), Ok(())), "{set}");
        }
        let op = "firh r10, r1, r2, r3, u8, rep, fcs3, #4, #0";
        assert_eq!(firh_on(bank(0), [0x8080_8080; 3], op), (Some(0x80), Ok(())));
        // with a load at 0x0a9c = 0 too (usse-filter-edges-fcs67-mode0); bank 1's are not
        // measured
        let op = "firh r10, r1, r2, r3, u8, rep, fcs6, #4, #0";
        let c = Some(FilterBlock { mode: 0, groups: Some([1; 9]) });
        assert_eq!(firh_on(c, [0x8080_8080; 3], op), (Some(0), Ok(())));
        let c = Some(FilterBlock { mode: 1, groups: Some([0; 9]) });
        assert_eq!(firh_on(c, [0x8080_8080; 3], op), (None, Ok(())));
    }

    #[test]
    fn firh_s_unwritten_latch_bytes_are_any_value() {
        // the latch belongs to the instance slot: bytes the task did not write read what an
        // earlier task left (0xffffff and 0 in the probe runs), so a result's other bytes are
        // any value and its own byte is exact (Bound::Mask, counted apart as any value)
        let (m, r) = run_video(
            bank(0),
            &[
                "mov r1, #0x00000040",
                "mov r2, #0",
                "mov r3, #0",
                "firh r10, r1, r2, r3, u8, rep, fcs3, #0, #1",
                "mov o0, r10",
            ],
        );
        assert_eq!(r, Ok(()));
        assert_eq!(m.o[0] & 0xff00, 0x3000); // fcs3 of 0x40, 0x40, 0: 48
        assert_eq!(m.bounds.get(&("o", 0)), Some(&Bound::Mask(0xffff_00ff)));
        // computed on, the value is not known
        let (_, r) = run_video(
            bank(0),
            &[
                "mov r1, #0x00000040",
                "mov r2, #0",
                "mov r3, #0",
                "firh r10, r1, r2, r3, u8, rep, fcs3, #0, #0",
                "firv r11, r10, r10, r10, u8, latch",
                "mov o0, r11",
            ],
        );
        assert!(stops_on(&r, "firh latch"), "{r:?}");
    }

    #[test]
    fn a_latch_byte_written_but_not_computed_is_not_any_value() {
        // fcs6 under bank 1 writes byte 0 with a value the run cannot compute: a later firh's
        // destination holds it, so the result is not known (not masked as any value)
        let src = [
            "mov r1, #0x00000040",
            "mov r2, #0",
            "mov r3, #0",
            "firh r10, r1, r2, r3, u8, rep, fcs6, #0, #0",
            "firh r11, r1, r2, r3, u8, rep, fcs0, #0, #1",
            "mov o0, r11",
        ];
        let (_, r) = run_video(bank(1), &src);
        assert!(stops_on(&r, "the task wrote but the run could not compute"), "{r:?}");
        // a firh a false predicate skips may have written its byte too
        let src = [
            "mov r1, #0x00000040",
            "mov r2, #0",
            "mov r3, #0",
            "and.testtanz.chan0 !c0, p0, r3, r3",
            "p0 firh r10, r1, r2, r3, u8, rep, fcs3, #0, #0",
            "firh r11, r1, r2, r3, u8, rep, fcs3, #0, #1",
            "mov o0, r11",
        ];
        let (_, r) = run_video(bank(0), &src);
        assert!(stops_on(&r, "the task wrote but the run could not compute"), "{r:?}");
    }

    #[test]
    fn fixed_banks_one_and_two_are_fitted_not_checked() {
        let op = |set: u32| format!("firh r10, r1, r2, r3, u8, rep, fcs{set}, #4, #0");
        let line = ["mov r1, #0x80808080", "mov r2, #0x80808080", "mov r3, #0x80808080"];
        for (c, set, fitted) in
            [(bank(1), 2, true), (bank(2), 5, true), (bank(0), 2, false), (bank(1), 0, false)]
        {
            let (m, r) = run_video(c, &[&line[..], &[op(set).as_str()]].concat());
            assert_eq!((r, m.fitted), (Ok(()), fitted), "{c:?} {set}");
        }
    }

    #[test]
    fn firh_folds_the_line_by_its_edge_mode() {
        // usse-filter-edges: a loaded identity filter (the centre tap 1) on a ramp line reads,
        // at centres -4 to 18, rep: the end byte; msc: mirrored about the end byte; mdc:
        // mirrored with it doubled; from 19 every mode reads 0
        let line = [0x4030_2010, 0x8070_6050, 0xc0b0_a090];
        let mut g = [0u32; 9];
        g[0] = 1;
        let c = Some(FilterBlock { mode: 3, groups: Some(g) });
        let read = |edge: &str, centre: i32| {
            let s = if centre >= 16 { centre - 32 } else { centre };
            let op = format!("firh r10, r1, r2, r3, u8, {edge}, fcs0, #{s}, #0");
            firh_on(c, line, &op).0.map(|b| b / 16)
        };
        for (edge, want) in
            [("rep", [1, 1, 12, 12, 0, 0]), ("msc", [5, 2, 11, 5, 0, 0]), ("mdc", [4, 1, 12, 6, 0, 0])]
        {
            let got: Vec<u8> = [-4, -1, 12, 18, 19, 27].iter().map(|&c| read(edge, c).unwrap()).collect();
            assert_eq!(got, want, "{edge}");
        }
    }

    #[test]
    fn firh_centres_from_minus_4_to_27() {
        // hardware (usse-video-filters-c10-firh-fcs3-s5neg-ped, c9-*, c10-*): the centre field's
        // values below #-4 (16-27) are centres 16 to 27; under rep positions 12-18 read byte 11
        // and positions from 19 read 0. fcs3 ([1 2 1]/4) on a pedestal of 0x80, byte 11 0xc0:
        let line = [0x8080_8080, 0x8080_8080, 0xc080_8080];
        let op = |s: i32| format!("firh r10, r1, r2, r3, u8, rep, fcs3, #{s}, #0");
        assert_eq!(firh_on(bank(0), line, &op(-16)), (Some(0xc0), Ok(()))); // 15, 16, 17
        assert_eq!(firh_on(bank(0), line, &op(-14)), (Some(0x90), Ok(()))); // 17, 18 (19 is 0)
        assert_eq!(firh_on(bank(0), line, &op(-13)), (Some(0x30), Ok(()))); // 18 only
        assert_eq!(firh_on(bank(0), line, &op(-12)), (Some(0), Ok(())));
        assert_eq!(firh_on(bank(0), line, &op(-5)), (Some(0), Ok(())));
        // -4 to -1 stay below the line's start, repeating byte 0
        assert_eq!(firh_on(bank(0), [0x40, 0, 0], &op(-1)), (Some(0x40), Ok(())));
    }

    #[test]
    fn firh_reads_fixed_banks_one_and_two() {
        // E079 (usse-filter-banks): on a pedestal of 0x80 centred at byte 4, bank 1 set 2 is
        // about [-1 9 9 -1]/16 (a byte at +1 raised by 0x20 adds 18), bank 2 set 4 [1 2 2 2 1]/8
        // (+8 at the centre), bank 2 set 5 [1 1 1 1]/4 (+8 at -2)
        let ped = [0x8080_8080u32; 3];
        let raise = |byte: usize| {
            let mut l = ped;
            l[byte / 4] += 0x20 << (8 * (byte % 4));
            l
        };
        let op = |set: u32| format!("firh r10, r1, r2, r3, u8, rep, fcs{set}, #4, #0");
        assert_eq!(firh_on(bank(1), ped, &op(2)), (Some(128), Ok(())));
        assert_eq!(firh_on(bank(1), raise(5), &op(2)), (Some(146), Ok(())));
        assert_eq!(firh_on(bank(1), raise(5), &op(3)), (Some(146), Ok(())));
        assert_eq!(firh_on(bank(2), raise(4), &op(4)), (Some(136), Ok(())));
        assert_eq!(firh_on(bank(2), raise(2), &op(5)), (Some(136), Ok(())));
        // bank 2 sets 2 and 3 on a line of 0x40 lifted to 0xc0 at the positive tap's byte
        // (usse-filter-bank2): [1 -4 4 -1]/8 at -1..+2 and [1 -2 1/2 1/2] at -2..+1
        let lift = |byte: usize| {
            let mut l = [0x4040_4040u32; 3];
            l[byte / 4] += 0x80 << (8 * (byte % 4));
            l
        };
        assert_eq!(firh_on(bank(2), lift(5), &op(2)), (Some(64), Ok(())));
        let mut l = lift(5);
        l[1] += 0x20; // byte 4, the centre: -4/8
        assert_eq!(firh_on(bank(2), l, &op(2)), (Some(48), Ok(())));
        assert_eq!(firh_on(bank(2), lift(2), &op(3)), (Some(128), Ok(())));
        let mut l = lift(2);
        l[0] += 0x20 << 24; // byte 3, at -1: -2
        assert_eq!(firh_on(bank(2), l, &op(3)), (Some(64), Ok(())));
    }

    #[test]
    fn atst8_tests_alpha_against_the_reference() {
        // E083 (usse-alpha-test, 687 fill cases): src0 bits 31:24 against src2 bits 31:24 by
        // src2 bits 15:13 (never, less, equal, lequal, greater, notequal, gequal, always); a pass
        // writes src0 and sets the predicate, a fail leaves the destination and clears it
        let run_one = |a: u32, func: u32| {
            let src2 = 0x8000_0000 | func << 13;
            run_after(
                &[
                    &format!("mov r1, #0x{a:08x}"),
                    "mov r2, #0",
                    &format!("mov r3, #0x{src2:08x}"),
                    "mov r10, #0xa0a1a2a3",
                    "mov r20, #0",
                ],
                &["and.skipinv.testtanz.chan0 !r0, p0, #0x00000001, #1", "atst8 r10, p0, r1, r2, r3, nfb"],
            )
        };
        let want = [
            [false; 3],
            [true, false, false],
            [false, true, false],
            [true, true, false],
            [false, false, true],
            [true, false, true],
            [false, true, true],
            [true; 3],
        ];
        for (func, w) in want.iter().enumerate() {
            for (n, a) in [0x7f00_0001u32, 0x8000_0002, 0x8100_0003].into_iter().enumerate() {
                let (m, r) = run_one(a, func as u32);
                assert_eq!(r, Ok(()));
                let pass = w[n];
                assert_eq!((m.p[0], m.r[10]), (pass, if pass { a } else { 0xa0a1_a2a3 }), "{func} {a:x}");
            }
        }
        // its .c10 sources are not measured
        let (_, r) =
            run_after(&["mov r1, #0", "mov r2, #0", "mov r3, #0"], &["atst8.c10 r10, p0, r1, r2, r3, fb"]);
        assert!(stops_on(&r, "c10"), "{r:?}");
    }

    #[test]
    fn the_fill_s_unseen_state_changes_nothing() {
        // in a fill: pcoeff and depthf (E083), moest (E087, E109) and setfc (E109) and setm
        // (E099) leave the registers and predicates as a nop does
        let init =
            ["mov r1, #0x3f800000", "mov r2, #0x11223344", "mov r3, #0x00000001", "mov r17, #0x01010101"];
        let (base, _) = run_after(&init, &["nop"]);
        for op in [
            "pcoeff r1, r2, r3",
            "depthf r1, r2, r3, nfb",
            "depthf r1, r2, r3, fb",
            "depthf r1, r2, r3, optdwd",
            "moest r17, #2",
            "moest r17, #12",
            "setfc #1, #0",
            "setm #15",
        ] {
            let (m, r) = run_after(&init, &[op]);
            assert_eq!(r, Ok(()), "{op}");
            assert_eq!((m.r, m.p), (base.r, base.p), "{op}");
        }
        // depthf twosided did not run (E083 ran nfb, fb and optdwd)
        let (_, r) = run_after(&init, &["depthf r1, r2, r3, twosided, optdwd"]);
        assert!(stops_on(&r, "depthf twosided"), "{r:?}");
    }

    #[test]
    fn an_unmapped_bit_the_hardware_reads_stops_the_run() {
        // usse-encoding-bits-state (E296): bits outside every field the hardware reads
        let end = usse_isa::encode("nop.end", Core::Sgx545).unwrap();
        let wdf = usse_isa::encode("wdf drc0", Core::Sgx545).unwrap();
        let run_word = |w: u64| {
            let mut m = Machine { uniform: true, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
            (m.r[1], m.r[2], m.written.r) = (7, 2, 0b110);
            let r = m.run(&Program::new(&[w, wdf, end], Core::Sgx545), &mut mem, 100);
            (m, r)
        };
        // the base word, idiv r10, r1, r2, drc0: 3 rem 1
        let (m, r) = run_word(0xD010_0000_0140_0082);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 3, 1));
        // usse-encoding-bits-state (E296): enc[51] on setfc and imo and enc[44] on depthf hang
        // the job; imo has no semantics, and stops on the bit as on any read bit
        for (text, bit, ok) in [
            ("setfc #1, #0", 51, true),
            ("imo #1, #2, #3, #4", 51, false),
            ("depthf r1, r2, r3, nfb", 44, true),
        ] {
            let w = usse_isa::encode(text, Core::Sgx545).unwrap();
            assert_eq!(w >> bit & 1, 0, "{text}");
            let (_, r) = run_word(w);
            assert_eq!(r.is_ok(), ok, "{text}: {r:?}");
            let name = text.split(' ').next().unwrap();
            let (_, r) = run_word(w | 1 << bit);
            assert!(stops_on(&r, &format!("{name} with enc[{bit}] set")), "{text}: {r:?}");
        }
    }

    #[test]
    fn a_bank_6_destination_with_no_index_register_writes_nothing() {
        // hardware (usse-destination-bank6-temps, -moved, -outputs): a mov to bank 6 numbers 0,
        // 4, 8, 16, 64 and 124 (printed i.) changes no temporary, internal, index, attribute or
        // output register a fill reads; numbers 1-3 write i.l, i.h and both
        let init = ["mov r1, #0x00030002", "mov i.l, #0x00000000"];
        for n in [0u64, 4, 8, 16, 64, 124] {
            let w = 0x2889_1002_2000_0080 | n << 21;
            let end = usse_isa::encode("nop.end", Core::Sgx545).unwrap();
            let mut m = Machine { uniform: true, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
            (m.r[1], m.written.r) = (0x0003_0002, 0b10);
            let before = (m.r, m.i, m.index, m.pa, m.sa, m.o);
            let r = m.run(&Program::new(&[w, end], Core::Sgx545), &mut mem, 10);
            assert_eq!(r, Ok(()), "number {n}");
            assert_eq!((m.r, m.i, m.index, m.pa, m.sa, m.o), before, "number {n}");
        }
        let (m, r) = run_after(&init, &["mov i.lh, r1"]);
        assert_eq!((r, m.index), (Ok(()), [2, 3]));
    }

    #[test]
    fn a_bank_6_number_not_run_stops() {
        // only numbers 0, 4, 8, 16, 64 and 124 were run (usse-destination-bank6-temps): another
        // number with the low two bits clear may write somewhere, so the run stops on it
        for n in [12u64, 20, 32, 60, 120] {
            let w = 0x2889_1002_2000_0080 | n << 21;
            let end = usse_isa::encode("nop.end", Core::Sgx545).unwrap();
            let mut m = Machine { uniform: true, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
            (m.r[1], m.written.r) = (0x0003_0002, 0b10);
            let r = m.run(&Program::new(&[w, end], Core::Sgx545), &mut mem, 10);
            assert!(stops_on(&r, "bank 6 number"), "number {n}: {r:?}");
        }
    }

    #[test]
    fn idiv_repeats_up_to_sixteen_times() {
        // hardware (usse-idiv-enc47-grid): the repeat count is enc[47:44] + 1; iteration k
        // divides src1 + k by src2 + k, the quotient to dst + k and the remainder to dst + k + 1,
        // which the next iteration's quotient overwrites; by zero both are 0xffffffff
        let g1: [u32; 9] = [0x4013caac, 0x155bee39, 0x445960b, 0x9c3a01, 0xe33d1, 0x117ad, 0x1073, 0xdd, 9];
        let mut init: Vec<String> =
            g1.iter().enumerate().map(|(k, v)| format!("mov r{}, #0x{v:08x}", k + 1)).collect();
        init.push("mov r10, #0xa0a1a20a".into());
        let init: Vec<&str> = init.iter().map(String::as_str).collect();
        let (m, r) = run_after(&init, &["idiv.repeat2 r12, r1, r2, drc0", "wdf drc0"]);
        assert_eq!((r, &m.r[12..15]), (Ok(()), &[3, 5, 2][..]));
        // enc[47] alone: nine iterations (usse-idiv-enc47-grid case "enc47 r12, r1, r2")
        let (m, r) = run_after(&init, &["idiv.repeat9 r12, r1, r2, drc0", "wdf drc0"]);
        assert_eq!((r, &m.r[12..22]), (Ok(()), &[3, 5, 7, 0xb, 0xd, 0x11, 0x13, 0x18, 0, 9][..]));
        let mut zero = init.clone();
        zero[2] = "mov r3, #0x00000000";
        let (m, r) = run_after(&zero, &["idiv.repeat4 r12, r1, r2, drc0", "wdf drc0"]);
        assert_eq!((r, &m.r[12..17]), (Ok(()), &[3, 0xffffffff, 0, 0xb, 6][..]));
        // a source an earlier iteration writes reads that iteration's result or the old value
        // depending on the distance between them (usse-idiv-enc47-grid): it stops
        let (_, r) = run_after(&init, &["idiv.repeat9 r10, r1, r2, drc0", "wdf drc0"]);
        assert!(stops_on(&r, "DRC"), "{r:?}");
    }

    #[test]
    fn a_repeated_idiv_into_pa_stops() {
        // E367 ran the repeats into temporaries only: a pa destination repeated is not shown;
        // a single idiv into pa (the 11.7 case) still runs
        let init =
            ["mov r1, #0x00000064", "mov r2, #0x00000007", "mov r3, #0x00000009", "mov r4, #0x00000003"];
        let (m, r) = run_after(&init, &["idiv pa4, r1, r2, drc0", "wdf drc0"]);
        assert_eq!((r, m.pa[4], m.pa[5]), (Ok(()), 14, 2));
        let (_, r) = run_after(&init, &["idiv.repeat2 pa4, r1, r2, drc0", "wdf drc0"]);
        assert!(stops_on(&r, "idiv repeated into pa"), "{r:?}");
    }

    #[test]
    fn dual_issue_runs_two_operations() {
        let init = [
            "mov r1, #0x3fc00000", // 1.5
            "mov r2, #0x40100000", // 2.25
            "mov r3, #0x40400000", // 3
            "mov r4, #0x40a00000", // 5
            "mov r5, #0x40e00000", // 7
            "mov r6, #0x41300000", // 11
            "mov i0, r4",
            "mov i1, r5",
            "mov i2, r6",
        ];
        let f = |x: f32| x.to_bits();
        // hardware (dual-issue): the primary as alone, the secondary on i0-i2
        let (m, r) = run_after(&init, &["fmad r10, r1, r2, r3+fmad i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), f(6.375), f(46.0)));
        let (m, r) = run_after(&init, &["mov r10, r1+fmsa i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), f(1.5), f(102.0)));
        // a register source is the primary's source in that position; both
        // read before either writes
        let (m, r) = run_after(&init, &["fmad i0, r1, r2, r3+fadd i1, r2, i0"]);
        assert_eq!((r, m.i[0], m.i[1]), (Ok(()), f(6.375), f(7.25)));
        // pairs that share a unit (usse-dual-issue-shared): an fmsa secondary
        // writes the primary's result, a multiplying secondary of a
        // two-product primary gets its second product
        let (m, r) = run_after(&init, &["fmad r10, r1, r2, r3+fmsa i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), f(6.375), f(6.375)));
        // fadm: a*c + b*c
        let (m, r) = run_after(&init, &["fadm r10, r1, r2, r3+fadd i1, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[1]), (Ok(()), f(11.25), f(18.0)));
        let (m, r) = run_after(&init, &["fadm r10, r1, r2, r3+fmul i1, i1, i2"]);
        assert_eq!((r, m.i[1]), (Ok(()), f(6.75)));
        // a single-source secondary
        let (m, r) = run_after(&[&init[..], &["mov r7, #0x40800000"]].concat(), &["mov r10, r7+frcp i0, r7"]);
        assert_eq!((r, m.i[0]), (Ok(()), f(0.25)));
        // hardware (dual-issue): .repeat2 repeats both, the primary's operands
        // advancing, the secondary again on the internal registers
        let (m, r) = run_after(&init, &["fmad.repeat2 r10, r1, r2, r3+fadd i0, i0, i1"]);
        assert_eq!((r, m.r[10], m.r[11], m.i[0]), (Ok(()), f(6.375), f(11.75), f(19.0)));
        // fmad16 secondaries run on half lanes (usse-dual-issue-shared: next to
        // fmad the primary gives 0): (2, 1) * (3, 2) + (1, 1)
        let h = [
            "mov i0, #0x3c004000",
            "mov i1, #0x40004200",
            "mov i2, #0x3c003c00",
            "mov r1, #0x3fc00000",
            "mov r2, #0x40100000",
            "mov r3, #0x40400000",
        ];
        let (m, r) = run_after(&h, &["mov r10, r1+fmad16 i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), f(1.5), 0x42004700));
        let (m, r) = run_after(&h, &["fmad r10, r1, r2, r3+fmad16 i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), 0, 0x42004700));
        // fminmax + ima32 is not settled
        assert!(run_after(&init, &["fminmax r10, r1, r2, r3+ima32 i0, i0, i1, i2"]).1.is_err());
    }

    #[test]
    fn an_fddp_primary_writes_i0_over_its_secondary() {
        let init = [
            "mov r1, #0x3fc00000", // 1.5
            "mov r2, #0x40100000", // 2.25
            "mov r3, #0x40400000", // 3
            "mov r4, #0x40a00000", // 5
            "mov r5, #0x40e00000", // 7
            "mov r6, #0x41300000", // 11
            "mov i0, r4",
            "mov i1, r5",
            "mov i2, r6",
        ];
        let f = |x: f32| x.to_bits();
        // hardware (usse-form-coverage-dual 9, 10; x-dual 105, 111): d = s0 * s1, i0 =
        // s0 * s2; a mov or function secondary runs as alone, but i0 is fddp's
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+fexp i2, i1"]);
        assert_eq!((r, m.r[10], m.i[0], m.i[2]), (Ok(()), f(3.375), f(4.5), f(128.0)));
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+mov i1, r1"]);
        assert_eq!((r, m.i[0], m.i[1]), (Ok(()), f(4.5), f(1.5)));
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+mov i0, i1"]);
        assert_eq!((r, m.i[0], m.i[1]), (Ok(()), f(4.5), f(7.0)));
        // the arithmetic secondaries share the unit (usse-form-coverage-dual 6, 7;
        // usse-dual-issue-conflicts 11): their destination gets s0 * s2 as well
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+fadd i1, i1, i2"]);
        assert_eq!((r, m.i[0], m.i[1], m.i[2]), (Ok(()), f(4.5), f(4.5), f(11.0)));
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+fmul i2, i1, i2"]);
        assert_eq!((r, m.i[0], m.i[1], m.i[2]), (Ok(()), f(4.5), f(7.0), f(4.5)));
        // x-dual 96: an fmad secondary writes i0, the same value
        let (m, r) = run_after(&init, &["fddp r10, i0, r1, r2, r3+fmad i0, i0, i1, i2"]);
        assert_eq!((r, m.r[10], m.i[0]), (Ok(()), f(3.375), f(4.5)));
        // x-dual 97: fmad16 zeroes both (one case, not modelled)
        assert!(run_after(&init, &["fddp r10, i0, r1, r2, r3+fmad16 i0, i0, i1, i2"]).1.is_err());
    }

    #[test]
    fn a_test_takes_a_one_source_function() {
        let p = |init: &str, op: &str| {
            let (m, r) = run_after(
                &["mov r7, #0x00000000", "and.testtanz.chan0 !c0, p0, r7, r7", "mov r10, #0xa0a1a2a3", init],
                &[op],
            );
            r.map(|_| (m.r[10], m.p[0]))
        };
        // hardware (usse-form-coverage-test-fn 0, 1, 3, 4): the function's value, tested
        // as a float by its sign and zero at chan0
        assert_eq!(p("mov r1, #0x40000000", "frcp.testtaz.chan0 r10, p0, r1"), Ok((0x3f000000, false)));
        assert_eq!(p("mov r1, #0x7f800000", "frcp.testtaz.chan0 r10, p0, r1"), Ok((0, true)));
        assert_eq!(p("mov r1, #0x3f000000", "flog.testpat.chan0 !c0, p0, r1"), Ok((0xa0a1a2a3, false)));
        assert_eq!(p("mov r1, #0xc3480000", "fexp.testtanz.chan0 r10, p0, r1"), Ok((0, false)));
        // usse-form-coverage-test-fn 2: frsq of -4 is a NaN, which does not test negative
        assert_eq!(p("mov r1, #0xc0800000", "frsq.testnat.chan0 r10, p0, r1"), Ok((0x7fffffff, false)));
        // the other tests of a NaN are not measured
        assert!(p("mov r1, #0xc0800000", "frsq.testpat.chan0 r10, p0, r1").is_err());
    }

    #[test]
    fn more_groups_repeat_one_iteration_after_another() {
        // hardware (usse-form-coverage-bitwise-repeat 0, 4): an immediate source stays
        let i = ["mov r1, #0x80f01234", "mov r2, #0xffff0001"];
        let (m, r) = run_after(&i, &["or.repeat2 r10, r1, #0x00000F0F"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x80f01f3f, 0xffff0f0f));
        let (m, r) = run_after(&i, &["shl.repeat2 r10, r1, #0x00000003"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x078091a0, 0xfff80008));
        // usse-form-coverage-fsc-repeat 0
        let (m, r) = run_after(&["mov r1, #0x40000000", "mov r2, #0xbe800000"], &["frcp.repeat2 r10, r1"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x3f000000, 0xc0800000));
        // usse-form-coverage-pack-repeat 0: 1, -2.5 then -2.5, 65504
        let (m, r) = run_after(
            &["mov r1, #0x3f800000", "mov r2, #0xc0200000", "mov r3, #0x477fe000"],
            &["pckf16f32.repeat2 r10, r1.0, r2.0, nearest"],
        );
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0xc1003c00, 0x7bffc100));
        // usse-form-coverage-rlp-repeat 1: the carry runs through the predicate
        let (m, r) = run_after(
            &[
                "mov r7, #0x00000000",
                "and.testtanz.chan0 !c0, p1, r7, r7",
                "mov r1, #0x80000001",
                "mov r2, #0x7ffffffe",
                "mov r3, #0xc0000003",
            ],
            &["rlp.repeat3 r10, r1, p1"],
        );
        assert_eq!((r, &m.r[10..13], m.p[1]), (Ok(()), &[2, 0xfffffffd, 0x80000006][..], true));
        // usse-form-coverage-movc-movmsk-repeat 0: each iteration tests its own source 0
        let (m, r) = run_after(
            &[
                "mov r1, #0x00000000",
                "mov r2, #0x00000080",
                "mov r3, #0xaaaa0001",
                "mov r4, #0xbbbb0002",
                "mov r5, #0xcccc0003",
                "mov r6, #0xdddd0004",
            ],
            &["movc.i32.repeat2.tz r10, r1, r3, r5"],
        );
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0xaaaa0001, 0xdddd0004));
    }

    #[test]
    fn colour_and_dot_repeats_advance_every_operand() {
        let init = ["mov r1, #0xaa170513", "mov r2, #0xe433837f", "mov r3, #0x23e66c17"];
        // hardware (usse-colour-ops-dot-repeats): each iteration on the next registers
        let (m, r) = run_after(&init, &["sop2.repeat2 r10, r1, r2, s1, s2, add+asop2 s1a, s2a, add"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0xff0c4341, 0xd1da7141));
        let (m, r) = run_after(&init, &["u8dot3.repeat2 r10, Cx1, Ax1, r1, r2"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 0x11111111, 0x71717171));
    }

    #[test]
    fn smbo_offsets_the_operands_for_the_rest_of_the_task() {
        // hardware (usse-moe-smbo-operands, E087): the values offset dst, src0, src1, src2
        let init = |m: &mut Machine| {
            for k in 1..=8 {
                m.r[k] = 0x11 * k as u32;
            }
            m.written.r |= 0x1fe;
        };
        let go = |src: &[&str]| {
            let mut m = Machine::default();
            init(&mut m);
            let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
            let r = m.run(&prog(src), &mut mem, 1000);
            (m, r)
        };
        let (m, r) = go(&["smbo #0, #0, #1, #0", "mov r10, r1", "nop.end"]);
        assert_eq!((r, m.r[10]), (Ok(()), 0x22));
        let (m, r) = go(&["smbo #0, #0, #0, #1", "or r10, r1, r3", "nop.end"]);
        assert_eq!((r, m.r[10]), (Ok(()), 0x55));
        let (m, r) = go(&["smbo #1, #0, #0, #0", "mov r10, r1", "nop.end"]);
        assert_eq!((r, m.r[11], m.written.r >> 10 & 1), (Ok(()), 0x11, 0));
        let (_, r) = go(&["smbo #0, #0, #1, #0", "mov r10, pa1", "nop.end"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("smbo")));
    }

    #[test]
    fn ldr_reads_the_measured_id_registers_and_no_others() {
        // hardware (usse-memory-mem-forms, E090): 0x001c and 0x0020 of our SGX545
        let (m, r) = run(&["ldr r1, #7, drc0", "wdf drc0", "ldr r2, #8, drc0", "wdf drc0", "mov.end o0, r1"]);
        assert!(r.is_ok(), "{r:?}");
        assert_eq!((m.r[1], m.r[2]), (0x0115_0000, 0x0001_000d));
        let (_, r) = run(&["ldr r1, #9, drc0", "wdf drc0", "mov.end o0, r1"]);
        assert!(matches!(r, Err(Error::Unsupported { why, .. }) if why.contains("#9")));
    }

    #[test]
    fn a_predicated_branch_follows_the_quads_first_instance() {
        // hardware (usse-branch-divergent, E089): the quad branches as its top-left
        // instance's predicate says, whatever the others' say
        let p = prog(&[
            "mov r10, #0",
            "and.testtaz.chan0 !c0, p0, r1, r1",
            "p0 br #3",
            "or r10, r10, #1",
            "or r10, r10, #2",
            "or r10, r10, #4",
            "nop.end",
        ]);
        for (first, want) in [(0u32, 4u32), (1, 7)] {
            let mut quad: [Machine; 4] = Default::default();
            for (k, m) in quad.iter_mut().enumerate() {
                m.r[1] = if k == 0 { first } else { 1 - first };
                m.written.r |= 2;
            }
            let mut mem = Memory { base: 0, words: vec![] };
            assert_eq!(run_quad(&mut quad, &p, &mut mem, 100), Ok(()));
            assert!(quad.iter().all(|m| m.r[10] == want), "instance 0 r1 = {first}");
        }
    }

    #[test]
    fn a_quad_shares_i3_and_the_derivatives() {
        let p = prog(&[
            "mov i0, r1",
            "mov i2, r1",
            "mov r2, i3",
            "fdsx r3, r1, r1",
            "fdsy r4, r1, r1",
            "mov r5, i7",
            "nop.end",
        ]);
        let mut quad: [Machine; 4] = Default::default();
        for (k, m) in quad.iter_mut().enumerate() {
            m.r[1] = (10.0 * (k + 1) as f32).to_bits();
            m.written.r |= 2;
        }
        let mut mem = Memory { base: 0, words: vec![] };
        assert_eq!(run_quad(&mut quad, &p, &mut mem, 100), Ok(()));
        let f = |x: f32| x.to_bits();
        for (k, m) in quad.iter().enumerate() {
            // hardware (usse-internal-registers-per-pixel): i3 is the next
            // instance's i0 (TL, TR, BL, BR, round again)
            assert_eq!(m.r[2], quad[(k + 1) % 4].r[1], "i3 of {k}");
            // usse-gradients-fds-quad: TR - TL and BL - TL, the same in all four
            assert_eq!((m.r[3], m.r[4]), (f(10.0), f(20.0)), "fds of {k}");
            // usse-internal-registers-bank7: i7 is i2 of the next instance
            assert_eq!(m.r[5], quad[(k + 1) % 4].r[1], "i7 of {k}");
        }
        // one instance alone cannot say
        let (_, r) = run(&["mov r1, #0x00000000", "fdsx r3, r1, r1"]);
        assert!(r.is_err());
        // a repeat in a quad: iteration k from a + k, b + k (usse-gradients-fds-quad, usse-gradients-fds-incs)
        let p = prog(&["fdsx.repeat2 r10, r1, r1", "nop.end"]);
        let mut quad: [Machine; 4] = Default::default();
        for (k, m) in quad.iter_mut().enumerate() {
            m.r[1] = (10.0 * (k + 1) as f32).to_bits();
            m.r[2] = (100.0 * (k + 1) as f32).to_bits();
            m.written.r |= 6;
        }
        assert_eq!(run_quad(&mut quad, &p, &mut mem, 100), Ok(()));
        assert!(quad.iter().all(|m| (m.r[10], m.r[11]) == (f(10.0), f(100.0))));
    }

    #[test]
    fn a_uniform_fill_repeats_fds_by_its_incs() {
        // usse-gradients-fds-incs (a fill, r1-r4 = 1, 2, 4, 8): every instance alike,
        // so fdsx = fdsy = a - b; .incs Y advances a, Z advances b, X nothing
        let f = |x: f32| x.to_bits();
        for (op, want) in [
            ("fdsx.repeat2", -6.0),
            ("fdsy.repeat2.incs111", -6.0),
            ("fdsx.repeat2.incs001", -7.0),
            ("fdsy.repeat2.incs010", -2.0),
            ("fdsx.repeat2.incs100", -3.0),
            ("fdsy.repeat2.incs011", -6.0),
        ] {
            let mut m = Machine { uniform: true, ..Machine::default() };
            for (k, x) in [1.0f32, 2.0, 4.0, 8.0].into_iter().enumerate() {
                m.r[1 + k] = f(x);
                m.written.r |= 2 << k;
            }
            let mut mem = Memory { base: 0, words: vec![] };
            let p = prog(&[&format!("{op} r10, r1, r3"), "nop.end"]);
            assert_eq!(m.run(&p, &mut mem, 100), Ok(()), "{op}");
            assert_eq!((m.r[10], m.r[11]), (f(-3.0), f(want)), "{op}");
        }
    }

    #[test]
    fn efo_gpiext_reaches_across_the_quad() {
        // each instance k: i0 = k + 1, i1 = 10 (k + 1), i2 = 100 (k + 1), r1 = 1
        let p = prog(&[
            "efo.gpiext r10= a0, i0 = a0, !i1 = a1, a0=m0+m1, a1=i1+i0, m0=src1*i0, m1=src2*i1, r1, r1, r1",
            "mov r11, i2",
            "efo.gpiext r12= a1, !i0 = a0, i1 = a1, a0=m0+i0, a1=i1+m1, m0=src0*src2, m1=src1*src2, r1, r1, r1",
            "nop.end",
        ]);
        let f = |x: f32| x.to_bits();
        let mut quad: [Machine; 4] = Default::default();
        for (k, m) in quad.iter_mut().enumerate() {
            let n = (k + 1) as f32;
            m.i = [f(n), f(10.0 * n), f(100.0 * n), 0];
            m.written.i = 7;
            m.r[1] = f(1.0);
            m.written.r |= 2;
        }
        let mut mem = Memory { base: 0, words: vec![] };
        assert_eq!(run_quad(&mut quad, &p, &mut mem, 100), Ok(()));
        for (k, m) in quad.iter().enumerate() {
            let n = (k + 1) as f32;
            // hardware (usse-internal-registers-efo-gpiext-quad): the multipliers read own i2 for i0
            // and own i0 for i1; a write of i0 goes to own i2
            assert_eq!((m.r[10], m.r[11]), (f(101.0 * n), f(101.0 * n)), "instance {k}");
            assert_eq!(m.r[12], f(10.0 * n + 1.0));
        }
        // the four i1 writes end in the top-right i0, as the bottom-right's
        assert_eq!(quad[1].i[0], f(41.0));
        assert_eq!((quad[0].i[0], quad[2].i[0], quad[3].i[0]), (f(1.0), f(3.0), f(4.0)));
    }

    const SMLSI: &str = "incrementmode, incrementmode, incrementmode, incrementmode, #0, #0, #0";

    #[test]
    fn smlsi_sets_the_destination_and_source_increments() {
        // hardware (usse-repeat-smlsi): increment 0 is the destination's, 2 the
        // source 1's (mov's source)
        let (m, r) = run_after(&R1_R7, &[&format!("smlsi #2, #1, #1, #1, {SMLSI}"), "mov.repeat2 r1, r5"]);
        assert_eq!((r, &m.r[1..4]), (Ok(()), &[0x55, 0x22, 0x66][..]));
        let (m, r) = run_after(&R1_R7, &[&format!("smlsi #1, #1, #0, #1, {SMLSI}"), "mov.repeat2 r1, r5"]);
        assert_eq!((r, &m.r[1..4]), (Ok(()), &[0x55, 0x55, 0x33][..]));
        // hardware (usse-moe-smlsi-three-sources): on three sources increment 1 is
        // source 0's, 2 source 1's and 3 source 2's: r1 * r3 + r5, then
        // r3 * r4 + r6
        let (m, r) =
            run_after(&ABC, &[&format!("smlsi #1, #2, #1, #1, {SMLSI}"), "fmad.repeat2 r10, r1, r3, r5"]);
        let f = |x: f32| x.to_bits();
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), f(105.0), f(235.0)));
    }

    /// A program of assembly lines and raw words ("0x" and 16 hex digits).
    fn run_mixed(m: &mut Machine, src: &[&str]) -> Result<(), Error> {
        let words: Vec<u64> = src
            .iter()
            .map(|t| match t.strip_prefix("0x") {
                Some(h) => u64::from_str_radix(h, 16).unwrap(),
                None => usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}")),
            })
            .collect();
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000)
    }

    /// The x-form2 probes' inputs: r1-r3 half pairs (1.5, -2.0), (0.75, 3.0),
    /// (-0.5, 10.0) as (.flt16.0, .flt16.2), i0-i2 = 5.0, -0.75, 2.0.
    const HALVES: [&str; 9] = [
        "mov r1, #0xc0003e00",
        "mov r2, #0x42003a00",
        "mov r3, #0x4900b800",
        "mov r4, #0x40a00000",
        "mov r5, #0xbf400000",
        "mov r6, #0x40000000",
        "mov i0, r4",
        "mov i1, r5",
        "mov i2, r6",
    ];

    fn halves(op: &str) -> (Machine, Result<(), Error>) {
        let mut m = Machine { uniform: true, ..Machine::default() };
        let r = run_mixed(&mut m, &[&HALVES[..], &[op, "nop.end"]].concat());
        (m, r)
    }

    #[test]
    fn half_float_forms_read_a_half_of_a_register() {
        let f = |x: f32| x.to_bits();
        // hardware (usse-form-coverage-form2-flt16 0-11): each operation as on f32
        // sources, a source the half of rN its component names
        for (case, op, want) in [
            (0, "fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0", 4.0),
            (1, "fmsa r10, r1.flt16.2, r2.flt16.0, r3.flt16.2", 11.5),
            (2, "fsubflr r10, r1.flt16, r2.flt16.2", -1.5),
            (3, "fsubflr r10, r3.flt16.2, r1.flt16.2", 12.0),
            (4, "fdp r10, r1.flt16.0, r2.flt16.2", 4.5),
            (5, "fdpc r10, cp0, r1.flt16, r2.flt16.2", 4.5),
            (8, "fmaxmin r10, r1.flt16.0, r2.flt16.2, r3.flt16.0", 3.0),
            (9, "fminmax r10, r1.flt16.2, r2.flt16.0, r3.flt16.2", 0.75),
            (10, "fdsx r10, r1.flt16.0, r2.flt16.2", -1.5),
            (11, "fdsy r10, r1.flt16.2, r2.flt16.0", -2.75),
        ] {
            let (m, r) = halves(op);
            assert_eq!((r, m.r[10]), (Ok(()), f(want)), "usse-form-coverage-form2-flt16 {case}: {op}");
        }
        // usse-form-coverage-form2-flt16 6, 7: fddp and fddpc, s0 * s2 into i0
        for op in [
            "fddp r10, i0, r1.flt16, r2.flt16.2, r3.flt16",
            "fddpc r10, i0, cp0, cp1, r1.flt16, r2.flt16.2, r3.flt16",
        ] {
            let (m, r) = halves(op);
            assert_eq!((r, m.r[10], m.i), (Ok(()), f(4.5), [f(-0.75), f(-0.75), f(2.0), 0]), "{op}");
        }
    }

    #[test]
    fn half_float_forms_stop_where_not_measured() {
        // a register numbered as a whole one, a modifier, a repeat
        for op in [
            "fmad r10, r1, r2.flt16.2, r3.flt16.0",
            "fmad r10, r1.flt16.0, r2.neg.flt16.2, r3.flt16.0",
            "fmad r10, r1.flt16.0, r2.flt16.2, c3",
            "fmad.repeat2 r10, r1.flt16.0, r2.flt16.2, r3.flt16.0",
        ] {
            let (_, r) = halves(op);
            assert!(matches!(r, Err(Error::Unsupported { .. })), "{op}: {r:?}");
        }
        // a half infinity
        let (_, r) = halves("fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0");
        assert!(r.is_ok());
        let mut m = Machine::default();
        let r = run_mixed(&mut m, &["mov r1, #0x7c003c00", "fdp r10, r1.flt16.2, r1.flt16.0", "nop.end"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
    }

    #[test]
    fn half_float_dual_issue_pairs_as_on_f32() {
        let f = |x: f32| x.to_bits();
        // hardware (usse-form-coverage-form2-dual-flt16): the primary's float sources
        // read halves; ima32, mov and a secondary sharing a primary source
        // read the whole register
        for (case, op, r10, i) in [
            // fmsa of fmad: the primary's result
            (
                0,
                "fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0+fmsa i0, i0, i1, i2",
                f(4.0),
                [f(4.0), f(-0.75), f(2.0)],
            ),
            // ima32's b is the primary's source 1, r2 whole
            (
                1,
                "fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0+ima32 i1, i1, i0, i2",
                f(4.0),
                [f(5.0), 0xc0000000, f(2.0)],
            ),
            (
                2,
                "fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0+fmul i2, i0, i1",
                f(4.0),
                [f(5.0), f(-0.75), f(-3.75)],
            ),
            (
                36,
                "fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0+mov i0, r2.flt16.2",
                f(4.0),
                [0x42003a00, f(-0.75), f(2.0)],
            ),
            // ima32 multiplies the whole registers
            (
                7,
                "ima32 r10, r1.flt16, r2.flt16.2, r3.flt16+fmsa i0, i0, i1, i2",
                0x570cb800,
                [f(23.5), f(-0.75), f(2.0)],
            ),
            (
                8,
                "ima32 r10, r1.flt16, r2.flt16.2, r3.flt16+ima32 i1, i1, i0, i2",
                0x570cb800,
                [f(5.0), 0x570cb800, f(2.0)],
            ),
            (15, "mov r10, r2.flt16.2+ima32 i1, i1, i0, i2", 0x42003a00, [f(5.0), 0xc8000000, f(2.0)]),
            (16, "mov r10, r2.flt16.2+fmul i2, i0, i1", 0x42003a00, [f(5.0), f(-0.75), f(-3.75)]),
            // fddp: d = s0 * s1, i0 = s0 * s2; an ima32 secondary as alone
            (
                22,
                "fddp r10, i0, r1.flt16, r2.flt16.2, r3.flt16+fmsa i0, i0, i1, i2",
                f(4.5),
                [f(-0.75), f(-0.75), f(2.0)],
            ),
            (
                23,
                "fddp r10, i0, r1.flt16, r2.flt16.2, r3.flt16+ima32 i1, i1, i0, i2",
                f(4.5),
                [f(-0.75), 0xc0000000, f(2.0)],
            ),
            (
                24,
                "fddp r10, i0, r1.flt16, r2.flt16.2, r3.flt16+fmul i2, i0, i1",
                f(4.5),
                [f(-0.75), f(-0.75), f(-0.75)],
            ),
            (
                37,
                "fddp r10, i0, r1.flt16, r2.flt16.2, r3.flt16+mov i1, r3.flt16",
                f(4.5),
                [f(-0.75), 0x4900b800, f(2.0)],
            ),
            // fssq: an fmsa secondary gets the primary's result, fmul the second square
            (29, "fssq r10, r2.flt16.2, r3.flt16+fmsa i0, i0, i1, i2", f(9.25), [f(9.25), f(-0.75), f(2.0)]),
            (
                30,
                "fssq r10, r2.flt16.2, r3.flt16+ima32 i1, i1, i0, i2",
                f(9.25),
                [f(5.0), 0xc0000000, f(2.0)],
            ),
            (31, "fssq r10, r2.flt16.2, r3.flt16+fmul i2, i0, i1", f(9.25), [f(5.0), f(-0.75), f(0.25)]),
            (32, "fssq r10, r2.flt16.2, r3.flt16+fexp i1, i2", f(9.25), [f(5.0), f(4.0), f(2.0)]),
        ] {
            let (m, r) = halves(op);
            assert_eq!(
                (r, m.r[10], [m.i[0], m.i[1], m.i[2]]),
                (Ok(()), r10, i),
                "usse-form-coverage-form2-dual-flt16 {case}: {op}"
            );
        }
        // usse-form-coverage-form2-dual-flt16 20, 35: the raw secondary movs of a shared source
        for (w, want) in [("0xD86443E0014F6280", 0x42003a00), ("0xDC6C83E0014F62C6", 0x4900b800)] {
            let (m, r) = halves(w);
            assert_eq!((r, m.i[1]), (Ok(()), want), "{w}");
        }
        // pairs not measured on halves stop
        let (_, r) = halves("fmad r10, r1.flt16.0, r2.flt16.2, r3.flt16.0+fadd i0, i0, i1");
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
    }

    /// The x-form2 test probes: r16 = p set, r17 = p clear around the test.
    fn tested(a: u32, b: u32, op: &str) -> (Machine, Result<(), Error>) {
        let mut m = Machine::default();
        let (pa, pb) = (format!("mov r1, #{a:#010x}"), format!("mov r2, #{b:#010x}"));
        let p = if op.contains(", p1,") || op == "0x480414840155C082" { "p1" } else { "p0" };
        let (set, clear) = (format!("{p} mov r16, #0x00000001"), format!("!{p} mov r17, #0x00000001"));
        // the mask forms (class 15) write no predicate, so nothing reads one after them
        let mask = op.contains("msk") || op.starts_with("0x78");
        let (pre, post): (&[&str], &[&str]) = if mask {
            (&[&pa, &pb, "mov r16, #0x00000000", "mov r17, #0x00000000", op], &["nop.end"])
        } else {
            (&[&pa, &pb, "mov r16, #0x00000000", "mov r17, #0x00000000", op], &[&set, &clear, "nop.end"])
        };
        let r = run_mixed(&mut m, &[pre, post].concat());
        (m, r)
    }

    #[test]
    fn the_test_group_with_enc50_tests_as_without() {
        let f = |x: f32| x.to_bits();
        // hardware (usse-form-coverage-form2-test-e50): value and predicate as the
        // class-9 forms; uadd8.sat saturates each byte, fpadd8 alike
        for (case, a, b, op, v, p) in [
            (0, 0xfffffffe, 5, "0x4804188001570082", 3, true),
            (1, 0x00030001, 0x00010005, "0x480414840155C082", 0x0002fffc, true),
            (3, 0x7f80ff10, 0x01ff0120, "uadd8.sat.testtaz.andall r10, p0, r1, r2", 0x80ffff30, false),
            (4, f(1.5), f(-2.25), "0x4804188001500082", f(-0.75), false),
            (5, f(1.5), f(-2.25), "0x4804148001534082", f(-3.375), true),
            (6, f(-0.5), f(0.5), "0x4804188001528082", f(0.5), true),
            (7, f(-0.5), f(0.5), "0x4804148001524082", f(-0.5), true),
            (8, f(-4.0), 0, "0x4804188001510080", f(-0.25), false),
            (9, 0x7f80ff10, 0x01ff0120, "0x480418800159C082", 0x80ffff30, true),
        ] {
            let (m, r) = tested(a, b, op);
            assert_eq!(
                (r, m.r[10], m.r[16], m.r[17]),
                (Ok(()), v, p as u32, !p as u32),
                "usse-form-coverage-form2-test-e50 {case}"
            );
        }
        // case 2: isub8.sat's bytes are not settled
        let (_, r) = tested(0x7f80ff10, 0x01ff0120, "isub8.sat.testnat.chan0 r10, p0, r1, r2");
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
    }

    #[test]
    fn unorm8_operations_per_byte() {
        // hardware (usse-unorm8-add-sub-mul, usse-unorm8-mul): with enc[50] clear, fpmul8 is
        // round(x * y / 255) per byte, fpsub8 x - y clamped at 0 and fpadd8 x + y clamped
        // at 255; chan0 tests byte 0's unclamped result (3 - 85 writes 0, not zero)
        for (op, a, b, v, p) in [
            ("fpmul8", 0x0180ffff, 0xff8080ff, 0x014080ff, false),
            ("fpmul8", 0xfe11c87f, 0xfe0f647f, 0xfd014e3f, false),
            ("fpmul8", 0xff10fa81, 0x01100281, 0x01010241, false),
            ("fpsub8", 0x0180ffff, 0xff8080ff, 0x00007f00, true),
            ("fpsub8", 0x40005503, 0xc0c80355, 0x00005200, false),
            ("fpsub8", 0xff10fa81, 0x01100281, 0xfe00f800, true),
            ("fpadd8", 0xfe11c87f, 0xfe0f647f, 0xff20fffe, false),
        ] {
            let (m, r) = tested(a, b, &format!("{op}.testtaz.chan0 r10, p0, r1, r2"));
            assert_eq!(
                (r, m.r[10], m.r[16], m.r[17]),
                (Ok(()), v, p as u32, !p as u32),
                "{op} {a:#x} {b:#x}"
            );
        }
    }

    #[test]
    fn a_fetch_steps_by_one_and_drops_past_the_temporaries() {
        // hardware (usse-numbered-modifiers-family-fetch, usse-numbered-modifiers-family-fetch-dst): at task start, before any
        // smlsi, .fetchN loads N dwords into consecutive registers, from one element after a
        // base-plus-offset address; (usse-numbered-modifiers-family-fetch-edge) with 32 temporaries a fetch that
        // would run past r31 writes nothing
        let mem = || Memory { base: 0x1000, words: (0..64).map(|i| 0xd000_0000 + i).collect() };
        for n in [2u32, 9, 16] {
            let mut m = Machine::default();
            let p = prog(&[
                "mov r1, #0x00001000",
                &format!("ldad.fetch{n} r20, [r1,+#0], drc0"),
                "wdf drc0",
                "nop.end",
            ]);
            assert_eq!(m.run(&p, &mut mem(), 100), Ok(()), "fetch{n}");
            for k in 0..n as usize {
                assert_eq!(m.r[20 + k], 0xd000_0001 + k as u32, "fetch{n} r{}", 20 + k);
            }
        }
        for (d, loaded) in [(28, true), (29, false), (30, false)] {
            let mut m = Machine { temps: 32, ..Machine::default() };
            let mut src: Vec<String> =
                (0..4).map(|k| format!("mov r{}, #0x{:08x}", 28 + k, 0xe1e2_e300u32 + k)).collect();
            src.push("mov r20, #0x00001000".into());
            src.push(format!("ldad.fetch4 r{d}, [r20,+#0], drc0"));
            src.extend(["wdf drc0".into(), "nop.end".into()]);
            let src: Vec<&str> = src.iter().map(|s| s.as_str()).collect();
            assert_eq!(m.run(&prog(&src), &mut mem(), 100), Ok(()), "fetch4 r{d}");
            let want: Vec<u32> =
                (0..4).map(|k| if loaded { 0xd000_0001 + k } else { 0xe1e2_e300 + k }).collect();
            assert_eq!(m.r[28..32].to_vec(), want, "fetch4 r{d}");
        }
    }

    #[test]
    fn smlsi_swizzle_mode_offsets_each_iteration() {
        // hardware (usse-moe-swizzle, E097): an operand in swizzle mode takes iteration
        // k's register offset from the swizzle's k-th component (x 0 ... w 3), k = 0 too
        let i: Vec<String> = (1..=4).map(|n| format!("mov r{n}, #0x{:08x}", n * 0x0101_0101)).collect();
        let i: Vec<&str> = i.iter().map(|s| s.as_str()).collect();
        let swz = |modes: &str, ops: &str| format!("smlsi {ops}, {modes}, #0, #0, #0");
        for (smlsi, want) in [
            (
                swz("incrementmode, incrementmode, swizzlemode, incrementmode", "#1, #0, swizzle(wzyx), #0"),
                [4u32, 3, 2, 1],
            ),
            (
                swz("incrementmode, incrementmode, swizzlemode, incrementmode", "#1, #0, swizzle(yyyy), #0"),
                [2, 2, 2, 2],
            ),
            (
                swz("swizzlemode, incrementmode, incrementmode, incrementmode", "swizzle(wzyx), #0, #1, #0"),
                [4, 3, 2, 1],
            ),
        ] {
            let (m, r) = run_after(&i, &[&smlsi, "mov.repeat4 r20, r1"]);
            assert_eq!(r, Ok(()), "{smlsi}");
            assert_eq!(m.r[20..24].to_vec(), want.map(|n| n * 0x0101_0101).to_vec(), "{smlsi}");
        }
        // hardware (usse-moe-swizzle 0-2): an instruction that does not repeat takes component
        // x's offset (wzyx: +3, yyyy: +1), stores' address operands stay
        for (s, want) in [("wzyx", 4u32), ("yyyy", 2), ("xxxx", 1)] {
            let smlsi = swz(
                "incrementmode, incrementmode, swizzlemode, incrementmode",
                &format!("#1, #0, swizzle({s}), #0"),
            );
            let (m, r) = run_after(&i, &[&smlsi, "mov r20, r1"]);
            assert_eq!((r, m.r[20]), (Ok(()), want * 0x0101_0101), "{s}");
        }
    }

    #[test]
    fn smoa_modes_map_an_operands_first_register() {
        // hardware (x-smoa-*, E105): with i = the register + the operand's smoa offset
        // and M = its smr range - 1, the mode maps the first register once (none i, clamp
        // min(i, M), mirror 2M - i past M, repeat i - (M + 1) past M) and the iterations
        // step by one from there; smr and smoa fields are dst, src0, src1, src2
        let i: Vec<String> = (0..47).map(|n| format!("mov r{n}, #0x{:08x}", 0xe0e1_e200u32 + n)).collect();
        let i: Vec<&str> = i.iter().map(|s| s.as_str()).collect();
        let mark = |n: u32| 0xe0e1_e200 + n;
        for (smr, smoa, op, dst, src) in [
            ("#4, #4, #4, #4", "#2, #0, #0, #0, none, none, none, none", "mov.repeat8 r20, r30", 22, 30),
            ("#12, #12, #12, #12", "#0, #0, #0, #0, clamp, none, none, none", "mov.repeat8 r20, r30", 11, 30),
            ("#12, #12, #12, #12", "#0, #0, #0, #0, mirror, none, none, none", "mov.repeat8 r20, r30", 2, 30),
            ("#12, #12, #12, #12", "#0, #0, #0, #0, repeat, none, none, none", "mov.repeat8 r20, r30", 8, 30),
            ("#24, #24, #24, #24", "#0, #0, #0, #0, clamp, none, none, none", "mov.repeat8 r20, r30", 20, 30),
            ("#16, #16, #16, #16", "#3, #0, #0, #0, mirror, none, none, none", "mov.repeat8 r20, r30", 7, 30),
            (
                "#10, #10, #10, #10",
                "#3, #0, #0, #0, repeat, none, none, none",
                "mov.repeat8 r20, r30",
                13,
                30,
            ),
            ("#4, #4, #4, #4", "#0, #0, #0, #0, none, none, clamp, none", "mov.repeat8 r40, r20", 40, 3),
            ("#4, #4, #4, #4", "#0, #0, #0, #0, none, none, repeat, none", "mov.repeat8 r40, r20", 40, 16),
            ("#0, #0, #4, #0", "#0, #0, #0, #0, none, none, clamp, none", "mov.repeat8 r40, r20", 40, 3),
            ("#4, #0, #0, #0", "#0, #0, #0, #0, clamp, none, none, none", "mov.repeat8 r20, r30", 3, 30),
            ("#4, #4, #4, #4", "#6, #0, #0, #0, clamp, none, none, none", "mov r20, r1", 3, 1),
        ] {
            let (m, r) = run_after(&i, &[&format!("smr {smr}"), &format!("smoa {smoa}"), op]);
            assert_eq!(r, Ok(()), "{smr} {smoa} {op}");
            let n = if op.contains("repeat8") { 8 } else { 1 };
            let want: Vec<u32> = (0..n).map(|k| mark(src + k)).collect();
            assert_eq!(m.r[dst as usize..(dst + n) as usize].to_vec(), want, "{smr} {smoa} {op}");
        }
        // a first register below r0 is not modelled (writes there vanish, reads are stale)
        let (_, r) = run_after(
            &i,
            &["smr #8, #8, #8, #8", "smoa #0, #0, #0, #0, mirror, none, none, none", "mov.repeat8 r20, r30"],
        );
        assert!(matches!(r, Err(Error::Unsupported { .. })));
    }

    #[test]
    fn eld_loads_an_element_below_its_limit() {
        // hardware (usse-cache-control-eld-address, usse-cache-control-eld-limit, E098): eldd/eldq load the dword or
        // quad at element index + offset from the base when it is below the limit (the
        // second operand), else zeros
        let mem = || Memory { base: 0x1000, words: (0..64).map(|i| 0xd000_0000 + i).collect() };
        for (t, idx, off, lim, want) in [
            ("d", 0u32, 0u32, 1u32, vec![0xd000_0000u32]),
            ("d", 3, 0, 4, vec![0xd000_0003]),
            ("d", 4, 0, 4, vec![0]),
            ("d", 1, 2, 4, vec![0xd000_0003]),
            ("d", 2, 2, 4, vec![0]),
            ("d", 0, 0, 0, vec![0]),
            ("q", 1, 0, 4, vec![0xd000_0004, 0xd000_0005, 0xd000_0006, 0xd000_0007]),
            ("q", 0, 3, 4, vec![0xd000_000c, 0xd000_000d, 0xd000_000e, 0xd000_000f]),
            ("q", 4, 0, 4, vec![0, 0, 0, 0]),
        ] {
            let mut m = Machine::default();
            let p = prog(&[
                "mov r46, #0x00001000",
                &format!("mov r45, #0x{idx:08x}"),
                &format!("mov r44, #0x{lim:08x}"),
                &format!("eld{t} r20, [r46, r45, #{off}], r44, drc0"),
                "wdf drc0",
                "nop.end",
            ]);
            assert_eq!(m.run(&p, &mut mem(), 100), Ok(()), "eld{t} {idx} {off} {lim}");
            assert_eq!(m.r[20..20 + want.len()].to_vec(), want, "eld{t} {idx} {off} {lim}");
        }
    }

    #[test]
    fn unsigned_lane_operations_wrap_or_clamp_per_lane() {
        // hardware (usse-lane-integer-rogue-int): each byte or 16-bit lane on its own,
        // unsigned, wrapping; .sat clamps the unsigned bytes to 255, and
        // iadd8.sat writes the wrapped bytes (0x7f + 0x02 is 0x81, 0x80 + 0x80
        // is 0x00); chan0 tests byte 0's non-zero result
        let (b8, c8) = (0x80ff7f02, 0x80020203);
        let (b16, c16) = (0xffff8000, 0x00028000);
        for (case, a, b, op, v) in [
            (0, b8, c8, "umul8", 0x00fefe06),
            (1, b8, c8, "umul8.sat", 0xfffffe06),
            (2, b8, c8, "uadd8", 0x00018105),
            (3, b8, c8, "uadd8.sat", 0xffff8105),
            (4, b8, c8, "usub8", 0x00fd7dff),
            (5, b8, c8, "imul8", 0x00fefe06),
            (6, b8, c8, "iadd8.sat", 0x00018105),
            (7, b16, c16, "uadd16", 0x00010000),
            (8, b16, c16, "umul16", 0xfffe0000),
            (9, b16, c16, "iadd16", 0x00010000),
            (10, b16, c16, "imul16", 0xfffe0000),
        ] {
            let (m, r) = tested(a, b, &format!("{op}.testtaz.chan0 r10, p0, r1, r2"));
            assert_eq!(
                (r, m.r[10], m.r[16], m.r[17]),
                (Ok(()), v, 0, 1),
                "usse-lane-integer-rogue-int {case}"
            );
        }
    }

    #[test]
    fn class_15_tests_into_a_mask() {
        let f = |x: f32| x.to_bits();
        // hardware (usse-form-coverage-form2-test-mask): bmsk byte k is chanN k's test,
        // wmsk half k chan 2k's, dmsk chan0's (a channel without a lane tests
        // as a positive non-zero value)
        for (case, a, b, op, v) in [
            (0, 0x7f80ff10, 0x01ff0120, "xor.testtanz.bmsk r10, r1, r2", 0xffffffff),
            (1, 0x00ff0000, 0xff00ff00, "and.testtaz.dmsk r10, r1, r2", 0xffffffff),
            (2, f(1.5), f(-2.25), "fadd.testpat.bmsk r10, r1, r2", 0xffffff00),
            (3, 0x00030001, 0x00010005, "iadd16.testtanz.dmsk r10, r1, r2", 0xffffffff),
            (4, f(-4.0), 0, "frcp.testpat.wmsk r10, r1", 0xffff0000),
            (5, 0x00030001, 0x00010005, "0x780412A001558082", 0xffffffff),
            (6, 0xfffe0003, 0x00050004, "0x7804189001560082", 0x0000ffff),
            (7, 0x7f80ff10, 0x01ff0120, "iadd8.sat.testtanz.bmsk r10, r1, r2", 0xffff00ff),
            (8, f(1.5), f(-2.25), "0x780418A001500082", 0),
            (9, f(-0.5), f(0.5), "0x780418A001528082", 0xffffffff),
            (10, f(-4.0), 0, "0x780418A001510080", 0),
            (11, 0x7f80ff10, 0x01ff0120, "0x780411A00159C082", 0),
        ] {
            let (m, r) = tested(a, b, op);
            assert_eq!((r, m.r[10]), (Ok(()), v), "usse-form-coverage-form2-test-mask {case}: {op}");
        }
        // case 12: fpmul8's bytes are not settled
        let (_, r) = tested(0x7f80ff10, 0x01ff0120, "0x7804128001594082");
        assert!(matches!(r, Err(Error::Unsupported { .. })), "{r:?}");
    }
}

/// The float datapath, as the hardware vectors show it: f32 operations
/// rounded to nearest even (Rust's f32 add and mul are correctly rounded),
/// denormal inputs and results flushed to a zero of the same sign, infinities
/// kept and NaN results 0x7fc00000.
mod flt {
    use super::Error;

    pub fn modify(v: u32, neg: bool, abs: bool) -> u32 {
        let v = if abs { v & 0x7fff_ffff } else { v };
        if neg { v ^ 0x8000_0000 } else { v }
    }

    /// An operand: a denormal flushes to a zero of its sign; infinities and
    /// NaNs pass (hardware, usse-fmad-move, usse-dot-products-fdp-specials, usse-float-misc-fadm-fmsa-fsubflr).
    fn input(v: u32) -> Result<f32, Error> {
        Ok(f32::from_bits(if v >> 23 & 0xff == 0 { v & 0x8000_0000 } else { v }))
    }

    /// A result: denormals flush, an infinity stays, and every NaN is
    /// 0x7fc00000 (hardware: fmad of a NaN, inf * 0, inf - inf).
    fn output(x: f32) -> Result<u32, Error> {
        if x.is_nan() {
            return Ok(0x7fc0_0000);
        }
        let b = x.to_bits();
        Ok(if b >> 23 & 0xff == 0 { b & 0x8000_0000 } else { b })
    }

    /// Whether a value is an infinity or a NaN (for the ops whose specials
    /// are not measured).
    pub fn special(v: u32) -> bool {
        v >> 23 & 0xff == 0xff
    }

    pub fn mul(a: u32, b: u32) -> Result<u32, Error> {
        output(input(a)? * input(b)?)
    }

    pub fn add(a: Result<u32, Error>, b: u32) -> Result<u32, Error> {
        output(input(a?)? + input(b)?)
    }

    pub fn sub(a: u32, b: Result<u32, Error>) -> Result<u32, Error> {
        output(input(a)? - input(b?)?)
    }

    /// IEEE minNum/maxNum (hardware, usse-float-minmax-fminmax-specials, usse-float-minmax-allnan): a NaN
    /// loses to a number, -0 is below +0, and of two NaNs the second stays
    /// with its payload.
    fn minmax(a: u32, b: u32, max: bool) -> Result<u32, Error> {
        let nan = |v: u32| v >> 23 & 0xff == 0xff && v & 0x7f_ffff != 0;
        let flush = |v: u32| if v >> 23 & 0xff == 0 { v & 0x8000_0000 } else { v };
        let (a, b) = (flush(a), flush(b));
        Ok(match (nan(a), nan(b)) {
            (_, true) if nan(a) => b,
            (true, false) => b,
            (false, true) => a,
            _ => {
                // order as numbers, -0 below +0: compare the total order key
                let key = |v: u32| if v >> 31 != 0 { !v as i64 } else { v as i64 | 1 << 32 };
                if (key(a) < key(b)) == max { b } else { a }
            }
        })
    }

    pub fn min(a: u32, b: u32) -> Result<u32, Error> {
        minmax(a, b, false)
    }

    pub fn max(a: u32, b: u32) -> Result<u32, Error> {
        minmax(a, b, true)
    }

    /// Whether an f32 (or f16) value is at least 0.5; a NaN is not.
    pub fn at_least_half(b: u32, half: bool) -> Result<bool, Error> {
        let x = if half {
            let (e, m) = (b >> 10 & 31, b & 1023);
            let mag = match e {
                31 if m != 0 => return Ok(false),
                31 => f64::INFINITY,
                0 => m as f64 * 2f64.powi(-24),
                _ => (1024 + m) as f64 * 2f64.powi(e as i32 - 25),
            };
            if b >> 15 != 0 { -mag } else { mag }
        } else {
            f32::from_bits(b) as f64
        };
        Ok(x >= 0.5)
    }

    pub fn floor(a: u32) -> Result<u32, Error> {
        output(input(a)?.floor())
    }
}

/// Half floats, as fmad16 computes them: hardware (usse-fmad16-lanes,
/// usse-fmad16-rounding, usse-fmad16-specials, x-fmad16) rounds the product to binary32
/// and a * b + c to a half, both to nearest even (one rounding for two
/// halves, whose products fit a binary32), keeps half denormals and gives
/// zeros IEEE signs; a .swzf32 source is its binary32 value. Infinities and
/// NaNs are not modelled.
mod half {
    use super::{Error, why};

    /// An exact value m * 2^e, and the sign of a zero; or a half infinity
    /// or NaN (special).
    #[derive(Clone, Copy)]
    pub struct Exact {
        m: i128,
        e: i32,
        neg: bool,
        special: Option<f32>,
    }

    impl Exact {
        fn value(&self) -> f64 {
            self.special.map_or(self.m as f64 * 2f64.powi(self.e), |s| s as f64)
        }
    }

    pub fn from_half(h: u16) -> Result<Exact, Error> {
        let (e, f) = ((h >> 10 & 31) as i32, (h & 1023) as i128);
        let neg = h >> 15 != 0;
        let m = match e {
            31 => {
                let s = if f != 0 {
                    f32::NAN
                } else if neg {
                    f32::NEG_INFINITY
                } else {
                    f32::INFINITY
                };
                return Ok(Exact { m: 0, e: 0, neg, special: Some(s) });
            }
            0 => f,
            _ => 1024 + f,
        };
        Ok(Exact { m: if neg { -m } else { m }, e: if e == 0 { -24 } else { e - 25 }, neg, special: None })
    }

    /// A .swzf32 source; its denormals, infinities and NaNs are undecided.
    pub fn from_f32(b: u32) -> Result<Exact, Error> {
        let (e, f) = ((b >> 23 & 0xff) as i32, (b & 0x7f_ffff) as i128);
        if e == 0xff || (e == 0 && f != 0) {
            return Err(why("fmad16 .swzf32 of a denormal, infinity or NaN"));
        }
        let neg = b >> 31 != 0;
        let m = if e == 0 { 0 } else { (1 << 23) + f };
        Ok(Exact { m: if neg { -m } else { m }, e: e - 150, neg, special: None })
    }

    /// m * 2^e rounded to 24 significant bits, to nearest even (a binary32
    /// product; one outside the normal range stops).
    fn to_f32(m: i128, e: i32) -> Result<(i128, i32), Error> {
        let a = m.unsigned_abs();
        let bits = 128 - a.leading_zeros() as i32;
        if a == 0 || bits <= 24 {
            return Ok((m, e));
        }
        let shift = (bits - 24) as u32;
        let (n, r) = (a >> shift, a & ((1u128 << shift) - 1));
        let half = 1u128 << (shift - 1);
        let n = n + (r > half || (r == half && n & 1 != 0)) as u128;
        let e = e + shift as i32;
        if !(-149..=104).contains(&(e + 23)) {
            return Err(why("fmad16 product outside the binary32 range (not modelled)"));
        }
        Ok((if m < 0 { -(n as i128) } else { n as i128 }, e))
    }

    pub fn fma(a: Exact, b: Exact, c: Exact) -> Result<u16, Error> {
        // hardware (usse-fmad16-specials): with an infinity or NaN operand, an
        // infinity stays and an invalid result is the half NaN 0x7fff
        if a.special.is_some() || b.special.is_some() || c.special.is_some() {
            let r = a.value() * b.value() + c.value();
            return Ok(if r.is_nan() { 0x7fff } else { if r < 0.0 { 0xfc00 } else { 0x7c00 } });
        }
        // hardware (x-fmad16, usse-fmad16-lanes): the product rounded to binary32,
        // then the sum to a half (fused for two halves, whose products fit)
        let (pm, pe) = to_f32(a.m * b.m, a.e + b.e)?;
        let p = Exact { m: pm, e: pe, neg: a.neg != b.neg, special: None };
        // align to the smaller exponent (the spans fit an i128 for every
        // finite half and binary32)
        let e = p.e.min(c.e);
        let (dp, dc) = ((p.e - e) as u32, (c.e - e) as u32);
        if dp > 60 || dc > 60 {
            return Err(why("fmad16 terms too far apart (not modelled)"));
        }
        let s = (p.m << dp) + (c.m << dc);
        if s == 0 {
            // an exact zero: -0 only when both addends are negative zeros
            return Ok(if p.m == 0 && p.neg && c.m == 0 && c.neg { 0x8000 } else { 0 });
        }
        let sign = if s < 0 { 0x8000 } else { 0 };
        let m = s.unsigned_abs();
        let lg = 127 - m.leading_zeros() as i32 + e; // floor(log2(value))
        // the quantum: 2^-24 for denormals, else 2^(lg - 10)
        let q = if lg < -14 { -24 } else { lg - 10 };
        let n = if q >= e {
            let shift = (q - e) as u32;
            if shift >= 127 {
                0
            } else {
                let (n, r) = (m >> shift, m & ((1u128 << shift) - 1));
                let half = if shift == 0 { 0 } else { 1u128 << (shift - 1) };
                n + (shift > 0 && (r > half || (r == half && n & 1 != 0))) as u128
            }
        } else {
            m << (e - q) as u32
        };
        if lg < -14 {
            // a denormal; 1024 is the smallest normal, encoded alike
            return Ok(sign | n as u16);
        }
        let (mut n, mut lg) = (n, lg);
        if n == 2048 {
            n = 1024;
            lg += 1;
        }
        if lg > 15 {
            return Ok(sign | 0x7c00);
        }
        Ok(sign | ((lg + 15) as u16) << 10 | (n - 1024) as u16)
    }
}

/// The USSE model after the hardware findings of phases 11.15 to 11.27 (the records are cited in
/// each test; the cases are the ones the hardware ran).
#[cfg(test)]
mod after_11_27 {
    use super::*;

    fn run(src: &[&str]) -> (Machine, Result<(), Error>) {
        let words: Vec<u64> =
            src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}"))).collect();
        let mut m = Machine::default();
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000);
        (m, r)
    }

    fn run_after(init: &[&str], src: &[&str]) -> (Machine, Result<(), Error>) {
        run(&[init, src, &["nop.end"]].concat())
    }

    fn refused(r: &Result<(), Error>) -> bool {
        matches!(r, Err(Error::Unsupported { .. }))
    }

    fn set(r1: u32, r2: u32, r3: u32) -> [String; 3] {
        [format!("mov r1, #0x{r1:08x}"), format!("mov r2, #0x{r2:08x}"), format!("mov r3, #0x{r3:08x}")]
    }

    fn with(init: &[String], src: &[&str]) -> (Machine, Result<(), Error>) {
        let init: Vec<&str> = init.iter().map(|s| s.as_str()).collect();
        run_after(&init, src)
    }

    #[test]
    fn the_carry_in_adds_bit_0_of_in() {
        // E494 (usse-ima32-forms-cie-in): 3 * 7 + 100 = 121; iK of 0x10000 or 0x80000000 adds nothing,
        // 0x10001, 0x80000001 and 0xaaaaaaab add 1, for i0, i1 and i2
        for (k, text) in ["cie, i0", "cie, i1", "cie, i2"].iter().enumerate() {
            for (v, want) in [(0x10000u32, 121u32), (0x8000_0000, 121), (0x10001, 122), (0xaaaa_aaab, 122)] {
                let mut init = set(3, 7, 100).to_vec();
                init.extend((0..3).map(|n| format!("mov i{n}, #0x{:08x}", if n == k { v } else { 1 })));
                let (m, r) = with(&init, &[&format!("ima32.u r10, r1, r2, r3, {text}")]);
                assert_eq!((r, m.r[10]), (Ok(()), want), "{text} {v:#x}");
            }
        }
        // the same for imae (E494 imae-cie-in), i0 and i1
        for (k, text) in ["cie, i0", "cie, i1"].iter().enumerate() {
            for (v, want) in [(0x10000u32, 121u32), (0x8000_0000, 121), (0x10001, 122), (1, 122)] {
                let mut init = set(3, 7, 100).to_vec();
                init.extend((0..2).map(|n| format!("mov i{n}, #0x{:08x}", if n == k { v } else { 1 })));
                let (m, r) = with(&init, &[&format!("imae.u r10, r1.low, r2.low, r3, u32, {text}")]);
                assert_eq!((r, m.r[10]), (Ok(()), want), "imae {text} {v:#x}");
            }
        }
    }

    fn edm(src: &[&str], sa: &[(usize, u32)]) -> (Machine, Result<(), Error>) {
        let words: Vec<u64> = src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap()).collect();
        let mut m = Machine { edm_task: true, ..Machine::default() };
        for &(n, v) in sa {
            (m.sa[n], m.written.sa) = (v, m.written.sa | 1 << n);
        }
        let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
        let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000);
        (m, r)
    }

    #[test]
    fn an_edm_tasks_pa_reads_are_sa_64_up() {
        // S2 e2r (3 of 3 jobs): pa_n reads sa_(64+n) for n = 0..4, in an EDM task
        let sa: Vec<(usize, u32)> = (0..5).map(|n| (64 + n, 0x100 + n as u32)).collect();
        for n in 0..5 {
            let (m, r) = edm(&[&format!("mov r10, pa{n}"), "nop.end"], &sa);
            assert_eq!((r, m.r[10]), (Ok(()), 0x100 + n as u32), "pa{n}");
        }
        // a write to sa67 shows through pa3 in the same pass (S2 e2w, 3 of 3 jobs)
        let (m, r) = edm(&["mov sa67, #0x55", "mov r10, pa3", "nop.end"], &[]);
        assert_eq!((r, m.r[10]), (Ok(()), 0x55));
        // pa5 and up are not measured there: refused under Q098; a pa the sa64 view never got
        // is unwritten and stops like any unwritten register
        let (_, r) = edm(&["mov r10, pa5", "nop.end"], &sa);
        assert!(
            matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("Q098") && why.contains("pa5"))
        );
        let (_, r) = edm(&["mov r10, pa0", "nop.end"], &[]);
        assert!(refused(&r), "{r:?}");
    }

    #[test]
    fn an_edm_tasks_mov_to_pa2_and_pa3_writes_sa66_and_sa67_and_to_pa4_is_lost() {
        // E820 (3 of 3 each): mov pa3 is sa67 (read back through both, in the pass and the next),
        // mov pa2 is sa66 in the pass (the next event rewrites it [infer]), mov pa4 is lost
        let sa: Vec<(usize, u32)> = (0..5).map(|n| (64 + n, 0x100 + n as u32)).collect();
        for (n, m) in [(2, 0x5a42_0006u32), (3, 0x5a43_0004)] {
            let src = [&format!("mov r1, #0x{m:08X}") as &str, &format!("mov pa{n}, r1"), "nop.end"];
            let (mm, r) = edm(&src, &sa);
            assert_eq!(r, Ok(()), "pa{n}");
            assert_eq!(mm.sa[64 + n], m, "sa{}", 64 + n);
            let src = [
                &format!("mov r1, #0x{m:08X}") as &str,
                &format!("mov pa{n}, r1"),
                &format!("mov r2, pa{n}"),
                "nop.end",
            ];
            let (mm, r) = edm(&src, &sa);
            assert_eq!((r, mm.r[2]), (Ok(()), m), "pa{n} read back");
            // the neighbours are unchanged
            for k in (2..5).filter(|&k| k != n) {
                assert_eq!(mm.sa[64 + k], 0x100 + k as u32, "sa{} after pa{n}", 64 + k);
            }
        }
        let (m, r) =
            edm(&["mov r1, #0x5A440005", "mov pa4, r1", "mov r2, pa4", "mov r3, sa68", "nop.end"], &sa);
        assert_eq!((r, m.r[2], m.r[3], m.sa[68]), (Ok(()), 0x104, 0x104, 0x104));
        // pa0, pa1 and pa5 up were refused by the verifier and did not run; other forms than mov
        // did not run either
        for n in [0, 1, 5, 7] {
            let (_, r) = edm(&["mov r1, #5", &format!("mov pa{n}, r1"), "nop.end"], &sa);
            assert!(
                matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("E820")),
                "pa{n}: {r:?}"
            );
        }
        let (_, r) = edm(&["mov r1, #5", "ima32.u pa3, r1, r1, r1", "nop.end"], &sa);
        assert!(matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("E820")), "{r:?}");
    }

    #[test]
    fn pclink_keeps_18_bits() {
        // E475 (usse-link-pclink-roundtrip): 0x40000 reads back 0, 0x7fffffff 0x3ffff, 0x80000000 0,
        // 0xa5a5a5a5 0x1a5a5, 0x5a5a5a5a 0x25a5a
        for (v, want) in [
            (0x40000u32, 0u32),
            (0x3ffff, 0x3ffff),
            (0x7fff_ffff, 0x3ffff),
            (0x8000_0000, 0),
            (0xa5a5_a5a5, 0x1a5a5),
            (0x5a5a_5a5a, 0x25a5a),
        ] {
            let (m, r) = run_after(&[&format!("mov r5, #0x{v:08x}"), "mov pclink, r5"], &["mov r6, pclink"]);
            assert_eq!((r, m.r[6]), (Ok(()), want), "{v:#x}");
        }
    }

    #[test]
    fn the_extra_operand_of_ima32_gets_the_high_word() {
        // E493 (usse-ima32-forms-extra-i): r10 the low 32 bits, iK the high ones, the other i
        // registers as they were (presets 0x55, 0x66, 0x77)
        let triples = [
            ((3u32, 7u32, 100u32), (0x79u32, 0u32)),
            ((0xffff_ffff, 1, 1), (0, 1)),
            ((0xffff_ffff, 0xffff_ffff, 0xffff_ffff), (0, 0xffff_ffff)),
            ((0x10000, 0x10000, 0), (0, 1)),
            ((0x8000_0000, 2, 0xffff_ffff), (0xffff_ffff, 1)),
        ];
        for k in 0..3 {
            for &((a, b, c), (lo, hi)) in &triples {
                let mut init = set(a, b, c).to_vec();
                init.extend(["mov i0, #0x55", "mov i1, #0x66", "mov i2, #0x77"].map(String::from));
                let (m, r) = with(&init, &[&format!("ima32.u r10, i{k}, r1, r2, r3")]);
                assert_eq!(r, Ok(()), "{a:#x} {b:#x} {c:#x}");
                assert_eq!(m.r[10], if (a, b, c) == (3, 7, 100) { 0x79 } else { lo }, "{a:#x} {b:#x} {c:#x}");
                let mut want = [0x55, 0x66, 0x77];
                want[k] = hi;
                assert_eq!(m.i, [want[0], want[1], want[2], 0], "K = {k} {a:#x} {b:#x} {c:#x}");
            }
        }
        // E501 (ima32hi): ima32.u r10, iK, r2, c56, r1 leaves a - b in r10 and b - [a < b] in iK
        for (a, b) in [(1u32, 0u32), (0, 1), (5, 5), (0x7fff_ffff, 0x8000_0000), (0xffff_ffff, 0x8000_0001)] {
            let (m, r) = with(&set(a, b, 0), &["mov i0, #0x55", "ima32.u r10, i0, r2, c56, r1"]);
            assert_eq!(
                (r, m.r[10], m.i[0]),
                (Ok(()), a.wrapping_sub(b), b - (a < b) as u32),
                "{a:#x} {b:#x}"
            );
        }
    }

    #[test]
    fn the_extra_operand_stops_where_it_was_not_run() {
        let init = set(3, 7, 100);
        for t in [
            "ima32.u r10, i0, r1, r2, r3, cie, i1", // with cie not run
            "ima32.u r10, i0, r1, r2.neg, r3",      // with .neg not run
            "ima32.u r10, i0, r1, #5, r3",          // an immediate: not run
            "ima32.u r10, i0, r1, r2, i0",          // an iK that is also a source: not run
        ] {
            assert!(refused(&with(&init, &[t]).1), "{t}");
        }
    }

    #[test]
    fn ima32_negates_sources_2_and_3() {
        // E470 and E495: .neg is a two's-complement negation of the source, .u and .s alike
        let (a, b, c) = (0x1234_5678u32, 0x9abc_def0u32, 0xdead_beefu32);
        for ty in ["u", "s"] {
            let init = set(a, b, c);
            let (m, r) = with(&init, &[&format!("ima32.{ty} r10, r1, r2.neg, r3")]);
            assert_eq!((r, m.r[10]), (Ok(()), a.wrapping_mul(b.wrapping_neg()).wrapping_add(c)));
            let (m, r) = with(&init, &[&format!("ima32.{ty} r10, r1, r2, r3.neg")]);
            assert_eq!((r, m.r[10]), (Ok(()), a.wrapping_mul(b).wrapping_sub(c)));
            let (m, r) = with(&init, &[&format!("ima32.{ty} r10, r1, r2.neg, r3.neg")]);
            assert_eq!((r, m.r[10]), (Ok(()), a.wrapping_mul(b.wrapping_neg()).wrapping_sub(c)));
        }
        // the subtract lowering of E470: ima32.u d, b, c56, a is a - b
        let (m, r) = with(&set(5, 7, 0), &["ima32.u r10, r2, c56, r1"]);
        assert_eq!((r, m.r[10]), (Ok(()), 0xffff_fffe));
        // an immediate or a constant negated, .s (E495): #1.neg and #127.neg, c56.neg
        let (m, r) = with(&set(a, b, c), &["ima32.s r10, r1, #1.neg, r3"]);
        assert_eq!((r, m.r[10]), (Ok(()), c.wrapping_sub(a)));
        let (m, r) = with(&set(a, b, c), &["ima32.s r10, r1, r2, #127.neg"]);
        assert_eq!((r, m.r[10]), (Ok(()), a.wrapping_mul(b).wrapping_sub(127)));
        let (m, r) = with(&set(a, b, c), &["ima32.s r10, r1, c56.neg, r3"]);
        assert_eq!((r, m.r[10]), (Ok(()), a.wrapping_add(c)));
        // and with the carry in, which was not run: stops
        let mut init = set(a, b, c).to_vec();
        init.push("mov i0, #1".into());
        assert!(refused(&with(&init, &["ima32.u r10, r1, r2.neg, r3, cie, i0"]).1));
    }

    #[test]
    fn a_call_not_taken_still_writes_the_link() {
        // E491 (usse-callfalse2-link): pclink holds the index after the call whatever the predicate
        for pred in ["p0", "p1", "p2", "p3", "!p0", "!p1"] {
            let set_p = |t: &str| format!("and.testtanz.chan0 !c0, {t}, r1, r1");
            let (init, p) = match pred {
                "!p0" | "!p1" => (vec!["mov r1, #1".to_string(), set_p("p0"), set_p("p1")], pred),
                _ => {
                    (vec!["mov r1, #0".to_string(), set_p("p0"), set_p("p1"), set_p("p2"), set_p("p3")], pred)
                }
            };
            for call in ["ba.savelink #0x00000020", "br.savelink #4"] {
                let mut src: Vec<&str> = init.iter().map(|s| s.as_str()).collect();
                src.push("mov pclink, r1");
                let text = format!("{p} {call}");
                src.push(&text);
                src.push("mov r11, #2");
                src.push("mov r15, pclink");
                src.push("nop.end");
                let n = src.len();
                let (m, r) = run(&src);
                assert_eq!(r, Ok(()), "{text}");
                // the call is at index n - 4 and its link the next instruction
                assert_eq!((m.r[15], m.r[11]), ((n - 3) as u32, 2), "{text}");
            }
        }
        // a call that is taken writes the same link (E491, 2 of 2)
        let (m, r) = run(&["ba.savelink #0x00000002", "mov r11, #2", "mov r15, pclink", "nop.end"]);
        assert_eq!((r, m.r[15]), (Ok(()), 1));
    }

    #[test]
    fn the_sum_tests_read_the_sum_as_the_hardware_does() {
        // E498 (usse-iaddu32-pairs, usse-compare32x): the 16 pairs (r1, r2)
        let pairs: [(u32, u32); 16] = [
            (0x8000, 0x8000),
            (0xffff, 1),
            (0x8000, 0xffff_8000),
            (0x8001, 0xffff_7fff),
            (0xffff, 0xffff_ffff),
            (0x9000, 0xffff_7000),
            (1, 0xffff_ffff),
            (0x7fff, 0xffff_8001),
            (0, 0),
            (0, 0xffff_ffff),
            (0x8000, 0),
            (0xffff, 0),
            (0x8000, 0x7fff_0000),
            (0xffff, 0x8000_0000),
            (5, 0xffff_fffb),
            (0x8000, 0x7fff_8000),
        ];
        let nat = [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0];
        let taz = [1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0];
        let flag = |op: &str, (a, b): (u32, u32)| {
            let (m, r) = with(
                &set(a, b, 0),
                &[&format!("{op}.chan0 !c0, p0, r1, r2"), "mov r10, #0", "p0 mov r10, #1"],
            );
            assert_eq!(r, Ok(()), "{op} {a:#x} {b:#x}");
            m.r[10]
        };
        for (n, &pr) in pairs.iter().enumerate() {
            // iadd32: n and p read the sign of the true sum sext16(r1) + r2 (r2 signed); z and nz
            // the zero of the sum with r1 sign-extended
            assert_eq!(flag("iadd32.testnat", pr), nat[n], "nat {pr:x?}");
            assert_eq!(flag("iadd32.testpat", pr), 1 - nat[n], "pat {pr:x?}");
            assert_eq!(flag("iadd32.testtaz", pr), taz[n], "taz {pr:x?}");
            assert_eq!(flag("iadd32.testtanz", pr), 1 - taz[n], "tanz {pr:x?}");
            // iaddu32: p always true, n never, the zero test counts the carry: true for (0, 0) only
            assert_eq!(flag("iaddu32.testpat", pr), 1, "upat {pr:x?}");
            assert_eq!(flag("iaddu32.testnat", pr), 0, "unat {pr:x?}");
            assert_eq!(flag("iaddu32.testtaz", pr), (pr == (0, 0)) as u32, "utaz {pr:x?}");
            assert_eq!(flag("iaddu32.testtanz", pr), (pr != (0, 0)) as u32, "utanz {pr:x?}");
        }
        // the value iaddu32 writes zero-extends r1 (usse-decoder-vectors-iaddu32-taz __5, usse-integer-iaddu32-value __0)
        for (a, b, want) in
            [(0x8000u32, 0x8000u32, 0x10000u32), (0xffff, 1, 0x10000), (0xffff_ffff, 2, 0x10001)]
        {
            let (m, r) = with(&set(a, b, 0), &["iaddu32.testtaz.chan0 r10, p0, r1, r2"]);
            assert_eq!((r, m.r[10]), (Ok(()), want));
        }
    }

    #[test]
    fn a_test_field_reads_as_its_two_parts() {
        // E499 (usse-rawcond, usse-rawcond2): the zero part is tanz if bit 41, else taz if bit 40,
        // the sign part pat if bit 43, else nat if bit 42; p0 is the AND of the parts present. The
        // words are `and.testtaz.chan0 !c0, p0, r1, r2` (0x48081181000C0082) with the field set
        let base = 0x4808_1181_000C_0082u64 & !(0xf << 40);
        let inputs: [(u32, u32); 6] = [
            (0, 0),
            (1, 1),
            (5, 3),
            (0x7fff_ffff, 0xffff_ffff),
            (0x8000_0000, 0x8000_0000),
            (0xffff_ffff, 0xffff_ffff),
        ];
        for field in 1..16u64 {
            for &(a, b) in &inputs {
                let word = base | field << 40;
                let src =
                    [format!("mov r1, #0x{a:08x}"), format!("mov r2, #0x{b:08x}"), "mov r10, #0".to_string()];
                let mut words: Vec<u64> =
                    src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap()).collect();
                words.extend([
                    word,
                    usse_isa::encode("p0 mov r10, #1", Core::Sgx545).unwrap(),
                    usse_isa::encode("nop.end", Core::Sgx545).unwrap(),
                ]);
                let (mut m, mut mem) = (Machine::default(), Memory { base: 0x1000, words: vec![0; 4] });
                let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100);
                let v = (a & b) as i32;
                let zero = if field & 2 != 0 {
                    Some(v != 0)
                } else if field & 1 != 0 {
                    Some(v == 0)
                } else {
                    None
                };
                let sign = if field & 8 != 0 {
                    Some(v >= 0)
                } else if field & 4 != 0 {
                    Some(v < 0)
                } else {
                    None
                };
                let want = zero.unwrap_or(true) && sign.unwrap_or(true);
                assert_eq!((r, m.r[10]), (Ok(()), want as u32), "field {field:#x} on {a:#x} & {b:#x}");
            }
        }
    }

    #[test]
    fn a_pa_destination_is_not_written() {
        // E496 (usse-pa-dest, usse-ima32-forms-dest): ima32.u pa0 and mov pa0 leave pa0 as it
        // was, so a read of it after the write is the job's, not the instruction's result
        let (_, r) = with(&set(3, 7, 100), &["ima32.u pa0, r1, r2, r3", "mov r10, pa0"]);
        assert!(refused(&r), "{r:?}");
        let (_, r) = with(&set(3, 7, 100), &["mov pa0, r1", "mov r10, pa0"]);
        assert!(refused(&r), "{r:?}");
        // E380 (30 fill jobs): a mov to pa1 to pa7 is lost the same way, the pa left as the job
        // had it (here untouched, 0 in a fresh machine)
        for n in 1..8 {
            let (m, r) = with(&set(3, 7, 100), &[&format!("mov pa{n}, r1")]);
            assert_eq!((r, m.pa[n]), (Ok(()), 0), "mov pa{n}");
        }
        // ima32 to pa1 and up is not measured (E496 did pa0 only): it stops, under Q098
        let (_, r) = with(&set(3, 7, 100), &["ima32.u pa1, r1, r2, r3"]);
        assert!(
            matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("Q098") && why.contains("pa1"))
        );
        // an EDM task's pa is not the fill's (Q098, E537, E820): a mov to pa0, pa1 or pa5 up stops
        // there (mov to pa2 to pa4: an_edm_tasks_mov_to_pa2_and_pa3_writes_sa66_and_sa67...)
        for n in [0, 1, 7] {
            let words: Vec<u64> = ["mov r1, #5".to_string(), format!("mov pa{n}, r1"), "nop.end".to_string()]
                .iter()
                .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
                .collect();
            let mut m = Machine { edm_task: true, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 64] };
            let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000);
            assert!(
                matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("EDM") && why.contains("Q098")),
                "{r:?}"
            );
        }
        // the other destinations of E496 are written: r0, sa0, o0, i1 and i2
        for d in ["r9", "r30", "sa0", "i1", "i2"] {
            let (m, r) =
                with(&set(3, 7, 100), &[&format!("ima32.u {d}, r1, r2, r3"), &format!("mov r10, {d}")]);
            assert_eq!((r, m.r[10]), (Ok(()), 0x79), "{d}");
        }
    }

    /// A machine with `n` pointer registers from `first` holding the dword addresses of a memory
    /// that starts at 0x1000 and whose dword i holds 0xd000_0000 | i, and r2 up holding 0x100 + k.
    fn memory_run(first: usize, pointers: &[u32], src: &[&str]) -> (Machine, Memory, Result<(), Error>) {
        let mut init: Vec<String> = pointers
            .iter()
            .enumerate()
            .map(|(k, p)| format!("mov r{}, #0x{:08x}", first + k, 0x1000 + 4 * p))
            .collect();
        init.extend((0..16).map(|k| format!("mov r{}, #0x{:08x}", 2 + k, 0x100 + k)));
        let mut words: Vec<u64> = init.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap()).collect();
        words.extend(src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}"))));
        words.push(usse_isa::encode("nop.end", Core::Sgx545).unwrap());
        let mut m = Machine { temps: 124, ..Machine::default() };
        let mut mem = Memory { base: 0x1000, words: (0..64).map(|i| 0xd000_0000 | i).collect() };
        let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000);
        (m, mem, r)
    }

    /// Two dwords of the narrow-memory probes (probes/usse/fw37-narrow.toml: bytes a7 b6 8d 9c 4b 5c 6d 7e) at
    /// 0x1000, r40 pointing at them, r5 = 0xaabbccdd.
    fn narrow_run(base: u32, src: &[&str]) -> (Machine, Memory, Result<(), Error>) {
        let mut words: Vec<u64> = ["mov r5, #0xaabbccdd".to_string(), format!("mov r40, #0x{base:08x}")]
            .iter()
            .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
            .collect();
        words.extend(src.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}"))));
        words.push(usse_isa::encode("nop.end", Core::Sgx545).unwrap());
        let mut m = Machine { temps: 124, ..Machine::default() };
        let mut mem =
            Memory { base: 0x1000, words: vec![0x9c8d_b6a7, 0x7e6d_5c4b, 0xd000_0012, 0xd000_0013] };
        let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 1000);
        (m, mem, r)
    }

    #[test]
    fn narrow_loads_count_elements_and_zero_extend() {
        // E598 (usse-fw37-narrow-ldab-offsets, -ldaw-offsets, -ld-unaligned, 22 jobs on the hardware): the offset
        // counts bytes for ldab and halfwords for ldaw, the value is zero-extended (every byte of the first dword
        // has bit 7 set except 4b..7e), and a halfword load at an odd address reads the bytes there
        let bytes = [0xa7u32, 0xb6, 0x8d, 0x9c, 0x4b, 0x5c, 0x6d, 0x7e];
        for (n, want) in bytes.iter().enumerate() {
            let (m, _, r) = narrow_run(0x1000, &[&format!("ldab r10, [r40,+#{n}], drc0"), "wdf drc0"]);
            assert_eq!(r, Ok(()), "ldab #{n}");
            assert_eq!(m.r[10], *want, "ldab #{n}");
        }
        for (n, want) in [0xb6a7u32, 0x9c8d, 0x5c4b, 0x7e6d].iter().enumerate() {
            let (m, _, r) = narrow_run(0x1000, &[&format!("ldaw r10, [r40,+#{n}], drc0"), "wdf drc0"]);
            assert_eq!(r, Ok(()), "ldaw #{n}");
            assert_eq!(m.r[10], *want, "ldaw #{n}");
        }
        for (off, want) in [(1u32, 0x8db6u32), (2, 0x9c8d), (3, 0x4b9c)] {
            let (m, _, r) = narrow_run(0x1000 + off, &["ldaw r10, [r40,+#0], drc0", "wdf drc0"]);
            assert_eq!(r, Ok(()), "ldaw at +{off}");
            assert_eq!(m.r[10], want, "ldaw at +{off}");
        }
    }

    #[test]
    fn narrow_stores_change_only_their_own_bytes() {
        // E599 (usse-fw37-narrow-stab, -staw, -stad-unaligned-control, 26 jobs): stab puts the low byte of the
        // source at base + n, staw the low halfword at base + 2n (aligned), nothing else changes
        let (_, mem, r) = narrow_run(0x1000, &["stab [r40,+#5], r5"]);
        assert_eq!((r, mem.words[0], mem.words[1]), (Ok(()), 0x9c8d_b6a7, 0x7e6d_dd4b));
        let (_, mem, r) = narrow_run(0x1000 + 1, &["stab [r40,+#2], r5"]);
        assert_eq!((r, mem.words[0], mem.words[1]), (Ok(()), 0xdd8d_b6a7, 0x7e6d_5c4b));
        let (_, mem, r) = narrow_run(0x1000, &["staw [r40,+#3], r5"]);
        assert_eq!((r, mem.words[0], mem.words[1]), (Ok(()), 0x9c8d_b6a7, 0xccdd_5c4b));
        let (_, mem, r) = narrow_run(0x1000 + 2, &["staw [r40,+#1], r5"]);
        assert_eq!((r, mem.words[0], mem.words[1]), (Ok(()), 0x9c8d_b6a7, 0x7e6d_ccdd));
    }

    #[test]
    fn narrow_forms_that_did_not_run_are_refused() {
        // not run in E598/E599: a negative offset, a register offset, the increment forms, a repeat, an
        // unaligned staw
        for text in [
            "ldab r10, [r40,-#1], drc0",
            "ldaw r10, [r40,-#1], drc0",
            "ldab r10, [r40,#1++], drc0",
            "ldab r10, [r40,++#1], drc0",
            "ldab.repeat2 r10, [r40,+#0], drc0",
            "stab [r40,-#1], r5",
            "staw [r40,#1++], r5",
            "stab.repeat2 [r40,+#0], r5",
        ] {
            let (_, _, r) = narrow_run(0x1000, &[text]);
            match r {
                Err(Error::Unsupported { why, .. }) => assert!(why.contains("not measured"), "{text}: {why}"),
                other => panic!("{text}: {other:?}"),
            }
        }
        let (_, _, r) = narrow_run(0x1000 + 1, &["staw [r40,+#0], r5"]);
        assert!(matches!(r, Err(Error::Unsupported { .. })), "an unaligned staw: {r:?}");
    }

    #[test]
    fn narrow_forms_with_flags_banks_or_a_second_drc_are_refused() {
        // E598/E599 ran the plain forms only: no flag, drc0, the r bank for the base, the destination and the
        // store's source. Everything else is refused, however the verifier of the loader would see it.
        for text in [
            "ldab.bypassl1 r10, [r40,+#0], drc0",
            "ldab.bpcache r10, [r40,+#0], drc0",
            "ldaw.fcfill r10, [r40,+#0], drc0",
            "ldab.syncs r10, [r40,+#0], drc0",
            "ldaw.skipinv r10, [r40,+#0], drc0",
            "stab.bypassl1 [r40,+#0], r5",
            "staw.syncs [r40,+#0], r5",
            "ldab r10, [r40,+#0], drc1",
            "ldaw r10, [r40,+#0], drc1",
            "ldab pa3, [r40,+#0], drc0",
            "ldaw pa3, [r40,+#0], drc0",
            "ldab r10, [pa0,+#0], drc0",
            "stab [pa0,+#0], r5",
            "stab [r40,+#0], pa1",
            "staw [r40,+#0], pa1",
        ] {
            let (_, _, r) = narrow_run(0x1000, &[text]);
            match r {
                Err(Error::Unsupported { why, .. }) => assert!(why.contains("not measured"), "{text}: {why}"),
                other => panic!("{text}: {other:?}"),
            }
        }
    }

    #[test]
    fn a_store_repeat_steps_the_pointer_and_the_data_register() {
        // E483, E515 (usse-store-repeat, usse-repeat-ptrs): iteration i stores r(2 + i) at the
        // address in r(40 + i); the post-increment form moves each of those pointers by k
        let ptrs: Vec<u32> = (0..16).map(|k| 8 + 2 * k).collect();
        for n in [2u32, 5, 9, 16] {
            let (m, mem, r) = memory_run(40, &ptrs, &[&format!("stad.repeat{n} [r40,+#0], r2")]);
            assert_eq!(r, Ok(()), "plain {n}");
            for k in 0..16usize {
                let want = if (k as u32) < n { 0x100 + k as u32 } else { 0xd000_0000 | (8 + 2 * k as u32) };
                assert_eq!(mem.words[8 + 2 * k], want, "plain {n} iteration {k}");
                assert_eq!(m.r[40 + k], 0x1000 + 4 * (8 + 2 * k as u32), "plain {n}: the pointers stay");
            }
            let (m, mem, r) = memory_run(40, &ptrs, &[&format!("stad.repeat{n} [r40,#2++], r2")]);
            assert_eq!(r, Ok(()), "post {n}");
            for k in 0..16usize {
                let moved = if (k as u32) < n { 2 } else { 0 };
                assert_eq!(m.r[40 + k], 0x1000 + 4 * (8 + 2 * k as u32 + moved), "post {n} pointer {k}");
                assert_eq!(mem.words[8 + 2 * k] == 0x100 + k as u32, (k as u32) < n, "post {n} store {k}");
            }
        }
        // the pre-increment form stores at the moved address and moves the pointer (E515, N = 8)
        let (m, mem, r) = memory_run(40, &ptrs, &["stad.repeat8 [r40,++#1], r2"]);
        assert_eq!(r, Ok(()));
        assert_eq!((mem.words[9], mem.words[8 + 2 * 7 + 1], m.r[47]), (0x100, 0x107, 0x1000 + 4 * 23));
        // a pointer that holds no address: no fault is predicted (the hardware's was not predictable)
        let (_, _, r) = memory_run(40, &ptrs[..2], &["stad.repeat4 [r40,+#0], r2"]);
        assert!(refused(&r), "{r:?}");
    }

    #[test]
    fn a_load_repeat_and_a_smlsi_series() {
        // E483, E515: ldad.repeatN loads from r(56 + i) into r(10 + i), the post-increment form
        // moving each pointer; the load lands at its wdf
        let ptrs: Vec<u32> = (0..16).map(|k| 3 * k).collect();
        let (m, _, r) = memory_run(56, &ptrs, &["ldad.repeat6 r10, [r56,#1++], drc0", "wdf drc0"]);
        assert_eq!(r, Ok(()));
        for k in 0..6 {
            assert_eq!(
                (m.r[10 + k], m.r[56 + k]),
                (0xd000_0000 | (3 * k as u32), 0x1000 + 4 * (3 * k as u32 + 1)),
                "{k}"
            );
        }
        // E483 (usse-store-repeat-regs smlsi): the second increment 0 and the fourth 1 make one
        // pointer series: r2 to r17 go to 16 consecutive dwords and r40 moves by 16
        let (m, mem, r) = memory_run(
            40,
            &[4],
            &[
                "smlsi #0, #0, #0, #1, incrementmode, incrementmode, incrementmode, incrementmode, #0, #0, #0",
                "stad.repeat16 [r40,#1++], r2",
            ],
        );
        assert_eq!(r, Ok(()));
        assert_eq!(
            (0..16).map(|k| mem.words[4 + k]).collect::<Vec<_>>(),
            (0..16).map(|k| 0x100 + k).collect::<Vec<u32>>()
        );
        assert_eq!(m.r[40], 0x1000 + 4 * 20);
        // not run: an ldad repeat after smlsi
        let (_, _, r) = memory_run(
            56,
            &ptrs,
            &[
                "smlsi #1, #1, #1, #1, incrementmode, incrementmode, incrementmode, incrementmode, #0, #0, #0",
                "ldad.repeat4 r10, [r56,+#0], drc0",
            ],
        );
        assert!(refused(&r), "{r:?}");
        // not run: a pre-increment load with a repeat, a repeat with a fetch
        let (_, _, r) = memory_run(56, &ptrs, &["ldad.repeat4 r10, [r56,++#1], drc0"]);
        assert!(refused(&r), "{r:?}");
    }

    #[test]
    fn a_store_fetch_writes_consecutive_dwords_from_the_shifted_start() {
        // E482, E516 (usse-repeat-ptrs fetch-*): rb at dword b = 8; the plain and pre forms start
        // at b + k + 1, the post-increment form at b + k and moves rb by N whatever k
        let at = |text: &str| {
            let (m, mem, r) = memory_run(40, &[8], &[text]);
            assert_eq!(r, Ok(()), "{text}");
            let written: Vec<usize> = (0..40).filter(|&i| mem.words[i] != 0xd000_0000 | i as u32).collect();
            (written, m.r[40])
        };
        assert_eq!(at("stad.fetch4 [r40,+#2], r2"), ((11..15).collect(), 0x1000 + 32));
        assert_eq!(at("stad.fetch8 [r40,+#3], r2"), ((12..20).collect(), 0x1000 + 32));
        assert_eq!(at("stad.fetch4 [r40,#2++], r2"), ((10..14).collect(), 0x1000 + 4 * 12));
        assert_eq!(at("stad.fetch2 [r40,#4++], r2"), ((12..14).collect(), 0x1000 + 4 * 10));
        assert_eq!(at("stad.fetch4 [r40,++#1], r2"), ((10..14).collect(), 0x1000 + 4 * 12));
        // the data: r2, r3 ... to consecutive dwords
        let (_, mem, _) = memory_run(40, &[8], &["stad.fetch4 [r40,+#0], r2"]);
        assert_eq!(&mem.words[9..13], &[0x100, 0x101, 0x102, 0x103]);
    }

    #[test]
    fn a_phase_gets_the_allocation_its_phas_asked_for() {
        // E487, E519: the second phase has the request modulo 256, 4 to 192; the others hung
        let phased = |request: u32| {
            run(&[
                &format!("phas #2, #{request}, pixel, none, parallel"),
                "nop.end",
                "mov r7, #0x7e57007b",
                "mov.end o0, r7",
            ])
        };
        let (m, r) = phased(132);
        assert_eq!((r, m.o[0], m.temps), (Ok(()), 0x7e57007b, 132));
        for request in [196, 228, 252, 256, 452, 504] {
            let (_, r) = phased(request);
            assert!(refused(&r), "{request}: {r:?}");
        }
        assert_eq!(phased(260).0.temps, 4);
        // a register past the allocation is not modelled (E486: most pixels read it modulo the
        // allocation and a write is dropped, E519: the marker of r123 read back)
        assert!(refused(&run(&["phas #2, #260, pixel, none, parallel", "nop.end", "mov.end r123, #1"]).1));
        // the temporaries of the first phase are not the second's (E119)
        assert!(refused(
            &run(&["phas #3, #8, pixel, none, parallel", "mov r1, #5", "nop.end", "mov.end o0, r1"]).1
        ));
        // vcull hangs a pixel task (usse-phases-phas-pix-vcull-*, E121) and pt hangs a vertex task
        // (usse-phases-phas-vtx-pt-parallel): refused. In a vertex task vcull waits for the MTE's cull
        // decision, which is not modelled: the program stops where its first phase ends
        for w in ["vcull", "pt"] {
            let t = format!("phas #2, #8, pixel, {w}, parallel");
            assert!(refused(&run(&[&t, "mov.end o0, #5", "mov.end o0, #7"]).1), "{w}");
        }
        let prog = ["phas #2, #8, pixel, vcull, parallel", "mov.end o0, #5", "mov.end o0, #7"];
        let words: Vec<u64> = prog.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap()).collect();
        let mut m = Machine { vertex_task: true, ..Machine::default() };
        let mut mem = Memory { base: 0x1000, words: vec![0; 4] };
        assert_eq!((m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100), m.o[0]), (Ok(()), 5));
        let words: Vec<u64> = ["phas #2, #8, pixel, pt, parallel", "mov.end o0, #5"]
            .iter()
            .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
            .collect();
        let mut m = Machine { vertex_task: true, ..Machine::default() };
        assert!(refused(&m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100)));
        // a rate or mode not run, with a next phase
        assert!(refused(&run(&["phas #2, #8, pixel, none, perinstance", "nop.end", "nop.end"]).1));
    }

    #[test]
    fn imae_carries_the_signed_add_and_both_carries() {
        // E471 (usse-imae-neg-coe-signed): imae.s multiplies the signed halves and adds c as an
        // unsigned number; coe writes that add's carry, 0 or 1
        let carry = |a: u32, b: u32, c: u32| {
            let (m, r) =
                with(&set(a, b, c), &["imae.s r10, r1.low, r2.low, r3, u32, coe, i0", "mov r11, i0"]);
            assert_eq!(r, Ok(()));
            (m.r[10], m.r[11])
        };
        assert_eq!(carry(0xffff, 0xffff, 0xffff_fff0), (0xffff_fff1, 0));
        assert_eq!(carry(0x8000, 0x8000, 0xffff_ffff), (0x3fff_ffff, 1));
        assert_eq!(carry(0x7fff, 0x7fff, 0x8000_0000), (0xbfff_0001, 0));
        assert_eq!(carry(1, 1, 0xffff_ffff), (0, 1));
        assert_eq!(carry(0xffff, 1, 0), (0xffff_ffff, 0));
        // E471 (usse-imae-neg-coe-cie): coe and cie on one iN: the sum includes bit 0 of iN and the
        // carry of the whole goes back to iN
        let mut init = set(2, 3, 0xffff_fffe).to_vec();
        init.push("mov i0, #1".into());
        let (m, r) = with(&init, &["imae.u r10, r1.low, r2.low, r3, u32, coe, cie, i0", "mov r11, i0"]);
        assert_eq!((r, m.r[10], m.r[11]), (Ok(()), 5, 1));
    }

    #[test]
    fn what_the_job_before_left_is_not_read() {
        // E477, E484, E475: p0-p3 and pclink are not reset between jobs, so a read before the
        // program sets them stops it
        assert!(refused(&run_after(&[], &["p0 mov r1, #1"]).1));
        assert!(refused(&run_after(&[], &["mov r1, pclink"]).1));
        assert!(refused(&run_after(&[], &["lapc"]).1));
        // set by a test, or by a call that is not taken, they are known
        assert_eq!(
            run_after(&["mov r5, #0", "and.testtanz.chan0 !c0, p0, r5, r5"], &["p0 mov r1, #1"]).1,
            Ok(())
        );
        assert_eq!(
            run_after(
                &["mov r5, #0", "and.testtanz.chan0 !c0, p0, r5, r5", "p0 br.savelink #1"],
                &["mov r1, pclink"]
            )
            .1,
            Ok(())
        );
    }

    #[test]
    fn the_signed_high_word_and_the_o_join() {
        // E526 (usse-ima32hi-signed): ima32.s iK = bits 63:32 of sext(a) * sext(b) + sext(c)
        for (a, b, c) in [
            (0xffff_ffffu32, 0xffff_ffffu32, 0xffff_ffffu32),
            (0x8000_0000, 2, 0xffff_ffff),
            (3, 7, 100),
            (0x7fff_ffff, 0x7fff_ffff, 0x8000_0000),
        ] {
            let (m, r) = with(&set(a, b, c), &["ima32.s r10, i0, r1, r2, r3"].map(|t| t));
            let want = (a as i32 as i64 * b as i32 as i64 + c as i32 as i64) as u64;
            assert_eq!((r, m.r[10], m.i[0]), (Ok(()), want as u32, (want >> 32) as u32), "{a:x} {b:x} {c:x}");
        }
        // E528: the signed compare, ima32.s r11, i0, r2, c56, r1 then i0 nonzero when a < b
        for (a, b) in [(1u32, 2u32), (0xffff_ffff, 0), (0x8000_0000, 0x7fff_ffff), (5, 5)] {
            let (m, _) = with(&set(a, b, 0), &["ima32.s r11, i0, r2, c56, r1"]);
            assert_eq!(m.i[0] != 0, (a as i32) < b as i32, "{a:x} {b:x}");
        }
        // with cie, a negated source, and i3 the extra operand still stops
        assert!(refused(&with(&set(1, 2, 3), &["ima32.s r10, i3, r1, r2, r3"]).1));
        assert!(refused(&with(&set(1, 2, 3), &["ima32.s r10, i0, r1, r2.neg, r3"]).1));
        // E529: the o join (enc[39] clear) ORs the parts, an absent part true: a field of one part is
        // always true; field 0xd (taz, pat) is taz OR pat
        let base = 0x4808_1181_000C_0082u64 & !(0xf << 40) & !(1 << 39);
        for (field, a, want) in [(3u64, 5u32, 1u32), (0xc, 5, 1), (0xd, 5, 1), (0x5, 5, 0), (0x5, 0, 1)] {
            let mut words: Vec<u64> =
                [format!("mov r1, #0x{a:08x}"), format!("mov r2, #0x{a:08x}"), "mov r10, #0".to_string()]
                    .iter()
                    .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
                    .collect();
            words.extend([
                base | field << 40,
                usse_isa::encode("p0 mov r10, #1", Core::Sgx545).unwrap(),
                usse_isa::encode("nop.end", Core::Sgx545).unwrap(),
            ]);
            let (mut m, mut mem) = (Machine::default(), Memory { base: 0x1000, words: vec![0; 4] });
            let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100);
            assert_eq!((r, m.r[10]), (Ok(()), want), "o join field {field:#x} on {a}");
        }
    }

    #[test]
    fn only_the_negations_that_ran_are_taken() {
        let init = set(5, 7, 100);
        // E495 and E470: refused, not run
        for t in [
            "ima32.s r10, r1, #127.neg, r3",
            "ima32.s r10, r1, r2, #5.neg",
            "ima32.s r10, r1, r2, c3.neg",
            "ima32.u r10, r1, #1.neg, r3",
            "ima32.u r10, r1, c3.neg, r3",
            "ima32.u r10, r1, r2, c3.neg",
        ] {
            assert!(refused(&with(&init, &[t]).1), "{t}");
        }
        // run: taken
        for t in
            ["ima32.s r10, r1, #5.neg, r3", "ima32.u r10, r1, #127.neg, r3", "ima32.u r10, r1, r2, c56.neg"]
        {
            assert_eq!(with(&init, &[t]).1, Ok(()), "{t}");
        }
    }

    #[test]
    fn what_was_not_run_stays_refused() {
        // E516: the registers of a fetch ran up to r33; E529, E1062: the join o
        let (_, _, r) = memory_run(40, &[8], &["stad.fetch4 [r40,+#0], r32"]);
        assert!(matches!(&r, Err(Error::Unsupported { why, .. }) if why.contains("E516")), "{r:?}");
        let (_, _, r) = memory_run(40, &[8], &["stad.fetch4 [r40,+#0], r14"]);
        assert_eq!(r, Ok(()));
        // E1062 ran the join o on the shifts, rol, iadd32, iaddu32, iadd8 and iadd16 as well; isub16 with
        // it (isub16.testtanz.chan0 !c0, p0, r1, r2, enc[39] clear) was not run, and the same on and was
        let isub16 = usse_isa::encode("isub16.testtanz.chan0 !c0, p0, r1, r2", Core::Sgx545).unwrap();
        for (word, ok) in [(isub16 & !(1 << 39), false), (0x4808_1281_000C_0082u64 & !(1 << 39), true)] {
            let mut words: Vec<u64> = ["mov r1, #5", "mov r2, #5"]
                .iter()
                .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
                .collect();
            words.extend([word, usse_isa::encode("nop.end", Core::Sgx545).unwrap()]);
            let mut m = Machine::default();
            let mut mem = Memory { base: 0x1000, words: vec![0; 4] };
            let r = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100);
            assert_eq!(r == Ok(()), ok, "{word:#x}: {r:?}");
        }
    }

    /// p0 of one raw test word on (r1, r2), read as E499 read it (`mov r10, #0; p0 mov r10, #1`).
    fn test_word_p0(word: u64, a: u32, b: u32) -> Result<u32, Error> {
        let mut words: Vec<u64> =
            [format!("mov r1, #0x{a:08x}"), format!("mov r2, #0x{b:08x}"), "mov r10, #0".into()]
                .iter()
                .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
                .collect();
        words.extend([
            word,
            usse_isa::encode("p0 mov r10, #1", Core::Sgx545).unwrap(),
            usse_isa::encode("nop.end", Core::Sgx545).unwrap(),
        ]);
        let (mut m, mut mem) = (Machine::default(), Memory { base: 0x1000, words: vec![0; 4] });
        m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100).map(|_| m.r[10])
    }

    #[test]
    fn the_test_field_on_the_shifts_the_sums_and_with_the_o_join() {
        // E1062 (r16-usse utest, 14 rows): the test field enc[43:40] = 0 to 15 under the a join
        // (enc[39] set) and the o join (clear), chan0, on six pairs a form; the hardware's p0 of
        // field f is bit f of each mask (a join, o join), E499's two-part rule and E529's o join
        let forms: [(&str, &str, [(u32, u32); 6], [u16; 6], [u16; 6]); 7] = [
            (
                "shl",
                "r2",
                [(0, 5), (0x8000_0000, 1), (1, 4), (0x6000_0000, 1), (0x7fff_ffff, 1), (0x1234_5678, 0)],
                [0x3303, 0x3303, 0xdd0d, 0x00dd, 0x00dd, 0xdd0d],
                [0xff3f, 0xff3f, 0xffdf, 0xddff, 0xddff, 0xffdf],
            ),
            (
                "shr",
                "r2",
                [(0, 3), (1, 1), (0x8000_0000, 0), (0xffff_ffff, 0), (0x8000_0000, 31), (0xf000_0000, 4)],
                [0x3303, 0x3303, 0x00dd, 0x00dd, 0xdd0d, 0xdd0d],
                [0xff3f, 0xff3f, 0xddff, 0xddff, 0xffdf, 0xffdf],
            ),
            (
                "asr",
                "r2",
                [(0, 7), (1, 1), (0x8000_0000, 31), (0x8000_0000, 4), (0x7fff_ffff, 30), (0x4000_0000, 2)],
                [0x3303, 0x3303, 0x00dd, 0x00dd, 0xdd0d, 0xdd0d],
                [0xff3f, 0xff3f, 0xddff, 0xddff, 0xffdf, 0xffdf],
            ),
            (
                "or",
                "#7",
                [(0, 0), (8, 0), (0x7fff_fff8, 0), (0x8000_0000, 0), (0xffff_fff8, 0), (0x1234_5670, 0)],
                [0xdd0d, 0xdd0d, 0xdd0d, 0x00dd, 0x00dd, 0xdd0d],
                [0xffdf, 0xffdf, 0xffdf, 0xddff, 0xddff, 0xffdf],
            ),
            (
                "rol",
                "#7",
                [(0, 0), (1, 0), (0x0100_0000, 0), (0x8000_0000, 0), (0xffff_ffff, 0), (0x0200_0000, 0)],
                [0x3303, 0xdd0d, 0x00dd, 0xdd0d, 0x00dd, 0xdd0d],
                [0xff3f, 0xffdf, 0xddff, 0xffdf, 0xddff, 0xffdf],
            ),
            (
                "iadd32",
                "r2",
                [(0, 0), (1, 0xffff_ffff), (0x8000, 0x8000), (5, 3), (0xffff, 0), (0x7fff, 0x7fff_ffff)],
                [0x3303, 0x3303, 0x3303, 0xdd0d, 0x00dd, 0xdd0d],
                [0xff3f, 0xff3f, 0xff3f, 0xffdf, 0xddff, 0xffdf],
            ),
            (
                "iaddu32",
                "r2",
                [
                    (0, 0),
                    (0xffff, 1),
                    (1, 0xffff_ffff),
                    (0x8000, 0x8000),
                    (0, 0x8000_0000),
                    (0xabcd, 0x1234_5678),
                ],
                [0x3303, 0xdd0d, 0xdd0d, 0xdd0d, 0xdd0d, 0xdd0d],
                [0xff3f, 0xffdf, 0xffdf, 0xffdf, 0xffdf, 0xffdf],
            ),
        ];
        for (op, src2, pairs, a_bits, o_bits) in forms {
            let text = format!("{op}.testtaz.chan0 !c0, p0, r1, {src2}");
            let base = usse_isa::encode(&text, Core::Sgx545).unwrap() & !(0xff << 36);
            for (j, &(a, b)) in pairs.iter().enumerate() {
                for (join, bits) in [(8u64, a_bits[j]), (0, o_bits[j])] {
                    for f in 0..16u64 {
                        let r = test_word_p0(base | (f << 4 | join) << 36, a, b);
                        assert_eq!(
                            r,
                            Ok((bits >> f & 1) as u32),
                            "{op} {a:#x} {b:#x} field {f:#x} join {join}"
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn the_lane_tests_with_the_o_join() {
        // E1062 (r16-usse utest t-iadd8-o, t-iadd16-o): the chan field chan0 to or02 under the o join
        // on iadd8 (bytes 0, 3, 0xf1, 8) and iadd16 (halves 0 and -15; chan1 and chan3 without a
        // lane), the nine fields the assembler names; bit f of each chan's mask is the hardware's p0
        // (the same masks on both operations), and E1062's a join rows as before
        let o: [u16; 8] = [0x0737, 0x0757, 0x0577, 0x0757, 0x0517, 0x0777, 0x0537, 0x0777];
        let a: [u16; 8] = [0x0303, 0x0505, 0x0055, 0x0505, 0x0001, 0x0757, 0x0001, 0x0357];
        for (op, x, y) in [("iadd8", 0x05f0_0100u32, 0x0301_0200u32), ("iadd16", 0xfff0_0005, 0x0001_fffb)] {
            let base = usse_isa::encode(&format!("{op}.testtaz.chan0 !c0, p0, r1, r2"), Core::Sgx545)
                .unwrap()
                & !(0xff << 36);
            for chan in 0..8u64 {
                for f in [0u64, 1, 2, 4, 5, 6, 8, 9, 10] {
                    for (join, bits) in [(0u64, o[chan as usize]), (8, a[chan as usize])] {
                        let r = test_word_p0(base | (f << 4 | join | chan) << 36, x, y);
                        assert_eq!(
                            r,
                            Ok((bits >> f & 1) as u32),
                            "{op} chan {chan} field {f:#x} join {join}"
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn a_write_mask_on_an_iaddu32_test_repeats_it() {
        // E1061 (r16-usse urpt): iaddu32.testtaz.chan0 r10.xy (.xyzw), p0, r1, r5 writes r10 + k with
        // (r1 + k & 0xffff) + r5 + k, as the masks of the other forms (component k from the sources
        // advanced by k); the predicate it leaves was not read, so a later read of it is refused
        let a = [0x8000u32, 0x8001, 0xabcd, 0xffff];
        let b = [0x8000u32, 0x7fff_0000, 1, 0xffff_ffff];
        let want = [0x0001_0000u32, 0x7fff_8001, 0x0000_abce, 0x0000_fffe];
        for (mask, n) in [(".xy", 2), (".xyzw", 4)] {
            let mut init: Vec<String> = (0..4).map(|k| format!("mov r{}, #0x{:08x}", 1 + k, a[k])).collect();
            init.extend((0..4).map(|k| format!("mov r{}, #0x{:08x}", 5 + k, b[k])));
            init.extend((0..4).map(|k| format!("mov r{}, #0xa0a0a0a{k}", 10 + k)));
            let text = format!("iaddu32.testtaz.chan0 r10{mask}, p0, r1, r5");
            let (m, r) = with(&init, &[text.as_str()]);
            assert_eq!(r, Ok(()), "{mask}");
            for k in 0..4 {
                let w = if k < n { want[k] } else { 0xa0a0_a0a0 | k as u32 };
                assert_eq!(m.r[10 + k], w, "{mask} r{}", 10 + k);
            }
            assert!(refused(&with(&init, &[text.as_str(), "p0 mov r20, #1"]).1), "{mask}: p0 after the mask");
        }
        // the mask on the other tests was not run
        assert!(refused(&with(&set(1, 2, 3), &["iadd32.testtaz.chan0 r10.xy, p0, r1, r2"]).1));
        assert!(refused(&with(&set(1, 2, 3), &["and.testtaz.chan0 r10.xy, p0, r1, r2"]).1));
    }

    #[test]
    fn a_placed_program_counts_from_its_code_base() {
        // E476, E492: the link of a br.savelink in a program placed at heap offset X reads
        // (X mod 0x80000) / 8 + the index after the call (the vectors have a phas first: one more); a ba counts from the code base too
        let prog = ["br.savelink #1", "mov r10, pclink", "mov.end o0, r10"];
        for (offset, want) in [(0x1a0000u32, 0x4001u32), (0x2ff000, 0xfe01), (0x300008, 2), (0x10000, 0x2001)]
        {
            let words: Vec<u64> = prog.iter().map(|t| usse_isa::encode(t, Core::Sgx545).unwrap()).collect();
            let mut m = Machine { code_index: offset % 0x80000 / 8, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 4] };
            assert_eq!((m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100), m.o[0]), (Ok(()), want));
        }
        // a lapc to the link plus 8 lands the same 8 words on, and a ba to a code-base index
        let words: Vec<u64> =
            ["br.savelink #1", "mov r10, pclink", "ba #8196", "mov.end o0, #0xBAD", "mov.end o0, #0x600D"]
                .iter()
                .map(|t| usse_isa::encode(t, Core::Sgx545).unwrap())
                .collect();
        let mut m = Machine { code_index: 8192, ..Machine::default() };
        let mut mem = Memory { base: 0x1000, words: vec![0; 4] };
        assert_eq!((m.run(&Program::new(&words, Core::Sgx545), &mut mem, 100), m.o[0]), (Ok(()), 0x600d));
    }

    #[test]
    fn a_placed_program_counts_on_across_the_code_step() {
        // E1098 (r23-pk q123, q123h): the index is an 18-bit counter from the code base, so a run
        // of nops, a ba and a lapc cross 0xffff to 0x10000 and 0x1ffff to 0x20000; every word
        // outside the code ends with o0 = 0xb0000000 | its word (gen/q123.py's pads)
        let pad = |k: usize| format!("mov.skipinv.end o0, #0x{:08X}", 0xB000_0000u32 | k as u32);
        let placed = |code: Vec<String>, n: usize| -> Vec<u64> {
            let mut t = code;
            let k0 = t.len();
            t.extend((k0..n).map(pad));
            t.iter().map(|w| usse_isa::encode(w, Core::Sgx545).unwrap()).collect()
        };
        for (idx0, n, kind, t) in [
            (0x8000u32, 600usize, "run", 590usize),
            (0x8000, 600, "lapc", 590),
            (0xffc0, 600, "run", 590),
            (0xffc0, 600, "ba", 80),
            (0xffc0, 600, "lapc", 80),
            (0xf000, 8192, "run", 8100),
            (0x1ffc0, 600, "run", 590),
            (0x1ffc0, 600, "ba", 80),
            (0x1ffc0, 600, "lapc", 80),
        ] {
            let tgt = idx0 + t as u32;
            let mut code = vec!["phas #0, #0, pixel, end, parallel".to_string()];
            match kind {
                "run" => code.extend((1..t).map(|_| "nop".to_string())),
                "ba" => code.extend([format!("ba #0x{tgt:05X}"), "mov.skipinv.end o0, #0xFA11".into()]),
                _ => code.extend([
                    "nop".into(),
                    format!("mov.skipinv r5, #0x{tgt:05X}"),
                    "mov pclink, r5".into(),
                    "nop".into(),
                    "lapc".into(),
                    "mov.skipinv.end o0, #0xFA11".into(),
                ]),
            }
            let words = placed(code, n);
            let mut m = Machine { code_index: idx0, ..Machine::default() };
            let mut mem = Memory { base: 0x1000, words: vec![0; 4] };
            let ran = m.run(&Program::new(&words, Core::Sgx545), &mut mem, 20000);
            assert_eq!((ran, m.o[0]), (Ok(()), 0xB000_0000 | t as u32), "{kind} at {idx0:#x}");
        }
    }
}
