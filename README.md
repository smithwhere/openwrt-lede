# Phicomm N1 OpenWrt firmware

This repository stores the build configuration and custom overlay for the N1 image. GitHub Actions checks out the pinned OpenWrt source, builds the `armsr/armv8/generic` root filesystem, and packages a bootable Phicomm N1 image with Flippy's kernel files.

## Configure build secrets

The repository is public. Wi-Fi and root passwords are supplied to Actions as repository secrets and are not stored in this repository.

In **Settings → Secrets and variables → Actions**, add:

- `N1_ROOT_PASSWORD`: set to `1` if you want the firmware's root password to be `1`.
- `N1_WIFI_PASSWORD`: WPA password, 8–63 letters, digits, underscores, or hyphens.

The workflow stops with a clear error if either secret is missing. These values are used only during the build.

## Build

Open **Actions → Build Phicomm N1 firmware → Run workflow**. The workflow also runs on pushes that change build inputs. It builds OpenWrt at the pinned source commit and uses pinned feed commits; the N1 packer and 6.18 kernel selection are pinned/configured in the workflow.

When it succeeds, download the `n1-firmware` artifact from the workflow run. It contains the compressed SD-card image, checksum, and build information. The artifact is retained for 14 days.

## Contents

- `.config`: compact OpenWrt diffconfig for the current N1 build.
- `feeds.conf.default`: pinned package feeds.
- `files/`: first-boot network/Wi-Fi defaults, persistent 5 GHz channel 149 HT40 enforcement, bridge netfilter, gateway-following DNS, and LuCI defaults.
- `scripts/`: build-time config/secret preparation, dnsmasq upgrade, root-password injection, and packer fixes.
- `.github/workflows/build-n1.yml`: GitHub Actions build and artifact workflow.

The workflow intentionally downloads OpenWrt, feeds, packer code, and kernel archives at build time. Generated `build_dir`, `staging_dir`, `dl`, rootfs archives, and firmware images are build outputs, not source files, and are not committed here.
