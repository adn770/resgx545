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
p0 and `pclink` values at the next entry (Q155), the stop of E537, TRC above 31 and a write past the
allocation (the T = 8 to 24 runs of E540 also read the register past the allocation, which the
simulator stops on, so only T = 31 is a vector).

The two runs of E535 (a write to `r123` with a marker of its own per job, client fills) are
converted by `tools/usse-asm/convert_extra.py` into `vectors/nokernel/usse/q147-a/` and `q147-b/`
(18 vectors each, `datasets/vectors-usse-q147.toml`): 14 replay exactly (the controls and the
request of 448), 12 are left out (their pixels are a mixture, no single o0) and 10 stop on `r123`
past the allocation, because the simulator takes a request of 260 to 376 to allocate its value
modulo 256 (Q144).

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
