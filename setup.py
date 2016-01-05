#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
with open('avendesora/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

setup(
    name='avendesora',
    version=version,
    author='Ken Kundert and Kale Kundert',
    author_email='avendesora@nurdletech.com',
    description='An XKCD-style password generator.',
    long_description=readme,
    url='https://github.com/kenkundert/avendesora',
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    keywords=[
        'avendesora',
        'password',
        'XKCD',
    ],
    packages=[
        'avendesora',
    ],
    install_requires=[
        'docopt',
        'gnupg',
    ],
    entry_points = {
        'console_scripts': ['avendesora=avendesora.cli:main'],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ],
)
