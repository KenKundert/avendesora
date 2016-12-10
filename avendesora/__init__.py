from .charsets import (
    exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
    HEXDIGITS, PUNCTUATION, SYMBOLS, WHITESPACE, PRINTABLE, DISTINGUISHABLE
)
from .account import Account, StealthAccount
from .secrets import (
    Password, Passphrase, PIN, Question, MixedPassword, PasswordRecipe,
    BirthDate,
)
from .obscure import Hidden, GPG
try:
    from .obscure import Scrypt
except ImportError:
    pass
from .recognize import (
    RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
    RecognizeHost, RecognizeUser, RecognizeEnvVar
)
from .generator import PasswordGenerator
from inform import Error
__version__ = '0.14.8'
