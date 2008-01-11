# TODO:
# - add certificate and compiling java client
# - make install attempts to useradd/groupadd and possibly succeeds if ran as root

%define	CDWuser		webcdwriter
%define	CDWgroup	cdwrite

Summary:	Network CD Writing tool
Summary(pl.UTF-8):	Narzędzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.8.1
Release:	2
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://joerghaeger.de/webCDwriter/download/%{name}-%{version}.tar.bz2
# Source0-md5:	7cf04f31507a1da96073eef2d50b65b0
Patch0:		%{name}-FHS.patch
# Source0Download: http://joerghaeger.de/webCDwriter/TARs.html
URL:		http://JoergHaeger.de/webCDwriter/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	pam-devel
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/chown
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/find
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires:	/usr/bin/isoinfo
Requires:	/usr/bin/mkisofs
Requires:	/usr/bin/readcd
Requires:	cdrdao
Requires:	cdrtools >= 2.01
Requires:	mpg123
Requires:	sox
Provides:	group(%{CDWgroup})
Provides:	user(%{CDWuser})
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/CDWserver

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

%description -l pl.UTF-8
webCdwriter służy do udostępniania pojedynczej nagrywarki dla
wszystkich użytkowników sieci. Zawiera serwer CDWserver oraz klientów:
webCDcreator i rcdrecord. CDWserver przechowuje pliki transmitowane
przez klientów, zarządza nagrywarką używając do tego celu cdrecord.
webCDcreator jest apletem Javy uruchamianym z przeglądarki (Mozilla,
Netscape, Internet Explorer,...), pomagającym transmitować pliki.
rcdrecord jest uruchamianym w powłoce klientem który spełnia funkcje
cdrecord w sieci (jeszcze nie skończony).

%package rcdrecord
Summary:	Network CD Writing tool - remote client
Summary(pl.UTF-8):	Narzędzie do sieciowego nagrywania CD - zdalny klient
Group:		Networking/Utilities

%description rcdrecord
Remote client for webCDwriter.

%description rcdrecord -l pl.UTF-8
Zdalny klient dla webCDwritera.

%prep
%setup -q
%patch0 -p1

%build

./configure	--pam \
		--group=%{CDWgroup} \
		--user=%{CDWuser} \
		--port=12411 \
		--destDir=$RPM_BUILD_ROOT \
		--doNotCompileWebCDcreator

#		--nosCert= # Netscape Object Signing Certificate
#		--sunCert= # certificate for the keytool from Sun
#		--debug

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
# looks like make install auto users $RPM_BUILD_ROOT?
%{__make} install

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_datadir}/CDWserver}
mv $RPM_BUILD_ROOT/etc/init.d/CDWserver $RPM_BUILD_ROOT/etc/rc.d/init.d/CDWserver
rm $RPM_BUILD_ROOT%{_bindir}/CDWuninstall.sh

%clean
if [ ! -e $RPM_BUILD_ROOT/dev/ ]; then
	rm -rf $RPM_BUILD_ROOT
fi

%pre
%groupadd -g 27 %{CDWgroup}
%useradd -g %{CDWgroup} -c "%{name} user" -u 109 -r -d %{_var}/lib/CDWserver -s /bin/false %{CDWuser}

%post
# TODO use trigger if it's from older PLD package or discard
# Since rpm will not change the owner of an existing %config file

%{__chown} %{CDWuser} %{_sysconfdir}/accounts 2> /dev/null || :
%{__chown} %{CDWuser} %{_sysconfdir}/config 2> /dev/null || :
%{__chown} %{CDWuser} %{_sysconfdir}/key.txt 2> /dev/null || :
%{__chown} %{CDWuser} %{_sysconfdir}/password 2> /dev/null || :
%{__chmod} 600 %{_sysconfdir}/password 2> /dev/null || :
%{__chown} %{CDWuser} %{_var}/log/CDWserver/CDinfos 2> /dev/null || :
%{__chown} %{CDWuser} %{_var}/log/CDWserver/connects 2> /dev/null || :
%{__chown} %{CDWuser} %{_var}/log/CDWserver/log 2> /dev/null || :
%{__chown} %{CDWuser} %{_var}/log/CDWserver/sessions 2> /dev/null || :

# use R: not test for -x
if [ -x /sbin/chkconfig ]; then
	/sbin/chkconfig --add CDWserver
fi

#move old projects files to new localization (FHS)
if [ -e /home/CDWserver/ ]; then
	echo "move project files to %{_libdir}/CDWserver/projects/..."
	cp /home/CDWserver/* %{_libdir}/CDWserver/projects/ 2> /dev/null || :
	echo "use #rmdir /home/CDWserver/ to clear directory"
fi

%{_sbindir}/CDWconfig.sh %{CDWuser} %{CDWgroup}

#patch and/or e-mail to program author
#if this not set WCDwriter display error
#%{_sbindir}/CDWconfig.sh root %{CDWgroup}
#
# if this not set WCDwriter display error
# chown root.cdwrite %{_bindir}/cdrdao
# chmod 4750 %{_bindir}/cdrdao
# chown root.cdwrite %{_bindir}/cdrecord
# chmod 4750 %{_bindir}/cdrecord
# chown root.cdwrite %{_bindir}/mkisofs
# chmod 4750 %{_bindir}/mkisofs

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/CDWserver stop || :

	if [ -x /sbin/chkconfig ]; then
		/sbin/chkconfig --del CDWserver
	fi

	if [ ! -e %{_var}/spool/CDWserver/bin/ ]; then
		rm -rf %{_var}/spool/CDWserver/*
	fi
fi

%postun
if [ $1 -ge 1 ]; then
	/etc/rc.d/init.d/CDWserver condrestart
fi

if [ "$1" = "0" ]; then
	%userremove %{CDWuser}
	%groupremove %{CDWgroup}
fi

%files
%defattr(644,root,root,755)
%doc CREDITS ChangeLog README *.html
%attr(754,root,root) /etc/rc.d/init.d/CDWserver
%dir %attr(755,%{CDWuser},%{CDWgroup}) %{_sysconfdir}
/etc/pam.d/cdwserver
%{_sysconfdir}/mime.types
%attr(600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/accounts
%config(noreplace) %attr(640, %{CDWuser}, %{CDWgroup}) %verify(not md5 mtime size) %{_sysconfdir}/config
%attr(640,root,%{CDWgroup}) %verify(not md5 mtime size) %{_sysconfdir}/config.default
%config(noreplace) %attr(640, root, %{CDWgroup}) %verify(not md5 mtime size)%{_sysconfdir}/config-root
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/greeting
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/insertCD.html
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/insertCD_de.html
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/insertCD_no.html
#%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/waitForCD
%attr(600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/password
%exclude %{_bindir}/files2cd
%exclude %{_bindir}/image2cd
%exclude %{_bindir}/rcdrecord

%dir %attr(700,%{CDWuser},%{CDWgroup}) %{_var}/log/CDWserver
%dir %attr(700,%{CDWuser},%{CDWgroup}) %{_var}/spool/CDWserver
%dir %{_datadir}/CDWserver
%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrecord-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrdao-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWrootGate
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify-dummy
#%attr(4754, root, %{CDWgroup}) %{_bindir}/setScheduler

%attr(755,root,root) %{_bindir}/dvd+rw-format-dummy
%attr(755,root,root) %{_bindir}/growisofs-dummy
%attr(755,root,root) %{_bindir}/MD5Verify.jar
%attr(755,root,root) %{_bindir}/tar2rpm.sh

%attr(755,root,root) %{_sbindir}/CDWconfig.sh
%attr(755,root,root) %{_sbindir}/CDWpasswd
%attr(755,root,root) %{_sbindir}/CDWserver
%attr(755,root,root) %{_sbindir}/CDWuseradd

%dir %{_var}/lib/CDWserver
%dir %{_var}/lib/CDWserver/export
%{_var}/lib/CDWserver/export/*

%dir %{_datadir}/CDWserver/http
%config(noreplace) %{_datadir}/CDWserver/http/about.html
%config(noreplace) %{_datadir}/CDWserver/http/config.html
%dir %{_datadir}/CDWserver/http/config
%{_datadir}/CDWserver/http/config/*
%{_datadir}/CDWserver/http/default.css
%{_datadir}/CDWserver/http/exampleProject.txt
%config(noreplace) %{_datadir}/CDWserver/http/favicon.ico
%config(noreplace) %{_datadir}/CDWserver/http/footer
%config(noreplace) %{_datadir}/CDWserver/http/head*
%config(noreplace) %{_datadir}/CDWserver/http/help*.html
%config(noreplace) %{_datadir}/CDWserver/http/index*.html
%config(noreplace) %{_datadir}/CDWserver/http/messages*
%dir %{_datadir}/CDWserver/http/rcdrecord
%{_datadir}/CDWserver/http/rcdrecord/*
%config(noreplace) %{_datadir}/CDWserver/http/status*.html
%config(noreplace) %{_datadir}/CDWserver/http/support*.html
%{_datadir}/CDWserver/http/*.png
%dir %{_datadir}/CDWserver/http/webCDcreator
%config(noreplace) %{_datadir}/CDWserver/http/webCDcreator/*.html
%config(noreplace) %{_datadir}/CDWserver/http/webCDcreator/*.jnlp
%dir %{_datadir}/CDWserver/http/webCDcreator/4netscape
%{_datadir}/CDWserver/http/webCDcreator/4netscape/*
%dir %{_datadir}/CDWserver/http/webCDcreator/4plugin
%{_datadir}/CDWserver/http/webCDcreator/4plugin/*
%dir %{_datadir}/CDWserver/http/webCDcreator/4pluginRSA
%{_datadir}/CDWserver/http/webCDcreator/4pluginRSA/*
%dir %{_datadir}/CDWserver/http/webCDcreator/doc
%{_datadir}/CDWserver/http/webCDcreator/doc/*
%dir %{_datadir}/CDWserver/http/webCDcreator/help
%{_datadir}/CDWserver/http/webCDcreator/help/*
%dir %{_datadir}/CDWserver/http/webCDcreator/i18n
%{_datadir}/CDWserver/http/webCDcreator/i18n/*
%dir %{_datadir}/CDWserver/http/webCDcreator/icons
%{_datadir}/CDWserver/http/webCDcreator/icons/*
%dir %{_datadir}/CDWserver/http/webCDcreator/errors
%{_datadir}/CDWserver/http/webCDcreator/errors/*.html
%{_datadir}/CDWserver/http/embeddedProjects.html
%dir %attr(700, %{CDWuser}, %{CDWgroup}) %{_var}/lib/CDWserver/projects

%files rcdrecord
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/image2cd
%attr(755,root,root) %{_bindir}/rcdrecord
