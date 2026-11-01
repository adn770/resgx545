+++
id = "E010"
claim = "The microkernel's register loads and stores name 191 distinct registers, with 183 read sites and 421 write sites; it writes EVENT_HOST_CLEAR at 34 sites, EVENT_HOST_CLEAR2 at 4, BIF_CTRL at 4, and no BIF directory-list base"
unit = "firmware"
method = "the cut ukernel image (firmware-images) disassembled with usse-dis and its register load and store immediates counted with regtouch.py, names from sgx545-ce's sgx545defs.h"
tiers = ["RE"]
date = "2026-10-30"
data = ["firmware-boot-path", "firmware-images"]
terms = ["CR_EVENT_HOST_CLEAR", "CR_EVENT_HOST_CLEAR2", "CR_BIF_CTRL", "CR_BIF_BANK0", "CR_BIF_BANK_SET", "CR_SOFT_RESET", "CR_CORE_ID", "CR_CORE_REVISION", "CR_EVENT_TIMER"]
+++

The EDM reaches SGX registers with load and store instructions whose immediate is a dword
register index (offset = index x 4). Over the whole microkernel, firmware-boot-path counts 191
distinct indices, 72 of them read and 140 written, at 183 read sites and 421 write sites;
`sgx545defs.h` names 21 of the 191.

Among them: `CORE_ID` and `CORE_REVISION` are read once each; `SOFT_RESET` is written at 2
sites; `EVENT_STATUS` is read at 21 sites and written at 6, `EVENT_STATUS2` read at 5;
`EVENT_HOST_CLEAR` is written at 34 sites and `EVENT_HOST_CLEAR2` at 4, and neither is read;
`EVENT_TIMER` is written at 2 sites; `0x0a68` and `0x0a6c` (`EVENT_OTHER_PDS_EXEC` and `_DATA`)
at 1 each. In the BIF, `BIF_CTRL` is read at 2 sites and written at 4, `BIF_BANK_SET` read and
written at 4 each, `BIF_BANK0` read at 5 and written at 2, and the requestor bases
`BIF_TA_REQ_BASE`, `BIF_3D_REQ_BASE` and `BIF_ZLS_REQ_BASE` written; no index falls on
`BIF_DIR_LIST_BASE0` (`0xc84`) or `BIF_DIR_LIST_BASE1..15` (`0xc38`-`0xc70`).

These are the statically named indices only. Stores through a computed register index, if
the EDM makes any, are not counted, so the absence of a directory-list write means no
statically resolvable one. Which code path reaches each site is not part of this count; the
per-register list is in the data.
