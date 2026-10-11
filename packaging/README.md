The GitHub Actions workflow pins the upstream OpenWrt source and invokes the pinned unifreq/openwrt_packit composite action. The custom `mk-n1.sh` wrapper applies the N1 wireless defaults and prevents packit from failing when an optional source-rootfs file is absent.

The packer invokes privileged package setup and image assembly commands. Run this workflow only on a trusted, isolated self-hosted Linux runner, with non-interactive sudo configured for the runner account.
