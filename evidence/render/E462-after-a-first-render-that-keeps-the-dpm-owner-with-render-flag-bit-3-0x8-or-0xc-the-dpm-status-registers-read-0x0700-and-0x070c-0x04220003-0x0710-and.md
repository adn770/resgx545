+++
id = "E462"
claim = "After a first render that keeps the DPM owner with render flag bit 3 (0x8 or 0xc) the DPM status registers read 0x0700 and 0x070c = 0x04220003, 0x0710 and 0x071c = 0x421, 0x0724 = 0x00020002 and 0x0728 = 2 (6 of 6 runs), and 0x00020003, 1, 0 and 0 with bit 2 alone or no flag (6 of 6); closing the first context changes none of the 85 registers 0x0600 to 0x0750 (4 of 4 runs with bit 3, and in the 4 runs with the control and bit 2 alone) and the second context's render then faults (9 of 9 runs) with none of the 85 changing before the recovery (3 of 3 timeline runs that sampled all of them), where with the first context open the second render takes them back to 0x00020003, 1, 2 and 0 (5 of 5)"
unit = "render"
method = "probes/render/kept-owner-regs.toml (kept-owner-regs.sh) and probes/render/kept-owner-timeline.toml on the laptop (direct cable): sgxfive-test tri -n 1 --ctx2 with --close-first-early or --words-between, the first context's render flags flipped through the kernel poke ta:7^=V, --words DIR with --regs 0x0600-0x0750 (the registers at each words snapshot, new in this phase) and, in the second table, regtimeline over the same range; the GPU reset before each run"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["render-kept-owner-regs", "render-kept-owner-timeline"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "CR_DPM_TASK_STATE"]
+++

**What runs.** E458 read TA3DCtl dwords 20 and 25 at four steps of the kept-owner cases; the DPM
registers only after the second render. `tri -n 1 --ctx2` renders the first context with its render
flags (TA command dword 7) flipped by the kernel poke `ta:7^=V`, then (`--close-first-early`)
closes it and renders the second context in the same VM, or (`--words-between`) keeps it open. New
in this phase, `--words DIR` with `--regs 0x0600-0x0750` also reads the 85 registers at every
snapshot: before the first render (0), after it and before the close (101), after the close (201)
and after the second render (1). Table `render/kept-owner-regs` (12 runs, the GPU reset before
each): no flip (control), V = 0x4, 0x8 and 0xc with the first context closed, V = 0x4 and 0xc with
it open, two runs each; the registers are printed as the first snapshot's non-zero ones and, after
it, those that changed since the snapshot before. The script ends with two regtimeline runs of the
same range (V = 0xc, closed first; their lines are cut at 200 characters, so only 21 of the 85
registers are in them and 0x0700 is not); they faulted too, and are counted among the 9 faulting
renders but not in the register comparisons. Table `render/kept-owner-timeline` (6 runs):
regtimeline, whole lines, over 0x0600-0x0750 while `tri -n 1 --ctx2` runs with V = 0xc, three runs
with the first context closed early and three with it open.

**Results** (DPM registers 0x0700, 0x070c, 0x0710, 0x071c, 0x0724, 0x0728 after the first render,
snapshot 101; TA3DCtl dwords 20 and 25 as E458; the two runs of every case gave the same registers,
words and outcome):

| flags flipped | first context | 0x0700 0x070c | 0x0710 0x071c | 0x0724 | 0x0728 | after the close (201) | second render |
|---|---|---|---|---|---|---|---|
| none | closed | 0x00020003 | 1 | 0 | 0 | no register changed | exact |
| 0x4 | closed | 0x00020003 | 1 | 0 | 0 | no register changed | exact |
| 0x8 | closed | 0x04220003 | 0x421 | 0x00020002 | 2 | no register changed | faulted |
| 0xc | closed | 0x04220003 | 0x421 | 0x00020002 | 2 | no register changed | faulted |
| 0x4 | open | 0x00020003 | 1 | 0 | 0 | not taken | exact, no 0x07xx change |
| 0xc | open | 0x04220003 | 0x421 | 0x00020002 | 2 | not taken | exact; 0x00020003, 1, 2 and 0 after it |

The last row's second render takes 0x0700 and 0x070c to 0x00020003, 0x0710 and 0x071c to 1, 0x0724
to 0x00000002 and 0x0728 to 0 (snapshot 1, 2 of 2; and in all 3 timeline runs). The words are those
of E458: dwords 20 and 25 hold the first context's RT data + 0x18 after the first render with bit
3, dword 20 only with bit 2 alone, and the open case's second render clears them. The faulting
renders were the 4 closed bit-3 runs of the first table, the 2 cut timeline runs that end its
script and the 3 closed runs of the second table (BIF fault status `0x90004` in the logs, 6 lines
for the first dataset and 3 for the second; E458 labelled it INT_STAT). regtimeline, 3 s, 85
registers: in the 3 faulting runs the first render's changes arrive at 50 to 55 ms (0x0700 to
0x04220003, by way of 0x04220001 in 2 of the 3, 0x0710 to 0x421, 0x0724, 0x0728, and 0x0748 from
0x1f to 0x1b), then nothing changes until the recovery at 162 to 165 ms (6 registers back to 0 and
0x0748 to 0x1f); in the 3 open-context runs the first render's changes come at 51 to 52 ms and the
second render's at 53.4 to 53.8 ms in 3 to 4 samples (0x0700 04220003, 04220001, 04220003, then
00020003; 0x0724 00020002, 00000002, 00020004, 00000002) and end at 0x0700 = 0x00020003, 0x0710 =
1, 0x0724 = 2 and 0x0728 = 0.

**What it shows.**

- The kept owner of bit 3 is visible in the DPM status registers as well as in TA3DCtl: after its
  render they read 0x04220003, 0x421 and the 0x0724 and 0x0728 values above, where a render with
  bit 2 alone or no flag leaves 0x00020003, 1, 0 and 0 [HW]. 0x422 is the parameter buffer's page
  count, so the registers hold the buffer's pages for the kept owner, 0x421 of them in 0x0710
  [infer].
- Closing the first context frees nothing the sampled registers show: the 85 registers are the same
  before and after the close, in 4 of 4 runs with bit 3 (and in the 4 runs with the control and bit
  2 alone) [HW]. With the first context open, the second render
  takes them back, in 5 of 5 runs [HW].
- The second context's render, with the first gone, fires none of that: no sampled register changed
  between the end of the first render and the recovery of the fault (3 of 3 runs that sampled all 85
  registers) [HW], so the access
  that faults (page 0x20003000, E458) comes before the DPM does anything the registers show, or is
  not visible in them [infer].

**What it does not show.** What accesses the page, the DPM state page's content, a third context
holding the VM, and registers outside 0x0600-0x0750.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (the installed module file and the loaded module, read from /sys/module,
were equal; the run prints both and stops if they differ), sgxfive-test sha256
fa7592a6170712ed0080066c56602304607ed31ec608afd66441a597587675a7 (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable. The first
run of render/kept-owner-timeline was overwritten: its three runs with the first context open were
refused by the tool (--words-between needs --words) and its timeline lines were cut at 200
characters; the data are its second run.
