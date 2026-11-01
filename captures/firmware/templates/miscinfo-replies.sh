# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Run srvinit under the harness at the REV1 layout once per GETMISCINFO reply (fakedrm.c's
# MISC_REPLY), and the plausible reply twice; keep each run's dump, log and decoded init info.
set -eu
LIBS=${RESGX545_CDV_LIBS:-$HOME/resgx545-uk/lib}
for lib in libsrv_um libsrv_init; do
    [ -e "$LIBS/$lib.so.1.7.862890" ] || {
        echo "miscinfo-replies.sh: $LIBS/$lib.so.1.7.862890 not found;" \
            "set RESGX545_CDV_LIBS to the usr/lib/ directory of your Cedarview package" >&2
        exit 1
    }
done
gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 loader.c -o loader -ldl
run() {
    name=$1
    shift
    stage=$PWD/stage-$name
    rm -rf "$stage"
    mkdir -p "$stage/lib"
    for lib in libsrv_um libsrv_init; do
        ln -sf "$LIBS/$lib.so.1.7.862890" "$stage/lib/$lib.so.1.7.862890"
        ln -sf "$lib.so.1.7.862890" "$stage/lib/$lib.so"
    done
    status=0
    env SGX_UK_DIR="$stage" "$@" MOCK_HEAP_BASE_2=0x30000000 MOCK_HEAP_BASE_3=0x32000000 \
        MOCK_HEAP_BASE_4=0x37000000 MOCK_HEAP_BASE_5=0x3C000000 MOCK_HEAP_BASE_6=0x2E000000 \
        LD_LIBRARY_PATH="$stage/lib" LD_PRELOAD=./fakedrm.so ./loader > "$OUT/$name.log" 2>&1 ||
        status=$?
    mkdir -p "$OUT/$name"
    cp "$stage"/dump/* "$stage/drm.log" "$OUT/$name/"
    python3 initinfo.py "$OUT/$name/devinitpart2_in.bin" > "$OUT/$name/initinfo.txt"
    echo "$name: exit $status, $(ls "$OUT/$name" | wc -l) files"
}
run reply_untouched MISC_REPLY=untouched
run reply_zero MISC_REPLY=zero
run reply_plausible MISC_REPLY=plausible
run reply_mismatched MISC_REPLY=mismatched
run reply_plausible_again MISC_REPLY=plausible
