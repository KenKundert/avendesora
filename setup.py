from setuptools import setup

setup(
    name='avendesora',
    description="password generator",
    author="Ken Kundert",
    author_email='avendesora@nurdletech.com',
    packages=['avendesora'],
    entry_points = {
        'console_scripts': ['avendesora=avendesora.cli:main'],
    },
    data_files=[('', ['avendesora/words'])]
)
