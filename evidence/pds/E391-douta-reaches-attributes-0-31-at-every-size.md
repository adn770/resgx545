+++
id = "E391"
claim = "A fill's secondary douta reaches sa0-sa31 at their own index and never sa32-sa63, whatever the secondary attribute size in the background object's dword 1 (bits 24:18 at 0, 1, 2, 4 and 8 rows): sixteen markers to attributes 0-15 and to 16-31 arrive in all 20 jobs, to 32-47 and 48-63 in none, and nowhere else, two runs"
unit = "pds"
method = "probes/pds/attribute-room.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: douta_words.s as a 64x32 fill's secondary program, sixteen douta per job to attributes 0-15, 16-31, 32-47 or 48-63 (control bits 19:8), markers naming run, size and attribute; sa64_dump.s storing sa0-sa63; bg:1 poked to (rows << 18) | 0x30000; 5 sizes x 4 sets, two runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-attribute-room"]
terms = []
+++
**Results.** At every size the 16 markers of attributes 0-15 and of 16-31 are in sa0-sa15 and
sa16-sa31; those of 32-47 and 48-63 are in no register of sa0-sa63 (40 jobs). Registers a job does
not write keep earlier jobs' markers.

**Correction 2026-11-15:** "Never sa32-sa63" and "those of 32-47 and 48-63 are in no register of
sa0-sa63" were read from sa0-sa31 only: the probe of this run printed the first 32 changed scratch
dwords, and every one of its 40 jobs ends `scratch 32 more changed` (raw.txt), so sa32-sa63 were
stored and not read (E1096's "What it does not show"). E1104 repeated the 40 jobs with the same
programs and pokes on t24, whose probe prints all 64 (`--scratch-show 64`): the markers of
attributes 32-47 and 48-63 are at their own sa in sa32-sa63 at every size, 0 to 8 rows, both runs,
as those of 0-31 are in sa0-sa31. The fill's douta reaches attributes 0-63, not 0-31; the readings
of sa0-sa31 stand.
