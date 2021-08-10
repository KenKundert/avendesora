#!/usr/bin/env python

# imports {{{1
from setuptools import setup
from codecs import open
import os

# build the description {{{1
with open('README.rst', encoding='utf-8') as file:
    readme = file.read()

# build the installation requirements {{{1
install_requirements = '''
    appdirs
    arrow!=0.14.*
    cryptography
    docopt
    inform>=1.21
    pygobject
    python-gnupg>=0.4.4
        # Be careful.  There's a package called 'gnupg' that's an
        # incompatible fork of 'python-gnupg'.  If both are installed, the
        # user will probably have compatibility issues.
    pyotp
        # pyotp is optional, it provides one-time-password (OTP) secrets.
    #scrypt
        # scrypt is optional. If you install it then Avendesora will offer
        # it. It is not required because it is little used and installing it
        # involves compiling C code and so significant additional
        # dependencies such as gcc.
'''
install_requires = []
for line in install_requirements.splitlines():
    code, _, comment = line.partition('#')
    requirement = code.strip()
    if requirement:
        if requirement.startswith('pygobject') and 'READTHEDOCS' in os.environ:
            pass
        else:
            install_requires.append(requirement)


# call setup {{{1
setup(
    name = 'avendesora',
    version = '1.21.0',
    author = 'Ken Kundert and Kale Kundert',
    author_email = 'avendesora@nurdletech.com',
    description = 'A password generator and account manager.',
    long_description = readme,
    long_description_content_type='text/x-rst',
    url = 'https://avendesora.readthedocs.io',
    download_url = 'https://github.com/kenkundert/avendesora/tarball/master',
    license = 'GPLv3+',
    packages = 'avendesora'.split(),
    entry_points = {
        'console_scripts': ['avendesora = avendesora.main:main'],
    },
    install_requires = install_requires,
    setup_requires = 'pytest-runner>=2.0'.split(),
    tests_require = 'pytest pexpect'.split(),
    python_requires='>=3.6',
    keywords = 'avendesora password XKCD'.split(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ],
)
