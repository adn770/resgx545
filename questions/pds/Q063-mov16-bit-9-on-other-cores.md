+++
id = "Q063"
question = "what does bit 9 of a mov16 or mov32 special source select on the rest of the SGX family, when on SGX545 it only makes mov16 read 0?"
unit = "pds"
phase = 11
evidence = ["E128"]
terms = []
+++

On SGX545 bit 9 (.1) of a special source makes a mov16 read 0 and a mov32 read the same register as
.0 (E128). SGX545 alone has two PDS pipes, so the bit may name the other pipe's registers, another
core's, or 64-bit specials [infer].

What is open (pds_isa.md §7, item 12): what the bit selects on other cores.

To settle it: the same special-source probe on a one-pipe core (SGX540 on a PandaBoard, SGX530 on an
N950), to see whether its special fields run at stride 1, and on an MP part (SGX544MP2) for the
cores. This needs other hardware than the laptop.
