# crates — the Rust tooling

The core tooling moves to Rust, with PyO3 bindings (`pysgx`), while the Python analysis scripts
(`kick3d`, `state3d`, `diff3d`, `edmtrace`, `ccb`, ...) stay Python. The kernel side stays C:
Rust-for-Linux has no i686 support, so the Rust tools generate the kernel's inputs.
Everything here builds and tests offline on Linux and macOS.

| crate | role |
|---|---|
| `usse-isa` | USSE decoder and encoder: the form engine, operand kinds, the SGX545 form table |
| `pds-isa` | PDS decoder and encoder: its code kinds and form table, on `usse-isa`'s engine |
| `sgx-sim` | USSE and PDS simulators over `decode_fields`, held to the hardware vectors |
| `sgx-pipe` | the pipeline simulator over `sgx-sim` (phase 12): one module per fixed-function unit, unit and scene vectors, the `Edm` seam; 12.0 has refusing stubs and four checked rules; 12.1 runs a fill or a copy; 12.2 a render's vertex side and the TA's output; 12.3 the ISP and the first triangle's image |
| `sgx-tools` | CLIs: `usse-dis`, `pds-dis`, `usse-asm`, `pds-asm` (each as its C twin), `sgx-asm` (sections + patch map), `sgx-sim` |
| `pysgx` | the Python module: decode/encode, `sgx-asm` in-process, the simulator with a Python bus |

Still to come: the rest of `sgx-sim` (the video filters `bilin`, `firv` and `firh`, the visibility
and MOE groups; past the boot, the timer and the CCB in the task loop). The firmware format
stays in Python (`tools/fwcutter`), reached through `pysgx`. `pysgx` is the only crate with
external dependencies (pyo3); the core crates stay dependency-free, so that a Mesa compiler
written in Rust could reuse them.

## Build and test

```sh
cargo test                       # unit tests, cross-checks with the C tools, the vectors
cargo run -p sgx-tools --bin usse-dis -- <blob.bin> [max_words]
cargo run -p sgx-tools --bin usse-asm -- -l -o out.bin asm/transfer/use_fill.s
cargo run -p sgx-tools --bin sgx-sim -- --trace prog.s     # run a program, trace its writes
cargo run -p sgx-tools --bin sgx-sim -- --vectors $RESGX545_DATA/vectors/vec1.vec.json
cargo clippy --all-targets && cargo fmt --check
```

## pysgx

`crates/pysgx` builds a CPython extension (abi3, Python 3.11+) against `.venv/bin/python`
(`.cargo/config.toml`). No maturin: `crates/pysgx/load.py` runs `cargo build -p pysgx`, copies
the library to `target/pysgx/pysgx.abi3.so` and imports it.

```python
sys.path.insert(0, "crates/pysgx"); import load; pysgx = load.pysgx()
pysgx.usse_decode(0xFCA4000100000000)        # 'mov.skipinv.end o0, #0x00000000'
p = pysgx.assemble(open("asm/transfer/transfer.s", "rb").read(), "asm/transfer/transfer.s")
m = pysgx.Machine(); m.set("r", 1, 5)        # registers the job sets before the task
m.run(pysgx.Program(words), bus)             # bus: load32, store32, reg_read, reg_write, emit
```

`assemble` returns what `sgx-asm -d` writes to `map.json`, each section's image as bytes;
`tools/fwcutter/asmmap.py` reads either (`assemble_in_process`). A bus method that is missing
stops the program as the simulator's own buses do; one that raises stops it with that
exception; a stop of the simulator raises `pysgx.SimError(kind, message)`.
`crates/pysgx/tests/test_pysgx.py` (pytest) checks it against the command-line tools.

The Rust tools may add what their C twins lack, behind options of their own, while everything
the C tools do stays identical: `usse-asm --explain` and `pds-asm --explain` follow each "cannot
assemble" with the closest forms (`usse_isa::explain`), as `sgx-sim` always does. Their sources
may also use `.include`, `.equ` with C expressions (`sgx_tools::expr`) and `.macro`
(`tools/usse-asm/README.md`, "Rust-only extensions"); `tests/asm_ext.rs` checks each against
the same source written out by hand. `sgx-asm` adds sections and patch records
(`tests/sgx_asm.rs`).

`sgx-sim` runs a USSE program (assembly source, or raw words with the `.bin` suffix) on the
simulator, as one instance or with `--quad X,Y` as the 2x2 quad holding pixel (X, Y), in the probe
harness's scratch memory; `--set REG=VALUE` presets registers, `--trace` prints each instruction
with what it wrote, and the end state lists every register written and every scratch dword changed.
An instruction the simulator does not model stops it with the reason (exit status 1). `--near` lets
the float functions give near values (below), each printed with `~ <bound>`. `--temps N` sets the
temporaries allocated to the task (124 by default; the probes run with 32), `--max N` the step limit
and `--core 540|545` the core. `--vectors FILE [--id ID]` runs vector files (`vectors/` of
resgx545-data) against their readbacks, the PDS ones included. `--pds` runs a PDS program instead
(pds-asm source, or raw words with `--data N`): `--set` presets `dsB[n]`, `ir0`-`ir2`, `tim`, `if0`
and `if1`, `--trace` prints each instruction with its writes, and the port writes are listed with
their words.

`cargo run --release -p usse-isa --example decode_bench` measures decoding: text (`decode`)
and structured (`decode_fields`, the form and its field values, which the simulator uses).
Both walk only the forms of the word's major class (`Table`); most of the time goes into
printing fields, which `decode_fields` avoids through `Kind::valid`. On an M-series Mac,
2026-10-23: text 344 ns, structured 118 ns per word (the linear walk with text: 367 ns).

The cross-checks run the C tools and skip without them:

- **`usse-isa`'s `tests/c_crosscheck.rs`** and `sgx-tools`' **`tests/usse_dis_cli.rs`** run
  the C decoder (`make -C tools/usse-dis`, or `$USSE_DIS_C`). They compare the `--forms`
  listing, then the text and the form index of 418k words per core (uniform random words,
  and 1000 words matching each form), and the CLI's output for every option.
- **`pds-isa`'s `tests/c_crosscheck.rs`** and `sgx-tools`' **`tests/pds_dis_cli.rs`** do the
  same for PDS (`tools/usse-dis/pds-dis`).

## Two decoders, one table

`tools/usse-dis` (C) stays: radare2 is C and the upstream plugin needs plain C. Both decoders
take their form tables from one description, `isa/usse/` and `isa/pds/` (`isa/README.md`): each
crate's `src/table.rs` is generated by `isa/gen.py` and committed. What is written twice is the
code kinds (`src/kinds.rs`, `src/forms/*.rs`, and their C twins), under the C names, and the
cross-check holds them to each other.

The generated table is `#[rustfmt::skip]`; everything else is `cargo fmt`.

The encoder (`usse_isa::encode`) is the C engine read step for step: the same matching, the
same order of the value search, the same check that the table decodes the word back, so both
pick the same word for a text. `tests/asm_crosscheck.rs` (and `pds-isa`'s tests) assemble the
text of decoded words, and respelled variants of it (case, decimal numbers, blanks, without
the disassembler's comments), with the C assembler and compare; `sgx-tools`' `asm_cli.rs` runs
both `usse-asm`/`pds-asm` on every program in `asm/`, listings on stdin and
broken sources, and compares binaries, listings, messages and exit status.

## The simulator

`sgx-sim` runs USSE programs decoded once (`decode_fields`): one instance (`Machine::run`) or
the four instances of a 2x2 pixel quad in lockstep (`run_quad`), which is what `i3`, the bank-7
numbers past it, `fdsx`/`fdsy` and `efo.gpiext` read across. What each form does is part of the
ISA description: an `op` per form and role names on its fields (`isa/README.md`), generated
into the Rust table only. Memory and the SGX registers go through a `Bus`; there is no timing or
cache, and the one fixed-function unit modelled is the texture unit (*Sampling*, below).

**The semantics are the ISA reference's**: `doc/specs/usse_isa.md`, whose probe sections
give each rule with the probes that measured it. The code cites those probes, and nothing is
guessed: what the vectors do not establish stops with `Error::Unsupported`, including the reads
a single task cannot define (a register it has not written, a result whose DRC has not landed,
temporaries past its allocation, which belong to other instances).

**Near values.** The hardware's `frcp`, `frsq`, `fsqrt`, `flog`, `fexp`, `fsin` and `fcos` are
measured only to a bound (within one ulp, two for `fexp`, 2^-15 for the fixed-point `fsin` and
`fcos`); their algorithms are not known. `src/func.rs` gives the value where the hardware is
exact (the specials, powers of two, integers, ...) and otherwise, with `Machine::near` set, the
nearest value and its `Bound`. `Machine::bounds` and `near_mem` follow such values: a move or a
store keeps the bound, anything else computed from one is `Bound::Derived`, and a predicate,
address or load from one stops. The vectors accept a near value within its bound, and stop on
a derived one that differs.

**Sampling.** `smp` hands its state words, coordinates and `.pcf` reference to the bus
(`Bus::sample`); its texels land at the `wdf` like loads. `src/tex.rs` is the texture unit as
measured (point and bilinear filtering, the address modes, stride and twiddled layouts, the
formats and conversions, PCF), which `Memory` uses over its own words; a bus without one stops
the program. Mipmaps and LOD values, tiled textures and the state bits not yet understood stop.

**The hardware is the reference for both.** `src/vectors.rs` runs the vectors of `vectors/` in
resgx545-data (`doc/specs/vectors.md`, that repository's README): one instance against the scratch
buffer and `o0`, or, for a vector that reports every pixel, each quad of the fill against every
pixel. `tests/vectors.rs` requires every modelled vector to match. Without the data repository those
tests print "SKIPPED" (and fail when `RESGX545_REQUIRE_DATA` is set). A rebuilt probe whose program
differs from what ran is on a documented skip list (`vectors::SKIP`, each with its reason).
`SGX_SIM_SHOW=<text>` lists the unsupported cases of one reason (`SGX_SIM_SHOW=fsin cargo test -p
sgx-sim --test vectors -- --nocapture`). On 2026-10-23: vec1 (recorded) 533 match, 4 unsupported and
1 skipped; the probe rounds 29961 match (2755 of them with near values) and 669 unsupported; the
pixel vectors 364 match and 45 unsupported; 0 mismatches.

`cargo run --release -p sgx-sim --example coverage` writes `doc/isa/sim-coverage.json`, what the
simulator models of each form against which probes (the PDS forms in `pds_forms`); the references
render it at the end of every USSE and PDS group, and `cargo test` fails while it is stale.
Where the simulator and the reference disagreed, the vectors decided: the reference was
corrected once (`fmad16` rounds its product to binary32) and the simulator once (`rlp`'s
predicates past p3 alias p0-p3, as the reference says).

Every non-zero word of the extracted ukernel has semantics.

### PDS

`src/pds.rs` runs PDS programs the same way, over `pds-isa`'s table with an `op` and roles per
form, by the rules of `doc/specs/pds_isa.md`. `Pds` keeps the two banks across tasks, as the
hardware does, and knows only what the running program's data segment and its own writes put
there; a write to `dsB[n]` lands in `dsB[48 + (n & 15)]`. The ports go to the bus
(`Bus::port`), which says what each does. The open semantics stop: `load`/`store` and the
fences, `mr01`/`mr23`, the specials other than `ir0` in a `movs`, in `mov16`/`mov32` (which
number them their own way) and `ir1` in a test, and `if0`/`if1` and the inputs unless the task
kind gives them (`Pds::secondary()`).

`vectors::run_pds` runs a PDS vector as the fill's secondary program, whose `douta` writes
become the secondary attributes of `sa_dump.s`, and compares the stored readback; a job the
hardware lost to a hang matches a program that does not halt. Against resgx545-data, `vectors/pds1`:
101 match (every settled probe), 15 unsupported (the recorded explorations), 0 mismatches;
`vectors/pds2`: 80 match, 6 unsupported (`pds-specials`, whose inputs the task does not
give), 0 mismatches; `vectors/pds3`: 24 match, 2 unsupported (`pds-specials-paths`, the
same), 0 mismatches; `vectors/pds4`: 9 match, 2 unsupported (the recorded specials probes),
0 mismatches; `vectors/pds5`: `pds-tim-words` 9 match, the index sweeps unsupported (their
words do not decode, or read inputs the task does not give), 0 mismatches. `movs tim` loads the
counter (`EVENT_TIMER`): the `Pds` keeps what it reads back, and the task loop writes
the register; a program's `tim` is that register while it is stopped (bit 24 clear).
`sgx-tools/tests/pds_sim.rs` runs our transfer templates and the microkernel's five PDS
programs to their port writes; #13 and #14 stop at their first `movs`, which passes `ir0.l`
(all of `ir0`), `ir1.l` or `tim.l` on: the task loop does not give ir0, and the other two are
open (`doc/specs/pds_isa.md` *Open questions* 9). `sgx-tools/tests/posstore_sim.rs` runs the
position-store pixel program (`probes/pds/templates/pix_posstore.s`, run in E904) as a
triangle's pixel instance at each of the 2048 pixels of a 64 x 32 area and checks its four scratch
stores (E898).

### The task loop

`src/sgx.rs` is one SGX as the microkernel sees it: device memory in pages, the register file,
one `Pds` and the USSE, and a queue of the work between them, run one piece at a time in the
order it was issued (the hardware overlaps them). `EVENT_KICK2` runs the other-event PDS
program, and so does `EVENT_KICK` (the host's command kick), with the host-kick bit 8 in `ir1`
and the `ir0` and counter the caller gives (`event_ir0`, `event_tim`; the hardware's are not
modelled); `emitpds` starts a PDS program with its control word and address (its `ir0` and
`ir1` stay unknown, E488: not s2, unless the caller assumes `emit_s2_is_ir0`, E146 [infer]); `doutu`
starts a USSE task at its code base and instruction; `doutd` and `douta` fill the task's
primary attributes for an event, and the EDM's secondaries, which persist, for an `emitpds`.
Each rule cites `doc/specs/hw_spec.md` 11.1-11.3. A register read before anything wrote it
stops, unless the caller seeded it with a value known from the hardware.

`pysgx.Sgx` exposes it. `crates/pysgx/tests/test_sgx_boot.py` places the closed firmware (the
ukernel image, `$RESGX545_UKERNEL`) as our driver does, replays the host's boot writes and kicks:
PDS #10, the boot task, PDS #11 and #12, `edm.task.pds11` and `edm.task.init_done` run in 75
instructions, which install PDS #13, program `EVENT_TIMER` and set `HostCtl.InitStatus`.
`crates/pysgx/tests/test_sgx_ccb.py` then submits kernel CCB commands as the host does and kicks:
PDS #13 runs `edm.event.general` and the CCB fetch, GETMISCINFO fills the misc-info block with the
values the hardware reported (core and DDK identity, build options, structure sizes) and POWER IDLE
sets the power status to 4 and stops the tick (`EVENT_TIMER` = 0), as on the laptop; the same for
the unmodelled inputs at their extremes. The event program passes `ir1.l` and `tim.l` on with
`movs`, which needs `alu_specials_in_movs` (measured in a fill's secondary program; in the event
program the firmware's fast paths need `ir1.l` to read as the ALU's `ir1`, and the `tim.l` it passes
on is never read). `USE0_SERV_EVENT` is seeded as the hardware reads it (bit 16 set). The timer tick
is `Sgx::event(0)` with `event_ir0` = 2 (`pa0` bit 1, the firmware's tick test): three ticks move
only `HostCtl.ui32TimeWraps`, as the laptop's snapshots showed. A program's `tim` is `EVENT_TIMER`:
a `movs tim` writes the register.
