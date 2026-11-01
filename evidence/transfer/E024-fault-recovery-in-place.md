+++
id = "E024"
claim = "A job that faults on the laptop is detected through the BIF fault; the kernel stops and resets the core and boots the firmware again in place, the EDM answering the kick within 152 to 684 µs; the faulting job's wait fails 111 ms after its submit, its context is lost, a job queued on another context runs again, later jobs run exactly, and the third fault from a file within a minute bans the file"
unit = "transfer"
method = "sgxfive-test on the laptop with the debug option on, on a fresh boot (probes/render/client-jobs.toml): isolation (nine cases), tri --fault, then tri -n 2 and a fill; the kernel log after isolation, after tri --fault, and after the last two"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-client-jobs"]
terms = ["CR_BIF_FAULT", "CR_EVENT_STATUS", "CR_SOFT_RESET"]
+++

**What runs.** Three isolation cases fault on purpose: a fill to an address only another VM
maps, a fill to another such address queued just ahead of a good fill on a second context,
and a write to a read-only mapping. The next case makes no fault; it checks that the file is
banned. `tri --fault` unmaps the scene's stream page before a render, from a new file.

**Results.** All nine isolation cases print PASS. The cases check more than their names:
the faulting fill's wait returns -EIO and its target stays untouched, a later submit to its
context returns -ECANCELED, the surviving and re-run fills hold their colour, and after the
third fault both creating a context and submitting to a context that never faulted return
-ECANCELED (sgxfive-test.c, cmd_isolation). The faulting job's wait returns its error 111 ms
after the job was submitted; the test's limit is 300 ms.

The kernel log shows four faults, three from isolation and one from `tri --fault`. Each
is a BIF fault (status `0x90020`, `0x80020` or `0x90008`) at the faulting address, logged as
"stalls job N, recovering". The kernel stops the core, logs EVENT_STATUS `0x20000000` with
`0x440` (transfer faults) or `0x480` (the render fault), and kicks the EDM again. The EDM
answers within 684, 203, 164 and 152 µs, upper bounds (E017). The first recovery, 684 µs,
is close to the first boot's 644 µs (E022), and its stop line counts 46 events against 0 or 1
in the others. From the fault line to "EDM up", the log spans 19 to 27 ms; these are printk
times, so the figure is only indicative. The third fault logs "3 faults within a minute, file
banned".

The faulting render fails with "context lost" (EIO), and `tri --fault` exits 1, as the
table expects. None of its target's pixels matches the reference, and its first pixel still
holds the sentinel. The two renders and the fill after it are exact (E023, E022).

This does not show the hang (timeout) path, other fault kinds, or how the core behaves
without recovery. Every fault in this run was recovered.
