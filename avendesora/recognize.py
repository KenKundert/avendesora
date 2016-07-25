# Account Recognizers
#
# Classes used in account discovery to recognize when a particular account
# should be used based on environmental conditions (window title, hostname,
# username, current directory, etc.)

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
from .utilities import gethostname, getusername
from shlib import cwd, to_path
from inform import error, log, warn, notify
from fnmatch import fnmatch
from urllib.parse import urlparse
import os

# Recognizer Base Class {{{1
class Recognizer:
    pass


# RecognizeAll {{{1
class RecognizeAll(Recognizer):
    def __init__(self, *recognizers, script=True):
        self.recognizers = recognizers
        self.script = script

    def match(self, data, account):
        if all([each.match(data, account) for each in self.recognizers]):
            return self.script


# RecognizeAny {{{1
class RecognizeAny(Recognizer):
    def __init__(self, *recognizers, script=True):
        self.recognizers = recognizers
        self.script = script

    def match(self, data, account):
        if Any([each.match(data, account) for each in self.recognizers]):
            return self.script


# RecognizeTitle {{{1
class RecognizeTitle(Recognizer):
    def __init__(self, *titles, script=True):
        self.titles = titles
        self.script = script

    def match(self, data, account):
        found = data.get('rawtitle')
        if found:
            for title in self.titles:
                if fnmatch(found, title):
                    return self.script


# RecognizeURL {{{1
class RecognizeURL(Recognizer):
    def __init__(self, *urls, script=True):
        self.urls = urls
        self.script = script

    def match(self, data, account):
        for url in self.urls:
            url = urlparse(url)
            protocol = url.scheme
            host = url.netloc
            path = url.path

            if host == data.get('host'):
                if not path or path == data.get('path'):
                    if (
                        protocol == data.get('protocol') or
                        protocol not in REQUIRED_PROTOCOLS
                    ):
                        return self.script
                    else:
                        msg = 'url matches, but uses wrong protocol.'
                        notify(msg)
                        error(msg, culprit=account.get_name())


# RecognizeCWD {{{1
class RecognizeCWD(Recognizer):
    def __init__(self, *dirs, script=True):
        self.dirs = dirs
        self.script = script

    def match(self, data, account):
        cwd = cwd()
        for directory in self.dirs:
            if cwd.samefile(to_path(directory)):
                return self.script


# RecognizeHost {{{1
class RecognizeHost(Recognizer):
    def __init__(self, *hosts, script=True):
        self.hosts = hosts
        self.script = script

    def match(self, data, account):
        hostname = gethostname()
        for host in self.hosts:
            if host == hostname:
                return self.script


# RecognizeUser {{{1
class RecognizeUser(Recognizer):
    def __init__(self, *users, script=True):
        self.users = users
        self.script = script

    def match(self, data, account):
        username = getusername()
        for user in self.users:
            if user == username:
                return self.script


# RecognizeEnvVar {{{1
class RecognizeEnvVar(Recognizer):
    def __init__(self, name, value, script=True):
        self.name = name
        self.value = value
        self.script = script

    def match(self, data, account):
        if name in os.environ and value == os.environ[name]:
            return self.script

