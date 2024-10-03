# Installing TuxLAVA via Debian packages

TuxLAVA provides Debian packages that have minimal dependencies, and should
work on any Debian or Debian-based (Ubuntu, etc) system.

1) Download the [repository signing key](https://tuxlava.org/packages/signing-key.gpg)
and save it to `/etc/apt/trusted.gpg.d/tuxlava.gpg`.

```
# wget -O /etc/apt/trusted.gpg.d/tuxlava.gpg \
  https://tuxlava.org/packages/signing-key.gpg
```

2) Create /etc/apt/sources.list.d/tuxlava.list with the following contents:

```
deb https://tuxlava.org/packages/ ./
```

3) Install `tuxlava` as you would any other package:

```
# apt update
# apt install tuxlava
```

Upgrading tuxlava will work just like it would for any other package (`apt
update`, `apt upgrade`).
