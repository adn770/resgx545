+++
id = "C0731"
source = "sgx545-ce"
locator = "src/services4/include/sgx_bridge.h:532"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_bridge.h#L532"
quote = "IMG_DEV_VIRTADDR sHWRenderContextDevVAddr;"
terms = ["hw_rt_data.hw_render_context_dev_vaddr"]
+++

Line 532 of `sgx_bridge.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sHWRenderContextDevVAddr`. It backs the glossary field `hw_rt_data.hw_render_context_dev_vaddr`:
owning HW render context.
