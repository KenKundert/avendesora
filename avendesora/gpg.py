#
# INTERFACE TO GNUPG PACKAGE
#

from .preferences import GPG_PATH, GPG_HOME, GPG_ARMOR
from messenger import display, error, fatal, is_collection
from shlib import Path
import gnupg
import io


class GPG:
    def __init__(self,
        gpg_id=None, gpg_path=None, gpg_home=None, armor=None
    ):
        self.gpg_id = gpg_id if gpg_id else self._guess_id()
        self.gpg_path = Path(gpg_path if gpg_path else GPG_PATH)
        self.gpg_home = Path(gpg_home if gpg_path else GPG_HOME).expanduser()
        self.armor = armor if armor is not None else GPG_ARMOR

        gpg_args = {}
        if self.gpg_path:
            gpg_args.update({'gpgbinary': str(self.gpg_path)})
        if self.gpg_home:
            gpg_args.update({'gnupghome': str(self.gpg_home)})
        self.gpg = gnupg.GPG(**gpg_args)

    def update_id(self, gpg_id):
        self.gpg_id = gpg_id

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
        encrypted = self.gpg.encrypt(contents, self.gpg_id, armor=self.armor)
        if not encrypted.ok:
            fatal('unable to encrypt.', encrypted.stderr, culprit=path, sep='\n')
        else:
            if self.armor:
                path.write_text(str(encrypted))
            else:
                path.write_bytes(encrypted)
            path.chmod(0o600)

    def read(self, path):
        with path.open('rb') as f:
            decrypted = self.gpg.decrypt_file(f)
            if not decrypted.ok:
                fatal('unable to decrypt.', decrypted.stderr, culprit=path, sep='\n')
        return decrypted.data

    def open(self, path):
        self.path = path
        self.stream = io.StringIO()
        return self.stream

    def close(self):
        contents = self.stream.getvalue()
        self.save(self.path, contents)
