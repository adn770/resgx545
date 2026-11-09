#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: run-table.sh NAME TABLE...     (RESGX545_KERNEL_COMMIT=<commit> required)
#
# Run probe tables (probes/<unit>/<feature>.toml) on the laptop through the campaign runner,
# with the laptop's tool ~/sgxfive-test-NAME (see deploy-tool.sh). One log per table in
# $RUN_LOG_DIR/NAME/ (default debug/runs), a summary line per table in $RUN_LOG_DIR/NAME.log.
# The runner itself checks that the loaded module is the installed one and writes the per-job
# marker lines to the kernel log, so this script does neither.
# Environment: SGX_TARGET_HOST, SGX_TARGET_SSH_OPTS (tools/bringup/local.env), RESGX545_DATA
# (default ../resgx545-data), RUN_LOCAL_TOOL (the local binary the runner reads the table's
# commands from, default userspace/libsgxfive/build/sgxfive-test). SGX_DRY_RUN=1 prints the
# commands.
set -u
cd "$(dirname "$0")/../.."
LOCAL_ENV=${SGX_LOCAL_ENV:-tools/bringup/local.env}
[ -f "$LOCAL_ENV" ] && . "$LOCAL_ENV"
[ $# -ge 2 ] || { echo "usage: run-table.sh NAME TABLE..." >&2; exit 2; }
NAME=$1; shift
: "${RESGX545_KERNEL_COMMIT:?run-table.sh: RESGX545_KERNEL_COMMIT is not set}"
PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python
DATA=${RESGX545_DATA:-../resgx545-data}
LOGS=${RUN_LOG_DIR:-debug/runs}
SUM=$LOGS/$NAME.log
[ -n "${SGX_DRY_RUN:-}" ] || mkdir -p "$LOGS/$NAME"
for t in "$@"; do
    log=$LOGS/$NAME/$(echo "$t" | tr / -).log
    cmd="SGX_SWEEP_TOOL=./sgxfive-test-$NAME SGX_PROBE_TOOL=./sgxfive-test-$NAME SGX_TARGET_HOST=${SGX_TARGET_HOST:-user@sgx-target} SGX_TARGET_SSH_OPTS='${SGX_TARGET_SSH_OPTS:-}' RESGX545_KERNEL_COMMIT=$RESGX545_KERNEL_COMMIT $PY tools/campaign/campaign.py --target laptop --tool ${RUN_LOCAL_TOOL:-userspace/libsgxfive/build/sgxfive-test} --repo data --data $DATA --datasets datasets probes/$t.toml"
    if [ -n "${SGX_DRY_RUN:-}" ]; then
        echo "$cmd > $log 2>&1"
        continue
    fi
    start=$(date +%s)
    eval "$cmd" > "$log" 2>&1
    echo "$t exit $? $(( $(date +%s) - start ))s $(tail -1 "$log" | cut -c1-120)" >> "$SUM"
done
[ -n "${SGX_DRY_RUN:-}" ] || echo done >> "$SUM"
