+++
id = "E025"
claim = "On the laptop the graphics device reports its stolen memory at 0x7f800000 and the table of GTT pages at 0x7ffc0000, so stolen memory is 7932 KiB (7936 KiB up to the GTT, less one page) and the GTT, if it runs to the end of that window, is 256 KiB; GMCH_CTRL reads 0x0030 and the host bridge's words at 0x50 and 0x52 read 0"
unit = "platform"
method = "script table probes/platform/memory-sizes.toml on the laptop, linux fork with the debug option on: read-only PCI configuration reads (lspci, setpci) of 00:02.0 and 00:00.0, one MMIO read of PGETBL_CTL, and the kernel log lines of the graphics device"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["platform-memory-sizes"]
terms = []
+++

**What runs.** A shell script reads, as root and without writing anything, the first 256 bytes of
configuration space of the graphics device (00:02.0) and of the host bridge (00:00.0), the
device's base of stolen memory (BSM, offset 0x5c), its GMCH_CTRL word (offset 0x52), the host
bridge's words at 0x50 and 0x52 (where other Intel parts keep the graphics control word), the
device's resources, and the register PGETBL_CTL at 0x2020 of the register region (it maps
`/dev/mem` for that one read). It then lists the lines the gma500 driver logged for the device.
These are the graphics device's own PCI and GTT registers, not SGX545's, named as the gma500
driver names them.

**Results.** The device is an Atom D2xxx/N2xxx integrated graphics controller (revision 9) with
a 1 MiB register region at 0x80000000 and I/O ports at 0x7100.

- BSM reads 0x7f800000.
- GMCH_CTRL reads 0x0030.
- PGETBL_CTL reads 0x7ffc0000.
- The host bridge words at 0x50 and at 0x52 both read 0, and its configuration space is zero
  from 0x40 to 0xcf, so the bridge holds no graphics control word.

From these, the stolen memory runs from 0x7f800000 up to the table at 0x7ffc0000: 0x7c0000 bytes,
7936 KiB, and 7932 KiB when one page is left out. The table of pages starts at 0x7ffc0000; its end
is not read. If the window ends at 0x80000000, the GTT is 0x40000 bytes, 256 KiB, which is 65536
page entries of four bytes and so a 256 MiB aperture of GTT addresses. That end and the entry size
are inferred, not read.

The kernel log of the boot shows the driver bound to the device, the framebuffer set up, and,
later in the same run, the SGX firmware loaded and the EDM up after 644 µs. The data reports
no GTT debugfs file (`gtt_mm` is absent), so the driver offers no second reading of the
sizes. One run, one boot.

**Not shown.** What GMCH_CTRL 0x0030 encodes; the data does not decode it, and it is not used
above. The log line "power management timed out" and the BIF fault near the end of the log
appear after the SGX boot lines and are not used for the sizes.
