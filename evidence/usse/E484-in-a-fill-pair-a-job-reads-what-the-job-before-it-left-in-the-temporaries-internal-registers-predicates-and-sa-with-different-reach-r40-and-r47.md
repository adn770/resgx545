+++
id = "E484"
claim = "In a fill pair, a job reads what the job before it left in the temporaries, internal registers, predicates and sa, with different reach: r40 and r47 written by one job are read by the next in 7 of 7 reader jobs (2048 of 2048 pixels each) and still by a reader two jobs later, after a job that wrote no temporary, in 2 of 2; i0, i1 and i2 in 9 of 9; p0 and p1 in 96.3 to 100 percent of the pixels of 10 of 10 reader jobs; sa1, sa5 and sa7 written by one job are read by the next in 9 of 9 reader jobs (2048 of 2048), but after a job that wrote no sa the reader reads that job's pixel output instead of the sa it wrote two jobs earlier (3 of 3), as it does for an sa nobody wrote (2 of 2), so sa is kept for one job only; and 12 pixels (4 of each of the three values) of every one of the 18 jobs that wrote sa1, sa5 and sa7 show the sa value as their output instead of the colour"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/task-state.toml (4 probes: sa 29 cases, temps 18, predicates 20, internal 19; 86 fill cases, a writer fill then a reader fill in table order, as E373; the writer's colour 0xC01C0001, or 0xC01C0002 when it wrote no state, differs from every marker); two runs (the campaign, the dataset, and a whole-table probe.py run): the readbacks agree in all but the predicate counts, which vary by up to 11 pixels (below)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-task-state"]
terms = []
+++

**What runs.** A writer fill writes sa1, sa5, sa7 (0x5A5A0001, 5, 7), r40 and r47 (0x7E570040, 47)
and i0-i2 (0x1E570000 to 2) and p0/p1, ends with its colour; a reader fill, the next job, reads one
of them into its pixel (or, for predicates, the predicate as 0 or 1). Pairs: sa5 five times, sa1
and sa7 twice, sa6 (never written) twice, with and without a gap job in between that wrote no sa;
r40 five times, r47 twice, r40 after a gap job twice; i0-i2 three times each; p0 and p1 after
writers with p0 set and p1 clear (three and two times) and p0 clear and p1 set (three and two
times). One-job controls (mov sa5 then read, mov i0 then read) read their own value.

**Results.** sa: all 9 readers of sa1, sa5, sa7 read the marker in 2048 of 2048 pixels; the 3
readers after a gap job read 0xC01C0002 (the gap job's colour); the 2 readers of sa6 read
0xC01C0001 (the writer's colour). The writer jobs (11 of the sa probe and 7 of the temps probe, the
ones that wrote sa) show 2036 pixels at the colour and 12 at the sa values, 4 each of 0x5A5A0001,
0x5A5A0005 and 0x5A5A0007; the writers that wrote no sa show 2048 at the colour. temps: 7 of 7
readers read 0x7E570040 or 0x7E570047 in 2048 of 2048 pixels, and 2 of 2 readers after a gap job
read 0x7E570040. internal: 9 of 9 read 0x1E57000n. predicates (campaign counts): p0 after p0 set: 1
in 2048 pixels, 3 of 3; p1 after p1 clear: 0 in 1982 and 1986 (1 in 66 and 62); p0 after p0 clear:
0 in 1973, 1977, 1981 (1 in 75, 71, 67); p1 after p1 set: 1 in 2033 and 2033 (0 in 15). The
probe.py run differs only in these counts, by up to 11 pixels (the pixels reading 1 in the five
readers that differ: 72, 72, 71, 60 and 68 against 66, 62, 75, 71 and 67; the 15 of the two p1
readers after a set p1 are the same). Those counts, 66, 62, 75, 71, 67 and 15 and 15 in the
dataset's run, are not all multiples of four, so those pixels are not whole 2 x 2 quads; the pixel
positions were not kept (Q125).

**What it shows.** [HW] In a fill pair on the render node, two temporaries, r40 and r47 (the fill
had 48 temporaries; the others were not read), and the internal registers are not cleared between
jobs, the predicates are kept by 96 to 100 percent of the instances (E477 has 98 to 99), and sa
shows its last write only to the next job: a job in between that writes no sa replaces it by its
output, the reading of E380. [HW] p0 and p1 here and p0-p3 in E477 agree. [infer] None of this is a
measurement of EDM tasks (the firmware toolchain asked about those): it is the persistence of a
client fill between two fills on the same render node, a proxy; the firmware may clear or write the
same registers between its own tasks. The 12 odd pixels are not explained (Q129).

**What it does not show.** Retention across more than two jobs for sa, i0-i2 and p0-p1 (only a gap
of one job was run, for sa and r40); which instances keep the value (the pixel positions were not
kept); an EDM task's persistence.
