#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name = 'avendesora',
    version = '1.16.0',
    author = 'Ken Kundert and Kale Kundert',
    author_email = 'avendesora@nurdletech.com',
    description = 'A password generator and account manager.',
    long_description = readme,
    url = 'https://avendesora.readthedocs.io',
    download_url = 'https://github.com/kenkundert/avendesora/tarball/master',
    license = 'GPLv3+',
    packages = 'avendesora'.split(),
    entry_points = {
        'console_scripts': ['avendesora = avendesora.main:main'],
    },
    install_requires = [
        'appdirs',
        'arrow!=0.14.*',
        'cryptography',
        'docopt',
        'inform>=1.17',
        #'pygobject',
            # pygobject seems broken in pypi. You can try uncommenting the above
            # and see if it works. Otherwise, do the following:
            #   > git clone git://git.gnome.org/pygobject
            #   > pip3.5 install ./pygobject
            # This install will fail if you do not have the right packages
            # installed in linux. For example, gnome-common is one that you will
            # need. Read the error messages carefully to determine
            # what other packages are needed. Then, be sure to install the
            # development versions. For example, on Fedora23 the libffi,
            # gobject-introspection and pycairo packages were needed. I
            # installed them with:
            #     dnf install libffi-devel
            #     dnf install gobject-introspection-devel
            #     dnf install python3-cairo-devel
        'python-gnupg>=0.4.4',
            # Be careful.  There's a package called 'gnupg' that's an
            # incompatible fork of 'python-gnupg'.  If both are installed, the
            # user will probably have compatibility issues.
        'pyotp',
            # pyotp is optional, it provides one-time-password (OTP) secrets.
        #'scrypt',
            # scrypt is optional. If you install it then Avendesora will offer
            # it. It is not required because it is little used and installing it
            # involves compiling C code and so significant additional
            # dependencies such as gcc.
    ],
    setup_requires = 'pytest-runner>=2.0'.split(),
    tests_require = 'pytest pexpect'.split(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
    keywords = 'avendesora password XKCD'.split(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ],
)
