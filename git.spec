# Pass --without docs to rpmbuild if you don't want the documentation
Name: 		git
Version: 	1.5.4.4
Release: 	1%{?dist}
Summary:  	Core git tools
License: 	GPLv2
Group: 		Development/Tools
URL: 		http://kernel.org/pub/software/scm/git/
Source: 	http://kernel.org/pub/software/scm/git/%{name}-%{version}.tar.gz
Source1:	git-init.el
Source2:	git.xinetd
Source3:	git.conf.httpd
Patch0:		git-1.5-gitweb-home-link.patch
Patch1:		git-gitweb-commitdiff.patch
BuildRequires:	zlib-devel >= 1.2, openssl-devel, curl-devel, expat-devel, emacs, gettext %{!?_without_docs:, xmlto, asciidoc > 6.0.3}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	perl-Git = %{version}-%{release}
Requires:	zlib >= 1.2, rsync, curl, less, openssh-clients, expat, perl(Error)
Provides:	git-core = %{version}-%{release}
Obsoletes:	git-core <= 1.5.4.2

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs the core tools with minimal dependencies.  To
install all git packages, including tools for integrating with other
SCMs, install the git-all meta-package.

%package all
Summary:	Meta-package to pull in all git tools
Group:		Development/Tools
Requires:	git = %{version}-%{release}
Requires:	git-svn = %{version}-%{release}
Requires:	git-cvs = %{version}-%{release}
Requires:	git-arch = %{version}-%{release}
Requires:	git-email = %{version}-%{release}
Requires:	gitk = %{version}-%{release}
Requires:	git-gui = %{version}-%{release}
Requires:	perl-Git = %{version}-%{release}
Requires:	emacs-git = %{version}-%{release}
Obsoletes:	git <= 1.5.4.2

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package daemon
Summary:	Git protocol dæmon
Group:		Development/Tools
Requires:	git-core = %{version}-%{release}
%description daemon
The git dæmon for supporting git:// access to git repositories

%package -n gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
Requires:       git-core = %{version}-%{release}

%description -n gitweb
Simple web interface to track changes in git repositories


%package svn
Summary:        Git tools for importing Subversion repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}, subversion, perl(Term::ReadKey)
%description svn
Git tools for importing Subversion repositories.

%package cvs
Summary:        Git tools for importing CVS repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}, cvs, cvsps
%description cvs
Git tools for importing CVS repositories.

%package arch
Summary:        Git tools for importing Arch repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}, tla
%description arch
Git tools for importing Arch repositories.

%package email
Summary:        Git tools for sending email
Group:          Development/Tools
Requires:	git = %{version}-%{release}, perl-Git = %{version}-%{release}
%description email
Git tools for sending email.

%package gui
Summary:        Git GUI tool
Group:          Development/Tools
Requires:       git = %{version}-%{release}, tk >= 8.4
%description gui
Git GUI tool.

%package -n gitk
Summary:        Git revision tree visualiser
Group:          Development/Tools
Requires:       git = %{version}-%{release}, tk >= 8.4
%description -n gitk
Git revision tree visualiser.

%package -n perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
Requires:       git = %{version}-%{release}, perl(Error)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)

%description -n perl-Git
Perl interface to Git.

%package -n emacs-git
Summary:       Git version control system support for Emacs
Group:         Applications/Editors
Requires:      git = %{version}-%{release}, emacs-common

%description -n emacs-git
%{summary}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
make %{_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" \
     ETC_GITCONFIG=/etc/gitconfig \
     prefix=%{_prefix} all %{!?_without_docs: doc}
make -C contrib/emacs

%install
rm -rf $RPM_BUILD_ROOT
make %{_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" DESTDIR=$RPM_BUILD_ROOT \
     prefix=%{_prefix} mandir=%{_mandir} \
     ETC_GITCONFIG=/etc/gitconfig \
     INSTALLDIRS=vendor install %{!?_without_docs: install-doc}
make -C contrib/emacs install \
		 emacsdir=$RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp
for elc in $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/*.elc ; do
	install -pm 644 contrib/emacs/$(basename $elc .elc).el \
	$RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp
done
install -Dpm 644 %{SOURCE1} \
	$RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/site-start.d/git-init.el
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d
install -m 644 %SOURCE2 $RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d/git
mkdir -p $RPM_BUILD_ROOT/var/www/git
install -m 644 -t $RPM_BUILD_ROOT/var/www/git gitweb/*.png gitweb/*.css
install -m 755 -t $RPM_BUILD_ROOT/var/www/git gitweb/gitweb.cgi
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d
install -m 0644 %SOURCE3 $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/git.conf

find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -empty -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name perllocal.pod -exec rm -f {} ';'

(find $RPM_BUILD_ROOT%{_bindir} -type f | grep -vE "archimport|svn|cvs|email|gitk|git-gui|git-citooli|git-daemon" | sed -e s@^$RPM_BUILD_ROOT@@)               > bin-man-doc-files
(find $RPM_BUILD_ROOT%{perl_vendorlib} -type f | sed -e s@^$RPM_BUILD_ROOT@@) >> perl-files
%if %{!?_without_docs:1}0
(find $RPM_BUILD_ROOT%{_mandir} $RPM_BUILD_ROOT/Documentation -type f | grep -vE "archimport|svn|git-cvs|email|gitk|git-gui|git-citool" | sed -e s@^$RPM_BUILD_ROOT@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf $RPM_BUILD_ROOT%{_mandir}
%endif
mkdir -p $RPM_BUILD_ROOT/srv/git

%clean
rm -rf $RPM_BUILD_ROOT

%files -f bin-man-doc-files
%defattr(-,root,root)
%{_datadir}/git-core/
%doc README COPYING Documentation/*.txt
%{!?_without_docs: %doc Documentation/*.html Documentation/howto}
%{!?_without_docs: %doc Documentation/technical}

%files svn
%defattr(-,root,root)
%{_bindir}/*svn*
%doc Documentation/*svn*.txt
%{!?_without_docs: %{_mandir}/man1/*svn*.1*}
%{!?_without_docs: %doc Documentation/*svn*.html }

%files cvs
%defattr(-,root,root)
%doc Documentation/*git-cvs*.txt
%{_bindir}/*cvs*
%{!?_without_docs: %{_mandir}/man1/*cvs*.1*}
%{!?_without_docs: %doc Documentation/*git-cvs*.html }

%files arch
%defattr(-,root,root)
%doc Documentation/git-archimport.txt
%{_bindir}/git-archimport
%{!?_without_docs: %{_mandir}/man1/git-archimport.1*}
%{!?_without_docs: %doc Documentation/git-archimport.html }

%files email
%defattr(-,root,root)
%doc Documentation/*email*.txt
%{_bindir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %doc Documentation/*email*.html }

%files gui
%defattr(-,root,root)
%{_bindir}/git-gui
%{_bindir}/git-citool
%{_datadir}/git-gui/
%{!?_without_docs: %{_mandir}/man1/git-gui.1*}
%{!?_without_docs: %doc Documentation/git-gui.html}
%{!?_without_docs: %{_mandir}/man1/git-citool.1*}
%{!?_without_docs: %doc Documentation/git-citool.html}

%files -n gitk
%defattr(-,root,root)
%doc Documentation/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{!?_without_docs: %{_mandir}/man1/*gitk*.1*}
%{!?_without_docs: %doc Documentation/*gitk*.html }

%files -n perl-Git -f perl-files
%defattr(-,root,root)

%files -n emacs-git
%defattr(-,root,root)
%{_datadir}/emacs/site-lisp/*git*.el*
%{_datadir}/emacs/site-lisp/site-start.d/git-init.el

%files daemon
%defattr(-,root,root)
%{_bindir}/git-daemon
%config(noreplace)%{_sysconfdir}/xinetd.d/git
/srv/git

%files -n gitweb
%defattr(-,root,root)
/var/www/git/
%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf
%{!?_without_docs: %doc Documentation/*.html Documentation/howto}
%{!?_without_docs: %doc Documentation/technical}

%files all
# No files for you!

%changelog
* Thu Mar 13 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-1
- git-1.5.4.4

* Mon Mar  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.5.4.3-3
- rebuild for new perl (again)

* Sun Feb 24 2008 Bernardo Innocenti <bernie@codewiz.org> 1.5.4.3-2
- Do not silently overwrite /etc/httpd/conf.d/git.conf

* Sat Feb 23 2008 James Bowes <jbowes@redhat.com> 1.5.4.3-1
- git-1.5.4.3
- Include Kristian Høgsberg's changes to rename git-core to
  git and git to git-all.

* Sun Feb 17 2008 James Bowes <jbowes@redhat.com> 1.5.4.2-1
- git-1.5.4.2

* Mon Feb 11 2008 Jeremy Katz <katzj@redhat.com> - 1.5.4.1-2
- Add upstream patch (e62a641de17b172ffc4d3a803085c8afbfbec3d1) to have 
  gitweb rss feeds point be commitdiffs instead of commit

* Sun Feb 10 2008 James Bowes <jbowes@redhat.com> 1.5.4.1-1
- git-1.5.4.1

* Tue Feb 05 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.5.4-3
- rebuild for new perl

* Sun Feb 03 2008 James Bowes <jbowes@redhat.com> 1.5.4-1
- Add BuidRequires on gettext.

* Sat Feb 02 2008 James Bowes <jbowes@redhat.com> 1.5.4-1
- git-1.5.4

* Tue Jan 08 2008 James Bowes <jbowes@redhat.com> 1.5.3.8-1
- git-1.5.3.8

* Fri Dec 21 2007 James Bowes <jbowes@redhat.com> 1.5.3.7-2
- Have git metapackage require explicit versions (bug 247214)

* Mon Dec 03 2007 Josh Boyer <jwboyer@gmail.com> 1.5.3.7-1
- git-1.5.3.7

* Tue Nov 27 2007 Josh Boyer <jwboyer@gmail.com> 1.5.3.6-1
- git-1.5.3.6
- git-core requires perl(Error) (bug 367861)
- git-svn requires perl(Term:ReadKey) (bug 261361)
- git-email requires perl-Git (bug 333061)

* Wed Oct 24 2007 Lubomir Kundrak <lkundrak@redhat.com> 1.5.3.4-2
- git-Perl requires Error package

* Tue Oct 09 2007 James Bowes <jbowes@redhat.com> 1.5.3.4-1
- git-1.5.3.4

* Sun Sep 30 2007 James Bowes <jbowes@redhat.com> 1.5.3.3-1
- git-1.5.3.3

* Wed Sep 26 2007 James Bowes <jbowes@redhat.com> 1.5.3.2-1
- git-1.5.3.2

* Thu Sep 06 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.3.1-2
- Include git-gui and git-citool docs

* Thu Sep 06 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.3.1-1
- git-1.5.3.1-1

* Thu Aug 23 2007 James Bowes <jbowes@redhat.com> 1.5.2.5-1
- git-1.5.2.5-1

* Fri Aug 03 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.4-1
- git-1.5.2.4-1

* Tue Jul 03 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.2-3
- Add git-daemon and gitweb packages

* Thu Jun 21 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.2-2
- Add emacs-git package (#235431)

* Mon Jun 18 2007 James Bowes <jbowes@redhat.com> 1.5.2.2-1
- git-1.5.2.2

* Fri Jun 08 2007 James Bowes <jbowes@redhat.com> 1.5.2.1-1
- git-1.5.2.1

* Tue May 13 2007 Quy Tonthat <qtonthat@gmail.com>
- Added lib files for git-gui
- Added Documentation/technical (As needed by Git Users Manual)

* Tue May 8 2007 Quy Tonthat <qtonthat@gmail.com>
- Added howto files

* Fri Mar 30 2007 Chris Wright <chrisw@redhat.com> 1.5.0.6-1
- git-1.5.0.6

* Mon Mar 19 2007 Chris Wright <chrisw@redhat.com> 1.5.0.5-1
- git-1.5.0.5

* Tue Mar 13 2007 Chris Wright <chrisw@redhat.com> 1.5.0.3-1
- git-1.5.0.3

* Fri Mar 2 2007 Chris Wright <chrisw@redhat.com> 1.5.0.2-2
- BuildRequires perl-devel as of perl-5.8.8-14 (bz 230680)

* Mon Feb 26 2007 Chris Wright <chrisw@redhat.com> 1.5.0.2-1
- git-1.5.0.2

* Mon Feb 13 2007 Nicolas Pitre <nico@cam.org>
- Update core package description (Git isn't as stupid as it used to be)

* Mon Feb 12 2007 Junio C Hamano <junkio@cox.net>
- Add git-gui and git-citool.

* Sun Dec 10 2006 Chris Wright <chrisw@redhat.com> 1.4.4.2-2
- no need to install manpages executable (bz 216790)
- use bytes for git-cvsserver

* Sun Dec 10 2006 Chris Wright <chrisw@redhat.com> 1.4.4.2-1
- git-1.4.4.2

* Mon Nov 6 2006 Jindrich Novy <jnovy@redhat.com> 1.4.2.4-2
- rebuild against the new curl

* Tue Oct 17 2006 Chris Wright <chrisw@redhat.com> 1.4.2.4-1
- git-1.4.2.4

* Wed Oct 4 2006 Chris Wright <chrisw@redhat.com> 1.4.2.3-1
- git-1.4.2.3

* Fri Sep 22 2006 Chris Wright <chrisw@redhat.com> 1.4.2.1-1
- git-1.4.2.1

* Mon Sep 11 2006 Chris Wright <chrisw@redhat.com> 1.4.2-1
- git-1.4.2

* Thu Jul 6 2006 Chris Wright <chrisw@redhat.com> 1.4.1-1
- git-1.4.1

* Tue Jun 13 2006 Chris Wright <chrisw@redhat.com> 1.4.0-1
- git-1.4.0

* Thu May 4 2006 Chris Wright <chrisw@redhat.com> 1.3.3-1
- git-1.3.3
- enable git-email building, prereqs have been relaxed

* Thu May 4 2006 Chris Wright <chrisw@redhat.com> 1.3.2-1
- git-1.3.2

* Fri Apr 28 2006 Chris Wright <chrisw@redhat.com> 1.3.1-1
- git-1.3.1

* Wed Apr 19 2006 Chris Wright <chrisw@redhat.com> 1.3.0-1
- git-1.3.0

* Mon Apr 10 2006 Chris Wright <chrisw@redhat.com> 1.2.6-1
- git-1.2.6

* Wed Apr 5 2006 Chris Wright <chrisw@redhat.com> 1.2.5-1
- git-1.2.5

* Wed Mar 1 2006 Chris Wright <chrisw@redhat.com> 1.2.4-1
- git-1.2.4

* Wed Feb 22 2006 Chris Wright <chrisw@redhat.com> 1.2.3-1
- git-1.2.3

* Tue Feb 21 2006 Chris Wright <chrisw@redhat.com> 1.2.2-1
- git-1.2.2

* Thu Feb 16 2006 Chris Wright <chrisw@redhat.com> 1.2.1-1
- git-1.2.1

* Mon Feb 13 2006 Chris Wright <chrisw@redhat.com> 1.2.0-1
- git-1.2.0

* Tue Feb 1 2006 Chris Wright <chrisw@redhat.com> 1.1.6-1
- git-1.1.6

* Tue Jan 24 2006 Chris Wright <chrisw@redhat.com> 1.1.4-1
- git-1.1.4

* Sun Jan 15 2006 Chris Wright <chrisw@redhat.com> 1.1.2-1
- git-1.1.2

* Tue Jan 10 2006 Chris Wright <chrisw@redhat.com> 1.1.1-1
- git-1.1.1

* Tue Jan 10 2006 Chris Wright <chrisw@redhat.com> 1.1.0-1
- Update to latest git-1.1.0 (drop git-email for now)
- Now creates multiple packages:
-	 git-core, git-svn, git-cvs, git-arch, gitk

* Mon Nov 14 2005 H. Peter Anvin <hpa@zytor.com> 0.99.9j-1
- Change subpackage names to git-<name> instead of git-core-<name>
- Create empty root package which brings in all subpackages
- Rename git-tk -> gitk

* Thu Nov 10 2005 Chris Wright <chrisw@osdl.org> 0.99.9g-1
- zlib dependency fix
- Minor cleanups from split
- Move arch import to separate package as well

* Tue Sep 27 2005 Jim Radford <radford@blackbean.org>
- Move programs with non-standard dependencies (svn, cvs, email)
  into separate packages

* Tue Sep 27 2005 H. Peter Anvin <hpa@zytor.com>
- parallelize build
- COPTS -> CFLAGS

* Fri Sep 16 2005 Chris Wright <chrisw@osdl.org> 0.99.6-1
- update to 0.99.6

* Fri Sep 16 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Linus noticed that less is required, added to the dependencies

* Sun Sep 11 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Updated dependencies
- Don't assume manpages are gzipped

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
