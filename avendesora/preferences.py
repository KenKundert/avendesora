# Avendesora Password Generator Preferences
#
# Copyright (C) 2016 Kenneth S. Kundert

# License {{{1
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from textwrap import dedent
import re
from appdirs import user_config_dir

# Config Settings {{{1
# These are the default values for settings that may be found in the config file
CONFIG_DEFAULTS = {
    'log_file': 'log.gpg',
    'archive_file': 'archive.gpg',
    'user_key_file': 'key.gpg',
    'dictionary_file': 'words',
    'accounts_files': None,
    'default_field': 'passcode',
    'default_vector_field': 'questions',
    'display_time': 60,
    # use absolute paths for executables so they cannot be maliciously replaced
    'xdotool_executable': '/usr/bin/xdotool',
    'xsel_executable': '/usr/bin/xsel',
    'gpg_executable': '/usr/bin/gpg2',
    'gpg_home': '~/.gnupg',
    'gpg_armor': True,
    'gpg_id': None,
    'browsers': {
        'f': 'firefox -new-tab %s',
        'g': 'google-chrome %s',
        't': 'torbrowser %s',
        'x': 'xdg-open %s', # system default browser
    },
    'default_browser': 'x',
    'required_protocols': ['https'],
}

# the following could be config settings, but they do not seem worth promoting
INDENT = '    '
LABEL_COLOR = 'yellow'
    # choose from normal, black, red, green, yellow, blue, magenta, cyan, white
INITIAL_AUTOTYPE_DELAY = 0.0

# Non-Config Settings {{{1
# These value can be accessed with get_settings,
# but should not be found in the config file
NONCONFIG_SETTINGS = {
    'config_file': 'config',
    'hashes_file': 'hashes',
    'settings_dir': user_config_dir('avendesora'),
    'default_accounts_file': 'accounts.gpg',
    'default_templates_file': 'templates',
    'dict_hash': '11fe5bc734f4a956c37d7cb3da16ab3f',
    'secrets_hash': 'f7aeadac3cefe513047fdb4efa26591f',
    'charsets_hash': '405332bcb8330b7502d292991026e328',
}


# Initial config file {{{1
CONFIG_FILE_INITIAL_CONTENTS = dedent('''\
    # List of the files that contain account information
    accounts_files = [
        {default_accounts_file},
        {default_templates_file}
    ]

    # The desired location of the log file (relative to config directory).
    # Adding a suffix of .gpg or .asc causes the file to be encrypted
    # (otherwise it can leak account names). Use None to disable logging.
    log_file = {log_file}

    # The desired location of the archive file (relative to config director).
    # End the path in .gpg. Use None to disable archiving.
    archive_file = {archive_file}

    # Various settings
    default_field = {default_field}
    default_vector_field = {default_vector_field}
    display_time = {display_time}
    browsers = {browsers}
    default_browser = {default_browser}
    required_protocols = {required_protocols}

    # Information used by GPG when encrypting and decrypting files.
    gpg_id = {gpg_id}
    gpg_armor = {gpg_armor}
    gpg_home = {gpg_home}
    gpg_executable = {gpg_executable}

    # Utilities
    xdotool_executable = {xdotool_executable}
    xsel_executable = {xsel_executable}

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
''')


# Initial hash file {{{1
HASH_FILE_INITIAL_CONTENTS = dedent('''\
    # Changing the contents of the dictionary, secrets, or charsets will change
    # the secrets you generate, thus you do not want to change these files once
    # you have started using the program. These are hashes for the contents of
    # these files at the time that this file was created. The program will
    # complain if the current contents of these files generate a different
    # hash. Only update these hashes if you know what you are doing.

    charsets_hash = {charsets_hash}  # DO NOT CHANGE THIS LINE
    dict_hash     = {dict_hash}  # DO NOT CHANGE THIS LINE
    secrets_hash  = {secrets_hash}  # DO NOT CHANGE THIS LINE
''')


# Initial accounts file {{{1
ACCOUNTS_FILE_INITIAL_CONTENTS = dedent('''\
    # Account information
    #
    # Add information about each of your accounts to the accounts dictionary.
    #
    # You can use the dedent function to strip leading whitespace from
    # multi-line remarks.  You can use the character sets and exclude function
    # to create alphabets for you character-base passwords.
    #
    # Example:
    # To create an alphabet with all characters except tabs use either:
    #     'alphabet': exclude(PRINTABLE, '\\t')
    # or:
    #     'alphabet': ALPHANUMERIC + PUNCTUATION + ' '

    from avendesora import (
        # Basics
        Account, Hidden,

        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Secrets
        Password, Passphrase, PIN, Question, MixedPassword, BirthDate,

        # Account Discovery
        RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
        RecognizeHost, RecognizeUser, RecognizeEnvVar,
    )

    master_password = Hidden({master_password})

    # Accounts
    # AAA {section}
    # BBB {section}
    # CCC {section}
    # DDD {section}
    # EEE {section}
    # FFF {section}
    # GGG {section}
    # HHH {section}
    # III {section}
    # JJJ {section}
    # KKK {section}
    # LLL {section}
    # MMM {section}
    # NNN {section}
    # OOO {section}
    # PPP {section}
    # QQQ {section}
    # RRR {section}
    # SSS {section}
    # TTT {section}
    # UUU {section}
    # VVV {section}
    # WWW {section}
    # XXX {section}
    # YYY {section}
    # ZZZ {section}

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
''')

# Initial templates file {{{1
TEMPLATES_FILE_INITIAL_CONTENTS = dedent('''\
    # Templates
    #
    # Templates are accounts without master passwords and without much in the way of
    # attributes. Use them to generate pass codes of various types for stealth
    # accounts.

    from avendesora import (
        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Account
        Account,

        # Secrets
        Password, Passphrase, PIN,
    )

    # Templates
    # AAA {section}
    class Anum4(Account):
        passcode = Password(length=4, alphabet=DISTINGUISHABLE)

    class Anum6(Account):
        passcode = Password(length=6, alphabet=DISTINGUISHABLE)

    class Anum8(Account):
        passcode = Password(length=8, alphabet=DISTINGUISHABLE)

    class Anum10(Account):
        passcode = Password(length=10, alphabet=DISTINGUISHABLE)

    class Anum12(Account):
        aliases = ['anum']
        passcode = Password(length=12, alphabet=DISTINGUISHABLE)

    class Anum14(Account):
        passcode = Password(length=14, alphabet=DISTINGUISHABLE)

    class Anum16(Account):
        passcode = Password(length=16, alphabet=DISTINGUISHABLE)

    class Anum18(Account):
        passcode = Password(length=18, alphabet=DISTINGUISHABLE)

    class Anum20(Account):
        passcode = Password(length=20, alphabet=DISTINGUISHABLE)

    # BBB {section}
    # CCC {section}
    class Char4(Account):
        passcode = Password(length=4, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char6(Account):
        passcode = Password(length=6, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char8(Account):
        passcode = Password(length=8, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char10(Account):
        passcode = Password(length=10, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char12(Account):
        aliases = ['char']
        passcode = Password(length=12, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char14(Account):
        passcode = Password(length=14, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char16(Account):
        passcode = Password(length=16, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char18(Account):
        passcode = Password(length=18, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char20(Account):
        passcode = Password(length=20, alphabet=ALPHANUMERIC+PUNCTUATION)

    # DDD {section}
    # EEE {section}
    class Extreme(Account):
        passcode = Passphrase(length=64, alphabet=PRINTABLE)

    # FFF {section}
    # GGG {section}
    # HHH {section}
    # III {section}
    # JJJ {section}
    # KKK {section}
    # LLL {section}
    # MMM {section}
    # NNN {section}
    # OOO {section}
    # PPP {section}
    class Pin4(Account):
        aliases = ['pin']
        passcode = PIN(length=4)

    class Pin6(Account):
        passcode = PIN(length=6)

    class Pin8(Account):
        aliases = ['num']
        passcode = PIN(length=8)

    class Pin10(Account):
        passcode = PIN(length=10)

    class Pin12(Account):
        passcode = PIN(length=12)

    # QQQ {section}
    # RRR {section}
    # SSS {section}
    # TTT {section}
    # UUU {section}
    # VVV {section}
    # WWW {section}
    class Word(Account):
        passcode = Passphrase(length=1)

    class Word2(Account):
        aliases = ['pair']
        passcode = Passphrase(length=2)

    class Word4(Account):
        aliases = ['word', 'xkcd']
        passcode = Passphrase(length=4)

    class Word6(Account):
        passcode = Passphrase(length=6)

    class Word8(Account):
        passcode = Passphrase(length=8)

    # XXX {section}
    # YYY {section}
    # ZZZ {section}

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
''')

# Initial user key file {{{1
USER_KEY_FILE_INITIAL_CONTENTS = dedent('''\
    # DO NOT CHANGE THIS KEY
    user_key = ({user_key})
''')


# Fields {{{1
# Fields reserved for use by Avendesora
TOOL_FIELDS = ['aliases', 'default', 'master', 'discovery', 'browser']

