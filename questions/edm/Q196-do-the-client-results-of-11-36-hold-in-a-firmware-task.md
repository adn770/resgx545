+++
id = "Q196"
question = "do the client results of 11.36 for the compare and the high word of ima32 (E595, E597), the predicated register moves and ba (E596) and the narrow memory forms (E598, E599) hold in a firmware (EDM) task"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E595", "E596", "E597", "E598", "E599", "E601", "E600"]
terms = []
+++
The firmware-task verifier refuses `ima32` with the extra operand i0 (unknown form), `p0 mov r, r`,
`!p0 mov r, r` (unknown form), `p0 ba` and `!p0 ba` (form not allowed), `ldab`, `ldaw`, `stab` and
`staw` (unknown form), `.fetchN`, `.bpcache`, `drc1` and a computed base on `ldad`, so those forms
were run in fills only: 256 of 256 compares, 300 of 300 high-word jobs, 74 of 74 predicated jobs and
48 of 48 narrow jobs matched the models. In a firmware task the forms the verifier accepts were run:
`p0 mov r, #n`, `!p0 mov r, #n`, `p0 br` and `!p0 br` (E601, 72 of 72) and the
one-`wdf`-over-many-`ldad` sequence (E602, 21 of 21, sufficiency only). The compare's `xor.testtanz`
of i0, which the verifier accepts, was not run.

To settle it: loader rows for the forms (a separate track), then the tables of E595 to E599 as
firmware tasks of ours: a task that executes the form for a per-job value from the page and stores
the result, judged as the fills were. Nothing about the firmware tasks is claimed from the fills.

Round 12 cites: E600 (xor.testtanz with an immediate or a limm operand on rV holds in a firmware
task, 7 of 7 jobs).
