# SGX545 instruction vectors

A vector is one short program run on the hardware with what went in and what came out, so the
USSE and PDS simulator (`crates/sgx-sim`) can be tested offline against the hardware. Hardware
is the source of truth for semantics (rounding, flags, edge cases), and the programs are our
own assembly, so the vectors stay clean-room. The vectors live in the data repository
(resgx545-data), under `vectors/`, beside the raw readbacks they come from; this note and the
converter (`tools/usse-asm/vectors.py`) describe and make them.

## 1. Where they live

```
<data repository>/vectors/<unit>/<feature>/<probe>.vec.json
<data repository>/vectors/followup/<unit>/<feature>/<probe>.vec.json
<data repository>/vectors/knowledge/<unit>/<feature>/<probe>.vec.json
<data repository>/vectors/semantics/<unit>/<feature>/<probe>.vec.json
<data repository>/vectors/jobs/<unit>/<feature>/<probe>.job.json
<data repository>/vectors/nokernel/<unit>/<feature>/<probe>.vec.json
```

One directory per probe table (`probes/<unit>/<feature>.toml`), one file per run of one probe
of it (`<unit>/<feature>/<probe>/raw.txt`, and the same under `followup/` for the follow-up
round; `knowledge/` holds the runs of the 11.x sub-phases to 11.7, `semantics/` those of 11.13 and
`nokernel/` those of 11.23 to 11.27 and, in `nokernel/usse/fwtask-9b/`, of 11.29 (directories of
their own, so that the earlier manifests' digests stay), `jobs/` the jobs of the
files converted before vectors carried them). Every table whose probes carry a program has one; a
probe run that read back no case of its table gives no file.
Each unit's vectors are a dataset (`datasets/vectors-<unit>.toml`,
`vectors-<unit>-followup.toml`) that names the converter as its recipe.

The usse runs of the phases 11.23 to 11.27 are converted by `tools/usse-asm/convert_extra.py`, the
converter above on the recorded `bins/` with the tree's probe tables, into
`vectors/nokernel/usse/<feature>/<run>.vec.json` (a directory of its own, so that the digest of
`datasets/vectors-usse.toml` stays; `datasets/vectors-usse-nokernel.toml` is its manifest). A run
of a program placed in the code heap (`--place OFFSET=FILE`) converts with `init.placed`
(`{"offset": heap offset, "words": [...]}`, the placed program from the run's `bins/`): that program
is the one that ran, from the code base the placement gives (`Machine::code_index`, the offset
modulo 0x80000 bytes in instructions, E476 and E492), and `program.words` is the fill's stub.
The 425 vectors of the 11.32 texture batch (`datasets/vectors-texture-p1132.toml`, 17 files in
`vectors/nokernel/usse/texture-p1132/`, converted from `texture/p1132-recomp/raw/`) are fills of
2048 pixels, `pa0` the coordinates; 241 replay exactly. A fill whose table pokes the transfer
command but whose run printed no pokes carries no `init.job`; the simulator takes the YUV
formats (28 and 29) as opaque black only where `init.job.pokes` is recorded and leaves the
colour-space load flag (`xfer:17` bit 0) clear (`Machine::csc_unloaded`), so the colour-space jobs
of that batch and the landed formats-other vectors stop on them.
The 8 vectors of the 11.39 bilinear jobs (`datasets/vectors-texture-p1141.toml`, one file in
`vectors/nokernel/usse/texture-p1141/`, converted by `vectors.py convert` from
`texture/p1141-recomp/raw/p1141-bilin/raw.txt`, which `texture/p1141-recomp/make_raw.py` makes from
the kept outputs of `texture/p1141`) are fills of 2048 pixels like the 11.32 ones. They are E720's
held-out jobs, every fraction from 0 to 63 on the 1/64 grid: the joint bilinear form of the
simulator mismatched all 8, and the two-stage form (x then y, +32 and a 6-bit shift at each stage)
replays all 8, with no other vector changed. The 21 landed `smp-bilinear` vectors give the same
words under both forms, so they could not have told them apart.
`--example replay` lists the outcome of every vector, one line each (`excluded` with its reason for
those it leaves out).

The 9b runs of phase 11.29 (a firmware task of ours, `str` then `ldr`) are converted by
`tools/fwtask/make_vectors.py` into `vectors/nokernel/usse/fwtask-9b/<run>.vec.json` (4 files, 318
vectors; `datasets/vectors-usse-fwtask-9b.toml` is their manifest, and `vectors-usse-nokernel.toml`
names the other directories of `nokernel/usse/` one by one, so that its digest stays). They are kind
`firmware` (`init.task = "firmware"`): `program.words` is our wrapper as the kernel patched it
(results address 0x32140000, continue index 6), `init.page` the results page (`base`, `dwords`),
`init.mem` the page dwords that went in, `init.regs` the SGX registers (byte offsets) before the
task, `readback.mem` and `readback.regs` what the host read after. The replay runs the wrapper to
its tail call (`lapc`; the closed task it jumps to is not run) over `sgx_sim::fwtask::FwBus`; a
wrapper that does not reach it in 3 000 000 steps (10000 in 11.29; the slow task of E539 spins
100000 iterations) stops as unsupported. In a firmware task `FwBus`
allows `str` only to 0x0814 and 0x0a78, of a value inside the register's 17 or 6 bits, and sees the
write at once, in every later `ldr` and for the host (the ordering measured, E534); it allows `ldr`
of those two and of `CORE_ID`, `CORE_REVISION` and `CR_TIMER`, and stops on a register nobody
seeded. Of these only the two registers and `CR_TIMER` have a vector (X11 seeds the timer and
compares the first read only; it never advances in the model), and no vector reads `CORE_ID` or
`CORE_REVISION`, so unit tests alone cover those two. The register-index forms of `ldr` and `str`
(no run used them), an index of more than 14 bits and every other register, the clock-gate ones
included, stop the run as unsupported. The client path (`Memory`) refuses `str`, and every `ldr` but
the two identity registers, as before. Not modelled: latency, a job running, other writers, the
closed task. The coverage report counts these vectors under `firmware`, apart from the scalar and
pixel totals.

The runs of phase 11.30 (state between tasks, event words, a slow task, the temporaries) are
converted by `tools/fwtask/make_vectors1130.py` into `vectors/nokernel/usse/fwtask-state/` (14
vectors, E536), `fwtask-events/` (6, E538), `fwtask-slow/` (10, E539) and `fwtask-trc/` (1, E540),
one file each (`datasets/vectors-usse-fwtask-p1130.toml`), so that 349 firmware vectors replay
exactly. They add optional keys to a firmware vector: `init.temps` (the TRC: the task is allocated
4T temporaries, 32 when absent; a register past it still stops the run), `init.state` (what the
hardware held at the task's entry and the task reads before writing it: `sa`, `r`, `i` and `pa`,
register numbers to hex values, `p`, predicate numbers to 0 or 1, and `pclink`; a register that
neither `init.state` nor the program gave still stops the run) and `readback.state` (the `sa`, `r`,
`i` and `p` the task must have left at its tail call, compared exactly). The closed task is not run,
so a value that differs at the next entry (`sa64`, p0 and `pclink`, which are [infer] the closed
task's, and p2 and p3, which move between readings with no writer, E536) is never listed: only p1 of
the predicates is shown to persist. A read of `sa64` after the task wrote it, a state key that is
not a register and a wrapper that does not reach its tail call stop the run. The readers' vectors
are seeded with their own readback, so they check the program and the simulator's reads of the
state, not the hardware's persistence; the writers' `readback.state` is what the next event's reader
read, so "349 replay exactly" says nothing of persistence. Two contents are not measurements of the
run: the tick vectors of `fwtask-events` take `pa` from E532 (E538 masked the tick's `pa1`, its
expected log of 0 comes from the quiet window), and the writers' state is what the next reader read,
not what the writer's own task read back. Not modelled: the closed task, the event queue, ticks, the
p0 and `pclink` values at the next entry (E792, E809), the stop of E537, TRC above 31 and a write
past the allocation (the T = 8 to 24 runs of E540 also read the register past the allocation,
which the simulator stops on, so only T = 31 is a vector).

The two runs of E535 (a write to `r123` with a marker of its own per job, client fills) are
converted by `tools/usse-asm/convert_extra.py` into `vectors/nokernel/usse/q147-a/` and `q147-b/`
(18 vectors each, `datasets/vectors-usse-q147.toml`): 14 replay exactly (the controls and the
request of 448), 12 are left out (their pixels are a mixture, no single o0) and 10 stop on `r123`
past the allocation, because the simulator takes a request of 260 to 376 to allocate its value
modulo 256 (Q133).

The simulator's tests (`crates/sgx-sim/tests/vectors.rs`) look for the data repository as
`$RESGX545_DATA`, else the `resgx545-data` checkout beside this tree (as
`tools/records/datasets.py` does), and skip with a message when it is absent.

## 2. How vectors are recorded

The probe harness (`tools/usse-asm/probe.py`, `sgxfive-test probe`) runs each case as the
pixel shader of a 64 x 32 client fill on the render node: 2048 instances of the same program.
The host reads back `o0` of every pixel (reported as one value when all agree) and the
64 KiB scratch buffer, whose dword *i* starts as `0xD000_0000 | i`; templates store registers
there with `stad`. With `--coords` each instance gets `pa0 = (y << 16) | x`, with `--pixels`
every pixel is reported. A job that faults or times out is reported as failed and recovered by
the driver. The campaign runner (`tools/campaign`) runs a table and keeps the assembled cases
(`bins/<probe>__<case>.bin`) beside `raw.txt`; the converter turns the pair into vectors.

## 3. File format, version 1

One JSON file per run:

```json
{
  "format": "sgx545-vectors", "version": 1,
  "run": {"raw": "usse/movc/usse-movc-i8/raw.txt", "raw_sha256": "...",
          "converted": "2026-11-01T19:00:00+01:00", "tool": "vectors.py 1"},
  "vectors": [ { ... }, ... ],
  "orphans": ["old-name__0"]
}
```

Each vector:

| field | meaning |
|---|---|
| `id` | `<probe>__<case>`, the label `sgxfive-test probe` printed |
| `program.isa` | `usse` (64-bit words) or `pds` (32-bit words) |
| `program.words` | the program as run, each word a hex string (`0x` + 16 or 8 digits) |
| `program.entry` | index of the first instruction (0: the task starts at the program) |
| `program.source` | `recorded` (bytes sent, saved) or `rebuilt` (assembled again) |
| `program.data` | PDS only: how many dwords at the start of `words` are the data segment |
| `init.task` | `pixel`: the shader of a fill instance; `pds-secondary`: the fill's PDS secondary |
| `init.instances` | 2048 (64 x 32), in raster order |
| `init.temps` | temporaries allocated to the task (`--temps`) |
| `init.pa0` | `coords` (`(y << 16) \| x`) or `fill` (the fill's own, not specified) |
| `init.scratch` | `{"base": "0x3e003000", "bytes": 65536, "fill": "0xd0000000\|i"}`; `base` is the device address of the run's mapping (0x3e003000 in most vectors, also 0x3e006000, 0x3e012000, 0x3e082000, 0x3e402000), and 170 vectors add `low`, the address the PDS sees for the scratch; the simulator test uses the constant `SCRATCH_BASE` (0x3e003000), not `base` |
| `init.regs` | what the program's leading `mov`s preset, `{"r1": "0x..."}`; informative only |
| `init.attrs` | PDS only: the secondary attributes its `douta` may write (16: `sa0` to `sa15`) |
| `init.use` | PDS only: the fill shader that reads them and stores them to scratch dwords 0-15 |
| `init.job` | a fill's job: `pokes`, the transfer-command pokes the run printed, and `use_coeffs`, the USE filter coefficients they load: `{"load": false}`, or `load` true with `mode` (`CR_USE_COEFFS_MODE`) and `words`, the nine coefficient words (E078) |
| `readback.failed` | null, or the failure text |
| `readback.o0` | the uniform `o0`, or null |
| `readback.mixed` | `[[value, count], ...]` when the pixels differ |
| `readback.scratch` | `{"0x004": "0x..."}`: the dwords that changed, the rest keep the fill |
| `readback.pixels` | every pixel's `o0` in raster order, or null |
| `provenance` | `probe`, `case`, `table`, `template`, `template_sha256`, `inputs`, `params`, |
| | `options` (the `sgxfive-test probe` flags), `question` |

Rules: integers are hex strings so no reader loses bits; a vector never carries firmware or
closed-library bytes; an unknown `version` is rejected (`vectors.py check` validates a file).
`orphans` lists readback labels whose probe or case is no longer in the tables, so nothing is
silently lost. A probe on the triangle host (`--tri` in `provenance.options`) reads back what
the scene drew, which is not the shader's output alone: a simulator test does not compare it.

**Vertex tasks** (`init.task = "vertex"`, phase 11.33, `vectors/nokernel/usse/globals-vertex/`): the
program runs once per vertex of a triangle job's draw, as `Machine::vertex` (the vertex's number,
the vertices a task holds, the vertices of the draw). `init.instances` is the draw's vertex count,
`init.per` the vertices a task holds, `init.outputs` the output registers compared (`o6`...),
`init.skip` the vertices the readback does not decode, and `readback.vertices` one row of values a
vertex, in `init.outputs` order. `run.raw` is the list of the dumps the rows were read from
(`usse/globals-vertex-eot/dumps/<script>/<job>.param.bin.gz`) with `run.raw_sha256` the list of
their digests; `tools/usse-asm/make_vertex_vectors.py` writes them, and the replay test
(`tests/vertex_vectors.rs`) skips, saying so, without them. The generic replay leaves them out (no
`readback.o0`).

**The job.** A fill runs in a transfer job whose command the probe may poke (`--poke
xfer:N=V`), per probe and per case (`case_set`); `firh` reads the filter coefficients the job
loads. Vectors converted before the converter carried `init.job` (all of `vectors/usse/` and
`vectors/followup/usse/`) have it in a sidecar, `vectors/jobs/<the same path>.job.json`
(`vectors.py jobs`, from the pokes each run printed): `{"format": "sgx545-vector-jobs",
"version": 1, "run": {...}, "jobs": {"<id>": <init.job>}}`. The simulator's loader
(`vectors::load`) gives each vector its sidecar job where it has none. Before 11.7 the
`provenance.options` of a probe with `case_set` named the probe's pokes only, not the case's;
the job (and `options` in files converted since) are the case's own.

**Recorded and rebuilt programs.** A run that saved its assembled cases converts as
`recorded`: the words are the bytes the hardware ran. Without them the converter assembles the
case again from the current table (`rebuilt`), which is wrong when the table changed after the
run; a mismatch on a rebuilt vector is first checked against the table's history. All the
vectors in the data repository are recorded.

## 4. What a simulator test does

Load `program.words` at `entry`, set up one instance per `init` (temporaries, `pa0`, the
scratch fill), run to the end, and compare `o0` and the scratch dwords with `readback`, for
every instance (as the fill's 2 x 2 quads) when `pixels` is given. A PDS vector runs its
program as the fill's secondary, then the shader in `init.use` with the attributes the
secondary wrote, and compares the scratch. Registers the program reads before writing them
are undefined: the simulator stops on such a read as unsupported rather than guess. A vector
whose run the simulator cannot reproduce (instances that share a dword they store, a loop
past the step limit, a job that ran after a faulted one) is on its skip list with the reason
(`crates/sgx-sim/src/vectors.rs`, `SKIP`). A job that hung is not replayed, but `--example
replay` says whether the simulator stops on a phas request that hangs (E519). The test reports
pass, unsupported and mismatch counts; a mismatch fails it. `doc/isa/sim-coverage.json` records,
per form, which probes have a passing vector
(`RESGX545_WRITE_COVERAGE=1 cargo test --release -p sgx-sim` writes it).

## 5. Unit vectors

The pipeline simulator (`crates/sgx-pipe`, phase 12) holds each fixed-function unit to the
hardware on its own. A unit vector is a vector of the same container (`"format":
"sgx545-vectors"`, version 1, section 3) whose `init.task` names a unit kind and whose result is
`expect` (not `readback`). It lives in the data repository under `unit-vectors/<unit>/<feature>/
<probe>.vec.json`, outside `vectors/`: the instruction replay walks `vectors/` and would list
these as excluded, which would change its output (`sgx_sim::vectors::probe_files`). The
directory is the constant `sgx_pipe::data::UNIT_DIR`, so it is one line to move; `$RESGX545_UNIT_
VECTORS` replays a set that is not landed yet.

| kind | unit | inputs (`init`) | result (`expect`) | state |
|---|---|---|---|---|
| `zls-store` | zls | size, G (ZLSCTL 11:3), two ramp dumps | counts | built |
| `te-region` | ta | size, the primitives' pixel vertices | tiles listed, counts | built |
| `ta-object` | ta | N, the size word, the format word | stored, masks, outcome | built |
| `isp-tile` | isp | MSAA mode, CR_TE_AA, two position dumps | counts | built |
| `zls-format` | zls | size, control, stencil, two depth dumps or ramps | dwords stored | built (12.4) |
| `zls-load` | zls | size, control, test, depth, load patterns | depth and stencil stored, drawn | built (12.4) |
| `zls-ctl` | zls | a control word, optionally the E411 scratch arrangement | fields, pages | built (12.4) |
| `pbe-emit` | pbe | sideband, reg 0400, colours | value stored each | built |
| `vdm-stream` | vdm | the stream words | tasks, state, hang or cull | stub |
| `bif-walk` | bif | directories, lists, banks, an access | address or fault fields | stub |

A stub kind replays as `unsupported` naming the unit's open questions (`<unit>::OPEN`); a kind
the crate does not know is an error, never a pass.

**`expect`.** One of:

- counts: `matched` (items the rule must reproduce: dwords, (primitive, tile) pairs, tiles,
  objects), `refused` (`{"Q107": n}`: items the rule must refuse, by open question) and
  kind-specific keys (`stored`, `back_ok`, `listed`, `tiles`, `iterated`, `masks`). The
  model counts its own items; every item the model gets wrong is a mismatch.
- `"outcome": "hang"` or `"fault"` (with `addr` where the record has it): the model must predict
  it, from a record, for that input. A model that computes a result where the hardware hung, or
  predicts a hang that did not happen, is a mismatch.
- `"refuse": ["Q165", ...]` beside either: the input is one a question keeps open, and the model
  must refuse it naming exactly those questions (a subset of them is a refusal the vector did not
  expect: `unsupported`).
- `"outcome": "either"` with `"either": [<expect>, <expect>]`: the hardware's result is not
  repeatable (D5: Q163 hung twice in one script and completed in another; Q026; E536's moving
  predicates). The vector lists the results measured; the model passes if it gives one of them
  (`either`, counted apart), and the result is never averaged. Each alternative is any form above.

**`provenance`.** `records`, `questions`, `table` and `case` as in section 3, `options`,
`rule_status` (the rule's status, see below), and `rebuilt` (false for a unit vector made from
a dump).

**Verdicts.** A replay gives one of: `matched`, `either`, `predicted hang`, `predicted fault`,
`near` (equal within a recorded bound), `fitted`, `refused` (as the vector expects),
`unsupported`, `mismatch`. The gate is zero mismatches (D5); there is no percentage gate.
Refusals are counted by question and predicted hangs and faults count as matches, as the
instruction replay counts the 42 of 44 hung `phas` jobs it predicts.

**Fitted rules (D6).** A rule is `fitted` only where its record states the fit, and its status is
set in one place, `sgx_pipe::rules`. A result by a fitted rule is `fitted` and is never reported
`matched`, and neither is any result built on it: `Verdict::combine` of a matched and a fitted
result is fitted, and a scene whose model used a fitted rule is fitted though every pixel is
exact (`SceneResult.fitted`). A fitted result that differs from the hardware is a mismatch. The
four rules of 12.0 are all marked fitted, because their records state a post hoc fit: E465
(fitted on the 1024 x 768 runs and the small targets), E503 (read post hoc from the 64 x 64
runs), E542 (H70-T1, fitted post hoc to E180's 472 regions), E541 (H70-F2, written from the
first run's 42 held-out jobs). Each was then checked on data it was not fitted to, which the
counts below show; flipping a rule to measured is a record decision, not a code one.

**The four built** (`tools/usse-asm/unit_vectors.py`: 18 + 35 + 59 + 48 = 160 vectors). The
expected values are what the datasets' own recompute output and dumps say, never
what the model computes.

- `zls-store` (E465, E489): 18 vectors, one per case of `zls/store-layout-dumps`: the x-ramp
  and y-ramp depth dumps (digest of the gz) and the counts of its `recompute.txt`: 3415552 dwords
  stored, 3279132 at the rule's address (3225000 for pixels of the target, 54132 for pixels past
  it inside E831's band), 7780 background depth (1124 at pixels past the band, E831; 6656 whole
  tiles of the two overflowed 4096 x 4096 jobs, Q107), 128640 zero (the same jobs, Q107), 0
  elsewhere, counted by a classification written in `unit_vectors.py` from the dumps; the slot
  sets equal the rule's and, where tiles do not overlap, 1098340 pixels walk to their address.
- `te-region` (E542): 35 jobs (27 `ta-tri-boundary`, 8 `ta-tri-corner`), 14656 (primitive, tile)
  pairs. The primitives' pixel vertices are the recompute's geometry (the NDC constants and the
  c / 16 pixel shift of copy c), an assumption the record states and not read from the packed
  vertices; `expect.listed` is the tiles of the first control stream of each region (`"any"`
  for the forms 0x80, 0x90 and 0x98 that name no primitive of the object).
- `ta-object` (E541): 59 jobs of `ta/object-format` (47) and its second run (12): 56 completed
  with the stored dwords, the format word's bits 31:16 and 15:8 and the four masks; 3 did not
  (N = 2 faulted, N = 3 and 8 hung): the model predicts these three inputs as recorded and
  nothing else about the `alt` pattern (the same settings completed at N = 4, 5, 6, 9 and 11:
  Q165).
- `isp-tile` (E503): 48 runs of `isp/msaa-ident`: the two position dumps and the counts of
  `an_ident_rule.txt`: 786 tiles, all equal to the window rule, 773 decodable in all 512 pixels
  (matched) and 13 with background pixels (refused, Q141).

**The fifth, built in 12.1** (`unit_vectors.py`, `pbe_emit`): `pbe-emit` (E031, E268), 74 vectors.
`init` is `sideband` (the emit's, pack mode in bits 5:0), `reg0400` (the word that loads
CR_REG_0400, default 0x80) and `colours` (the shader's o0 values), `expect.stored` the value the
hardware stored for each (a 16-bit pixel as its 16 bits). 64 vectors are the pack modes of
`pbe/pack-modes`, with the background 0xff203040 and the shader colour 0x80ff8040 of the 64 x 64
triangle: modes 0 to 3 (ARGB8888, ABGR8888, BGRA8888, RGB565) store the values the dumps hold
(matched), and the other 60 refuse by question (`Q012` for modes 22 and 34, `Q044` for the rest;
the vector keeps the recorded `mixed` counts). Ten more are mode 0 over the ten colours of
`pbe/pack-colours` (the colour stored unchanged). Measured rules: no vector is fitted.

**The sixth to eighth, built in 12.4** (`tools/usse-asm/zls_vectors.py`, offline, no new run; 88
vectors in `unit-vectors/zls-store-format/`, `unit-vectors/zls-load/` and `unit-vectors/zls-ctl/`,
directories of their own so that the digest of the 12.0 dataset, which holds `unit-vectors/zls/`,
does not change; dataset `datasets/unit-vectors-12-4.toml`). The expectations are the records'
own numbers (the dump counts of E490, the lines of E467's output, the per-page counts of the
control-bit runs, the bit tables of E337 and E411), made by the script; a field of a flipped
control word comes from the bit arithmetic of the records' reading, so it is a reading and not a
measurement. A key of `expect` that the kind does not read is a mismatch (a misspelled key would
otherwise compare nothing and pass). A vector that matched but compared no item is counted
`empty`, not matched.

- `zls-format` (E466, E490), 11 vectors, one per buffer of the format runs. `init`: `w`, `h`,
  `ctl` (the control word), `stencil` (a stencil buffer was bound), `x` and `y` (the dumps of the
  x and y ramp: path, sha256, `g`) and `depth_x` and `depth_y` (`{"ramp": size}`, the geometry's
  depth 0.25 + 0.5 (p + 0.5) / (3 size) along the axis, compared within E490's 1e-5, or a dump of
  the sibling float-format run whose float is the depth the tile pass left). `expect.stored`: the
  dwords that left the 0xdeadbeef fill. The float, the 24-bit and the 16-bit stores answer at
  E465's address rule (the 16-bit one at G = 33, two rows to a dword), the integer formats only
  over the ramp's 0.25 to 0.4166 and at 1.0, where the fitted rounding and its fourth candidate
  agree (Q242): 6 fitted, 2 empty (formats 4 and 7 store nothing without a stencil buffer) and 3
  refused (formats 3, 5 and 6, Q120).
- `zls-load` (E467), 30 vectors, one per case. `init`: `w`, `h`, `ctl`, `test` (`never` or
  `less`), `z` and `clear` (the triangle's depth and the clear, as float bits), `depth_fill` and
  `stencil_fill` (the load buffers' pattern, `index` by default). `expect`: `depth` and `stencil`
  (`stored` and the dwords by `classes` of E467's script or by `values`) and `drawn` (pixels the
  triangle drew). The loaded depth loses its sign bit, feeds the depth test, and the stencil is
  copied by dword. 30 fitted (983040 counted dwords: no stored dump exists, so the vectors test
  the counts and not the address rule).
- `zls-ctl` (E337, E411, E467), 47 vectors: the fields of one control word, each compared with
  the reading when the vector gives it (`expect.g`, `fmt`, `load`, `load_depth`, `load_stencil`,
  `store_depth`, `store_stencil`, `negate`, `writes_pixels`), and with `init.arrangement =
  "e411-scratch"` the pages of the 16-page scratch buffer E411 stored (`expect.pages`, a 64 x 64
  target with the stencil buffer). What a field rests on decides the outcome (D6): the pitch
  (E465), the format (E466), a load by bit 1 alone ([infer], E411 part B saw no effect) and every
  stored page make the vector fitted, and one that compares only the store enables, the negation,
  the loads by bits 13 and 14 and whether the image is written stays matched. 15 matched, 23
  fitted, 9 refused (bits 5 to 11, which faulted the job, and bit 25: Q242; bit 26: Q120). Bit 0 is
  the colour image off and stores the control's pages, modelled for 0x0017100d only (Q071).

## 6. Scene vectors

A scene vector is a whole job as the hardware ran it, for the pipeline simulator's `Edm`
(`sgx_pipe::edm`). `vectors/scenes` of the plan is `scene-vectors/<unit>/<feature>/<probe>.
scene.json` here, for the reason of section 5 (`sgx_pipe::data::SCENE_DIR`).

### 6.1 Format

```
{ "format": "sgx545-scene-vectors", "version": 1, "run": {...}, "scenes": [ scene, ... ] }
scene = { "id", "kind": "render" | "transfer",
  "target": { "w", "h", "format", "base" },
  "regs":   { "0x0420": "0x...", ... },     # what the kick writes, byte offsets
  "regs_log": [["0x0420", "0x..."], ...],   # optional: the writes in order, where order matters
  "memory": [ { "base", "dwords": [...] | "file", "sha256", "source": "recorded" | "rebuilt" } ],
  "vm":     { "lists", "banks", "tables" }, # optional; flat when absent, until 12.5
  "expect": { "image", "buffers", "regs", "counters", "outcome", "refuse", "either" },
  "provenance": { "probe", "case", "table", "options", "raw", "raw_sha256", "records",
                  "questions", "rebuilt" } }
```

A file may also be compact (what `tools/usse-asm/transfer_scenes.py` writes for a sweep of one
job): `"bases": [{"kind": "fill" | "copy", "target", "xfer", "layout", "memory"}]` and per scene
`{"id", "base", "delta", "expect", "provenance"}`; `delta` is `{"xfer": {"index": value},
"memory": [{"base", "at": {"index": value}}]}`, the words the pokes changed, and `Scene::load_file`
expands it (a segment's trailing zero dwords are not stored; a poked index past them extends
with zeros). A transfer scene adds `xfer` (the command's words from the register block, in
command order: word i is at command offset 4 i), `layout` (`pds_page`, `use_page`, `bg`: where
the builder put the programs and the background object) and the target's `stride` (bytes) and
`pages` (those the target's buffer holds; the harness fills them with 0xdeadbeef before the job).

A `file` is relative to the data repository and checked against its `sha256`. A segment with
neither `dwords` nor `file` is an error. `source` is `recorded` when the run itself captured the
words and `rebuilt` otherwise (6.3).

### 6.2 `expect`

- `image`: `{"pixels": [...]}` (every pixel, raster order), `{"mixed": [[value, count], ...]}`,
  `{"o0": value}` (every pixel equal) or `{"hash": "0x..."}` (FNV-1a 64 over the little-endian
  bytes of the target's pixels, the `hash` the sweeps print), alone or together, each checked;
  `"near": n` allows n on each 8-bit channel and a result that needed it is `near`. `outside`
  is the number of dwords of the target's buffer outside its rectangle that the job changed.
- `buffers`: `{name: {"sparse": {"0xaddr": "0xvalue"}} | {"dwords": [...]}}` for the parameter
  buffer (`param`), TA data (`tadata`), depth and stencil, compared by byte address.
- `regs`: the registers the host reads back (status, DPM); `counters`: the visibility counters.
- `outcome`, `refuse` and `either` as in section 5, at the scene level; an alternative of an
  `either` may carry an image of its own. The comparer is `sgx_pipe::scene::compare`; it shares
  the verdicts of section 5, so a scene resting on a fitted rule is `fitted`.

### 6.3 Where the words come from (D4)

1. **Rebuilt offline.** `sgxfive-test --emit-scene FILE` (a new option, no kernel change, no
   laptop) runs the builder that made a recorded scene against the mock backend and writes the
   words a real run would have submitted: the render details, TA command, state blocks, VDM
   stream, programs and PDS words from the run's `bins/`, the buffers. The segments are tagged
   `rebuilt`: a table may have changed after its run. Where the run kept a render dump (the 65
   triangle-host vectors with `--dump-render`) the rebuilt parameter-buffer words are compared with
   the dump and a scene that differs is excluded and listed. The others are rebuilt unchecked and
   say so in `provenance.rebuilt`.
2. **Recorded in every new run.** Every new run records the job's inputs directly, so no new data
   needs a rebuild. Format to build the tool option against (`--record-scene DIR`, work to follow):
   - one `<case>.scene.json` per submitted job, written at submission before the kick, its
     `expect` filled in when the job completes, hangs or faults;
   - `regs`: the register words the kick writes; `regs_log` the host's writes in order;
   - `memory`: one segment for every buffer object of the context (the builder's own allocation
     list, so nothing is left out by choice): the programs, PDS words, state blocks, VDM stream,
     parameter buffer descriptor, textures, the background object, ZLS and target buffers, each
     with `"source": "recorded"`, as `dwords` up to 4 KiB and a `file` of raw little-endian
     dwords with its sha256 beyond;
   - `vm`: the page directory and tables the kernel built for the context, as segments of their
     own, when 12.5 needs them;
   - `expect`: the readback image, the dumps of the parameter buffer and TA data
     (`buffers.param`, `buffers.tadata`), the status registers, and the failure text as
     `outcome` (`hang`, `fault` with the address from the log);
   - a run repeated n times with different results writes one scene whose `expect` is `either`
     of the distinct results (D5), with the count of each in `provenance.runs`.
   The tool's allocation list is the completeness check: a scene whose `memory` does not cover
   every segment the kick's structures point to is refused by the loader (`Mem` refuses an access
   to an unmapped address, it does not return zero).

### 6.4 What a replay does

`sgx_pipe::job::run` loads `memory` into the device address space (`mem`, flat until 12.5), applies
`regs` through the register file (`regs`: an unlisted register or a value wider than its measured
width refuses), and runs the units in the order of the data dependencies. A render runs the vertex
side and the TA (6.6), then the ISP, the pixel programs and the PBE (6.7), and gives the parameter
buffer, the TA data and an image. A transfer (fill or copy) runs through `sgx_pipe::xfer` (12.1):
the 17 register words, the render box in 32 x 16 tiles, the pixel-event PDS program of each tile
through `sgx-sim` with ir1 = 6 on the last tile, the end-of-tile task and its emit to the PBE (pack
modes 0 to 3), the pixel shader per pixel of every tile of the box and a copy's texel through
`tex::sample`. The end-of-tile task stores its tile at the place its U1 tile fields name in
half-tile units (E876, held out in E884), each axis by its own field also when both move at once
(E909, held out at 128 x 64), so a poke of the pixel-event program's U1 word or tile masks moves
tiles, and a place past the target is cut by the PBE's rectangle. A command word or a task no
record explains refuses (`Q206`, the words of a transfer with no record and a U1 bit outside the
tile fields among them), a PDS program or input no record
measured (a program that is not a template the records ran included) under `Q207`; `Q011` a copy's
tag; `Q180` the iterator word; `Q066` the background object; `Q205` a copy's iterated coordinates;
`Q078` the sampler words; `Q076` and `Q003` an access outside the scene's memory, and `Q003` also a
job whose completion the words leave unknown. A refusal depends on the scene's words only, never on
the recorded result. The scene vector lists the questions its poked words are open under in
`expect.refuse`. The one fitted rule is the place of a moved tile (`rules::XFER_U1_PLACE`: E876
states the fit, E884 held it out), so a scene whose tile moved is `fitted`, every other result
`matched` (1601 fitted in the replay, the 1532 moved fills of the two end-of-tile sweeps among
them); the PBE predicts the hangs its records state (E266 and E267) and none of the replay's scenes
reaches them, so no hang or fault is predicted in a replay. The PDS inputs `alu_specials_in_movs`,
`ifs` and `ir2` are assumptions confined to the template programs. A model that returns a result
must say which fitted rules it used.

### 6.5 Not yet (scope of the format)

- `expect.image` and `expect.buffers` have inline forms only; a `file` plus `sha256` form comes
  with the first scene whose image does not fit inline (12.4 or 12.7).
- A scene is one job. Multi-kick jobs (TA then 3D, partial renders, parameter-buffer overflow:
  Q038, Q107) need an ordered list of kicks and the memory between them; out of scope until 12.7.
- `vm` is refused by the loader (a scene with one would run as flat memory); its shape (lists,
  banks, tables) is specified in 12.5. Unknown keys of a scene or its target are errors.
- Memory segments carry no role (program, pds, state, vdm, pb, tadata, zls, target, texture) yet;
  the completeness check of 6.3 needs them, and `--record-scene` names them.
- A `mixed` image compares value counts only (a permuted image passes): weaker evidence than
  `pixels` or a hash.
- An `either` lists two or more alternatives that each check something, and a scene or vector whose
  `expect` compares nothing is a mismatch, not a match.

### 6.6 Render scenes: the vertex side and the TA (12.2)

A `render` scene built by `tools/usse-asm/ta_scenes.py` is one `--tri` probe of a `ta` or `vdm`
table: `sgxfive-test --mock probe --tri ... --emit-scene` writes the render command's words
(`cmd`, `drm_sgxfive_render_cmd` order), `vertices`, the `layout` (`pdsv`, `usev`, `pdsp`, `usep`,
`gen`, `fb`, the three code and PDS bases) and the five program and stream pages, each segment
with its `role`. The words are rebuilt; the probe's pixel program is a placeholder, which the TA
does not read, so a job that replaced the vertex program or a PDS program (`--slot`) is listed in
`run.excluded`, not built. The rebuilt state block's three pixel PDS words must equal the dump's
first three object dwords (E306); a case that differs is excluded and listed, and a dump with no
object (a culled job) has nothing to check and says `header_checked: false`.

`expect.buffers.param` and `.tadata` hold the non-zero dwords of the saved dump inside a `window`
(`param` 0x1000 to 0x6000 by slot address, the TA data's headers 0x4000 to 0x5000 by dump offset),
and the comparer takes a window to mean the whole range: a dword the model writes that the
hardware left 0 is a mismatch, and only dwords non-zero on either side count as items. What the
dump holds outside the windows (the DPM state, `provenance.outside_window_nonzero`) is not modelled
before 12.7.

`sgx_pipe::render::run` parses the VDM stream (`vdm`), runs each state block and each vertex of a
task through its PDS program and USSE task on `sgx-sim` unchanged (`vtx`: the `doutd` copy is the
pipe's, the task runs until it hands its outputs to the vertex cache), puts the clip positions
through the viewport (`mte`) and writes the object, the region headers and the streams (`ta`). The
TA's rules (E541, E542, E651, E652) and the 1/w replacement (E197) are fitted, so every result is
`fitted`, never `matched`. Refused by question: stream words and state words nobody flipped (Q047,
Q042, Q094, Q112; the history-dependent values Q163), lines and points (Q159, Q160, Q161),
other output selects and state blocks (Q069, Q162), TE words other than the library's tiling (Q100,
Q139, Q086, Q142), a triangle the clip removes or cuts or no target region lists (Q230), command
words 10 to 25 that no stage reads (6.7 leaves the ones the pixel side reads to it), the state's
WCLAMP and the end-of-scene word that no record reads or that no dump varied (Q231). A stream the
parser refuses names the stream's shape (Q112) with its words, so a two-object stream lists what
blocks it.

### 6.7 Render scenes with an image: the ISP and the first triangle (12.3)

`sgx_pipe::render::run` goes on from the TA's output to `sgx_pipe::pixel::image`: for each 32 x 16
tile the region header and the control stream the TA wrote are read back (`objects`), the ISP
resolves the tile's pixels (`isp::resolve_tile`: coverage, the depth test, the object's ISP words),
the pixel programs of the winning object and of the background object run per pixel on `sgx-sim`
(the PDS primary and secondary programs, then the USSE task), the pixel-event program starts the
end-of-tile task of each tile and the PBE stores it (`pbe::store_tile`). The result is `image` (the
target as the host reads it), `outside` (dwords past the target that changed) and, where `regs`
holds a `CR_ISP_ZLSCTL` (`0x0480`) of E465's depth store and the store base (`0x0488`), `depth`.
The command words 10 to 25 are the pixel side's (`pixel::READS`): the vertex side's refusal of
words no stage reads (6.6, Q231) leaves them to it, and the pixel side recognises the library's
values, CR_ISP_CTL bits 5:0 (the gate), the background depth and the pixel-event program's place,
and refuses the rest by its own question.

Rules, and what each rests on:

- Coverage (E606, E607): the vertices on the 1/256 pixel grid, the pixel centre tested exactly in
  integers, a centre on an edge belongs to the triangle iff the edge is a left or a top edge, a
  triangle with no area draws nothing. A fit: every image that rests on it is `fitted` (D6), never
  `matched`, and names E606, E607 (the grid) and, where the depth is stored, E465. A render only
  inside what E606 ran: the targets 64 x 64, 128 x 128 and 256 x 128 (Q262 on E680's ten, where
  the depth missed E606's tolerance on 1- and 2-pixel triangles, E912; Q240 for every other),
  vertices from -9% to +124% of the target (Q199), 1/w = 1 and a single sample (Q202), `x >= 0`
  for a coordinate with a fraction below the grid (Q199). The coverage alone (`isp::coverage_image`)
  is admitted on E680's ten targets and on E913's ten (the family around E606's, two below one
  tile, 4096 x 16 and two odd heights), each kept image of R7-geo's zd and zf stages replayed pixel
  for pixel (`tests/isp_closing_r7_geo.rs`).
- Depth: the plane through the vertices at the pixel centre, exact. No bit-exact model exists, so
  a depth the model stores is compared with E606's tolerance (3 units of 2^-23 where the plane's
  gradient |dz/dx| + |dz/dy| is below 0.03; the data do not pin the 3 from below):
  `scene::depth_verdict` says `Near`. A compare against a plane of gradient 0.03 or more, or
  between two depths closer than the sum of their tolerances (the bound is inclusive), refuses
  (Q200): the hardware's decision is not predictable from the plane. The refusal drops the whole
  image of its scene, coverage included, which skews a replayed sample to shallow planes. A vertex
  depth outside [0, 1] refuses (Q241) unless the compare is always and no depth is written: E287
  saw the depth clamped in clip space (one run, inferred).
- Iterated values (`iter`): the plane through the attribute at the centre, within 4 units where
  the range per root area is below 0.05, for the clip z only (the clip x of the same jobs reached
  23 units: no tolerance, Q200). Not in the scene path: the TA writes position-only objects (12.2).
- ISP words (`isp::decode_words`): depth compare 0, 1, 4, 7 (2, 3, 5, 6 were inferred, Q241), depth
  write (bit 20) and colour write (bit 21), pass types (3 and 7 remove, E065; 1, 2, 4, 5 and 6
  draw a single triangle as opaque only for the library's colour write, the shader E065 ran, and
  several triangles or another shader refuse: Q073, Q032, Q241), the gate of ISP word 1 bits 31:26
  against `CR_ISP_CTL` bits 5:0 only for the pairs E232 and E235 measured (gate 0 at the values 0
  to 8, 16, 32, 63; gate 0 and 63 at 1 and 63; every other pair refuses, Q241). A stencil word
  (Q071), bits 15 to 18, a visibility test and the polygon offset (Q241) and bit 28 (Q202) refuse.
  No replayed vector exercises these decodes (the depth-test and punch-through vectors stop at
  Q094): the unit tests check the model against itself.
- The command's pixel-side words must be the library's (Q202, Q099, Q066, Q231, Q206).
- A pixel program with an `o0` write, a store or an emit that lacks `.skipinv` also runs for the
  helper instances of a partly covered quad and lands in some runs only (E104, E111, E113): it
  refuses where the triangle covers a quad in part (Q052). A branch refuses (E112: Q050).
- The vertex emits (E102): `emitvcbvtx` without `.twopart` hangs the job when `emitmtevtx` has it
  (a predicted hang: the record that defined the rule is the only case) and draws nothing when it
  has not either (refused: what the TA writes then was not dumped, Q230).

`tools/usse-asm/isp_scenes.py` rebuilds the scenes: `first-triangle` (E023, E148, E174: the
library's triangle on 16 sizes with the first render's image hash; three are E606's sizes, the
others refuse Q240), `arith` (a sample of the E606 depth jobs: the vertices of `cases.tsv`, the
image hash and the dump of the stored depth in `provenance.depth`), and `inventory` (every
triangle-host vector of the data repository: its recorded image as the expectation, nothing
declared refused, for a census; the census is a development set, with duplicates). The builder
declares the questions open for an input from the input alone (`open_questions`,
`plane_questions`), never from a result. Examples: `arith_stats` (the unit model against the
recorded images of E606 and E607 pixel for pixel), `inventory_stats` (the census), `scene_image`
(one scene's image and code).

## 7. Vectors of the closing pass (round 4, sim item 4)

`vectors/closing/r3-pixel/` of the data repository holds what R3-pixel's kept jobs
(`render/closing-r3-pixel`, attempt 20261110-160415) give a simulator, made by
`tools/usse-asm/closing_vectors.py` (tests: `test_closing_vectors.py`) and replayed by
`crates/sgx-sim/tests/closing_vectors.rs`. Three kinds, none a prediction of a rule:

- `loops/<stage>.vec.json` (q-f0, q-f1a, q-f1b, q-t: 204 pixel loops, q-v: 73 vertex loops): vectors
  of the layout of section 3 with `init.task` `loop-proof` (a pixel loop) or `vertex` (a vertex
  loop) and `readback.o0` null, so the generic replay leaves them out. A pixel loop proves itself:
  it leaves MARK = 0xC0DE0000 | N in o0 where its counter reached zero (0 for E431's `ba` loop), and
  `readback.proof` says the value and how many of how many pixels read it. `init.host` is `fill`
  (code index 0) or `tri` (a `--tri pixel` slot, code index 0x20, `init.code_index`); the replay
  runs the program as one instance from that index and its o0 must equal the proof. A vertex loop's
  `readback.depth_words` is the stored depth word of each vertex the dump decodes (`pbdump
  first_object`), 0x3f200000 + N, the float32 0.5 + 0.5 z of the z the loop leaves in o2; the replay
  is refused today (the model stops on the program's `phas ... vcull`, E121), the files are kept.
- `direct-reads/p-c3.vec.json` (E808's 8 direct reads of g23, g24 and g25, one compact file):
  `init.task` `direct-read`, the target's image as printed (`readback.image`, raster order) and
  `readback.undecoded`, the raster indices the premise control (the pixel's own position written by
  `c-<shape>-pa-x` and `-y`) does not confirm; a replay runs the aligned 2 x 2 quads and compares
  the written pixels outside that list (48038 of them, no mismatch).
- `timings/<stage>.timing.json` (format `sgx545-timings`, 285 rows): per job the burst, the TA
  clocks' run, bits 6 and 7 of CR_EVENT_STATUS2 after the job and when they showed. They are
  measurements the simulator has no clock for, the input of the STATUS2 latch rule of `events.rs`.

## 8. Tables of the closing pass (format `sgx545-tables`)

What the closing pass measured and no simulator replays is kept as tables beside section 7's
vectors, under `vectors/closing/` of the data repository, made by `tools/usse-asm/closing_tables.py`
(tests: `test_closing_tables.py`) from the kept files of each published session, one table a stage
and one row a job (E833):

```
closing_tables.py KIND --session DIR --out OUT STAGE...
```

A file is `{format: "sgx545-tables", version: 1, run, kind, note, replay, rows, skipped}`. `run`
names the session, the stage and the tool; `replay` is `{status, reason}`, and the status is
`refused` in every table but the `zls` ones, with the reason the simulator does not model what the
rows hold, so a table is never counted as a pass; the `zls` tables are `replayed`, with the `test`
that replays them (below); `rows` are what the job's kept files say, under the keys of the
session's own readers (its frozen scorer, or the reader named in the tool), with the raw file and,
for a dump, its sha256; `skipped` lists the jobs a session scored only as gates or void, with the
reason. `crates/sgx-sim/tests/closing_tables.rs` checks that every table has the format, rows, and
either a refused status with a reason or a replayed one naming its test.

| dataset | path under `vectors/closing/` | kind | stages, jobs | records |
|---|---|---|---|---|
| `vectors-closing-r3-geo-depth` | `r3-geo/depth-words/` | `depth` | g-da to g-dd, 57 | E795-E798 |
| `vectors-closing-r3-geo-dword36` | `r3-geo/dword36.table.json` | `dword36` | g-d36, g-c4 to g-c7, 60 | E803 |
| `vectors-closing-r3-geo-counts` | `r3-geo/counts/` | `counts` | g-c4 to g-c7, g-d36, 60 | E803 |
| `vectors-closing-r3-geo-c-counts` | `r3-geo-c/counts/` | `counts` | g-qf 22, g-qh 8 (+ 6 void) | E832 |
| `vectors-closing-r3-geo-c-zls` | `r3-geo-c/zls-extents/` | `zls` | g-z, 15 | E831 |
| `vectors-closing-r6-misc-zls` | `r6-misc/zls-extents/` | `zls` | q287, 20 | E885 |
| `vectors-closing-r7-rp-zls` | `r7-rp/zls-extents/` | `zls` | q287, 25 | E903 |
| `vectors-closing-r3k-pixel-pb-pages` | `r3k-pixel/pb-pages/` | `pbpages` | k-f4, 10 dumps | E824 |

- `depth`: per job the stored depth word and 1/w of each vertex of the first object of the render
  dump and the vertex count; refused, no frozen formula of the depth word held (E795, E796).
- `dword36`: per job the count before the last abort (`CR_DPM_GLOBAL_PAGE_STATUS` low half) and
  dword 36 of the TA/3D control block, with whether they agree (60 of 60, E803's rule); refused,
  the DPM's page counts and the control block are not modelled.
- `counts`: per job P, the first threshold the job read (`0x0624`), the partial renders (the rising
  edges of `0x0658` bit 0), the peak of each TA run, the counts before each abort and dwords 36 to
  38; refused, the abort and partial-render sequence is not modelled (the count is Q211, E832).
- `zls`: per job the stored (not 1.0f) dwords of the depth store's tile area, their extent and the
  tool's count of target pixels that differ. Replayed by `crates/sgx-pipe/tests/zls_table.rs`
  (`the_band_replays_every_modelled_row_of_the_zls_tables`): per job, the pixels of the tile area
  that the job's triangle (the full-screen one, or the `--tri-v` of `cases.tsv` in the session's
  stage directory: `render/closing-r3-geo-c/out/g-z/`,
  `render/closing-r6-misc/out/20261112-152213/q287/`, `render/closing-r7-rp/out/20261112-205431/
  q287/`) covers inside `zls::in_band` (rule A: E831 at even sizes, E885 at odd heights, E903 at
  odd widths; the band's W twice the viewport's x scale where a job pokes it, E903's twins, else
  the target's) are the stored ones, and their count and extent equal the row's: 15 of 15, 20 of 20
  and 25 of 25 match, none refused. A table's `replay` says `replayed` only because no modelled row
  mismatched. The test skips without the data. sgx-sim does not model the band.
- `pbpages`: per dump the non-zero 4 KiB pages of the parameter buffer, their runs, the TA data
  size and the tile count; refused, the page writes are not modelled (the page model the table
  agrees with in 8 of 8 dumps was fitted to them, E833).
