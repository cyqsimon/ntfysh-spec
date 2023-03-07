%global debug_package %{nil}
%global _commit 477c9d3
%global _prj_name ntfy
%global _ntfy_user ntfy

Name:           ntfysh
Version:        2.1.2
Release:        2%{?dist}
Summary:        Send push notifications to your phone or desktop via PUT/POST

License:        ASL 2.0 AND GPLv2
URL:            https://ntfy.sh/
Source0:        https://github.com/binwiederhier/ntfy/archive/v%{version}.tar.gz

Requires(pre):  shadow-utils
BuildRequires:  curl gcc git glibc-static jq npm systemd-rpm-macros tar
# Python 3.8 or newer needed to build docs
%if 0%{?el7}
BuildRequires:  rh-python38
%endif
%if 0%{?el8}
BuildRequires:  python39-pip
%endif
%if 0%{?rhel} >=9 || 0%{?fedora}
BuildRequires:  python3-pip
%endif

%description
ntfy (pronounce: notify) is a simple HTTP-based pub-sub notification service.

It allows you to send notifications to your phone or desktop via scripts from
any computer, entirely without signup or cost. It's also open source if you
want to run your own.

%prep
%autosetup -n %{_prj_name}-%{version}

# Use latest official stable Go build
_GO_VER="$(curl -Lf https://golang.org/VERSION?m=text)"
%ifarch x86_64
    _ARCH=amd64
%endif
%ifarch aarch64
    _ARCH=arm64
%endif
if [[ -z "${_ARCH}" ]]; then
    echo "Unsupported architecture!"
    exit 1
fi
_GO_DL_NAME="${_GO_VER}.linux-${_ARCH}.tar.gz"
_GO_DL_URL="https://go.dev/dl/${_GO_DL_NAME}"

curl -Lfo "${_GO_DL_NAME}" "${_GO_DL_URL}"
tar -xf "${_GO_DL_NAME}"
# bins in go/bin

%build
_GO_BIN_DIR=$(realpath "go/bin")
export PATH="${_GO_BIN_DIR}:${PATH}"

# enable Python3.8 on EL7
%if 0%{?el7}
source /opt/rh/rh-python38/enable
%endif

make docs
make web
make VERSION=%{version} COMMIT=%{_commit} cli-linux-server

%check
_GO_BIN_DIR=$(realpath "go/bin")
export PATH="${_GO_BIN_DIR}:${PATH}"

make test

%install
# bin
install -Dpm 755 dist/ntfy_linux_server/%{_prj_name} %{buildroot}%{_bindir}/%{_prj_name}

# logo
install -Dpm 644 web/src/img/%{_prj_name}.png %{buildroot}%{_datadir}/%{_prj_name}/logo.png

# units
install -Dpm 644 client/%{_prj_name}-client.service %{buildroot}%{_unitdir}/%{_prj_name}-client.service
install -Dpm 644 server/%{_prj_name}.service %{buildroot}%{_unitdir}/%{_prj_name}.service

# configs
install -Dpm 644 client/client.yml %{buildroot}%{_sysconfdir}/%{_prj_name}/client.yml
install -Dpm 644 server/server.yml %{buildroot}%{_sysconfdir}/%{_prj_name}/server.yml

# doc
mkdir -p %{buildroot}%{_docdir}/%{name}
cp -r docs/subscribe %{buildroot}%{_docdir}/%{name}/
install -Dpm 644 docs/*.md %{buildroot}%{_docdir}/%{name}

# var dirs
mkdir -p %{buildroot}%{_localstatedir}/cache/%{_prj_name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{_prj_name}

%files
%license LICENSE LICENSE.GPLv2
%doc README.md
%{_bindir}/%{_prj_name}
%{_datadir}/%{_prj_name}/*
%{_unitdir}/%{_prj_name}-client.service
%{_unitdir}/%{_prj_name}.service
%config(noreplace) %{_sysconfdir}/%{_prj_name}/*
%{_docdir}/%{name}/*
%attr(750, %{_ntfy_user}, %{_ntfy_user}) %{_localstatedir}/cache/%{_prj_name}
%attr(750, %{_ntfy_user}, %{_ntfy_user}) %{_sharedstatedir}/%{_prj_name}

%pre
# create user
echo "Creating user '%{_ntfy_user}' if it does not exist..."
getent passwd %{_ntfy_user} >/dev/null || \
    useradd --system --home-dir %{_sharedstatedir}/%{_prj_name} --shell /sbin/nologin \
    --no-create-home --comment "ntfy service user" %{_ntfy_user}

%preun
# if remove, then stop and disable services
if [[ "$1" -lt 1 ]]; then
    for SVC in "%{_prj_name}.service" "%{_prj_name}-client.service"; do
        echo "Stopping and disabling ${SVC} ..."
        systemctl disable --now ${SVC}
    done
fi

%post
# if update, then restart services if running
if [[ "$1" -gt 1 ]]; then
    systemctl daemon-reload
    for SVC in "%{_prj_name}.service" "%{_prj_name}-client.service"; do
        echo "Restarting ${SVC} if it's running..."
        systemctl try-restart ${SVC}
    done
fi

%changelog
* Wed Mar 08 2023 cyqsimon - 2.1.2-2
- Build docs

* Mon Mar 06 2023 cyqsimon - 2.1.2-1
- Release 2.1.2

* Thu Mar 02 2023 cyqsimon - 2.1.1-1
- Release 2.1.1
- Always use latest official stable Go build

* Sun Feb 26 2023 cyqsimon - 2.1.0-1
- Release 2.1.0

* Thu Feb 23 2023 cyqsimon - 2.0.1-2
- Improve scriptlets

* Sat Feb 18 2023 cyqsimon - 2.0.1-1
- Release 2.0.1

* Fri Feb 17 2023 cyqsimon - 2.0.0-1
- Release 2.0.0
- Re-enable tests

* Wed Feb 15 2023 cyqsimon - 1.31.0-1
- Release 1.31.0
- Two licenses are conjunctive not disjunctive

* Sun Dec 25 2022 cyqsimon - 1.30.1-2
- Build web app

* Sat Dec 24 2022 cyqsimon - 1.30.1-1
- Release 1.30.1

* Fri Nov 18 2022 cyqsimon - 1.29.1-1
- Release 1.29.1
- Set correct commit hash

* Sun Nov 13 2022 cyqsimon - 1.29.0-1
- Release 1.29.0

* Wed Sep 28 2022 cyqsimon - 1.28.0-1
- Release 1.28.0

* Thu Aug 04 2022 cyqsimon - 1.27.2-6
- Bump static go binaries version

* Tue Aug 02 2022 cyqsimon - 1.27.2-5
- Add scriptlets relating to systemd

* Tue Aug 02 2022 cyqsimon - 1.27.2-4
- Add 'ntfy' user and group
- Install dirs under '/var' with owner set to 'ntfy'

* Tue Aug 02 2022 cyqsimon - 1.27.2-3
- Patch 'commit' variable in 'Makefile' to fix build

* Sun Jul 31 2022 cyqsimon - 1.27.2-2
- Mark config files as 'noreplace'

* Fri Jul 22 2022 cyqsimon - 1.27.2-1
- Release 1.27.2
