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
```

One directory per probe table (`probes/<unit>/<feature>.toml`), one file per run of one probe
of it (`<unit>/<feature>/<probe>/raw.txt`, and the same under `followup/` for the follow-up
round; `knowledge/` holds the runs of the 11.x sub-phases to 11.7, `semantics/` those of 11.13
(a directory of its own, so that the earlier manifest's digest stays), `jobs/` the jobs of the
files converted before vectors carried them). Every table whose probes carry a program has one; a
probe run that read back no case of its table gives no file.
Each unit's vectors are a dataset (`datasets/vectors-<unit>.toml`,
`vectors-<unit>-followup.toml`) that names the converter as its recipe.

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
(`crates/sgx-sim/src/vectors.rs`, `SKIP`). The test reports pass, unsupported and mismatch
counts; a mismatch fails it. `doc/isa/sim-coverage.json` records, per form, which probes have a
passing vector (`RESGX545_WRITE_COVERAGE=1 cargo test --release -p sgx-sim` writes it).
