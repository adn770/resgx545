+++
id = "Q109"
question = "do page directory entries whose page-size field (bits 3:1) names 16 KiB to 4 MiB translate on the hardware, and with which address mask and which table layout?"
unit = "bif"
kind = "hw"
value = "low"
phase = 11
evidence = ["E021", "E151"]
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