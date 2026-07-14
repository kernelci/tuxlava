Name:      tuxlava
Version:   0.23.0
Release:   0%{?dist}
Summary:   TuxLAVA, helps to generate LAVA jobs
License:   MIT
URL:       https://tuxsuite.com
Source0:   %{pypi_source}


BuildRequires: git
BuildRequires: make
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: python3-flit
BuildRequires: python3-pip
BuildRequires: python3-pytest
BuildRequires: python3-pytest-cov
BuildRequires: python3-pytest-mock
BuildRequires: python3-yaml
BuildRequires: wget
Requires: python3 >= 3.10
Requires: python3-requests
Requires: python3-yaml
Requires: python3-jinja2

BuildArch: noarch

%global debug_package %{nil}

%description
TuxLAVA is a python library and tool to generate LAVA jobs for devices of type
qemu, fvp, fastboot and nfs. TuxLAVA has standard list of devices that are
supported along with tests that could be run on these devices.

%prep
%setup -q

%build
export FLIT_NO_NETWORK=1
make run
# make man
# make bash_completion

# %check
# python3 -m pytest test/

%install
mkdir -p %{buildroot}/usr/share/tuxlava/
cp -r run tuxlava %{buildroot}/usr/share/tuxlava/
mkdir -p %{buildroot}/usr/bin
ln -sf ../share/tuxlava/run %{buildroot}/usr/bin/tuxlava

%files
/usr/share/tuxlava
%{_bindir}/tuxlava

%doc README.md
%license LICENSE

%changelog
* Mon Jul 06 2026 Anders Roxell <anders.roxell@linaro.org> - 0.23.0-1
- Release 0.23.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.23.0

* Tue Jun 16 2026 Anders Roxell <anders.roxell@linaro.org> - 0.22.0-1
- Release 0.22.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.22.0

* Wed Jun 03 2026 Anders Roxell <anders.roxell@linaro.org> - 0.21.0-1
- Release 0.21.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.21.0

* Mon Jun 01 2026 Anders Roxell <anders.roxell@linaro.org> - 0.20.0-1
- Release 0.20.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.20.0

* Thu May 21 2026 Anders Roxell <anders.roxell@linaro.org> - 0.19.0-1
- Release 0.19.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.19.0

* Thu May 21 2026 Anders Roxell <anders.roxell@linaro.org> - 0.18.0-1
- Release 0.18.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.18.0

* Thu Mar 05 2026 Anders Roxell <anders.roxell@linaro.org> - 0.17.0-1
- Release 0.17.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.17.0

* Fri Feb 13 2026 Anders Roxell <anders.roxell@linaro.org> - 0.16.0-1
- Release 0.16.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.16.0

* Thu Feb 05 2026 Anders Roxell <anders.roxell@linaro.org> - 0.15.0-1
- Release 0.15.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.15.0

* Wed Jan 28 2026 Anders Roxell <anders.roxell@linaro.org> - 0.14.0-1
- Release 0.14.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.14.0

* Tue Jan 27 2026 Anders Roxell <anders.roxell@linaro.org> - 0.13.0-1
- Release 0.13.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.13.0

* Mon Jan 26 2026 Anders Roxell <anders.roxell@linaro.org> - 0.12.0-1
- Release 0.12.0. See: https://github.com/kernelci/tuxlava/releases/tag/v0.12.0


* Mon Feb 03 2025 Senthil Kumaran <senthil.kumaran@linaro.org> - 0.0.1-1
- Initial version of the package
