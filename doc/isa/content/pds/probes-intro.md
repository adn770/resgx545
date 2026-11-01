<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Hardware probes

The questions of *Open questions* are put to the GPU by PDS probes: our own PDS program runs
as the PDS secondary program of a client fill, copies its preset data words to the
temporaries, does the operation under test there and passes the results to the fill's shader
`sa_dump.s` with `douta` (into `sa0`-`sa15`), which stores them where the host reads them
(the probe runner and the tables under `probes/pds/` of the data repository, each probe
listing the readings it tests). The first,
`pds-alu-readback`, checks that path itself. Each fact
is one snippet in `doc/isa/content/pds/probe/`, measured on 2026-10-24; the vectors are in the data
repository's
`vectors/` directory, one set per series of probes:

<!-- @probes -->
