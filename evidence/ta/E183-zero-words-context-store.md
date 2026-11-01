+++
id = "E183"
claim = "The TA command's twelve zero register words read best as state a TA saves and resumes when it is interrupted: the measurements fit it (every word zero in the job, three address-shaped, none a cull disable, none used as an address by a TA that runs to its end), but no run interrupts a TA, so the reading is untested"
unit = "ta"
method = "comparison of the results of E054, E056 and E182 (register readback after ~0, scratch-page values, cull dumps) with the shape of state a TA would need to save and resume; the reading is ours, no public source is cited (the tree holds no citation record for one)"
tiers = ["infer", "HW"]
date = "2026-11-01"
data = ["ta-zero-words"]
terms = [
    "cmd_ta.use_reg_0a04", "cmd_ta.use_reg_0aa0", "cmd_ta.ta_reg_02b0", "cmd_ta.ta_reg_02b4",
    "cmd_ta.ta_reg_02d0", "cmd_ta.ta_reg_02d4", "cmd_ta.reg_0324", "cmd_ta.reg_0364",
    "cmd_ta.reg_0368", "cmd_ta.reg_0370", "cmd_ta.reg_0374", "cmd_ta.te_reg_02a8",
]
+++

**What it rests on.** Three results, each a measurement on the triangle job:

- every one of these words is 0 in the kernel-built command (E054), and no change to one, to a
  scratch-page address or to ~0, alters a pixel or touches the scratch buffer, except `ta:167`
  at one value (E056);
- the register each word lands in keeps only some bits when loaded with ~0: three keep an
  address-shaped field (low bits clear), four keep all 32 bits, one is a 26-bit field, one 15
  bits, one 8 bits in 31:24, one 8 bits in 19:12, and one reads 0xff whatever is loaded (E182);
- loading ~0 does not stop a culled or off-target triangle from being culled (E182).

**The reading [infer].** Words that no complete TA run reads, that are all zero, and that include
address-shaped and counter-shaped registers fit state a TA would save when it is interrupted
(for example by running out of parameter buffer) and restore to resume. The word-by-word reading
of the shapes, each an inference, takes the register each word lands in:

- `cmd_ta.use_reg_0a04`, `cmd_ta.reg_0324`, `cmd_ta.ta_reg_02d0`: addresses of saved state
  (the first two 16-byte aligned, the last dword aligned);
- `cmd_ta.use_reg_0aa0`, `cmd_ta.reg_0364`, `cmd_ta.reg_0370`, `cmd_ta.reg_0374`: full-width
  words of saved state, a resume position or task word each;
- `cmd_ta.ta_reg_02d4` (26 bits), `cmd_ta.reg_0368` (15 bits): a size or count of the saved
  state;
- `cmd_ta.ta_reg_02b0` (8 bits in 31:24) and `cmd_ta.te_reg_02a8` (8 bits in 19:12): a state
  field and a resume position of the tiling engine;
- `cmd_ta.ta_reg_02b4` (reads 0xff after any job): a status that a finished TA leaves full.

**Not shown.** No run interrupts a TA mid-scene, so no run loads these words with a saved state or
reads them back after an interruption; every reading above is a fit to the shapes, not a result.
What would test it: a TA interrupted by a parameter buffer too small for the scene, with the
words poisoned beforehand, and the registers read after the interruption. The alternative that
the words are unused fields of the interface, or are specific to a path no client takes, is not
excluded.
