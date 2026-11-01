+++
id = "E184"
claim = "After a one-render triangle job TA3DCtl dword 24 reads 0x32400000 and after a two-render job 0x324002c0, so it moves 0x2c0 for the second render; the DPM free-list status registers 0x0700, 0x070c, 0x0710 and 0x071c change together on every render; VDM_CTRL_STREAM_BASE is not in the register file and is not shown"
unit = "vdm"
method = "the register snapshot script of probes/platform/register-snapshots.toml on the laptop, linux fork with the debug option on: the debugfs register file (registers and the TA3DCtl and CCBCtl words) before and after sgxfive-test tri, tri -n 2 and tri at 256x256, as the diff; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-register-snapshots"]
terms = []
+++

**What runs.** The script dumps the debugfs register file (the registers it can read, then
`ta3dctl` and `ccbctl` lines for dwords of the TA/3D control block and the kernel CCB control),
runs one job, dumps again and keeps the diff. The relevant steps are `tri` (one 64x64 render),
`tri -n 2` (two renders in one context) and `tri` at 256x256 (one render), in that order. The
fresh-boot "before" of the first step holds zeros in these words.

**Results.** Dword 24 of the TA/3D control block is the `ta3dctl 0x60` line:

| step | renders | before | after |
|---|---|---|---|
| tri | 1 | 0x00000000 | 0x32400000 |
| tri -n 2 | 2 | 0x32400000 | 0x324002c0 |
| tri 256x256 | 1 | 0x324002c0 | 0x32400000 |

So after one render in a new context the word reads 0x32400000, after two renders 0x324002c0, a
step of 0x2c0, and a new context starts again at 0x32400000. (That the word is the TA client
CCB's read address, and 0x2c0 the size of a command, are readings: the table shows only the
values.)

The DPM free-list status registers (0x0700, 0x070c, 0x0710, 0x071c) change at each of the three
steps, and read alike in pairs: 0x0700 and 0x070c agree each time, 0x0710 and 0x071c agree.
Their values after the three steps are 0x00020003, 0x00040005 and 0x00010006 (the first pair) and
1, 3 and 5 (the second). The first two steps add 2 to each half of the first pair and 2 to the
second; the third does not continue that count (the first pair's high half falls from 4 to 1).
So the values do not read as a running count of pages across these steps, and this record states
no page count.

Other words in the same diffs move at every render: `ta3dctl 0xa4` and `0xa8` (1, 2, 1) and
`ta3dctl 0xc4` (2, 3, 4), and the CCB control words (`ccbctl 0x00` and `0x04` equal, 0x09 to
0x0f to 0x16 to 0x1c).

**Not shown.** `CR_VDM_CTRL_STREAM_BASE` (register 0x0238) is not among the registers the file
lists, so what it reads after a TA kick, and whether that is the end of the stream the TA walked,
is not shown by this data. The DPM registers' meaning is not read. One run.
