Summary:	Network CD Writing tool
Summary(pl):	Narzêdzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.6.2
Release:	0.1
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://JoergHaeger.de/webCDwriter/download/%{name}-%{version}.tar.bz2
# Source0-md5:	d1280b4323aace88742c3bc28fe80e02
# Source0Download: http://joerghaeger.de/webCDwriter/TARs.html
Source1:	%{name}.init
URL:		http://JoergHaeger.de/webCDwriter/
Requires(pre):	/bin/chown
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/find
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires:	cdrtools
Requires:	mkisofs
Requires:	mpg123
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	CDWuser		webcdwriter
%define	CDWgroup	cdwrite

%description
webCDwriter can be used to make a single CD-writer available to the
users in your network. It consists of the server CDWserver and the
clients webCDcreator and rcdrecord. CDWserver stores the files
transmitted by the clients, reserves the CD-writer and controls the
CD-writer using cdrecord. webCDcreator is a Java applet that runs
within your browser (Mozzila, Netscape...), assists you when putting
together a CD and transmits the files. Finally rcdrecord is a command
line client that trys to offer the functionality of cdrecord over the
network (not complete yet).

%description -l pl
webCdwriter mo¿e byæ u¿ywany do udostêpniania pojedynczej nagrywarki
dla wszystkich u¿ytkowników sieci. Zawiera serwer CDWserver oraz
klientów: webCDcreator i rcdrecord. CDWserver przechowuje pliki
transmitowane przez klientów, zarz±dza nagrywark± u¿ywaj±c do tego
celu cdrecord. webCDcreator jest apletem Javy uruchamianym z
przegl±darki (Mozilla, Netscape...), pomagaj±cym transmitowaæ pliki.
rcdrecord jest uruchamianym w pow³oce klientem który spe³nia funkcje
cdrecord w sieci (jeszcze nie skoñczony).

%package rcdrecord
Summary:	Network CD Writing tool - remote client
Summary(pl):	Narzêdzie do sieciowego nagrywania CD - zdalny klient
Group:		Networking/Utilities

%description rcdrecord
Remote client for webCDwriter

%description rcdrecord -l pl
Zdalny klient dla webCDwriter

%prep
%setup -q

%build
./configure \
	--user=%{CDWuser} \
	--group=%{CDWgroup}

%{__make} CXXFLAGS="%{rpmcflags} -Wall -D_REENTRANT"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},/etc/rc.d/init.d,/home/services/CDWserver/bin}
%{__make} \
	BINDIR=$RPM_BUILD_ROOT%{_bindir} \
	HOMEBINDIR=$RPM_BUILD_ROOT/home/services/CDWserver/bin \
	install

rm -f $RPM_BUILD_ROOT%{_bindir}/*-dummy

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/CDWserver

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" = 2 ] && ! id -u %{CDWuser} >/dev/null 2>&1 && \
   id -u webCDwriter >/dev/null 2>&1; then
	OLDUID=`id -u webCDwriter`
	/usr/sbin/usermod -u 109 -d /home/services/CDWserver -m -l webCDwriter %{CDWuser} 1>&2
	find /home/services/CDWserver -uid $OLDUID -exec chown %{CDWuser} {} \;
fi
if [ -n "`/usr/bin/getgid %{CDWgroup}`" ]; then
	if [ "`getgid %{CDWgroup}`" != "27" ]; then
		echo "Error: group %{CDWgroup} doesn't have gid=27. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 27 %{CDWgroup}
fi
if [ -n "`id -u %{CDWuser} 2>/dev/null`" ]; then
	if [ "`id -u %{CDWuser}`" != 109 ]; then
		echo "Error: user %{CDWuser} doesn't have uid=109. Correct this before installing %{name}." 1>&2
	else
		/usr/sbin/useradd -u 109 -r -d /home/services/CDWserver -s /bin/false -c "%{name} user" -g %{CDWgroup} %{CDWuser} 1>&2
	fi
fi

%post
/sbin/chkconfig --add CDWserver
if [ -f /var/lock/subsys/CDWserver ]; then
	/etc/rc.d/init.d/CDWserver restart >&2
else
	echo "Run \"/etc/rc.d/init.d/CDWserver start\" to start webCDwriter daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/CDWserver ]; then
		/etc/rc.d/init.d/CDWserver stop >&2
	fi
	/sbin/chkconfig --del CDWserver
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel %{CDWuser}
	/usr/sbin/groupdel %{CDWgroup}
fi

%files
%defattr(644,root,root,755)
%doc CREDITS ChangeLog README *.html
%attr(754,root,root) /etc/rc.d/init.d/CDWserver
%dir %attr(0755,%{CDWuser},%{CDWgroup}) /etc/CDWserver
%attr(0600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/accounts
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/config*
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/greeting
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/waitForCD
%attr(0600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/password
%attr(4754,root,%{CDWgroup}) %{_bindir}/*
%exclude %{_bindir}/files2cd
%exclude %{_bindir}/image2cd
%exclude %{_bindir}/rcdrecord
%attr(755,root,root) %{_sbindir}/CDWserver
%dir %attr(0700,%{CDWuser},%{CDWgroup}) /var/log/CDWserver
%dir %attr(0700,%{CDWuser},%{CDWgroup}) /var/spool/CDWserver
# cleanup (and patches) needed
/etc/CDWserver/export/*
%dir %attr(0755, %{CDWuser}, %{CDWgroup}) /etc/CDWserver/export
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /home/services/CDWserver
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /home/services/CDWserver/bin
%attr(0700, %{CDWuser}, %{CDWgroup}) /home/services/CDWserver/bin/*-dummy
/etc/CDWserver/http

%files rcdrecord
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/image2cd
%attr(755,root,root) %{_bindir}/rcdrecord
