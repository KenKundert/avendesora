#
# INTERFACE TO GNUPG PACKAGE
#
# Package for reading and writing text files that may or may not be encrypted.
# File will be encrypted if file path ends in a GPG extension.

from .config import get_setting, override_setting
from inform import debug, display, fatal, is_collection
from shlib import to_path
import gnupg
import io
GPG_EXTENSIONS = ['.gpg', '.asc']


class GnuPG:
    __shared_state = {}

    def __init__(self,
        gpg_id=None, gpg_path=None, gpg_home=None, armor=None
    ):
        if not gpg_id:
            gpg_id = get_setting('gpg_id')
        if not gpg_id:
            gpg_id = self._guess_id()
        self.gpg_id = gpg_id
        override_setting('gpg_id', gpg_id)

        self.gpg_path = to_path(
            gpg_path if gpg_path else get_setting('gpg_executable')
        )
        override_setting('gpg_path', self.gpg_path)

        self.gpg_home = to_path(
            gpg_home if gpg_home else get_setting('gpg_home')
        )
        override_setting('gpg_home', self.gpg_home)

        self.armor = armor if armor is not None else get_setting('gpg_armor')
        override_setting('gpg_armor', self.armor)

        gpg_args = {}
        if self.gpg_path:
            gpg_args.update({'gpgbinary': str(self.gpg_path)})
        if self.gpg_home:
            gpg_args.update({'gnupghome': str(self.gpg_home)})
        self.gpg = gnupg.GPG(**gpg_args)

    def _guess_id(self):
        import socket, getpass
        username = getpass.getuser()
        hostname = socket.gethostname().split('.')
        if len(hostname) <= 2:
            hostname = '.'.join(hostname)
        else:
            # strip off name of local machine
            hostname = '.'.join(hostname[1:])
        return username + '@' + hostname

    def save(self, path, contents):
        if path.suffix.lower() in GPG_EXTENSIONS:
            encrypted = self.gpg.encrypt(contents, self.gpg_id, armor=self.armor)
            if not encrypted.ok:
                fatal('unable to encrypt.', encrypted.stderr, culprit=path, sep='\n')
            else:
                if self.armor:
                    path.write_text(str(encrypted))
                else:
                    path.write_bytes(encrypted)
                path.chmod(0o600)
        else:
            path.write_text(contents)

    def read(self, path):
        # file is only assumed to be encrypted if path has gpg extension
        if path.suffix.lower() in GPG_EXTENSIONS:
            with path.open('rb') as f:
                decrypted = self.gpg.decrypt_file(f)
                if not decrypted.ok:
                    fatal('unable to decrypt.', decrypted.stderr, culprit=path, sep='\n')
            return decrypted.data
        else:
            return path.read_text()

    def open(self, path):
        # file will only be encrypted if path has gpg extension
        self.path = path
        self.stream = io.StringIO()
        return self.stream

    def close(self):
        contents = self.stream.getvalue()
        self.save(self.path, contents)
