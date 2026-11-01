+++
id = "C0686"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:161"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L161"
quote = "#define SGXMKIF_TQFLAGS_TATQ_SYNC\t\t\t\t0x00000004"
terms = ["TQ_FLAGS.TA_TQ_SYNC"]
+++

Line 161 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_TQFLAGS_TATQ_SYNC`. It backs the glossary flag `TQ_FLAGS.TA_TQ_SYNC`: update the TA-side TQ
sync (transfer_cmd_shared.sync_ta_*) (0x4).
