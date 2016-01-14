#
# READ or WRITE POSSIBLY ENCRYPTED PYTHON CODE FILES
#

from __future__ import print_function
from shlib import Path, mkdir
from messenger import display, error, narrate, debug, os_error
from .preferences import (
    SETTINGS_DIR, DEFAULT_ACCOUNTS_FILENAME, DEFAULT_LOG_FILENAME, 
    DEFAULT_ARCHIVE_FILENAME
)

class AccountFile:
    def __init__(self, path, gpg, generator, init=None, contents=''):
        path = Path(path).expanduser()
        try:
            mkdir(Path(SETTINGS_DIR).expanduser())
            if init and path.exists():
                display("%s: already exists." % path)
                # file creation (init) requested, but file already exists
                # don't overwrite the file, instead read it so the information 
                # can be used to create any remaining files.
            if init and not path.exists():
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
                if path.suffix in ['.gpg', '.asc']:
                    narrate('encrypting.', culprit=path)
                    # encrypt it
                    gpg.save(Path(path), code)
                else:
                    narrate('not encrypting.', culprit=path)
                    # file is not encrypted
                    with path.open('w') as f:
                        f.write(code)
            else:
                # read the file
                if path.suffix in ['.gpg', '.asc']:
                    # file is encrypted, decrypt it
                    code = gpg.read(Path(path))
                else:
                    # file is not encrypted
                    code = path.read_text()
        except OSError as exception:
            error(os_error(exception))

        contents = {}
        compiled = compile(code, str(path), 'exec')
        exec(compiled, contents)
        if 'master_password' in contents:
            generator.add_missing_master(contents['master_password'])
        self.contents = contents

    def __getattr__(self, name):
        return self.contents[name]
