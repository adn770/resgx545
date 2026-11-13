# SPDX-License-Identifier: MIT
# run/hooks.sh: @NAME@'s hooks into the kit's laptop runner (kit/run_stage.sh), sourced by it.
# Only reads: no debugfs write, no rm, no exit (session.py guard). $JW/NAME.out, .err, .dmesg are
# the job's files, $W its work directory.
# hook_reading NAME: a control's reading, `key=value` words (every key of its reads: knob)
hook_reading() {
	local d
	d=$(sed -n 's/^diff: \([0-9][0-9]*\) of .*/\1/p' "$JW/$1.out" | head -n 1)
	[ -n "$d" ] && printf 'diff=%s\n' "$d"
	return 0
}
# hook_check NAME: after a job that read ok, a reason to stop the stage (rc 24), or nothing
hook_check() { return 0; }
# hook_fault NAME: after an expected fault or hang row (reset and strict health done), a reason to
# stop the stage (rc 24), or nothing
hook_fault() { return 0; }
