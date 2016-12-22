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
from shlib import to_path, mv, mkdir
from inform import (
    conjoin, cull, display, Error, log, narrate, os_error, warn, is_str,
    full_stop
)
import gnupg
try:
    from StringIO import StringIO   # python2
except ImportError:
    from io import StringIO         # python3

# Globals {{{1
GPG_EXTENSIONS = ['.gpg', '.asc']
ARMOR_CHOICES = ['always', 'never', 'extension']
ActiveFile= None

# get_active_file() {{{1
def get_active_file():
    return ActiveFile

# GnuPG class {{{1
class GnuPG(object):
    def __init__(self, path):
        self.path = to_path(path)

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
                "'%s' is not valid, choose from %s." % (
                    armor, conjoin(ARMOR_CHOICES)
                ), culprit=(get_setting('config_file'), 'gpg_armor')
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

    def save(self, contents, gpg_ids=None):
        path = self.path
        if not gpg_ids:
            gpg_ids = get_setting('gpg_ids', [])
        if is_str(gpg_ids):
            gpg_ids = gpg_ids.split()
        if not gpg_ids:
            raise Error('must specify GPG ID.')

        use_gpg, use_armor = self._choices()
        if use_gpg:
            try:
                encoded = contents.encode(get_setting('encoding'))
                encrypted = self.gpg.encrypt(encoded, gpg_ids, armor=use_armor)
                if not encrypted.ok:
                    msg = ' '.join(cull([
                        'unable to encrypt.',
                        getattr(encrypted, 'stderr', None)
                    ]))
                    raise Error(msg, culprit=path, sep='\n')
                else:
                    path.write_bytes(encrypted.data)
            except ValueError as err:
                raise Error(full_stop(err), culprit=path)
        else:
            path.write_text(contents, encoding=get_setting('encoding'))
        path.chmod(0o600)

    def read(self):
        path = self.path
        # file is only assumed to be encrypted if path has gpg extension
        if path.suffix.lower() in GPG_EXTENSIONS:
            try:
                with path.open('rb') as f:
                    decrypted = self.gpg.decrypt_file(f)
                    if not decrypted.ok:
                        msg = ' '.join(cull([
                            'unable to decrypt.',
                            getattr(decrypted, 'stderr', None)
                        ]))
                        raise Error(msg, culprit=path, sep='\n')
            except ValueError as err:
                raise Error(full_stop(err), culprit=path)
            except (IOError, OSError) as err:
                raise Error(os_error(err))
            return decrypted.data.decode(get_setting('encoding'))
        else:
            return path.read_text(encoding=get_setting('encoding'))

    def _choices(self):
        extension = self.path.suffix.lower()
        if extension in GPG_EXTENSIONS:
            if self.armor == 'never':
                return True, False
            elif self.armor != 'always' and extension == '.gpg':
                return True, False
            return True, True
        else:
            return False, False

    def remove(self):
        self.path.unlink()

    def rename(self, extension):
        new = to_path(str(self.path) + extension)
        mv(self.path, new)
        self.path = new

    def will_encrypt(self):
        return self.path.suffix in GPG_EXTENSIONS


# BufferedFile class {{{1
class BufferedFile(GnuPG):
    def __init__(self, path, ignore_errors_on_close=False):
        # file will only be encrypted if path has gpg extension
        self.path = path
        self.stream = StringIO()
        self.ignore_errors_on_close = ignore_errors_on_close

    def write(self, content):
        self.stream.write(content)

    def flush(self):
        pass

    def close(self):

        if get_setting('discard_logfile'):
            # this is the case when the output would be uninteresting (such as
            # with help messages) and running GPG (and thus risk requiring the
            # user to type in the passphrase) is silly.
            return
        contents = self.stream.getvalue()
        try:
            self.save(contents, get_setting('gpg_ids'))
        except Error:
            if not self.ignore_errors_on_close:
                raise


# PythonFile class {{{1
class PythonFile(GnuPG):
    def run(self):
        global ActiveFile
        ActiveFile = self.path
        path = self.path
        self.encrypted = path.suffix in ['.gpg', '.asc']
        log('reading.', culprit=path)
        try:
            self.code = self.read()
                # need to save the code for the new command
        except OSError as err:
            raise Error(os_error(err))

        try:
            compiled = compile(self.code, str(path), 'exec')
        except SyntaxError as err:
            culprit = (err.filename, err.lineno)
            if err.text is None or err.offset is None:
                raise Error(full_stop(err.msg), culprit=culprit)
            else:
                raise Error(
                    err.msg + ':', err.text, (err.offset-1)*' ' + '^',
                    culprit=culprit, sep='\n'
                )
                # File "/home/ken/.config/avendesora/config", line 18
                #   'c': 'google-chrome %s'
                #      ^

        contents = {}
        try:
            exec(compiled, contents)
        except Exception as err:
            from .utilities import error_source
            raise Error(full_stop(err), culprit=error_source())
        ActiveFile = None
        return contents

    def create(self, contents, gpg_ids):
        path = self.path
        try:
            mkdir(get_setting('settings_dir'))
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
                self.save(contents, gpg_ids)
            else:
                narrate('not encrypting.', culprit=path)
                # file is not encrypted
                with path.open('wb') as f:
                    f.write(contents.encode(get_setting('encoding')))
        except OSError as err:
            raise Error(os_error(err))

    def exists(self):
        return self.path.exists()

    def __str__(self):
        return str(self.path)
