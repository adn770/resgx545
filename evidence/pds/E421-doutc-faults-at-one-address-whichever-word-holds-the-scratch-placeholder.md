+++
id = "E421"
claim = "A movs to doutc in the triangle's primary pixel program faults the job in 8 of 8 jobs with BIF status 0xd0400 at 0x1f031 (once 0x1f034) whichever of its four words holds the scratch buffer's placeholder 0x5CAF0000, while the control completes"
unit = "pds"
method = "probes/pds/doutc-address.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the primary pixel program of probes/pds/task-inputs.toml (pds_iter_if.s) with `movs doutc` of four data words one of which (ds0[4] by parameter C) is the placeholder, in each of the four positions and a control that does not issue it, twice (10 jobs)"
tiers = ["HW"]
date = "2026-11-07"
data = ["pds-doutc-address"]
terms = ["PORT.DOUTC"]
+++

**What was seen.** The control drew exactly in both runs. Each of the eight doutc jobs failed with a
BIF fault, status 0xd0400 (E264's value, not the PDS's own 0x92000 or 0xd2000), the address 0x1f031
in seven jobs and 0x1f034 in one, the same for the placeholder as word 0, 1, 2 or 3.

**What it shows.** The faulting address does not follow the placeholder: either the unit takes its
address from something other than the four words (a register, the program's own data pointer) or the
placeholder was not patched in this program's data and the words read as 0x5CAF0000 unpatched; the
probe cannot tell [infer].

**What it does not show.** What doutc starts; a mapped address in a word (the patch of PDS data
placeholders in this template was not confirmed, and no case reads the scratch back).
