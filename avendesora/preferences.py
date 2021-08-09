# Avendesora Password Generator Preferences

# License {{{1
# Copyright (C) 2016-2021 Kenneth S. Kundert
#
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
from appdirs import user_config_dir, user_cache_dir

# Non-Config Settings {{{1
# These value can be accessed with get_settings,
# but should not be found in the config file
NONCONFIG_SETTINGS = {
    'config_file': 'config',
    'config_doc_file': 'config.doc',
    'settings_dir': user_config_dir('avendesora'),
    'cache_dir': user_cache_dir('avendesora'),
    'default_accounts_file': 'accounts.gpg',
    'default_stealth_accounts_file': 'stealth_accounts',
    'charsets_hash': 'a055240c4c498e1470f5f3e80b3ec599',
    'dict_hash': '5dbabd4114eae520c1de8963a8b8d09d',
    'mnemonic_hash': 'cafd522d6627011d78e576f2d0b6ed58',
    'secrets_hash': 'd0e7d25e0c4e2e7281d62b44e2203a21',
    'discard_logfile': False,
    'commonly_mistaken_attributes': {
        'url': 'urls',
        'alias': 'aliases',
        'description': 'desc',
    }
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
    'archive_stale': 1,
    'previous_archive_file': 'archive.prev.gpg',
    'config_dir_mask': 0o077,
    'account_file_mask': 0o077,
    'command_aliases': None,
    'credential_ids': 'username email',
    'credential_secrets': 'passcode password passphrase',
    'label_color': 'blue',
    'highlight_color': 'magenta',
    'color_scheme': 'dark',
    'browsers': {
        'c':  'google-chrome {url}',
        'ci': 'google-chrome --incognito {url}',
        'f':  'firefox -new-tab {url}',
        'fp':  'firefox -private-window {url}',
        'q':  'qutebrowser {url}',
        't':  'torbrowser {url}',
        'x':  'xdg-open {url}',  # system default browser
    },
    'help_url': 'https://avendesora.readthedocs.io/en/latest',
    'default_field': 'passcode password passphrase',
    'default_vector_field': 'questions',
    'dynamic_fields': '',
    'hidden_fields': '',
    'default_browser': 'x',
    'display_time': 60,
    'ms_per_char': None,
    'dictionary_file': None,
    'encoding': 'utf-8',
    'edit_account': (
        'gvim',                       # use gvim -v so that user can access
        '-v',                         # the X clipboard buffers
        '+silent! /^class {account}(Account):/',
        '+silent! normal zozt',       # open the fold, position near top of screen
        '{filepath}'
    ),
    'edit_template': (
        'gvim',                       # use gvim -v so that user can access
        '-v',                         # the X clipboard buffers
        r'+silent! /_[A-Z0-9_]\+_/',  # matches user modifiable template fields
                                      # fields take the form '_AAA_'
        '+silent! normal zozt',       # open the fold, position near top of screen
        '{filepath}'
    ),
    'hashes_file': 'hashes',
    'indent': '    ',
    'log_file': 'log.gpg',
    'default_protocol': 'https',
    'user_key_file': 'key.gpg',
    'use_pager': True,
    'selection_utility': 'gtk',
    'verbose': False,
    'default_account_template': 'bank',
    'account_templates': {
        'website': dedent("""
            class _NAME_(Account): # %s1
                desc = '_DESCRIPTION_'
                aliases = '_ALIAS1_ _ALIAS2_'
                username = '_USERNAME_'
                email = '_EMAIL_'
                passcode = Password()
            # Avendesora: above provides a random selection of letters and digits
            # Avendesora: Alternative 1: passcode = PasswordRecipe('12 2u 2d 2s')
            # Avendesora:     length is 12, includes 2 upper, 2 digits and 2 symbols
            # Avendesora:     use '12 2u 2d 2c!@#$&' to specify valid symbol characters.
            # Avendesora: Alternative 2: passcode = Passphrase()
            # Avendesora:     provides a random selection of 4 words
                questions = [
                    Question("_QUESTION1_?"),
                    Question("_QUESTION2_?"),
                    Question("_QUESTION3_?"),
                ]
                urls = '_URL_'
            # Avendesora: specify URL or URLs to be used by the browse command.
            # Avendesora: generally this is the URL of the sign-in page.
                discovery = RecognizeURL(
                    'https://_URL_',
                    script='{email}{tab}{passcode}{return}'
                )
            # Avendesora: Specify multiple urls to recognizer if several pages need same script.
            # Avendesora: Specify list of recognizers if multiple pages need different scripts.

            # Avendesora: Tailor the account entry to suit you needs.
            # Avendesora: You can add or delete class attributes as you see fit.
            # Avendesora: The 'n' key should take you to the next field name.
            # Avendesora: Use 'cw' to specify a field value, or 'dd' to delete it if unneeded.
            # Avendesora: Fields surrounded by << and >> will be hidden.
            # Avendesora: All lines that begin with '# Avendesora:' are automatically removed.
        """ % (3*'{')),
        'shell': dedent("""
            class _NAME_(Account): # %s1
                desc = '_DESCRIPTION_'
                aliases = '_ALIAS1_ _ALIAS2_'
                passcode = Passphrase()
            # Avendesora: Alternatively use PasswordRecipe('12 2u 2d 2s')
            # Avendesora: or '12 2u 2d 2c!@#$&' to specify valid symbol characters.
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
        """ % (3*'{')),
        'bank': dedent("""
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
            # Avendesora: length is 12, includes 2 upper, 2 digits and 2 symbols
            # Avendesora: Alternatively use '12 2u 2d 2c!@#$&' to specify valid symbol characters.
            # Avendesora: Alternatively use Passphrase()
                verbal = Passphrase(length=2)
                pin = PIN()
                questions = [
                    Question("_QUESTION1_?"),
                    Question("_QUESTION2_?"),
                    Question("_QUESTION3_?"),
                ]
                urls = '_URL_'
            # Avendesora: specify urls to indicate the url to be used by the browse command.
                discovery = RecognizeURL(
                    'https://_URL_',
                    script='{email}{tab}{passcode}{return}'
                )
            # Avendesora: Specify multiple urls to recognizer if several pages need same script.
            # Avendesora: Specify list of recognizers if multiple pages need different scripts.

            # Avendesora: Tailor the account entry to suit you needs.
            # Avendesora: You can add or delete class attributes as you see fit.
            # Avendesora: The 'n' key should take you to the next field name.
            # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
            # Avendesora: Fields surrounded by << and >> will be hidden.
            # Avendesora: All lines that begin with '# Avendesora:' are deleted.
        """ % (3*'{')),
    },

    # use absolute paths for executables so they cannot be maliciously replaced
    # by changing the path.
    'gpg_executable': '/usr/bin/gpg2',
    'gpg_home': '~/.gnupg',
    'gpg_armor': 'extension',
    'gpg_ids': None,
    'xdotool_executable': '/usr/bin/xdotool',
    'xsel_executable': '/usr/bin/xsel',
    'dmenu_executable': '/usr/bin/dmenu',
    'arp_executable': '/sbin/arp',
}

# The following could be config settings, but they do not seem worth promoting.
INITIAL_AUTOTYPE_DELAY = 0.25
    # Give the window manager a bit of time to close the 'choose' dialog and
    # refocus on the original window. Delay given in seconds.

# Initial config file {{{1
CONFIG_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Configuration
    #
    # This file is read by Avendesora. Use it to change any configuration
    # settings from their default values.  See {config_doc_file} for the list of
    # available settings along with a description and the default value of the
    # setting.

    # Default identity to use when creating encrypted files.
    gpg_ids = {gpg_ids}

    default_browser = 'f'
    browsers = {{
        'c': 'google-chrome {{url}}',
        'ci': 'google-chrome --incognito {{url}}',
        'f': 'firefox -new-tab {{url}}',
        'fp': 'firefox -private-window {{url}}',
        'q': 'qutebrowser {{url}}',
        't': 'torbrowser {{url}}',
        'x': 'xdg-open {{url}}',
    }}
    command_aliases = dict(
        a = 'add',
        A = 'archive',
        b = 'browse',
        bc = 'browse --browser c',
        c = 'conceal',
        C = 'changed',
        e = 'edit',
        f = 'find',
        h = 'help',
        ident = 'identity',
        I = 'identity',
        init = 'initialize',
        i = 'interactive',
        login = 'credentials',
        l = 'credentials',
        N = 'new',
        alphabet = 'phonetic',
        p = 'phonetic',
        quest = 'questions',
        q = 'questions',
        qc = 'questions --clipboard',
        r = 'reveal',
        s = 'search',
        val = 'value',
        v = 'value',
        vc = 'value --clipboard',
        vals = 'values',
        vs = 'values',
        V = 'values',
    )
    # vim: filetype=python sw=4 sts=4 et ai ff=unix nofen fileencoding={encoding} :
''')

# Initial config.doc file {{{1
CONFIG_DOC_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Configuration Documentation
    #
    # This file is generated and updated by Avendesora using the initialize
    # command. It documents the supported configuration settings and gives the
    # default values for those settings. However it is not read by Avendesora. To
    # change your configuration settings, you should modify your config file:
    # {config_file}. In general you want to include only those settings that
    # differ from their defaults in {config_file}. In this way, if the defaults
    # change as Avendesora is upgraded you will naturally pick up the new
    # values.
    #
    # This file is replaced every time you run 'avendesora initialize'. Any
    # changes you make to this file will be lost.

    # Avendesora settings
    log_file = {log_file}
        # The desired location of the log file (relative to config directory).
        # Adding a suffix of .gpg or .asc causes the file to be encrypted
        # (otherwise it can leak account names). Use None to disable logging.

    archive_file = {archive_file}
    previous_archive_file = {previous_archive_file}
        # The desired location of the archive files (relative to config director).
        # End the path in .gpg or .asc. Use None to disable archiving.

    archive_stale = {archive_stale}
        # The archive file is consider stale if it is this many days older than
        # the most recently updated account file.

    default_field = {default_field}
        # The name of the field to use for the value command when one is not
        # given. May be a space separated list of names, in which case the first
        # that is found is used.

    default_vector_field = {default_vector_field}
        # The name of the field to use when an integer is given as the argument
        # to the value command. In this case the field is expected to be a list
        # and the argument is taken to be the index of the desired value.
        # For example, if default_vector_field is 'question' and the argument
        # given with the value command is 1, then question[1] is produced.

    dynamic_fields = {dynamic_fields}
        # Fields whose values can change in real time. These fields will not be
        # mentioned by the *changed* command, even if their value differs from
        # when the last archive was created.

    hidden_fields = {hidden_fields}
        # Names of fields that should not appear in the summary produced by the
        # values command unless the --all option is specified.  A typical value
        # includes estimated_value, postmortem_recipients, and bitwarden.

    credential_ids = {credential_ids}
        # A string that contains the field names (space separated) that should be
        # considered by the credentials command for the account identity.

    credential_secrets = {credential_secrets}
        # A string that contains the field names (space separated) that should be
        # considered by the credentials command for the primary account secret.

    display_time = {display_time}
        # The number of seconds that the secret will be displayed before it is
        # erase when writing to the TTY or clibboard.

    ms_per_char = {ms_per_char}
        # The time between keystrokes when autotyping in milliseconds. The
        # default is 12ms.

    encoding = {encoding!r}
        # The unicode encoding to use when reading or writing files.

    edit_account = {edit_account}
        # The command used when editing an account. The command is given as
        # list of strings. The strings may contain {{filepath}} and {{account}},
        # which are replaced by the path to the file and the name of the
        # account.

    edit_template = {edit_template}
        # The command used when creating a new account that has been initialized
        # with a template. The command is given as list of strings. The strings
        # may contain {{filepath}}, which is replaced by the path to the file.

    browsers = {browsers}
        # A dictionary containing the supported browsers. For each entry the key
        # is the name to be used for the browser, and the value is string that
        # contains the command that invokes the browser. The value may contain
        # {{url}}, which is replaced by the URL to open.

    default_browser = {default_browser}
        # The name of the default browser. This name should be one of the keys
        # in the browsers dictionary.

    command_aliases = {command_aliases}
        # A dictionary of command short cuts. Each alias should map to two
        # values, the full command name and a list of command line options,
        # which may be None.  For example:
        #     command_aliases = dict(
        #         v = ('value', None),
        #         vc = ('value', ['--clipboard']),
        #     )

    default_protocol = {default_protocol}
        # The default protocol to use for a URL if the protocol is not specified
        # in the requested URL. Generally this should be 'https' or 'http',
        # though 'https' is recommended.

    config_dir_mask = {config_dir_mask}
        # An integer that determines if a warning should be printed about the
        # file permissions on the Avendesora configuration directory
        # (~/.config/avendesora) being too loose. A bitwise and operation is
        # performed between this value and the actual file permissions, and if
        # the result is nonzero, a warning is printed.  Set to 0o000 to disable
        # the warning. Set to 0o077 to generate a warning if the configuration
        # directory is readable or writable by the group or others. Set to 0o007
        # to generated a warning if the directory is readable or writable by
        # others.

    account_file_mask = {account_file_mask}
        # An integer that determines if a warning should be printed about the
        # file permissions of the accounts and archive files being too loose.  A
        # bitwise and operation is performed between this value and the actual
        # file permissions, and if the result is nonzero, a warning is printed.
        # Set to 0o000 to disable the warning. Set to 0o077 to generate a
        # warning if the configuration directory is readable or writable by the
        # group or others. Set to 0o007 to generated a warning if the directory
        # is readable or writable by others.

    label_color = {label_color}
        # The color of the label use by the value and values commands.
        # Choose from black, red, green, yellow, blue, magenta, cyan, white.

    highlight_color = {highlight_color}
        # The color of the highlight use by the value and values commands.
        # Choose from black, red, green, yellow, blue, magenta, cyan, white.

    color_scheme = {color_scheme}
        # The color scheme used for the label color.  Choose from dark, light.
        # If the shell background color is light, use dark.

    use_pager = {use_pager}
        # Use a external program to break long output into pages.
        # May be either a boolean or a string. If a string the string is taken
        # to be a command line use to invoke a paging program (like 'more'). If
        # True, the program name is taken from the PAGER environment variable if
        # set, or 'less' is used if not set. If False, a paging program is not
        # used.

    selection_utility = {use_pager}
        Which utility should be used when it becomes necessary for you to
        interactively make a choice. Two utilities are available: 'gtk', the
        default, and 'dmenu'.

        'gtk' is the built-in selection. When needed it pops a small dialog box in
        the middle of the screen. You can use the 'j' and 'k' to navigate to your
        selection and 'l' to make the selection or 'h' to cancel.  Alternately you
        can use the arrow keys and Enter and Esc to navigate, select, and cancel.

        'dmenu' is an external utility, and must be installed. With *dmenu* you
        type the first few letters of your selection to highlight it, then type
        'Enter' to select or 'Esc' to cancel.

    verbose = {verbose}
        # Set this to True to generate additional information in the log file
        # that can help debug account discovery issues.  Normally it should be
        # False to avoid leaking account information into log file.
        # This is most useful when debugging account discovery, and in that case
        # this setting has largely been superseded by the use of the --title and
        # --verbose command line options.

    help_url = {help_url}
        # The base URL for Avendesora's online documentation.

    # Account templates
    # Use these settings to specify the available account templates that are
    # used when creating new accounts.  The templates are given as a dictionary
    # where the key is the name of the template and the value is the template
    # itself. The template is passed through textwrap.dedent() to remove any
    # leading white space.  Any lines that begin with '# Avendesora: ' represent
    # comments that can contain instructions to the user. They will are removed
    # when the account is created.
    account_templates = {account_templates}
    default_account_template = {default_account_template}

    # GPG settings
    # Information used by GPG when encrypting and decrypting files.
    gpg_ids = {gpg_ids}
        # the GPG IDs to use by default when creating encrypted files (the
        # archive and account files).
    gpg_armor = {gpg_armor}
        # In the GPG world, armoring a file means converting it to simple ASCI.
        # Choose between 'always', 'never' and 'extension' (.asc: armor, .gpg:
        # no).
    gpg_home = {gpg_home}
        # This is your GPG home directory. By default it will be ~/.gnupg.

    # External Executables
    # Use of full absolute paths for executables is recommended.
    gpg_executable = {gpg_executable}
        # Path to the gpg2 executable.
    xdotool_executable = {xdotool_executable}
    xsel_executable = {xsel_executable}
        # recommend '/usr/bin/xsel -p' if you wish to use mouse middle click
        # recommend '/usr/bin/xsel -b' if you wish to use mouse right click then paste
    dmenu_executable = {dmenu_executable}

    # vim: filetype=python sw=4 sts=4 et ai ff=unix nofen fileencoding={encoding} :
''')


# Initial hash file {{{1
HASH_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Hashes
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} :
    #
    # Changing the contents of the dictionary, secrets, or charsets files can change
    # the secrets you generate, thus you should be very careful in changing
    # these files.  These files may change when upgrading the program. Care is
    # taken to assure than your generated passwords do not change as a result of
    # an upgrade, but mistakes can be made.  Hashes for the contents of these
    # files are stored here, and the hashes are checked each time Avendesora is
    # run.  If you get a message indicating that the hashes have changed, it
    # does not mean that there is a problem. Rather it indicates that a change
    # has been made that could conceivably have created a problem and you
    # should do some checking before continuing to use the program. Once you are
    # convinced everything is working as expected, you should update these
    # hashes as needed.
    #
    # When upgrading the program, here is the procedure you should use.
    # 1. Before upgrading you should run 'avendesora changed' and examine all
    #    the differences and make sure they are all expected.
    # 2. Run 'avendesora archive' to create a clean archive.
    # 3. Update Avendesora
    #    This version may emit hash warnings.
    # 4. Run 'avendesora changed'. If no changes are noted, it is okay to update
    #    the appropriate hashes below.
    # 5. If there are changes, do not upgrade and report the situation to
    #    Avendesora's authors.

    charsets_hash = {charsets_hash}
    dict_hash     = {dict_hash}
    mnemonic_hash = {mnemonic_hash}
    secrets_hash  = {secrets_hash}

    # CHANGE THESE VALUES ONLY WHEN REQUESTED BY AVENDESORA AND IF YOU HAVE
    # FOLLOWED THE ABOVE PROCEDURE TO ASSURE YOUR GENERATED SECRETS HAVE NOT
    # CHANGED.

    # Generally the best way to upgrade this file is to simply delete it and
    # then run 'avendesora init', which will regenerate it with the updated
    # values.
''')


# Initial accounts file {{{1
ACCOUNTS_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Accounts
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} foldmethod=marker :

    # Description {section}
    # Subclass Account to create new accounts. Attributes of the subclass are
    # the account fields. Fields can be strings, lists, dictionaries or
    # Avendesora classes.
    #
    # Example:
    #     class Mortgage(Account):
    #         username = 'herbie962'
    #         account = '0036727963'
    #         passcode = PasswordRecipe('12 2u 2d 2s')
    #         phone = '800-529-2345'
    #         discovery = [
    #             RecognizeURL(
    #                 'https://www.loanservicing.com/login.jsp',
    #                 script='{{account}}{{tab}}{{passcode}}{{return}}',
    #             ),
    #         ]

    # Imports {section}
    from avendesora import (
        # Basics
        Account, StealthAccount, Hide, Hidden, GPG, Script, WriteFile,

        # Character sets
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, SYMBOLS, WHITESPACE, PRINTABLE, DISTINGUISHABLE,

        # Secrets
        Password, Passphrase, PIN, Question, MixedPassword, PasswordRecipe,
        BirthDate, OTP,

        # Account Discovery
        RecognizeAll, RecognizeAny, RecognizeCWD, RecognizeEnvVar,
        RecognizeFile, RecognizeHost, RecognizeNetwork, RecognizeTitle,
        RecognizeURL, RecognizeUser,
    )
    try:
        import Scrypt
    except ImportError:
        # You need to install scrypt using 'pip install scrypt' to use Scrypt
        pass

    # Shared Values {section}
    # These values are shared across all accounts defined in this file.
    #
    # Never disclose the master seed to anyone you are not collaborating with.
    # Never give it to your collaborator using an insecure channel, such as
    # email.  If you have encrypted this file with your colloborator's public
    # GPG key, is best to simply send the encrypted file to your
    # collaborator the first time. After than, you can send the account
    # informaiton in clear text as long as you are careful not to expose the
    # master_seed.
    master_seed = Hidden({master_seed}, secure=True)
    gpg_ids = {gpg_ids}


    # Accounts
''')

# Initial stealth_accounts file {{{1
STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS = dedent('''\
    # Avendesora Stealth Accounts
    # vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding={encoding} foldmethod=marker :

    # Description {section}
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
    class Pin2(StealthAccount):
        passcode = PIN(length=2)

    class Pin3(StealthAccount):
        passcode = PIN(length=3)

    class Pin4(StealthAccount):
        aliases = 'pin'
        passcode = PIN(length=4)

    class Pin5(StealthAccount):
        passcode = PIN(length=5)

    class Pin6(StealthAccount):
        passcode = PIN(length=6)

    class Pin7(StealthAccount):
        passcode = PIN(length=7)

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


    # Passphrases {section}
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
    #     hidden text: <hidden_arg>
    #
    # or
    #
    #     > base64 -d - < <filename>
    #
    # where <filename> contains <hidden_arg>.
    #

    from avendesora import (
        Hidden, Question, Script, OTP, WriteFile,
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
    # The list of files that contain accounts.
    #
    # The first file given becomes the default file for the add command, meaning
    # that the add command will add a new account to the first file specified
    # unless a different files is specified explicitly.
    #
    # When an account is not in the cache, these files are searched in the order
    # given.  You should list the most likely candidates first.

    accounts_files = {accounts_files}
''')


# Fields {{{1
# Fields reserved for use by Avendesora
# They are not displayed by the values command.
HIDDEN_TOOL_FIELDS = 'NAME aliases default discovery browser default_url'.split()
FORBIDDEN_TOOL_FIELDS = 'master_seed account_seed'.split()
