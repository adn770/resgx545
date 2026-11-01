# resgx545: tools

Host-side tools. None of them needs the Cedarview hardware: they run on any Linux or macOS
machine with Python 3.11+ (pytest for the tests).

- `records/`: the evidence records' format and checker (`evidence.py`:
  `evidence/<unit>/E<nnn>-<slug>.md`, one finding per file) and the dataset manifests
  (`datasets.py`: `datasets/<id>.toml`, which data repository holds the bytes and the hash
  that pins them), the open questions (`questions.py`: `questions/<unit>/Q<nnn>-<slug>.md`,
  one per file, retired once answered, rendered as `doc/open_questions.md`); `open_rows.py`,
  a glossary view kept beside the records tooling, renders the glossary's inferred terms as
  `doc/open_rows.md`; `citations.py` checks the citation records
  (`citations/<source>/C<nnnn>-<slug>.md`: locator, link at the pin, one quoted line) and the
  glossary's references to them.
- `clean-room/`: the glossary tooling: `glossary.py` loads the glossary terms under
  `glossary/` and renders `doc/glossary.md`; `glossary_coverage.py` counts them per unit.
- `fwcutter/`: cuts the firmware container from the user's own copy of the closed libraries
  (`fwcutter.py`, `get-firmware.sh`), reads and writes the container (`fwformat.py`) and holds
  the reference loader (`fwload.py`); the format is `doc/specs/fw_format.md`.
- `sgx_fw/`: the same loader in C, in kernel coding style, for the driver.

The extraction harness that produces the loader's captures is in `harness/ukernel-extract/`,
beside `tools/`.
