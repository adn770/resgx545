# Sweep probes

Exhaustive, unguided sweeps of the words our jobs give the SGX545: every bit of every word of
a space, plus all-zero and all-ones, each as its own job on the laptop, the results recorded
raw and classified mechanically. A table says which space of which job to sweep, never what a
word is expected to do; names for the words follow later, from the results, through the
glossary review.

| file | what |
|------|------|
| `sweep.py` | the runner: tables, cases, runs (mock, local or over ssh), raw.txt, report |
| `kernel_masks.toml` | what the kernel does with each word userspace submits |
| `regtimeline.c` | samples registers read-only through `/dev/mem` around one command |
| `loadsummary.py` | a script table's runs under register values: job times, held runs (11.15) |
| `casesummary.py` | a script table's `one()` cases: job, wrong pixels, hash, time (11.15) |
| `counters.py` | the visibility counters around every case, and the scan of saved runs |
| `gate.sh` | the health check between tables |
| `test_sweep.py`, `test_sweep_tables.py`, `test_counters.py` | the tests |
| `test_loadsummary.py`, `test_casesummary.py` | the tests of the two summaries (11.15) |

The sweeps themselves are tables under `probes/<unit>/` (see "Tables"); `tools/campaign` runs
them in order, one dataset each, and `probes/transfer/gen_kernel_words.py` writes the
kernel-word tables.

### Job times

A case's report line set carries the jobs' times: `sgxfive-test` prints `job time: N us` for a
fill, a copy and a probe (and the triangle's `tri WxH #1: N us`), and the report gives the
baseline's time, the spread of the cases' and the cases over twice or under half the median.

### Pixels against the baseline

A run's report counts a changed case's pixels against the CPU reference, which tolerates what
the reference does not model. `sweep.py rerun DIR` runs the baseline and every changed case of
the run in DIR again with `--pixels` (same target, mock or local options as `run`), into
DIR/pixels, and its report gives each case's pixels against the baseline's: how many differ,
the box holding them and the most frequent new values.



## Method

- A table names a job of `sgxfive-test` (a 64x32 fill, a 64x32 copy, a 64x64 triangle) and a
  space of words; every word gets a flip of each bit (relative to the job's own value) and the
  values 0 and ~0, each as its own job after an unpoked baseline. Value sweeps flip every value
  of a field the bit sweeps found.
- Classes are mechanical: unchanged, changed (pixels differing from the CPU reference or the
  baseline), fault, hang, overflow (parameter buffer), rejected (by our kernel, never reached
  the GPU).
- Spaces: `xfer` (the transfer command userspace submits), `cmd` (the render command), `vdm`,
  `eos`, `blk` (the triangle's VDM stream, end of scene, state block), `pds:SLOT` (data words of
  a PDS program), `tex`, `bg`; the kernel spaces `tq` (the transfer command the kernel builds),
  `ta`, `rd` (the render command and its render details), armed through the kernel fork's
  debugfs; `kreg` (registers the firmware never touches, written around a job).
- The words the kernel builds from the user's are swept in two tables: the data words, every
  bit, and the words that hold GPU addresses, counts of address arrays, sync objects or
  register-address pairs, page-offset bits only (bits 0-11), so an address stays in its page.
  The address sweeps are open: they run last, behind the data sweeps.

## How a case runs

A case is one `sgxfive-test` process (`userspace/libsgxfive`) with one `--poke`, so every
case gets a fresh file, VM and context: the kernel's recovery of a fault or hang loses only
that context, and a file banned after its faults is gone with the process. The poke is
applied to the built job right before it is submitted: `SPACE:N^=V` flips bits relative to
what the job would have written, so a table does not encode the baseline values, and
`SPACE:N=V` sets the word. The spaces and their sizes are the libsgxfive README's ("Job
options"); a range of `"all"` takes the size from the tool itself (`sgxfive-test --mock HOST
--poke SPACE:0xffffffff=0` reports it), so the tables follow the jobs we build.

The cases of a table: the baseline (no poke) first, then for each word of each range, a flip
of each of `bits` (`^=1<<b`) and each of `values` (`=0`, `=0xffffffff`), all `repeat`
times. With `pb_pages`, the whole list runs once per parameter-buffer size (debugfs
`render_pb_pages` on the laptop, `--mock-pb-pages` on the mock), and the runner sets it back
to 0x422 at the end.

## Results

Each case appends to `raw.txt` as it finishes:

```
=== case xfer:3^=0x100
$ ./sgxfive-test fill --poke xfer:3^=0x100
job: ok
target: 64x32 hash 0x...
diff: 0 of 2048 pixels
outside: 0 dwords
--- stderr
--- rc 0 0.180 s
```

A case cut off before its `--- rc` line does not count, so a run resumes from `raw.txt`:
`run` skips the cases already there. A hang-heavy sweep can be split over sessions, or cut
with `--limit N`.

`report.txt` classifies every case against the baseline from the result lines alone:

| class | meaning |
|-------|---------|
| `unchanged` | the job completed; target hash and writes outside it as the baseline's |
| `changed (n pixels[, m outside])` | another target hash; n pixels differ from the reference |
| `outside (m dwords)` | the same target, other writes outside it than the baseline's |
| `fault`, `hang`, `cancelled` | the job failed so; the kernel recovered, the context is lost |
| `overflow` | the scene overflowed the parameter buffer (`-ENOSPC`, context kept) |
| `rejected (error)` | the library or the kernel refused the job; nothing ran |
| `usage` | sgxfive-test refused the command line (exit 2) |
| `error` | anything else: the tool or ssh failed, no job line, a wait that gave up |

The report has a summary line, then one line per word with every case that was not
`unchanged` (repeats that disagree as `unchanged/hang`). The run stops after `--max-errors`
errors in a row (default 5): a GPU the kernel could not recover makes every later case fail
the same way. Job failures (fault, hang, ...) never stop a sweep. A baseline that is not
`unchanged` against itself (a failed job) stops the run before any poke: there is no
reference.

### What the kernel does with each word

`kernel_masks.toml` lists, for every word userspace submits (`xfer:0-41`, the transfer
command; `cmd:0-25`, the render command), what the kernel fork does with it, read from its
code (file:line at the commit the file names): `pass` (copied unchanged), `validate` (a
value that breaks the rule fails the submission with `-EINVAL`, nothing runs), `mask` (only
some bits reach the firmware) or `override` (the kernel writes its own value), and where it
lands in the firmware command the kernel builds (`tq:N`, `ta:N`, `rd:N`, the kernel-poke
spaces below). Today 54 words pass and 14 are validated (`xfer:4, 6, 9, 15, 16, 17`, `cmd:0,
2-5, 9, 15, 18`); none is masked or overridden.

On a word that is not `pass`, the report tags each listed case `[never reached the GPU]`
(rejected, overridden, or a flip only of masked-off bits) or `[reached]`, and ends the line
with `[kernel: ACTION (RULE), lands ..., FILE:LINE; reached the GPU in N of M]`. So an
`all unchanged` validated word is told from one that never got there:

```
xfer:15: ^=0x1 rejected (Invalid argument) [never reached the GPU]; ... [kernel: validate
(equal to the PDS_PIXEL heap base, ...), lands tq:15, sgxfive_cmd.c:111; reached the GPU in 0 of 34]
```

Update the file when the fork's checks change (and its `fork` commit).

### Kernel pokes and registers

The words the kernel builds itself are swept through the kernel fork's root-only debugfs files
(`dri/0/sgx`, `SGX_SWEEP_DEBUGFS`):

| space | what | words | jobs |
|-------|------|-------|------|
| `ta:N` | the TA command of a render | 176 | `tri` |
| `rd:N` | the render details of a render | 123 | `tri` |
| `tq:N` | the transfer command | 306 | `fill`, `copy` |
| `kreg:OFF` | a register the firmware never touches | 5: 0x0810-0x0818, 0x0a78, 0x0abc | any |

The sizes are the kernel's (`sgxfive_kpoke_words`, `sgxfive_kreg_allowed`), not the tool's. A
case of a kernel space runs the host job without a userspace poke, inside a shell script that
`target_cmd` builds (debugfs through `sudo -n`, the tool as the table says):

- `kpoke`: before the job it writes `clear` and the poke (`ta:3^=0x1`), which the kernel applies
  to the next job of its kind (`ta`, `rd`: the next render; `tq`: the next transfer that is not
  a dummy) and drops; after the job it prints `kpoke left: ...` (what is still armed, `none`)
  and clears. Every case of the table clears first, the baseline included, so a poke a cut-off
  case left armed never reaches the next job.
- `kreg`: before the job it prints `kreg: 0x0810=V ...` (every register), sets the poked
  register back to the baseline's value (a case cut off before its restore leaves its poke),
  writes the poke and prints `kreg OFF: was V reads V`; after the job `kreg OFF: after the job
  V`, and writes back what it was.

An arming or a write the kernel refuses (no firmware, a job still running) fails the case with
rc 3, an `error`. On the mock the kernel poke is not applied: the case only checks that it runs.

The report ends a kernel word's line with `[kpoke applied in N of M; carries cmd:0]`: the cases
whose poke the kernel took (a poke still armed after the job never reached the GPU, and its
case says so) and the userspace word that lands on the word (`kernel_masks.toml`), if any; a
register's with `[register: was V; flips that took T, did not N; the job changed it in J of
K]`, the bits a flip changed on read-back, those it did not, and the cases whose job left the
register other than the write did.

## Running

Tables run through the campaign runner (`tools/campaign/campaign.py`), which fences the GPU
between cases, writes each table's data and manifest and records the target's environment.
The sweep runner also runs a table of one sweep by itself:

```sh
make -C userspace/libsgxfive                    # the local sgxfive-test: sizes, mock runs
tools/sweep/sweep.py list                       # sweeps and case counts
tools/sweep/sweep.py cases probes/render/command-words.toml   # a table of one sweep
tools/sweep/sweep.py run --mock probes/render/command-words.toml --out debug/sweeps/x
tools/sweep/sweep.py report debug/sweeps/x
```

`run` copies the table to `DIR/table.toml` (the report needs it), defaults `DIR` to
`debug/sweeps/NAME`, and prints each case's class with `-v`. Without `--mock` or `--local`
the cases go over ssh to `SGX_TARGET_HOST` (with `SGX_TARGET_SSH_OPTS`, or
`kernel/scripts/local.env`), one command per case over a shared connection
(`ControlMaster`). On the laptop the runner expects:

| variable | default | |
|----------|---------|-|
| `SGX_SWEEP_TOOL` | `./sgxfive-test` (or `SGX_PROBE_TOOL`) | the i686 build of `sgxfive-test` |
| `SGX_SWEEP_TIMELINE` | `./regtimeline` | for tables with a `timeline`, and the counters |
| `SGX_SWEEP_COUNTERS` | `1` | `0`: no counters around the cases |
| `SGX_SWEEP_DEBUGFS` | `/sys/kernel/debug/dri/0/sgx` | for `pb_pages` and the kernel spaces |

Tables with `sudo`, `timeline` or `pb_pages` run their commands with `sudo -n`, and those of
the kernel spaces their debugfs writes (passwordless on the laptop). `--local` runs the
local tool without the mock, for running the runner on the laptop itself. Mock runs only
check that every case executes: what the mock does with a poked word means nothing about the
hardware.

A run that stops (errors in a row) resumes with the same command once the laptop is back.
Between tables, `gate.sh` checks the laptop is healthy (a plain fill passes, the kernel log
holds no oops, BUG, lockdep report or call trace).

## Tables

A sweep table is `probes/<unit>/<feature>.toml`. A table of one sweep is named
`<unit>-<feature>` and has the keys below at its top; a table of several has one `[[sweep]]`
per sweep (its own `name`, `host`, options and `[[sweep.range]]`), each named
`<unit>-<feature>-<case>` and run into a directory of its own. A table may also carry
`needs = [...]` (what the target must offer: `render` for the render node, or a file of the
kernel's debugfs directory such as `kpoke`) and `open = [...]` (kept sweeps or probes no
earlier run recorded, run last).

```toml
name = "pds-data-words"           # <unit>-<feature>
about = "the data words of the fill's PDS programs"
host = "fill"                     # fill, copy or tri
options = ["--width", "64"]       # the host command's options (sgxfive-test)
mock_options = []                 # extra global options with --mock
bits = [0, 1, ..., 31]            # default: 0-31
values = ["=0", "=0xffffffff"]    # default; "^=V" flips V
repeat = 1
timeout = 60                      # seconds per case, ssh included
sudo = false                      # the tool as root (sgxfive-test --regs reads /dev/mem)
pb_pages = []                     # run everything once per parameter-buffer size
timeline = { regs = "0x0740", total = 2.0, lead = 0.2 }    # regtimeline around each case

[[range]]
space = "pds:prim"                # cmd, xfer, vdm, eos, blk, pds:SLOT, tex, bg; ta, rd, tq, kreg
indices = "all"                   # or [first, last] (kreg: offsets, the registers between)
```

The tables cover every word of every space of the three jobs (checked by
`test_sweep_tables.py` against the tool's sizes): 32 flips, 0 and ~0 a word, after the
baseline.

| table | job | spaces | cases |
|-------|-----|--------|-------|
| `transfer/command-words` | fill, copy 64x32 | `xfer` 0-41 | 1429 each |
| `render/command-words` | tri 64x64 | `cmd` 0-25 | 885 |
| `vdm/stream-words` | tri 64x64 | `vdm` 0-10, `eos` 0-1, `blk` 0-17 | 1055 |
| `pds/data-words` | tri, fill, copy | `pds:` slots (libsgxfive README) | 1905, 953, 1225 |
| `texture/state-words` | copy 64x32 | `tex` 0-3, `bg` 0-22 | 1123 |
| `isp/background-object` | fill 64x32 | `bg` 0-16 | 579 |
| `dpm/parameter-buffer` | tri 1024x768, 4096x4096 | 10 PB sizes twice, timeline | 20 each |
| `transfer/kernel-words` | fill, copy | `tq` 0-305 (kernel) | 205, 3181 (address) |
| `render/kernel-words` | tri 64x64 | `ta` 0-175, `rd` 0-122 (kernel) | 2313, 2557 (address) |
| `platform/untouched-registers` | tri, fill, copy | `kreg`, 5 registers | 171 each |

The render command userspace submits has 26 dwords, its TA and 3D words together; the rest of
the firmware's command is the kernel's, swept by the kernel-word tables (the kernel spaces
need the kernel fork's `resgx545` branch with the debugfs group, `DRM_GMA500_SGXFIVE_DEBUG`).
The data-word tables of the kernel spaces leave out the words userspace passes through
unchanged, which the command-word tables sweep.

## regtimeline

```
sudo ./regtimeline TOTAL LEAD REGS -- COMMAND...
```

Samples the registers REGS (byte offsets in the bank, `LO-HI` ranges or single offsets,
comma-separated) in a tight loop through `/dev/mem`, read-only, starts COMMAND after LEAD
seconds and samples for TOTAL seconds (and until COMMAND exits; TOTAL 0 samples only while it
runs). It exits with COMMAND's status. After COMMAND's output it
prints `timeline: regs ... samples N seconds T start NS end NS rc R` and a `tl T_NS V0 V1
...` line per change. The bank is at physical 0x80080000 (`REGTIMELINE_BASE` overrides it,
`REGTIMELINE_MEM` the file, which the tests use). Build it for the laptop like
`sgxfive-test` (`cc -O2 -o regtimeline tools/sweep/regtimeline.c`, i686) and copy it to the
home directory. Registers are only ever read; whether a read has a side effect on some
register is not known, which is a reason to keep the ranges to what a sweep needs.

## The visibility counters

Every case run over ssh, by `sweep.py` and by `tools/usse-asm/probe.py`, runs inside
`regtimeline 0 0 0x0494-0x04b4` (added to a table's own `timeline`), as root: the ISP
visibility counters, which counted on one boot and not after a reboot. The first sample is
what the previous job left. A sweep report's `counters:` line and a probe report's `counters:`
line name the cases where they were ever non-zero, and

```
counters.py scan DATA debug/sweeps
```

lists every such case in the saved runs with the case before it (probe runs mark each case
with a `probe-case NAME` line). `SGX_SWEEP_COUNTERS=0` and `SGX_PROBE_COUNTERS=0` turn it off.
