+++
id = "E264"
claim = "In the primary pixel program of a 64x64 triangle, a movs to mr, slc, douts or ir0 before the iteration leaves every pixel as the control's and the render completes; mr01 reads 0 after the movs to mr, and ir0 still reads the tile position after the movs to ir0; a movs to doutc faults the job (BIF status 0xd0400, address 0x0401f030)"
unit = "pds"
method = "probes/pds/task-inputs.toml (pds-task-inputs-primary-ports) on the laptop, linux fork with the debug option on: pds_iter_if.s as in E262, with one movs of the data's row 2 to the port before the iteration, or that movs and then a tstz-predicated choice of the iteration on mr01's low dword or on ir0; every pixel read back; the fault from the kernel log the runner kept (pds/task-inputs/kernel.log); one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pds-task-inputs"]
terms = ["PORT.DOUTC", "CR_BIF_FAULT"]
+++

**Results** (1062 triangle pixels each):

| case | outcome |
|---|---|
| control (no port write) | completes, every pixel the coordinate set |
| `movs mr, ...` | as the control |
| `movs slc, ...` | as the control |
| `movs douts, ...` | as the control |
| `movs doutc, ...` | job faulted, context lost |
| `movs ir0, ...` | as the control |
| `movs mr, ...`, then `mr01`'s low dword zero? | true on all 1062 |
| `movs ir0, ...`, then `ir0` zero? | true on the 48 pixels of tile (0, 0) only |

The `doutc` fault is logged as status 0xd0400 at 0x0401f030, where the PDS's own load and store
faults (E145) and the jumps of E260 have status 0x92000 or 0xd2000.
[infer] Another requestor, so `doutc` starts something outside the PDS that reads memory the job
did not map; the status suggests it, it does not show it. In a fill's secondary
program the same port made the fill's USE task fault storing to page 0.
