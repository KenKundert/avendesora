#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='avendesora',
    version='0.0.2',
    author='Ken Kundert and Kale Kundert',
    author_email='avendesora@nurdletech.com',
    description='An XKCD-style password generator.',
    long_description=readme,
    url='https://github.com/kenkundert/avendesora',
    include_package_data=True,
    license='GPLv3+',
    zip_safe=False,
    keywords=[
        'avendesora',
        'password',
        'XKCD',
    ],
    packages=[
        'avendesora',
    ],
    data_files=[('avendesora', ['avendesora/words'])],
    install_requires=[
        'docopt',
        'python-gnupg',
        'messenger',
        'shlib',
    ],
    entry_points = {
        'console_scripts': ['avendesora=avendesora.cli:main'],
    },
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
