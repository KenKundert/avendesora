# File
# Read or write possibly encrypted python code files

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
from .preferences import (
    SETTINGS_DIR, DEFAULT_ACCOUNTS_FILENAME, DEFAULT_LOG_FILENAME, 
    DEFAULT_ARCHIVE_FILENAME
)
from shlib import to_path
from inform import debug, display, Error, fatal, log, narrate, os_error

# File class {{{1
class File:
    def __init__(self, path, gpg=None, contents=None):
        self.path = to_path(path)
        self.gpg = gpg

    def read(self):
        path = self.path
        self.encrypted = path.suffix in ['.gpg', '.asc']
        log('reading.', culprit=path)
        try:
            if self.encrypted:
                # file is encrypted, decrypt it
                code = self.gpg.read(to_path(path))
            else:
                # file is not encrypted
                code = path.read_text()
        except OSError as err:
            raise Error(os_error(err))

        contents = {}
        compiled = compile(code, str(path), 'exec')
        exec(compiled, contents)
        self.contents = contents
        return contents

    def create(self, contents):
        path = self.path
        try:
            to_path(SETTINGS_DIR).mkdir(parents=True, exist_ok=True)
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
                self.gpg.save(to_path(path), contents)
            else:
                narrate('not encrypting.', culprit=path)
                # file is not encrypted
                with path.open('w') as f:
                    f.write(contents)
        except OSError as err:
            raise Error(os_error(err))

