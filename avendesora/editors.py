# Editors
#
# Open and editor on a file.

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from .config import get_setting, setting_path
from .error import PasswordError
from .shlib import Run
from inform import Error


# Editor base class {{{1
class Editor(object):
    pass


# GenericEditor class {{{1
class GenericEditor(Editor):
    NAME = 'generic'

    @classmethod
    def run(cls, filepath, account = None):
        args = dict(
            filepath = filepath,
            account = account,
        )
        try:
            editor_setting = 'edit_account' if account else 'edit_template'
            cmd = get_setting(editor_setting)
            cmd = [e.format(**args) for e in cmd]

            try:
                Run(cmd, 'soEW')
            except Error as e:
                e.reraise(culprit=cmd[0])
        except KeyError as e:
            raise PasswordError(
                *e.args,
                template='invalid field: {0}',
                culprit=setting_path(editor_setting)
            )
