+++
id = "Q028"
question = "what does a faulting job leave wedged when the kernel does not recover, and which reset steps does the recovery need?"
unit = "transfer"
phase = 9
evidence = ["E024"]
terms = []
+++

On the laptop a job that faults is detected through the BIF fault, the kernel stops and resets
the core, boots the firmware again in place, and later jobs run exactly (E024). What that
recovery puts right is not shown: whether a fault wedges the 3D pipe, the EDM's command loop or
both, and which of its steps (the core reset, the firmware boot, restoring the transfer
contexts and the client command queues) a later job needs.

To settle it: a debug switch in the kernel that leaves a fault unrecovered, then a faulting
job followed by jobs on the same and on other contexts, reading the EDM's and the core's state
after each (the debugfs `kreg` file and `miscinfo`); then the recovery steps added back one at a
time until later jobs run again.
