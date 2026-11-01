+++
id = "C0330"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:215"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L215"
quote = "IMG_DEV_VIRTADDR\tsAccessDevAddr;"
terms = ["hw_render_details.access_dev_vaddr"]
+++

Line 215 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sAccessDevAddr`. It backs the glossary field `hw_render_details.access_dev_vaddr`: access/lock word
(SYNCINFO).
