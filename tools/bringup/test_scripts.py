"""The test-cycle scripts take their hosts, paths and ports from the environment.

push-gma500.sh is checked in dry-run mode (SGX_DRY_RUN=1 prints the commands instead of
running them), so no build host or laptop is needed. test-session.sh only runs on the
laptop; here we check that it refuses to start without a netconsole target.
netconsole-listen.py is run for real on a free local port.
"""
from __future__ import annotations

import os
import pathlib
import socket
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PUSH = HERE / "push-gma500.sh"
SESSION = HERE / "test-session.sh"
PUSH_TOOLS = HERE / "push-tools.sh"
LISTEN = HERE / "netconsole-listen.py"


def clean_env(**extra: str) -> dict[str, str]:
    """The caller's environment without any SGX_* setting, plus extra."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("SGX_")}
    env["SGX_LOCAL_ENV"] = os.devnull       # never pick up the developer's local.env
    env.update(extra)
    return env


def push(*args: str, **extra: str) -> str:
    out = subprocess.run(["bash", str(PUSH), *args], env=clean_env(SGX_DRY_RUN="1", **extra),
                         capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_push_defaults_to_ssh_aliases():
    out = push()
    assert "ssh sgx-build " in out
    assert "sgx-target:/tmp/" in out
    assert "cd src/linux-sgx" in out
    assert "vermagic=7.3.0-sgx " in out
    assert "/usr/lib/modules/7.3.0-sgx/" in out
    assert "-j\\$(nproc)" in out or "-j$(nproc)" in out


def test_push_takes_hosts_and_paths_from_the_environment():
    out = push(SGX_BUILD_HOST="builder", SGX_TARGET_HOST="me@laptop",
               SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box", SGX_KERNEL_TREE="work/linux",
               SGX_KERNEL_RELEASE="7.4.0-sgx", SGX_BUILD_JOBS="8",
               SGX_BUILD_PATH="~/.local/bin", SGX_NETCONSOLE_HOST="10.1.2.3",
               SGX_NETCONSOLE_PORT="7777")
    assert "ssh builder " in out
    assert "builder:work/linux/drivers/gpu/drm/gma500/gma500_gfx.ko" in out
    assert "-o HostKeyAlias=box me@laptop" in out
    assert "me@laptop:/tmp/" in out
    assert "cd work/linux" in out
    assert "-j8 " in out
    assert "PATH=~/.local/bin:" in out
    assert "vermagic=7.4.0-sgx " in out
    assert "depmod 7.4.0-sgx" in out
    assert "test-session.sh 10.1.2.3 7777" in out
    assert "sgx-build" not in out and "sgx-target" not in out


def test_push_netconsole_defaults_to_the_build_host_address():
    out = push(SGX_BUILD_HOST="10.9.8.7")
    assert "test-session.sh 10.9.8.7 6666" in out


def test_push_reads_local_env(tmp_path):
    env_file = tmp_path / "local.env"
    env_file.write_text("SGX_BUILD_HOST=${SGX_BUILD_HOST:-from-file}\n"
                        "SGX_TARGET_HOST=${SGX_TARGET_HOST:-laptop-from-file}\n")
    out = push(SGX_LOCAL_ENV=str(env_file))
    assert "ssh from-file " in out
    assert "laptop-from-file:/tmp/" in out
    # the environment still wins over the file
    out = push(SGX_LOCAL_ENV=str(env_file), SGX_BUILD_HOST="override")
    assert "ssh override " in out


def test_push_reads_the_example_settings():
    out = push(SGX_LOCAL_ENV=str(HERE / "local.env.example"))
    assert "-o HostKeyAlias=sgx-target user@sgx-target" in out
    assert "export PATH=~/.local/bin:$PATH;" in out     # ~ left for the build host
    assert "-j8 " in out
    assert "test-session.sh 192.0.2.10 6666" in out


def test_push_no_reboot_stops_after_install():
    out = push("--no-reboot")
    assert "mkinitcpio" in out
    assert "boot-test-kernel.sh" not in out.split("mkinitcpio", 1)[1]


def test_push_passes_the_render_gate():
    assert "boot-test-kernel.sh 0" in push(SGX_RENDER="0")
    assert "boot-test-kernel.sh 1" in push()


def test_session_needs_a_netconsole_target():
    out = subprocess.run(["bash", str(SESSION)], env=clean_env(), capture_output=True,
                         text=True, timeout=30)
    assert out.returncode != 0
    assert "usage" in out.stderr


def stub_laptop(tmp_path: pathlib.Path, route: str, neigh: str) -> dict[str, str]:
    """A PATH whose ip/ping/sysctl/modprobe/dmesg fake the laptop; modprobe logs its args."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {
        "ip": f'case "$*" in\n'
              f'"-o route get "*) echo "{route}" ;;\n'
              f'"neigh show "*) echo "{neigh}" ;;\n'
              f'esac\n',
        "modprobe": f'echo "$*" >> "{tmp_path}/modprobe.log"\n',
        "ping": "", "sysctl": "", "dmesg": "",
    }
    for name, body in stubs.items():
        path = bin_dir / name
        path.write_text("#!/bin/bash\n" + body)
        path.chmod(0o755)
    return clean_env(PATH=f"{bin_dir}:{os.environ['PATH']}")


def session(tmp_path: pathlib.Path, route: str, neigh: str) -> str:
    out = subprocess.run(["bash", str(SESSION), "10.42.0.1", "6666"],
                         env=stub_laptop(tmp_path, route, neigh), capture_output=True,
                         text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    return (tmp_path / "modprobe.log").read_text()


def test_session_sends_to_the_next_hop_mac(tmp_path):
    # macOS drops netconsole's default broadcast MAC, so a direct link needs the real one
    log = session(tmp_path, "10.42.0.1 dev enp5s8 src 10.42.0.2 uid 1000",
                  "10.42.0.1 lladdr f4:4d:ad:05:b4:8d REACHABLE")
    assert "netconsole=6665@10.42.0.2/enp5s8,6666@10.42.0.1/f4:4d:ad:05:b4:8d" in log


def test_session_sends_through_the_gateway_mac(tmp_path):
    log = session(tmp_path, "10.42.0.1 via 192.168.12.1 dev enp5s8 src 192.168.12.234",
                  "192.168.12.1 lladdr 02:00:00:00:00:01 STALE")
    assert "6666@10.42.0.1/02:00:00:00:00:01" in log


def test_session_falls_back_to_broadcast_without_a_neighbour(tmp_path):
    log = session(tmp_path, "10.42.0.1 dev enp5s8 src 10.42.0.2 uid 1000", "")
    assert log.strip().endswith("6666@10.42.0.1/")


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_listener_takes_port_and_log_from_the_environment(tmp_path):
    port, log = free_udp_port(), tmp_path / "nc.log"
    proc = subprocess.Popen([sys.executable, str(LISTEN)],
                            env=clean_env(SGX_NETCONSOLE_PORT=str(port),
                                          SGX_NETCONSOLE_LOG=str(log)))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            for _ in range(50):
                s.sendto(b"hello sgx\n", ("127.0.0.1", port))
                time.sleep(0.1)
                if log.exists() and "hello sgx" in log.read_text():
                    break
        assert "hello sgx" in log.read_text()
    finally:
        proc.kill()
        proc.wait()


# ---- the laptop as its own build host (away from the build machine) --------------------

SGX_BUILD = HERE / "sgx-build"
BUILD_KERNEL = HERE / "build-kernel.sh"
BOOT = HERE / "boot-test-kernel.sh"


def test_push_builds_on_the_laptop_when_the_build_host_is_the_target():
    out = push(SGX_BUILD_HOST="target", SGX_TARGET_HOST="me@laptop",
               SGX_KERNEL_TREE="src/linux-resgx545", SGX_NETCONSOLE_HOST="10.42.0.1",
               SGX_BUILD_JOBS="4")
    build = next(l for l in out.splitlines() if "make" in l)
    assert build.startswith("ssh me@laptop ") and "sgx-build kernel" in build
    assert "SGX_KERNEL_TREE=src/linux-resgx545" in build and "-j4 " in build
    assert "M=drivers/gpu/drm/gma500" in build
    assert "install -m644 src/linux-resgx545/drivers/gpu/drm/gma500/gma500_gfx.ko" in out
    assert "scp -q target:" not in out and "/tmp/gma500_gfx.ko" not in out
    assert "test-session.sh 10.42.0.1 6666" in out


def test_push_on_the_laptop_needs_a_netconsole_host():
    env = clean_env(SGX_DRY_RUN="1", SGX_BUILD_HOST="target", SGX_TARGET_HOST="me@laptop")
    out = subprocess.run(["bash", str(PUSH)], env=env, capture_output=True, text=True,
                         timeout=30)
    assert out.returncode != 0 and "SGX_NETCONSOLE_HOST" in out.stderr


def test_push_takes_the_kernel_package_base():
    out = push(SGX_KERNEL_PKGBASE="linux-resgx545", SGX_KERNEL_RELEASE="7.3.0-resgx545")
    assert "mkinitcpio -p linux-resgx545" in out
    assert "boot-test-kernel.sh 1 linux-resgx545" in out
    assert "/usr/lib/modules/7.3.0-resgx545/" in out
    assert "mkinitcpio -p linux-sgx " in push() + " "        # the default stays


def tool(script, *args, **extra):
    return subprocess.run(["bash", str(script), *args], env=clean_env(SGX_DRY_RUN="1", **extra),
                          capture_output=True, text=True, timeout=30)


def test_sgx_build_binds_the_kernel_tree_it_is_given():
    out = tool(SGX_BUILD, "kernel", "make", "ARCH=i386", SGX_KERNEL_TREE="src/linux-resgx545",
               HOME="/home/me")
    assert out.returncode == 0, out.stderr
    assert "systemd-nspawn" in out.stdout
    assert "--bind=/home/me/src/linux-resgx545 " in out.stdout
    assert "--chdir=/home/me/src/linux-resgx545 " in out.stdout
    assert out.stdout.rstrip().endswith("nice make ARCH=i386")


def test_sgx_build_refuses_an_unknown_tree_kind():
    out = tool(SGX_BUILD, "firmware", "make")
    assert out.returncode == 2 and "usage" in out.stderr


def test_build_kernel_builds_and_packages_under_its_own_package_base():
    out = tool(BUILD_KERNEL, SGX_KERNEL_TREE="src/linux-resgx545",
               SGX_KERNEL_PKGBASE="linux-resgx545", SGX_BUILD_JOBS="4")
    assert out.returncode == 0, out.stderr
    lines = out.stdout.splitlines()
    # one make: pacman-pkg builds the kernel itself, and a second pass would relink and
    # recompress it again (about 45 minutes on the laptop)
    makes = [l for l in lines if "make" in l]
    assert len(makes) == 1 and "-j4" in makes[0]
    pkg = next(l for l in lines if "pacman-pkg" in l)
    assert "PACMAN_PKGBASE=linux-resgx545" in pkg and "SGX_KERNEL_TREE=src/linux-resgx545" in pkg
    # 32-bit zstd -22 runs out of memory: the build root's zstd-kernel wrapper compresses
    assert all("ZSTD=zstd-kernel" in l for l in lines if "make" in l)


def fake_grub(tmp_path):
    cfg = tmp_path / "grub.cfg"
    cfg.write_text(
        "submenu 'Advanced options for Arch Linux' $menuentry_id_option "
        "'gnulinux-advanced-1234' {\n"
        "\tmenuentry 'Arch Linux, with Linux linux-sgx' $menuentry_id_option "
        "'gnulinux-linux-sgx-advanced-1234' {\n"
        "\t\tlinux\t/boot/vmlinuz-linux-sgx root=UUID=1234 rw\n\t}\n"
        "\tmenuentry 'Arch Linux, with Linux linux-resgx545' $menuentry_id_option "
        "'gnulinux-linux-resgx545-advanced-1234' {\n"
        "\t\tlinux\t/boot/vmlinuz-linux-resgx545 root=UUID=1234 rw\n\t}\n}\n")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ("grub-script-check", "grub-editenv", "grub-reboot", "systemctl"):
        (bindir / name).write_text(f'#!/bin/bash\necho "{name} $*" >> "{tmp_path}/calls"\n')
        (bindir / name).chmod(0o755)
    return cfg, {"PATH": f"{bindir}:{os.environ['PATH']}", "SGX_GRUB_CFG": str(cfg)}


def test_boot_test_kernel_boots_the_package_base_it_is_given(tmp_path):
    cfg, env = fake_grub(tmp_path)
    out = subprocess.run(["bash", str(BOOT), "1", "linux-resgx545"], env=clean_env(**env),
                         capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    calls = (tmp_path / "calls").read_text()
    assert "grub-reboot gnulinux-advanced-1234>gnulinux-linux-resgx545-advanced-1234" in calls
    text = cfg.read_text()
    assert "/boot/vmlinuz-linux-resgx545 root=UUID=1234 rw $sgx_cmdline" in text
    assert "/boot/vmlinuz-linux-sgx root=UUID=1234 rw\n" in text      # the other kept as is


def test_boot_test_kernel_defaults_to_linux_sgx(tmp_path):
    cfg, env = fake_grub(tmp_path)
    subprocess.run(["bash", str(BOOT)], env=clean_env(**env), capture_output=True, timeout=30)
    assert ">gnulinux-linux-sgx-advanced-1234" in (tmp_path / "calls").read_text()


def push_tools(**extra: str) -> str:
    out = subprocess.run(["sh", str(PUSH_TOOLS)], env=clean_env(SGX_DRY_RUN="1", **extra),
                         capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_push_tools_builds_in_the_image_the_build_host_has():
    out = push_tools()
    assert "sgxhumation/arch32:igt make" in out
    assert "resgx545/arch32:igt" not in out


def test_push_tools_image_is_overridable():
    out = push_tools(SGX_TOOLS_IMAGE="mine/arch32:x")
    assert "mine/arch32:x make" in out
    assert "sgxhumation/arch32:igt" not in out
