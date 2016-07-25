# Help
# Output a help topic.
#
# To Do:  Output the obscured text within a class instantiation. So rather than
# just outputting obscured text, output 'Hidden('obscured-text'). Also, accept
# obscured text within its class and try to decode it using the class name, so
# if GPG("ciphertext") then it will use GPG to decode it even if user does not
# provide the encoding.
#
# Also implement script class that uses a personal password. Call this Encrypt
# or PersonalEncrypt.

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
from .conceal import Conceal
from .config import get_setting
from inform import error, output
from textwrap import dedent

# Help Class {{{1
class Help:
    __DESCRIPTION = "Lists available help topics."
    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.name.lower()
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to
            # dashes.
            return cls.__name__.lower()

    # topics {{{2
    @classmethod
    def topics(cls):
        yield cls
        for sub in cls.__subclasses__():
            yield sub

    # show {{{2
    @classmethod
    def show(cls, name=None):
        name = name.lower() if name else 'help'
        for topic in cls.topics():
           if name == topic.get_name():
               topic.help()
               return
        error('topic not found.', culprit=name)

    # help {{{2
    @classmethod
    def help(cls):
        output('Available topics:')
        for topic in sorted(cls.topics(), key=lambda topic: topic.get_name()):
            output('    %s: %s' % (
                topic.get_name(),
                getattr(topic, '_%s__DESCRIPTION' % topic.__name__, '')
            ))


# Hide class {{{1
class Hide(Help):
    __DESCRIPTION = 'Obscure a text string.'

    @staticmethod
    def help():
        encodings = '    ' + '\n    '.join(Conceal.encodings())
        text = dedent("""
            Hide text by encoding it. Possible encodings include:
            {encodings}

            base64 (default):
                This encoding obscures but does not encrypt the text. It can
                protect text from observers that get a quick glance of the
                encoded text, but if they are able to capture it they can easily
                decode it.
        """).strip()
        output(text.format(encodings=encodings))


# Show class {{{1
class Show(Help):
    __DESCRIPTION = 'Reveals an obscured text string.'

    @staticmethod
    def help():
        encodings = '    ' + '\n    '.join(Conceal.encodings())
        text = dedent("""
            Reveal obscured text by decoding it. Possible encodings include:
            {encodings}

            base64 (default):
                This encoding obscures but does not encrypt the text. It can
                protect text from observers that get a quick glance of the
                encoded text, but if they are able to capture it they can easily
                decode it.
        """).strip()
        output(text.format(encodings=encodings))


# Find class {{{1
class Find(Help):
    __DESCRIPTION = 'Find accounts whose name contain a string.'

    @staticmethod
    def help():
        text = dedent("""
            List the account names that contain the search text.
        """).strip()
        output(text)


# Search class {{{1
class Search(Help):
    __DESCRIPTION = 'Find accounts whose fields contain a string.'

    @staticmethod
    def help():
        text = dedent("""
            List the account names that contain the search text.

            Only fields that are either not obscured or not generated are
            searched.
        """).strip()
        output(text)


# Init class {{{1
class Init(Help):
    __DESCRIPTION = 'Initialize Avendesora.'

    @staticmethod
    def help():
        text = dedent("""
            Creates an initial config files and initial accounts files if they
            do not already exist.
        """).strip()
        output(text)


# Browse class {{{1
class Browse(Help):
    __DESCRIPTION = 'Open the account in the web browser.'

    @staticmethod
    def help():
        default_browser = get_setting('default_browser')
        browsers = get_setting('browsers')
        browsers = '\n'.join(
            ['    %s  %s' % (k, browsers[k].split()[0]) for k in sorted(browsers)]
        )
        text = dedent("""
            Open the account URL in the web browser. Use -b or --browser to
            choose which browser to use. The default browser is {default}. The
            available browsers are:
            {browsers}
        """).strip()
        output(text.format(default=default_browser, browsers=browsers))
