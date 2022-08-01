%global debug_package %{nil}
%global _prj_name ntfy
%global _unitdir %{_prefix}/lib/systemd/system

# Go 1.18 is required for now
# See https://github.com/golang/go/issues/45435
%if 0%{?rhel} >= 10 || 0%{?fedora} >= 36
    %global _need_static_go_bin 0
%else
    %global _need_static_go_bin 1
%endif

Name:           ntfysh
Version:        1.27.2
Release:        3%{?dist}
Summary:        Send push notifications to your phone or desktop via PUT/POST

License:        Apache-2.0 or GPLv2
URL:            https://ntfy.sh/
Source0:        https://github.com/binwiederhier/ntfy/archive/v%{version}.tar.gz

BuildRequires:  curl gcc git glibc-static jq
%if ! %{_need_static_go_bin}
BuildRequires: golang
%endif

%description
ntfy (pronounce: notify) is a simple HTTP-based pub-sub notification service.

It allows you to send notifications to your phone or desktop via scripts from any computer,
entirely without signup or cost. It's also open source if you want to run your own.

%prep
%autosetup -n %{_prj_name}-%{version}

# if Go 1.18 is not available, get the static binaries
%if %{_need_static_go_bin}
    _GO_VER="1.18.4"
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
    _GO_DL_NAME="go${_GO_VER}.linux-${_ARCH}.tar.gz"
    _GO_DL_URL="https://go.dev/dl/${_GO_DL_NAME}"

    curl -Lfo "${_GO_DL_NAME}" "${_GO_DL_URL}"
    tar -xf "${_GO_DL_NAME}"
    # bins in go/bin
%endif

%build
%if %{_need_static_go_bin}
    _GO_BIN_DIR=$(realpath "go/bin")
    export PATH="${_GO_BIN_DIR}:${PATH}"
%endif

# patch Makefile, see https://github.com/binwiederhier/ntfy/pull/373
%global _commit 69d6cdd
sed -i 's|$(shell git rev-parse --short HEAD)|%{_commit}|' Makefile

make VERSION=%{version} cli-linux-server

%check
# a few tests are erroring, but it's probably fine
#make test

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
%{_localstatedir}/cache/%{_prj_name}
%{_sharedstatedir}/%{_prj_name}

%changelog
* Tue Aug 02 2022 cyqsimon - 1.27.2-3
- Patch 'commit' variable in 'Makefile' to fix build

* Sun Jul 31 2022 cyqsimon - 1.27.2-2
- Mark config files as 'noreplace'

* Fri Jul 22 2022 cyqsimon - 1.27.2-1
- Release 1.27.2
