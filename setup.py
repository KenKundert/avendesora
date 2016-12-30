#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='avendesora',
    version='0.20.1',
    author='Ken Kundert and Kale Kundert',
    author_email='avendesora@nurdletech.com',
    description='An XKCD-style password generator.',
    long_description=readme,
    url='http://nurdletech.com/linux-utilities/avendesora',
    download_url='https://github.com/kenkundert/avendesora/tarball/master',
    license='GPLv3+',
    packages=[
        'avendesora',
    ],
    package_data={'avendesora': ['words']},
    entry_points={
        'console_scripts': ['avendesora=avendesora.main:main'],
    },
    install_requires=[
        'appdirs',
        'docopt',
        'inform>=1.6',
        #'pygobject',
            # pygobject seems broken in pypi. Instead, do the following:
            # git clone git://git.gnome.org/pygobject
            # pip3.5 install ./pygobject
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
        'python-gnupg',
            # Be careful.  There's a package called 'gnupg' that's an 
            # incompatible fork of 'python-gnupg'.  If both are installed, the 
            # user will probably have compatibility issues.
        #'scrypt',
            # scrypt is optional. If you install it then Avendesora will offer
            # it. It is not required because it involves compiling C code and so
            # significant additional dependencies such as gcc.
        'shlib>=0.4',
    ],
    tests_require=['pytest'],
    keywords=[
        'avendesora',
        'password',
        'XKCD',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ],
)
