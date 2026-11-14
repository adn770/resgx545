+++
id = "Q299"
question = "does a ZLS store whose extent runs past its buffer fault the job (E411's G 5 to 17 in a 16-page buffer), and what does a load pass store over overlapping tiles?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E411", "E465", "E991", "E996", "E1041", "E1051", "E1064"]
terms = ["CR_ISP_ZLSCTL"]
+++

Opened 2026-11-14 with Q298's retirement (answered by E1051, round 15 decision R15-6 (a), the lead
confirming). E1051 stored E411's faulting pitches where E465 puts their tiles once the buffer holds
them, without a fault, so E411's faults came from the extent past its 16-page buffer [infer,
E991]; that inference and what sgx-pipe's `zls` still refuses were never clauses of Q298 and are
carried here:

- whether a store past a mapped buffer faults the job (E411 faulted at G 5 to 17 in 16 pages, but
  its G 3 stored past them without a fault: E991, E1041), a planned fault, not safe class;
- a load pass over overlapping tiles (E996, E1041 and E1051 ran the store alone there);
- a NaN depth reaching an integer conversion (no route made one).

What would settle it: E411's G 5 row with a 16-page buffer (flagged class: a fault is expected);
E1050's pass at a pitch under the tiles across.

Narrowed 2026-11-14 (r16-zls, E1064). A load pass over overlapping whole tiles (64 x 32 G 0,
160 x 48 G 2) loads each tile's slot, passes each tile on its own and keeps in a shared slot the
tile visited last, for a depth load over E996's plane and a stencil load (H-OVL-PASS 4 of 4 held
out); a NaN kept from the load stores 0x00ffffff in format 1 and 0xffffffff in format 2 (H-NAN-SAT 5
of 5). sgx-pipe models both. Open: whether a store past its buffer faults (a planned fault, not
safe class) and a pass over overlapping tiles with edge tiles.

Status: open.
