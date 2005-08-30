# Pass --without docs to rpmbuild if you don't want the documetnation
Name: 		git-core
Version: 	0.99.4
Release: 	4%{?dist}
Summary:  	Git core and tools
License: 	GPL
Group: 		Development/Tools
URL: 		http://kernel.org/pub/software/scm/git/
Source: 	http://kernel.org/pub/software/scm/git/%{name}-%{version}.tar.gz
BuildRequires:	zlib-devel, openssl-devel, curl-devel  %{!?_without_docs:, xmlto, asciidoc > 6.0.3}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: 	rsync, rcs, curl

%description
This is a stupid (but extremely fast) directory content manager.  It
doesn't do a whole lot, but what it _does_ do is track directory
contents efficiently. It is intended to be the base of an efficient,
distributed source code management system. This package includes
rudimentary tools that can be used as a SCM, but you should look
elsewhere for tools for ordinary humans layered on top of this.

%prep
%setup -q

%build
make COPTS="$RPM_OPT_FLAGS" prefix=%{_prefix} all %{!?_without_docs: doc}
make COPTS="$RPM_OPT_FLAGS" -C tools all

%install
rm -rf $RPM_BUILD_ROOT
make dest=$RPM_BUILD_ROOT prefix=%{_prefix} mandir=%{_mandir} \
     install install-tools %{!?_without_docs: install-doc}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/*
%{_datadir}/git-core/
%doc README COPYING Documentation/*.txt
%{!?_without_docs: %doc Documentation/*.html }
%{!?_without_docs: %{_mandir}/man1/*.1.gz}
%{!?_without_docs: %{_mandir}/man7/*.7.gz}

%changelog
* Thu Aug 18 2005 Chris Wright <chrisw@osdl.org> 0.99.4-4
- drop sh_utils, sh-utils, diffutils, mktemp, and openssl Requires
- use RPM_OPT_FLAGS in spec file, drop patch0

* Wed Aug 17 2005 Tom "spot" Callaway <tcallawa@redhat.com> 0.99.4-3
- use dist tag to differentiate between branches
- use rpm optflags by default (patch0)
- own %{_datadir}/git-core/

* Mon Aug 15 2005 Chris Wright <chrisw@osdl.org>
- update spec file to fix Buildroot, Requires, and drop Vendor

* Sun Aug 07 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Redid the description
- Cut overlong make line, loosened changelog a bit
- I think Junio (or perhaps OSDL?) should be vendor...

* Thu Jul 14 2005 Eric Biederman <ebiederm@xmission.com>
- Add the man pages, and the --without docs build option

* Wed Jul 7 2005 Chris Wright <chris@osdl.org>
- initial git spec file
