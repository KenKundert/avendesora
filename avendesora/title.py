# Window Titles
#
# Get and parse window title strings.
# KSK
# perhaps a better way of handling this is to use title.split(' - ') and then
# focus and then recombine the initial ones to end up with three: title, url,
# browser.
# Also AddURLToWindowTitle no longer seems to output the host.

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
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
from .shlib import Run
from inform import log, Error
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import re


# Regular expressions {{{1
def labelRegex(label, regex):
    return "(?P<%s>%s)" % (label, regex)

URL_REGEX = r'[^ ]+://[^ ]+'
HOST_REGEX = r'(?:[^ ]+://)?[^ ]+'
REGEX_COMPONENTS = {
    'title': labelRegex('title', r'.*'),
    'url': labelRegex('url', URL_REGEX),
    'host': labelRegex('host', URL_REGEX),
    'browser': labelRegex('browser', r'[\w ()]+'),
}


# Title base class {{{1
class Title(object):
    def __init__(self, url=None, override=None):
        if url:
            self.data = self._process_url(url)
            return
        if override:
            title = override
        else:
            xdotool = get_setting('xdotool_executable')
            if not xdotool:
                raise PasswordError(
                    "must set xdotool_executable'.",
                    culprit=setting_path('xdotool_executable')
                )
            cmd = [xdotool, 'getactivewindow', 'getwindowname']
            try:
                output = Run(cmd, 'sOEW')
            except Error as e:
                e.reraise(culprit=xdotool)
            title = output.stdout.strip()
        log('Focused window title:\n    %s' % title)
        data = {'rawtitle': title}
        for sub in sorted(Title.__subclasses__(), key=lambda c: c.PRIORITY):
            matched = sub._process(title, data)
            log('%s: %s.' % (sub.__name__, 'matched' if matched else 'no match'))
            if matched:
                break

        # log the components of the title
        log('Recognized title components;')
        for k, v in data.items():
            log('    %s: %s' % (k, v))

        self.data = data

    def get_data(self):
        return self.data

    @classmethod
    def _process(cls, title, data):
        match = cls.PATTERN.match(title)
        if match:
            found = match.groupdict()
            if 'url' in found:
                components = cls._process_url(found['url'])
                if components:
                    data.update(found)
                    data.update(components)
                    return True

    @staticmethod
    def _process_url(url):
        components = urlparse(url)
        if components.netloc:
            return dict(
                protocol = components.scheme,
                host = components.netloc,
                path = components.path,
                fragment = components.fragment,
            )


# AddURLToWindowTitle (Firefox) {{{1
class AddURLToWindowTitle(Title):
    # This matches the default pattern produced by AddURLToWindowTitle in
    # Firefox, though sometimes it outputs the host, and sometimes it does not.
    PATTERN = re.compile(
        r'\A{title}- {url} - (?:{host} - )?{browser}\Z'.format(**REGEX_COMPONENTS)
    )
    PRIORITY = 1


# URLinTitle (Chrome) {{{1
class URLinTitle(Title):
    # This matches the default pattern produced by URLinTitle in Chrome
    # By default URLinTitle does not include path or args. Can change the
    # tab title format option to:
    #     {title} - {protocol}://{hostname}{port}/{path}{args}
    # to access these fields as well.
    PATTERN = re.compile(
        r'\A{title} - {url} - {browser}\Z'.format(**REGEX_COMPONENTS)
    )
    PRIORITY = 2
