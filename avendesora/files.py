#
# READ or WRITE POSSIBLY ENCRYPTED PYTHON CODE FILES
#

from __future__ import print_function
from scripts import exists, extension, fopen, join, mkdir, ScriptError
from messenger import display, error, narrate
from .preferences import (
    SETTINGS_DIR, DEFAULT_ACCOUNTS_FILENAME, DEFAULT_LOG_FILENAME, 
    DEFAULT_ARCHIVE_FILENAME
)

class AccountFile:
    def __init__(self, path, gpg, init=None, contents=''):
        try:
            mkdir(join(SETTINGS_DIR))
            if init and exists(path):
                display("%s: already exists." % path)
                # file creation (init) requested, but file already exists
                # don't overwrite the file, instead read it so the information 
                # can be used to create any remaining files.
            if init and not exists(path):
                # create the file
                code = contents.format(
                    dict_hash='not implemented yet',
                    secrets_hash='not implemented yet',
                    charsets_hash='not implemented yet',
                    accounts_file=DEFAULT_ACCOUNTS_FILENAME,
                    log_file=DEFAULT_LOG_FILENAME,
                    archive_file=DEFAULT_ARCHIVE_FILENAME,
                    gpg_id=gpg.gpg_id,
                    gpg_home='~/.gnupg',
                    gpg_path='/usr/bin/gpg2',
                    section='{''{''{''1',
                    master_password='not implemented yet',
                )
                display('%s: creating.' % path)
                if extension(path) in ['.gpg', '.asc']:
                    narrate('encrypting.', culprit=path)
                    # encrypt it
                    gpg.save(path, code)
                else:
                    narrate('not encrypting.', culprit=path)
                    # file is not encrypted
                    with fopen(path, 'w') as f:
                        f.write(code)
            else:
                # read the file
                if extension(path) in ['.gpg', '.asc']:
                    # file is encrypted, decrypt it
                    code = gpg.read(path)
                else:
                    # file is not encrypted
                    with fopen(path) as f:
                        code = f.read()
        except ScriptError as exception:
            error(str(exception))

        contents = {}
        compiled = compile(code, path, 'exec')
        exec(compiled, contents)
        self.contents = contents

    def __getattr__(self, name):
        return self.contents[name]
