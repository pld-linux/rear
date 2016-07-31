Summary:	Relax-and-Recover is a Linux disaster recovery and system migration tool
Name:		rear
Version:	1.18
Release:	0.1
License:	GPL v3
Group:		Applications/File
# as GitHub stopped with download section we need to go back to Sourceforge for downloads
Source0:	https://sourceforge.net/projects/rear/files/rear/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	ce12c1c036207e71750d64d89c072b55
Source1:	rear.cron
URL:		http://relax-and-recover.org/
# rear contains only bash scripts plus documentation so that on first glance it could be "BuildArch: noarch"
# but actually it is not "noarch" because it only works on those architectures that are explicitly supported.
# Of course the rear bash scripts can be installed on any architecture just as any binaries can be installed on any architecture.
# But the meaning of architecture dependent packages should be on what architectures they will work.
# Therefore only those architectures that are actually supported are explicitly listed.
# This avoids that rear can be "just installed" on architectures that are actually not supported (e.g. ARM or IBM z Systems):
ExclusiveArch:	%{ix86} %{x8664} x32 ppc ppc64 ppc64le
# Furthermore for some architectures it requires architecture dependent packages (like syslinux for x86 and x86_64)
# so that rear must be architecture dependent because ifarch conditions never match in case of "BuildArch: noarch"
# see the GitHub issue https://github.com/rear/rear/issues/629
%ifarch %{ix86} %{x8664}
Requires:	syslinux
%endif
# In the end this should tell the user that rear is known to work only on ix86 x86_64 ppc ppc64 ppc64le
# and on ix86 x86_64 syslinux is explicitly required to make the bootable ISO image
# (in addition to the default installed bootloader grub2) while on ppc ppc64 the
# default installed bootloader yaboot is also useed to make the bootable ISO image.
### Dependencies on all distributions
Requires:	attr
Requires:	binutils
Requires:	ethtool
Requires:	gawk
Requires:	gzip
Requires:	iputils
Requires:	openssl
Requires:	parted
Requires:	tar
### If you require NFS, you may need the below packages
#Requires:	nfsclient portmap rpcbind
### We drop LSB requirements because it pulls in too many dependencies
### The OS is hardcoded in /etc/rear/os.conf instead
#Requires: redhat-lsb
### Required for Bacula/MySQL support
#Requires: bacula-mysql
### Required for OBDR
#Requires:	lsscsi sg3_utils
### Optional requirement
#Requires: cfg2html
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Relax-and-Recover is the leading Open Source disaster recovery and
system migration solution. It comprises of a modular frame-work and
ready-to-go workflows for many common situations to produce a bootable
image and restore from backup using this image. As a benefit, it
allows to restore to different hardware and can therefore be used as a
migration tool as well.

Currently Relax-and-Recover supports various boot media (incl. ISO,
PXE, OBDR tape, USB or eSATA storage), a variety of network protocols
(incl. sftp, ftp, http, nfs, cifs) as well as a multitude of backup
strategies (incl. IBM TSM, HP DataProtector, Symantec NetBackup, EMC
NetWorker, Bacula, Bareos, rsync).

Relax-and-Recover was designed to be easy to set up, requires no
maintenance and is there to assist when disaster strikes. Its
setup-and-forget nature removes any excuse for not having a disaster
recovery solution implemented.

Professional services and support are available.

%prep
%setup -q

### Add a specific os.conf so we do not depend on LSB dependencies
cat <<EOF> etc/rear/os.conf
OS_VENDOR=PLD
OS_VERSION=%{pld_release}
EOF

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT"

install -d $RPM_BUILD_ROOT/etc/cron.d/rear
cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/rear

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -gt 1 ] ; then
	# during upgrade remove obsolete directories
	%{__rm} -rf %{_datadir}/rear/output/NETFS
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING README.adoc doc/*.txt
%config(noreplace) %verify(not md5 mtime size) /etc/cron.d/rear
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/local.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/os.conf
%attr(755,root,root) %{_sbindir}/rear
%{_mandir}/man8/rear.8*
%{_datadir}/%{name}
%{_localstatedir}/lib/%{name}
