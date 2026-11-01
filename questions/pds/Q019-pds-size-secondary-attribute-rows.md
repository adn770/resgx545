+++
id = "Q019"
question = "what does the secondary attribute size (bits 24:18 of dword 1 of the background object) limit, given that all sixteen douta words reach sa0 to sa15 with 0, 1 and 4 rows, or does the task take its size from elsewhere?"
unit = "pds"
phase = 7
evidence = ["E125"]
terms = []
+++

The fill's secondary PDS program passes sixteen values to the task it starts with sixteen `douta`
writes, and the task stores `sa0` to `sa15` (E125). The background object's dword 1, bits 24:18,
was poked to 4 rows (0x130000), 1 row (0x70000) and 0 rows (0x30000), one job per case.

- 4 rows: markers A and markers B each read all sixteen markers in order.
- 1 row: markers C read all sixteen C markers, not only `sa0` to `sa3`.
- 0 rows: markers B read all sixteen B markers in order.

The same in both runs (the second is the follow-up run). So no value tried makes fewer than
sixteen words arrive, and what the field limits is not shown. The bits were poked, not read back.
Attributes a job does not write read what earlier jobs left, and in one case which job's values
differ between the runs (job C of the persist probe, `sa1` to `sa7`), so the task's registers are
not cleared between jobs.

Not tried: a task that reads more than sixteen attributes, or a `douta` write whose control word
names an attribute past 15, with the size at 0, 1 and 4. Two readings are open: the field sizes the
attribute store the task is given and the hardware does not stop a task that writes past it, or the
task takes its size from another word (the task's own state, the DOUTU words) and the field is
read by something not exercised here.

To settle it: a fill that writes 32 or 64 attributes by `douta` (the attribute index is bits 19:8 of
the control word) and stores them all, at 0, 1, 2, 4 and 8 rows; read the registers back from the
task and compare which attribute indices arrive at each size. Run it twice, since what stays in
the attributes across jobs differs between the runs. Read `bg:1` back after the poke if the
interface allows it.
