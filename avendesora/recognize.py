# Account Recognizers
#
# Classes used in account discovery to recognize when a particular account
# should be used based on environmental conditions (window title, hostname,
# username, current directory, etc.)

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
from .collection import Collection
from .config import get_setting
from .error import PasswordError
from .shlib import to_path, Run
from .utilities import gethostname, getusername, OSErrors
from inform import Error, cull, log, notify, warn, os_error, indent, render
from fnmatch import fnmatch
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import os


# Utilities {{{1
def render_arg(value, name=None):
    if hasattr(value, 'render'):
        rendered_value = value.render()
    else:
        rendered_value = render(value, level=1)
    if name:
        return name + '=' + rendered_value
    return rendered_value

# Recognizer Base Class {{{1
class Recognizer(object):
    def all_urls(self, components=False):
        urls = {}
        if hasattr(self, 'recognizers'):
            for each in self.recognizers:
                urls.update(each.all_urls(components))
        if hasattr(self, 'get_urls'):
            urls.update(self.get_urls(components))
        # returns a dictionary where the keys are the names associated with the
        # urls, and the value is a list of pairs, the first member of the pair
        # is a url and the second is a boolean indicating whether an exact match
        # is needed (use by cache).
        return urls

    def all_titles(self):
        titles = {}
        if hasattr(self, 'recognizers'):
            for each in self.recognizers:
                titles.update(each.all_titles())
        if hasattr(self, 'get_titles'):
            titles.update(self.get_titles())
        # returns a dictionary where the keys are the names associated with the
        # titles, and the value is a list of glob strings that match the title.
        return titles

    def get_name(self):
        return self.__class__.__name__

    def _inform_get_kwargs(self):
        kwargs = {}
        if hasattr(self, 'script'):
            kwargs['script'] = getattr(self, 'script')
            if kwargs['script'] is True:
                del kwargs['script']  # don't clutter arg list with a default
        if hasattr(self, 'name'):
            kwargs['name'] = getattr(self, 'name')
        return cull(kwargs)

    def render(self):
        return render(self)

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

    def match(self, given, account, verbose=False):
        try:
            match = all([
                each.match(given, account, verbose) for each in self.recognizers
            ])
            if match:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def _inform_get_args(self):
        return self.recognizers

    def __repr__(self):
        return self.render()


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

    def match(self, given, account, verbose=False):
        try:
            match = any([
                each.match(given, account, verbose) for each in self.recognizers
            ])
            if match:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def _inform_get_args(self):
        return self.recognizers

    def __repr__(self):
        return self.render()


# RecognizeTitle {{{1
class RecognizeTitle(Recognizer):
    """Run script if window title matches.

    Takes one or more glob strings.
    Script is run if window title matches any of the glob strings.

    Args:
        titles (str):
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
        self.titles = Collection(titles, splitter=False)
        self.script = kwargs.pop('script', True)
        self.name = kwargs.pop('name', None)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
        try:
            actual = given.get('rawtitle')
            if actual:
                for candidate in self.titles:
                    if isinstance(candidate, str):
                        hit = fnmatch(actual, candidate)
                    else:
                        hit = candidate(actual)

                    if hit:
                        if verbose:
                            log('    %s: matches.' % self.get_name())
                        return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())

    def get_titles(self):
        return {self.name: self.titles}

    def _inform_get_args(self):
        return self.titles

    def __repr__(self):
        return self.render()


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
        urls (list):
            At least one url.
        exact_path (bool):
            If True, path given in the URL must be matched completely, partial
            matches are ignored.
        fragment (str):
            If given, it must match the URL fragment exactly. The URL fragment
            is the part of the url after #.
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
        self.urls = Collection(urls, splitter=True)
        self.script = kwargs.pop('script', True)
        self.name = kwargs.pop('name', None)
        self.exact_path = kwargs.pop('exact_path', False)
        self.fragment = kwargs.pop('fragment', None)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
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

                # given may contain the following fields after successful title
                # recognition:
                #     rawdata: the original title
                #     title: the processed title
                #     url: the full url
                #     browser: the name of the browser
                #     protocol: the url scheme (ex. http, https, ...)
                #     host: the url host name or IP address
                #     path: the path component of the url
                #           does not include options or anchor
                if host == given.get('host'):

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

                    if path_matches(path, given.get('path')):
                        if self.fragment and given.get('fragment') != self.fragment:
                            continue
                        if (protocol == given.get('protocol')):
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

    def get_urls(self, components=False):
        if components:
            urls = []
            for url in self.urls:
                url = url if '//' in url else ('//'+url)
                url_components = urlparse(url)
                host = url_components.netloc
                path = url_components.path
                urls.append((host, path, self.exact_path))
            return {self.name: urls}
        else:
            return {self.name: self.urls}

    def _inform_get_args(self):
        return self.urls

    def __repr__(self):
        return self.render()


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
        self.dirs = Collection(dirs, splitter=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
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

    def _inform_get_args(self):
        return self.dirs

    def __repr__(self):
        return self.render()


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
        self.hosts = Collection(hosts, splitter=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
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

    def _inform_get_args(self):
        return self.hosts

    def __repr__(self):
        return self.render()


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
        self.users = Collection(users, splitter=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
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

    def _inform_get_args(self):
        return self.users

    def __repr__(self):
        return self.render()


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

    def match(self, given, account, verbose=False):
        try:
            if self.name in os.environ and self.value == os.environ[self.name]:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Exception as e:
            raise PasswordError(str(e), culprit=e.__class__.__name__)
        if verbose:
            log('    %s: no match.' % self.get_name())


    def _inform_get_args(self):
        return []

    def _inform_get_kwargs(self):
        kwargs = dict(name=self.name, value=self.value)
        base = super()._inform_get_kwargs()
        kwargs['script'] = base.get('script')
        return cull(kwargs)

    def __repr__(self):
        return self.render()


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
        self.macs = Collection(macs, splitter=True)
        self.script = kwargs.pop('script', True)
        if kwargs:
            raise TypeError(
                '%s: invalid keyword argument.' % ', '.join(kwargs.keys()))

    def match(self, given, account, verbose=False):
        # should modify this so that 'ip neigh' can be used in lieu of arp,
        # after all, arp is supposedly obsolete.
        try:
            arp_executable = get_setting('arp_executable')
            try:
                arp = Run([arp_executable], 'sOEW')
            except Error as e:
                e.reraise(cuplrit=arp_executable)
            lines = arp.stdout.strip().split('\n')
            macs = [field.split()[2] for field in lines[1:]]

            found = set([mac.lower() for mac in macs])
            expected = set([mac.lower() for mac in self.macs])
            if found & expected:
                if verbose:
                    log('    %s: matches.' % self.get_name())
                return self.script
        except Error as e:
            warn(e)
            return
        if verbose:
            log('    %s: no match.' % self.get_name())

    def _inform_get_args(self):
        return self.macs

    def __repr__(self):
        return self.render()


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

    def match(self, given, account, verbose=False):
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
        except OSErrors as e:
            warn(os_error(e))
        if verbose:
            log('    %s: no match.' % self.get_name())

    def _inform_get_args(self):
        return [str(self.filepath)]

    def _inform_get_kwargs(self):
        kwargs = dict(contents = self.expected, wait = self.wait)
        base = super()._inform_get_kwargs()
        kwargs['script'] = base.get('script')
        return cull(kwargs)

    def __repr__(self):
        return self.render()
