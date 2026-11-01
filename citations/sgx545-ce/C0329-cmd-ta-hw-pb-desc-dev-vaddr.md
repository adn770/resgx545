+++
id = "C0329"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxinfokm.h:316"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxinfokm.h#L316"
quote = "IMG_DEV_VIRTADDR\tsHWPBDescDevVAddr;"
terms = ["cmd_ta.hw_pb_desc_dev_vaddr", "hw_render_context.hw_pb_desc_dev_vaddr"]
+++

Line 316 of `sgxinfokm.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sHWPBDescDevVAddr`. It backs the glossary field `cmd_ta.hw_pb_desc_dev_vaddr`: PB descriptor of the
kick; and the glossary field `hw_render_context.hw_pb_desc_dev_vaddr`: PB descriptor of the context.
