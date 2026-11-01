+++
id = "C0682"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:162"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L162"
quote = "#define SGXMKIF_TQFLAGS_3DTQ_SYNC\t\t\t\t0x00000008"
terms = ["TQ_FLAGS.3D_TQ_SYNC"]
+++

Line 162 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_TQFLAGS_3DTQ_SYNC`. It backs the glossary flag `TQ_FLAGS.3D_TQ_SYNC`: update the 3D-side TQ
sync (transfer_cmd_shared.sync_3d_*) (0x8).
