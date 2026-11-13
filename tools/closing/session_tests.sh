#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: tools/closing/session_tests.sh [--cached] <area/closing-name>   e.g. edm/closing-r4-q152
#
# Re-runs a published closing session's own tests (resgx545-data) from a scratch copy, laid out
# the way the session was run, and prints PASS or FAIL with the tests' exit code (the script's
# own exit code is the tests' exit code; 2 = usage or setup error). The data repository is never
# written to. In the scratch tree:
#   - the session is copied to scratch/resgx545/closing3/<name> (name = the directory without
#     "closing-"), with an empty debug/;
#   - every published session is linked as scratch/resgx545/{closing,closing2,...,closing6}/<name>
#     (the copy takes its own place), so the sessions' relative references to siblings resolve;
#   - scratch/resgx545/{closing,closing2,closing3}/pixel-faults/.venv/bin/python is a wrapper
#     that runs $PY;
#   - HOME is a fake home whose src/resgx545 is a git worktree of the tool repository at the
#     newest commit of the session's FROZEN.commits (or, when the session has a TOOLSRC.sha256,
#     the newest commit holding exactly that tool source), each pinned file replaced by its
#     pinned blob (a FROZEN.commits line may name its repository, R5-dpm's resgx545:PATH; a
#     line of another repository, linux: or data:, is left to the session's own checks), and
#     src/scratch/resgx545 is the scratch tree. The copy's FROZEN.sha256 has its absolute
#     resgx545 and resgx545-data paths pointed at the fake home, so the freeze verifies against
#     the pinned source; a pin of a tree that sat under scratch/resgx545/ (round 4 froze against
#     closing4/lead/wt) is pointed at the worktree by its FROZEN.commits path, and a frozen file
#     of the session that only lists such paths of the freeze (R4-G's gen/data/sources.lst) is
#     pointed there too, its hash line following (a list named in postrun/paths-as-frozen.txt,
#     r6-held's, which its generator checks against the fixed paths it writes, keeps them, and
#     the freeze's lines of those paths stay as frozen; a freeze that a freeze names as a
#     session file, a post-run fix's FROZEN.pre-fix.sha256, keeps its bytes);
#   - src/resgx545-data is the data repository (or, when the session has a
#     postrun/data-view.txt, a view of it in which each area the file names holds only the
#     sessions it lists: the corpus a generator that scans the area saw at the freeze, with a git
#     repository of its own that borrows the data repository's objects, so a freeze's data: pins
#     show at their commits and nothing is written to the data repository); the
#     worktree's target/ is the runner's own (RESGX545_SESSION_TARGET, kept between runs, never
#     the main checkout's), the main checkout's userspace/libsgxfive/build/ is copied and its
#     .venv linked (current, not pinned), and a session's debug-src/ is copied to debug/ with its
#     path dependencies on crates/ pointed at the worktree;
#   - TOOL_SRC, RESGX545 and RESGX545_MAIN name the pinned worktree and RESGX545_DATA the fake
#     home's data link (the sessions' overrides of their tool and data trees, which some default
#     to an agent worktree that no longer exists or to the author's absolute paths); a
#     variable named in the session's postrun/env-as-frozen.txt is left unset instead, so the
#     session's own default applies (R7-rp's generator writes the trees it read into a frozen
#     list, kept with postrun/paths-as-frozen.txt);
#   - each sibling-src/<dir>/ of the session (inputs it read from scratch beside it) is copied
#     to scratch/resgx545/closing3/<dir>;
#   - a frozen input the session read from scratch outside every tree (an absolute path under
#     scratch/resgx545/ that no FROZEN.commits line pins: a plan, a reading of the firmware) is
#     copied from its published copy, cited/<path> of the data repository or of the private one,
#     to scratch/resgx545/<path>, and the copy's freeze points there (no copy: the freeze fails);
#   - a file of the session frozen by its relative path but derived from the closed firmware, so
#     left out of the published session, is copied back from cited/closingN/<name>/<path> of the
#     private repository (r6-held's private/o3/; no copy: the freeze fails);
#   - a binary the session built and ran, frozen by its relative path (R7-geo's
#     bin/t6/sgxfive-test), is bound to its source by a FROZEN.commits line
#     `<binary-sha256>  built  <commit>  <source-path>  <source-sha256>  <recipe>`: the source blob
#     at the commit must hash to <source-sha256> and the recipe (data:PATH in the data repository,
#     else a PATH of the tool tree at the commit) must be in place, else the session FAILs; the
#     bytes are neither looked for nor restored: the binary's place holds a stand-in (one text
#     line naming the hash) that a shasum wrapper first on PATH reads as the pinned hash, so the
#     session's freeze, verify and re-freeze steps run as frozen (R7-geo's run_mock re-freezes
#     copies and its freeze script compares the binary with TOOL6.sha256); a changed stand-in
#     hashes as itself, and no test runs it (a session's mocks run fakes of its tools);
#   - a part of the session with a freeze of its own (r6-held's p/, its FROZEN.sha256 and
#     FROZEN.commits) is pinned and pointed as the session's freeze is;
#   - the copy's tests/ files that no freeze names have their absolute resgx545-data and resgx545
#     paths (the author's trees: R6-dpm's tests/test_read.py scans render/ by its path)
#     pointed at the fake home, so they read the data view and the pinned tree; a frozen file
#     keeps the bytes that ran;
#   - the entry is tests/run_all.sh, else tests/run_mock.sh, else tests/run_mock.py.
#
# The run's PID is written to $TARGET/session_tests.pid (named in the first output line, removed on
# exit): tools/waitfor.py --pidfile <it> --timeout N waits on it exactly, with no process-name match.
#
# Environment: PY (the python the tests use; default <tool>/.venv/bin/python, else python3),
# RESGX545_TOOL (the tool repository; default this checkout), RESGX545_DATA (default
# ../resgx545-data beside the tool repository), RESGX545_DATA_PRIVATE (default
# ../resgx545-data-private; only its cited/ copies are read), RESGX545_SESSION_TARGET (default
# scratch/resgx545/session-target beside the tool repository), KEEP=1 (keep the scratch tree and
# print it).
#
# A pass is recorded as $RESGX545_SESSION_TARGET/passes/<key>, the key from passcache.py (the
# session's path and files, this runner's digest, the commits the session pins, PY); --cached
# prints CACHED PASS and runs nothing when the key has passed before.
HERE=$(cd "$(dirname "$0")" && pwd)
TOOL=$(cd "${RESGX545_TOOL:-$HERE/../..}" && pwd)
DATA=$(cd "${RESGX545_DATA:-$TOOL/../resgx545-data}" 2>/dev/null && pwd)
DATAP=$(cd "${RESGX545_DATA_PRIVATE:-$TOOL/../resgx545-data-private}" 2>/dev/null && pwd)
TARGET=${RESGX545_SESSION_TARGET:-$(dirname "$TOOL")/scratch/resgx545/session-target}
die() { echo "session_tests: $*" >&2; exit 2; }

CACHED=0
[ "$1" = --cached ] && { CACHED=1; shift; }
SESSION=${1%/}
[ -n "$SESSION" ] && [ $# = 1 ] || die "usage: $0 <area/closing-name>"
# a waiter needs something exact, never a process name: the PID of this run, named here
PIDFILE=$TARGET/session_tests.pid
mkdir -p "$TARGET" && echo $$ > "$PIDFILE" || die "cannot write $PIDFILE"
echo "session_tests: pidfile $PIDFILE (pid $$); wait with tools/waitfor.py --pidfile $PIDFILE --timeout N"
trap 'rm -f "$PIDFILE"' EXIT
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
KEY=$("$PY" "$HERE/passcache.py" key "$SRC" "$TOOL" "$PY" "$HERE/session_tests.sh" \
    "$HERE/passcache.py") \
    || { KEY=; echo "session_tests: warning: no pass key, nothing cached"; }
if [ "$CACHED" = 1 ] && [ -n "$KEY" ] && [ -f "$TARGET/passes/$KEY" ]; then
    echo "session_tests: $SESSION CACHED PASS"
    exit 0
fi

W=$(mktemp -d "${TMPDIR:-/tmp}/session_tests.XXXXXX") || die "no scratch directory"
W=$(cd "$W" && pwd -P)
HOMEDIR=$W/home
R=$HOMEDIR/src/resgx545
S=$W/scratch/resgx545
cleanup() {
    rm -f "$PIDFILE"
    git -C "$TOOL" worktree remove --force "$R" >/dev/null 2>&1
    git -C "$TOOL" worktree prune >/dev/null 2>&1
    [ "$KEEP" = 1 ] && echo "session_tests: kept $W" || rm -rf "$W"
}
trap cleanup EXIT

mkdir -p "$HOMEDIR/src" "$S/closing" "$S/closing2" "$S/closing3" "$S/closing4" "$S/closing5" \
    "$S/closing6"
ln -s "$W/scratch" "$HOMEDIR/src/scratch"
# a session whose generator scans an area of the data repository lists in postrun/data-view.txt
# the sessions of that area its freeze saw; the fake home's data repository is then a view that
# holds only those in each listed area, every other entry linked whole
VIEW=$SRC/postrun/data-view.txt
if [ -f "$VIEW" ]; then
    FD=$HOMEDIR/src/resgx545-data
    mkdir "$FD"
    for e in "$DATA"/*; do
        a=$(basename "$e")
        if grep -q "^$a/" "$VIEW"; then
            mkdir "$FD/$a"
            for s in "$e"/*; do
                grep -qxF "$a/$(basename "$s")" "$VIEW" && ln -s "$s" "$FD/$a/"
            done
        else
            ln -s "$e" "$FD/$a"
        fi
    done
    # git in the view reads the data repository's commits (a freeze's data: pins) through a
    # repository of its own that borrows the objects, so nothing git writes lands in the data
    if DGIT=$(git -C "$DATA" rev-parse --path-format=absolute --git-common-dir 2>/dev/null); then
        git init -q "$FD" && echo "$DGIT/objects" > "$FD/.git/objects/info/alternates" \
            || die "no git repository for the data view"
    fi
else
    ln -s "$DATA" "$HOMEDIR/src/resgx545-data"
fi
export CARGO_HOME=${CARGO_HOME:-$HOME/.cargo} RUSTUP_HOME=${RUSTUP_HOME:-$HOME/.rustup}
for g in closing closing2 closing3; do   # a session's shims find it beside the session's group
    mkdir -p "$S/$g/pixel-faults/.venv/bin"
    printf '#!/bin/sh\nexec "%s" "$@"\n' "$PY" > "$S/$g/pixel-faults/.venv/bin/python"
    chmod +x "$S/$g/pixel-faults/.venv/bin/python"
done
for d in "$DATA"/*/closing-*; do
    [ -d "$d" ] || continue
    n=$(basename "$d"); n=${n#closing-}
    for g in closing closing2 closing3 closing4 closing5 closing6; do ln -s "$d" "$S/$g/$n"; done
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
    # a line may name its repository (R5-dpm: resgx545:PATH, linux:PATH, data:PATH): only the
    # tool tree's lines choose the commit
    pinned=$(awk '!/^#/ && $2 != "untracked" && $2 != "built" && NF >= 3 \
        && ($3 !~ /^[a-z][a-z0-9-]*:/ || $3 ~ /^resgx545:/) {print $2}' "$COMMITS" | sort -u)
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
# a source pinned by commit (`<sha256>  <commit>:<path>`, r8-k2 and r8-lgeo) is verified at that
# commit, and the worktree is that commit
if [ -f "$C/TOOLSRC.sha256" ] && awk '$2 ~ /^[0-9a-f]+:/' "$C/TOOLSRC.sha256" | grep -q .; then
    while read -r h spec; do
        case "$spec" in [0-9a-f]*:*) ;; *) continue ;; esac
        tc=$(git -C "$TOOL" rev-parse --verify -q "${spec%%:*}^{commit}") \
            || { echo "session_tests: $SESSION FAIL (TOOLSRC.sha256: no commit ${spec%%:*})"; exit 1; }
        sum=$(git -C "$TOOL" show "$tc:${spec#*:}" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
        [ "$sum" = "$h" ] || { echo "session_tests: $SESSION FAIL (TOOLSRC.sha256: $spec hashes to $sum, not $h)"; exit 1; }
        BASE=$tc
        echo "session_tests: tool source verified, $spec"
    done < "$C/TOOLSRC.sha256"
elif [ -f "$C/TOOLSRC.sha256" ] && ! awk '$2 ~ /^\//' "$C/TOOLSRC.sha256" | grep -q .; then
    tc=$(toolsrc_commit "$C/TOOLSRC.sha256")
    if [ -n "$tc" ]; then BASE=$tc
    else echo "session_tests: warning: no commit holds the frozen tool source (TOOLSRC.sha256)"
    fi
fi
git -C "$TOOL" worktree add -q --detach "$R" "$BASE" || die "cannot check out $BASE of $TOOL"
# a part of the session with a freeze of its own (r6-held's p/) is pinned and pointed as the
# session is: each directory of the copy that holds a FROZEN.sha256, with the FROZEN.commits
# beside it
freezes() {
    local f
    for f in "$C"/FROZEN*.sha256 "$C"/*/FROZEN*.sha256; do [ -f "$f" ] && echo "$f"; done
}
# the freezes whose absolute paths are pointed at the fake home: not a freeze that a freeze beside
# it names as a session file (a post-run fix's FROZEN.pre-fix.sha256, r8-ldpm): it keeps its bytes
pointed() {
    local f g
    for f in $(freezes); do
        for g in "$(dirname "$f")"/FROZEN*.sha256; do
            awk -v n="$(basename "$f")" '$2 == n || $2 == "*" n {found = 1} END {exit !found}' \
                "$g" && continue 2
        done
        echo "$f"
    done
}
for CM in "$C"/FROZEN.commits "$C"/*/FROZEN.commits; do
    [ -f "$CM" ] || continue
    while read -r hash commit path; do
        case "$hash" in "#"*|"") continue ;; esac
        [ "$commit" = built ] && continue
        case "$path" in resgx545:*) path=${path#resgx545:} ;; [a-z]*:*) continue ;; esac
        grep -q "^$hash [ *]/.*/$path\$" "$(dirname "$CM")/FROZEN.sha256" 2>/dev/null || continue
        mkdir -p "$R/$(dirname "$path")"
        if [ "$commit" = untracked ]; then
            [ -f "$COMMON/../$path" ] && cp "$COMMON/../$path" "$R/$path" \
                || echo "session_tests: warning: untracked pin $path not found in the main checkout"
        else
            git -C "$TOOL" show "$commit:$path" > "$R/$path" \
                || die "cannot read $commit:$path"
        fi
    done < "$CM"
done
# a binary bound to its source (a built line of FROZEN.commits) is verified by the source blob at
# its commit and the recipe's place, never by its bytes: its place in the copy holds a stand-in
# that the shasum wrapper below reads as the pinned hash
built_fail() { echo "session_tests: $SESSION FAIL (built $1)"; exit 1; }
STANDIN="resgx545 session_tests stand-in for the built binary"
BUILT=0
for CM in "$C"/FROZEN.commits "$C"/*/FROZEN.commits; do
    [ -f "$CM" ] || continue
    while read -r hash kind commit src want recipe; do
        [ "$kind" = built ] || continue
        src=${src#resgx545:}
        got=$(git -C "$TOOL" show "$commit:$src" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
        [ "$got" = "$want" ] || built_fail "$hash: $commit:$src hashes to $got, not $want"
        r=${recipe#resgx545:}
        case "$r" in
            data:*) [ -n "$DATA" ] && [ -f "$DATA/${r#data:}" ] ;;
            [a-z]*:*) false ;;
            *) git -C "$TOOL" cat-file -e "$commit:$r" 2>/dev/null ;;
        esac || built_fail "$hash: recipe $recipe is not in place"
        d=$(dirname "$CM"); names=
        for f in "$d"/FROZEN*.sha256; do
            [ -f "$f" ] || continue
            for b in $(awk -v h="$hash" \
                    '$1 == h && $2 !~ /^\*?\// {sub(/^\*/, "", $2); print $2}' "$f"); do
                names="$names $b"
                [ -e "$d/$b" ] && continue
                mkdir -p "$(dirname "$d/$b")" && echo "$STANDIN $hash" > "$d/$b"
                BUILT=1
            done
        done
        echo "session_tests: built${names:- $hash}: source verified, $commit:$src" \
            "(recipe $recipe)"
    done < "$CM"
done
if [ $BUILT = 1 ]; then
    # shasum reads an exact stand-in as the hash it names: printed hashes are replaced, and the
    # lines of a -c list that name a stand-in by its hash are checked against the stand-in itself
    REAL_SHASUM=$(command -v shasum) || die "no shasum"
    mkdir -p "$W/shims"
    cat > "$W/shims/shasum" <<SHIM
#!/usr/bin/perl
use strict; use Digest::SHA qw(sha256_hex); use File::Temp qw(tempfile);
my \$real = "$REAL_SHASUM";
sub standin { my \$p = shift; open my \$f, "<", \$p or return; local \$/; my \$t = <\$f>;
              return defined \$t && \$t =~ /^\Q$STANDIN\E ([0-9a-f]{64})\n\z/ ? \$1 : undef }
sub own { my \$p = shift; open my \$f, "<", \$p or return ""; local \$/; return sha256_hex(<\$f>) }
if (grep { \$_ eq "-c" || \$_ eq "--check" } @ARGV) {
    for my \$a (@ARGV) {
        next if \$a =~ /^-/ || ! -f \$a;
        open my \$in, "<", \$a or next; my @l = <\$in>; close \$in;
        for (@l) { s{^([0-9a-f]{64})( [ *])(.*)\$}{my \$s = standin(\$3);
                   (defined \$s && \$s eq \$1 ? own(\$3) : \$1) . "\$2\$3"}e }
        my (\$fh, \$tmp) = tempfile(); print \$fh @l; close \$fh; \$a = \$tmp;
    }
    exec \$real, @ARGV;
}
open my \$out, "-|", \$real, @ARGV or exit 2;
while (<\$out>) {
    s{^([0-9a-f]{64})( [ *])(.*)\$}{my \$s = standin(\$3); (\$s // \$1) . "\$2\$3"}e; print
}
close \$out; exit(\$? >> 8);
SHIM
    chmod +x "$W/shims/shasum"
    export PATH="$W/shims:$PATH"
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
# a file of the session that derives from the closed firmware (r6-held's O3 oracle, private/o3/)
# is frozen by its relative path but published only in resgx545-data-private, as
# cited/closingN/<name>/<path>: the copy is put back in its place (no copy: the freeze fails)
for f in $(freezes); do
    d=$(dirname "$f"); sub=${d#"$C"}; sub=${sub#/}
    while read -r hash path; do
        case "$path" in /*|"") continue ;; esac
        [ -e "$d/$path" ] && continue
        for p in "$DATAP"/cited/closing*/"$NAME"/${sub:+$sub/}"$path"; do
            [ -n "$DATAP" ] && [ -f "$p" ] || continue
            mkdir -p "$(dirname "$d/$path")" && cp "$p" "$d/$path"
            break
        done
    done < "$f"
done
# a frozen file that only lists absolute paths of the freeze itself (R4-G's gen/data/sources.lst,
# the files its generator read outside the session) moves with them: its paths are pointed at
# the fake home as the freeze's are below, and its hash line follows; a list named in
# postrun/paths-as-frozen.txt (r6-held's, which its generator checks against the fixed data path
# it writes) keeps its bytes
for f in $(pointed); do
    R=$R D=$HOMEDIR/src/resgx545-data C=$(dirname "$f") K="$C/postrun/paths-as-frozen.txt" perl -e '
        use Digest::SHA qw(sha256_hex);
        sub moved { my $p = shift;
            $p =~ s{^/(?:[^/]+/)*?resgx545-data/}{$ENV{D}/}
                || $p =~ s{^/(?:[^/]+/)*?resgx545/}{$ENV{R}/};
            return $p }
        my @lines = <STDIN>;
        my %abs = map { /^[0-9a-f]{64} [ *](\/.*)$/ ? ($1 => 1) : () } @lines;
        my %keep;
        if (open my $k, "<", $ENV{K}) { while (<$k>) { chomp; $keep{$_} = 1 unless /^#/ } }
        for (@lines) {
            next unless /^([0-9a-f]{64})( [ *])([^\/\n].*)$/;
            my ($h, $sep, $rel) = ($1, $2, $3);
            next if $keep{$rel};
            open my $in, "<", "$ENV{C}/$rel" or next;
            my @l = <$in>; close $in;
            next unless @l && !grep { chomp(my $x = $_); !$abs{$x} } @l;
            my $text = join "", map { chomp(my $x = $_); moved($x) . "\n" } @l;
            open my $out, ">", "$ENV{C}/$rel" or die; print $out $text; close $out;
            $_ = sha256_hex($text) . "$sep$rel\n";
        }
        print @lines;' < "$f" > "$f.new" && mv "$f.new" "$f"
done
# the paths a list of postrun/paths-as-frozen.txt names stay as frozen in the freeze too (data,
# tool, pinned and scratch paths alike: R7-rp's lists name all four)
KEPT=$W/kept-paths
: > "$KEPT"
[ -f "$C/postrun/paths-as-frozen.txt" ] && grep -v '^#' "$C/postrun/paths-as-frozen.txt" \
    | while read -r l; do [ -n "$l" ] && [ -f "$C/$l" ] && cat "$C/$l"; done >> "$KEPT"
# a frozen input read from scratch outside every tree (a plan, a reading of the firmware), named by
# an absolute path under scratch/resgx545/ and pinned by no FROZEN.commits line, is published as
# cited/<path> of a data repository: the copy is put at its scratch place and the freeze points
# there
for f in $(pointed); do
    CM=$(dirname "$f")/FROZEN.commits
    while read -r hash path; do
        case "$path" in /*/scratch/resgx545/*) ;; *) continue ;; esac
        [ -f "$CM" ] && grep -q "^$hash " "$CM" && continue
        rel=${path#*/scratch/resgx545/}
        [ -e "$S/$rel" ] && continue
        for d in "$DATA" "$DATAP"; do
            if [ -n "$d" ] && [ -f "$d/cited/$rel" ]; then
                mkdir -p "$S/$(dirname "$rel")" && cp "$d/cited/$rel" "$S/$rel"
                break
            fi
        done
    done < "$f"
    S=$S P="$CM" K=$KEPT perl -e '
        my %pin;
        if (open my $c, "<", $ENV{P}) { while (<$c>) { $pin{$1} = 1 if /^([0-9a-f]{64})\s/ } }
        open my $k, "<", $ENV{K}; my %k = map { chomp; ($_ => 1) } <$k>;
        while (<STDIN>) {
            s{^([0-9a-f]{64})( [ *])/(?:[^/]+/)*?scratch/resgx545/}{$1$2$ENV{S}/}
                unless $pin{substr($_, 0, 64)} || (m{^[0-9a-f]{64} [ *](.*)$} && $k{$1});
            print;
        }' < "$f" > "$f.new" && mv "$f.new" "$f"
done
for f in $(pointed); do
    R=$R S=$S D=$HOMEDIR/src/resgx545-data K=$KEPT perl -pe \
        'BEGIN { open my $k, "<", $ENV{K}; %k = map { chomp; ($_ => 1) } <$k> }
         m{^[0-9a-f]{64} [ *](.*)$} && $k{$1}
         || m{^[0-9a-f]{64} [ *]\Q$ENV{S}\E/}
         || s{^([0-9a-f]{64} [ *])/(?:[^/]+/)*?resgx545-data/}{$1$ENV{D}/}
         || s{^([0-9a-f]{64} [ *])/(?:[^/]+/)*?resgx545/}{$1$ENV{R}/}' "$f" > "$f.new" \
        && mv "$f.new" "$f"
done
# a pin of a tree that sat under scratch/resgx545/ (round 4's integration worktree closing4/lead/wt)
# is pointed at the pinned worktree by its FROZEN.commits path, matched by hash and path suffix
for f in $(pointed); do
    CM=$(dirname "$f")/FROZEN.commits
    if [ -f "$CM" ]; then
        R=$R P="$CM" K=$KEPT perl -e '
            open my $c, "<", $ENV{P} or die;
            open my $k, "<", $ENV{K}; my %k = map { chomp; ($_ => 1) } <$k>;
            my %pin;
            while (<$c>) { next if /^#/; my ($h, $m, $p) = split; next unless defined $p;
                           $p =~ s{^resgx545:}{}; $pin{$h}{$p} = 1 unless $p =~ /^[a-z][a-z0-9-]*:/ }
            while (<STDIN>) {
                if (/^([0-9a-f]{64} [ *])(\/.*)$/ && $pin{substr($1, 0, 64)} && !$k{$2}) {
                    my ($pre, $path) = ($1, $2);
                    for my $p (keys %{$pin{substr($pre, 0, 64)}}) {
                        if (substr($path, -length($p) - 1) eq "/$p") { $_ = "$pre$ENV{R}/$p\n"; last }
                    }
                }
                print;
            }' < "$f" > "$f.new" && mv "$f.new" "$f"
    fi
done
# a test that names the author's data or tool tree by its absolute path (R6-dpm's
# tests/test_read.py scans render/ that way) would read past the data view and the pinned tree:
# the copy's tests/ files that no freeze names are pointed at the fake home (a frozen file keeps
# the bytes that ran, and its session's verify may want every test file frozen as it is)
FROZEN_REL=$W/frozen-relative
: > "$FROZEN_REL"
for f in $(freezes); do
    d=$(dirname "$f")
    sed -n "s#^[0-9a-f]\{64\} [ *]\([^/].*\)\$#$d/\1#p" "$f" >> "$FROZEN_REL"
done
[ -d "$C/tests" ] && find "$C/tests" -type f -print0 | H=$HOMEDIR/src K=$FROZEN_REL perl -0ne '
    BEGIN { local $/ = "\n"; open my $k, "<", $ENV{K}; %k = map { chomp; ($_ => 1) } <$k> }
    chomp(my $f = $_);
    next if $k{$f};
    open my $in, "<", $f or next; my $t = do { local $/; <$in> }; close $in;
    $t =~ s{(?<![\w.-])/(?:[^/\s"\x27\x60:;()]+/)*?src/(resgx545-data|resgx545)(?![\w-])}{$ENV{H}/$1}g
        or next;
    open my $out, ">", $f or die "$f: $!"; print $out $t; close $out;'

cd "$C" || die "cannot enter the copy"
export HOME=$HOMEDIR PY RESGX545=$R TOOL_SRC=$R RESGX545_MAIN=$R \
    RESGX545_DATA=$HOMEDIR/src/resgx545-data PYTHONDONTWRITEBYTECODE=1
# a variable named in postrun/env-as-frozen.txt is left unset, so the session's own default (the
# path of the freeze) applies: R7-rp's g_rd.py writes the trees it read into a frozen list
if [ -f "$C/postrun/env-as-frozen.txt" ]; then
    for v in $(grep -v '^#' "$C/postrun/env-as-frozen.txt"); do
        case "$v" in RESGX545_MAIN|RESGX545_DATA|RESGX545|TOOL_SRC) unset "$v" ;;
            *) die "postrun/env-as-frozen.txt: $v is not a variable this script sets" ;; esac
    done
fi
case "$ENTRY" in
    *.py) "$PY" "$ENTRY" ;;
    *) bash "$ENTRY" ;;
esac
rc=$?
if [ $rc = 0 ]; then verdict=PASS; else verdict=FAIL; fi
[ $rc = 0 ] && [ -n "$KEY" ] && mkdir -p "$TARGET/passes" \
    && echo "$SESSION $(date '+%Y-%m-%d %H:%M:%S')" > "$TARGET/passes/$KEY"
echo "session_tests: $SESSION $verdict (exit $rc)"
exit $rc
