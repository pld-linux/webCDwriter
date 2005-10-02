#TODO:
# add certificate and compiling java client
# XXX: FHS violation
#	/var/CDWserver/{http,bin,exports} --> /usr/share/CDWserver/{http,bin,exports}
#	/var/CDWserver/export/Server/doc --> /usr/share/doc/CDWserver
#	/var/CDWserver --> /var/lib/CDWserver

%define	CDWuser		webcdwriter
%define	CDWgroup	cdwrite

Summary:	Network CD Writing tool
Summary(pl):	Narzêdzie do sieciowego nagrywania CD
Name:		webCDwriter
Version:	2.7.2
Release:	0.3
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://joerghaeger.de/webCDwriter/download/%{name}-%{version}.tar.bz2
# Source0-md5:	88e97d83b172c646603323426d429065
#Source0:	http://haeger.homeip.net/download/%{version}/%{name}-%{version}.tar.bz2
Patch0:		%{name}-FHS.patch
# Source0Download: http://joerghaeger.de/webCDwriter/TARs.html
URL:		http://JoergHaeger.de/webCDwriter/

BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	pam-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	binutils
BuildRequires:	libstdc++-devel
BuildRequires:	jdkgcj

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
Remote client for webCDwriter.

%description rcdrecord -l pl
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
%{__make} install 

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_datadir}/CDWserver}
mv $RPM_BUILD_ROOT/etc/init.d/CDWserver $RPM_BUILD_ROOT/etc/rc.d/init.d/CDWserver
rm $RPM_BUILD_ROOT/%{_bindir}/CDWuninstall.sh

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

%{__chown} %{USER} /etc/CDWserver/accounts 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/config 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/key.txt 2> /dev/null || :
%{__chown} %{USER} /etc/CDWserver/password 2> /dev/null || :
%{__chmod} 600 /etc/CDWserver/password 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/CDinfos 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/connects 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/log 2> /dev/null || :
%{__chown} %{USER} %{_var}/log/CDWserver/sessions 2> /dev/null || :

# use R: not test for -x
if [ -x /sbin/chkconfig ]; then
	/sbin/chkconfig --add CDWserver
fi

# XX: packaging policy violations
#make "setgid root copies" of cdrdao, cdrecord, mkisofs and readcd

#for tool in cdrdao cdrecord mkisofs readcd
#do
# 	if [ ! -e %{_bindir}/CDWserver/bin/$tool ]; then
# 		if [ -e %{_bindir}/$tool ]; then
# 			cp -af %{_bindir}/$tool %{_bindir}/CDWserver/bin/ || :
# 		else
# 			cp -af /usr/local/bin/$tool %{_bindir}/CDWserver/bin/ 2> /dev/null || :
# 		fi
# 	fi
# 	if [ -e %{_bindir}/CDWserver/bin/$tool ]; then
# 		%{__chown} root:%{CDWgroup} %{_bindir}/CDWserver/bin/$tool || :
# 		%{__chmod} 4750 %{_bindir}/CDWserver/bin/$tool || :
# 	fi
# done

#move old projects files to new localization (FHS)
if [ -e /home/CDWserver/ ]; then
	echo "move project files to %{_libdir}/CDWserver/projects/..."
	cp /home/CDWserver/* %{_libdir}/CDWserver/projects/ 2> /dev/null || :
	echo "use #rmdir /home/CDWserver/ to clear directory"
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
%attr(600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/accounts
%config(noreplace) %attr(650, %{CDWuser}, %{CDWgroup}) %verify(not md5 mtime size) /etc/CDWserver/config
%attr(650,root,%{CDWgroup}) %verify(not md5 mtime size) /etc/CDWserver/config.default
%config(noreplace) %attr(650, root, %{CDWgroup}) %verify(not md5 mtime size)/etc/CDWserver/config-root
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/greeting
%config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/waitForCD
%attr(600,%{CDWuser},%{CDWgroup}) %config(noreplace) %verify(not md5 mtime size) /etc/CDWserver/password
%exclude %{_bindir}/files2cd
%exclude %{_bindir}/image2cd
%exclude %{_bindir}/rcdrecord

%dir %attr(0700,%{CDWuser},%{CDWgroup}) %{_var}/log/CDWserver
%dir %attr(0700,%{CDWuser},%{CDWgroup}) %{_var}/spool/CDWserver
%dir %{_datadir}/CDWserver 
%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrecord-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/cdrdao-dummy
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWrootGate
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify
%attr(4754, root, %{CDWgroup}) %{_bindir}/CDWverify-dummy
#%attr(4754, root, %{CDWgroup}) %{_bindir}/setScheduler

%{_bindir}/dvd+rw-format-dummy
%{_bindir}/growisofs-dummy
%{_bindir}/MD5Verify.jar
%{_bindir}/tar2rpm.sh

%attr(755,root,root) %{_sbindir}/CDWconfig.sh
%attr(755,root,root) %{_sbindir}/CDWpasswd
%attr(755,root,root) %{_sbindir}/CDWserver
%attr(755,root,root) %{_sbindir}/CDWuseradd

%dir %{_bindir}/CDWserver/bin
%dir %{_datadir}/CDWserver/export
%{_datadir}/CDWserver/export/*

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
%dir %attr(700, %{CDWuser}, %{CDWgroup}) %{_var}/lib/CDWserver/projects

%files rcdrecord
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/files2cd
%attr(755,root,root) %{_bindir}/image2cd
%attr(755,root,root) %{_bindir}/rcdrecord
