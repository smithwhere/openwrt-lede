#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
overlay_repo = Path(sys.argv[2]).resolve()

# Apply the dnsmasq 2.93 upgrade that was validated against this pinned LEDE tree.
makefile = repo / "package/network/services/dnsmasq/Makefile"
text = makefile.read_text()
replacements = {
    "PKG_UPSTREAM_VERSION:=2.91": "PKG_UPSTREAM_VERSION:=2.93",
    "PKG_RELEASE:=1": "PKG_RELEASE:=4",
    "PKG_HASH:=f622682848b33677adb2b6ad08264618a2ae0a01da486a93fd8cd91186b3d153":
        "PKG_HASH:=0c00d4e5c97c8306e5fb932b348b34269c9c29a0e7df0e8e82958b407092bc19",
}
for old, new in replacements.items():
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Expected dnsmasq Makefile entry not found: {old}")
    text = text.replace(old, new, 1)
makefile.write_text(text)

patch = repo / "package/network/services/dnsmasq/patches/100-remove-old-runtime-kernel-support.patch"
patch_text = patch.read_text()
marker = "--- a/src/util.c"
if marker in patch_text:
    patch_text = patch_text[:patch_text.index(marker)].rstrip() + "\n"
patch_text = patch_text.replace(" src/util.c    | 19 ---------------\n", "")
patch_text = patch_text.replace(" 4 files changed, 5 insertions(+), 87 deletions(-)",
                                " 3 files changed, 5 insertions(+), 68 deletions(-)")
patch.write_text(patch_text)
if "PKG_UPSTREAM_VERSION:=2.93" not in makefile.read_text():
    raise SystemExit("dnsmasq version validation failed")
if marker in patch.read_text():
    raise SystemExit("obsolete dnsmasq util.c patch hunk remains")

shutil.copy2(overlay_repo / "feeds.conf.default", repo / "feeds.conf.default")
shutil.copytree(overlay_repo / "files", repo / "files", dirs_exist_ok=True)
for rel in (
    "etc/init.d/n1-wireless-enforce",
    "etc/uci-defaults/97-wireless-cn-channel149",
    "etc/uci-defaults/98-uhttpd-http",
    "etc/uci-defaults/99-theme-bootstrap",
    "etc/hotplug.d/iface/99-n1-dnsmasq-upstream",
):
    path = repo / "files" / rel
    if not path.is_file():
        raise SystemExit(f"Required overlay missing: {path}")
    path.chmod(0o755)
print("OpenWrt source pinned overlay and dnsmasq changes are ready.")
