#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

packit = Path(sys.argv[1])

def replace_once(path, old, new):
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected packit copy loop not found in {path}")
    path.write_text(text.replace(old, new, 1))

replace_once(
    packit / "files/openwrt-install-amlogic",
    '''        for src in $COPY_SRC; do
            echo "copy [ $src ] ..."
            (cd / && tar cf - $src) | tar xf -
            sync
        done''',
    '''        for src in $COPY_SRC; do
            echo "copy [ $src ] ..."
            if [ -e "/$src" ]; then
                (cd / && tar cf - "$src") | tar xf -
            else
                echo "skip [ $src ] (not present in source rootfs)"
            fi
            sync
        done''',
)
replace_once(
    packit / "files/openwrt-update-amlogic",
    '''for src in ${COPY_SRC}; do
    echo "Copy [ ${src} ] ... "
    (cd ${P2} && tar cf - ${src}) | tar xf -
    sync
done''',
    '''for src in ${COPY_SRC}; do
    echo "Copy [ ${src} ] ... "
    if [ -e "${P2}/${src}" ]; then
        (cd "${P2}" && tar cf - "${src}") | tar xf -
    else
        echo "Skip [ ${src} ] (not present in source rootfs)"
    fi
    sync
done''',
)

wireless = packit / "files/s905d/wireless"
wifi_password = os.environ.get("N1_WIFI_PASSWORD", "")
if not re.fullmatch(r"[A-Za-z0-9_-]{8,63}", wifi_password):
    raise SystemExit("N1_WIFI_PASSWORD must be 8-63 letters, digits, underscores, or hyphens.")
text = wireless.read_text()
sections = re.split(r"(\n\s*\n)", text)
def set_option(block, name, value):
    pattern = rf"(?m)^(\s*option\s+{re.escape(name)}\s+)'[^']*'\s*$"
    if re.search(pattern, block):
        return re.sub(pattern, rf"\g<1>'{value}'", block)
    return block.rstrip() + f"\n\toption {name} '{value}'\n"

found_radio = found_iface = False
for i, block in enumerate(sections):
    header = block.lstrip()
    if header.startswith("config wifi-device 'radio0'"):
        found_radio = True
        for key, value in (("type", "mac80211"), ("hwmode", "11a"),
                           ("country", "CN"), ("channel", "149"),
                           ("band", "5g"), ("htmode", "HT40"),
                           ("disabled", "0")):
            block = set_option(block, key, value)
        sections[i] = block
    elif header.startswith("config wifi-iface 'default_radio0'"):
        found_iface = True
        block = set_option(block, "disabled", "0")
        block = set_option(block, "key", wifi_password)
        sections[i] = block
if not found_radio or not found_iface:
    raise SystemExit(f"Expected N1 wireless sections missing in {wireless}")
wireless.write_text("".join(sections))
result = wireless.read_text()
for expected in ("option channel '149'", "option band '5g'",
                 "option htmode 'HT40'", "option disabled '0'"):
    if expected not in result:
        raise SystemExit(f"Packit wireless validation failed: {expected}")
print("Patched packit to skip absent optional files and use N1 5 GHz channel 149 HT40.")
