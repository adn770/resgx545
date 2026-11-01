+++
id = "E089"
claim = "A predicated br whose quad's instances disagree takes the whole quad where its top-left instance (instance 0) goes: p0 set on the even-x instances gives 4 in all 2048 pixels, p0 set on the odd-x instances or on instances 1-3 gives 7 in all 2048; when the quad agrees, each quad follows its predicate (1024 pixels 4, 1024 pixels 7); br.syncent and br.nosched give the same results as br, and br.synce and br.mon hang the job in the two predicates they were run on"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/branch.toml, probe divergent, a 64x32 fill whose pixel program sets r10 = 0, tests g25 (the instance's place in its quad) or g24 (its tile row) into p0, runs `p0 br #3` over two `or` instructions, then ors 4 into r10 for everyone, r10 as the pixel; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-branch"]
terms = ["SR.INST_NUM", "SR.TILE_Y_PIX"]
+++

**What runs.** r10 = 0, a test that sets p0, then `p0 br #3` (or `.synce`, `.syncent`, `.mon`,
`.nosched`) over `or r10, r10, #1` and `or r10, r10, #2`, then `or r10, r10, #4`. An instance
that branches ends with 4, one that falls through with 7. Twelve cases: p0 from g25 bit 0 clear
(instances 0 and 2 of each quad), from g24 bit 3 clear (a tile row, so uniform per quad),
from g25 bit 0 set (instances 1 and 3), and from g25 bits 1:0 nonzero (instances 1 to 3).

**Results.**

- Uniform per quad (g24 bit 3): `br`, `br.syncent` and `br.nosched` give 1024 pixels of 4 and
  1024 of 7, each quad as its predicate.
- p0 set on the even-x instances (0 and 2): 4 in all 2048 pixels with `br`, `br.syncent` and
  `br.nosched`.
- p0 set on the odd-x instances (instance 0 clear) or on instances 1 to 3: 7 in all 2048
  pixels with `br`.
- `br.synce` and `br.mon` hang the job in the even-x case and in the uniform case, and the
  context is lost with a timeout.

So when a quad disagrees, all four instances follow instance 0: taken when its predicate is
set, even if the others are clear, and not taken when it is clear, even if the other three are
set. The instances that fall through in a taken quad do not run the two `or`s: there is no
per-instance masking.

**Not shown.** `.syncent` and `.nosched` were only run on two of the predicates. The other two
disagreeing predicates were run with plain `br` only, and `.synce` and `.mon` were not run on
them. One run.
