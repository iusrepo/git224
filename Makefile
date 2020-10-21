#
# Build mock and local RPM versions of tools for RT
#

# Assure that sorting is case sensitive
LANG=C

# Ignore ownership and group,
RSYNCOPTS=-a --no-owner --no-group
# Skip existing files to avoid binary churn in yum repos
RSYNCSAFEOPTS=$(RSYNCOPTS) --ignore-existing 

# "mock" configurations to build with, activate only as needed
#MOCKS+=fedora-32-x86_64
MOCKS+=epel-8-x86_64
MOCKS+=epel-7-x86_64
MOCKS+=epel-6-x86_64

#REPOBASEDIR=/var/www/linux/gitrepo
REPOBASEDIR:=`/bin/pwd`/gitrepo

SPEC := `ls *.spec | head -1`

all:: $(MOCKS)

.PHONY: getsrc
getsrc::
	spectool -g $(SPEC)

srpm:: src.rpm

#.PHONY:: src.rpm
src.rpm:: Makefile
	@rm -rf rpmbuild
	@rm -f $@
	@echo "Building SRPM with $(SPEC)"
	rpmbuild --define '_topdir $(PWD)/rpmbuild' \
		--define '_sourcedir $(PWD)' \
		-bs $(SPEC) --nodeps
	mv rpmbuild/SRPMS/*.src.rpm src.rpm

.PHONY: build
build:: src.rpm
	rpmbuild --define '_topdir $(PWD)/rpmbuild' \
		--rebuild $?

.PHONY: fastbuild
fastbuild:: src.rpm
	rpmbuild --define '_topdir $(PWD)/rpmbuild' \
		--without docs \
		--without tests \
		--rebuild $?

.PHONY: $(MOCKS)
$(MOCKS):: src.rpm
	@if [ -e $@ -a -n "`find $@ -name \*.rpm 2>/dev/null`" ]; then \
		echo "	Skipping RPM populated $@"; \
	else \
		echo "Actally building $? in $@"; \
		rm -rf $@; \
		mock -q -r /etc/mock/$@.cfg \
		     --resultdir=$(PWD)/$@ \
		     $?; \
	fi

mock:: $(MOCKS)

install:: $(MOCKS)
	@for repo in $(MOCKS); do \
	    echo Installing $$repo; \
	    case $$repo in \
		*-6-x86_64) yumrelease=el/6; yumarch=x86_64; ;; \
		*-7-x86_64) yumrelease=el/7; yumarch=x86_64; ;; \
		*-8-x86_64) yumrelease=el/8; yumarch=x86_64; ;; \
		*-32-x86_64) yumrelease=fedora/32; yumarch=x86_64; ;; \
		*-f32-x86_64) yumrelease=fedora/32; yumarch=x86_64; ;; \
		*-rawhide-x86_64) yumrelease=fedora/rawhide; yumarch=x86_64; ;; \
		*) echo "Unrecognized release for $$repo, exiting" >&2; exit 1; ;; \
	    esac; \
	    rpmdir=$(REPOBASEDIR)/$$yumrelease/$$yumarch; \
	    srpmdir=$(REPOBASEDIR)/$$yumrelease/SRPMS; \
	    install -d $$rpmdir; \
	    install -d $$srpmdir; \
	    echo "    Pushing SRPMS to $$srpmdir"; \
	    rsync -a $$repo/*.src.rpm --no-owner --no-group $$repo/*.src.rpm $$srpmdir/. || exit 1; \
	    createrepo -q $$srpmdir/.; \
	    echo "    Pushing RPMS to $$rpmdir"; \
	    rsync -a $$repo/*.rpm --exclude=*.src.rpm --exclude=*debuginfo*.rpm --no-owner --no-group $$repo/*.rpm $$rpmdir/. || exit 1; \
	    createrepo -q $$rpmdir/.; \
	done

clean::
	rm -rf */
	rm -f *.out
	rm -f *.rpm

realclean distclean:: clean
