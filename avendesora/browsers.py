# Browsers
#
# Implement browser access

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
from .preferences import BROWSERS, DEFAULT_BROWSER
from shlib import Run
from inform import error, log


# Browser base class {{{1
class Browser:
    pass


# StandardBrowser class {{{1
class StandardBrowser(Browser):
    def __init__(self, name=None, cmd=None):
        self.name = name if name else DEFAULT_BROWSER
        self.cmd = cmd

    def run(self, url, name=None):
        name = name if name else self.name
        if url:
            if '://' not in url:
                url = 'https://' + url
            try:
                cmd = self.cmd if self.cmd else BROWSERS[name]
                try:
                    cmd = cmd % url
                except TypeError:
                    pass
                log("running '%s'" % cmd)
                Run(cmd, 'sOew')
            except KeyError:
                error('unknown browser, choose from %s.' % (
                    name, ', '.join(BROWSERS)
                ))
            except OSError as err:
                error(os_error(err))
        else:
            error('url not available.')
