Summary:        OpenStack API on top of libvirt/kvm
Name:           dwarf
Version:        0.1.5
Release:        0%{?dist}
License:        Apache 2.0
Group:          System Environment/Base
URL:            https://github.com/juergh/dwarf

Source0:        dwarf-%{version}.tar.gz
Source10:       dwarf.service
Source20:       dwarf-polkit.rules

BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  systemd-units

Requires:       iptables
Requires:       libvirt-daemon
Requires:       libvirt-daemon-config-network
Requires:       libvirt-daemon-config-nwfilter
Requires:       libvirt-daemon-driver-network
Requires:       libvirt-daemon-driver-qemu
Requires:       libvirt-python
Requires:       polkit
Requires:       python-bottle
Requires:       python-cheetah
Requires:       python-m2ext
Requires:       python-simplejson
Requires:       python-yaml
Requires:       qemu-kvm
Requires:       shadow-utils
Requires:       systemd-units


%description
In a nutshell, dwarf is OpenStack API on top of local libvirt/kvm. It supports
a subset of the Keystone, Glance and Nova APIs to manage images and instances
on the local machine.


%prep
%setup -q


%build
%{__python} setup.py build


%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# etc files
install -p -D -m 644 etc/dwarf.conf %{buildroot}/etc/dwarf.conf
install -p -D -m 400 etc/sudoers.d/dwarf %{buildroot}/etc/sudoers.d/dwarf

# systemd files
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/dwarf.service

# polkit files
install -p -D -m 644 %{SOURCE20} %{buildroot}%{_sysconfdir}/polkit-1/rules.d/50-dwarf.rules


%pre
if ! getent group dwarf >/dev/null ; then
    groupadd -r dwarf
fi
if ! getent passwd dwarf >/dev/null ; then
    useradd -r -g dwarf -G dwarf,nobody,qemu -d /var/lib/dwarf \
	-s /sbin/nologin dwarf
fi


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    mkdir -p /var/lib/dwarf/instances/_base
    mkdir -p /var/lib/dwarf/images

    chown -R dwarf:dwarf /var/lib/dwarf /etc/dwarf.conf

    chown root:root /etc/sudoers.d/dwarf
    chmod 440 /etc/sudoers.d/dwarf

    if [ ! -e /var/lib/dwarf/dwarf.db ] ; then
	su -s /bin/sh -c 'dwarf-manage db-init' dwarf
    fi

    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    /bin/systemctl enable dwarf.service > /dev/null 2>&1 || :
fi


%preun
if [ $1 -eq 0 ] ; then
    /bin/systemctl --no-reload disable dwarf.service > /dev/null 2>&1 || :
    /bin/systemctl stop dwarf.service > /dev/null 2>&1 || :
fi


%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
   /bin/systemctl try-restart dwarf.service >/dev/null 2>&1 || :
fi


%files
%doc README LICENSE ChangeLog

# etc files
%config(noreplace) /etc/dwarf.conf
%config(noreplace) /etc/sudoers.d/dwarf

# polkit files
%config(noreplace) %{_sysconfdir}/polkit-1/rules.d/50-dwarf.rules

# scripts
%{_bindir}/dwarf
%{_bindir}/dwarf-manage

# python files
%{python_sitelib}/*

# systemd files
%{_unitdir}/dwarf.service


%changelog
* Mon Apr 10 2014 Juerg Haefliger <juerg.haefliger@hp.com> - 0.1.5-0
- Initial package
