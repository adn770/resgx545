+++
id = "E549"
claim = "On the module built from the reworked phase 11.29 series (tip 3d9b8bdefe94: the code page read-only for the EDM, the stricter verifier, 6 of 6 series checks PASS, KUnit 106 debug off and 172 on), the firmware tasks of E531 to E534 behave as before: the null wrapper, which only tail-calls the closed task from a page the EDM can now only read, is fetched and runs (ticks 994 Hz, fill and triangle exact, no fault), so the EDM fetches code from a read-only page; the memory-only wrapper stores its marker (the tick's event words as in E532), ldr reads CORE_ID, CORE_REVISION and CR_TIMER (the first two equal the host's), the same-value str (X0, X1) lands as before, and one repeat of the 9b matrix on 0x0814 and on 0x0a78 (17 cases each, the discriminating value pair) reads the same (L, H) per case as E534, 34 of 34 as predicted"
unit = "usse"
method = "as E531 and E534, on the module srcversion 5AD04F33F6BCDA7B880E238 (vermagic 7.3.0-resgx545), tool = overlay 11.29 tools/fwtask (blobs null, mem, ldr, x9b_r1, x9b_r2 assembled and verified by the tool and by the kernel's verifier), predictions frozen (sha256 38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183). Stages in order, each after the previous passed: unarmed deploy (p1129-recheck-s1b-unarmed; the first attempt s1-unarmed stopped in the tool before any task because the SGX had not been loaded after the module reload: kept), null (s2), mem (s3), ldr (s4), X0 and X1 on 0x0814 (s5, 12 runs), 9b with one repeat and one value pair per register (s6r1, s6r2, 17 cases each), then reset and the unarmed gate again (s7-post-stock). Only str on 0x0814 and 0x0a78; no clock-gate register; no trc_hazard; no item 11, 12 or 13. A firmware task, not a client pixel task. Run-keeping notes: the fork tip 3d9b8bdefe94 in the nine env.toml files was set by hand, because the tool could not find the fork; the SGX was loaded and booted by hand after the module reload; s6r1 and s6r2 were run by a thin driver, drive9b.py, that calls the tool's 9b stage with one repeat and one value pair per register, not by the stage entry point; the first s1 attempt stopped in the tool (a KeyError in tick_rate, the SGX not booted, no task ran), its directory holds the kernel log only"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-recheck"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++

**Read-only code page.** [HW] With the code page mapped read-only in the EDM's page directory
the null wrapper is fetched and the closed handler runs after it: 994.4 Hz, miscinfo answered,
fill (0 of 2048 pixels) and triangle (0 of 4096) exact, BIF fault 0, EVENT_STATUS2 0x400 (E531:
998.0 Hz with the page writable). The firmware fetches code from a page it cannot write, and the
wrapper's tail-call ran without a fault. The unarmed gates read 1013.9 Hz before the stages
(s1b) and 963.4 Hz after them (s7), the fill and triangle exact again.

**Agreement with 11.29.** s3: slot (pa0, pa1, pa2, marker) = (2, 0x2000000, 0x1061a70,
0x5a5a1129), equal to p1129-s3b-mem; the stage passed and the prediction row about pa1 failed
again (S3_mem false), as in E532. s4: CORE_ID 0x01150000 and CORE_REVISION 0x1000d equal the
host's; CR_TIMER read 0x482c66a2 here and differs per run. s5: 12 of 12 as predicted. 9b, one
repeat and one value pair per register (0x0814 as R1: A = 88666, B = 42405; 0x0a78 as R2: A = 21,
B = 42), 17 cases each, 17 of 17 as predicted on each register, 34 of 34. Case by case the (L, H)
is that of E534 (p1129-s6r1b pair 0 for 0x0814, p1129-s6r2 pair 0 for 0x0a78): X2 at d = 0, 1, 2,
4 and 16, X3, X4, X5, X9, X10 and X11 (B, B); X6 at d = 0 and 4 (A, B); X0 and X1 (A, A). X7 (C, C)
and X8 (the other register's own value, then B) carry the classifier's generic label "other", as
in E534; their verdict is `predicted_ok`, the match to the frozen row.

**How the run went.** The first s1 attempt stopped in the tool (a KeyError in `tick_rate`, the SGX
not booted after the module reload, no task ran) and is kept with its kernel log only; the SGX was
then loaded and booted by hand and s1b onward ran as listed. The fork tip 3d9b8bdefe94 in the nine
env.toml files was set by hand, because the tool could not find the fork. s6r1 and s6r2 came from
the thin driver `drive9b.py`, which calls the tool's 9b stage with one repeat and one pair. The
series check of the three commits on this tip passed under qemu: 106 KUnit cases debug off on each,
157, 164 and 172 debug on (E549's module is the one built from the third).

**KUnit at module load.** [infer] The author saw one failure in each of two suites when the
module was loaded on the laptop: gma500_sgx_render (test_pb) and gma500_sgxfive_debug
(test_pb_small), both "Expected pt != NULL". The author read it as an allocation failure on the
laptop's 2 GB after the builds. The module-load KUnit output was not kept in the logs or in the
data, so the failures and that reading cannot be checked here; the qemu series check ran the same
suites and passed them (render 20, debug 20 on the tip). Whether it is a real failure risk is
open as Q167.

**Not shown.** Anything beyond one repeat per register; items 11, 12, 13 and trc rows (not run);
that a store through a base other than the results page is refused (verifier tests, not hardware);
the cause of the two KUnit failures at module load (Q167).
