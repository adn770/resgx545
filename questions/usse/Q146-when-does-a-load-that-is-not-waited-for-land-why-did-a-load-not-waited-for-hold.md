+++
id = "Q146"
question = "when does a load that is not waited for land, why did a load not waited for hold the loaded value after 40, 100 and 128 `nop` but not after 48 and 64, and in what order two loads and a `mov` to one register land"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E517"]
terms = []
+++

E517: a load not waited for is seen by a stad as landed at 40, 100 and 128 `nop` and not landed at
32, 48 and 64 (E478, E517); an ALU reader has no interlock (6 of 6, 0 to 48 `nop`); a later `mov` is
overwritten by the load (4 of 4).

What is open: the load's time (one sample per value), whether the loads of two registers or counters
land in a fixed order, and what a write that comes after the wdf of an earlier load does (the
control: the mov wins). To settle it: a timer read before and after each case and a series of many
runs per value.
