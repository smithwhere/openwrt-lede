# Phicomm N1 OpenWrt firmware

This repository contains the reproducible build inputs for a Phicomm N1 image and a manually triggered GitHub Actions workflow. The workflow builds the `armsr/armv8/generic` root filesystem and packages it as a bootable N1 image.

## Runner requirement

A standard GitHub-hosted runner does not have enough free disk for this OpenWrt build. Configure a Linux x86_64 self-hosted runner on the build VM (or another Linux host) with at least 50 GiB free disk and the OpenWrt build dependencies installed. The pinned packer also uses non-interactive `sudo` for package setup and image assembly, so the runner account must be configured for the needed non-interactive sudo commands.

Add the runner from **Settings → Actions → Runners → New self-hosted runner** and follow GitHub's displayed install/registration commands. The workflow only has a `workflow_dispatch` trigger; keep it that way when using a self-hosted runner in this public repository, and do not add pull-request triggers.

## Configure build secrets

The repository is public. Wi-Fi and root passwords are supplied to Actions as repository secrets and are not stored in this repository.

In **Settings → Secrets and variables → Actions**, add:

- `N1_ROOT_PASSWORD`: set to `1` if you want the firmware's root password to be `1`.
- `N1_WIFI_PASSWORD`: WPA password, 8–63 letters, digits, underscores, or hyphens.

The workflow stops with an error if either secret is missing. The root password hash and Wi-Fi key are injected during the build.

## Build

Open **Actions → Build Phicomm N1 firmware → Run workflow** after adding the secrets and registering the runner. When it succeeds, download the `n1-firmware` artifact from the workflow run. It contains the compressed SD-card image, checksum, and generic rootfs archive. The artifact is retained for 14 days.

The build pins OpenWrt commit `1d585dc90248b09ff61358e504edf2a302d3493a`, all package feed commits, and the N1 packer commit. The packer resolves the latest 6.18.y kernel archive when the workflow runs.

## Contents

- `.config`: compact OpenWrt diffconfig for this N1 build.
- `feeds.conf.default`: pinned package feeds.
- `files/`: first-boot network/Wi-Fi defaults, persistent 5 GHz channel 149 HT40 enforcement, bridge netfilter, gateway-following DNS, and LuCI defaults.
- `scripts/`: build-time config/secret preparation, dnsmasq upgrade, root-password injection, and packer fixes.
- `.github/workflows/build-n1.yml`: manual GitHub Actions build and artifact workflow.

The workflow downloads source feeds, packer code, and kernel archives at build time. Generated `build_dir`, `staging_dir`, `dl`, rootfs archives, and firmware images are outputs, not source inputs, and are not committed here.
