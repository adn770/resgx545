# resgx545: tools

Host-side tools. None of them needs the Cedarview hardware: they run on any Linux or macOS
machine with Python 3.15 (`requirements-dev.txt`: pytest, reuse).

- `records/`: the evidence records' format and checker (`evidence.py`:
  `evidence/<unit>/E<nnn>-<slug>.md`, one finding per file) and the dataset manifests
  (`datasets.py`: `datasets/<id>.toml`, which data repository holds the bytes and the hash
  that pins them), the open questions (`questions.py`: `questions/<unit>/Q<nnn>-<slug>.md`,
  one per file, retired once answered, rendered as `doc/open_questions.md`); `open_rows.py`,
  a glossary view kept beside the records tooling, renders the glossary's inferred terms as
  `doc/open_rows.md`; `citations.py` checks the citation records
  (`citations/<source>/C<nnnn>-<slug>.md`: locator, link at the pin, one quoted line) and the
  glossary's references to them. `new_record.py --session DIR --id E<nnn> --stage S` drafts
  a record's front matter, method and printed verdicts from a published closing session's own
  files, leaving the claim and the readings as `TODO-FILL` markers. `digest.py [--check]`
  renders `doc/state_digest.md`, the project's state on one page (open questions, recent
  records, closing sessions, tool and fork versions).
- `clean-room/`: the glossary tooling: `glossary.py` loads the glossary terms under
  `glossary/` and renders `doc/glossary.md`; `glossary_coverage.py` counts them per unit. Also
  the clean-room guard, `guard.py`: no identifier found only in the confidential sources, and
  none of the private patterns or renamed-away spellings, may be in a tracked file, a commit
  message or the history (`--tree`, `--staged`, `--history`, `--message`); its data is in the
  private data repository, see `HACKING.md`, "Workflow".
- `check.sh`: the one check script (`--quick` for the staged change); `hooks/`: the pre-commit
  and commit-msg hooks (enable with `git config core.hooksPath tools/hooks`) and the message
  rules.
- `fork/`: the Linux fork's series check (`fork-check.sh`), `recheck.sh` to run it on the build
  host, and `fork-land.sh` to move a fork branch to a tested tip.
- `bringup/`: the test-cycle scripts (build and push the kernel module, `push-tools.sh`,
  `deploy-tool.sh`, `health.sh`, `run-table.sh`) and `local.env.example`, their settings.
- `fwcutter/`: cuts the firmware container from the user's own copy of the closed libraries
  (`fwcutter.py`, `get-firmware.sh`), reads and writes the container (`fwformat.py`) and holds
  the reference loader (`fwload.py`); the format is `doc/specs/fw_format.md`.
- `sgx_fw/`: the same loader in C, in kernel coding style, for the driver.

The extraction harness that produces the loader's captures is in `harness/ukernel-extract/`,
beside `tools/`.
