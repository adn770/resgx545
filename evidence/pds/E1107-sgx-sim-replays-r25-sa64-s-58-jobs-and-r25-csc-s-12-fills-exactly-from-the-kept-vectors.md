+++
id = "E1107"
claim = "sgx-sim replays the kept vectors of two published sessions exactly: r25-sa64's 58 jobs (E1104; stages pk64 and q019, one vector a job) replay 58 of 58 with each set's sixteen markers read exactly at their own sa (sa0-sa63) and the attributes a job does not write as earlier jobs left them, and r25-csc's 12 fills (E1103; 2048 pixels each) replay 12 of 12 exactly with the colour-space set the batch left in run order (E037's BT.601 conversion after a BT.601 load, opaque black after a zeros load); r25-csc's 4 copies are listed as skipped, not replayed [HW]; the vectors are the sessions' own printed outputs in the sgx545-vectors format, so a replay that agrees says the sim models what the hardware printed, not more [infer]"
unit = "pds"
method = "round 26 package P1, replayed offline by crates/sgx-sim/tests/session_vectors.rs (cargo test -p sgx-sim --test session_vectors) over the vectors that tools/usse-asm/closing_vectors.py --probes wrote from the published sessions render/closing-r25-sa64 (attempt out/20261115-220241) and render/closing-r25-csc (attempt out/20261115-213805) in the format of tools/usse-asm/vectors.py; the data is the two manifests datasets/vectors-closing-r25-sa64-pds.toml (2 files, 349773 bytes) and datasets/vectors-closing-r25-csc-texture.toml (1 file, 497989 bytes), digests checked by tools/records/datasets.py against resgx545-data; no hardware ran for this record, and E1103 and E1104 stand as written (they claim the sessions, this one the replays)"
tiers = ["HW", "infer"]
date = "2026-11-15"
data = ["vectors-closing-r25-sa64-pds", "vectors-closing-r25-csc-texture"]
terms = []
+++
**What ran.** The vector tables of E1104's stages pk64 and q019 (58 jobs: the PDS secondary program
and data size, the USE program as sent, the 64 attributes of `--scratch-show 64`, the job's pokes,
the scratch dwords and o0 it printed) and of E1103's stage csc (12 fills, each with its program,
pokes, the colour-space set its batch left in init.job.csc and the 2048 pixels it printed) were
replayed by sgx-sim's `session_vectors.rs`, one vector a job, in run order.

**Results [HW, infer].** sa64: 58 of 58 jobs replay, each set's markers exact at their own sa
(sa0-sa63); the attributes a job does not write are compared as AnyValue, since earlier jobs left
them. A marker changed in the readback fails (the control), and the vector cut back to 16 attributes
stops at sa16. csc: 12 of 12 fills exact over 2048 pixels, the 4 copies listed as skipped.

**What it shows.** The sim's PDS secondary-attribute path and E037's colour conversion with the
carried colour-space set agree with every kept output of the two sessions.

**What it does not show.** Anything the sessions did not print: the 4 skipped copies, attributes the
jobs left as earlier jobs set them, other colour-space sets than the ones loaded, and hardware
behaviour beyond E1103 and E1104.
