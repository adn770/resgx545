+++
id = "C0685"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:159"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L159"
quote = "#define SGXMKIF_TQFLAGS_NOSYNCUPDATE\t\t\t0x00000001"
terms = ["TQ_FLAGS.NO_SYNC_UPDATE"]
+++

Line 159 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_TQFLAGS_NOSYNCUPDATE`. It backs the glossary flag `TQ_FLAGS.NO_SYNC_UPDATE`: do not update
src/dst syncs (0x1).
