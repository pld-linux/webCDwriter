
%define	CDWuser		webcdwriter
%define	CDWgroup	cdwrite

Summary:	Network CD Writing tool
Summary(pl):	Narzêdzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.6.92
Release:	0.1
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://joerghaeger.de/webCDwriter/download/%{version}/%{name}-%{version}.tar.bz2
#Patch:
# Source0-md5:
# Source0Download: http://joerghaeger.de/webCDwriter/TARs.html
URL:		http://JoergHaeger.de/webCDwriter/

BuildRequires:	rpmbuild(macros) >= 1.159
BuildRequires:	pam-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	binutils
BuildRequires:	libstdc++-devel

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
Requires:	cdrtools >= 2.01
Requires:       cdrtools-readcd >= 2.01
Requires:	cdrtools-mkisofs >= 2.01
Requires:	cdrtools-utils >= 2.01
Requires:	mpg123

Provides:	group(%{CDWgroup})
Provides:	user(%{CDWuser})
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
webCdwriter s³u¿y do udostêpniania pojedynczej nagrywarki
dla wszystkich u¿ytkowników sieci. Zawiera serwer CDWserver oraz
klientów: webCDcreator i rcdrecord. CDWserver przechowuje pliki
transmitowane przez klientów, zarz±dza nagrywark± u¿ywaj±c do tego
celu cdrecord. webCDcreator jest apletem Javy uruchamianym z
przegl±darki (Mozilla, Netscape, Internet Explorer,...), pomagaj±cym
transmitowaæ pliki. rcdrecord jest uruchamianym w pow³oce klientem
który spe³nia funkcje cdrecord w sieci (jeszcze nie skoñczony).

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
./configure --pam
%{__make}

#TO DO:
# kompilacja klienta w javie

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install

#umieszczenie pliku rc startuj±cego serwer we w³a¶ciwym katalogu
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
mv $RPM_BUILD_ROOT/etc/init.d/CDWserver $RPM_BUILD_ROOT/etc/rc.d/init.d/CDWserver

%clean
if [ ! -e $RPM_BUILD_ROOT/dev/ ]; then
	rm -rf $RPM_BUILD_ROOT
fi

%pre
# Add the "webCDwriter" user and group
if [ -n "`/usr/bin/getgid %{CDWgroup}`" ]; then
		if [ "`/usr/bin/getgid %{CDWgroup}`" != "27" ]; then
			echo "Error: group %{CDWgroup} doesn't have gid=27. Correct this before installing %{name}." 1>&2
			exit 1
		fi
	else
	/usr/sbin/groupadd -g 27 %{CDWgroup}
fi

if [ -n "`/bin/id -u %{CDWuser} 2>/dev/null`" ]; then
		if [ "`/bin/id -u %{CDWuser}`" != 109 ]; then
			echo "Error: user %{CDWuser} doesn't have uid=109. Correct this before installing %{name}." 1>&2
			exit 1
		fi
	else
		/usr/sbin/useradd -c "systemowy u¿ytkownik dla %{name}" -u 109 -r -d /home/services/CDWserver -s /bin/false -g %{CDWgroup} %{CDWuser} 1>&2
fi

%post

# Since rpm will not change the owner of an existing %config file
%{__chown} %{USER} /etc/CDWserver/accounts 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/config 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/key.txt 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/password 2> /dev/null || :
%{__chmod} 600 /etc/CDWserver/password 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/CDinfos 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/connects 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/log 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/sessions 2> /dev/null || :

if [ -e %{_bindir}/CDWserver-GPL ]; then
	rm -f %{_bindir}/CDWserver-GPL
fi

 if [ -x /sbin/chkconfig ]; then
 	/sbin/chkconfig --add CDWserver
 fi

 if [ -x /sbin/insserv ]; then
 	/sbin/insserv /etc/rc.d/init.d/CDWserver
 fi

# make "setgid root copies" of cdrdao, cdrecord, mkisofs and readcd
for tool in cdrdao cdrecord mkisofs readcd
do
 	if [ ! -e %{_var}/CDWserver/bin/$tool ]; then
 		if [ -e %{_bindir}/$tool ]; then
 			cp -af %{_bindir}/$tool %{_var}/CDWserver/bin/ || :
 		else
 			cp -af /usr/local/bin/$tool %{_var}/CDWserver/bin/ 2> /dev/null || :
 		fi
 	fi
 	if [ -e %{_var}/CDWserver/bin/$tool ]; then
 		%{__chown} root.%{CDWgroup} %{_var}/CDWserver/bin/$tool || :
 		%{__chmod} 4750 %{_var}/CDWserver/bin/$tool || :
 	fi
 done

#move projects files to new localization (FHS)

 if [ -e /home/CDWserver/ ]; then
 	echo "Przenoszê pliki Projektów do %{_var}/CDWserver/projects/..."
 	mv /home/CDWserver/* %{_var}/CDWserver/projects/ 2> /dev/null || :
 	rmdir /home/CDWserver/
 fi

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
if [ $1 = 0 ]; then
	if [ -x /sbin/insserv ]; then
		/sbin/insserv /etc/rc.d/init.d
	fi
fi

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
%dir %attr(0755,%{CDWuser},%{CDWgroup}) /etc/CDWserver
/etc/pam.d/cdwserver
/etc/CDWserver/mime.types
%attr(0600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/accounts
%config(noreplace) %attr(650, %{CDWuser}, %{CDWgroup}) %verify(not md5 mtime size) /etc/CDWserver/config
%attr(650, root, %{CDWgroup})  %verify(not md5 mtime size) /etc/CDWserver/config.default
%config(noreplace) %attr(650, root, %{CDWgroup}) %verify(not md5 mtime size)/etc/CDWserver/config-root
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/greeting
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/waitForCD
%attr(0600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/password
%exclude %{_bindir}/files2cd
%exclude %{_bindir}/image2cd
%exclude %{_bindir}/rcdrecord

%dir %attr(0700,%{CDWuser},%{CDWgroup}) %{_var}/log/CDWserver
%dir %attr(0700,%{CDWuser},%{CDWgroup}) %{_var}/spool/CDWserver
%dir %{_var}/CDWserver

%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrecord-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrdao-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWrootGate
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/setScheduler

%{_bindir}/dvd+rw-format-dummy
%{_bindir}/growisofs-dummy
%{_bindir}/MD5Verify.jar
%{_bindir}/tar2rpm.sh

%{_sbindir}/CDWpasswd
%attr(755,root,root) %{_sbindir}/CDWserver
%{_sbindir}/CDWuseradd

%dir %{_var}/CDWserver/bin/
%dir %{_var}/CDWserver/export/
%{_var}/CDWserver/export/*

%dir %{_var}/CDWserver/http/
%config(noreplace) %{_var}/CDWserver/http/about.html
%config(noreplace) %{_var}/CDWserver/http/config.html
%dir %{_var}/CDWserver/http/config/
%{_var}/CDWserver/http/config/*
%{_var}/CDWserver/http/default.css
%{_var}/CDWserver/http/exampleProject.txt
%config(noreplace) %{_var}/CDWserver/http/favicon.ico
%config(noreplace) %{_var}/CDWserver/http/footer
%config(noreplace) %{_var}/CDWserver/http/head*
%config(noreplace) %{_var}/CDWserver/http/help*.html
%config(noreplace) %{_var}/CDWserver/http/index*.html
%config(noreplace) %{_var}/CDWserver/http/messages*
%dir %{_var}/CDWserver/http/rcdrecord/
%{_var}/CDWserver/http/rcdrecord/*
%config(noreplace) %{_var}/CDWserver/http/status*.html
%config(noreplace) %{_var}/CDWserver/http/support*.html
%{_var}/CDWserver/http/*.png
%dir %{_var}/CDWserver/http/webCDcreator/
%config(noreplace) %{_var}/CDWserver/http/webCDcreator/*.html
%config(noreplace) %{_var}/CDWserver/http/webCDcreator/*.jnlp
%dir %{_var}/CDWserver/http/webCDcreator/4netscape/
%{_var}/CDWserver/http/webCDcreator/4netscape/*
%dir %{_var}/CDWserver/http/webCDcreator/4plugin/
%{_var}/CDWserver/http/webCDcreator/4plugin/*
%dir %{_var}/CDWserver/http/webCDcreator/4pluginRSA/
%{_var}/CDWserver/http/webCDcreator/4pluginRSA/*
%dir %{_var}/CDWserver/http/webCDcreator/doc/
%{_var}/CDWserver/http/webCDcreator/doc/*
%dir %{_var}/CDWserver/http/webCDcreator/help/
%{_var}/CDWserver/http/webCDcreator/help/*
%dir %{_var}/CDWserver/http/webCDcreator/i18n/
%{_var}/CDWserver/http/webCDcreator/i18n/*
%dir %{_var}/CDWserver/http/webCDcreator/icons/
%{_var}/CDWserver/http/webCDcreator/icons/*
%dir %{_var}/CDWserver/http/webCDcreator/errors/
%{_var}/CDWserver/http/webCDcreator/errors/*.html
%dir %attr(700, %{CDWuser}, %{CDWgroup}) %{_var}/CDWserver/projects/

%files rcdrecord
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/image2cd
%attr(755,root,root) %{_bindir}/rcdrecord
