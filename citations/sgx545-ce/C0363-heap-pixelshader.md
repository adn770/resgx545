+++
id = "C0363"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxconfig.h:103"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxconfig.h#L103"
quote = "#define SGX_PIXELSHADER_HEAP_BASE\t\t\t 0xF4000000"
terms = ["HEAP.PIXELSHADER"]
+++

Line 103 of `sgxconfig.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGX_PIXELSHADER_HEAP_BASE`. It backs the glossary enum value `HEAP.PIXELSHADER`: pixel USE code
heap base (USE_CODE_BASE_0).
