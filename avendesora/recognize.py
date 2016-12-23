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
from .config import get_setting
from .utilities import gethostname, getusername, error_source
from shlib import cwd, to_path, Run
from inform import Error, is_collection, is_str, log, notify, warn
from fnmatch import fnmatch
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import os

# Utilities {{{1
# flatten {{{2
def flatten(collection, split=False):
    # if split is specified, create list from string by splitting at whitespace
    if split and is_str(collection):
        collection = collection.split()

    if is_collection(collection):
        for each in collection:
            for e in flatten(each):
                yield e
    else:
        yield collection

# Recognizer Base Class {{{1
class Recognizer(object):
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
    def __init__(self, *recognizers, **kwargs):
        self.recognizers = recognizers
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
    def __init__(self, *recognizers, **kwargs):
        self.recognizers = recognizers
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
    def __init__(self, *titles, **kwargs):
        self.titles = flatten(titles, split=False)
        self.script = kwargs.pop('script', True)
        self.name = kwargs.pop('name', None)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
        if self.name:
            args.append('name=%r' % self.name)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeURL {{{1
class RecognizeURL(Recognizer):
    def __init__(self, *urls, **kwargs):
        self.urls = flatten(urls, split=True)
        self.script = kwargs.pop('script', True)
        self.name = kwargs.pop('name', None)
        self.exact_path = kwargs.pop('exact_path', False)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
    def __init__(self, *dirs, **kwargs):
        self.dirs = flatten(dirs, split=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
    def __init__(self, *hosts, **kwargs):
        self.hosts = flatten(hosts, split=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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
    def __init__(self, *users, **kwargs):
        self.users = flatten(users, split=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

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

# RecognizeNetwork {{{1
class RecognizeNetwork(Recognizer):
    """RecognizeNetwork from MAC address

    Matches if any of the MAC addresses reported by /sbin/arp match any of those
    given as an argument.
    """
    def __init__(self, *macs, **kwargs):
        self.macs = flatten(macs, split=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, data, account, verbose=False):
        # should modify this so that 'ip neigh' can be used in lieu of arp,
        # after all, arp is supposedly obsolete.
        try:
            arp = Run([get_setting('arp_executable')], 'sOeW')
            lines = arp.stdout.strip().split('\n')
            macs = [field.split()[2] for field in lines[1:]]

            found = set([mac.lower() for mac in macs])
            expected = set([mac.lower() for mac in self.macs])
            if found & expected:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except OSError as err:
            warn(os_error())
            return
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.macs]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))
