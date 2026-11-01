+++
id = "Q281"
question = "do the three T3 address jobs that faulted (ad-tw64x64-L2e2, ad-tw64x64-L3e3, ad-st128x32-L3e2) complete and fit the address model when the texture buffer is larger than 64 KiB, and how large is the buffer the sampler may read"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E722", "E566"]
terms = ["T3.BITS19_18", "T3.BITS28_27"]
+++
E722: A4 is exact on the 13 jobs that completed, and the 3 jobs whose A4 extent is 86016, 87040
and 174080 bytes faulted (BIF fault 0x90002 at 0x3e017007, 0x3e02d002 and 0x3e018004) while the
largest completed job reads 65536 bytes. One reading fits (a 64 KiB buffer), none was measured. To
settle it: the same 3 jobs with the probe's texture buffer allocated at 512 KiB (a tool option, or
a larger scratch map), and one job whose extent is 0x10000 plus one dword to see where the fault
starts.

Status: open. Needed to close the model on levels 2 and 3 with scales.
