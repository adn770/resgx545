#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: tools/closing/session_tests.sh <area/closing-name>     e.g. edm/closing-r4-q152
#
# Re-runs a published closing session's own tests (resgx545-data) from a scratch copy, laid out
# the way the session was run, and prints PASS or FAIL with the tests' exit code (the script's
# own exit code is the tests' exit code; 2 = usage or setup error). The data repository is never
# written to. In the scratch tree:
#   - the session is copied to scratch/resgx545/closing3/<name> (name = the directory without
#     "closing-"), with an empty debug/;
#   - every published session is linked as scratch/resgx545/{closing,closing2,closing3}/<name>
#     (the copy takes its own place), so the sessions' relative references to siblings resolve;
#   - scratch/resgx545/{closing,closing2,closing3}/pixel-faults/.venv/bin/python is a wrapper
#     that runs $PY;
#   - HOME is a fake home whose src/resgx545 is a git worktree of the tool repository at the
#     newest commit of the session's FROZEN.commits (or, when the session has a TOOLSRC.sha256,
#     the newest commit holding exactly that tool source), each pinned file replaced by its
#     pinned blob, and src/scratch/resgx545 is the scratch tree. The copy's FROZEN.sha256 has its
#     absolute resgx545 and resgx545-data paths pointed at the fake home, so the freeze
#     verifies against the pinned source;
#   - src/resgx545-data is the data repository; the worktree's target/ is the runner's own
#     (RESGX545_SESSION_TARGET, kept between runs, never the main checkout's), the main
#     checkout's userspace/libsgxfive/build/ is copied and its .venv linked (current, not
#     pinned), and a session's debug-src/ is copied to debug/ with its path dependencies on
#     crates/ pointed at the worktree;
#   - TOOL_SRC, RESGX545 and RESGX545_MAIN name the pinned worktree and RESGX545_DATA the fake
#     home's data link (the sessions' overrides of their tool and data trees, which some default
#     to an agent worktree that no longer exists or to the author's absolute paths);
#   - each sibling-src/<dir>/ of the session (inputs it read from scratch beside it) is copied
#     to scratch/resgx545/closing3/<dir>;
#   - the entry is tests/run_all.sh, else tests/run_mock.sh, else tests/run_mock.py.
#
# Environment: PY (the python the tests use; default <tool>/.venv/bin/python, else python3),
# RESGX545_TOOL (the tool repository; default this checkout), RESGX545_DATA (default
# ../resgx545-data beside the tool repository), RESGX545_SESSION_TARGET (default
# scratch/resgx545/session-target beside the tool repository), KEEP=1 (keep the scratch tree and
# print it).
HERE=$(cd "$(dirname "$0")" && pwd)
TOOL=$(cd "${RESGX545_TOOL:-$HERE/../..}" && pwd)
DATA=$(cd "${RESGX545_DATA:-$TOOL/../resgx545-data}" 2>/dev/null && pwd)
TARGET=${RESGX545_SESSION_TARGET:-$(dirname "$TOOL")/scratch/resgx545/session-target}
die() { echo "session_tests: $*" >&2; exit 2; }

SESSION=${1%/}
[ -n "$SESSION" ] && [ $# = 1 ] || die "usage: $0 <area/closing-name>"
[ -n "$DATA" ] || die "no data repository (set RESGX545_DATA)"
SRC="$DATA/$SESSION"
[ -d "$SRC" ] || die "no such session: $SESSION"
for e in tests/run_all.sh tests/run_mock.sh tests/run_mock.py; do
    [ -f "$SRC/$e" ] && { ENTRY=$e; break; }
done
[ -n "$ENTRY" ] || die "$SESSION has no tests/run_all.sh, run_mock.sh or run_mock.py"
if [ -z "$PY" ]; then
    PY=$TOOL/.venv/bin/python
    [ -x "$PY" ] || PY=$(command -v python3)
fi
case "$PY" in /*) ;; *) PY=$(command -v "$PY") ;; esac
NAME=$(basename "$SESSION"); NAME=${NAME#closing-}
COMMON=$(cd "$TOOL" && git rev-parse --path-format=absolute --git-common-dir) \
    || die "$TOOL is not a git repository"

W=$(mktemp -d "${TMPDIR:-/tmp}/session_tests.XXXXXX") || die "no scratch directory"
W=$(cd "$W" && pwd -P)
HOMEDIR=$W/home
R=$HOMEDIR/src/resgx545
S=$W/scratch/resgx545
cleanup() {
    git -C "$TOOL" worktree remove --force "$R" >/dev/null 2>&1
    git -C "$TOOL" worktree prune >/dev/null 2>&1
    [ "$KEEP" = 1 ] && echo "session_tests: kept $W" || rm -rf "$W"
}
trap cleanup EXIT

mkdir -p "$HOMEDIR/src" "$S/closing" "$S/closing2" "$S/closing3"
ln -s "$W/scratch" "$HOMEDIR/src/scratch"
ln -s "$DATA" "$HOMEDIR/src/resgx545-data"
export CARGO_HOME=${CARGO_HOME:-$HOME/.cargo} RUSTUP_HOME=${RUSTUP_HOME:-$HOME/.rustup}
for g in closing closing2 closing3; do   # a session's shims find it beside the session's group
    mkdir -p "$S/$g/pixel-faults/.venv/bin"
    printf '#!/bin/sh\nexec "%s" "$@"\n' "$PY" > "$S/$g/pixel-faults/.venv/bin/python"
    chmod +x "$S/$g/pixel-faults/.venv/bin/python"
done
for d in "$DATA"/*/closing-*; do
    [ -d "$d" ] || continue
    n=$(basename "$d"); n=${n#closing-}
    for g in closing closing2 closing3; do ln -s "$d" "$S/$g/$n"; done
done
# names the sessions used while they were scratch directories
[ -e "$S/closing/s1b" ] && ln -s "$S/closing/s1b" "$S/closing/s1b-v2"
rm -f "$S/closing3/$NAME"
cp -R "$SRC" "$S/closing3/$NAME" || die "cannot copy $SESSION"
C=$S/closing3/$NAME
mkdir -p "$C/debug"
for d in "$C"/sibling-src/*/; do       # inputs the session read from scratch beside it
    [ -d "$d" ] || continue
    n=$(basename "$d")
    [ -e "$S/closing3/$n" ] && die "sibling-src/$n would replace closing3/$n"
    cp -R "$d" "$S/closing3/$n"
done

# the pinned tool source: a worktree at the newest pinned commit (or the tool source's commit),
# each pin overlaid
COMMITS=$C/FROZEN.commits
BASE=HEAD
if [ -f "$COMMITS" ]; then
    pinned=$(awk '!/^#/ && $2 != "untracked" && NF >= 3 {print $2}' "$COMMITS" | sort -u)
    # shellcheck disable=SC2086
    [ -n "$pinned" ] && BASE=$(git -C "$TOOL" rev-list --no-walk --date-order $pinned | head -1)
fi
# a session that deployed a tool froze its source in TOOLSRC.sha256 (paths relative to the
# tree): the worktree is then the newest commit holding exactly those files
toolsrc_commit() {
    local c h p ok sum
    for c in $(git -C "$TOOL" rev-list -n 300 HEAD -- $(awk '{print $2}' "$1")); do
        ok=1
        while read -r h p; do
            sum=$(git -C "$TOOL" show "$c:$p" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
            [ "$sum" = "$h" ] || { ok=0; break; }
        done < "$1"
        [ $ok = 1 ] && { echo "$c"; return; }
    done
}
if [ -f "$C/TOOLSRC.sha256" ] && ! awk '$2 ~ /^\//' "$C/TOOLSRC.sha256" | grep -q .; then
    tc=$(toolsrc_commit "$C/TOOLSRC.sha256")
    if [ -n "$tc" ]; then BASE=$tc
    else echo "session_tests: warning: no commit holds the frozen tool source (TOOLSRC.sha256)"
    fi
fi
git -C "$TOOL" worktree add -q --detach "$R" "$BASE" || die "cannot check out $BASE of $TOOL"
if [ -f "$COMMITS" ]; then
    while read -r hash commit path; do
        case "$hash" in "#"*|"") continue ;; esac
        grep -q "^$hash [ *]/.*/resgx545/$path\$" "$C/FROZEN.sha256" 2>/dev/null || continue
        mkdir -p "$R/$(dirname "$path")"
        if [ "$commit" = untracked ]; then
            [ -f "$COMMON/../$path" ] && cp "$COMMON/../$path" "$R/$path" \
                || echo "session_tests: warning: untracked pin $path not found in the main checkout"
        else
            git -C "$TOOL" show "$commit:$path" > "$R/$path" \
                || die "cannot read $commit:$path"
        fi
    done < "$COMMITS"
fi
MAIN=$(dirname "$COMMON")
# Builds of the pinned tool go to the runner's own target/, never the main checkout's (old
# binaries there would replace current ones, and on macOS a library rewritten in place kills
# the next process that loads it); libsgxfive's build is copied for the same reason.
mkdir -p "$TARGET" && ln -s "$TARGET" "$R/target" || die "cannot link the runner's target"
[ -d "$MAIN/userspace/libsgxfive/build" ] \
    && cp -R "$MAIN/userspace/libsgxfive/build" "$R/userspace/libsgxfive/build"
for b in .venv tools/usse-asm/usse-asm; do
    [ -e "$MAIN/$b" ] && [ ! -e "$R/$b" ] && ln -s "$MAIN/$b" "$R/$b"
done
# The sessions' scripts run target/release/sgx-sim or target/debug/sgx-sim (a binary of
# sgx-tools): build the workspace's binaries in both profiles from the pinned tree.
if [ -d "$R/crates/sgx-sim" ]; then
    (cd "$R" && cargo build -q --release --workspace --bins \
        && cargo build -q --workspace --bins) \
        || echo "session_tests: warning: cannot build the binaries at the pinned commit"
fi
if [ -d "$C/debug-src" ]; then
    cp -R "$C/debug-src/." "$C/debug/"
    for f in "$C"/debug/*/Cargo.toml; do
        [ -f "$f" ] && R=$R perl -pi -e 's{"(?:/[^/"]+)*?/resgx545/crates/}{"$ENV{R}/crates/}' "$f"
    done
fi
for f in "$C"/FROZEN*.sha256; do
    [ -f "$f" ] || continue
    R=$R D=$HOMEDIR/src/resgx545-data perl -pe \
        's{^([0-9a-f]{64} [ *])/(?:[^/]+/)*?resgx545-data/}{$1$ENV{D}/}
         || s{^([0-9a-f]{64} [ *])/(?:[^/]+/)*?resgx545/}{$1$ENV{R}/}' "$f" > "$f.new" \
        && mv "$f.new" "$f"
done

cd "$C" || die "cannot enter the copy"
export HOME=$HOMEDIR PY RESGX545=$R TOOL_SRC=$R RESGX545_MAIN=$R \
    RESGX545_DATA=$HOMEDIR/src/resgx545-data PYTHONDONTWRITEBYTECODE=1
case "$ENTRY" in
    *.py) "$PY" "$ENTRY" ;;
    *) bash "$ENTRY" ;;
esac
rc=$?
if [ $rc = 0 ]; then verdict=PASS; else verdict=FAIL; fi
echo "session_tests: $SESSION $verdict (exit $rc)"
exit $rc
