Name:           uwsgi
Version:        2.0.10
Release:        2%{?dist}
Summary:        Fast, self-healing, application container server
Group:          System Environment/Daemons
License:        GPLv2
URL:            http://projects.unbit.it/uwsgi
Source0:        http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
Source1:        rhel6.ini
Source2:        uwsgi.init
Source3:        spinningfifo.c
Source4:        uwsgiplugin.py
Patch0:         uwsgi_trick_chroot_rpmbuild.patch
Patch1:         uwsgi_fix_rpath.patch
BuildRequires:  python2-devel, libxml2-devel, libuuid-devel, ruby, ruby-devel
BuildRequires:  libyaml-devel, perl-devel, pcre-devel, perl-ExtUtils-Embed
Requires: /bin/bash libboost_filesystem.so.1.57.0()(64bit) libboost_system.so.1.57.0()(64bit) libboost_thread.so.1.57.0()(64bit) libc.so.6()(64bit) libc.so.6(GLIBC_2.10)(64bit) libc.so.6(GLIBC_2.2.5)(64bit) libc.so.6(GLIBC_2.3)(64bit) libc.so.6(GLIBC_2.3.2)(64bit) libc.so.6(GLIBC_2.3.4)(64bit) libc.so.6(GLIBC_2.4)(64bit) libc.so.6(GLIBC_2.8)(64bit) libcrypt.so.1()(64bit) libcrypt.so.1(GLIBC_2.2.5)(64bit) libcrypto.so.10()(64bit) libcrypto.so.10(OPENSSL_1.0.1_EC)(64bit) libcrypto.so.10(libcrypto.so.10)(64bit) libdl.so.2()(64bit) libdl.so.2(GLIBC_2.2.5)(64bit) libgcc_s.so.1()(64bit) libgcc_s.so.1(GCC_3.0)(64bit) libm.so.6()(64bit) libm.so.6(GLIBC_2.2.5)(64bit) libmongoclient.so.1()(64bit) libpcre.so.0()(64bit) libpthread.so.0()(64bit) libpthread.so.0(GLIBC_2.2.5)(64bit) libpthread.so.0(GLIBC_2.4)(64bit) libssl.so.10()(64bit) libssl.so.10(libssl.so.10)(64bit) libutil.so.1()(64bit) libuuid.so.1()(64bit) libuuid.so.1(UUID_1.0)(64bit) libxml2.so.2()(64bit) libxml2.so.2(LIBXML2_2.4.30)(64bit) libxml2.so.2(LIBXML2_2.6.0)(64bit) libz.so.1()(64bit) libz.so.1(ZLIB_1.2.0)(64bit) rtld(GNU_HASH)
Autoreq: 0

%description
uWSGI is a fast (pure C), self-healing, developer/sysadmin-friendly
application container server.  Born as a WSGI-only server, over time it has
evolved in a complete stack for networked/clustered web applications,
implementing message/object passing, caching, RPC and process management.
It uses the uwsgi (all lowercase, already included by default in the Nginx
and Cherokee releases) protocol for all the networking/interprocess
communications.  Can be run in preforking mode, threaded,
asynchronous/evented and supports various form of green threads/co-routine
(like uGreen and Fiber).  Sysadmin will love it as it can be configured via
command line, environment variables, xml, .ini and yaml files and via LDAP.
Being fully modular can use tons of different technology on top of the same
core.

%package -n %{name}-devel
Summary:  uWSGI - Development header files and libraries
Group:    Development/Libraries
Requires: %{name}

%description -n %{name}-devel
This package contains the development header files and libraries
for uWSGI extensions


%prep
%setup -q
cp -p %{SOURCE1} buildconf/
mkdir -p plugins/spinningfifo
cp -p %{SOURCE3} plugins/spinningfifo/
cp -p %{SOURCE4} plugins/spinningfifo/
echo "plugin_dir = %{_libdir}/%{name}" >> buildconf/$(basename %{SOURCE1})
%patch0 -p1
%patch1 -p1

%build
CFLAGS="%{optflags}" /usr/local/bin/python2.7 uwsgiconfig.py --build rhel6

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_includedir}/%{name}
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/run/%{name}
%{__install} -p -m 0755 uwsgi %{buildroot}%{_sbindir}
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -p -m 0755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -m 0644 *.h %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 0755 *_plugin.so %{buildroot}%{_libdir}/%{name}

%pre
getent group uwsgi >/dev/null || groupadd -r uwsgi
getent passwd uwsgi >/dev/null || \
    useradd -r -g uwsgi -d '/etc/uwsgi' -s /sbin/nologin \
    -c "uWSGI Service User" uwsgi

%post
/sbin/chkconfig --add uwsgi

%preun
if [ $1 -eq 0 ]; then
    /sbin/service uwsgi stop >/dev/null 2>&1
    /sbin/chkconfig --del uwsgi
fi

%postun
if [ $1 -ge 1 ]; then
    /sbin/service uwsgi condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%{_sbindir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_initrddir}/%{name}
%doc LICENSE README
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/log/%{name}
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/run/%{name}
%{_libdir}/%{name}/spinningfifo_plugin.so
%{_libdir}/%{name}/stats_pusher_mongodb_plugin.so

%files -n %{name}-devel
%{_includedir}/%{name}

%changelog
* Thu Apr 8 2015 Michal Kubenka <mkubenka@gmail.com> - 2.0.10-2
- Ensure that the pidfile path exists.

* Thu Mar 26 2015 Michal Kubenka <mkubenka@gmail.com> - 2.0.10-1
- Updated to latest upstream stable version

* Tue Dec 02 2014 Mark Carbonaro <mark@carbonaro.org> - 2.0.8
- Updated to latest upstream stable version
- Added http and corerouter plugins

* Sat Sep 06 2014 Alan Chalmers <alan.chalmers@gmail.com> - 2.0.7
- Upgraded to latest stable upstream version

* Thu Jun 19 2014 Aleks Bunin <sbunin@gmail.com> - 2.0.5.1-2
- Restored cgi plugin

* Tue Jun 03 2014 Sergey Morozov <sergey.morozov@corp.mail.ru> - 2.0.5.1-1
- Build now inherits "base" buildconf with only python, rack and psgi plugins
- Removed wiki doc
- Upgraded to latest stable upstream version

* Thu Apr 19 2012 Aleks Bunin <sbunin@gmail.com> - 1.1.2-1
- RHEL 6 Support (removed not compatible plugins)
- Upgraded to latest stable upstream version

* Sun Feb 19 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.4-1
- Addressing issues from package review feedback
- s/python-devel/python2-devel
- Make the libdir subdir owned by -plugins-common
- Upgraded to latest stable upstream version

* Mon Feb 06 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.2.1-2
- Fixing 'unstripped-binary-or-object'

* Thu Jan 19 2012 Jorge A Gallegos <kad@blegh.net> - 1.0.2.1-1
- New upstream version

* Thu Dec 08 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.3-1
- New upstream version

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-2
- Don't download the wiki page at build time

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-1
- Updated to latest stable version
- Correctly linking plugin_dir
- Patches 1 and 2 were addressed upstream

* Sun Aug 21 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.8.3-3
- Got rid of BuildRoot
- Got rid of defattr()

* Sun Aug 14 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-2
- Added uwsgi_fix_rpath.patch
- Backported json_loads patch to work with jansson 1.x and 2.x
- Deleted clean steps since they are not needed in fedora

* Sun Jul 24 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-1
- rebuilt
- Upgraded to latest stable version 0.9.8.3
- Split packages

* Sun Jul 17 2011 Jorge Gallegos <kad@blegh.net> - 0.9.6.8-2
- Heavily modified based on Oskari's work

* Mon Feb 28 2011 Oskari Saarenmaa <os@taisia.fi> - 0.9.6.8-1
- Initial.
