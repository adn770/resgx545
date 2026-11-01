+++
id = "C0158"
source = "sgx545-ce"
locator = "src/services4/include/sgx_bridge.h:121"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_bridge.h#L121"
quote = "IMG_UINT32              ui32OffsetOfPriorityField;"
terms = ["hw_transfer_context.priority"]
+++

Line 121 of `sgx_bridge.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32OffsetOfPriorityField`. It backs the glossary field `hw_render_context.priority`: scheduling
priority; the glossary field `hw_transfer_context.priority`: priority; and the glossary field
`offset_of_priority_field`: offset of the context's priority word.
