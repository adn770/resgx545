# Hacking on resgx545

The working charter: the rules, the sources, the records, and how to test. What the project is
lives in `README.md`.

## Ground rules

- **Clean-room discipline.** Architectural understanding comes from published patents,
  Imagination's public documents and open source code; behaviour is measured on our own
  hardware. Closed user-space libraries are run or probed only as black boxes. The closed
  firmware is disassembled only to learn the interface our driver must meet: facts about that
  interface may be recorded (tier RE below), its code and bytes never.
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
- **RE**: our disassembly of the firmware, for interoperability; facts only, no code;
- **DDK**: the GPL kernel sources;
- **infer**: an inference; verify before relying on it.

An id is assigned once. A record that turns out wrong is removed and its id retired
(`tools/records/evidence.py`, `RETIRED`), never reused.

## Open questions

What is not settled is a question, one per file, `questions/<unit>/Q<nnn>-<slug>.md`
(`tools/records/questions.py`): TOML front matter (id, question, unit, phase, evidence, terms,
in that order), then prose on what is known, what was tried and what experiment would settle
it. Specs, evidence records and glossary terms cite it as Q<nnn>. When it is answered, the
commit that adds the answering evidence record removes the question and retires its id
(`RETIRED`: "answered by E<nnn>"); from then on the answer is cited, not the question.
`doc/open_questions.md` is generated from the files.

## Dataset manifests

Data is recorded by dataset manifests, `datasets/<id>.toml` (`tools/records/datasets.py`),
with these keys in order: the title, the repository that holds the bytes (`data` or
`data-private`), the paths in it, the method, the date, the file count, the size, a SHA-256
over the files, and the recipe that made them. The tests check the manifests against a checkout
of each data repository beside this one (`../resgx545-data`, `../resgx545-data-private`) or
named by `RESGX545_DATA` / `RESGX545_DATA_PRIVATE`, and skip a repository that is absent.

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
