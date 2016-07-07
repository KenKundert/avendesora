# Read or write possibly encrypted python code fileS

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
from shlib import to_path
from inform import debug, display, fatal, narrate, os_error
from .preferences import (
    SETTINGS_DIR, DEFAULT_ACCOUNTS_FILENAME, DEFAULT_LOG_FILENAME, 
    DEFAULT_ARCHIVE_FILENAME
)

# AccountsFile class {{{1
class AccountFile:
    def __init__(self, path, gpg, generator, init=None, contents=''):
        path = to_path(path)
        try:
            to_path(SETTINGS_DIR).mkdir(parents=True, exist_ok=True)
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
                    gpg.save(to_path(path), code)
                else:
                    narrate('not encrypting.', culprit=path)
                    # file is not encrypted
                    with path.open('w') as f:
                        f.write(code)
            else:
                # read the file
                if path.suffix in ['.gpg', '.asc']:
                    # file is encrypted, decrypt it
                    code = gpg.read(to_path(path))
                else:
                    # file is not encrypted
                    code = path.read_text()
        except OSError as exception:
            fatal(os_error(exception))

        contents = {}
        compiled = compile(code, str(path), 'exec')
        exec(compiled, contents)
        if 'master_password' in contents:
            generator.add_missing_master(contents['master_password'])
        self.contents = contents

    def __getattr__(self, name):
        return self.contents[name]
