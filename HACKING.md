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
glossary terms as their units are published): platform, firmware, bif (bus interface), edm (event data
master), dpm (dynamic parameter management), vdm (vertex data master), ta (tile accelerator), mte
(macro tiling engine), isp (image synthesis processor), tsp (texture and shading processor), pds
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

## Firmware tasks of our own

Phases 11.29 and 11.30 run tasks of ours as firmware (EDM) tasks. The rules below are what lets
a reviewer check that they stay clean-room; each check is a test.

- **What they are.** `asm/fwtask/*.s` are our own sources, generated by `tools/fwtask/gen_blobs.py`
  from `doc/specs/usse_isa.md` and the records they cite in their headers (E475, E476, E480, E512,
  E146, E155), assembled with `usse-asm`, never made from the firmware image. Of them `null`, `mem`,
  `ldr`, `x9b_r1` and `x9b_r2` ran in 11.29 and `state` only for its first task (stage 8 stopped on
  its trigger, E533); in 11.30 `state2` (E536), `state3` (E537: one writer, then the stage
  stopped), `events_m` (E538), `slow` (E539) and `trc_08`, `trc_09`, `trc_12`, `trc_16`,
  `trc_24` and `trc_31` (E540) ran. `events`, `trc_32`, `trc_40`, `trc_48`, `trc_49` and `trc_64`
  did not run. All pass the verifier as it is now (`test_sources.py`); the runs of 11.29 and 11.30
  used the module built before the verifier's review (E531), whose verifier accepted some words
  the present one refuses.
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

You need Python 3.11+ (for `tomllib`) with pytest and reuse:

```sh
python3 -m venv .venv
.venv/bin/pip install pytest reuse
.venv/bin/pytest                 # every suite (pytest.ini lists the trees)
.venv/bin/reuse lint
```

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

## Markdown

Wrap lines at 100 characters and break long sentences at natural points.
