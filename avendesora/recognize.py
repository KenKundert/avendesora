# Account Recognizers
#
# Classes used in account discovery to recognize when a particular account
# should be used based on environmental conditions (window title, hostname,
# username, current directory, etc.)

# License {{{1
# Copyright (C) 2016-17 Kenneth S. Kundert
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
from .config import get_setting
from .error import PasswordError
from .utilities import gethostname, getusername, error_source
from shlib import cwd, to_path, Run
from inform import is_collection, is_str, log, notify, warn, os_error
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
    """Run script if all recognizers match.

    Takes one or more recognizers. Script is run if all recognizers match.

    Args:
        recognizer (Recognizer):
            One or more instances of Recognizer.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

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
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.recognizers]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeAny {{{1
class RecognizeAny(Recognizer):
    """Run script if any recognizers match.

    Takes one or more recognizers. Script is run if any recognizers match.

    Args:
        recognizer (Recognizer):
            One or more instances of Recognizer.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

    def __init__(self, *recognizers, **kwargs):
        self.recognizers = recognizers
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, data, account, verbose=False):
        try:
            match = any([
                each.match(data, account, verbose) for each in self.recognizers
            ])
            if match:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.recognizers]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeTitle {{{1
class RecognizeTitle(Recognizer):
    """Run script if window title matches.

    Takes one or more glob strings.
    Script is run if window title matches any of the glob strings.

    Args:
        title (str):
            One or more glob strings.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

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
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
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
    """Run script if URL matches.

    Takes one or more URLs.
    Script is run if URL embedded in window title matches any of the given URLs.
    Assumes that a browser plugin has embedded the URL in the browser's window
    title.  This is generally safer and more robust that RecognizeTitle when
    trying to match web pages.

    When giving the URL, anything specified must match and globbing is
    not supported. If you give a partial path, by default Avendesora
    will match up to what you have given, but you can require an exact
    match of the entire path by specifying exact_path=True to
    RecognizeURL.  If you do not give the protocol, the default_protocol
    (https) is assumed.

    Args:
        url (str):
            One or more URLs.
        exact_path (bool):
            If True, path given in the URL must be matched completely, partial
            matches are ignored.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

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
                url = url if '//' in url else ('//'+url)
                url_components = urlparse(url)
                if url_components.scheme:
                    protocol = url_components.scheme
                else:
                    protocol = get_setting('default_protocol')
                host = url_components.netloc
                path = url_components.path

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
                        if (protocol == data.get('protocol')):
                            if verbose:
                                log('    %s: matches.' % self.get_name())
                            return self.script
                        else:
                            msg = 'url matches, but uses wrong protocol.'
                            notify(msg)
                            raise PasswordError(msg, culprit=account.get_name())
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
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
    """Run script if current working directory matches.

    Takes one or more paths.  Script is run if any path refers to the current
    working directory.

    Args:
        path (str):
            One or more directory paths.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

    def __init__(self, *dirs, **kwargs):
        self.dirs = flatten(dirs, split=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, data, account, verbose=False):
        try:
            cwd = os.cwd()
            for directory in self.dirs:
                if cwd.samefile(to_path(directory)):
                    if verbose:
                        log('    %s: matches.' % self.get_name())
                    return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.dirs]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeHost {{{1
class RecognizeHost(Recognizer):
    """Run script if host name matches.

    Takes one or more host names.
    Script is run if the current host name matches one of the given host names.

    Args:
        host (str):
            One or more host names.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

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
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.hosts]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeUser {{{1
class RecognizeUser(Recognizer):
    """Run script if user name matches.

    Takes one or more user names.
    Script is run if the current user name matches one of the given user names.

    Args:
        user (str):
            One or more user names.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

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
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.users]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))

# RecognizeEnvVar {{{1
class RecognizeEnvVar(Recognizer):
    """Run script if environment variable matches.

    Script is run if the environment variable exists and its value matches the value given.

    Args:
        name (str):
            Name of environment variable.
        value (str):
            Value of environment variable.
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """

    def __init__(self, name, value, script=True):
        self.name = name
        self.value = value
        self.script = script

    def match(self, data, account, verbose=False):
        try:
            if self.name in os.environ and self.value == os.environ[self.name]:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join([
            repr(each) for each in [self.name, self.value, self.script]
        ]))

# RecognizeNetwork {{{1
class RecognizeNetwork(Recognizer):
    """Recognize network from MAC address.

    Matches if any of the MAC addresses reported by /sbin/arp match any of those
    given as an argument.

    Args:
        mac (str):
            MAC address given in the form: '00:c9:a9:f7:30:00'.

        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
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
        except OSError as e:
            warn(os_error(e))
            return
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(each) for each in self.macs]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))


# RecognizeFile {{{1
class RecognizeFile(Recognizer):
    """Recognize file.

    Matches if file exists and was created within the last few seconds.

    Args:
        filepath (str):
            Path to file.
        contents (str):
            Expected file contents. If given, should match contents of file.
        wait (float):
            Do not match if file is older than this value (seconds).
        script (str or True):
            A script that indicates the text that should be typed to active
            application. The names of fields can be included in the script
            surrounded by braces, in which case the value of the field replaces the
            field reference.  For example::

                Script('username: {username}, password: {passcode}')

            In this case, *{username}* and *{passcode}* are replaced by with the
            value of the corresponding account attribute. In addition to the
            fields, *{tab}* and *{return}* are replaced by a tab or carriage
            return character, and *{sleep N}* causes the typing to pause for *N*
            seconds.

            If True is give, the default field is produced followed by a return.

    Raises:
        :exc:`avendesora.PasswordError`
    """
    def __init__(self, filepath, contents=None, wait=60, **kwargs):
        self.filepath = to_path(filepath)
        self.expected = contents
        self.wait = wait
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, data, account, verbose=False):
        import arrow
        try:
            mtime = self.filepath.stat().st_mtime
            now = arrow.now().timestamp
            if mtime + float(self.wait) > now:
                if self.expected:
                    found = self.filepath.read_text()
                    if found.strip() == self.expected.strip():
                        if verbose:
                            log('    %s: matches.' % self.get_name())
                        return self.script
                    elif verbose:
                        log('    %s: content mismatch.' % self.get_name())
                        return
            elif verbose:
                log('    %s: file stale.' % self.get_name())
                return
        except FileNotFoundError:
            pass
        except OSError as e:
            warn(os_error(e))
        if verbose:
            log('    %s: no match.' % self.get_name())

    def __repr__(self):
        args = [repr(str(self.filepath))]
        if self.script:
            args.append('script=%r' % self.script)
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))
