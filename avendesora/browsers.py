# Browsers
#
# Implement browser access

# License {{{1
# Copyright (C) 2016-2024 Kenneth S. Kundert
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
from .config import get_setting, setting_path
from .error import PasswordError
from .shlib import Cmd
from inform import log


# Browser base class {{{1
class Browser(object):
    pass


# StandardBrowser class {{{1
class StandardBrowser(Browser):
    def __init__(self, name=None, cmd=None):
        self.name = name if name else get_setting('default_browser')
        self.cmd = cmd

    def run(self, url, name=None):
        name = name if name else self.name
        if url:
            if '://' not in url:
                url = 'https://' + url
            try:
                cmd = self.cmd if self.cmd else get_setting('browsers')[name]
            except KeyError:
                raise PasswordError("unknown browser, choose from %s." % (
                    ', '.join(get_setting('browsers', name))
                ), culprit=name)

            try:
                cmd = cmd.format(url=url)
            except TypeError:
                pass
            except KeyError as e:
                raise PasswordError(
                    'unknown key {%s}.  Choose from: {url}.' % e.args[0],
                    culprit=setting_path('browsers', name)
                )

            browser = Cmd(cmd, 'sOE')
                # capture both stdout and stderr because browsers are
                # notoriously noisy
            log("running '%s'" % str(browser))
            browser.start()
        else:
            raise PasswordError('URL not available from account.')
