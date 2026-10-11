#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
password = os.environ.get("N1_WIFI_PASSWORD", "")
if not re.fullmatch(r"[A-Za-z0-9_-]{8,63}", password):
    raise SystemExit("N1_WIFI_PASSWORD is required and must be 8-63 letters, digits, '_' or '-'.")

marker = "__N1_WIFI_PASSWORD__"
targets = [
    root / "etc/uci-defaults/97-wireless-cn-channel149",
    root / "etc/init.d/n1-wireless-enforce",
]
for path in targets:
    text = path.read_text()
    if marker not in text:
        raise SystemExit(f"Missing Wi-Fi secret marker in {path}")
    path.write_text(text.replace(marker, password))
print("Rendered Wi-Fi password into the build overlay.")
