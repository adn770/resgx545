+++
id = "C0344"
source = "intel-ctp-k900"
locator = "linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h:238"
link = "https://github.com/xxx-man/android_kernel_lenovo_redhookbay/blob/41a61d5ffcbee9e185a2aeeb980e69de9274adf6/linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h#L238"
quote = "IMG_UINT32\t\t\tui32FrameNum;"
terms = ["cmd_ta.frame_num", "hw_render_details.frame_num"]
+++

Line 238 of `sgxinfo.h` in the Lenovo K900 kernel (DDK 1.11) declares `ui32FrameNum`. It backs the
glossary field `cmd_ta.frame_num`: frame number; and the glossary field
`hw_render_details.frame_num`: frame number.
