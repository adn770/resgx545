+++
id = "Q297"
question = "what does the ZLS load pass (a depth or stencil load feeding the depth test and the store) do over edge tiles, with bit 19 set, with an integer stored format, and against a triangle depth other than 0.5 and 0.25 to 0.4166?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E467", "E664", "E831", "E977", "E995", "E1029", "E1040", "E1050"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE"]
+++

Opened 2026-11-14 with Q243's retirement (answered by E1040, round 14 decision R14-6 (a), the lead
confirming). Q243 asked where the load reads and what it does with an integer format, NaN,
infinity and equal depths: E977, E995, E1029 and E1040 decided every clause with held-out rows.
What sgx-pipe's `zls::pass` still refuses was never a clause of Q243's line and is carried here:

- a load pass over a target with edge tiles (E831's band is measured for the store without a
  load; E467's load and pass ran on whole tiles);
- bit 19 (the negated float) with a load: the loaded sign is cleared (E467) and whether it is
  re-negated did not run;
- a pass with an integer stored format: E977 and E1040 read the loaded dword as a float and the
  store by the floor rule, but the pass's compare and store were not modelled from them;
- a triangle depth other than 0.5 (E467, E411) and the ramps' 0.25 to 0.4166.

What would settle it: E467's load run at 34 x 18 with the dumps kept; a load with bit 19 under the
depth test never and less; E977's integer rows under less and never at another depth; the pass at
triangle depths over 0 to 1.

Narrowed 2026-11-14 (r15-zls, E1050). Over 34 x 18 edge tiles the pass tests E831's band against
the load and keeps the loaded depth and stencil past it (H-EDGE 1 of 1 each); bit 19 with a load
stores every depth negated, the kept load too (H-19-RENEG 2 of 2); formats 1 and 2 compare the
loaded float and store the floor rule (H-INT-PASS 2 of 2); the test is strictly less at 0, 0.75 and
1 (H-PASS-Z 3 of 4; at 0.125 the drawn count held and the flat plane stored 1 to 9 ulps below the
depth, Q200's plane error, post hoc). sgx-pipe's `zls::pass` models them.

Status: open.
