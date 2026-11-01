+++
id = "Q002"
question = "is the laptop's SGX core clock 399.0 MHz rather than the DDK's 400 MHz, or do TIMER and the EDM tick run from a reference other than the core clock?"
unit = "edm"
phase = 3
evidence = ["E009"]
terms = ["CR_TIMER", "host_ctl.edm_ticks"]
+++

The DDK assumes a constant 400 MHz (`SYS_SGX_CLOCK_SPEED`, sgx545-ce `sysconfig.c:48`) and
sets the EDM tick to 400000 core clocks (HostCtl dword 6). Against an NTP-checked clock the
tick runs at 997.46 Hz and `TIMER` at 24.9366 MHz (E009): both give 398.99 MHz, if the tick is
dword 6 core clocks and `TIMER` counts core clocks divided by 16. Neither assumption is
measured.

Settling it needs a third view of the core clock: the tick with a different dword 6 (does the
rate scale as 1/dword 6?), and a timed workload whose cycle count is known, such as a USSE loop
of a fixed number of instructions timed against the host's clock. The only consequence for the
driver so far is the length of the EDM tick (1.0025 ms instead of 1 ms) and of the DDK's
`SGXWaitClocks` delays.
