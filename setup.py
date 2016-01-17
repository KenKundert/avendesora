#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='avendesora',
    version='0.0.4',
    author='Ken Kundert and Kale Kundert',
    author_email='avendesora@nurdletech.com',
    description='An XKCD-style password generator.',
    long_description=readme,
    url='https://github.com/kenkundert/avendesora',
    license='GPLv3+',
    zip_safe=False,
    packages=[
        'avendesora',
    ],
    entry_points = {
        'console_scripts': ['avendesora=avendesora.cli:main'],
    },
    data_files=[('avendesora', ['avendesora/words'])],
    install_requires=[
        'docopt',
        'inform',
        'python-gnupg',
            # Be careful.  There's a package called 'gnupg' that's an 
            # incompatible fork of 'python-gnupg'.  If both are installed, the 
            # user will probably have compatibility issues.
        'six',
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
