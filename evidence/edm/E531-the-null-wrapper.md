+++
id = "E531"
claim = "A firmware (EDM) task of our own runs: with the start dword of PDS #13's general slot (instruction index 6, E146) retargeted at load to a page of our code at the kernel code heap + 0x20000 (index 0x4000), a 3-instruction wrapper that only jumps to the closed task the slot used to start (mov pclink, limm; lapc, the index taken from the replaced CODE_WORD record) left the EDM as it was in the one run that finished its evaluation (p1129-s2b-null: ticks at 998.0 Hz, miscinfo answered, a 64x32 fill exact, 0 of 2048 pixels differing, a 64x64 triangle exact, 0 of 4096, no BIF fault, EVENT_STATUS2 0x400) and in the gate of the earlier attempt (p1129-s2-null: the same fill and triangle exact, 994.2 Hz)"
unit = "edm"
method = "on the laptop (direct cable): linux fork tip d614af574cc6 (6ee9501832af plus three debug-only commits), module srcversion 7ED723C25D78D7FCB3C08C1 installed and loaded, as printed by the tool; tools/fwtask/run_stage.py, stages 1 and 2. Task setting: own_arm slots=0x1 entry=0 trc=8 trc_hazard=0 (the general slot only, the stock allocation of 32 temporaries), blob null (asm/fwtask/null.s, 50 bytes, sha256 e3ea807a4200016e77e80851dd92da038a247e8a5244deaca80e35b5bbccb810), load then boot, no job queued before the gate, no register written. Stage 1 (stock, own_arm off): p1129-s1-unarmed (its gate returned no output and the stage was not a pass) and p1129-s1b-unarmed (gate exact, 996.2 Hz). Stage 2: p1129-s2-null (arm and gate as above, then no verdict file: the tool stopped; kept) and p1129-s2b-null (the whole stage, verdict S2_null true). Not falsified. The predictions (tools/fwtask/predictions.toml, sha256 38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183) were frozen before p1129-s2b-null and before every run that could str (no str is in null, mem or ldr; the first run that records the hash is s2b, and the first that could str is s5); p1129-s1-unarmed, p1129-s1b-unarmed and p1129-s2-null ran before the file existed (the hash is empty in their env.toml), so for those three runs the prediction is the design plan, not a frozen row. The tool's files changed between stages: env.toml names a tool_sha256 per run (six values over the 16 runs of the phase) and the landed tools/fwtask are those files as they were after the last run, with paths made relative to the tree, so their hash is none of those. The verifier of our code that these runs used is the kernel's, in module srcversion 7ED723C25D78D7FCB3C08C1; a review of the fork commits found bypasses in it afterwards, fixed in later fork commits. The tasks that ran are ours and contained none of the forms that bypassed it, so the runs are not invalidated; the fixed verifier was not used for them, and once the rebuilt module is rechecked these tasks must pass the new verifier (reported with the fork commits, not here). A firmware task, not a client pixel task"
tiers = ["HW"]
date = "2026-11-08"
data = ["firmware-tasks-null-wrapper"]
terms = ["Event Data Master (EDM)", "CR_EVENT_OTHER_PDS_EXEC"]
+++

**What ran.** Four runs, each a fresh load and boot of the firmware: two of the unarmed stock
firmware (stage 1) and two with the null wrapper armed (stage 2). The only difference from the stock
buffers is the PDS #13 start dword of slot 0: our index 0x4000 with the addend of the record (CBASE
15, TRC 8, E003). The closed bytes are untouched; the jump to index 6 is by the index the replaced
record states (E146), written by the kernel into a `limm` of our code, not in our source.

**Results.** [HW] The code page is fetched, the retargeted word works, and the closed handler runs
after our three instructions. In p1129-s2b-null: ticks at 998.0 Hz, `miscinfo` answered, fill and
triangle exact with the wrapper in the path of their events, no fault, `EVENT_STATUS2` 0x400,
`HostCtl` dword 12 and `USE0_SERV_EVENT` advancing over three reads. The arm records of all the runs
of the phase with a wrapper armed show 964.0 to 999.3 Hz (the stock runs 996.5, 996.2 and, after the
reset of E533, 971.6 Hz), so the wrapper's rate is not told from the stock one by this phase. 2 of 2
gates passed with the wrapper armed; 1 of 2 stock gates passed (the other returned no output).

**Not shown.** That nothing else changed (one fill and one triangle per run); anything of a task
that does more than jump; a client job whose events pass through the wrapper in any number.
