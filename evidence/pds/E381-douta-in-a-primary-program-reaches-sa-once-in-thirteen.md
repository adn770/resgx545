+++
id = "E381"
claim = "In the triangle's primary pixel program, sixteen douta writes reached the USE task's sa registers in one job of thirteen: markers C to attributes 16-31 arrived in sa16-sa31 in their third run, with sa0-sa15 holding markers B of a job three jobs earlier; in the other twelve jobs sa0-sa31 held one of two sets of values that other jobs had left (one the sa of the fill probe run just before, with sa0 = 0x00000002 in place of its first value), and pa0-pa15 held values that differ from job to job"
unit = "pds"
method = "probes/pds/douta-primary.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: douta_words.s as the 64x64 triangle's primary pixel program (state word 4 = 0x130004, room for 16 secondary attributes), its sixteen douta writes giving markers A, B (attributes 0-15) or C (attributes 16-31); pa_sa_dump.s as the pixel shader stores pa0-pa15 and sa0-sa31 to scratch; A and B alternating five times, C three times"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["pds-douta-primary"]
terms = []
+++
**Results.** All 13 jobs completed with the 1062 triangle pixels at the shader's colour.

| jobs | sa0-sa15 | sa16-sa31 |
|---|---|---|
| A runs 1-4, B runs 2, 4 and 5, C run 2: 8 jobs | set X: 0x00000002, then the temporaries of the last fill of the mov128 table run before | set X's |
| B runs 1 and 3, A run 5, C run 1: 4 jobs | set Y: 0x00000002, 0x00010001, 0, 1.0, 0.75, -0.375, 0, 1.0, -0.375, 0.75, 0, 1.0, then 0xd0d00303 | 0xd0d00303 |
| C run 3 | markers B (job 9's) | markers C, this job's |

pa0-pa15 held other values in every job, some repeating between jobs.

**Reading [infer].** A `douta` from the primary program does write secondary attributes, but the
task the program starts mostly reads attribute storage that other jobs filled: which storage a
task reads and which one a `douta` writes need not be the same. E125's markers and E142's inputs fit
this. Not shown: what picks the storage.
