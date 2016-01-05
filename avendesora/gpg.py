#
# INTERFACE TO GNUPG PACKAGE
#

from scripts import chmod, exists, fopen, join
from messenger import display, error, fatal, is_collection
from .preferences import GPG_PATH, GPG_HOME, GPG_ARMOR
import gnupg
import io


class GPG:
    def __init__(self,
        gpg_id=None, gpg_path=None, gpg_home=None, armor=None
    ):
        self.gpg_id = gpg_id if gpg_id else self._guess_id()
        self.gpg_path = gpg_path if gpg_path else GPG_PATH
        self.gpg_home = join(gpg_home if gpg_path else GPG_HOME)
        self.armor = armor if armor is not None else GPG_ARMOR

        gpg_args = {}
        if self.gpg_path:
            gpg_args.update({'gpgbinary': self.gpg_path})
        if self.gpg_home:
            gpg_args.update({'gnupghome': self.gpg_home})
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
            with fopen(path, 'w') as f:
                f.write(str(encrypted))
            chmod(0o600, path)

    def read(self, path):
        with fopen(path, 'rb') as f:
            decrypted = self.gpg.decrypt_file(f)
            if not decrypted.ok:
                fatal('unable to decrypt.', decrypted.stderr, culprit=path, sep='\n')
        return decrypted.data

    def open(self, path):
        self.path = path
        if is_collection(path):
            self.path = join(*path)
        self.stream = io.StringIO()
        return self.stream

    def close(self):
        contents = self.stream.getvalue()
        self.save(self.path, contents)
