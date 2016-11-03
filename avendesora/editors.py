# Avendesora Password Generator Preferences
#
# Copyright (C) 2016 Kenneth S. Kundert

# License {{{1
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
from .config import get_setting, add_setting
from shlib import Run
from inform import log, Error

# Editor base class {{{1
class Editor(object):
    pass

# GenericEditor class {{{1
class GenericEditor(Editor):
    NAME = 'generic'

    @classmethod
    def open_and_search(cls, filepath, account = None):
        args = {
            'filepath': filepath,
            'account': account,
            'section': '{' '{' '{' '1',
        }
        try:
            editor_setting = 'edit_account' if account else 'edit_template'
            cmd = get_setting(editor_setting)
            cmd = [e.format(**args) for e in cmd]

            log("running '%s'." % ' '.join(cmd))
            Run(cmd, 'soeW')
        except OSError as err:
            raise Error(os_error(err))
        except KeyError as err:
            raise Error('invalid field: %s.' % err, culprit=editor_setting)
