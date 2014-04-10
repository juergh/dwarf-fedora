# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DIST ?= .fc20
VERSION = $(shell awk '/^Version: / {print $$2}' dwarf.spec)

all: rpm

tgz:
	wget -O dwarf-$(VERSION).tar.gz \
		https://github.com/juergh/dwarf/archive/v$(VERSION).tar.gz

rpm: tgz
rpm:
	rm -rf build || true
	rpmbuild -ba \
                --define='_topdir $(CURDIR)/build' \
                --define='_sourcedir $(CURDIR)' \
                --define='dist $(DIST)' \
		dwarf.spec && \
	mv build/SRPMS/* . && \
	mv build/RPMS/noarch/* .

srpm: tgz
srpm:
	rm -rf build || true
	rpmbuild -bs \
                --define='_topdir $(CURDIR)/build' \
                --define='_sourcedir $(CURDIR)' \
		dwarf.spec && \
	mv build/SRPMS/* .

mock: srpm
	sudo mock \
		--root=fedora-20-x86_64 \
		--rebuild \
		--resultdir=$(CURDIR) \
		--define='dist $(DIST)' \
		dwarf-$(VERSION)-*$(DIST).src.rpm

clean:
	@find . \( -name '*~' \) -type f -print | \
		xargs rm -f
	@rm -rf build *.tar.gz *.rpm || :
