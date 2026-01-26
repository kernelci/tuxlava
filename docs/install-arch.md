# Installing TuxLAVA via Arch Linux packages

TuxLAVA provides Arch Linux packages that have minimal dependencies.

1. Create /etc/pacman.d/tuxlava.conf with the following contents:

```
[tuxpkg]
SigLevel = Optional TrustAll
Server = https://tuxlava.org/packages/
```
2. Include it from /etc/pacman.conf. Add one line at the bottom:

```
Include = /etc/pacman.d/*.conf
```

If you already have this line, do nothing.

3. Sync and install:

```shell
# pacman -Syu
# pacman -S tuxlava
```

Upgrades will be available in the same repository.

### Method 2: Manual download and install

If the pacman database is not available, download and install manually:

```shell
# curl -LO https://tuxlava.org/packages/tuxlava-VERSION-any.pkg.tar.zst
# pacman -U tuxlava-VERSION-any.pkg.tar.zst
```

Replace VERSION with the desired version number.
