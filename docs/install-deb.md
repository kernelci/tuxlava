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
sudo apt update
sudo apt install tuxlava
```

Upgrading tuxlava will work just like it would for any other package (`apt
update`, `apt upgrade`).

## Install using Debian extrepo

extrepo is a tool that helps configuring external repositories on
Debian in a secure manner. As a pre-requisite for installation using
this method, extrepo should be installed in your Debian machine.

1) Install extrepo if it is not installed previously:

```
sudo apt update
sudo apt install extrepo
```

2) Enable the tuxlava repository with extrepo:

```
sudo extrepo enable tuxlava
```

3) Install tuxlava as you would any other package:

```
sudo apt update
sudo apt install tuxlava
```

If the URL or the GPG key has changed, once updated in the
extrepo-data repository, it can be easily updated with:

```
sudo extrepo update tuxlava
```
