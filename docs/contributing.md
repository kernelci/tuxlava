# Contributing to TuxLAVA

## Source code

The TuxLAVA source code is available in the
[tuxlava gitlab repository](https://gitlab.com/Linaro/tuxlava). To clone the
repository, run:

```console
git clone git@gitlab.com:Linaro/tuxlava.git
```

or if you don't (want to) have a gitlab account:

```console
git clone https://gitlab.com/Linaro/tuxlava.git
```

## Issue tracker

The TuxLAVA issue tracker is also on Gitlab:
<https://gitlab.com/Linaro/tuxlava/-/issues>.

## Development dependencies

The Python packages needed to develop TuxLAVA are listed in `pyproject.toml`
section `dev`. You can either install them using `pip install -r
requirements-dev.txt`, or install the corresponding distribution (e.g. Debian)
packages. There are also a few non Python packages used for development: `make`
and `git`.

## Running the tests

To run the tests, `make`: it will run all the included tests, including unit
tests, integration tests, coding style checks, etc.  `python3 -m pytest -vvv
test/unit/test_device.py` to run just a specific group of unit tests.  Please
make sure all the tests pass before submitting patches.  To see all the
available make targets please run `make help`.


To update tests automatically after changing some test templates run
`TUXLAVA_RENDER=1 make test`.

## Sign your work - the Developer's Certificate of Origin

The commit message should have a sign-off line at the end of the explanation
for the patch, which looks like the following:
`Signed-off-by: Random J Developer <random@developer.example.org>`
This line certifies that you wrote the patch or otherwise have the right to
pass it on as an open-source patch.  This will be done for you automatically if
you use ``git commit -s``.  Reverts should also include "Signed-off-by". ``git
revert -s`` does that for you. The rules are pretty simple: if you can certify
the below:

### [Developer's Certificate of Origin 1.1](https://developercertificate.org/)

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.


Some people also put extra tags at the end.  They'll just be ignored for
now, but you can do this to mark internal company procedures or just
point out some special detail about the sign-off.

Any further SoBs (Signed-off-by:'s) following the author's SoB are from
people handling and transporting the patch, but were not involved in its
development. SoB chains should reflect the **real** route a patch took
as it was propagated to the maintainers, with the first SoB entry signalling
primary authorship of a single author.

## Sending your contributions.

Contributions should be sent as merge requests on the GitLab repository. When
creating a merge request, please check that the pipeline ran and passed the
Continuous Integration (CI). This ensures your changes are properly tested and
helps maintain the quality of the codebase.

If that's too high of a barrier for you to send your patches, you can also send
them by email to `tuxsuite@linaro.org`. However, we really prefer merge requests
because the GitLab Continuous Integration will run all the tests against your
changes, and that makes it a lot easier for us to evaluate your contribution.
