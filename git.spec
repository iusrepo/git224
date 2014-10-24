# Pass --without docs to rpmbuild if you don't want the documentation

# Settings for EL-5
# - Leave git-* binaries in %{_bindir}
# - Don't use noarch subpackages
# - Use proper libcurl devel package
# - Patch emacs and tweak docbook spaces
# - Explicitly enable ipv6 for git-daemon
# - Use prebuilt documentation, asciidoc is too old
# - Define missing python macro
%if 0%{?rhel} && 0%{?rhel} <= 5
%global gitcoredir          %{_bindir}
%global noarch_sub          0
%global libcurl_devel       curl-devel
%global emacs_old           1
%global docbook_suppress_sp 1
%global enable_ipv6         1
%global use_prebuilt_docs   1
%global filter_yaml_any     1
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%else
%global gitcoredir          %{_libexecdir}/git-core
%global noarch_sub          1
%global libcurl_devel       libcurl-devel
%global emacs_old           0
%global docbook_suppress_sp 0
%global enable_ipv6         0
%global use_prebuilt_docs   0
%global filter_yaml_any     0
%endif

# Settings for F-19+ and EL-7+
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%global desktop_vendor_tag  0
%global gnome_keyring       1
%global use_new_rpm_filters 1
%global use_systemd         1
%else
%global desktop_vendor_tag  1
%global gnome_keyring       0
%global use_new_rpm_filters 0
%global use_systemd         0
%endif

Name:           git
Version:        2.1.0
Release:        5%{?dist}
Summary:        Fast Version Control System
License:        GPLv2
Group:          Development/Tools
URL:            http://git-scm.com/
Source0:        http://www.kernel.org/pub/software/scm/git/%{name}-%{version}.tar.gz
Source2:        git-init.el
Source3:        git.xinetd.in
Source4:        git.conf.httpd
Source5:        git-gui.desktop
Source6:        gitweb.conf.in
Source10:       http://www.kernel.org/pub/software/scm/git/%{name}-manpages-%{version}.tar.gz
Source11:       http://www.kernel.org/pub/software/scm/git/%{name}-htmldocs-%{version}.tar.gz
Source12:       git@.service
Source13:       git.socket
Patch0:         git-1.8-gitweb-home-link.patch
# https://bugzilla.redhat.com/490602
Patch1:         git-cvsimport-Ignore-cvsps-2.2b1-Branches-output.patch
# https://bugzilla.redhat.com/600411
Patch3:         git-1.7-el5-emacs-support.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
BuildRequires:  asciidoc >= 8.4.1
BuildRequires:  xmlto
%endif
BuildRequires:  desktop-file-utils
BuildRequires:  emacs
BuildRequires:  expat-devel
BuildRequires:  gettext
BuildRequires:  %{libcurl_devel}
%if %{gnome_keyring}
BuildRequires:  libgnome-keyring-devel
%endif
BuildRequires:  pcre-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel >= 1.2
%if %{use_systemd}
# For macros
BuildRequires:  systemd
%endif

Requires:       less
Requires:       openssh-clients
Requires:       perl(Error)
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
Requires:       perl-Git = %{version}-%{release}
Requires:       rsync
Requires:       zlib >= 1.2

Provides:       git-core = %{version}-%{release}
%if 0%{?rhel} && 0%{?rhel} <= 5
Obsoletes:      git-core <= 1.5.4.3
%endif

# Obsolete git-arch
Obsoletes:      git-arch < %{version}-%{release}

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs the core tools with minimal dependencies.  To
install all git packages, including tools for integrating with other
SCMs, install the git-all meta-package.

%package all
Summary:        Meta-package to pull in all git tools
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
Requires:       git-cvs = %{version}-%{release}
Requires:       git-email = %{version}-%{release}
Requires:       git-gui = %{version}-%{release}
Requires:       git-svn = %{version}-%{release}
Requires:       git-p4 = %{version}-%{release}
Requires:       gitk = %{version}-%{release}
Requires:       perl-Git = %{version}-%{release}
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
Requires:       emacs-git = %{version}-%{release}
Obsoletes:      git <= 1.5.4.3

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package bzr
Summary:        Git tools for working with bzr repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
Requires:       bzr

%description bzr
%{summary}.

%package daemon
Summary:        Git protocol dæmon
Group:          Development/Tools
Requires:       git = %{version}-%{release}
%if %{use_systemd}
Requires:	systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires:       xinetd
%endif
%description daemon
The git dæmon for supporting git:// access to git repositories

%package -n gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}

%description -n gitweb
Simple web interface to track changes in git repositories

%package hg
Summary:        Git tools for working with mercurial repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
Requires:       mercurial >= 1.8

%description hg
%{summary}.

%package p4
Summary:        Git tools for working with Perforce depots
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
BuildRequires:  python
Requires:       git = %{version}-%{release}
%description p4
%{summary}.

%package svn
Summary:        Git tools for importing Subversion repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}, subversion
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
%description svn
Git tools for importing Subversion repositories.

%package cvs
Summary:        Git tools for importing CVS repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, cvs
Requires:       cvsps
Requires:	perl-DBD-SQLite
%description cvs
Git tools for importing CVS repositories.

%package email
Summary:        Git tools for sending email
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, perl-Git = %{version}-%{release}
Requires:       perl(Authen::SASL)
Requires:       perl(Net::SMTP::SSL)
%description email
Git tools for sending email.

%package gui
Summary:        Git GUI tool
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, tk >= 8.4
Requires:       gitk = %{version}-%{release}
%description gui
Git GUI tool.

%package -n gitk
Summary:        Git revision tree visualiser
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, tk >= 8.4
%description -n gitk
Git revision tree visualiser.

%package -n perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)
Requires:       perl(Error)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git
Perl interface to Git.

%package -n perl-Git-SVN
Summary:        Perl interface to Git::SVN
Group:          Development/Libraries
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git-SVN
Perl interface to Git.

%package -n emacs-git
Summary:        Git version control system support for Emacs
Group:          Applications/Editors
Requires:       git = %{version}-%{release}
%if %{noarch_sub}
BuildArch:      noarch
Requires:       emacs(bin) >= %{_emacs_version}
%else
Requires:       emacs-common
%endif

%description -n emacs-git
%{summary}.

%package -n emacs-git-el
Summary:        Elisp source files for git version control system support for Emacs
Group:          Applications/Editors
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       emacs-git = %{version}-%{release}

%description -n emacs-git-el
%{summary}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%if %{emacs_old}
%patch3 -p1
%endif

%if %{use_prebuilt_docs}
mkdir -p prebuilt_docs/{html,man}
tar xf %{SOURCE10} -C prebuilt_docs/man
tar xf %{SOURCE11} -C prebuilt_docs/html
# Remove non-html files
find prebuilt_docs/html -type f ! -name '*.html' | xargs rm
find prebuilt_docs/html -type d | xargs rmdir --ignore-fail-on-non-empty
%endif

# Use these same options for every invocation of 'make'.
# Otherwise it will rebuild in %%install due to flags changes.
cat << \EOF > config.mak
V = 1
CFLAGS = %{optflags}
BLK_SHA1 = 1
NEEDS_CRYPTO_WITH_SSL = 1
USE_LIBPCRE = 1
ETC_GITCONFIG = %{_sysconfdir}/gitconfig
DESTDIR = %{buildroot}
INSTALL = install -p
GITWEB_PROJECTROOT = %{_var}/lib/git
GNU_ROFF = 1
htmldir = %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}
prefix = %{_prefix}
gitwebdir = %{_var}/www/git
EOF

%if "%{gitcoredir}" == "%{_bindir}"
echo gitexecdir = %{_bindir} >> config.mak
%endif

%if %{docbook_suppress_sp}
# This is needed for 1.69.1-1.71.0
echo DOCBOOK_SUPPRESS_SP = 1 >> config.mak
%endif

# Filter bogus perl requires
# packed-refs comes from a comment in contrib/hooks/update-paranoid
# YAML::Any is optional and not available on el5
%if %{use_new_rpm_filters}
%{?perl_default_filter}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(packed-refs\\)
%if ! %{defined perl_bootstrap}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(Term::ReadKey\\)
%endif
%else
cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed \
%if %{filter_yaml_any}
    -e '/perl(YAML::Any)/d' \
%endif
    -e '/perl(packed-refs)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}
%endif

%build
make %{?_smp_mflags} all
%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
make %{?_smp_mflags} doc
%endif

make -C contrib/emacs

%if %{gnome_keyring}
make -C contrib/credential/gnome-keyring/
%endif

make -C contrib/subtree/

# Remove shebang from bash-completion script
sed -i '/^#!bash/,+1 d' contrib/completion/git-completion.bash

%install
rm -rf %{buildroot}
make %{?_smp_mflags} INSTALLDIRS=vendor install
%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
make %{?_smp_mflags} INSTALLDIRS=vendor install-doc
%else
cp -a prebuilt_docs/man/* %{buildroot}%{_mandir}
cp -a prebuilt_docs/html/* Documentation/
%endif

%if %{emacs_old}
%global _emacs_sitelispdir %{_datadir}/emacs/site-lisp
%global _emacs_sitestartdir %{_emacs_sitelispdir}/site-start.d
%endif
%global elispdir %{_emacs_sitelispdir}/git
make -C contrib/emacs install \
    emacsdir=%{buildroot}%{elispdir}
for elc in %{buildroot}%{elispdir}/*.elc ; do
    install -pm 644 contrib/emacs/$(basename $elc .elc).el \
    %{buildroot}%{elispdir}
done
install -Dpm 644 %{SOURCE2} \
    %{buildroot}%{_emacs_sitestartdir}/git-init.el

%if %{gnome_keyring}
install -pm 755 contrib/credential/gnome-keyring/git-credential-gnome-keyring \
    %{buildroot}%{gitcoredir}
# Remove built binary files, otherwise they will be installed in doc
make -C contrib/credential/gnome-keyring/ clean
%endif

make -C contrib/subtree install
%if ! %{use_prebuilt_docs}
make -C contrib/subtree install-doc
%endif

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -pm 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/httpd/conf.d/git.conf
sed "s|@PROJECTROOT@|%{_var}/lib/git|g" \
    %{SOURCE6} > %{buildroot}%{_sysconfdir}/gitweb.conf

find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type f -name '*.bs' -empty -exec rm -f {} ';'
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} ';'

# git-archimport is not supported
find %{buildroot} Documentation -type f -name 'git-archimport*' -exec rm -f {} ';'

exclude_re="archimport|email|git-citool|git-cvs|git-daemon|git-gui|git-remote-bzr|git-remote-hg|gitk|p4|svn"
(find %{buildroot}{%{_bindir},%{_libexecdir}} -type f | grep -vE "$exclude_re" | sed -e s@^%{buildroot}@@) > bin-man-doc-files
(find %{buildroot}{%{_bindir},%{_libexecdir}} -mindepth 1 -type d | grep -vE "$exclude_re" | sed -e 's@^%{buildroot}@%dir @') >> bin-man-doc-files
(find %{buildroot}%{perl_vendorlib} -type f | sed -e s@^%{buildroot}@@) > perl-git-files
(find %{buildroot}%{perl_vendorlib} -mindepth 1 -type d | sed -e 's@^%{buildroot}@%dir @') >> perl-git-files
# Split out Git::SVN files
grep Git/SVN perl-git-files > perl-git-svn-files
sed -i "/Git\/SVN/ d" perl-git-files
%if %{!?_without_docs:1}0
(find %{buildroot}%{_mandir} -type f | grep -vE "$exclude_re|Git" | sed -e s@^%{buildroot}@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf %{buildroot}%{_mandir}
%endif

mkdir -p %{buildroot}%{_var}/lib/git
%if %{use_systemd}
mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE12} %{SOURCE13} %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
# On EL <= 5, xinetd does not enable IPv6 by default
enable_ipv6="        # xinetd does not enable IPv6 by default
        flags           = IPv6"
perl -p \
    -e "s|\@GITCOREDIR\@|%{gitcoredir}|g;" \
    -e "s|\@BASE_PATH\@|%{_var}/lib/git|g;" \
%if %{enable_ipv6}
    -e "s|^}|$enable_ipv6\n$&|;" \
%endif
    %{SOURCE3} > %{buildroot}%{_sysconfdir}/xinetd.d/git
%endif

# Install bzr and hg remote helpers from contrib
install -pm 755 contrib/remote-helpers/git-remote-{bzr,hg} %{buildroot}%{gitcoredir}

# Setup bash completion
mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
install -pm 644 contrib/completion/git-completion.bash %{buildroot}%{_sysconfdir}/bash_completion.d/git

# Install tcsh completion
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-completion.tcsh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# Move contrib/hooks out of %%docdir and make them executable
mkdir -p %{buildroot}%{_datadir}/git-core/contrib
mv contrib/hooks %{buildroot}%{_datadir}/git-core/contrib
chmod +x %{buildroot}%{_datadir}/git-core/contrib/hooks/*
pushd contrib > /dev/null
ln -s ../../../git-core/contrib/hooks
popd > /dev/null

# Install git-prompt.sh
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-prompt.sh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# install git-gui .desktop file
desktop-file-install \
%if %{desktop_vendor_tag}
  --vendor fedora \
%endif
  --dir=%{buildroot}%{_datadir}/applications %{SOURCE5}

# find translations
%find_lang %{name} %{name}.lang
cat %{name}.lang >> bin-man-doc-files

# quiet some rpmlint complaints
chmod -R g-w %{buildroot}
find %{buildroot} -name git-mergetool--lib | xargs chmod a-x
rm -f {Documentation/technical,contrib/emacs,contrib/credential/gnome-keyring}/.gitignore
chmod a-x Documentation/technical/api-index.sh
find contrib -type f | xargs chmod -x


%clean
rm -rf %{buildroot}

%if %{use_systemd}
%post daemon
%systemd_post git@.service

%preun daemon
%systemd_preun git@.service

%postun daemon
%systemd_postun_with_restart git@.service
%endif

%files -f bin-man-doc-files
%defattr(-,root,root)
%{_datadir}/git-core/
%doc README COPYING Documentation/*.txt Documentation/RelNotes contrib/
%{!?_without_docs: %doc Documentation/*.html Documentation/docbook-xsl.css}
%{!?_without_docs: %doc Documentation/howto Documentation/technical}
%{_sysconfdir}/bash_completion.d

%files bzr
%defattr(-,root,root)
%{gitcoredir}/git-remote-bzr

%files hg
%defattr(-,root,root)
%{gitcoredir}/git-remote-hg

%files p4
%defattr(-,root,root)
%{gitcoredir}/*p4*
%{gitcoredir}/mergetools/p4merge
%doc Documentation/*p4*.txt
%{!?_without_docs: %{_mandir}/man1/*p4*.1*}
%{!?_without_docs: %doc Documentation/*p4*.html }

%files svn
%defattr(-,root,root)
%{gitcoredir}/*svn*
%doc Documentation/*svn*.txt
%{!?_without_docs: %{_mandir}/man1/*svn*.1*}
%{!?_without_docs: %doc Documentation/*svn*.html }

%files cvs
%defattr(-,root,root)
%doc Documentation/*git-cvs*.txt
%{_bindir}/git-cvsserver
%{gitcoredir}/*cvs*
%{!?_without_docs: %{_mandir}/man1/*cvs*.1*}
%{!?_without_docs: %doc Documentation/*git-cvs*.html }

%files email
%defattr(-,root,root)
%doc Documentation/*email*.txt
%{gitcoredir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %doc Documentation/*email*.html }

%files gui
%defattr(-,root,root)
%{gitcoredir}/git-gui*
%{gitcoredir}/git-citool
%{_datadir}/applications/*git-gui.desktop
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

%files -n perl-Git -f perl-git-files
%defattr(-,root,root)
%exclude %{_mandir}/man3/*Git*SVN*.3pm*
%{!?_without_docs: %{_mandir}/man3/*Git*.3pm*}

%files -n perl-Git-SVN -f perl-git-svn-files
%defattr(-,root,root)
%{!?_without_docs: %{_mandir}/man3/*Git*SVN*.3pm*}

%files -n emacs-git
%defattr(-,root,root)
%doc contrib/emacs/README
%dir %{elispdir}
%{elispdir}/*.elc
%{_emacs_sitestartdir}/git-init.el

%files -n emacs-git-el
%defattr(-,root,root)
%{elispdir}/*.el

%files daemon
%defattr(-,root,root)
%doc Documentation/*daemon*.txt
%if %{use_systemd}
%{_unitdir}/git.socket
%{_unitdir}/git@.service
%else
%config(noreplace)%{_sysconfdir}/xinetd.d/git
%endif
%{gitcoredir}/git-daemon
%{_var}/lib/git
%{!?_without_docs: %{_mandir}/man1/*daemon*.1*}
%{!?_without_docs: %doc Documentation/*daemon*.html}

%files -n gitweb
%defattr(-,root,root)
%doc gitweb/INSTALL gitweb/README
%config(noreplace)%{_sysconfdir}/gitweb.conf
%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf
%{_var}/www/git/


%files all
# No files for you!

%changelog
* Fri Oct 24 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.1.0-5
- Rename the git.service into git@.service fixing
  https://bugzilla.redhat.com/980574

* Mon Sep 08 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-4
- Perl 5.20 re-rebuild of bootstrapped packages

* Thu Aug 28 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-3
- Perl 5.20 rebuild

* Tue Aug 26 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-2
- Disable requires perl(Term::ReadKey) when perl bootstraping

* Mon Aug 18 2014 Ondrej Oprala <ooprala@redhat.com - 2.1.0-1
- 2.1.0

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.4-1
- 2.0.4

* Mon Jul 28 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.3-1
- 2.0.3

* Fri Jul 11 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.1-1
- 2.0.1

* Tue Jun 10 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-4
- Change source URLs, as googlecode doesn't have up-to-date tarballs

* Tue Jun 10 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-3
- Conditionalize an ancient obsolete

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-1
- Update to 2.0.0

* Mon May 19 2014 Jon Ciesla <limburgher@gmail.com> - 1.9.3-1
- Update to 1.9.3

* Mon Feb 17 2014 Ondrej Oprala <ooprala@redhat.com> - 1.9.0-1
- Update to 1.9.0

* Thu Jan 16 2014 Todd Zullinger <tmz@pobox.com> - 1.8.5.3-2
- Drop unused python DESTIR patch
- Consolidate settings for Fedora 19+ and EL 7+
- Use new rpm filtering on Fedora 19+ and EL 7+
- Rebuild with file-5.14-14 (#1026760)

* Thu Jan 16 2014 Ondrej Oprala <ooprala@redhat.com> - 1.8.5.3-1
* Update to 1.8.5.3

* Wed Dec 18 2013 Ondrej Oprala <ooprala@redhat.com> - 1.8.5.2-1
* Update to 1.8.5.2

* Wed Nov 13 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.8.4.2-2
- Fix htmldir when doc dir is unversioned (#993779).

* Tue Oct 29 2013 Todd Zullinger <tmz@pobox.com> - 1.8.4.2-1
- Update to 1.8.4.2 (#1024497)

* Sat Oct 05 2013 Todd Zullinger <tmz@pobox.com>
- Add mercurial version requirement to git-hg, for those rebuilding on EL

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 15 2013 Petr Pisar <ppisar@redhat.com> - 1.8.3.1-2
- Perl 5.18 rebuild

* Fri Jun 14 2013 Todd Zullinger <tmz@pobox.com> - 1.8.3.1-1
- Update to 1.8.3.1
- Add bzr and hg subpackages, thanks to Michael Scherer (#974800)

* Mon May 13 2013 Jon Ciesla <limburgher@gmail.com> - 1.8.2.1-4
- Fix typo introduced in 1.8.2-3, fixed desktop tag.

* Wed May  1 2013 Tom Callaway <spot@fedoraproject.org> - 1.8.2.1-3
- conditionalize systemd vs xinetd
- cleanup systemd handling (it was not quite right in -2)

* Tue Apr 30 2013 Tom Callaway <spot@fedoraproject.org> - 1.8.2.1-2
- switch to systemd instead of xinetd (bz 737183)

* Sun Apr 14 2013 Todd Zullinger <tmz@pobox.com> - 1.8.2.1-1
- Update to 1.8.2.1
- Exclude optional perl(YAML::Any) dependency on EL-5

* Wed Apr 10 2013 Jon Ciesla <limburgher@gmail.com> - 1.8.2-3
- Drop desktop vendor tag for >= f19.

* Wed Mar 27 2013 Todd Zullinger <tmz@pobox.com> - 1.8.2-2
- Require perl(Term::ReadKey) for git add --interactive (#928328)
- Drop DESTDIR from python instlibdir
- Fix bogus changelog dates

* Tue Mar 19 2013 Adam Tkac <atkac redhat com> - 1.8.2-1
- update to 1.8.2
- 0001-DESTDIR-support-in-contrib-subtree-Makefile.patch has been merged

* Tue Feb 26 2013 Todd Zullinger <tmz@pobox.com> - 1.8.1.4-2
- Update asciidoc requirements, drop unsupported ASCIIDOC7
- Define GNU_ROFF to force ASCII apostrophes in manpages (so copy/paste works)
- Install tcsh completion (requires manual setup by users)
- Clean up dist conditionals, don't pretend to support EL-4 builds
- Use prebuilt documentation on EL-5, where asciidoc is too old
- Respect gitexecdir variable in git-subtree install

* Wed Feb 20 2013 Adam Tkac <atkac redhat com> - 1.8.1.4-1
- update to 1.8.1.4

* Wed Jan 30 2013 Adam Tkac <atkac redhat com> - 1.8.1.2-1
- update to 1.8.1.2
- own directories which should be owned (#902517)

* Thu Jan 03 2013 Adam Tkac <atkac redhat com> - 1.8.1-1
- update to 1.8.1
- build git-svn as arch subpkg due to new git-remote-testsvn binary

* Tue Dec 11 2012 Adam Tkac <atkac redhat com> - 1.8.0.2-1
- update to 1.8.0.2

* Thu Dec 06 2012 Adam Tkac <atkac redhat com> - 1.8.0.1-2
- don't install some unneeded credential-gnome-keyring stuff

* Thu Nov 29 2012 Adam Tkac <atkac redhat com> - 1.8.0.1-1
- update to 1.8.0.1
- include git-subtree in git rpm (#864651)

* Mon Oct 29 2012 Adam Tkac <atkac redhat com> - 1.8.0-1
- update to 1.8.0
- include git-credential-gnome-keyring helper in git pkg
- 0001-cvsimport-strip-all-inappropriate-tag-strings.patch was merged

* Thu Oct 25 2012 Adam Tkac <atkac redhat com> - 1.7.12.1-2
- move git-prompt.sh into usr/share/git-core/contrib/completion (#854061)

* Thu Sep 27 2012 Adam Tkac <atkac redhat com> - 1.7.12.1-1
- update to 1.7.12.1
- cvsimport should skip more characters (#850640)

* Thu Aug 23 2012 Todd Zullinger <tmz@pobox.com> - 1.7.12-2
- Install git-prompt.sh which provides __git_ps1()

* Wed Aug 22 2012 Adam Tkac <atkac redhat com> - 1.7.12-1
- update to 1.7.12

* Wed Aug 15 2012 Todd Zullinger <tmz@pobox.com> - 1.7.11.5-1
- Update to 1.7.11.5
- Add git-p4 subpackage (#844008)

* Tue Aug 07 2012 Adam Tkac <atkac redhat com> - 1.7.11.4-1
- update to 1.7.11.4

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.11.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 25 2012 Todd Zullinger <tmz@pobox.com> - 1.7.11.2-2
- Split perl(Git::SVN) into its own package (#843182)

* Mon Jul 16 2012 Adam Tkac <atkac redhat com> - 1.7.11.2-1
- update to 1.7.11.2

* Thu Jun 28 2012 Petr Pisar <ppisar@redhat.com> - 1.7.10.4-2
- Perl 5.16 rebuild

* Fri Jun 15 2012 Adam Tkac <atkac redhat com> - 1.7.10.4-1
- update to 1.7.10.4

* Thu Jun 07 2012 Petr Pisar <ppisar@redhat.com> - 1.7.10.2-2
- Perl 5.16 rebuild

* Mon May 14 2012 Adam Tkac <atkac redhat com> - 1.7.10.2-1
- update to 1.7.10.2

* Thu May 03 2012 Adam Tkac <atkac redhat com> - 1.7.10.1-1
- update to 1.7.10.1

* Tue Apr 10 2012 Adam Tkac <atkac redhat com> - 1.7.10-1
- update to 1.7.10

* Fri Mar 30 2012 Adam Tkac <atkac redhat com> - 1.7.9.5-1
- update to 1.7.9.5

* Thu Mar 08 2012 Adam Tkac <atkac redhat com> - 1.7.9.3-1
- update to 1.7.9.3

* Wed Feb 15 2012 Todd Zullinger <tmz@pobox.com> - 1.7.9.1-1
- Update to 1.7.9.1
- Fix EPEL builds (rpm doesn't accept mutiple -f options in %files)

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 1.7.9-2
- Rebuild against PCRE 8.30

* Mon Jan 30 2012 Adam Tkac <atkac redhat com> - 1.7.9-1
- update to 1.7.9

* Thu Jan 19 2012 Adam Tkac <atkac redhat com> - 1.7.8.4-1
- update to 1.7.8.4

* Thu Jan 12 2012 Adam Tkac <atkac redhat com> - 1.7.8.3-1
- update to 1.7.8.3

* Mon Jan 02 2012 Adam Tkac <atkac redhat com> - 1.7.8.2-1
- update to 1.7.8.2

* Fri Dec 23 2011 Adam Tkac <atkac redhat com> - 1.7.8.1-1
- update to 1.7.8.1

* Wed Dec 07 2011 Adam Tkac <atkac redhat com> - 1.7.8-1
- update to 1.7.8

* Tue Nov 29 2011 Adam Tkac <atkac redhat com> - 1.7.7.4-1
- update to 1.7.7.4

* Thu Nov 10 2011 Adam Tkac <atkac redhat com> - 1.7.7.3-1
- update to 1.7.7.3

* Mon Nov 07 2011 Adam Tkac <atkac redhat com> - 1.7.7.2-1
- update to 1.7.7.2

* Tue Nov 01 2011 Adam Tkac <atkac redhat com> - 1.7.7.1-1
- update to 1.7.7.1

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.7-2
- Rebuilt for glibc bug#747377

* Thu Oct 20 2011 Adam Tkac <atkac redhat com> - 1.7.7-1
- update to 1.7.7
  - git-1.6-update-contrib-hooks-path.patch is no longer needed

* Mon Sep 26 2011 Adam Tkac <atkac redhat com> - 1.7.6.4-1
- update to 1.7.6.4

* Wed Sep 07 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.2-1
- Update to 1.7.6.2
- Fixes incompatibility caused by git push --quiet fix
  http://thread.gmane.org/gmane.comp.version-control.git/180652

* Mon Aug 29 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.1-2
- Build with PCRE support (#734269)

* Fri Aug 26 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.1-1
- Update to 1.7.6.1
- Include gpg signature for tarball in SRPM

* Fri Aug 05 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6-5
- Fix git push --quiet, thanks to Clemens Buchacher (#725593)
- Obsolete git-arch as needed

* Tue Jul 26 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6-4
- Drop git-arch on fedora >= 16, the tla package has been retired
- Rework most spec file dist conditionals to make future changes easier

* Thu Jul 21 2011 Petr Sabata <contyk@redhat.com> - 1.7.6-3
- Perl mass rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 1.7.6-2
- Perl mass rebuild

* Wed Jun 29 2011 Adam Tkac <atkac redhat com> - 1.7.6-1
- update to 1.7.6

* Mon Jun 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.7.5.4-2
- Perl mass rebuild

* Thu Jun 09 2011 Adam Tkac <atkac redhat com> - 1.7.5.4-1
- update to 1.7.5.4

* Tue May 24 2011 Adam Tkac <atkac redhat com> - 1.7.5.2-1
- update to 1.7.5.2

* Thu May 05 2011 Adam Tkac <atkac redhat com> - 1.7.5.1-1
- update to 1.7.5.1

* Wed Apr 27 2011 Adam Tkac <atkac redhat com> - 1.7.5-1
- update to 1.7.5

* Mon Apr 11 2011 Adam Tkac <atkac redhat com> - 1.7.4.4-1
- update to 1.7.4.4

* Mon Mar 28 2011 Adam Tkac <atkac redhat com> - 1.7.4.2-1
- update to 1.7.4.2
- move man3/Git.3pm file to perl-Git subpkg (#664889)
- add perl-DBD-SQLite dependency to git-cvs (#602410)

* Sun Feb 13 2011 Todd Zullinger <tmz@pobox.com> - 1.7.4.1-1
- Update to 1.7.4.1
- Clean up documentation settings (the defaults changed in 1.7.4)
- Improve EL-5 compatibility, thanks to Kevin Fenzi for emacs testing

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Adam Tkac <atkac redhat com> - 1.7.4-1
- update to 1.7.4

* Wed Jan 19 2011 Adam Tkac <atkac redhat com> - 1.7.3.5-1
- update to 1.7.3.5

* Thu Dec 16 2010 Adam Tkac <atkac redhat com> - 1.7.3.4-1
- update to 1.7.3.4

* Mon Dec 06 2010 Adam Tkac <atkac redhat com> - 1.7.3.3-1
- update to 1.7.3.3

* Fri Oct 22 2010 Adam Tkac <atkac redhat com> - 1.7.3.2-1
- update to 1.7.3.2

* Thu Sep 30 2010 Adam Tkac <atkac redhat com> - 1.7.3.1-1
- update to 1.7.3.1

* Wed Sep 29 2010 jkeating - 1.7.3-3
- Rebuilt for gcc bug 634757

* Mon Sep 20 2010 Todd Zullinger <tmz@pobox.com> - 1.7.3-2
- Ensure the release notes are included in %%doc

* Sun Sep 19 2010 Todd Zullinger <tmz@pobox.com> - 1.7.3-1
- Update to 1.7.3

* Tue Sep 07 2010 Adam Tkac <atkac redhat com> - 1.7.2.3-1
- update to 1.7.2.3

* Fri Aug 20 2010 Adam Tkac <atkac redhat com> - 1.7.2.2-1
- update to 1.7.2.2

* Fri Jul 30 2010 Thomas Spura <tomspur@fedoraproject.org> - 1.7.2.1-2
- cherry-pick: "Do not unquote + into ' ' in URLs"

* Thu Jul 29 2010 Todd Zullinger <tmz@pobox.com> - 1.7.2.1-1
- Update to git-1.7.2.1

* Thu Jul 22 2010 Adam Tkac <atkac redhat com> - 1.7.2-1
- update to 1.7.2

* Fri Jul 02 2010 Adam Tkac <atkac redhat com> - 1.7.1.1-1
- update to 1.7.1.1

* Fri Jun 25 2010 Adam Tkac <atkac redhat com> - 1.7.1-2
- rebuild against new perl

* Tue May 04 2010 Todd Zullinger <tmz@pobox.com> - 1.7.1-1
- git-1.7.1
- Fix conditionals for EL-6
- Comply with Emacs add-on packaging guidelines (#573423), Jonathan Underwood
  - Place elisp source files in separate emacs-git-el package
  - Place git support files in own directory under site-lisp
  - Use Emacs packaging macros

* Thu Apr 29 2010 Marcela Maslanova <mmaslano@redhat.com> - 1.7.0.1-2
- Mass rebuild with perl-5.12.0

* Mon Mar 01 2010 Todd Zullinger <tmz@pobox.com> - 1.7.0.1-1
- git-1.7.0.1

* Sat Feb 13 2010 Todd Zullinger <tmz@pobox.com> - 1.7.0-1
- git-1.7.0
- Link imap-send with libcrypto (#565147)
- Disable building of unused python remote helper libs

* Tue Jan 26 2010 Todd Zullinger <tmz@pobox.com> - 1.6.6.1-1
- git-1.6.6.1
- Use %%{gitcoredir}/git-daemon as xinetd server option, for SELinux (#529682)
- Make %%{_var}/lib/git the default gitweb projectroot (#556299)
- Include gitweb/INSTALL file as documentation, the gitweb README refers to it
- Ship a short example gitweb config file (%%{_sysconfdir}/gitweb.conf)
- Remove long fixed xinetd IPv6 workaround on Fedora (#557528)
- Install missing gitweb.js (#558740)

* Wed Dec 23 2009 Todd Zullinger <tmz@pobox.com> - 1.6.6-1
- git-1.6.6

* Fri Dec 11 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.6-1
- git-1.6.5.6

* Sun Dec 06 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.5-1
- git-1.6.5.5

* Fri Dec  4 2009 Stepan Kasal <skasal@redhat.com> - 1.6.5.3-2
- rebuild against perl 5.10.1

* Sat Nov 21 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.3-1
- git-1.6.5.3
- Only BR perl(Error) on Fedora and RHEL >= 5
- Use config.mak to set build options
- Improve compatibility with EPEL
- Replace $RPM_BUILD_ROOT with %%{buildroot}
- Fix Obsoletes for those rebuilding on EL-4

* Mon Oct 26 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.2-1
- git-1.6.5.2
- Drop asciidoc --unsafe option, it should not be needed anymore
- Don't use install -t/-T, they're not compatible with older coreutils
- Don't use -perm /a+x with find, it's incompatible with older findutils

* Sat Oct 17 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.1-1
- git-1.6.5.1

* Sun Oct 11 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5-1
- git-1.6.5

* Mon Sep 28 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5-0.2.rc2
- git-1.6.5.rc2
- Enable Linus' block-sha1 implementation

* Wed Sep 16 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.4-1
- git-1.6.4.4

* Sun Sep 13 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.3-1
- git-1.6.4.3

* Sun Aug 30 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.2-1
- git-1.6.4.2

* Sat Aug 22 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.1-1
- git-1.6.4.1

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.6.4-2
- rebuilt with new openssl

* Wed Jul 29 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4-1
- git-1.6.4

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jun 28 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.3-1
- git-1.6.3.3
- Move contributed hooks to %%{_datadir}/git-core/contrib/hooks (bug 500137)
- Fix rpmlint warnings about Summary and git-mergetool--lib missing shebang

* Fri Jun 19 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-3
- Temporarily disable asciidoc's safe mode until bug 506953 is fixed

* Fri Jun 19 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-2
- Fix git-daemon hang on invalid input (CVE-2009-2108, bug 505761)

* Fri Jun 05 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-1
- git-1.6.3.2
- Require emacs >= 22.2 for emacs support (bug 495312)
- Add a .desktop file for git-gui (bug 498801)
- Set ASCIIDOC8 and ASCIIDOC_NO_ROFF to correct documentation issues,
  the sed hack to fix bug 485161 should no longer be needed
- Escape newline in git-daemon xinetd description (bug 502393)
- Add xinetd to git-daemon Requires (bug 504105)
- Organize BuildRequires/Requires, drop redundant expat Requires
- Only build noarch subpackages on Fedora >= 10
- Only build emacs and arch subpackages on Fedora
- Handle curl/libcurl naming for EPEL and Fedora

* Fri Apr 03 2009 Todd Zullinger <tmz@pobox.com> - 1.6.2.2-1
- git-1.6.2.2
- Include contrib/ dir in %%doc (bug 492490)
- Don't set DOCBOOK_XSL_172, fix the '\&.ft' with sed (bug 485161)
- Ignore Branches output from cvsps-2.2b1 (bug 490602)
- Remove shebang from bash-completion script
- Include README in gitweb subpackage

* Mon Mar 09 2009 Todd Zullinger <tmz@pobox.com> - 1.6.2-1
- git-1.6.2
- Include contrib/emacs/README in emacs subpackage
- Drop upstreamed git-web--browse patch

* Tue Feb 24 2009 Todd Zullinger <tmz@pobox.com> - 1.6.1.3-2
- Require perl(Authen::SASL) in git-email (bug 483062)
- Build many of the subpackages as noarch
- Update URL field

* Mon Feb 09 2009 Todd Zullinger <tmz@pobox.com> 1.6.1.3-1
- git-1.6.1.3
- Set htmldir so "git help -w <command>" works
- Patch git-web--browse to not use "/sbin/start" to browse
- Include git-daemon documentation in the git-daemon package

* Thu Jan 29 2009 Josh Boyer <jwboyer@gmail.com> 1.6.1.2-1
- git-1.6.1.2

* Mon Jan 26 2009 Todd Zullinger <tmz@pobox.com> 1.6.1.1-1
- git-1.6.1.1
- Make compile more verbose

* Fri Jan 16 2009 Tomas Mraz <tmraz@redhat.com> 1.6.1-2
- rebuild with new openssl

* Sat Jan 03 2009 Todd Zullinger <tmz@pobox.com> 1.6.1-1
- Install git-* commands in %%{_libexecdir}/git-core, the upstream default
- Remove libcurl from Requires, rpm will pick this up automatically
- Consolidate build/install options in %%make_git (Roland McGrath)
- Include DirectoryIndex in gitweb httpd-config (bug 471692)
- Define DOCBOOK_XSL_172 to fix minor manpage issues
- Rename %%{_var}/lib/git-daemon to %%{_var}/lib/git
- Preserve timestamps on installed files
- Quiet some rpmlint complaints
- Use macros more consistently

* Sat Dec 20 2008 Todd Zullinger <tmz@pobox.com> 1.6.0.6-1
- git-1.6.0.6
- Fixes a local privilege escalation bug in gitweb
  (http://article.gmane.org/gmane.comp.version-control.git/103624)
- Add gitk Requires to git-gui (bug 476308)

* Thu Dec 11 2008 Josh Boyer <jboyer@gmail.com> 1.6.0.5-1
- git-1.6.0.5

* Mon Nov 17 2008 Seth Vidal <skvidal at fedoraproject.org>
- switch from /srv/git to /var/lib/git-daemon for packaging rules compliance

* Fri Nov 14 2008 Josh Boyer <jwboyer@gmail.com> 1.6.0.4-1
- git-1.6.0.4

* Wed Oct 22 2008 Josh Boyer <jwboyer@gmail.com> 1.6.0.3-1
- git-1.6.0.3
- Drop curl requirement in favor of libcurl (bug 449388)
- Add requires for SMTP-SSL perl module to make git-send-email work (bug 443615)

* Thu Aug 28 2008 James Bowes <jbowes@redhat.com> 1.6.0.1-1
- git-1.6.0.1

* Thu Jul 24 2008 James Bowes <jbowes@redhat.com> 1.5.6-4
- git-1.5.6.4

* Thu Jun 19 2008 James Bowes <jbowes@redhat.com> 1.5.6-1
- git-1.5.6

* Tue Jun  3 2008 Stepan Kasal <skasal@redhat.com> 1.5.5.3-2
- use tar.bz2 instead of tar.gz

* Wed May 28 2008 James Bowes <jbowes@redhat.com> 1.5.5.3-1
- git-1.5.5.3

* Mon May 26 2008 James Bowes <jbowes@redhat.com> 1.5.5.2-1
- git-1.5.5.2

* Mon Apr 21 2008 James Bowes <jbowes@redhat.com> 1.5.5.1-1
- git-1.5.5.1

* Wed Apr 09 2008 James Bowes <jbowes@redhat.com> 1.5.5-1
- git-1.5.5

* Fri Apr 04 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-3
- Remove the last two requires on git-core.

* Wed Apr 02 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-2
- Remove a patch that's already upstream.

* Fri Mar 28 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-1
- git-1.5.4.5

* Wed Mar 26 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-4
- Own /etc/bash_completion.d in case bash-completion isn't installed.

* Tue Mar 25 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-3
- Include the sample hooks from contrib/hooks as docs (bug 321151).
- Install the bash completion script from contrib (bug 433255).
- Include the html docs in the 'core' package again (bug 434271).

* Wed Mar 19 2008 James Bowes 1.5.4.4-2
- Obsolete git <= 1.5.4.3, to catch going from F8 to rawhide/F9

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

* Sun May 13 2007 Quy Tonthat <qtonthat@gmail.com>
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

* Tue Feb 13 2007 Nicolas Pitre <nico@cam.org>
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

* Wed Feb 1 2006 Chris Wright <chrisw@redhat.com> 1.1.6-1
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
-        git-core, git-svn, git-cvs, git-arch, gitk

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
- own %%{_datadir}/git-core/

* Mon Aug 15 2005 Chris Wright <chrisw@osdl.org>
- update spec file to fix Buildroot, Requires, and drop Vendor

* Sun Aug 07 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Redid the description
- Cut overlong make line, loosened changelog a bit
- I think Junio (or perhaps OSDL?) should be vendor...

* Thu Jul 14 2005 Eric Biederman <ebiederm@xmission.com>
- Add the man pages, and the --without docs build option

* Thu Jul 7 2005 Chris Wright <chris@osdl.org>
- initial git spec file
