SRPM tools for git 2.26.x

This github repo includes tools for building git-2.26.x RPMs. It is
based on the latest Fedora RPMs, with hooks for buiiding on Fedora and
RHEL, and with modifications from iusrelease to bundle as "git2u", for
separate installation from the standard "git" package and
repositories.

    https://www.kernel.org/pub/software/scm/git/

"make" options include:

  * make getsrc # Download the source tarballs
  * make build # Build with all docs and tests
  * make fastbuild # Build without docs and tests for fast smoke test

  * make # Build full multi-platform versions with mock
  * make install # build and install multi-platform versions in REPOBASEDIR

Run the "make getsrc" command, and run "make build" to build a local RPM under
rpmbuild.



Run "make" to use "mock" to build the default designated RPM's in the
local working directories such as epel-7-x86_64 and epel-6-x86_64.

       	  Nico Kadel-Garcia <nkadelgmail.com>
