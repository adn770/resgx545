+++
id = "C0333"
source = "sgx545-ce"
locator = "src/include4/sgxapi_km.h:254"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/include4/sgxapi_km.h#L254"
quote = "IMG_UINT32\t\t\tui32NumSPMRenders;"
terms = ["hw_rt_data_set.num_spm_renders"]
+++

Line 254 of `sgxapi_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32NumSPMRenders`. It backs the glossary field `hw_rt_data_set.num_spm_renders`: partial renders
run.
