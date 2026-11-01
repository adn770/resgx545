+++
id = "Q102"
question = "what state does a completed job with VDM state word 1 bits 11:9 = 7 leave that makes the next such job hang, and why does the reset after a hang clear it?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E060", "E185", "E299", "E413"]
terms = ["VDM_STATE1.BITS11_9"]
+++

Jobs with bits 11:9 = 7 alternate strictly between completing and hanging (E413, 55 of 55 jobs),
across controls between them, with or without the pixel readback; values 3 and 5 hang sometimes. A
hang's reset restores the state a completed job changes.

What is open: where the state sits (the VDM, the TA, the MTE, the USE partitions), whether a fresh
boot starts a series with a completed job, whether a longer cycle governs 3 and 5, and what a
partition count of 7 (a field of three bits) does that 3 and 5 do less. To settle it: the
regtimeline snapshots of the VDM, TA and DPM registers around a completed and a hung job of the
series, the same series on a fresh boot, and series of 3 and 5 of fifty jobs.
