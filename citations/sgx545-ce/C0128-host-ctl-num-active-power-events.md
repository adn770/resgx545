+++
id = "C0128"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:94"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L94"
quote = "IMG_UINT32\t\t\t\tui32NumActivePowerEvents;"
terms = ["host_ctl.num_active_power_events"]
+++

Line 94 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32NumActivePowerEvents`. It backs the glossary field `host_ctl.num_active_power_events`: active
power-down count.
