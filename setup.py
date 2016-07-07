#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='avendesora',
    version='0.1.0',
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
        'console_scripts': ['avendesora=avendesora.cli:main'],
    },
    install_requires=[
        'appdirs',
        'docopt',
        'inform',
        'shlib',
        'python-gnupg',
            # Be careful.  There's a package called 'gnupg' that's an 
            # incompatible fork of 'python-gnupg'.  If both are installed, the 
            # user will probably have compatibility issues.
    ],
    keywords=[
        'avendesora',
        'password',
        'XKCD',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ],
)
