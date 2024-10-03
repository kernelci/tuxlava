# Installing TuxLAVA via RPM packages

TuxLAVA provides RPM packages that have minimal dependencies, and should work
on any RPM-based (Fedora, etc) system.

1) Create `/etc/yum.repos.d/tuxlava.repo` with the following contents:

```
[tuxlava]
name=tuxlava
type=rpm-md
baseurl=https://tuxlava.org/packages/
gpgcheck=1
gpgkey=https://tuxlava.org/packages/repodata/repomd.xml.key
enabled=1

```

2) Install tuxlava as you would any other package:

```
# dnf install tuxlava
```

Upgrades will be available in the same repository, so you can get them using
the same procedure you already use to get other updates for your system.
