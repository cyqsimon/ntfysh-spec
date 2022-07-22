%global debug_package %{nil}
%global _prj_name ntfy

Name:           ntfysh
Version:        1.27.2
Release:        1%{?dist}
Summary:        Send push notifications to your phone or desktop via PUT/POST

License:        Apache-2.0 or GPLv2
URL:            https://ntfy.sh/
Source0:        https://github.com/binwiederhier/ntfy/archive/v%{version}.tar.gz

BuildRequires:  curl gcc golang jq
%if 0%{?el7} || 0%{?el9} || 0%{?fedora}
BuildRequires:  python3-pip
%endif
%if 0%{?el8}
BuildRequires:  python39-pip
%endif

%description
ntfy (pronounce: notify) is a simple HTTP-based pub-sub notification service.

It allows you to send notifications to your phone or desktop via scripts from any computer,
entirely without signup or cost. It's also open source if you want to run your own.

%prep
%autosetup -n %{_prj_name}-%{version}

%build
make cli-linux-server

%check
make test

%install
# bin
install -Dpm 755 dist/ntfy_linux_server/%{_prj_name} %{buildroot}%{_bindir}/%{_prj_name}

# doc
mkdir -p %{buildroot}%{_docdir}/%{name}
cp -r docs/subscribe %{buildroot}%{_docdir}/%{name}/
install -Dpm 644 docs/*.md %{buildroot}%{_docdir}/%{name}

%files
%license LICENSE LICENSE.GPLv2
%doc README.md
%{_bindir}/%{_prj_name}
%{_docdir}/%{name}/*

%changelog
* Fri Jul 22 2022 cyqsimon - 1.27.2-1
- Release 1.27.2
