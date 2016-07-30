#
# INTERFACE TO GNUPG PACKAGE
#
# Package for reading and writing text files that may or may not be encrypted.
# File will be encrypted if file path ends in a GPG extension.

# License {{{1
# Copyright (C) 2016 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from .config import get_setting, override_setting
from shlib import to_path
from inform import display, Error, error, fatal, log, narrate, os_error, is_str
import gnupg
import io

# Globals {{{1
GPG_EXTENSIONS = ['.gpg', '.asc']
ARMOR_CHOICES = ['always', 'never', 'extension']


# GnuPG class {{{1
class GnuPG:
    def __init(self):
        # This class acts as a singleton by just using class methods
        raise NotImplementedError

    @classmethod
    def initialize(cls,
        gpg_path=None, gpg_home=None, armor=None
    ):
        from .config import get_setting, override_setting

        cls.gpg_path = to_path(
            gpg_path if gpg_path else get_setting('gpg_executable')
        )
        override_setting('gpg_executable', cls.gpg_path)

        cls.gpg_home = to_path(
            gpg_home if gpg_home else get_setting('gpg_home')
        )
        override_setting('gpg_home', cls.gpg_home)

        armor = armor if armor is not None else get_setting('gpg_armor')
        if armor not in ARMOR_CHOICES:
            warn(
                "'%s' is not valid, choose from %s." % conjoin(ARMOR_CHOICES),
                culprit=get_setting('config_file')
            )
            armor = None
        cls.armor = armor
        override_setting('gpg_armor', armor)

        gpg_args = {}
        if cls.gpg_path:
            gpg_args.update({'gpgbinary': str(cls.gpg_path)})
        if cls.gpg_home:
            gpg_args.update({'gnupghome': str(cls.gpg_home)})
        cls.gpg = gnupg.GPG(**gpg_args)

    @classmethod
    def _guess_id(cls):
        import socket, getpass
        username = getpass.getuser()
        hostname = socket.gethostname().split('.')
        if len(hostname) <= 2:
            hostname = '.'.join(hostname)
        else:
            # strip off name of local machine
            hostname = '.'.join(hostname[1:])
        return username + '@' + hostname

    @classmethod
    def save_encrypted(cls, path, contents, gpg_ids=None):
        encoded = contents.encode(get_setting('encoding'))
        if not gpg_ids:
            gpg_ids = get_setting('gpg_ids', [])
        if not gpg_ids:
            raise Error('must specify GPG ID.')

        use_gpg, use_armor = cls.make_choices(path)
        if use_gpg:
            try:
                encrypted = cls.gpg.encrypt(encoded, gpg_ids, armor=use_armor)
                if not encrypted.ok:
                    raise Error(
                        'unable to encrypt.', encrypted.stderr,
                        culprit=path, sep='\n'
                    )
                else:
                    if use_armor:
                        path.write_text(str(encrypted))
                    else:
                        path.write_bytes(encrypted.data)
                    path.chmod(0o600)
            except ValueError as err:
                raise Error(str(err), culprit=path)
        else:
            path.write_text(encoded)

    @classmethod
    def read_encrypted(cls, path):
        # file is only assumed to be encrypted if path has gpg extension
        if path.suffix.lower() in GPG_EXTENSIONS:
            with path.open('rb') as f:
                try:
                    decrypted = cls.gpg.decrypt_file(f)
                    if not decrypted.ok:
                        fatal('unable to decrypt.', decrypted.stderr, culprit=path, sep='\n')
                except ValueError as err:
                    raise Error(str(err), culprit=path)
            return decrypted.data.decode(get_setting('encoding'))

        else:
            return path.read_text().decode(get_setting('encoding'))

    @classmethod
    def make_choices(cls, path):
        extension = path.suffix.lower()
        if extension in GPG_EXTENSIONS:
            if cls.armor == 'never':
                return True, False
            elif cls.armor != 'always' and extension == '.gpg':
                return True, False
            return True, True
        else:
            return False, False

# BufferedFile class {{{1
class BufferedFile(GnuPG):
    def __init__(self, path):
        # file will only be encrypted if path has gpg extension
        self.path = path
        self.stream = io.StringIO()

    def write(self, content):
        self.stream.write(content)

    def flush(self):
        pass

    def close(self):
        contents = self.stream.getvalue()
        self.save_encrypted(self.path, contents, get_setting('gpg_ids'))


# PythonFile class {{{1
class PythonFile(GnuPG):
    def __init__(self, path, contents=None):
        self.path = to_path(path)

    def read(self):
        path = self.path
        self.encrypted = path.suffix in ['.gpg', '.asc']
        log('reading.', culprit=path)
        try:
            if self.encrypted:
                # file is encrypted, decrypt it
                code = self.read_encrypted(to_path(path))
            else:
                # file is not encrypted
                code = path.read_text()
        except OSError as err:
            raise Error(os_error(err))

        contents = {}
        try:
            compiled = compile(code, str(path), 'exec')
        except SyntaxError as err:
            fatal(
                err.msg + ':', err.text, (err.offset-1)*' ' + '^',
                culprit=(err.filename, err.lineno), sep='\n'
            )
            # File "/home/ken/.config/avendesora/config", line 18
            #   'g': 'google-chrome %s'
            #      ^

        exec(compiled, contents)
        self.contents = contents
        return contents

    def create(self, contents, gpg_ids):
        path = self.path
        try:
            to_path(get_setting('settings_dir')).mkdir(parents=True, exist_ok=True)
            if path.exists():
                # file creation (init) requested, but file already exists
                # don't overwrite the file, instead read it so the information 
                # can be used to create any remaining files.
                display("%s: already exists." % path)
                return
            # create the file
            display('%s: creating.' % path)
            if path.suffix in ['.gpg', '.asc']:
                narrate('encrypting.', culprit=path)
                # encrypt it
                self.save_encrypted(to_path(path), contents, gpg_ids)
            else:
                narrate('not encrypting.', culprit=path)
                # file is not encrypted
                with path.open('w') as f:
                    f.write(contents)
        except OSError as err:
            raise Error(os_error(err))

    def __str__(self):
        return str(self.path)
