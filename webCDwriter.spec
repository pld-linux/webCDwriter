Summary:	Network CD Writing tool
Summary(pl):	Narzêdzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.4.1
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://129.70.4.38/download/%{name}-%{version}.tar.bz2
URL:		http://www.uni-bielefeld.de/~jhaeger/webCDwriter/
Requires:	cdrecord >= 1.10
Requires:	lynx
Requires:	mkisofs
Requires:	mpg123
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define CDWgroup cdwriter
%define CDWuser cdwriter

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

%prep
%setup -q

%build
./configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
%{__make} \
    BINDIR=$RPM_BUILD_ROOT%{_bindir} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING CREDITS ChangeLog README *.html
%dir %attr(0755, %{CDWuser}, %{CDWgroup}) %{_sysconfdir}/CDWserver/
%dir %attr(0755, %{CDWuser}, %{CDWgroup}) %{_sysconfdir}/CDWserver/export/
%config(noreplace) %attr(0600, %{CDWuser}, %{CDWgroup}) %{_sysconfdir}/CDWserver/accounts
%config(noreplace) %{_sysconfdir}/CDWserver/config*
%config(noreplace) %{_sysconfdir}/CDWserver/favicon.ico
%config(noreplace) %{_sysconfdir}/CDWserver/footer
%config(noreplace) %{_sysconfdir}/CDWserver/greeting
%config(noreplace) %{_sysconfdir}/CDWserver/header
%config(noreplace) %{_sysconfdir}/CDWserver/logo.png
%config(noreplace) %{_sysconfdir}/CDWserver/status.html
%config(noreplace) %{_sysconfdir}/CDWserver/waitForCD
%{_sysconfdir}/CDWserver/export/*
%{_sysconfdir}/CDWserver/rcdrecord/*
%config(noreplace) %{_sysconfdir}/CDWserver/webCDcreator/*.html
%config(noreplace) %{_sysconfdir}/CDWserver/webCDcreator/*.jnlp
%{_sysconfdir}/CDWserver/webCDcreator/4netscape/*
%{_sysconfdir}/CDWserver/webCDcreator/4plugin/*
%{_sysconfdir}/CDWserver/webCDcreator/4pluginRSA/*
%{_sysconfdir}/CDWserver/webCDcreator/doc/*
%{_sysconfdir}/CDWserver/webCDcreator/i18n/*
%{_sysconfdir}/CDWserver/webCDcreator/icons/*
/etc/rc.d/init.d/CDWserver
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /home/CDWserver/
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/rcdrecord
%attr(4710, root, cdwriter) %{_bindir}/setScheduler
%attr(4710, root, cdwriter) %{_bindir}/CDWverify
%attr(755,root,root) %{_sbindir}/CDWserver
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /var/log/CDWserver/
%dir %attr(0700, %{CDWuser}, %{CDWgroup}) /var/spool/CDWserver/

%pre
# Add the "webCDwriter" user and group
#/usr/sbin/groupadd %{CDWgroup} 2> /dev/null || :
#/usr/sbin/useradd -c "webCDwriter user" \
#	-g %{CDWgroup} %{CDWuser} 2> /dev/null || :

%post
/sbin/chkconfig --add CDWserver
if [ -f /var/lock/subsys/postfix ]; then
	/etc/rc.d/init.d/postfix restart >&2
else
	echo "Run \"/etc/rc.d/init.d/postfix start\" to start postfix daemon." >&2
fi

# make cdrecord and mkisofs setuid root
#chown root.%{CDWgroup} /usr/bin/cdrecord /usr/bin/mkisofs
#chmod 4710 /usr/bin/cdrecord /usr/bin/mkisofs
#
#echo
#echo -e "Now you can start CDWserver by"
#echo -e "   service CDWserver start"
#echo -e "Then visit"
#echo -e "   http://`hostname`:12411"
#echo -e "or try rcdrecord or files2cd on the command line."
#echo

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/postfix ]; then
		/etc/rc.d/init.d/postfix stop >&2
	fi
	/sbin/chkconfig --del postfix

#	if [ -f /var/lock/subsys/web ]; then
#	service CDWserver stop || :
#	/sbin/chkconfig --del CDWserver
#	rm /var/spool/CDWserver/* -rf
fi

%postun
if [ "$1" = "0" ]; then
	# reset the owner and mode of cdrecord and mkisofs
	#chgrp root /usr/bin/cdrecord /usr/bin/mkisofs
	#chmod 755 /usr/bin/cdrecord /usr/bin/mkisofs
fi
