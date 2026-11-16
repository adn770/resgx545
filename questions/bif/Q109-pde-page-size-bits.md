+++
id = "Q109"
question = "do page directory entries whose page-size field (bits 3:1) names 16 KiB to 4 MiB translate on the hardware, and with which address mask and which table layout?"
unit = "bif"
kind = "hw"
value = "low"
phase = 11
evidence = ["E021", "E151", "E1117", "E1118", "E1119"]
terms = ["CR_BIF_DIR_LIST_BASE0"]
+++

A page directory entry has a valid bit (bit 0), a page-size field in bits 3:1 (4 KiB, 16 KiB, 64
KiB, 256 KiB, 1 MiB, 4 MiB) and the page table's address in bits 31:12 (doc/specs/hw_spec.md section
4, from the driver headers, not from a run). No record shows a run with an entry of a size other
than the smallest.

Open: whether the hardware translates a page of each larger size, how a larger page changes the page
table's layout and the address bits the table uses, and what the bus interface reports for a size
field it does not take. To settle it: a new kernel switch in the linux fork (so a run needs a fork
change) that builds one directory entry of a client with a chosen size field over a table laid out
for that size, then `fill` and `copy` aimed at the pages it maps, compared with the same buffer
mapped by 4 KiB entries, and the bus interface's registers read after a job that crosses the page's
end.

Measured in round 30 (r30-pde, fork r30-kernel 8bc0877e8603, module 7CE8E38E): the fork's debugfs
`vm_pde_*` mapped one client 4 MiB slot through a PDE of each code 0 to 7 over a tagged region
the driver owns. The size field is not taken: codes 1 to 5 over dense tables read and wrote the
pages a 4 KiB walk names, never the large page (E1117, H-4K 15 of 15 frozen rows); the PDE's bits
11:4 do not offset the table and a misaligned entry is walked as a 4 KiB one (E1118); the
unnamed codes 6 and 7 neither fault nor stall and walk 4 KiB entries too (E1119). The frozen rule
(`score.py q109`) prints RETIRE.
