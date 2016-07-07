from .utilities import gethostname, getusername
from shlib import cwd, to_path
from inform import error, log, warn
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
                        warn(
                            'url matches, but uses wrong protocol.',
                            culprit=account.get_name()
                        )


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

