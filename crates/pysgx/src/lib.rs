// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! pysgx: the Rust tooling for the Python scripts (crates/README.md).
//!
//! - `usse_decode`, `usse_encode`, `pds_decode`, `pds_encode`: one word, one text.
//! - `assemble(source, file, core)`: sgx-asm in-process; sections with their
//!   images, labels and patch records, as `sgx-asm -d` writes them to map.json.
//! - `Program`, `Machine`: the USSE simulator. A run reads memory, SGX registers
//!   and task emissions through a bus, any Python object with the methods
//!   `load32(addr)`, `store32(addr, value)`, `reg_read(index)`,
//!   `reg_write(index, value)`, `emit(text, (a, b, c))`; a missing one stops the
//!   program as the simulator's own buses do.
//! - `Sgx`: one SGX as its microkernel sees it (sgx_sim::sgx): device memory,
//!   the register file and the event -> PDS -> USSE task loop.

use pyo3::call::PyCallArgs;
use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};
use sgx_sim::{Bus, Error};
use sgx_tools::asm;
use usse_isa::Core;

create_exception!(pysgx, AsmError, PyException, "sgx-asm's messages, one per line.");
create_exception!(
    pysgx,
    SimError,
    PyException,
    "The simulator stopped: args are (kind, message), kind one of unsupported, fault, pc, steps."
);

fn core(c: u32) -> PyResult<Core> {
    match c {
        540 => Ok(Core::Sgx540),
        545 => Ok(Core::Sgx545),
        _ => Err(PyValueError::new_err("core must be 540 or 545")),
    }
}

/// The text of a USSE instruction word, as usse-dis prints it.
#[pyfunction]
#[pyo3(signature = (word, core = 545))]
fn usse_decode(word: u64, core: u32) -> PyResult<String> {
    Ok(usse_isa::decode(word, self::core(core)?).text)
}

/// The word of a USSE instruction text, or None.
#[pyfunction]
#[pyo3(signature = (text, core = 545))]
fn usse_encode(text: &str, core: u32) -> PyResult<Option<u64>> {
    Ok(usse_isa::encode(text, self::core(core)?))
}

/// The text of a PDS instruction word, as pds-dis prints it.
#[pyfunction]
fn pds_decode(word: u32) -> String {
    pds_isa::decode(word).text
}

/// The word of a PDS instruction text, or None.
#[pyfunction]
fn pds_encode(text: &str) -> Option<u32> {
    pds_isa::encode(text)
}

#[derive(FromPyObject)]
enum Source {
    Text(String),
    Bytes(Vec<u8>),
}

/// Assemble an sgx-asm source: a dict with "sections" (name, isa, id, image,
/// data), "symbols" (name, section, index, offset) and "patches" (section, id,
/// offset, encoding, kind, target, addend), as in sgx-asm's map.json. `file`
/// names the source in messages; .include is relative to its directory.
#[pyfunction]
#[pyo3(signature = (source, file = "<string>", core = 545))]
fn assemble<'py>(py: Python<'py>, source: Source, file: &str, core: u32) -> PyResult<Bound<'py, PyDict>> {
    let text = match source {
        Source::Text(s) => s.into_bytes(),
        Source::Bytes(b) => b,
    };
    let p = asm::assemble_program(&text, file, self::core(core)?, false);
    if p.errors > 0 {
        return Err(AsmError::new_err(String::from_utf8_lossy(&p.messages).trim_end().to_string()));
    }
    let sections = PyList::empty(py);
    for s in &p.sections {
        let d = PyDict::new(py);
        let image: Vec<u8> = s.words.iter().flat_map(|w| w.to_le_bytes()[..s.isa.width].to_vec()).collect();
        d.set_item("name", &s.name)?;
        d.set_item("isa", s.isa_name())?;
        d.set_item("id", s.id)?;
        d.set_item("image", PyBytes::new(py, &image))?;
        d.set_item("data", s.ndata)?;
        sections.append(d)?;
    }
    let symbols = PyList::empty(py);
    for y in &p.symbols {
        let d = PyDict::new(py);
        d.set_item("name", &y.name)?;
        d.set_item("section", &p.sections[y.section].name)?;
        d.set_item("index", y.index)?;
        d.set_item("offset", y.offset)?;
        symbols.append(d)?;
    }
    let patches = PyList::empty(py);
    for r in &p.patches {
        let d = PyDict::new(py);
        let s = &p.sections[r.section];
        d.set_item("section", &s.name)?;
        d.set_item("id", s.id)?;
        d.set_item("offset", r.offset)?;
        d.set_item("encoding", asm::ENCODINGS[r.encoding])?;
        d.set_item("kind", asm::KINDS[r.kind].name)?;
        d.set_item("target", r.target)?;
        d.set_item("addend", r.addend)?;
        patches.append(d)?;
    }
    let out = PyDict::new(py);
    out.set_item("sections", sections)?;
    out.set_item("symbols", symbols)?;
    out.set_item("patches", patches)?;
    Ok(out)
}

/// A USSE program, decoded once.
#[pyclass(unsendable)]
struct Program {
    p: sgx_sim::Program,
    len: usize,
}

#[pymethods]
impl Program {
    #[new]
    #[pyo3(signature = (words, core = 545))]
    fn new(words: Vec<u64>, core: u32) -> PyResult<Self> {
        Ok(Program { p: sgx_sim::Program::new(&words, self::core(core)?), len: words.len() })
    }

    fn __len__(&self) -> usize {
        self.len
    }

    /// The text of the instruction at `pc`.
    fn text(&self, pc: usize) -> Option<String> {
        sgx_sim::Machine::text(&self.p, pc).map(String::from)
    }
}

/// The bus a run goes through: the Python object's methods.
struct PyBus<'a, 'py> {
    obj: &'a Bound<'py, PyAny>,
    /// the first exception a method raised; the run stops on it
    err: Option<PyErr>,
}

impl<'py> PyBus<'_, 'py> {
    fn has(&self, name: &str) -> bool {
        self.obj.hasattr(name).unwrap_or(false)
    }

    /// Call a method; an exception is kept and stops the program.
    fn call<T: FromPyObjectOwned<'py>>(
        &mut self,
        name: &str,
        args: impl PyCallArgs<'py>,
    ) -> Result<T, Error> {
        match self.obj.call_method1(name, args).and_then(|v| v.extract::<T>().map_err(Into::into)) {
            Ok(v) => Ok(v),
            Err(e) => {
                let why = format!("bus.{name} raised {e}");
                self.err.get_or_insert(e);
                Err(Error::Unsupported { pc: 0, text: String::new(), why })
            }
        }
    }
}

fn no(what: String) -> Error {
    Error::Unsupported { pc: 0, text: String::new(), why: what }
}

impl Bus for PyBus<'_, '_> {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        if !self.has("load32") {
            return Err(Error::Fault(addr));
        }
        // None: nothing there
        let v: Option<u32> = self.call("load32", (addr,))?;
        v.ok_or(Error::Fault(addr))
    }

    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        if !self.has("store32") {
            return Err(Error::Fault(addr));
        }
        let ok: Option<bool> = self.call("store32", (addr, v))?;
        if ok == Some(false) { Err(Error::Fault(addr)) } else { Ok(()) }
    }

    fn reg_read(&mut self, index: u32) -> Result<u32, Error> {
        if !self.has("reg_read") {
            return Err(no(format!("ldr #{index}: no SGX registers on this bus")));
        }
        self.call("reg_read", (index,))
    }

    fn reg_write(&mut self, index: u32, v: u32) -> Result<(), Error> {
        if !self.has("reg_write") {
            return Err(no(format!("str #{index}: no SGX registers on this bus")));
        }
        let _: Option<bool> = self.call("reg_write", (index, v))?;
        Ok(())
    }

    fn emit(&mut self, text: &str, srcs: [u32; 3]) -> Result<(), Error> {
        if !self.has("emit") {
            return Err(no(format!("{text}: no task emission on this bus")));
        }
        let _: Option<bool> = self.call("emit", (text.to_string(), (srcs[0], srcs[1], srcs[2])))?;
        Ok(())
    }
}

fn sim_error(e: Error) -> PyErr {
    let kind = match e {
        Error::Unsupported { .. } => "unsupported",
        Error::Fault(_) => "fault",
        Error::PcOutOfRange(_) => "pc",
        Error::StepLimit => "steps",
    };
    SimError::new_err((kind, e.to_string()))
}

/// One USSE instance. Registers a program reads must have been written, by
/// the program or with `set` (the simulator stops on anything else).
#[pyclass(unsendable)]
struct Machine {
    m: sgx_sim::Machine,
}

/// A bank's registers and its written-bits.
fn bank<'m>(m: &'m mut sgx_sim::Machine, name: &str) -> PyResult<(&'m mut [u32], &'m mut u128)> {
    let w = &mut m.written;
    Ok(match name {
        "r" => (&mut m.r[..], &mut w.r),
        "o" => (&mut m.o[..], &mut w.o),
        "pa" => (&mut m.pa[..], &mut w.pa),
        "sa" => (&mut m.sa[..], &mut w.sa),
        _ => return Err(PyValueError::new_err(format!("no bank '{name}' (r, o, pa, sa, i)"))),
    })
}

#[pymethods]
impl Machine {
    #[new]
    #[pyo3(signature = (core = 545, near = false))]
    fn new(core: u32, near: bool) -> PyResult<Self> {
        let mut m = sgx_sim::Machine { core: self::core(core)?, ..Default::default() };
        m.near = near;
        Ok(Machine { m })
    }

    /// Register `n` of bank r, o, pa, sa or i.
    fn get(&mut self, bank: &str, n: usize) -> PyResult<u32> {
        if bank == "i" {
            return self.m.i.get(n).copied().ok_or_else(|| PyValueError::new_err("i0-i3"));
        }
        let (regs, _) = self::bank(&mut self.m, bank)?;
        regs.get(n).copied().ok_or_else(|| PyValueError::new_err(format!("{bank}{n}: no such register")))
    }

    /// Set register `n` of a bank, as the job would before the task starts.
    fn set(&mut self, bank: &str, n: usize, value: u32) -> PyResult<()> {
        if bank == "i" {
            if n >= 4 {
                return Err(PyValueError::new_err("i0-i3"));
            }
            self.m.i[n] = value;
            self.m.written.i |= 1 << n;
            return Ok(());
        }
        let (regs, written) = self::bank(&mut self.m, bank)?;
        let Some(r) = regs.get_mut(n) else {
            return Err(PyValueError::new_err(format!("{bank}{n}: no such register")));
        };
        *r = value;
        *written |= 1u128 << n;
        Ok(())
    }

    /// Predicate `n` (0-3).
    fn pred(&self, n: usize) -> PyResult<bool> {
        self.m.p.get(n).copied().ok_or_else(|| PyValueError::new_err("p0-p3"))
    }

    fn set_pred(&mut self, n: usize, value: bool) -> PyResult<()> {
        if self.m.set_pred(n, value) { Ok(()) } else { Err(PyValueError::new_err("p0-p3")) }
    }

    #[getter]
    fn pc(&self) -> usize {
        self.m.pc
    }

    #[setter]
    fn set_pc(&mut self, pc: usize) {
        self.m.pc = pc;
    }

    #[getter]
    fn steps(&self) -> usize {
        self.m.steps
    }

    /// Run from `pc` until an instruction with `.end` retires; raises SimError
    /// when the simulator stops, or what a bus method raised.
    #[pyo3(signature = (program, bus, max_steps = 100_000))]
    fn run(&mut self, program: &Program, bus: &Bound<'_, PyAny>, max_steps: usize) -> PyResult<()> {
        let mut b = PyBus { obj: bus, err: None };
        let r = self.m.run(&program.p, &mut b, max_steps);
        if let Some(e) = b.err {
            return Err(e);
        }
        r.map_err(sim_error)
    }

    /// Run one instruction: True when it ended the program.
    fn step(&mut self, program: &Program, bus: &Bound<'_, PyAny>) -> PyResult<bool> {
        let mut b = PyBus { obj: bus, err: None };
        let r = self.m.step(&program.p, &mut b);
        if let Some(e) = b.err {
            return Err(e);
        }
        r.map_err(sim_error)
    }
}

/// One SGX as its microkernel sees it: device memory, the register file, the
/// PDS and the USSE, and the work between them (sgx_sim::sgx). Host register
/// writes may queue work (EVENT_KICK2, EVENT_KICK); `run` does it.
#[pyclass(unsendable)]
struct Sgx {
    s: sgx_sim::sgx::Sgx,
    mem_trace: Option<std::rc::Rc<std::cell::RefCell<Vec<sgx_sim::trace::Ev>>>>,
}

impl Sgx {
    fn hw(&mut self) -> PyResult<&mut sgx_sim::hw::HwModel> {
        self.s.st.hw.as_mut().ok_or_else(|| PyValueError::new_err("no hardware model: hw_enable() first"))
    }
}

#[pymethods]
impl Sgx {
    #[new]
    fn new() -> Self {
        Sgx { s: sgx_sim::sgx::Sgx::default(), mem_trace: None }
    }

    /// Map `data` at device address `addr`.
    fn map(&mut self, addr: u32, data: &[u8]) {
        self.s.st.mem.map(addr, data);
    }

    fn load32(&self, addr: u32) -> PyResult<u32> {
        self.s.st.mem.load(addr).map_err(sim_error)
    }

    fn store32(&mut self, addr: u32, value: u32) -> PyResult<()> {
        self.s.st.mem.store(addr, value).map_err(sim_error)
    }

    /// A register value known from the hardware, readable before anything writes it.
    fn seed(&mut self, index: u32, value: u32) {
        self.s.seed(index, value);
    }

    /// A host register write.
    fn write_reg(&mut self, index: u32, value: u32) -> PyResult<()> {
        self.s.write_reg(index, value).map_err(sim_error)
    }

    /// An event: the other-event PDS program with the event word `ir1` (and event_ir0,
    /// event_tim); the timer tick is event_ir0 = 2 with ir1 = 0.
    fn event(&mut self, ir1: u32) -> PyResult<()> {
        self.s.event(ir1).map_err(sim_error)
    }

    /// Register `index`, or None if nothing wrote or seeded it.
    fn reg(&self, index: u32) -> Option<u32> {
        self.s.st.regs.get(&index).copied()
    }

    /// The EDM's secondary attribute `n`, or None if nothing wrote it.
    fn sa(&self, n: usize) -> Option<u32> {
        (n < 128 && self.s.st.sa_written >> n & 1 != 0).then(|| self.s.st.sa[n])
    }

    #[getter]
    fn steps(&self) -> usize {
        self.s.steps
    }

    /// An event program's ir0 (EVENT_KICK), which the hardware gives; None: unknown.
    #[getter]
    fn event_ir0(&self) -> Option<u32> {
        self.s.event_ir0
    }

    #[setter]
    fn set_event_ir0(&mut self, v: Option<u32>) {
        self.s.event_ir0 = v;
    }

    /// The counter (tim) an event program reads (EVENT_KICK); None: unknown.
    #[getter]
    fn event_tim(&self) -> Option<u32> {
        self.s.event_tim
    }

    #[setter]
    fn set_event_tim(&mut self, v: Option<u32>) {
        self.s.event_tim = v;
    }

    /// The assumption that a movs reads specials 1 and 2 as the ALU does (off by default).
    #[getter]
    fn alu_specials_in_movs(&self) -> bool {
        self.s.alu_specials_in_movs
    }

    #[setter]
    fn set_alu_specials_in_movs(&mut self, v: bool) {
        self.s.alu_specials_in_movs = v;
    }

    /// The instructions a task reads from its code base (None: the default window).
    #[getter]
    fn code_len(&self) -> Option<usize> {
        self.s.code_len
    }

    #[setter]
    fn set_code_len(&mut self, v: Option<usize>) {
        self.s.code_len = v;
    }

    /// Carry the task state that outlives a task (sgx_sim::sgx::Carry, E536) from here on, the
    /// next entry seeded with these values (None: unknown, a read of it is refused).
    #[pyo3(signature = (pclink = None, p = None, r20 = None, r21 = None, i0 = None, i1 = None))]
    fn seed_carry(
        &mut self,
        pclink: Option<u32>,
        p: Option<[Option<bool>; 4]>,
        r20: Option<u32>,
        r21: Option<u32>,
        i0: Option<u32>,
        i1: Option<u32>,
    ) {
        self.s.carry = Some(sgx_sim::sgx::Carry { pclink, p: p.unwrap_or_default(), r20, r21, i0, i1 });
    }

    /// The carried task state as a dict, or None when nothing is carried.
    fn carry<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyDict>>> {
        let Some(c) = &self.s.carry else { return Ok(None) };
        let d = PyDict::new(py);
        d.set_item("pclink", c.pclink)?;
        d.set_item("p", c.p.to_vec())?;
        d.set_item("r20", c.r20)?;
        d.set_item("r21", c.r21)?;
        d.set_item("i0", c.i0)?;
        d.set_item("i1", c.i1)?;
        Ok(Some(d))
    }

    /// Run the queued work until none is left; raises SimError when it stops.
    #[pyo3(signature = (max_steps = 1_000_000))]
    fn run(&mut self, max_steps: usize) -> PyResult<()> {
        self.s.run(max_steps).map_err(sim_error)
    }

    /// Passes run to the end (the queue empty), counted from 0.
    #[getter]
    fn passes(&self) -> u64 {
        self.s.passes
    }

    /// Trace the run from here on into `path` (JSON lines; sgx_sim::trace): refused unless the
    /// path lies under `<private>/firmware/fwsim/`, `private` defaulting to
    /// $RESGX545_DATA_PRIVATE. Without a path the events are kept in memory (`trace_events`).
    #[pyo3(signature = (path = None, private = None))]
    fn trace_to(
        &mut self,
        path: Option<std::path::PathBuf>,
        private: Option<std::path::PathBuf>,
    ) -> PyResult<()> {
        use sgx_sim::trace::FileSink;
        let Some(path) = path else {
            let rec = std::rc::Rc::new(std::cell::RefCell::new(Vec::new()));
            self.mem_trace = Some(rec.clone());
            self.s.trace_to(Box::new(rec));
            return Ok(());
        };
        let private =
            private.or_else(|| std::env::var_os("RESGX545_DATA_PRIVATE").map(Into::into)).ok_or_else(
                || PyValueError::new_err("trace_to: no private data directory (RESGX545_DATA_PRIVATE)"),
            )?;
        let sink = FileSink::create(&path, &private).map_err(PyValueError::new_err)?;
        self.mem_trace = None;
        self.s.trace_to(Box::new(sink));
        Ok(())
    }

    /// The in-memory trace's events so far, as JSON lines (`trace_to()` without a path).
    fn trace_events(&self) -> Vec<String> {
        self.mem_trace.as_ref().map_or_else(Vec::new, |r| r.borrow().iter().map(|e| e.json()).collect())
    }

    /// Stop tracing (a file is flushed and closed).
    fn finish_trace(&mut self) -> PyResult<()> {
        self.mem_trace = None;
        match self.s.take_trace() {
            Some(Err(e)) => Err(PyValueError::new_err(e.to_string())),
            _ => Ok(()),
        }
    }

    /// Put a hardware model behind the register reads (sgx_sim::hw::HwModel): from here on a
    /// read is a run write, a cited seed, a landed rule or a reset value, or the run stops.
    /// `reset_cite` names the kept snapshot the reset values come from.
    fn hw_enable(&mut self, reset_cite: &str) {
        let mut hw = sgx_sim::hw::HwModel::default();
        hw.reset_from(reset_cite);
        self.s.st.hw = Some(hw);
    }

    fn hw_reset(&mut self, index: u32, value: u32) -> PyResult<()> {
        self.hw()?.reset(index, value);
        Ok(())
    }

    /// A seed; refused without an E-number in `cite`.
    fn hw_seed(&mut self, index: u32, value: u32, cite: &str) -> PyResult<()> {
        self.hw()?.seed(index, value, cite).map_err(PyValueError::new_err)
    }

    /// CR_USE0_SERV_EVENT's E009 rule: `value` now, one count a tick.
    fn hw_count_serv_events(&mut self, value: u32, cite: &str) -> PyResult<()> {
        self.hw()?.count_serv_events(value, cite).map_err(PyValueError::new_err)
    }

    fn hw_note_open(&mut self, index: u32, note: &str) -> PyResult<()> {
        self.hw()?.note_open(index, note);
        Ok(())
    }

    /// The refused reads by register index (counts).
    fn hw_refused(&mut self) -> PyResult<std::collections::BTreeMap<u32, u32>> {
        Ok(self.hw()?.refused.clone())
    }

    /// The answered reads by source name (counts).
    fn hw_answered(&mut self) -> PyResult<std::collections::BTreeMap<String, u64>> {
        Ok(self.hw()?.answered.clone())
    }

    /// What happened, in order: ("write", host, index, value), ("pds", addr,
    /// data dwords, ir0 or None), ("task", code base, instruction, temporaries).
    fn log<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        use sgx_sim::sgx::Event;
        let out = PyList::empty(py);
        for e in &self.s.st.log {
            match *e {
                Event::Write { host, index, value } => out.append(("write", host, index, value))?,
                Event::Pds { addr, data, ir0 } => out.append(("pds", addr, data, ir0))?,
                Event::Task { base, pc, temps } => out.append(("task", base, pc, temps))?,
            }
        }
        Ok(out)
    }
}

#[pymodule]
fn pysgx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(usse_decode, m)?)?;
    m.add_function(wrap_pyfunction!(usse_encode, m)?)?;
    m.add_function(wrap_pyfunction!(pds_decode, m)?)?;
    m.add_function(wrap_pyfunction!(pds_encode, m)?)?;
    m.add_function(wrap_pyfunction!(assemble, m)?)?;
    m.add_class::<Program>()?;
    m.add_class::<Machine>()?;
    m.add_class::<Sgx>()?;
    m.add("AsmError", m.py().get_type::<AsmError>())?;
    m.add("SimError", m.py().get_type::<SimError>())?;
    Ok(())
}
