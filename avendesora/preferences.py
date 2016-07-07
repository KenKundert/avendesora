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

# Filenames {{{1
SETTINGS_DIR = user_config_dir('avendesora')
DICTIONARY_FILENAME = 'words'
CONFIG_FILENAME = 'config'
    # config file must be unencrypted (it contains the gpg settings)
DEFAULT_ACCOUNTS_FILENAME = 'accounts.gpg'
DEFAULT_LOG_FILENAME = 'log'
    # log file will be encrypted if you add .gpg or .asc extension
DEFAULT_ARCHIVE_FILENAME = 'archive.gpg'

# Settings {{{1
INDENT = '    '
LABEL_COLOR = 'yellow'
    # choose from normal, black, red, green, yellow, blue, magenta, cyan, white
INITIAL_AUTOTYPE_DELAY = 0.0
DEBUG = False
    # Turns on the logging of extra information, but may expose sensitive
    # account information in the log file.
PREFER_HTTPS = True
    # When PREFER_HTTPS is true, avendesora requires the https protocol unless
    # http is explicitly specified in the url.
    # When PREFER_HTTPS is false, avendesora allows the http protocol unless
    # https is explicitly specified in the url.
DEFAULT_FIELD = 'passcode'
DEFAULT_VECTOR_FIELD = 'questions'
DEFAULT_DISPLAY_TIME = 60


# Utility programs {{{1
# use absolute paths for xdotool and xsel so they cannot be maliciously replaced
XDOTOOL = '/usr/bin/xdotool'
XSEL = '/usr/bin/xsel'
NOTIFIER_NORMAL = ['notify-send', '--urgency=low']
NOTIFIER_ERROR = ['notify-send', '--urgency=normal']

# Signatures {{{1
# These signatures must be the sha1 signatures for the corresponding files
# Regenerate them with 'sha1sum <filename>'
# These are used in creating the initial master password file.
SECRETS_SHA1 = "5d1c97a0fb699241fca5d50a7ad0508047990510"
CHARSETS_SHA1 = "dab48b2103ebde97f78cfebd15cc1e66d6af6ed0"
DICTIONARY_SHA1 = "d9aa1c08e08d6cacdf82819eeb5832429eadb95a"

# GPG Settings
GPG_PATH = '/usr/bin/gpg2'
GPG_HOME = '~/.gnupg'
GPG_ARMOR = True

# Browsers {{{1
# Associate a command with a browser key.
# The command must contain a single %s, which is replaced with URL.
BROWSERS = {
    'x': 'xdg-open %s > /dev/null', # system default browser
    'f': 'firefox -new-tab %s > /dev/null',
    'd': 'dwb %s',
    'c': 'google-chrome %s',
    't': 'torbrowser %s > /dev/null',
}
DEFAULT_BROWSER = 'x'


# Account Recognition {{{1
# Title Recognition
# Build up the regular expression used to recognize the various component of 
# the window title.
def labelRegex(label, regex):
    return "(?P<%s>%s)" % (label, regex)
HOST_REGEX = r'(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z0-9]+'
EMAIL_REGEX = r'[a-zA-Z0-9\-]+@' + HOST_REGEX
REGEX_COMPONENTS = {
    # If you add new components, you must also add code that handles the
    # component in accounts.py.
    'title': labelRegex('title', r'.*'),
    'host': labelRegex('host', HOST_REGEX),
    'protocol': labelRegex('protocol', r'\w+'),
    'browser': labelRegex('browser', r'\w+'),
    'username': labelRegex('username', r'\w+'),
    'email': labelRegex('email', EMAIL_REGEX)
}

# Required protocols (protocals that must be present in url if specified in
# account
REQUIRED_PROTOCOLS = ['https']

# Hostname in Titlebar browser title regex
HNITB_BROWSER_TITLE_PATTERN = re.compile(
    r'(?:{title} - )?{host} \({protocol}\)(?: - {browser})?'.format(
        **REGEX_COMPONENTS
    )
)

# This is for version 3 and beyond; requires that preferences in HNINTB be set 
# to 'show the short URL' with a separator of '-'.
HNITBv3_BROWSER_TITLE_PATTERN = re.compile(
    r'(?:{title} - ){protocol}?://{host}(?: - {browser})?'.format(
        **REGEX_COMPONENTS
    )
)
# Simple browser title regex
SIMPLE_BROWSER_TITLE_PATTERN = re.compile(
    r'{title}(?: - {browser})?'.format(**REGEX_COMPONENTS))
# Recognize components of the url
URL_PATTERN = re.compile(
    r'(?:{protocol}://)?{host}(?:/.*)?'.format(**REGEX_COMPONENTS))
TITLE_PATTERNS = [
    ('hostname-in-titlebar-browser-v3', HNITBv3_BROWSER_TITLE_PATTERN),
    #('hostname-in-titlebar-browser', HNITB_BROWSER_TITLE_PATTERN),
    # You can comment out the entry above if you are not using 'Hostname in
    # Titlebar' extension to Firefox and Thunderbird
    ('simple browser title', SIMPLE_BROWSER_TITLE_PATTERN)]

# Initial config file {{{1
CONFIG_FILE_INITIAL_CONTENTS = dedent('''\
    # Changing the contents of the dictionary, secrets, or charsets will change 
    # the secrets you generate, thus you do not want to change these files once 
    # you have started using the program. These are hashes for the contents of 
    # these files at the time that this file was created. The program will 
    # complain if the current contents of these files generate a different 
    # hash. Only update these hashes if you know what you are doing.
    dict_hash = '{dict_hash}'      # DO NOT CHANGE THIS LINE
    secrets_hash = '{secrets_hash}'   # DO NOT CHANGE THIS LINE
    charsets_hash = '{charsets_hash}'  # DO NOT CHANGE THIS LINE

    # List of the files that contain account information
    accounts_files = ['{accounts_file}']

    # The desired location of the log file (relative to config directory).
    # Adding a suffix of .gpg or .asc causes the file to be encrypted 
    # (otherwise it can leak account names). Use None to disable logging.
    log_file = '{log_file}'

    # The desired location of the archive file (relative to config directory 
    # and end the path in .gpg). Use None to disable archiving.
    archive_file = '{archive_file}'

    # Information used by GPG when encrypting and decrypting files.
    gpg_id = '{gpg_id}'
    gpg_home = '{gpg_home}'
    gpg_path = '{gpg_path}'

    # vim: filetype=python sw=4 sts=4 et ai ff=unix :
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

    from textwrap import dedent
    from avendesora.charsets import (
        exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
        HEXDIGITS, PUNCTUATION, WHITESPACE, PRINTABLE, DISTINGUISHABLE
    )
    from avendesora.utilities import (
        gethostname, getusername, Autotype, Hidden
    )
    from avendesora.account import Account
    from avendesora.secrets import (
        Password, Passphrase, PIN, BirthDate, SecurityQuestions
    )
    from avendesora.recognizers import (
        RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
        RecognizeHost, RecognizeUser, RecognizeEnvVar
    )

    master_password = Hidden("""{master_password}""")

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

# Fields {{{1
# Do not change these (not user configurable)
SEARCH_FIELDS = ['username', 'account', 'email', 'url', 'remarks']
STRING_FIELDS = [
    'alphabet', 'autotype', 'email', 'master', 'prefix',
    'remarks', 'separator', 'suffix', 'template', 'type',
    'username', 'version'
]
INTEGER_FIELDS = ['num-chars', 'num-words']
LIST_FIELDS = ['security questions', 'aliases']
LIST_OR_STRING_FIELDS = ['account', 'window', 'url']
ENUM_FIELDS = {
    'password-type': ['words', 'chars']
}
ALL_FIELDS = (
    STRING_FIELDS + INTEGER_FIELDS + LIST_FIELDS + LIST_OR_STRING_FIELDS +
    [each for each in ENUM_FIELDS.keys()]
)
