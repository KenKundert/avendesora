from binascii import a2b_base64, b2a_base64, Error
from inform import error, is_str, log

# gethostname {{{1
# returns short version of the hostname (the hostname without any domain name)
import socket
def gethostname():
    return socket.gethostname().split('.')[0]

# getusername {{{1
import getpass
def getusername():
    return getpass.getuser()

# RecognizeURL {{{1
class RecognizeURL():
    def __init__(self, *args, **kwargs):
        pass
    def _initiate(self, name, account):
        log('        initializing RecognizeURL(%s)' % account.get_name())

# Autotype {{{1
class Autotype():
    def __init__(self, *args, **kwargs):
        pass
    def _initiate(self, name, account):
        log('        initializing Autotype(%s)' % account.get_name())

# Hidden {{{1
import linecache
import sys

class Hidden():
    def __init__(self, value, **kwargs):
        try:
            value = a2b_base64(value)
            self.value = value.decode(kwargs.get('encoding', 'utf8'))
        except Error as err:
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            filename, lineno = traceback.extract_stack()[-2][:2]
                # context and content are also available, but in this case
                # Hidden is generally instantiated from top-level so the 
                # context is not interesting and the content (the actual line 
                # of code) shown in this case is gibberish (encrypted).
            error(
                'invalid value specified to Hidden().',
                culprit=(filename, lineno)
            )

    def _initiate(self, name, account):
        log('        initializing Hidden(%s)' % account.get_name())

    def __str__(self):
        return self.value

    @staticmethod
    def hide(value, **kwargs):
        value = value.encode(kwargs.get('encoding', 'utf8'))
        return b2a_base64(value).rstrip().decode('ascii')

    @staticmethod
    def reveal(value, **kwargs):
        value = a2b_base64(value.encode('ascii'))
        return value.decode(kwargs.get('encoding', 'utf8'))

