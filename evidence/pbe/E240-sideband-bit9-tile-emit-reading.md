+++
id = "E240"
claim = "A public Rogue PBE state description names a one-bit field tilerelative, which suggests bit 9 of our sideband word is tile-relative addressing; on a one-tile target our bit 9 clear still hangs the job, so we read bit 9 as marking an emit that counts against a PBE tile, which is a reading of E239's measurements and not a name"
unit = "pbe"
method = "comparison with public sources (C0206) and the one-tile and two-emit probes of probes/pbe/sideband.toml on the laptop with the linux fork and the debug option on, two runs (the second is the follow-up run)"
tiers = ["infer", "HW"]
date = "2026-11-01"
data = ["pbe-sideband", "pbe-sideband-followup"]
terms = ["SIDEBAND.BIT9", "SIDEBAND.PACKMODE"]
+++

**What was compared.** C0206 is the field `tilerelative` of a public Rogue PBE state description,
a one-bit flag. Its name makes tile-relative addressing a reading to test for our bit 9 of the
sideband word (the glossary's SIDEBAND.BIT9). It predicts that on a target of one tile, where the
tile offset is 0, a sideband with bit 9 clear would store the same image as one with it set.

**Results.** It does not. The probes pbe-sideband-0000-32x16, with bit 9 clear, and
pbe-sideband-0200-32x16, with it set, gave a hang for the first (job hung, context lost) and a
drawn tile for the second (135 dwords of 0x00ff8040 over 377 of 0xff203040), in both runs. The
two-emit probes of E239 add that a second emit of the same tile does not change the tile's image
but changes the next job's: the baseline triangle drawn after each such probe differed from its
clean image in 1977 to 2165 of 4096 places, according to the second emit's sideband, in both runs.

**Reading [infer].** Bit 9 marks an emit that the PBE counts against a tile: the only emit of a
tile without it never completes the tile (the hang), and an extra emit is carried out at the next
job's first tile. This is our reading of those two observations. The data do not show the PBE's
count itself; a probe that read the queue's state after emits with and without the bit would.

**Not shown.** Whether the public field and our bit are the same thing in a different guise:
only that tile-relative addressing does not explain the hangs on this core.
