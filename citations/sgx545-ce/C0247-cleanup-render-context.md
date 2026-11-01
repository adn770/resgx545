+++
id = "C0247"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:250"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L250"
quote = "#define\tPVRSRV_CLEANUPCMD_RC\t\t0x2U"
terms = ["CLEANUP.RENDER_CONTEXT"]
+++

Line 250 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`PVRSRV_CLEANUPCMD_RC`. It backs the glossary enum value `CLEANUP.RENDER_CONTEXT`: clean up a HW
render context.
