Summary:	Network CD Writing tool
Summary(pl):	Narz�dzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.4.2
Release:	0.1
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://129.70.4.38/download/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
URL:		http://www.uni-bielefeld.de/~jhaeger/webCDwriter/
Requires:	cdrecord >= 1.10
Requires:	mkisofs
Requires:	mpg123
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define CDWuser webCDwriter
%define CDWgroup cdwrite

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
webCdwriter mo�e by� u�ywany do udost�pniania pojedynczej nagrywarki
dla wszystkich u�ytkownik�w sieci. Zawiera serwer CDWserver oraz
klient�w: webCDcreator i rcdrecord. CDWserver przechowuje pliki
transmitowane przez klient�w, zarz�dza nagrywark� u�ywaj�c do tego
celu cdrecord. webCDcreator jest apletem Javy uruchamianym z
przegl�darki (Mozilla, Netscape...), pomagaj�cym transmitowa� pliki.
rcdrecord jest uruchamianym w pow�oce klientem kt�ry spe�nia funkcje
cdrecord w sieci (jeszcze nie sko�czony).

%package rcdrecord
Summary:	Network CD Writing tool - remote client
Summary(pl):	Narz�dzie do sieciowego nagrywania CD - zdalny klient
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

%{__make} "CXXFLAGS=%{rpmcflags} -Wall -D_REENTRANT"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},/etc/rc.d/init.d,/home/services/CDWserver}
%{__make} \
    BINDIR=$RPM_BUILD_ROOT%{_bindir} install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/CDWserver

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CREDITS ChangeLog README *.html
%attr(754,root,root) /etc/rc.d/init.d/CDWserver
%dir %attr(0755,%{CDWuser},%{CDWgroup}) /etc/CDWserver/
%attr(0600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/accounts
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/config*
%attr(4750,root,%{CDWgroup}) %{_bindir}/setScheduler
%attr(4750,root,%{CDWgroup}) %{_bindir}/CDWverify
%attr(755,root,root) %{_sbindir}/CDWserver
%dir %attr(0700,%{CDWuser},%{CDWgroup}) /var/log/CDWserver/
%dir %attr(0700,%{CDWuser},%{CDWgroup}) /var/spool/CDWserver/
# cleanup (and patches) needed
%dir %attr(0755, %{CDWuser}, %{CDWgroup}) /etc/CDWserver/export/
/etc/CDWserver/favicon.ico
/etc/CDWserver/footer
/etc/CDWserver/greeting
/etc/CDWserver/header
/etc/CDWserver/logo.png
/etc/CDWserver/status.html
/etc/CDWserver/waitForCD
/etc/CDWserver/about.html
/etc/CDWserver/head
/etc/CDWserver/help*
/etc/CDWserver/messages*
/etc/CDWserver/export/*
/etc/CDWserver/rcdrecord/*
/etc/CDWserver/webCDcreator/*.html
/etc/CDWserver/webCDcreator/*.jnlp
/etc/CDWserver/webCDcreator/4netscape/*
/etc/CDWserver/webCDcreator/4plugin/*
/etc/CDWserver/webCDcreator/4pluginRSA/*
/etc/CDWserver/webCDcreator/doc/*
/etc/CDWserver/webCDcreator/i18n/*
/etc/CDWserver/webCDcreator/icons/*
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /home/services/CDWserver/

%files rcdrecord
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/rcdrecord

%pre
if [ -n "`/usr/bin/getgid %{CDWgroup}`" ]; then
	if [ "`getgid %{CDWgroup}`" != "27" ]; then
		echo "Error: group %{CDWgroup} doesn't have gid=27. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 27 %{CDWgroup}
fi
if [ -z "`/bin/id -u %{CDWuser} 2>/dev/null`" ]; then
	/usr/sbin/useradd -d /home/services/CDWserver -s /bin/false -c "webCDwriter user" -g %{CDWgroup} %{CDWuser}
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
