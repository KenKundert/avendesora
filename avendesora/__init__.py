from .charsets import (
    exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
    HEXDIGITS, PUNCTUATION, SYMBOLS, WHITESPACE, PRINTABLE, DISTINGUISHABLE
)
from .account import Account, StealthAccount, Script
from .secrets import (
    Password, Passphrase, PIN, Question, MixedPassword, PasswordRecipe,
    BirthDate,
)
from .obscure import Hide, Hidden, GPG
try:
    from .obscure import Scrypt
except ImportError:  # no cover
    pass
from .recognize import (
    RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
    RecognizeHost, RecognizeUser, RecognizeEnvVar, RecognizeNetwork,
)
from .generator import PasswordGenerator
from inform import Error as PasswordError

__version__ = '0.18.0'
__released__ = '2016-12-27'
