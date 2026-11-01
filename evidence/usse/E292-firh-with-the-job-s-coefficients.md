+++
id = "E292"
claim = "Given the coefficients its job loaded, every firh vector of the earlier probe rounds runs in the simulator with no mismatch: of 17,851, 16,753 match (15,053 of them with the latch bytes the task did not write taken as any value), 1,066 under fixed banks 1 and 2 agree with tap families fitted to those same vectors and count as fitted, not as matches, and 32 stop; the loaded sets read as E078 gives them, a job that loads nothing has mode 0 and zero groups, the centre field's values written #-16 to #-5 are centres 16 to 27, and positions from 19 read 0"
unit = "usse"
method = "offline: tools/usse-asm/vectors.py jobs wrote each fill vector's job (the transfer-command pokes its run printed and the USE coefficients they load) into sidecars under vectors/jobs/ for the files of vectors/usse/ and vectors/followup/usse/ (whose provenance named a probe's pokes but not its cases'); crates/sgx-sim runs firh from that job; cargo test --release -p sgx-sim and its coverage example over every vector of the data repository, once without the 11.7 runs' vectors (vectors/knowledge/usse/); the fixed banks fitted by tools/usse-asm/firh_banks.py (test_firh_banks.py rebuilds the simulator's table from the data)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = [
    "vectors-usse", "vectors-usse-followup", "vectors-usse-jobs", "vectors-usse-knowledge",
    "usse-filter-banks", "usse-filter-bank2", "usse-filter-edges",
]
terms = ["CR_USE_COEFFS_MODE.MODE", "transfer_cmd.load_use_coeffs"]
+++

**What was missing.** Before 11.7 the simulator stopped on 16,529 firh vectors because the vector
did not say which coefficients the job had loaded, on 1,126 centred below #-4 and on 196 that
read latch bytes the task had not written (E147). The vectors' `provenance.options` named the
probe's pokes; a probe whose cases poke words of their own (`case_set`, the filter-taps tables)
lost those. Each run's raw file prints every case's pokes, so the job of every fill vector is
known: `vectors.py jobs` writes it beside the vector files (`vectors/jobs/`), and new conversions
carry it as `init.job`. 25,369 fill vectors have one; 7,821 firh vectors load nothing, 10,030
load the filter block (`xfer:17` bit 2) with `xfer:32` at 0, 1, 2, 3 or other values.

**The model the vectors take** (measured in E078-E080, E293 and the edge table below, but for
the parts marked **[infer]**):

- Sets 0 and 1 are the loaded groups 0 and 1 at every mode; with mode 3 (0x0a9c bits 1:0) set 2
  is group 2 reading its taps at -3, 0 and +3 only, and sets 3 to 7 give 0. With no load, sets 0,
  1, 6 and 7 give 0 and sets 2 to 5 are bank 0's: a job that loads nothing runs with mode 0 and
  zero groups, even after one that loaded (`usse-filter-sets`: each load0 probe ran after a
  loading one). Bank 0's sets 6 and 7 give 0 with a load as well.
- Banks 1 and 2 (modes 1 and 2) are fitted **[infer]**. `tools/usse-asm/firh_banks.py` takes
  each set's centre in 128ths: E079's changes times 4 ([-8 72 72 -8] for bank 1 sets 2 and 3,
  [-8 108 36 -4] for set 4, [-8 104 36 -8] for set 5, [16 32 32 32 16] and [32 32 32 32] for
  bank 2 sets 4 and 5) and E293's taps ([16 -64 64 -16] and [128 -256 64 64] for bank 2 sets 2
  and 3), shift 7. Every tap vector within 5 of the centre in each tap (the L-infinity
  distance) is kept if some bias fits every case of the set, with the bias range those cases
  allow. The cases are the single-firh vectors at 0x0a9c = 1 and 2 of usse-filter-banks (117
  or 130 per set), usse-filter-control (13 per set) and usse-filter-bank2 (23 per set of bank
  2's sets 2 and 3), centred from -4. The families: 18 members for bank 1 sets 2 and 3, 13 each
  for sets 4 and 5, 7 each for bank 2 sets 2 and 3, 11 each for sets 4 and 5. The window of 5
  is a choice **[infer]**: a 0x20 step moves the result by one count per 4/128 of tap, so E079
  knows each tap to about 4 in 128ths, and 5 holds that with a margin. The simulator gives a
  result only where every member agrees; taps outside the window are zero, as the impulse cases
  show no change there. Since the families are fitted to every bank 1 and 2 vector in the data,
  agreeing with one of them is consistency with the fit, not a hardware check: the simulator
  reports it as fitted (`Outcome::Fitted`), and the coverage counts it with the stops.
- The centre field is 5 bits; its values 16 to 27 (written #-16 to #-5) are centres 16 to 27.
  Positions 12 to 18 fold by the edge mode (rep the end byte, msc mirrored about it, mdc mirrored
  with it doubled), and positions from 19 read 0 in every mode (usse-filter-edges: a loaded
  identity filter on a ramp line reads exactly these positions at every centre -4 to 27). This
  fits all 1,126 vectors centred below #-4, which no per-tap rule fitted before.
- The bytes of the latch a task did not write hold what the slot's last task left, for example
  0xffffff in the filter tables' first runs, 0 in the video-filter rounds, 0x5a5a5a and 0x02 in
  byte 2 in the 11.7 runs, and 0xff00ff, 0x3e and 0x80803e that earlier cases of the same probe
  left. A firh's destination is checked on the byte it wrote, its other bytes taken as any value
  (`Bound::Mask`, counted apart, as the PDS timer is). A byte the task wrote but the run could
  not compute (a bias range, a family that disagrees, sets 6 and 7 under banks 1 and 2, a firh
  a false predicate skipped) is not known, and a result that holds it stops.

**Results.** firh (form 218) on the vectors of the earlier rounds: 16,753 match, 1,066 fitted,
32 stop, none differs (before: 0 match, 17,851 stop). 15,053 of the matches rest on the latch
bytes taken as any value; the byte each firh wrote is exact in all of them. The 1,066 fitted
are the bank 1 and 2 cases of usse-filter-banks and usse-filter-control: they agree with the
families by construction. The 32 that stop read the latch where a later firh may reach it first
(24), where the instances of a slot share it (4) or computed on from its unwritten bytes (4).
With the 11.7 runs, usse-filter-bank2's 46 cases are fitted as well (1,112 in all). firv's
matches rise from 443 to 2,139 (285 stop, 281 of them on unwritten latch bytes they compute
with). No vector of any form differs.

**Not shown.** Sets 6 and 7 under banks 1 and 2 (they are not 0, E298). The exact taps of banks
1 and 2 within their families, and that the families hold out of sample: no vector outside the
fit tests them (Q050). 0x0a9c's value in a job that loads nothing is inferred from the results,
not read **[infer]**.
