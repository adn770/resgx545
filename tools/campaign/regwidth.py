# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Register width tables: which bits of a register take a write, measured on the laptop by
regwidth.c through /dev/mem, batch by batch, with the GPU checked after each batch.

A regwidth table (probes/<unit>/<feature>.toml, named <unit>-<feature>) lists the registers to
measure, each in a numbered batch, and the registers kept read-only, each with its reason:

    kind = "regwidth"
    name = "platform-register-widths"
    needs = ["kreg", "regs"]

    [[register]]                  # written with all ones, its value, zero, its value
    offset = 0x0418
    name = "CR_ISP_LINE_SAMPLE_POS"
    batch = 1

    [[readonly]]                  # never written; read before the first batch and after
    offset = 0x0080               # the last, unless read = false (a register whose read
    name = "CR_SOFT_RESET"        # the kernel's register file skips)
    reason = "a write resets the units whose bits it sets"

A register on the program's own deny list (DENY, the same as regwidth.c's) is refused in a
table's write list: the deny list is the floor, the table's read-only list adds to it. A
read-only register's reason ends in "(deny list)" exactly when the deny list holds it, and every
register whose write starts work, invalidates a cache or could inject a task is on it.

The laptop script (script()) compiles regwidth.c, and for each batch in order checks that the
firmware is live and idle (a debugfs kreg write of 0x0810 with itself, which the kernel
refuses while a job is queued), runs the write test, then checks that a debugfs fill and the
triangle still draw clean and that no MMU fault was added; the first failed check stops the
script (exit 1) and no later batch runs. The gate is a check before the writes, not a lock: a
job queued between it and the writes is not excluded, and only the check after the batch would
show its effect. parse() reads the output; a register's implemented
bits are those that read 1 after all ones and 0 after zero (`ones & ~zero`); `stuck` are the
bits that read 1 after zero. render() writes the summary kept beside the output.
"""
from __future__ import annotations

import dataclasses
import re
import tomllib
import pathlib

# never written (regwidth.c's deny list): inclusive offset ranges
DENY = (
    (0x0000, 0x000C),     # clock gating control, status, override
    (0x0080, 0x0080),     # soft reset
    (0x0110, 0x0144),     # event enable, clear, status; PDS cache events; timer
    (0x0200, 0x0200),     # VDM start
    (0x0224, 0x0224),     # TE tail-pointer cache clear and flush
    (0x024C, 0x024C),     # MTE OTPM operation
    (0x0428, 0x0428),     # ISP start render
    (0x0430, 0x0430),     # a write the kernel's register file treats as starting work
    (0x043C, 0x043C),     # TSP parameter cache invalidate
    (0x0450, 0x0450),     # a write the kernel's register file treats as starting work
    (0x063C, 0x063C),     # DPM 3D deallocate
    (0x0648, 0x064C),     # DPM TA allocate, DPM 3D
    (0x0658, 0x0658),     # DPM partial render
    (0x0680, 0x06A0),     # DPM tasks, out-of-memory response, free context
    (0x0804, 0x0804),     # cache control: invalidates
    (0x0A08, 0x0A08),     # USSE instruction cache invalidate
    (0x0A0C, 0x0A48),     # USSE code bases, the EDM's among them
    (0x0A58, 0x0A70),     # event-to-PDS enable and the event PDS programs
    (0x0AA4, 0x0AA8),     # USSE slot allocation, USSE 0 and 1
    (0x0AB8, 0x0AB8),     # PDS execution base
    (0x0AC4, 0x0AEC),     # event kicker, kicks, EDM timer, PDS invalidates
    (0x0B0C, 0x0B20),     # USSE 0 and 1 service queues, the EDM task registers
    (0x0B80, 0x0B98),     # USSE slot allocation and service queues, USSE 2 and 3
    (0x0C00, 0x0CFC),     # BIF: MMU control, faults, directories, banks, requestors
    (0x0E80, 0x0E80),     # HWPerf pulse
)
ALL = 0xFFFFFFFF


class RegwidthError(Exception):
    pass


@dataclasses.dataclass
class Register:
    offset: int
    name: str
    batch: int


@dataclasses.dataclass
class ReadOnly:
    offset: int
    name: str
    reason: str
    read: bool = True


@dataclasses.dataclass
class Table:
    name: str
    registers: list[Register]
    readonly: list[ReadOnly]

    def batches(self) -> list[int]:
        return sorted({r.batch for r in self.registers})

    def batch(self, n: int) -> list[Register]:
        return [r for r in self.registers if r.batch == n]


def denied(off: int) -> bool:
    return any(lo <= off <= hi for lo, hi in DENY)


def _offset(e: dict, where: str) -> int:
    off = e.get("offset")
    if not isinstance(off, int) or off % 4:
        raise RegwidthError(f"{where}: offset {off!r} is not a dword offset")
    if not 0 <= off < 0x1000:
        raise RegwidthError(f"{where}: offset {off:#06x} is not below 0x1000")
    return off


def load(path: pathlib.Path) -> Table:
    """The table, checked: dword offsets below 0x1000, each named once, a reason for every
    read-only register, a positive batch for every written one, none on the deny list."""
    path = pathlib.Path(path)
    spec = tomllib.loads(path.read_text())
    if spec.get("kind") != "regwidth":
        raise RegwidthError(f"{path.name}: not a regwidth table (kind = \"regwidth\")")
    regs, ro, seen = [], [], set()
    for e in spec.get("register", []):
        where = f"{path.name}: register {e.get('name', '?')}"
        off = _offset(e, where)
        b = e.get("batch")
        if not isinstance(b, int) or isinstance(b, bool) or b < 1:
            raise RegwidthError(f"{where}: batch {b!r} is not a positive number")
        if denied(off):
            raise RegwidthError(f"{where}: {off:#06x} is on the deny list; it is never written")
        regs.append(Register(off, str(e.get("name", "")), b))
    for e in spec.get("readonly", []):
        where = f"{path.name}: readonly {e.get('name', '?')}"
        off = _offset(e, where)
        if not str(e.get("reason", "")).strip():
            raise RegwidthError(f"{where}: no reason")
        ro.append(ReadOnly(off, str(e.get("name", "")), e["reason"], bool(e.get("read", True))))
    for r in [*regs, *ro]:
        if r.offset in seen:
            raise RegwidthError(f"{path.name}: {r.offset:#06x} is listed twice")
        seen.add(r.offset)
    if not regs:
        raise RegwidthError(f"{path.name}: no register to write")
    return Table(str(spec.get("name", "")), regs, ro)


def _offs(offs: list[int]) -> str:
    return ",".join(f"{o:#06x}" for o in offs)


HEAD = r"""set -u
D=$(sudo -n sh -c 'ls -d /sys/kernel/debug/dri/*/sgx' 2>/dev/null | head -n 1)
[ -n "$D" ] || { echo "no sgx debugfs directory (debug option off?)"; exit 1; }
T=${SGXFIVE_TEST:-$HOME/sgxfive-test}
B=$SGXFIVE_PROBE_BINS
gcc -O2 -Wall -o "$B/regwidth" "$B/regwidth.c" || { echo "regwidth.c does not build"; exit 1; }
RW=$B/regwidth
echo "## uname"; uname -r
echo "## firmware"; sha256sum /lib/firmware/sgx545_ukernel.fw
faults() { sudo -n cat "$D/status" | head -n 1 | sed -n 's/.*bif_faults \([0-9]*\).*/\1/p'; }
F0=$(faults)
# live and idle: the kernel takes a kreg write only with the firmware live and no job queued
idle() { echo '0x0810^=0x0' | sudo -n tee "$D/kreg" >/dev/null 2>&1; }
gate() {
	if ! idle; then echo "## batch $1: firmware not live or not idle"; exit 1; fi
	echo "## batch $1: firmware live and idle"
}
# a debugfs fill and the triangle draw clean, and no MMU fault was added
check() {
	echo "## check $1"
	sudo -n cat "$D/status" | head -n 1
	fill=$(sudo -n cat "$D/xfer_fill" 2>&1)
	nfill=$(echo "$fill" | grep -c '^fill ')
	nok=$(echo "$fill" | grep -c 'solid fill correct')
	tri=$(sudo -n "$T" tri 2>&1 | grep '^diff')
	echo "fills $nfill, correct $nok; $tri"
	ok=1
	[ "$nfill" -gt 0 ] && [ "$nfill" -eq "$nok" ] || ok=0
	case "$tri" in "diff: 0 "*) ;; *) ok=0;; esac
	[ "$(faults)" = "$F0" ] || ok=0
	if [ $ok = 1 ]; then echo "## check $1: ok"; else echo "## check $1: FAILED"; exit 1; fi
}
"""


def script(t: Table) -> str:
    """The laptop script of a table: the read-only snapshot, then each batch gated and
    checked, then the read-only snapshot again."""
    readable = [r.offset for r in t.readonly if r.read]
    out = [HEAD, "check start"]
    if readable:
        out += ['echo "#### read-only before"', f'sudo -n "$RW" -r {_offs(readable)}']
    for n in t.batches():
        out += [f'echo "#### batch {n}"', f"gate {n}",
                f'sudo -n "$RW" {_offs([r.offset for r in t.batch(n)])} || '
                f'{{ rc=$?; echo "## batch {n}: regwidth exit $rc"; exit 1; }}',
                f"check {n}"]
    if readable:
        out += ['echo "#### read-only after"', f'sudo -n "$RW" -r {_offs(readable)}']
    out.append('echo "## done"')
    return "\n".join(out) + "\n"


@dataclasses.dataclass
class Reading:
    offset: int
    prior: int | None = None
    ones: int | None = None
    back: int | None = None
    zero: int | None = None
    restored: int | None = None
    moving: bool = False
    values: list[int] = dataclasses.field(default_factory=list)

    @property
    def implemented(self) -> int | None:
        """The bits that took a write: 1 after all ones, 0 after zero."""
        if self.moving or self.ones is None or self.zero is None:
            return None
        return self.ones & ~self.zero & ALL

    @property
    def stuck(self) -> int | None:
        """The bits that read 1 after a write of zero."""
        if self.moving or self.ones is None or self.zero is None:
            return None
        return self.ones & self.zero

    @property
    def restored_ok(self) -> bool:
        return self.prior is not None and self.restored == self.prior


_W = re.compile(r"^regwidth 0x([0-9a-f]{4}) prior 0x([0-9a-f]{8}) ones 0x([0-9a-f]{8}) "
                r"back 0x([0-9a-f]{8}) zero 0x([0-9a-f]{8}) restored 0x([0-9a-f]{8})$")
_M = re.compile(r"^regwidth 0x([0-9a-f]{4}) moving 0x([0-9a-f]{8}) 0x([0-9a-f]{8})$")
_V = re.compile(r"^regval 0x([0-9a-f]{4}) 0x([0-9a-f]{8})$")


def parse(out: str) -> dict[int, Reading]:
    """{offset: Reading} of a regwidth output (the script's, or the program's alone)."""
    res: dict[int, Reading] = {}
    for line in out.splitlines():
        line = line.strip()
        if m := _W.match(line):
            off, *v = (int(x, 16) for x in m.groups())
            r = res.setdefault(off, Reading(off))
            r.prior, r.ones, r.back, r.zero, r.restored = v
        elif m := _M.match(line):
            off, a, b = (int(x, 16) for x in m.groups())
            r = res.setdefault(off, Reading(off))
            r.moving, r.values = True, [a, b]
        elif m := _V.match(line):
            off, v = (int(x, 16) for x in m.groups())
            res.setdefault(off, Reading(off)).values.append(v)
    return res


def ranges(mask: int) -> str:
    """The set bits of a mask as ranges, high first: 31:0, 27:24, 4, 0."""
    out, bit = [], 31
    while bit >= 0:
        if mask >> bit & 1:
            lo = bit
            while lo > 0 and mask >> (lo - 1) & 1:
                lo -= 1
            out.append(f"{bit}:{lo}" if lo != bit else str(bit))
            bit = lo - 1
        else:
            bit -= 1
    return ", ".join(out) or "-"


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(t: Table, res: dict[int, Reading]) -> str:
    """The summary (TOML): per written register its readings and bits, per read-only
    register its reason and the values read."""
    lines = [f"# regwidth summary of {t.name}: implemented = the bits that took a write "
             "(1 after all ones, 0 after zero); stuck = the bits that read 1 after zero.", ""]
    for reg in sorted(t.registers, key=lambda r: r.offset):
        r = res.get(reg.offset)
        lines += [f'[reg."{reg.offset:#06x}"]', f"name = {_q(reg.name)}", f"batch = {reg.batch}"]
        if r is None:
            lines += ["measured = false", ""]
            continue
        if r.moving:
            lines += ["moving = true",
                      "values = [" + ", ".join(f'"{v:#010x}"' for v in r.values) + "]", ""]
            continue
        lines += [f'{k} = "{getattr(r, k):#010x}"'
                  for k in ("prior", "ones", "back", "zero", "restored")]
        lines += [f'implemented = "{ranges(r.implemented)}"',
                  f"width = {bin(r.implemented).count('1')}",
                  f'stuck = "{ranges(r.stuck)}"',
                  f"restored_ok = {'true' if r.restored_ok else 'false'}", ""]
    for ro in sorted(t.readonly, key=lambda r: r.offset):
        r = res.get(ro.offset)
        lines += [f'[readonly."{ro.offset:#06x}"]', f"name = {_q(ro.name)}",
                  f"reason = {_q(ro.reason)}"]
        if ro.read and r is not None:
            lines.append("values = [" + ", ".join(f'"{v:#010x}"' for v in r.values) + "]")
        elif not ro.read:
            lines.append("read = false")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
