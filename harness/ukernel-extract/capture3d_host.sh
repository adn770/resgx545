#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
#
# capture3d_host.sh: one 3D capture table on a capture host (README "3D capture"), run by
# the campaign runner (tools/campaign, a capture table whose template names the list) in a
# work directory holding the harness sources and the list. It builds fakedrm.so,
# libpvrFAKEWSEGL.so, loader, tri and tri1, stages the closed usr/lib
# ($RESGX545_CDV_LIBS) so that every name of a library opens the one file, runs srvinit once
# for the init info, runs the list through capture3d.sh one run at a time, and keeps each run
# as $OUT/<name>.tar.xz (tri.out, powervr.ini, drm.log and dump3d/, a reproducible archive)
# and capture3d.sh's line per run in $OUT/runs.txt. Nothing here touches a GPU.
#
#   OUT=dir RESGX545_CDV_LIBS=dir sh capture3d_host.sh <list> [name...]
set -eu

list=${1:?usage: capture3d_host.sh <list> [name...]}
shift
: "${OUT:?set OUT}"
LIBS=${RESGX545_CDV_LIBS:-$HOME/resgx545-uk3d/lib}
V=1.7.862890
for lib in libsrv_um libsrv_init libEGL libIMGegl libGLESv2 libGLES_CM libglslcompiler libusc; do
    [ -e "$LIBS/$lib.so.$V" ] || {
        echo "capture3d_host.sh: $LIBS/$lib.so.$V not found;" \
            "set RESGX545_CDV_LIBS to the usr/lib/ directory of your Cedarview package" >&2
        exit 1
    }
done
here=$PWD

# The staged lib/: a link per file, then every unversioned name of a library (libX.so,
# libX.so.N) at its one versioned file, whether the copy kept the package's links or made
# them files; a library loaded twice under two names keeps two states (no current context
# in the second). libGLESv1_CM is the package's other name of libGLES_CM.
mkdir -p uk/lib
for f in "$LIBS"/*; do ln -sfn "$f" uk/lib/; done
for v in "$LIBS"/*.so.$V; do
    b=$(basename "$v" ".$V")
    for l in "uk/lib/$b" uk/lib/"$b".[0-9]; do
        if [ -e "$l" ] || [ -L "$l" ]; then ln -sfn "$v" "$l"; fi
    done
done
for l in uk/lib/libGLESv1_CM.so uk/lib/libGLESv1_CM.so.1; do
    ln -sfn "$LIBS/libGLES_CM.so.$V" "$l"
done
rm -f uk/lib/libpvrFAKEWSEGL.so

gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 -shared -fPIC fakewsegl.c -o uk/lib/libpvrFAKEWSEGL.so
gcc -m32 loader.c -o loader -ldl
gcc -m32 tri.c -o tri -ldl -lm
gcc -m32 tri1.c -o tri1 -ldl -lm
# the shader corpus's files (shaders3d.txt names them under shaders/)
if [ -e gen_shaders3d.py ]; then python3 gen_shaders3d.py; fi

# srvinit once, for the init info the client stacks read back (devinit.bin)
mkdir -p init
ln -sfn "$here/uk/lib" init/lib
SGX_UK_DIR=$here/init LD_LIBRARY_PATH=$here/uk/lib LD_PRELOAD=./fakedrm.so ./loader \
    > init.log 2>&1
cp init/dump/devinitpart2_in.bin uk/devinit.bin
printf '[default]\nWindowSystem=libpvrFAKEWSEGL.so\n' > uk/powervr.ini

{
    uname -srm
    gcc --version | head -1
} > "$OUT/host.txt"
# One run at a time, archived and removed before the next: a run's snapshots take tens of
# megabytes, and the work directory may be a small tmpfs.
: > "$OUT/runs.txt"
grep -v '^[[:space:]]*\(#\|$\)' "$list" | while read -r name _; do
    if [ $# -gt 0 ]; then
        case " $* " in *" $name "*) ;; *) continue ;; esac
    fi
    SGX_UK_DIR=$here/uk sh ./capture3d.sh "$list" "$name" >> "$OUT/runs.txt" < /dev/null
    d=uk/var/$name
    keep=
    for f in tri.out powervr.ini drm.log dump3d; do
        if [ -e "$d/$f" ]; then keep="$keep $f"; fi
    done
    # a run that left nothing gets no archive (an empty one would unpack as an empty run)
    if [ -n "$keep" ]; then
        # shellcheck disable=SC2086  # the kept names are separate words
        tar -C "$d" --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner -cf - $keep \
            | xz -6 > "$OUT/$name.tar.xz"
    fi
    rm -rf "$d"
done
cat "$OUT/runs.txt"
