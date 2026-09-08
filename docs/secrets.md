# Secrets

Some artefacts are not public. `--secrets` adds HTTP headers to the
downloads in the job definition, so LAVA can fetch them.

```shell
tuxlava --device qemu-arm64 \
        --kernel https://private.example.com/Image.gz \
        --secrets Authorization="Bearer <token>"
```

The key is the header name, the value is the header value. You write the
whole value, including the scheme:

```shell
--secrets Authorization="Bearer <token>"
--secrets PRIVATE-TOKEN=<token>
```

## One secret per artefact

A key can name the artefact it belongs to:

```shell
tuxlava --device nfs-x86_64 \
        --kernel https://kernels.example.com/Image \
        --rootfs https://images.example.com/rootfs.tar.xz \
        --secrets kernel:Authorization="Bearer <kernel-token>" \
                  rootfs:PRIVATE-TOKEN=<rootfs-token>
```

The form is `<artefact>:<header>=<value>`. These artefacts are supported:

* `bios`
* `boot`
* `dtb`
* `kernel`
* `modules`
* `pflash`
* `ramdisk`
* `rootfs`
* the name of an overlay

The fvp devices add the firmware artefacts:

* `ap_romfw`
* `bl1`
* `fip`
* `mcp_fw`
* `mcp_romfw`
* `scp_fw`
* `scp_romfw`
* `uefi`

An unknown artefact is an error, so a typo does not fail later inside
LAVA.

A key without an artefact is the fallback. When both match, the artefact
wins:

```shell
# Bearer bbb for the rootfs, Bearer aaa for the rest
--secrets Authorization="Bearer aaa" rootfs:Authorization="Bearer bbb"
```

## Where the fallback is used

The fallback is only used on the urls you pass on the command line.

Every device has default urls, for example the rescue bootloader for the
fastboot devices. They point to a public host that has nothing to do with
your artefacts. Sending your token there would leak it, so they get no
header.

Name the artefact if you do want a header on a default url:

```shell
--secrets ramdisk:Authorization="Bearer <token>"
```

## Supported devices

Device    | Notes                                 |
----------|---------------------------------------|
avh       | Needs `avh_api_token`, see below      |
fastboot  | All the download urls                 |
flasher   | The image url                         |
fvp       | All the download urls, firmware too   |
nfs       | All the download urls                 |
qemu      | All the download urls                 |

The `fastboot-aosp-*` and ssh devices do not take `--secrets`.

## AVH

The AVH devices talk to a remote service, so they need an API token. It
is not a header, and the key name is fixed:

```shell
tuxlava --device avh-imx93 --secrets avh_api_token=<token>
```

An empty value is ignored, it would render an empty header.
