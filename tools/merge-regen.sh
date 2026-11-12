#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Git merge driver "regen" for the generated files (.gitattributes): keep our side, report no
# conflict. The file is stale until tools/regen_generated.py rebuilds it from the merged sources
# (the driver runs before the tree is merged, so it cannot rebuild). See HACKING.md.
# usage (set by git): merge-regen.sh %O %A %B %L %P
exit 0
