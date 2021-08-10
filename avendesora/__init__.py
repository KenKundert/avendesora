from .account import Account, StealthAccount
from .charsets import (
    exclude, LOWERCASE, UPPERCASE, LETTERS, DIGITS, ALPHANUMERIC,
    HEXDIGITS, PUNCTUATION, SYMBOLS, WHITESPACE, PRINTABLE, DISTINGUISHABLE
)
from .error import PasswordError
from .generator import PasswordGenerator
from .obscure import Hide, Hidden, GPG
from .file import WriteFile
try:
    from .obscure import Scrypt
except ImportError:  # pragma: no cover
    pass
try:
    from .otp import OTP
except ImportError:  # pragma: no cover
    pass
from .recognize import (
    RecognizeAll, RecognizeAny, RecognizeTitle, RecognizeURL, RecognizeCWD,
    RecognizeHost, RecognizeUser, RecognizeEnvVar, RecognizeNetwork,
    RecognizeFile
)
from .script import Script
from .secrets import (
    Password, Passphrase, PIN, Question, MixedPassword, PasswordRecipe,
    BirthDate, SecretExhausted
)

# the following are used when generating the documentation and are not needed
# otherwise
from . import command
from .account import AccountValue

__version__ = '1.21.0'
__released__ = '2021-08-09'
