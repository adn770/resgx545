<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Testing an instruction yourself

What an instruction does is settled on the hardware, not in the text. The probe harness
(`tools/usse-asm/probe.py`) runs a case as the pixel shader of a 64 x 32 fill on the real GPU:
a template sets inputs, runs the instruction under test, and stores registers to a scratch
buffer the host reads back. This is the middle of the template most cases use (it sets
more inputs before and stores more registers after):

<!-- @prog dump.s match='^(.OP.|mov\S* r29,|stad .r29,.#0.)' -->

`{OP}` is the instruction under test, and `#0x5CAF0000` a marker the harness replaces by the
scratch buffer's address; the simulator does the same, so the template runs on it unchanged.
Here it asks how `fmad` rounds a tie: 1 + 2^-12 squared, written to `r10` and stored:

<!-- @sim prog=tutorial/fmad_tie.s -->

The product, 1 + 2^-11 + 2^-24, is a tie between two binary32 values; `fmad` rounds it to even
(*Float rounding and NaN*). On the hardware, the same case is an entry of a probe table in
`probes/usse/` (the `fmad.toml` table holds this one); the probe runner sends it to the GPU, and
the vector tool turns the readback into a vector the simulator is tested against
(`doc/specs/vectors.md`), so a rule found this way is held to the hardware from then on:

```
$ cargo run --release -p sgx-tools --bin sgx-sim -- --vectors \
    $RESGX545_DATA/vectors/<unit>/<feature>/<probe>.vec.json
```
