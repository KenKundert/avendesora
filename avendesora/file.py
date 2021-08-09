# Write File that Contains Secret
#
# Create or update a file that contains information contains within Avendesora.

# License {{{1
# Copyright (C) 2016-2021 Kenneth S. Kundert
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
from .error import PasswordError
from .shlib import to_path
from inform import os_error


# WriteFile {{{1
class WriteFile():
    """Write a text file containing a secret.


    Args:
        path (str):
            A path to the file that is to be written.
        contents (str or secret):
            The desired contents of the file.
    """

    def __init__(self, path, contents, mode=0o0600):
        self.path = path
        self.contents = contents
        self.mode = mode

    def render(self):
        try:
            contents = self.contents.render()
        except AttributeError:
            contents = self.contents
        try:
            path = to_path(self.path)
            path.write_text(contents)
            path.chmod(self.mode)
        except OSError as e:
            raise PasswordError(os_error(e))

        return 'Contents written to {}.'.format(str(path))

    # __repr__() {{{2
    def __repr__(self):
        return "WriteFile('{!s}', contents={!r})".format(
            self.path, self.contents
        )

    # __str__() {{{2
    def __str__(self):
        return self.render()
