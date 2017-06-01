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
    'default_stealth_accounts_file': 'stealth_accounts',
    'charsets_hash': 'e4ae3714d9dbdffc0cf3b51a0462b5ec',
    'dict_hash': '11fe5bc734f4a956c37d7cb3da16ab3f',
    'secrets_hash': 'ed6affe9ce4c3db17bb03750fc71dc51',
    'discard_logfile': False,
}


# Config Settings {{{1
# These are the default values for settings that may be found in the config file
CONFIG_DEFAULTS = {
    'accounts_files': [
        NONCONFIG_SETTINGS['default_accounts_file'],
        NONCONFIG_SETTINGS['default_stealth_accounts_file'],
    ],
    'account_list_file': 'accounts_files',
    'archive_file': 'archive.gpg',
    'previous_archive_file': 'archive.prev.gpg',
    'credential_ids': 'username email',
    'credential_secrets': 'passcode password passphrase',
    'label_color': 'blue',
    'color_scheme': 'dark',
    'browsers': {
        'f': 'firefox -new-tab {url}',
        'c': 'google-chrome {url}',
        't': 'torbrowser {url}',
        'x': 'xdg-open {url}', # system default browser
    },
    'default_command': 'credentials',
    'default_field': 'passcode',
    'default_vector_field': 'questions',
    'default_browser': 'x',
    'display_time': 60,
    'dictionary_file': 'words',
    'encoding': 'utf-8',
    'edit_account': (
        'gvim',   # use gvim -v so that user can access X clipboard buffers
        '-v',
        '+silent /^class {account}(Account):/',
        '+silent normal zozt',      # open the fold, position near top of screen
        '{filepath}'
    ),
    'edit_template': (
        'gvim',   # use gvim -v so that user can access X clipboard buffers
        '-v',
        '+silent /_[A-Z0-9_]\+_/',  # matches user modifiable template fields
                                    # fields take the form '_AAA_'
        '+silent normal zozt',      # open the fold, position near top of screen
        '{filepath}'
    ),
    'hashes_file': 'hashes',
    'indent': '    ',
    'log_file': 'log.gpg',
    'default_protocol': 'https',
    'user_key_file': 'key.gpg',
    'verbose': False,
    'default_account_template': 'bank',
    'account_templates': {
        'website': """
            class _NAME_(Account): # %s1
                desc = '_DESCRIPTION_'
                aliases = '_ALIAS1_ _ALIAS2_'
                username = '_USERNAME_'
                email = '_EMAIL_'
                passcode = PasswordRecipe('12 2u 2d 2s')
                questions = [
                    Question("_QUESTION1_?"),
                    Question("_QUESTION2_?"),
                    Question("_QUESTION3_?"),
                ]
                discovery = RecognizeURL(
                    'https://_URL_',
                    script='{email}{tab}{passcode}{return}'
                )

            # Avendesora: Tailor the account entry to suit you needs.
            # Avendesora: You can add or delete class attributes as you see fit.
            # Avendesora: The 'n' key should take you to the next field name.
            # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
            # Avendesora: Fields surrounded by << and >> will be hidden.
            # Avendesora: All lines that begin with '# Avendesora:' are deleted.
        """ % (3*'{'),
        'shell': """
            class _NAME_(Account): # %s1
                desc = '_DESCRIPTION_'
                aliases = '_ALIAS1_ _ALIAS2_'
                passcode = Passphrase()
                discovery = RecognizeTitle(
                    '_TITLE1_', '_TITLE2_',
                    script='{passcode}{return}'
                )

            # Avendesora: Tailor the account entry to suit you needs.
            # Avendesora: You can add or delete class attributes as you see fit.
            # Avendesora: The 'n' key should take you to the next field name.
            # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
            # Avendesora: Fields surrounded by << and >> will be hidden.
            # Avendesora: All lines that begin with '# Avendesora:' are deleted.
        """ % (3*'{'),
        'bank': """
            class _NAME_(Account): # %s1
                desc = '_DESCRIPTION_'
                aliases = '_ALIAS1_ _ALIAS2_'
                username = '_NAME_'
                email = '_EMAIL_'
                accounts = {
                    'checking':   <<_ACCOUNT_NUMBER_>>,
                    'savings':    <<_ACCOUNT_NUMBER_>>,
                    'creditcard': <<_ACCOUNT_NUMBER_>>,
                }
                customer_service = '_PHONE_NUMBER_'
                passcode = PasswordRecipe('12 2u 2d 2s')
                verbal = Passphrase(length=2)
                pin = PIN()
                questions = [
                    Question("_QUESTION1_?"),
                    Question("_QUESTION2_?"),
                    Question("_QUESTION3_?"),
                ]
                discovery = RecognizeURL(
                    'https://_URL_',
                    script='{email}{tab}{passcode}{return}'
                )

            # Avendesora: Tailor the account entry to suit you needs.
            # Avendesora: You can add or delete class attributes as you see fit.
            # Avendesora: The 'n' key should take you to the next field name.
            # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
            # Avendesora: Fields surrounded by << and >> will be hidden.
            # Avendesora: All lines that begin with '# Avendesora:' are deleted.
        """ % (3*'{'),
    },

    # use absolute paths for executables so they cannot be maliciously replaced
    # by changing the path.
    'gpg_executable': '/usr/bin/gpg2',
    'gpg_home': '~/.gnupg',
    'gpg_armor': 'extension',
    'gpg_ids': None,
    'xdotool_executable': '/usr/bin/xdotool',
    'xsel_executable': '/usr/bin/xsel -p',
    'use_pager': True,
    'arp_executable': '/sbin/arp',
}

# The following could be config settings, but they do not seem worth promoting.
INITIAL_AUTOTYPE_DELAY = 0.25
    # Give the window manager a bit of time to close the 'choose' dialog and
    # refocus on the original window. Delay given in seconds.

# Initial config file {{{1
CONFIG_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Configuration
    # vim: filetype=python sw=4 sts=4 et ai ff=unix nofen fileencoding={encoding} :
    #
    # The desired location of the log file (relative to config directory).
    # Adding a suffix of .gpg or .asc causes the file to be encrypted
    # (otherwise it can leak account names). Use None to disable logging.
    log_file = {log_file}

    # The desired location of the archive file (relative to config director).
    # End the path in .gpg. Use None to disable archiving.
    archive_file = {archive_file}
    previous_archive_file = {previous_archive_file}

    # Various settings
    default_command = {default_command}
    default_field = {default_field}
    default_vector_field = {default_vector_field}
    display_time = {display_time}
    encoding = {encoding}
    edit_account = {edit_account}
    edit_template = {edit_template}
    browsers = {browsers}
    default_browser = {default_browser}
    default_protocol = {default_protocol}
    label_color = {label_color}
        # Choose from black, red, green, yellow, blue, magenta, cyan, white.
    color_scheme = {color_scheme}
        # Choose from dark, light.
    use_pager = {use_pager}
    verbose = {verbose}
        # Set this to True to generate additional information in the log file
        # that can help debug account discovery issues.  Normally it should be
        # False to avoid leaking account information into log file.

    # Prototype accounts
    default_account_template = {default_account_template}
    account_templates = {account_templates}

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
''')


# Initial hash file {{{1
HASH_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Hashes
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} :
    #
    # Changing the contents of the dictionary, secrets, or charsets will change
    # the secrets you generate, thus you do not want to change these files once
    # you have started using the program. These are hashes for the contents of
    # these files at the time that this file was created. The program will
    # complain if the current contents of these files generate a different
    # hash. Only update these hashes if you know what you are doing.
    #
    # Here is the procedure you should use.
    # 1. Using the original version of Advendesora, run 'avendesora archive'
    #    This version should not emit a hash warning.
    # 2. Update Avendesora
    #    This version may emit hash warnings.
    # 3. Run 'avendesora changed'. If no changes are noted, it is okay to update
    #    the appropriate hashes.
    # 4. If there are changes, either do not upgrade or manually override the
    #    changed secrets to return them to their original values.

    charsets_hash = {charsets_hash}  # DO NOT CHANGE THIS LINE
    dict_hash     = {dict_hash}  # DO NOT CHANGE THIS LINE
    secrets_hash  = {secrets_hash}  # DO NOT CHANGE THIS LINE
''')


# Initial accounts file {{{1
ACCOUNTS_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Accounts
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} foldmethod=marker :
    #
    # Add information about each of your accounts to the accounts dictionary.
    #
    # You can use the dedent function to strip leading whitespace from
    # multi-line remarks.  You can use the character sets and exclude function
    # to create alphabets for you character-base passwords.
    #
    # Example:
    # To create an alphabet with all characters except tabs use either:
    #     Password(..., alphabet = exclude(PRINTABLE, '\\t'))
    # or:
    #     Password(..., alphabet = ALPHANUMERIC + PUNCTUATION + ' ')
    #
    # You can use PasswordRecipe() to generate passwords that include certain
    # character classes.
    #
    # Examples:
    # To create a 12 character password that contains 2 upper, 2 lower, 2
    # digits, and 2 symbols, use:
    #     PasswordRecipe("12 2u 2l 2d 2s")
    #
    # To create a 12 character password that contains 2 upper, 2 lower, 2
    # digits, and 2 characters from a specific set of characters, use:
    #     PasswordRecipe("12 2u 2l 2d 2c~!@#$%^&*+=?")
    #

    from avendesora import (
        # Basics
        Account, StealthAccount, Hide, Hidden, GPG, Script,

        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, SYMBOLS, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Secrets
        Password, Passphrase, PIN, Question, MixedPassword, PasswordRecipe,
        BirthDate,

        # Account Discovery
        RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
        RecognizeHost, RecognizeUser, RecognizeEnvVar, RecognizeNetwork,
    )
    try:
        # You need to install scrypt using 'pip install scrypt' to use Scrypt
        import Scrypt
    except ImportError:
        pass

    master_seed = Hidden({master_seed}, secure=True)
    gpg_ids = {gpg_ids}


    # Accounts
''')

# Initial stealth_accounts file {{{1
STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Stealth Accounts
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} foldmethod=marker :
    #
    # Stealth accounts are accounts where the class name is not taken to be the
    # account name, instead the user is interactively asked for the account
    # name. In this way there is no record that the account actually exists.

    # Imports {section}
    from avendesora import (
        # Account
        StealthAccount,

        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Secrets
        Password, PasswordRecipe, Passphrase, PIN, Hidden
    )

    # Accounts
    # Alphanumeric passwords {section}
    class Anum4(StealthAccount):
        passcode = Password(length=4, alphabet=DISTINGUISHABLE)

    class Anum6(StealthAccount):
        passcode = Password(length=6, alphabet=DISTINGUISHABLE)

    class Anum8(StealthAccount):
        passcode = Password(length=8, alphabet=DISTINGUISHABLE)

    class Anum10(StealthAccount):
        passcode = Password(length=10, alphabet=DISTINGUISHABLE)

    class Anum12(StealthAccount):
        aliases = 'anum'
        passcode = Password(length=12, alphabet=DISTINGUISHABLE)

    class Anum14(StealthAccount):
        passcode = Password(length=14, alphabet=DISTINGUISHABLE)

    class Anum16(StealthAccount):
        passcode = Password(length=16, alphabet=DISTINGUISHABLE)

    class Anum18(StealthAccount):
        passcode = Password(length=18, alphabet=DISTINGUISHABLE)

    class Anum20(StealthAccount):
        passcode = Password(length=20, alphabet=DISTINGUISHABLE)

    class Anum24(StealthAccount):
        passcode = Password(length=24, alphabet=DISTINGUISHABLE)

    class Anum32(StealthAccount):
        passcode = Password(length=32, alphabet=DISTINGUISHABLE)

    class Anum48(StealthAccount):
        passcode = Password(length=48, alphabet=DISTINGUISHABLE)

    class Anum64(StealthAccount):
        passcode = Password(length=64, alphabet=DISTINGUISHABLE)


    # Ascii passwords {section}
    class Char4(StealthAccount):
        passcode = Password(length=4, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char6(StealthAccount):
        passcode = Password(length=6, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char8(StealthAccount):
        passcode = Password(length=8, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char10(StealthAccount):
        passcode = Password(length=10, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char12(StealthAccount):
        aliases = 'char'
        passcode = Password(length=12, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char14(StealthAccount):
        passcode = Password(length=14, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char16(StealthAccount):
        passcode = Password(length=16, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char18(StealthAccount):
        passcode = Password(length=18, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char20(StealthAccount):
        passcode = Password(length=20, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char24(StealthAccount):
        passcode = Password(length=24, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char32(StealthAccount):
        passcode = Password(length=32, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char48(StealthAccount):
        passcode = Password(length=48, alphabet=ALPHANUMERIC+PUNCTUATION)

    class Char64(StealthAccount):
        alias = 'extreme'
        passcode = Password(length=64, alphabet=ALPHANUMERIC+PUNCTUATION)


    # Hex passwords {section}
    class Hex4(StealthAccount):
        passcode = Password(length=4, alphabet=HEXDIGITS, prefix='0x')

    class Hex8(StealthAccount):
        passcode = Password(length=8, alphabet=HEXDIGITS, prefix='0x')

    class Hex16(StealthAccount):
        passcode = Password(length=16, alphabet=HEXDIGITS, prefix='0x')

    class Hex24(StealthAccount):
        passcode = Password(length=24, alphabet=HEXDIGITS, prefix='0x')

    class Hex32(StealthAccount):
        passcode = Password(length=32, alphabet=HEXDIGITS, prefix='0x')

    class Hex48(StealthAccount):
        passcode = Password(length=48, alphabet=HEXDIGITS, prefix='0x')

    class Hex64(StealthAccount):
        passcode = Password(length=64, alphabet=HEXDIGITS, prefix='0x')

    class Hex96(StealthAccount):
        passcode = Password(length=96, alphabet=HEXDIGITS, prefix='0x')


    # PINs {section}
    class Pin4(StealthAccount):
        aliases = 'pin'
        passcode = PIN(length=4)

    class Pin6(StealthAccount):
        passcode = PIN(length=6)

    class Pin8(StealthAccount):
        aliases = 'num'
        passcode = PIN(length=8)

    class Pin10(StealthAccount):
        passcode = PIN(length=10)

    class Pin12(StealthAccount):
        passcode = PIN(length=12)

    class Pin14(StealthAccount):
        passcode = PIN(length=14)

    class Pin16(StealthAccount):
        passcode = PIN(length=16)

    class Pin18(StealthAccount):
        passcode = PIN(length=18)

    class Pin20(StealthAccount):
        passcode = PIN(length=20)

    class Pin24(StealthAccount):
        passcode = PIN(length=24)

    class Pin32(StealthAccount):
        passcode = PIN(length=32)

    class Pin48(StealthAccount):
        passcode = PIN(length=48)

    class Pin64(StealthAccount):
        passcode = PIN(length=64)


    # Pass phrases {section}
    class Word1(StealthAccount):
        aliases = 'word'
        passcode = Passphrase(length=1)

    class Word2(StealthAccount):
        aliases = 'pair'
        passcode = Passphrase(length=2)

    class Word3(StealthAccount):
        passcode = Passphrase(length=3)

    class Word4(StealthAccount):
        aliases = 'words xkcd'
        passcode = Passphrase(length=4)

    class Word5(StealthAccount):
        passcode = Passphrase(length=5)

    class Word6(StealthAccount):
        passcode = Passphrase(length=6)

    class Word7(StealthAccount):
        passcode = Passphrase(length=7)

    class Word8(StealthAccount):
        passcode = Passphrase(length=8)

    class Word10(StealthAccount):
        passcode = Passphrase(length=10)

    class Word12(StealthAccount):
        passcode = Passphrase(length=12)

    class Word16(StealthAccount):
        passcode = Passphrase(length=16)

    class Word20(StealthAccount):
        passcode = Passphrase(length=20)

    class Word24(StealthAccount):
        passcode = Passphrase(length=24)

    class Word32(StealthAccount):
        passcode = Passphrase(length=32)


    # Web passwords {section}
    class Web6(StealthAccount):
        passcode = PasswordRecipe('6 u d s')

    class Web8(StealthAccount):
        passcode = PasswordRecipe('8 u d s')

    class Web10(StealthAccount):
        passcode = PasswordRecipe('10 2u 2d 2s')

    class Web12(StealthAccount):
        aliases = 'web'
        passcode = PasswordRecipe('12 2u 2d 2s')

    class Web14(StealthAccount):
        passcode = PasswordRecipe('14 2u 2d 2s')

    class Web16(StealthAccount):
        passcode = PasswordRecipe('16 3u 3d 3s')

    class Web18(StealthAccount):
        passcode = PasswordRecipe('18 3u 3d 3s')

    class Web20(StealthAccount):
        passcode = PasswordRecipe('20 3u 3d 3s')

    class Web24(StealthAccount):
        passcode = PasswordRecipe('24 4u 4d 4s')

    class Web32(StealthAccount):
        passcode = PasswordRecipe('32 5u 5d 5s')

    class Web48(StealthAccount):
        passcode = PasswordRecipe('48 6u 6d 6s')

    class Web64(StealthAccount):
        passcode = PasswordRecipe('64 8u 8d 8s')
''')

# Initial user key file {{{1
USER_KEY_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Personal Key
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} :
    #
    # This is your personal encryption key.
    # DO NOT CHANGE THIS KEY.  DO NOT SHARE THIS KEY.
    user_key = ({user_key})
''')

# Archive file header {{{1
ARCHIVE_FILE_CONTENTS = dedent('''\
    # Avendesora Archive File
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} :
    #
    # This file allows you to recover your secrets if Avendesora is not
    # available.  Except for the master seeds it contains all of the
    # information for all of the accounts. The secrets have been generated and
    # hidden using base64 encoding. To decode a hidden argument of the form:
    # Hidden('<hidden_arg>'), you can use:
    #
    #     > avendesora reveal
    #     hidden text: <hidden_text>
    #
    # or
    #
    #     > base64 -d - < <filename>
    #
    # where <filename> contains <hidden_arg>.
    #

    from avendesora import (
        Hidden, Question, Script,
        RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
        RecognizeHost, RecognizeUser, RecognizeEnvVar, RecognizeNetwork,
        RecognizeFile
    )

    CREATED = '{date}'
    ACCOUNTS = {{
    {accounts}
    }}
''')

# Account list file {{{1
ACCOUNT_LIST_FILE_CONTENTS = dedent('''\
    # The list of files that contain accounts. The order of the files is
    # immaterial, except that first file given is the default file, meaning that
    # the add account will add a new account to the first files specified unless
    # a different files is specified explicitly.

    accounts_files = {accounts_files}
''')


# Fields {{{1
# Fields reserved for use by Avendesora
TOOL_FIELDS = [
    'NAME', 'aliases', 'default', 'master', 'discovery', 'browser', 'default_url'
]
