#!/usr/bin/env python3
import copy
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

rootfs = Path(sys.argv[1])
password = os.environ.get("N1_ROOT_PASSWORD", "")
if not password:
    raise SystemExit("Set repository Actions secret N1_ROOT_PASSWORD.")

proc = subprocess.run(
    ["openssl", "passwd", "-6", "-stdin"],
    input=password + "\n",
    text=True,
    check=True,
    capture_output=True,
)
password_hash = proc.stdout.strip()
if not password_hash.startswith("$6$"):
    raise SystemExit("OpenSSL did not produce a SHA-512 crypt password hash.")

fd, tmp = tempfile.mkstemp(prefix=rootfs.name + ".", suffix=".tmp", dir=rootfs.parent)
os.close(fd)
replaced = 0
try:
    with tarfile.open(rootfs, "r:gz") as src, tarfile.open(tmp, "w:gz", format=src.format) as dst:
        for member in src.getmembers():
            if member.name.lstrip("./") == "etc/shadow":
                original = src.extractfile(member).read()
                lines = original.splitlines()
                root_lines = [i for i, line in enumerate(lines) if line.startswith(b"root:")]
                if len(root_lines) != 1:
                    raise SystemExit("Expected exactly one root row in /etc/shadow.")
                fields = lines[root_lines[0]].split(b":")
                fields[1] = password_hash.encode()
                lines[root_lines[0]] = b":".join(fields)
                data = b"\n".join(lines) + b"\n"
                info = copy.copy(member)
                info.size = len(data)
                info.mode, info.uid, info.gid = 0o600, 0, 0
                info.uname, info.gname = "root", "root"
                dst.addfile(info, io.BytesIO(data))
                replaced += 1
            else:
                stream = src.extractfile(member) if member.isfile() else None
                dst.addfile(copy.copy(member), stream)
                if stream is not None:
                    stream.close()
    if replaced != 1:
        raise SystemExit(f"Expected one etc/shadow entry in rootfs, found {replaced}.")
    os.replace(tmp, rootfs)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)

with tarfile.open(rootfs, "r:gz") as check:
    member = next(m for m in check.getmembers() if m.name.lstrip("./") == "etc/shadow")
    data = check.extractfile(member).read()
    root_hash = next(line.split(b":", 2)[1].decode() for line in data.splitlines() if line.startswith(b"root:"))
    parts = root_hash.split("$")
    if member.mode != 0o600 or len(parts) < 4 or parts[1] != "6":
        raise SystemExit("Root password hash/mode verification failed.")
    verify = subprocess.run(
        ["openssl", "passwd", "-6", "-salt", parts[2], "-stdin"],
        input=password + "\n",
        text=True,
        check=True,
        capture_output=True,
    ).stdout.strip()
    if verify != root_hash:
        raise SystemExit("Root password verification failed.")
print("Root password injected and SHA-512 hash verified; plaintext was not written to the image log.")
