+++
id = "C0156"
source = "sgx545-ce"
locator = "src/services4/include/sgx_bridge.h:520"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_bridge.h#L520"
quote = "IMG_UINT32       ui32OffsetToPDDevPAddr;"
terms = ["hw_transfer_context.pd_dev_paddr"]
+++

Line 520 of `sgx_bridge.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32OffsetToPDDevPAddr`. It backs the glossary field `hw_render_context.pd_dev_paddr`:
page-directory physical address (kernel writes); the glossary field
`hw_transfer_context.pd_dev_paddr`: PD physical address (kernel writes); and the glossary field
`offset_to_pd_dev_paddr`: offset where the kernel writes the PD address.
