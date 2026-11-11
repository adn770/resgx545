# Hacking on resgx545

The working charter: the rules, the sources, the records, and how to test. What the project is
lives in `README.md`.

## Ground rules

- **Clean-room discipline.** Architectural understanding comes from published patents,
  Imagination's public documents and open source code; behaviour is measured on our own
  hardware. Closed user-space libraries are run or probed only as black boxes, with one
  exception: srvinit's x86 code was disassembled only to locate the firmware and the values it
  patches, for interoperability (below); only those facts are recorded, and black-box captures
  back them wherever they reach. The closed firmware is disassembled only to learn the
  interface our driver must meet: facts about that interface may be recorded (tier RE below),
  its code and bytes never.
- **Interoperability.** The project is developed in the EU. Where it decompiles, it relies on
  the interoperability exception of Directive 2009/24/EC Art. 6, as transposed into national
  law: only the parts indispensable to make an independently created driver work with the
  hardware are studied, and only the interface facts that driver needs are published. This is
  not legal advice.
- **Names come from the glossary.** Every name for SGX545 hardware and firmware is a glossary
  term (`glossary/<group>/<NAME>.toml`, rendered as `doc/glossary.md`; both arrive with the
  first units that name hardware), with its sources and a status (named, inferred, unset). A
  thing no source names gets a descriptive name of our own (tier "ours"), after what our
  evidence shows it does, or a neutral one (`CR_ISP_REG_0418`, `DOUTU1.BIT22`) when the
  evidence does not show it.
- **A neutral name is promoted only on unbiased evidence.** A neutral term gets a functional
  name only from an exhaustive sweep read from its own results, a complete dataflow analysis,
  or a public source.
- **No Imagination bytes in the tree.** The firmware, the PDS programs and anything cut or
  captured from the closed libraries stay out of this repository; data derived from them lives
  in resgx545-data-private.
- **Tests first.** No functional change without a test that failed before it.
- **Clean code.** Remove trailing whitespace before staging.
- **Licences.** Every new source file gets an `SPDX-License-Identifier` line; records and
  documents are covered by `REUSE.toml`. `reuse lint` must pass.
- **`debug/`** is for throwaway artifacts; nothing tracked may depend on it.

## Sources

A glossary term lists its sources, each a record under `cites/` with a tier:

- **1**: the original spelling in open SGX code (GPL or MIT kernel sources, Intel's register
  list), applying to SGX545 directly or at the same offset;
- **1c**: as 1, from another SGX core; the term's evidence says which, and whether the offset
  matches;
- **2**: a string or exported symbol of our own Cedarview package, observed as a black box;
- **3**: Imagination's open Rogue code (Linux, Mesa): the same function on the descendant
  core, an analogy rather than SGX545's own spelling;
- **4**: Imagination's public SGX documents and patents: unit and concept names;
- **ours**: our own term for a thing no source names, after what we measured.

Nothing read from inside a closed binary is a source of a name; a string or exported symbol
seen from outside, as a black box, may back one (tier 2).

## Citation records

An external source is cited by a record, `citations/<source>/C<nnnn>-<slug>.md`: TOML front matter
between `+++` lines (`id`, `source`, `locator`, `link`, `quote`, `terms`), then a short prose
abstract in our own words. The `locator` is where the fact sits in the upstream source (a tree's
`path:line` at the pin, a document's or patent's page, a package's `string@<lib>`); the `link`
is the deep link to it at the pinned version; the `quote` is the one verbatim line that carries
the fact, on one line of at most 200 characters (`tools/records/citations.py` enforces it); the
`terms` are the glossary names that cite the record. Terms, evidence records and specs cite
`C<nnnn>`, not a path into a source. Ids are given once and never reused
(`tools/records/citations.py`, `RETIRED`).

## Evidence records

A finding is one file, `evidence/<unit>/E<nnn>-<slug>.md`: TOML front matter between `+++` lines
(id, claim, unit, method, tiers, date, data, terms, in that order), then prose: what was done, what
was seen, what it shows and what it does not. The units are the hardware's (the abbreviations become
glossary terms as their units are published): platform, firmware, bif (bus interface), edm (event
data master), dpm (dynamic parameter management), vdm (vertex data master), ta (tile accelerator),
mte (macro tiling engine), isp (image synthesis processor), tsp (texture and shading processor), pds
(programmable data sequencer), usse (the shader cores), texture, pbe (pixel back end), zls
(depth/stencil load and store), transfer, render.

The provenance tags (`tiers` in the front matter) say where a claim comes from:

- **HW**: measured on our hardware;
- **CAP**: captured from the closed user-space stack, run as a black box;
- **RE**: our disassembly of the firmware (and of srvinit's firmware loading), for
  interoperability; facts only, no code;
- **DDK**: the GPL kernel sources;
- **infer**: an inference; verify before relying on it.

An id is assigned once. A record that turns out wrong is removed and its id retired
(`tools/records/evidence.py`, `RETIRED`), never reused.

## Open questions

What is not settled is a question, one per file, `questions/<unit>/Q<nnn>-<slug>.md`
(`tools/records/questions.py`): TOML front matter (id, question, unit, kind, an optional value for
a hardware question, phase, evidence, terms, in that order), then prose on what is known, what was
tried and what experiment would settle it. The kind says whose behaviour the open part asks about:
`hw` (what the SGX545 does, the target of knowledge recovery), `fw` (the closed firmware's or
driver's own behaviour) or `kernel` (the design of our kernel driver); the `fw` and `kernel` ones
stay open, parked. A hardware question has a value, `high`, `medium` or `low`, for how much a
simulator loses without the answer. A question that mixes a hardware part with another is narrowed
to the hardware part, with the rest split off as its own parked question, or folded into the
hardware question that holds it. Specs, evidence records and glossary terms cite it as Q<nnn>.
When it is answered, the commit that adds the answering evidence record removes the question and
retires its id (`RETIRED`: "answered by E<nnn>"); from then on the answer is cited, not the
question. A question folded into another (its hardware open part and its evidence moved there) is
retired as "folded into Q<nnn>"; the target has to be open, a citation of the folded id is refused
with the target named, and a fold is not an answer. `doc/open_questions.md` is generated from the
files: the hardware work queue by unit, then the parked `fw` and `kernel` questions.

## Dataset manifests

Data is recorded by dataset manifests, `datasets/<id>.toml` (`tools/records/datasets.py`),
with these keys in order: the title, the repository that holds the bytes (`data` or
`data-private`), the paths in it, the method, the date, the file count, the size, a SHA-256
over the files, and the recipe that made them. The tests check the manifests against a checkout
of each data repository beside this one (`../resgx545-data`, `../resgx545-data-private`) or
named by `RESGX545_DATA` / `RESGX545_DATA_PRIVATE`, and skip a repository that is absent.

A published session (the closing pass's `render/closing-*` and `edm/closing-*` in resgx545-data)
freezes its inputs in `FROZEN.sha256` before its first job. A freeze that names a file of this
tree by absolute path stops verifying when the tree changes that file, so the session pins those
files by commit in `FROZEN.commits` beside the freeze: one `<sha256>  <commit>  <path>` line per
pinned file and hash, the path relative to this tree, `untracked` in the commit's place for a
build product the history never held (`tools/usse-asm/usse-asm`). `tools/records/frozen.py
--write` finds the commits (the newest at or before the manifest's date whose blob has the
pinned hash) and writes the missing files; `--check`, a step of `tools/check.sh`, verifies each
line with `git show <commit>:<path>` and refuses a session that pins this tree without one.
Future freezes are pinned the same way when they are published. The published freeze bytes are
never rewritten: a `FROZEN.commits` is a new file, and the manifest's digest and method follow it.

## Closing-session scorers

A closing session's scorer turns kept job records into verdict lines. The round-3 audit found
the same few mistakes in several sessions, so the verdict rules live in one helper,
`tools/closing/scorekit.py` (tests beside it, standard library only). A new session copies it
byte for byte into its `score/scorekit.py`, so the freeze pins it, names the commit it was copied
from, and draws every bracket, gate and headline from it rather than writing its own:

- A row is held, FAILED or cannot tell; a void job is cannot tell and never a pass.
- A ladder bracket is (last clear, first set]. A void point never narrows it: one inside it
  widens it. A predicted window is tested by strict overlap with the bracket, an open end is
  `None` (never zero, never a large number) and there is no slack of a step.
- An exact-point hypothesis is refuted only when every point it allows lies outside the
  bracket, and held only when the bracket is closed and every point it could hold is allowed.
- A control that is not a pass, FAILED, NODATA or cannot tell alike, gates every row that
  depends on it, not some of them. A control that cannot fail is no control.
- Replicates that disagree are mixed, never held. Counts of jobs behind a hypothesis count only
  the rows that decided.
- A headline is printed only when every control passed and at least one row decided, and it
  says how many rows decided; no data is "cannot tell", and rows that were read and matched no
  hypothesis say so rather than "could not be read".

A scorer bug found after a run is fixed in a post-run copy, never in the frozen file's place
without a trace: `score/<name>.as-run.py` keeps the frozen scorer byte for byte (its hash is the
scorer's line of `FROZEN.pre-fix.sha256`, the freeze the run used), the fixed scorer takes the
frozen name, `out/score-<stage>.fixed.txt` is its output on the kept records beside the kept
`out/score-<stage>.txt`, and `POSTRUN-FIX.md` gives the bug, the reproduction, the fix and the
lines that changed. `out/`, the predictions and the freeze the run used are never changed.

## Firmware tasks of our own

Phases 11.29, 11.30 and 11.32 run tasks of ours as firmware (EDM) tasks. The rules below are what
lets a reviewer check that they stay clean-room; each check is a test.

- **What they are.** `asm/fwtask/*.s` are our own sources, generated by `tools/fwtask/gen_blobs.py`
  from `doc/specs/usse_isa.md` and the records they cite in their headers (E475, E476, E480, E512,
  E146, E155), assembled with `usse-asm`, never made from the firmware image. Of them `null`, `mem`,
  `ldr`, `x9b_r1` and `x9b_r2` ran in 11.29 and `state` only for its first task (stage 8 stopped on
  its trigger, E533); in 11.30 `state2` (E536), `state3` (E537: one writer, then the stage
  stopped), `events_m` (E538), `slow` (E539) and `trc_08`, `trc_09`, `trc_12`, `trc_16`,
  `trc_24` and `trc_31` (E540) ran. `events`, `trc_32`, `trc_40`, `trc_48`, `trc_49` and `trc_64`
  did not run; in 11.32 `trcp_32`, `trcp_36`, `trcp_40`, `trcp_44` and `trcp_48` (one blob, the
  marker written to `r123`, E550) ran on the fixed module. All pass the verifier as it is now
  (`test_sources.py`); the runs of 11.29 and 11.30 used the module built before the verifier's
  review (E531), whose verifier accepted some words the present one refuses.
- **The tail call.** A task jumps into the closed handler of the slot it replaced (`mov pclink, rN`,
  `lapc`) by an instruction index that a landed record states: the four start indices of PDS #13
  (6, 1434, 2766, 3594) are in E146 and are the `target` of the four `CODE_WORD` records of buffer 4
  in E003. The user approved a jump by such an index and nothing more. No closed code or byte is
  copied, assembled, quoted or read for a task, and the index is in no `asm/fwtask` source: the
  kernel writes it into a patched `limm` from the record it replaces (`sgx_fw_patch_word()`, the
  loader's own evaluation). The four stated indices do appear elsewhere, as E146 states them: in
  the tests (`test_overlay.py`, `test_sources.py`, which leaves out 6 as too common a number to
  scan for), in `tools/fwtask/make_vectors.py` (`CONT = {0: 6}`, the continue index of the
  general slot) and `make_vectors1130.py` (all four, for the program words of `events_m`), to
  rebuild what a run saw, and in the kernel's KUnit synthetic firmware.
- **What changes in the firmware.** One dword per armed slot, the slot's start word in PDS #13's
  data (FACT data the loader patches anyway); the ukernel, the five PDS programs and every other
  buffer stay as the loader builds them. The code is in the kernel's debug group, off by default,
  armed at load, and a reset gives the stock buffers back.
- **Checks** (`tools/fwtask`, `pytest tools/fwtask`):
  1. *The sha map.* `asm/fwtask/fwtask.map` has the sha256 of each source and of the blob it
     assembles to; `test_sources.py` assembles again and compares, and regenerates the sources
     from `gen_blobs.py`. Each run's `env.toml` in resgx545-data names the blob hashes the tool
     uploaded, which equal the map's.
  2. *The source scan.* `test_sources.py`: no source holds 1434, 2766 or 3594. With the private
     firmware (`RESGX545_DATA_PRIVATE`), `test_overlay.py` checks that no constant of 17 bits or
     more in any source is an aligned 32-bit word of any of the 15 buffers (a smaller constant is
     a word of any program); it reports a count and never a word.
  3. *The 15-buffer comparison.* `test_overlay.py` builds the 15 buffers with the reference
     loader and models the kernel's overlay (`overlay_model.py`, from `sgx_own_apply()`): armed
     (each slot, pairs, all four; TRC 8, 9, 12) exactly the start dword of each armed slot differs
     and equals `(trc << 24) | 0xf | (0x4000 << 4)`. That is a check of the model. The kernel's
     code is checked on the real firmware by a host build, `tools/fwtask/host/own_host.c`, which
     compiles the fork's `sgx_fw.c` and `sgxfive_owntask.c` (needs `RESGX545_LINUX` or `../linux`
     and a C compiler) with shim headers, runs `sgx_fw_build()` and `sgx_own_apply()` on the
     firmware and prints only a sha256 per buffer: unarmed they equal the reference loader's,
     armed they equal the model's and only buffer 4 differs. Without the fork checkout this
     check skips, and what remains is the check of the model. The kernel's KUnit makes the same
     comparison on a synthetic firmware. No test compares closed bytes: a failure names buffers,
     digests, offsets or counts.
  4. *The verifier.* The tool and the kernel refuse by default: a word is accepted only if it is
     canonical, a row of one generated table (`gen_verify.py` writes `sgx_own_regs.h`) whose mask
     pins every bit no field names, so a stray bit is never ignored; only the forms our sources use
     are rows. The clock-gate registers are refused by name for `str` and `ldr` (a first run of
     writes to `CR_CLKGATECTL2` froze the laptop once, E445; the exact write was not recorded),
     the register-index forms, `ba` and `.savelink` are refused, `lapc` is only the patched
     triple (limm, `mov pclink`, `lapc`) and nothing else touches `pclink`, the last word ends the
     task, and every `ldad` and `stad` base is, on every path, a register set from a patched
     results-page `limm` and not written since, with the offset inside the page (the EDM's page
     directory maps the closed code, so a store through any other base could write it); the
     code page is also mapped read-only for the EDM. The tool's tests (`test_verifier.py`) and the
     kernel's KUnit run the same crafted blobs and compare the reason of each refusal, and
     `test_host_verifier.py` runs the kernel's verifier on the host against the tool's over every
     single-bit change of several blobs and random words of the canonical forms.
  5. *The `str` allow list.* `tools/fwtask/regs.toml` names the registers a task may store to:
     0x0814 and 0x0a78, plain storage (phase 11.29), and since round 3 of the closing pass
     (2026-11-10, the user's decisions R3-K1 and R3-K10) `CR_EVENT_HOST_CLEAR2` (0x0114),
     `CR_EVENT_HOST_CLEAR` (0x0134) and `CR_EVENT_TIMER` (0x0acc), each for `str` only, never
     `ldr`. Every other register whose write has an effect, and every clock-gate register, stays
     refused. This decides Q198 (whether the list would take a register whose write has an
     effect): the user widened it to these three, and the runs that stored to them are E818 and
     E822; the str-then-ldr test while a job runs that Q198 named was not run.
- **What the author ran.** `pytest tools/fwtask` with both data repositories and a fork checkout
  present: every test passes, including those of `test_overlay.py` (the model, the host build on
  the real firmware and the source scan) and the ones that compare the vectors of resgx545-data
  with the raw runs; without the private repository the overlay tests skip and say "SKIPPED, NOT
  PASSED", and without the fork checkout so do the host builds. The checks print counts and
  digests, never firmware words, and nothing of the closed data is recorded. The kernel's KUnit
  and the series check have not been run on this code yet.
- **Task sources.** `state.s` no longer writes `pclink` (the verifier refuses `mov pclink` outside
  the patched triple), so its second task reads the `pclink` the first one left, not a value of
  ours; the task of E533 did write one (an arbitrary value), and its blob was not reassembled here,
  so that the present verifier refuses it rests on the verifier's rule, not on a check of that blob.
  `state2.s` and `state3.s` (11.30) read `pclink` and write `sa`, `r`, `i` and `p`, as `state.s`
  does, and call the closed task through the patched triple; the verifier accepts them and all other
  sources (`test_sources.py` checks every source against it). The blobs of the sources that ran in
  11.30 equal the hashes the `env.toml` of the run names (21 of its 22 names reassemble to theirs);
  the `state` blob listed there does not match the landed `state.s` (sha256 977c2027...), whose
  source as it ran is not kept, was not reassembled, and did not run in 11.30.

## Getting set up

You need Python 3.15 (the venv is pinned to it) with the dev requirements, pytest and reuse:

```sh
python3.15 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
tools/check.sh                   # every check (cargo, pytest, records, reuse, the guard)
.venv/bin/pytest                 # every suite (pytest.ini lists the trees)
.venv/bin/reuse lint
```

numpy is not in `requirements-dev.txt`: no tracked `.py` imports it (`tools/check.sh` fails if one
does), so keep it in a scratch venv.

The record checkers run inside pytest; `python3 tools/records/evidence.py --draft` checks
records whose ids are not assigned yet. Some checks need inputs from outside this repository
and skip without them, so a plain CI runs them only if it provides those inputs:

- the data repositories, as above;
- `RESGX545_CDV_LIBS`: the `usr/lib/` directory of your Cedarview package, for the tier-2
  black-box checks of the glossary.

## Commits

GNOME/freedesktop style:

```
topic: short summary (max 70 chars total)

Description of the changes, wrapped at 80 characters. Explain
what changed and why.
```

- The topic is the component or a type (`docs`, `fix`, `test`, `refactor`, `chore`).
- Lowercase after the colon, imperative mood, no period at the end of the first line.
- One logical change per commit, with its tests.
- AI-assisted commits say so: a `Co-Authored-By:` trailer here, `Assisted-by: LLM` in the
  kernel fork. An AI agent never adds a `Signed-off-by:`.

## Workflow

Since 2026-11-09 work is committed directly. The rewrite kit that built the first 61 commits from
a notebook is retired: those commits keep their 2026-11-01 dates and are never rewritten, and
new commits carry real dates. Landed history stays as it is once anything is pushed; nothing is
pushed before `tools/clean-room/guard.py --history` has run over every ref.

- Once per clone: the venv above, then `git config core.hooksPath tools/hooks`. The pre-commit
  hook runs `tools/check.sh --quick` on the staged change (whitespace, the guard on the index,
  no numpy, the cheap record checks), the commit-msg hook the message rules (subject of at
  most 70 characters, body wrapped at 80, the trailer) and the guard's patterns on the message.
  `tools/check.sh` runs everything, as the hooks' parent. Stage first, then check: the guard
  reads the index.
- Confidential sources stay out. The guard derives, on each run, the identifiers found only in
  the confidential sources from trees outside every repository (in no casing in a public tree,
  and not one letter and digits only), and refuses any of them, the private patterns and the
  renamed-away spellings in files, messages and history. Its data
  lives in the private data repository's `clean-room/` directory, found through
  `RESGX545_GUARD_DIR` (default `../resgx545-data-private/clean-room/` beside this checkout):
  never copy, quote or summarise it here, in a message or in a report. The machine-local paths
  of the trees it reads are in `refs.local.toml` there (untracked; `refs.local.toml.example`
  in `tools/clean-room/` shows the shape). A glossary term allows nothing by existing: a
  confidential-only token passes only through the private review list. A name we reached
  ourselves (a job name, a scorer word, a hypothesis) is claimed through that review, with its
  provenance, and never reworded or renamed around; only a real slip is reworded. With the
  data missing the guard fails when `RESGX545_REQUIRE_GUARD=1` (the default of `check.sh` and
  the hooks) and says NOT CHECKED otherwise; a checkout without the private repository sets it
  to 0 and gets no guard. The private repository is never pushed to a public remote.
- Landed records get dated corrections only: append a `Correction YYYY-MM-DD:` section, leave
  the rest as it was. The pre-commit hook warns about any other change to an evidence record;
  it does not block. One exception (user decision, 2026-11-11): when a correction contradicts
  the record's `claim`, the claim line is edited to the corrected reading and ends with
  `[corrected YYYY-MM-DD, see Correction]`, so that `doc/evidence_log.md`, built from the claim,
  shows it; the correction section of that date quotes the claim as it was. `evidence.py`
  refuses a mark without its correction, and a test refuses a claim edited since 2026-11-11
  without the mark.
- The forks (Linux, radare2) are committed to directly in their clones, with the trailer
  `Assisted-by: LLM`, the hooks of this checkout and `RESGX545_GUARD_FORK=1`, so the fork
  patterns apply too. Landed fork commits are never rewritten. `tools/fork/fork-check.sh`
  checks a series on the build host, `tools/fork/recheck.sh BASE TIP` sends and runs it and
  records the tested tip, `tools/fork/fork-land.sh HOME BRANCH BASE TIP` moves the branch only
  to that tested tip, after the guard.
- On the laptop (no docker) the series check runs in its build root:
  `FORK_CHECK_RUNNER=chroot FORK_CHECK_WORK=$HOME/src/linux-sgx-checkout-check
  tools/fork/recheck.sh BASE TIP`, the work directory being the host's existing, already built
  one (`CHECK_RUNNER` and `CHECK_WORK` for `fork-check.sh` itself). `FORK_CHECK_RUNNER` defaults
  to `docker`. The chroot runner without `FORK_CHECK_WORK` is refused before anything is sent:
  the default directory would start a from-scratch kernel build on the Atom.
- Commit style is the one under Commits. The test-cycle scripts and their settings are in
  `tools/bringup/` (`local.env.example`).

## Markdown

Wrap lines at 100 characters and break long sentences at natural points.
