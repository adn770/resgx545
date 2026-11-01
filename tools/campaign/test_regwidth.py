# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Register width tables (regwidth.py) and the laptop program that measures them
(regwidth.c): which bits of a register take a write, measured in small batches with the
GPU checked after each, never on a register of the program's own deny list."""
import pathlib
import re
import shutil
import subprocess

import pytest

import regwidth

HERE = pathlib.Path(__file__).resolve().parent

TABLE = '''kind = "regwidth"
name = "platform-register-widths"
needs = ["kreg", "regs"]

[[register]]
offset = 0x0418
name = "CR_ISP_LINE_SAMPLE_POS"
batch = 1

[[register]]
offset = 0x0520
name = "CR_ISP_SAMPLE_POS"
batch = 1

[[register]]
offset = 0x0148
name = "CR_REG_0148"
batch = 2

[[readonly]]
offset = 0x0080
name = "CR_SOFT_RESET"
reason = "a write resets the units whose bits it sets"

[[readonly]]
offset = 0x0ac8
name = "CR_EVENT_KICK"
reason = "a write starts the EDM"
read = false
'''


def write(tmp_path, text=TABLE) -> pathlib.Path:
    p = tmp_path / "register-widths.toml"
    p.write_text(text)
    return p


# ---- the table ---------------------------------------------------------------------------

def test_a_table_loads_its_registers_by_batch(tmp_path):
    t = regwidth.load(write(tmp_path))
    assert t.name == "platform-register-widths"
    assert t.batches() == [1, 2]
    assert [r.offset for r in t.batch(1)] == [0x0418, 0x0520]
    assert [r.name for r in t.batch(2)] == ["CR_REG_0148"]
    assert [(r.offset, r.read) for r in t.readonly] == [(0x0080, True), (0x0ac8, False)]


@pytest.mark.parametrize("bad, why", [
    (TABLE.replace("offset = 0x0418", "offset = 0x0419"), "dword"),
    (TABLE.replace("offset = 0x0418", "offset = 0x1000"), "below 0x1000"),
    (TABLE.replace("offset = 0x0520", "offset = 0x0418"), "twice"),
    (TABLE.replace("offset = 0x0ac8", "offset = 0x0148"), "twice"),
    (TABLE.replace('reason = "a write starts the EDM"\n', ""), "reason"),
    (TABLE.replace("batch = 2", "batch = 0"), "batch"),
    (TABLE.replace('kind = "regwidth"', 'kind = "script"'), "regwidth"),
])
def test_a_bad_table_is_refused(tmp_path, bad, why):
    with pytest.raises(regwidth.RegwidthError, match=why):
        regwidth.load(write(tmp_path, bad))


@pytest.mark.parametrize("off", [0x0000, 0x0080, 0x0134, 0x0200, 0x0224, 0x024c, 0x0428,
                                 0x0430, 0x043c, 0x0450, 0x0648, 0x064c, 0x0658, 0x0680,
                                 0x0804, 0x0a08, 0x0a48, 0x0a58, 0x0aa4, 0x0ab8, 0x0ac8,
                                 0x0b0c, 0x0b14, 0x0b98, 0x0b80, 0x0c84, 0x0e80])
def test_the_deny_list_refuses_a_write_to_bus_clock_reset_event_edm_and_mmu(tmp_path, off):
    bad = TABLE.replace("offset = 0x0148", f"offset = {off:#06x}")
    with pytest.raises(regwidth.RegwidthError, match="deny"):
        regwidth.load(write(tmp_path, bad))


# what a read-only reason says a write would do, when the write must never happen
STARTS = re.compile(r"\bstart|\binject|invalidat|could find no slot|pulse")
TABLE_PATH = HERE.parent.parent / "probes" / "platform" / "register-widths.toml"


def test_every_register_whose_write_starts_work_is_on_the_deny_list():
    t = regwidth.load(TABLE_PATH)
    starts = [r for r in t.readonly if STARTS.search(r.reason)]
    assert len(starts) > 20
    assert [hex(r.offset) for r in starts if not regwidth.denied(r.offset)] == []


def test_a_reason_says_deny_list_exactly_when_the_deny_list_holds_the_register():
    t = regwidth.load(TABLE_PATH)
    bad = [hex(r.offset) for r in t.readonly
           if regwidth.denied(r.offset) != r.reason.endswith("(deny list)")]
    assert bad == []


def test_the_deny_list_takes_no_register_the_table_writes():
    t = regwidth.load(TABLE_PATH)      # load refuses a written register on the deny list
    assert t.registers and not any(regwidth.denied(r.offset) for r in t.registers)


def test_the_python_deny_list_is_the_programs():
    src = (HERE / "regwidth.c").read_text()
    block = re.search(r"deny\[\]\[2\] = \{(.*?)\};", src, re.S).group(1)
    pairs = [(int(a, 16), int(b, 16)) for a, b in
             re.findall(r"\{\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+)\s*\}", block)]
    assert pairs == list(regwidth.DENY)


# ---- the laptop script ---------------------------------------------------------------------

THREE = TABLE.replace("""[[readonly]]
offset = 0x0080""", """[[register]]
offset = 0x0400
name = "CR_REG_0400"
batch = 3

[[readonly]]
offset = 0x0080""")


def test_the_script_runs_the_batches_in_order_gated_and_checked(tmp_path):
    s = regwidth.script(regwidth.load(write(tmp_path, THREE)))
    assert "regwidth.c" in s and "gcc" in s
    regs = {1: "0x0418,0x0520", 2: "0x0148", 3: "0x0400"}
    at = [0]
    for n in (1, 2, 3):
        # gate n, then batch n's write, then check n, and only then batch n + 1
        gate = s.index(f"\ngate {n}\n")
        rw = s.index(f'"$RW" {regs[n]} ||')
        check = s.index(f"\ncheck {n}\n")
        assert at[-1] < gate < rw < check
        at.append(check)
    assert s.count("\ngate ") == 3 and s.count("\ncheck ") == 4     # the start check too
    assert "solid fill correct" in s and "diff: 0 " in s
    # the read-only registers that may be read are snapshotted, the others never named
    assert "0x0080" in s and "0x0ac8" not in s


# The script run with bash against stubs of sudo, gcc and sha256sum: sudo answers for the
# debugfs files, the triangle and regwidth, and logs every regwidth call.
SUDO = r"""#!/bin/sh
[ "$1" = "-n" ] && shift
count() { n=$(( $(cat "$STUB/$1" 2>/dev/null || echo 0) + 1 )); echo $n > "$STUB/$1"; echo $n; }
case "$1" in
sh) echo /fake/sgx ;;
cat) case "$2" in
	*/status) echo "loaded 1 live 1 sw_events 1 bif_faults 0" ;;
	*/xfer_fill) echo "fill 64x32: solid fill correct" ;;
	esac ;;
tee) cat >/dev/null; [ "$(count idle)" != "${IDLE_FAIL_AT:-0}" ] ;;
*/regwidth) shift; echo "regwidth $*" >> "$STUB/calls" ;;
*) [ "$(count tri)" = "${TRI_FAIL_AT:-0}" ] && echo "diff: 7 of 4096 pixels" \
	|| echo "diff: 0 of 4096 pixels" ;;
esac
"""


def run_script(tmp_path, env):
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("no bash")
    stub = tmp_path / "stub"
    stub.mkdir()
    for name, text in [("sudo", SUDO), ("gcc", "#!/bin/sh\nexit 0\n"),
                       ("sha256sum", "#!/bin/sh\necho 0\n")]:
        (stub / name).write_text(text)
        (stub / name).chmod(0o755)
    s = regwidth.script(regwidth.load(write(tmp_path, THREE)))
    r = subprocess.run([bash, "-c", s], capture_output=True, text=True, timeout=30,
                       env={"PATH": f"{stub}:/usr/bin:/bin", "STUB": str(stub),
                            "SGXFIVE_PROBE_BINS": str(tmp_path),
                            "SGXFIVE_TEST": "/fake/sgxfive-test", **env})
    calls = (stub / "calls").read_text().splitlines() if (stub / "calls").exists() else []
    return r, [c for c in calls if " -r " not in c]


def test_the_script_runs_every_batch_when_every_check_passes(tmp_path):
    r, writes = run_script(tmp_path, {})
    assert r.returncode == 0, r.stdout
    assert writes == ["regwidth 0x0418,0x0520", "regwidth 0x0148", "regwidth 0x0400"]
    assert "## done" in r.stdout


def test_a_failed_check_stops_the_script_before_the_next_batch(tmp_path):
    # the triangle of check 2 (the third: start, 1, 2) draws wrong
    r, writes = run_script(tmp_path, {"TRI_FAIL_AT": "3"})
    assert r.returncode == 1
    assert "## check 2: FAILED" in r.stdout and "#### batch 3" not in r.stdout
    assert writes == ["regwidth 0x0418,0x0520", "regwidth 0x0148"]


def test_a_batch_whose_gate_finds_the_firmware_busy_writes_nothing(tmp_path):
    r, writes = run_script(tmp_path, {"IDLE_FAIL_AT": "2"})
    assert r.returncode == 1
    assert "## batch 2: firmware not live or not idle" in r.stdout
    assert writes == ["regwidth 0x0418,0x0520"]


# ---- the output -------------------------------------------------------------------------------

OUT = """#### batch 1
regwidth 0x0418 prior 0x00000001 ones 0x00000001 back 0x00000001 zero 0x00000000 restored 0x00000001
regwidth 0x0520 prior 0x00000000 ones 0xffffffff back 0x00000000 zero 0x00000000 restored 0x00000000
regwidth 0x0148 prior 0x00000010 ones 0x000000f0 back 0x00000010 zero 0x00000010 restored 0x00000010
regwidth 0x0600 moving 0x00000001 0x00000002
regval 0x0080 0x00000000
## check batch 1: ok
"""


def test_the_output_gives_the_bits_that_took_a_write():
    r = regwidth.parse(OUT)
    assert r[0x0418].implemented == 0x1
    assert r[0x0520].implemented == 0xffffffff
    # 0x0148: bit 4 reads 1 whatever is written, bits 7:5 take a write
    assert r[0x0148].implemented == 0xe0 and r[0x0148].stuck == 0x10
    assert r[0x0148].restored_ok
    assert r[0x0600].moving and r[0x0600].implemented is None


def test_a_register_left_changed_is_reported():
    out = OUT.replace("restored 0x00000010", "restored 0x00000000")
    assert not regwidth.parse(out)[0x0148].restored_ok


def test_the_summary_lists_each_register_with_its_bits(tmp_path):
    t = regwidth.load(write(tmp_path))
    text = regwidth.render(t, regwidth.parse(OUT))
    assert '[reg."0x0520"]' in text and 'implemented = "31:0"' in text
    assert '[reg."0x0148"]' in text and 'stuck = "4"' in text and 'implemented = "7:5"' in text
    assert 'name = "CR_ISP_LINE_SAMPLE_POS"' in text
    assert 'reason = "a write starts the EDM"' in text


def test_ranges_write_masks_high_bits_first():
    assert regwidth.ranges(0xffffffff) == "31:0"
    assert regwidth.ranges(0x0f000011) == "27:24, 4, 0"
    assert regwidth.ranges(0) == "-"


# ---- the program, against a plain file -----------------------------------------------------

@pytest.fixture(scope="module")
def program(tmp_path_factory):
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("no C compiler")
    exe = tmp_path_factory.mktemp("rw") / "regwidth"
    subprocess.run([cc, "-O2", "-Wall", "-Werror", "-o", str(exe), str(HERE / "regwidth.c")],
                   check=True)
    return exe


def bank(tmp_path, words: dict[int, int]) -> pathlib.Path:
    b = bytearray(0x1000)
    for off, v in words.items():
        b[off:off + 4] = v.to_bytes(4, "little")
    f = tmp_path / "bank"
    f.write_bytes(bytes(b))
    return f


def run(program, f, *args):
    env = {"REGWIDTH_MEM": str(f), "REGWIDTH_BASE": "0", "PATH": "/usr/bin:/bin"}
    return subprocess.run([str(program), *args], capture_output=True, text=True, env=env,
                          timeout=10)


def test_the_program_writes_ones_zero_and_restores(program, tmp_path):
    f = bank(tmp_path, {0x0418: 0x1, 0x041c: 0x12345678})
    before = f.read_bytes()
    r = run(program, f, "0x0418-0x041c")
    assert r.returncode == 0, r.stderr
    got = regwidth.parse(r.stdout)
    assert got[0x0418].prior == 1 and got[0x0418].implemented == 0xffffffff
    assert got[0x041c].prior == 0x12345678 and got[0x041c].restored_ok
    assert f.read_bytes() == before                      # every register put back


def test_the_program_reads_only_with_r(program, tmp_path):
    f = bank(tmp_path, {0x0080: 0x4, 0x0c84: 0x1000})
    before = f.read_bytes()
    r = run(program, f, "-r", "0x0080,0x0c84")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["regval 0x0080 0x00000004", "regval 0x0c84 0x00001000"]
    assert f.read_bytes() == before


@pytest.mark.parametrize("regs", ["0x0080", "0x0418,0x0c00", "0x0100-0x0140", "0x0ac8"])
def test_the_program_refuses_its_deny_list_before_writing_anything(program, tmp_path, regs):
    f = bank(tmp_path, {0x0418: 0x1})
    before = f.read_bytes()
    r = run(program, f, regs)
    assert r.returncode == 2 and "deny" in r.stderr
    assert r.stdout == "" and f.read_bytes() == before


@pytest.mark.parametrize("args", [[], ["0x0419"], ["0x1000"], ["-r"], ["-x", "0x0418"]])
def test_the_program_usage(program, tmp_path, args):
    r = run(program, bank(tmp_path, {}), *args)
    assert r.returncode == 2


# ---- the program's failure paths, through the test build's faults --------------------------

@pytest.fixture(scope="module")
def faulty(tmp_path_factory):
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("no C compiler")
    exe = tmp_path_factory.mktemp("rwt") / "regwidth"
    subprocess.run([cc, "-O2", "-Wall", "-Werror", "-DREGWIDTH_TEST", "-o", str(exe),
                    str(HERE / "regwidth.c")], check=True)
    return exe


def run_faulty(program, f, *args, **faults):
    env = {"REGWIDTH_MEM": str(f), "REGWIDTH_BASE": "0", "PATH": "/usr/bin:/bin", **faults}
    return subprocess.run([str(program), *args], capture_output=True, text=True, env=env,
                          timeout=10)


def test_a_failed_restore_is_written_again_and_stops_the_program(faulty, tmp_path):
    f = bank(tmp_path, {0x0418: 0x5, 0x041c: 0x12345678})
    r = run_faulty(faulty, f, "0x0418-0x041c", REGWIDTH_DROP="0x0418")
    assert r.returncode == 3
    out = r.stdout.splitlines()
    assert out == ["regwidth 0x0418 prior 0x00000005 ones 0xffffffff back 0x00000005 "
                   "zero 0x00000000 restored 0x00000000",
                   "regwidth 0x0418 not restored: reads 0x00000000"]
    # ones, prior, zero, prior, then the prior once more; 0x041c is never touched
    assert r.stderr.splitlines() == [f"write 0x0418 0x{v:08x}"
                                     for v in (0xffffffff, 5, 0, 5, 5)]
    assert f.read_bytes()[0x041c:0x0420] == (0x12345678).to_bytes(4, "little")
    assert not regwidth.parse(r.stdout)[0x0418].restored_ok


def test_a_register_that_moves_is_not_written(faulty, tmp_path):
    f = bank(tmp_path, {0x0418: 0x5, 0x041c: 0x7})
    r = run_faulty(faulty, f, "0x0418-0x041c", REGWIDTH_MOVING="0x0418")
    assert r.returncode == 0, r.stderr
    got = regwidth.parse(r.stdout)
    assert got[0x0418].moving and got[0x0418].values == [6, 7]
    assert not any(line.startswith("write 0x0418") for line in r.stderr.splitlines())
    assert got[0x041c].restored_ok and got[0x041c].implemented == 0xffffffff
