#!/usr/bin/env bash
set -euo pipefail
python3 "${GITHUB_WORKSPACE}/packaging/patch-packit.py" "$PWD"
exec ./mk_s905d_n1.sh
