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
from .utilities import flatten, gethostname, getusername, split
from shlib import cwd, to_path
from inform import Error, log, warn, notify
from fnmatch import fnmatch
from urllib.parse import urlparse
import os

# Recognizer Base Class {{{1
class Recognizer:
    def all_urls(self):
        urls = {}
        if hasattr(self, 'recognizers'):
            for each in self.recognizers:
                urls.update(each.all_urls())
        if hasattr(self, 'get_urls'):
            urls.update(self.get_urls())
        return urls

    def get_name(self):
        return self.__class__.__name__

# RecognizeAll {{{1
class RecognizeAll(Recognizer):
    def __init__(self, *recognizers, script=True):
        self.recognizers = recognizers
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            match = all([
                each.match(data, account, verbose) for each in self.recognizers
            ])
            if match:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.recognizers]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeAny {{{1
class RecognizeAny(Recognizer):
    def __init__(self, *recognizers, script=True):
        self.recognizers = recognizers
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            match = Any([
                each.match(data, account, verbose) for each in self.recognizers
            ])
            if match:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.recognizers]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeTitle {{{1
class RecognizeTitle(Recognizer):
    def __init__(self, *titles, script=True):
        self.titles = flatten(titles)
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            actual = data.get('rawtitle')
            if actual:
                for candidate in self.titles:
                    if fnmatch(actual, candidate):
                        if verbose:
                            log('    %s: matches.' % self.get_name())
                        return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.titles]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeURL {{{1
class RecognizeURL(Recognizer):
    def __init__(self, *urls, script=True, name=None, exact_path=False):
        self.urls = flatten(urls)
        self.script = script
        self.name = name
        self.exact_path = exact_path

    def match(self, data, account, verbose=False):
        try:
            for url in self.urls:
                url = urlparse(url)
                protocol = url.scheme
                host = url.netloc
                path = url.path

                # data may contain the following fields after successful title
                # recognition:
                #     rawdata: the original title
                #     title: the processed title
                #     url: the full url
                #     browser: the name of the browser
                #     protocol: the url scheme (ex. http, https, ...)
                #     host: the url host name or IP address
                #     path: the path component of the url
                #           does not include options or anchor
                if host == data.get('host'):

                    def path_matches(expected, actual):
                        if not expected:
                            # path was not specified, treat it as don't care
                            return True
                        if self.exact_path:
                            # exact path match expected
                            return expected == actual
                        else:
                            # otherwise just match what was given
                            return actual.startswith(expected)

                    if path_matches(path, data.get('path')):
                        if (
                            protocol == data.get('protocol') or
                            protocol not in REQUIRED_PROTOCOLS
                        ):
                            if verbose:
                                log('    %s: matches.' % self.get_name())
                            return self.script
                        else:
                            msg = 'url matches, but uses wrong protocol.'
                            notify(msg)
                            raise Error(msg, culprit=account.get_name())
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def get_urls(self):
        return {self.name: self.urls}

    def __repr__(self):
        args = [repr(each) for each in self.urls]
        if self.script:
            args.append('script=%r' % self.script)
        if self.name:
            args.append('name=%r' % self.name)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))

# RecognizeCWD {{{1
class RecognizeCWD(Recognizer):
    def __init__(self, *dirs, script=True):
        self.dirs = flatten(dirs)
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            cwd = cwd()
            for directory in self.dirs:
                if cwd.samefile(to_path(directory)):
                    if verbose:
                        log('    %s: matches.' % self.get_name())
                    return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.dirs]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeHost {{{1
class RecognizeHost(Recognizer):
    def __init__(self, *hosts, script=True):
        self.hosts = flatten(hosts)
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            hostname = gethostname()
            for host in self.hosts:
                if host == hostname:
                    if verbose:
                        log('    %s: matches.' % self.get_name())
                    return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.hosts]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeUser {{{1
class RecognizeUser(Recognizer):
    def __init__(self, *users, script=True):
        self.users = flatten(users)
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            username = getusername()
            if username in self.users:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.users]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))

# RecognizeEnvVar {{{1
class RecognizeEnvVar(Recognizer):
    def __init__(self, name, value, script=True):
        self.name = name
        self.value = value
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            if name in os.environ and value == os.environ[name]:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as err:
            raise Error(str(err), culprit=err.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join([
            repr(each) for each in [self.name, self.value, self.script]
        ]))

