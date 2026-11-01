# Phase 11.36 run files (the work directory of the second firmware requests, as run)

The files the runs of phase 11.36 used, kept as they were run (the file names keep the 1137 of the
work directory, which the data repository's dataset names and env.toml files also carry).

The predictions (`predictions-1137.toml`, sha256
17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2) and every file of
`manifest-1137.sha256` were written and hashed before the first run: from this directory,
`shasum -a 256 -c manifest-1137.sha256` checks them (the asm sources and blobs, the frozen tables
under `probes/usse/` and their templates, the generators, the judge, the runner and the host
models). The tables the laptop ran are the renamed copies in `probes/usse/fw37-*.toml` of the
tree (only their `name =` lines differ; the sha256 values are in the records).

The header of `predictions-1137.toml` says every runnable file is in the manifest: it is not so
for these files, written after the freeze, none of which judges a frozen hypothesis:

- `fw_stage_1137.sh` 5db48d2b9ea6afc6e9c53c5c40294ccd1876ec9fdd843b6de72a0fb00eaa709b
- `imm-encode.txt` 74e27b9b22de8ec02f3e7bcd6a233adececd9fd708045661334f48d9322aa18b
- `judge_client_1137.py` 18df2bc162ea6e1c0cc5be316710df23792c786f5f7c92d9cd3fb1ae48795291
- `make_vectors1137.py` 0b6faa6efe5cd4d42373e559fa2f663ef70ea0e6218cc98ab6e9e2961a5ce7de
- `narrow_table_1137.py` c86ebc99a598c0fc015ac34b32896ba6a90227633c68560bfb24567beb2664b5
- `predictions-1137.sha256` d8a5bd33efb765f4f5ccf03c50c676a90c6bbf5af87827eb2b787244a7c4feae
- `run_1137_logged.py` 203fd0865437a398fff637c9b312de58373a90995244154a38d363330f5172b3
- `run_client_1137.sh` ee65e25413706b9a8550b85101c259d84df21d8b63b407c27480fd37e8f4eb51
- `stats_client_1137.py` 6bc4ff1b1af8f2c9f48489868c05c4c94bca9ef7a63024ef0b3eb5cfd896bd40
- `stop_recover_1137.py` 1b992623250e46a3d107eb42c932c4b7dd46e3ebe7ffbcd7ace759d81958d2a9
- `summarize_client_1137.py` 939f8961cd15f438ae121615c885f8ec570123cf7a2187074bd943536291175e
- `verifier-matrix.txt` 11eb6c7d62dda28bdb1af723b3e221a21bd69fa63ea2880e12b9b836dbd32256

The stages f14a, f14b, f14c, f15 and q033q2 of `run_1137.py` were not run in this phase (their
follow-up is run separately). `imm_encode.py` and `verifier_matrix.py` are host checks; their
output is `imm-encode.txt` and `verifier-matrix.txt`, which are not part of a dataset.
