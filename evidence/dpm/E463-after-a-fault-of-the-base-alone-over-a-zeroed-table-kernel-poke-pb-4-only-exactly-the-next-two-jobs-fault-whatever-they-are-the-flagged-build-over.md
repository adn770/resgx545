+++
id = "E463"
claim = "After a fault of the base alone over a zeroed table (kernel poke pb:4 only), exactly the next two jobs fault whatever they are (the flagged build over zeros 20 of 20, the plain triangle 8 of 8, the base over the kernel's table 4 of 4) and the third completes (8 of 8), with a debugfs GPU reset before each job or none (16 of 16 sequences, the same outcomes); a fault from an unmapped scene stream leaves nothing (16 of 16 followed by an exact job)"
unit = "dpm"
method = "probes/dpm/ctx-table-fault-order.toml (ctx-table-fault-order.sh) and probes/dpm/ctx-table-fault-chain.toml (ctx-table-fault-chain.sh) on the laptop (direct cable): sequences of sgxfive-test tri jobs (64x64, alias_ctx_rw on) of the flagged build over a zero table (Z), the base alone over zeros (B) or over the kernel's table (K), the plain triangle (P) and an unmapped-stream fault (F), each step after a debugfs GPU reset or with none, two runs of each sequence, the BIF registers 0x0c00-0x0cff read after each step"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["dpm-ctx-table-fault-order", "dpm-ctx-table-fault-chain"]
terms = ["hw_pb_desc.page_table_base", "hw_pb_desc.pb_flags"]
+++

**What runs.** E453 saw the flagged build over zeros (kernel pokes pb:0 = 0x1 and pb:4 = the
scratch address) fault only after a run that had faulted, and the plain health triangle after the
last faulted run fault too. Two scripts run sequences of 64x64 `tri` jobs (a render context for
64x64, debugfs `alias_ctx_rw` set) of these kinds: Z, the flagged build over a zero-filled scratch
table (16 scratch pages, `--scratch-at` 1 MiB above the allocator's address, as E453); B, the base
alone over the zeros (`pb:4` only); K, the base alone over the table the kernel builds before a job
(`--scratch-file`); P, the plain triangle; F, an intended fault (`tri --fault`, the scene's stream
page unmapped). Each step is preceded by a debugfs GPU reset (`reset`), and every sequence is also
run with no reset between its steps (`norst`); two runs of each. `dpm/ctx-table-fault-order` (84
steps): Z P Z P Z P, F Z P Z P, F P P Z and Z F Z F P Z. `dpm/ctx-table-fault-chain` (64 steps): B
Z Z P, Z B Z P, B P Z and B K Z K P.

**Results.**

`fault-order`: the 16 F steps all faulted (job faulted, context lost) and each was followed by an
exact job: F then P 8 of 8, F then Z 8 of 8. All 36 Z steps and all 32 P steps were exact, after F,
after Z, after P and with no reset. The kernel log has 16 BIF faults and no "recovery failed".

`fault-chain`:

| step relative to the B | jobs | faulted | exact |
|---|---|---|---|
| before it (a Z first) | 4 | 0 | 4 |
| the B itself | 16 | 16 | 0 |
| the next job (Z 8, P 4, K 4) | 16 | 16 | 0 |
| the one after (Z 12, P 4) | 16 | 16 | 0 |
| the third after (P 4, K 4) | 8 | 0 | 8 |
| the fourth after (P) | 4 | 0 | 4 |

The 16 sequences are the 4 shapes, with and without the reset, twice. Every B faulted and every Z,
P or K inside the two jobs after it faulted, the same with a reset before each step as without; a K
exact in its last place (4 dwords changed in the scratch, as E453) and a plain triangle after it
were exact (4 of 4 each). The kernel log has 48 BIF faults (= 16 sequences x 3, all BIF fault status
`0x90004`, at 0x10000051 in 44, 0x10000052 in 2 and 0x10000053 in 2), and 31 lines "SGX recovery
failed: -110" with 31 "render context cleanup failed". The steps of the 8 sequences with a reset
show it: the B's recovery failed, the next job's recovered, the second job's failed again (8 of 8
sequences). The same per-step counts of the sequences without a reset are wrong in output.txt (each
step's mark was found in the first run's log, a label repeated), so kernel.log is authoritative for
them, the 16 failed recoveries of the 8 sequences with a reset account for half of the 31; the
other 15 are in the 8 without. A Z faulting wrote 1058 dwords of the scratch (as E453), a faulting
K and P none, a B 2.

**What it shows.**

- The follow-on faults come from the B fault, not from any fault: the 16 F faults (stream unmapped,
  recovered each time) leave nothing, and the flagged build over zeros is exact whenever no B came
  before it (36 of 36 Z in fault-order, 4 of 4 in fault-chain) [HW].
- After a B fault exactly two further jobs fault, whatever they are: Z (20 of 20), a plain triangle
  (8 of 8) and K (4 of 4), so a plain triangle faults after it as well as the flagged build; this
  fits the plain-triangle fault of E453's health check, which followed a base-only run over zeros
  [infer]. The third job completes (8 of 8) [HW].
- A debugfs GPU reset between the jobs changes nothing: the same 3 faults follow with and without
  it (8 sequences with and 8 without a reset, all agree) [HW]. What the B fault leaves is
  therefore not cleared by that reset; the failed recoveries (-110, the B's and the second job's)
  fit a state kept by the driver or the bus interface for two jobs [infer].

**What it does not show.** What the state is and where it lives, why the first job after the B
recovers and the second does not, whether a B with a recovery that succeeds would leave it, and the
role of the zero table beyond making the base alone fault.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (the installed module file and the loaded module, read from /sys/module,
were equal; the run prints both and stops if they differ), sgxfive-test sha256
fa7592a6170712ed0080066c56602304607ed31ec608afd66441a597587675a7 (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable.
kernel.log is authoritative for the logged counts: the driver lines of output.txt for the runs
without a reset repeat earlier runs' lines.
