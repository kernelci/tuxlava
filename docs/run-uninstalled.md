# Running TuxLAVA uninstalled

- TuxLAVA requires Python 3.9 or newer.

If you don't want to or can't install TuxLAVA, you can run it directly from the
source directory. After getting the sources via git or something else, there is
a `run` script that will do the right thing for you: you can either use that
script directly, or symlink it to a directory in your `PATH`.

```shell
/path/to/tuxlava/run --help
sudo ln -s /path/to/tuxlava/run /usr/local/bin/tuxlava && tuxlava --help
```
