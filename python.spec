# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.26
# 

Name:       python

# >> macros
%global _default_patch_fuzz 2
%global pybasever 2.7
%global pylibdir %{_libdir}/python%{pybasever}
%global dynload_dir %{pylibdir}/lib-dynload
# << macros

Summary:    An interpreted, interactive, object-oriented programming language
Version:    2.7.5
Release:    1
Group:      Development/Languages
License:    Python
URL:        http://www.python.org/
Source0:    http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
Source100:  python.yaml
Patch0:     cgi-py-shebang.patch
Patch1:     Python-2.2.1-pydocnogui.patch
Patch2:     notimestamp.patch
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(ncursesw)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  bzip2
BuildRequires:  bzip2-devel
BuildRequires:  db4-devel >= 4.8
BuildRequires:  gcc
BuildRequires:  gdbm-devel
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  readline-devel
BuildRequires:  tar
Provides:   python-abi = %{pybasever}

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules.

This package provides the "python" executable; most of the actual
implementation is within the "python-libs" package.


%package libs
Summary:    Runtime libraries for Python
Group:      Applications/System
Requires:   %{name} = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description libs
This package contains runtime libraries for use by Python:
- the libpython dynamic library, for use by applications that embed Python as
a scripting language, and by the main "python" executable
- the Python standard library


%package test
Summary:    The test modules from the main python package
Group:      Development/Languages
Requires:   %{name} = %{version}-%{release}

%description test
The test modules from the main python package: %{name}
These have been removed to save space, as they are never or almost
never used in production.

You might want to install the python-test package if you're developing python
code that uses more than just unittest and/or test_support.py.


%package tools
Summary:    A collection of development tools included with Python
Group:      Development/Tools
Requires:   %{name} = %{version}-%{release}
Provides:   python2-tools = %{version}
Obsoletes:  python2-tools < %{version}

%description tools
This package includes several tools to help with the development of Python
programs, including IDLE (an IDE with editing and debugging facilities), a
color editor (pynche), and a python gettext program (pygettext.py).


%package devel
Summary:    The libraries and header files needed for Python development
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Provides:   python2-devel = %{version}-%{release}
Obsoletes:  python2-devel < %{version}-%{release}

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.


%prep
%setup -q -n Python-%{version}

# cgi-py-shebang.patch
%patch0 -p1
# Python-2.2.1-pydocnogui.patch
%patch1 -p1
# notimestamp.patch
%patch2 -p1
# >> setup
# << setup

%build
# >> build pre
export CC=gcc
# << build pre

%configure --disable-static \
    --enable-ipv6 \
    --enable-unicode=ucs4 \
    --enable-shared \
    --with-system-ffi

make %{?jobs:-j%jobs}

# >> build post
#have to test pre-installed here (or can we move yaml's check up here)?

echo STARTING: CHECKING OF PYTHON
echo NOTE: the test suite is run two times
echo arch is "%{_arch}"
echo buildarch is "%{_build_arch}"

#skip failing tests (FAIL or crash (seg fault, etc)).
#otherwise rpmbuild will bomb (make test exits w/ non-zero status).
#
#always excluded are due to no tkinter module:
#test_tcl skipped -- No module named _tkinter
#they would show up as skips unexpected on linux2 otherwise
ALWAYS_EXCLUDED_TESTS=" \
test_tcl \
test_tk \
test_ttk_guionly \
test_ttk_textonly \
%{nil}"

#scratchbox2 builds (arm or mipsel) cause several unexpected failures
#see, e.g., mer#309 (gdb)
#test_ftplib, test_posix fail on at least sb2/armv7 (but ok on osc)
SB2_EXCLUDED=" \
test_capi \
test_epoll \
test_ftplib \
test_gdb \
test_hashlib \
test_httpservers \
test_mmap \
test_multiprocessing \
test_posix \
test_threading \
%{nil}"

%ifarch %{arm}

echo "testing: ifarch is arm"
#2.7.3 is much worse (seg faults, crashes) in tests under qemu than 2.7.2 was
#and definite armv7el / armv8el differences


ARCH_EXCLUDED="\
$SB2_EXCLUDED \
test_bz2 \
test_cmath \
test_file \
test_file2k \
test_float \
test_io \
test_locale \
test_math \
test_openpty \
test_pty \
test_strtod \
test_sys \
test_uuid \
%{nil}"

%endif

%ifarch %{mipsel}

echo "testing: ifarch is mipsel"
ARCH_EXCLUDED="\
$SB2_EXCLUDED \
%{nil}"

%endif

%ifarch %{ix86}

ARCH_EXCLUDED="\
test_file \
test_file2k \
test_locale \
%{nil}"

%endif

%ifarch x86_64

ARCH_EXCLUDED="\
test_file \
test_file2k \
test_io \
test_os \
test_posix \
%{nil}"

%endif

EXCLUDED_TESTS=" \
$ALWAYS_EXCLUDED_TESTS \
$ARCH_EXCLUDED \
%{nil}"

# Note that we're running the tests using the version of the code in the
# builddir, not in the buildroot.

#sb2/qemu is just too unstable...
%if ! 0%{?qemu_user_space_build}

echo "the EXCLUDED tests were: $EXCLUDED_TESTS"

EXTRATESTOPTS="--verbose3"

# Actually invoke regrtest.py:
EXTRATESTOPTS="$EXTRATESTOPTS -x $EXCLUDED_TESTS" make test

echo FINISHED: CHECKING OF PYTHON
echo add any failing tests to arch-specific EXCLUDED_TESTS
echo to allow package build to succeed

%endif


# << build post

%install
rm -rf %{buildroot}
# >> install pre
# << install pre
%make_install

# >> install post


#the test(s) sub-pkg logic/info comes from fedora fc15 spec file
# Junk, no point in putting in -test sub-pkg
rm -f %{buildroot}/%{pylibdir}/idlelib/testcode.py*

# Get rid of egg-info files (core python modules are installed through rpms)
rm -f %{buildroot}%{pylibdir}/*.egg-info

#set some links
ln -s ../../libpython%{pybasever}.so %{buildroot}%{pylibdir}/config/libpython%{pybasever}.so

# python's build is stupid and doesn't fail if extensions fail to build
# let's list a few that we care about...
# ?
for so in _bsddb.so _ctypes.so _curses.so _elementtree.so _sqlite3.so _ssl.so readline.so _hashlib.so zlib.so bz2.so pyexpat.so; do
if [ ! -f %{buildroot}/%{dynload_dir}/$so ]; then
echo %{buildroot}/%{dynload_dir}
/bin/ls -l %{buildroot}/%{dynload_dir}
echo "Missing $so!!!"
exit 1
fi
done

#meego does not support tk (regardless of what pkg description says)?
rm -rf %{buildroot}%{pylibdir}/lib-tk

#we already have a LICENSE file elsewhere
rm -f %{buildroot}%{pylibdir}/LICENSE.txt

# << install post

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%doc LICENSE README
%{_bindir}/pydoc
%{_bindir}/python
%{_bindir}/python2
%{_bindir}/python%{pybasever}
%{_mandir}/*/*
# >> files
# << files

%files libs
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%dir %{pylibdir}
%dir %{dynload_dir}
%{dynload_dir}/Python-%{version}-py%{pybasever}.egg-info
#warning, hardwired SOVERSION 1.0
%{_libdir}/libpython%{pybasever}.so.1.0
#this list is from the stdout of rpmbuild -bl ('provides...' section).
#note the 'module' disappeared from some names 2.7.1 to 2.7.2(?).
%{dynload_dir}/_bisect.so
%{dynload_dir}/_bsddb.so
%{dynload_dir}/_codecs_cn.so
%{dynload_dir}/_codecs_hk.so
%{dynload_dir}/_codecs_iso2022.so
%{dynload_dir}/_codecs_jp.so
%{dynload_dir}/_codecs_kr.so
%{dynload_dir}/_codecs_tw.so
%{dynload_dir}/_collections.so
%{dynload_dir}/_csv.so
%{dynload_dir}/_ctypes.so
%{dynload_dir}/_curses.so
%{dynload_dir}/_curses_panel.so
%{dynload_dir}/_elementtree.so
%{dynload_dir}/_functools.so
%{dynload_dir}/_hashlib.so
%{dynload_dir}/_heapq.so
%{dynload_dir}/_hotshot.so
%{dynload_dir}/_io.so
%{dynload_dir}/_json.so
%{dynload_dir}/_locale.so
%{dynload_dir}/_lsprof.so
%{dynload_dir}/_multibytecodec.so
%{dynload_dir}/_multiprocessing.so
%{dynload_dir}/_random.so
%{dynload_dir}/_socket.so
%{dynload_dir}/_sqlite3.so
%{dynload_dir}/_ssl.so
%{dynload_dir}/_struct.so
%{dynload_dir}/array.so
%{dynload_dir}/audioop.so
%{dynload_dir}/binascii.so
%{dynload_dir}/bz2.so
%{dynload_dir}/cPickle.so
%{dynload_dir}/cStringIO.so
%{dynload_dir}/cmath.so
%{dynload_dir}/crypt.so
%{dynload_dir}/datetime.so
%{dynload_dir}/dbm.so
%{dynload_dir}/dl.so
%{dynload_dir}/fcntl.so
%{dynload_dir}/future_builtins.so
%{dynload_dir}/gdbm.so
%{dynload_dir}/grp.so
%{dynload_dir}/imageop.so
%{dynload_dir}/itertools.so
%{dynload_dir}/linuxaudiodev.so
%{dynload_dir}/math.so
%{dynload_dir}/mmap.so
%{dynload_dir}/nis.so
%{dynload_dir}/operator.so
%{dynload_dir}/ossaudiodev.so
%{dynload_dir}/parser.so
%{dynload_dir}/pyexpat.so
%{dynload_dir}/readline.so
%{dynload_dir}/resource.so
%{dynload_dir}/select.so
%{dynload_dir}/spwd.so
%{dynload_dir}/strop.so
%{dynload_dir}/syslog.so
%{dynload_dir}/termios.so
%{dynload_dir}/time.so
%{dynload_dir}/unicodedata.so
%{dynload_dir}/zlib.so
%dir %{pylibdir}/site-packages
%{pylibdir}/site-packages/README
%{pylibdir}/*.py*
%dir %{pylibdir}/bsddb
%{pylibdir}/bsddb/*.py*
%{pylibdir}/pdb.doc
%{pylibdir}/compiler
%dir %{pylibdir}/ctypes
%{pylibdir}/ctypes/*.py*
%{pylibdir}/ctypes/macholib
%{pylibdir}/curses
%dir %{pylibdir}/distutils
%{pylibdir}/distutils/*.py*
%{pylibdir}/distutils/README
%{pylibdir}/distutils/command
%exclude %{pylibdir}/distutils/command/wininst-*.exe
%dir %{pylibdir}/email
%{pylibdir}/email/*.py*
%{pylibdir}/email/mime
%{pylibdir}/encodings
%{pylibdir}/hotshot
%{pylibdir}/idlelib
%exclude %{pylibdir}/idlelib/idle.bat
%{pylibdir}/importlib
%dir %{pylibdir}/json
%{pylibdir}/json/*.py*
%{pylibdir}/lib2to3
%{pylibdir}/logging
%{pylibdir}/multiprocessing
%{pylibdir}/plat-linux2
%{pylibdir}/pydoc_data
%dir %{pylibdir}/sqlite3
%{pylibdir}/sqlite3/*.py*
#see -tests pkg for others
%dir %{pylibdir}/test
%{pylibdir}/test/test_support.py*
%{pylibdir}/test/__init__.py*
%{pylibdir}/unittest
%{pylibdir}/wsgiref
%{pylibdir}/xml
%dir %{pylibdir}/config
%{pylibdir}/config/Makefile
%dir %{_includedir}/python%{pybasever}
#note: this config.h might only support 32 bit arch?
%{_includedir}/python%{pybasever}/pyconfig.h
# >> files libs
# << files libs

%files test
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%{pylibdir}/bsddb/test
%{pylibdir}/ctypes/test
%{pylibdir}/distutils/tests
%{pylibdir}/email/test
%{pylibdir}/json/tests
%{pylibdir}/sqlite3/test
%{pylibdir}/test/*
# These two are shipped in the main package:
%exclude %{pylibdir}/test/test_support.py*
%exclude %{pylibdir}/test/__init__.py*
%{dynload_dir}/_ctypes_test.so
%{dynload_dir}/_testcapi.so
# >> files test
# << files test

%files tools
%defattr(-,root,root,-)
%defattr(-, root, root, 755)
%{_bindir}/2to3
#no tkinter -> no idle?
%exclude %{_bindir}/idle
%{_bindir}/smtpd.py
# >> files tools
# << files tools

%files devel
%defattr(-,root,root,-)
%{_libdir}/pkgconfig/python-%{pybasever}.pc
%{_libdir}/pkgconfig/python2.pc
%{_libdir}/pkgconfig/python.pc
%{pylibdir}/config/*
#Makefile is included in the main pkg
%exclude %{pylibdir}/config/Makefile
%{pylibdir}/distutils/command/wininst-*.exe
%{_includedir}/python%{pybasever}/*.h
#pyconfig.h is included in the main pkg
%exclude %{_includedir}/python%{pybasever}/pyconfig.h
%{_bindir}/python%{pybasever}-config
%{_bindir}/python2-config
%{_bindir}/python-config
%{_libdir}/libpython%{pybasever}.so
# >> files devel
# << files devel
