# Window Titles
#
# Get and parse window title strings.

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
from .config import get_setting
from shlib import Run
from inform import fatal, log
from urllib.parse import urlparse
import re


# Regular expressions {{{1
def labelRegex(label, regex):
    return "(?P<%s>%s)" % (label, regex)

URL_REGEX = r'(?:[^ ]+)://(?:[^ ]+)'
REGEX_COMPONENTS = {
    'title': labelRegex('title', r'.*'),
    'url': labelRegex('url', URL_REGEX),
    'host': labelRegex('host', URL_REGEX),
    'browser': labelRegex('browser', r'[\w ]+'),
}


# Title base class {{{1
class Title:
    def __init__(self, override=None):
        if override:
            title = override
        else:
            xdotool = get_setting('xdotool_executable')
            if not xdotool:
                fatal(
                    "must set xdotool_executable'.",
                    culprit=get_setting('config_file')
                )
            try:
                output = Run(
                    [xdotool, 'getactivewindow', 'getwindowname'],
                    'sOeW'
                )
            except OSError as err:
                fatal(str(err))
            title = output.stdout.strip()
        log('Focused window title: %s' % title)
        data = {'rawtitle': title}
        for sub in Title.__subclasses__():
            sub._process(title, data)

        # split the url into basic components if found
        url = data.get('url')
        if url:
            url = urlparse(url)
            data['protocol'] = url.scheme
            data['host'] = url.netloc
            data['path'] = url.path

        # log the components of the title
        log('Recognized title components ...')
        for k, v in data.items():
            log('    %s: %s' % (k, v))

        self.data = data

    def get_data(self):
        return self.data

    @classmethod
    def _process(cls, title, data):
        match = cls.pattern.match(title)
        if match:
            data.update(match.groupdict())


# AddURLToWindow class {{{1
class AddURLToWindow(Title):
    # This matches the default pattern produced by AddURLToWindow in Firefox
    # Also matches old HostNameInTitleBar in Firefox
    pattern = re.compile(
        r'\A{title} - {url} - {host} - {browser}\Z'.format(**REGEX_COMPONENTS)
    )
