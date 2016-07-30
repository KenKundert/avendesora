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

# Non-Config Settings {{{1
# These value can be accessed with get_settings,
# but should not be found in the config file
NONCONFIG_SETTINGS = {
    'config_file': 'config',
    'settings_dir': user_config_dir('avendesora'),
    'default_accounts_file': 'accounts.gpg',
    'default_templates_file': 'templates.asc',
    'dict_hash': '11fe5bc734f4a956c37d7cb3da16ab3f',
    'secrets_hash': 'f7aeadac3cefe513047fdb4efa26591f',
    'charsets_hash': '405332bcb8330b7502d292991026e328',
}


# Config Settings {{{1
# These are the default values for settings that may be found in the config file
CONFIG_DEFAULTS = {
    'accounts_files': [
        NONCONFIG_SETTINGS['default_accounts_file'],
        NONCONFIG_SETTINGS['default_templates_file'],
    ],
    'account_list_file': '.accounts_files',
    'archive_file': 'archive.gpg',
    'browsers': {
        'f': 'firefox -new-tab %s',
        'g': 'google-chrome %s',
        't': 'torbrowser %s',
        'x': 'xdg-open %s', # system default browser
    },
    'color_scheme': 'dark',
    'default_browser': 'x',
    'default_field': 'passcode',
    'default_vector_field': 'questions',
    'display_time': 60,
    'dictionary_file': 'words',
    'encoding': 'utf8',
    'hashes_file': '.hashes',
    'indent': '    ',
    'label_color': 'blue',
    'log_file': 'log.gpg',
    'required_protocols': ['https'],
    'user_key_file': '.key.gpg',

    # use absolute paths for executables so they cannot be maliciously replaced
    # by changing the path.
    'gpg_executable': '/usr/bin/gpg2',
    'gpg_home': '~/.gnupg',
    'gpg_armor': 'extension',
    'gpg_ids': None,
    'xdotool_executable': '/usr/bin/xdotool',
    'xsel_executable': '/usr/bin/xsel',

}

# the following could be config settings, but they do not seem worth promoting
INITIAL_AUTOTYPE_DELAY = 0.0

# Initial config file {{{1
CONFIG_FILE_INITIAL_CONTENTS = dedent('''\
    # Include a few unicode characters, but to make sure they work: ±αβγδε
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
    encoding = {encoding}
    browsers = {browsers}
    default_browser = {default_browser}
    required_protocols = {required_protocols}
    label_color = {label_color}
        # choose from black, red, green, yellow, blue, magenta, cyan, white
    color_scheme = {color_scheme}
        # choose from dark, light

    # Information used by GPG when encrypting and decrypting files.
    gpg_ids = {gpg_ids}
    gpg_armor = {gpg_armor}
        # choose between 'always', 'never' and 'by-ext' (.asc: armor, .gpg: no)
    gpg_home = {gpg_home}

    # Utilities
    # use of full absolute paths for executables is recommended
    gpg_executable = {gpg_executable}
    xdotool_executable = {xdotool_executable}
    xsel_executable = {xsel_executable}

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
''')


# Initial hash file {{{1
HASH_FILE_INITIAL_CONTENTS = dedent('''\
    # Include a few unicode characters, but to make sure they work: ±αβγδε
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
    # Include a few unicode characters, but to make sure they work: ±αβγδε
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
    gpg_ids = {gpg_ids}

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
    # Include a few unicode characters, but to make sure they work: ±αβγδε
    # Templates
    #
    # Templates are accounts without master passwords and without much in the way of
    # attributes. Use them to generate pass codes of various types for stealth
    # accounts.

    # Imports {section}
    from avendesora import (
        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Account
        Account,

        # Secrets
        Password, Passphrase, PIN,
    )
    gpg_ids = {gpg_ids}

    # Templates
    # Alphanumeric passwords {section}
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

    # High entropy passwords {section}
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

    # Extreme passwords {section}
    class Extreme(Account):
        passcode = Passphrase(length=64, alphabet=PRINTABLE)

    # PINs {section}
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

    # Pass phrases {section}
    class Word(Account):
        passcode = Passphrase(length=1)

    class Word2(Account):
        aliases = ['pair']
        passcode = Passphrase(length=2)

    class Word3(Account):
        passcode = Passphrase(length=3)

    class Word4(Account):
        aliases = ['word', 'xkcd']
        passcode = Passphrase(length=4)

    class Word5(Account):
        passcode = Passphrase(length=5)

    class Word6(Account):
        passcode = Passphrase(length=6)

    class Word7(Account):
        passcode = Passphrase(length=7)

    class Word8(Account):
        passcode = Passphrase(length=8)

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
''')

# Initial user key file {{{1
USER_KEY_FILE_INITIAL_CONTENTS = dedent('''\
    # Include a few unicode characters, but to make sure they work: ±αβγδε
    # DO NOT CHANGE THIS KEY
    user_key = ({user_key})
''')

# Account list file {{{1
ACCOUNT_LIST_FILE_CONTENTS = dedent('''\
    # Include a few unicode characters, but to make sure they work: ±αβγδε
    accounts_files = {accounts_files}
''')


# Fields {{{1
# Fields reserved for use by Avendesora
TOOL_FIELDS = ['aliases', 'default', 'master', 'discovery', 'browser']

