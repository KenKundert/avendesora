# Account
# API for an account

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
from .preferences import (
    DEFAULT_FIELD, DEFAULT_VECTOR_FIELD, LABEL_COLOR, INDENT, TOOL_FIELDS
)
from .recognizers import Recognizer
from .browsers import StandardBrowser
from inform import Error, is_collection, log, output, Color
from textwrap import indent, dedent
import re
import sys


# Globals {{{1
VECTOR_PATTERN = re.compile(r'\A(\w+)\[(\w+)\]\Z')
LabelColor = Color(LABEL_COLOR, enable=Color.isTTY())

# Utilities {{{1
# items {{{2
# iterate through either a dictionary or an array
def items(collection):
    try:
        iterator = collection.items()
    except AttributeError:
        iterator = enumerate(collection)
    for key, value in iterator:
        yield key, value

# Account Class {{{1
class Account:
    # all_accounts() {{{2
    @classmethod
    def all_accounts(cls):
        for sub in cls.__subclasses__():
            yield sub
            for sub in sub.all_accounts():
                yield sub

    # all_fields() {{{2
    @classmethod
    def all_fields(cls):
        for key, value in cls.__dict__.items():
            if not key.startswith('_'):
                yield key, value

    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.name
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to 
            # dashes.
            return cls.__name__.lower()

    # matches_exactly() {{{2
    @classmethod
    def matches_exactly(cls, account):
        if account == cls.get_name():
            return True
        try:
            if account in cls.aliases:
                return True
        except AttributeError:
            pass
        return False

    # id_contains() {{{2
    @classmethod
    def id_contains(cls, target):
        target = target.lower()
        if target in cls.get_name().lower():
            return True
        try:
            for alias in cls.aliases:
                if target in alias.lower():
                    return True
        except AttributeError:
            pass
        return False

    # account_contains() {{{2
    @classmethod
    def account_contains(cls, target):
        if cls.id_contains(target):
            return True
        target = target.lower()
        for key, value in cls.all_fields():
            if key in TOOL_FIELDS:
                continue
            try:
                if is_collection(value):
                    for k, v in items(value):
                        if target in v.lower():
                            return True
                elif target in value.lower():
                    return True
            except AttributeError:
                # is not a string, and so 
                pass
        return False

    # recognize() {{{2
    @classmethod
    def recognize(cls, data):
        discovery = getattr(cls, 'discovery', ())
        for recognizer in discovery:
            if isinstance(recognizer, Recognizer):
                secret = recognizer.match(data, cls)
                if secret:
                    return secret

    # initialize() {{{2
    @classmethod
    def initialize(cls):
        log('initializing', cls.get_name())
        for key, value in cls.__dict__.items():

            # initiate the secret
            if not key.startswith('_'):
                try:
                    # initiate a scalar secret
                    value._initiate(key, cls)
                    log('    found secret attribute:', key)
                except AttributeError:
                    try:
                        # initiate a dictionary secret
                        for n, v in value.items():
                            name = 'key[%s]' % n
                            v._initiate(name, cls)
                    except AttributeError:
                        try:
                            # initiate a vector secret
                            for i, each in enumerate(value):
                                name = 'key[%s]' % i
                                each._initiate(name, cls)
                        except AttributeError:
                            # not a secret
                            continue

    # values() {{{2
    @classmethod
    def values(cls):
        for key in sorted(cls.__dict__):
            if not key.startswith('__'):
                yield key, cls.__dict__[key]

    # get_value() {{{2
    @classmethod
    def get_value(cls, name, key=None, default=False):
        value = cls.__dict__.get(name)
        if value is None:
            if default is False:
                raise Error('not found.', culprit=cls.combine_name(name, key))
            else:
                return default
        if key is None:
            if is_collection(value):
                raise Error(
                    'composite value found, need key.',
                    culprit=name,
                    is_collection=True,
                    collection = value
                )
            return value
        else:
            try:
                return value[key]
            except (IndexError, KeyError, TypeError):
                raise Error('not found.', culprit=cls.combine_name(name, key))

    # is_secret() {{{2
    @classmethod
    def is_secret(cls, name, key=None):
        value = cls.__dict__.get(name)
        if key is None:
            return hasattr(value, '_initiate')
        else:
            try:
                return hasattr(value[key], '_initiate')
            except (IndexError, KeyError, TypeError):
                raise Error('not found.', culprit=cls.combine_name(name, key))

    # split_name() {{{2
    @classmethod
    def split_name(cls, name):
        # Account fields can either be scalars or composites (vectors or
        # dictionaries). This function takes a string (name) that the user
        # provides to specify which account value they wish and splits it into a
        # field name and a key.  If the field is a scalar, the key will be None.
        # Users request a value using one of the following forms:
        #     True: use default name
        #     field: scalar value (key=None)
        #     index: questions (field->'questions', key=index)
        #     field[index] or field/index: for vector value
        #     field[key] or field/key: for dictionary value

        if name is True or not name:
            name = cls.get_value('default', default=None)
        if not name:
            name = DEFAULT_FIELD

        # convert dashes to underscores
        name = name.replace('-', '_')

        # If name is an integer, treat it as number of security question.
        try:
            return DEFAULT_VECTOR_FIELD, int(name)
        except ValueError:
            pass

        # Split name if given in the form: name/key
        try:
            name, key = name.split('.')
            try:
                return name, int(key)
            except ValueError:
                return name, key
        except ValueError:
            pass

        # Split name if given in the form: name[key]
        match = VECTOR_PATTERN.match(name)
        if match:
            # vector name using 'name[key]' syntax
            name, key = match.groups()
            try:
                return name, int(key)
            except ValueError:
                return name, key

        # Must be scalar name
        return name, None

    # combine_name() {{{2
    @classmethod
    def combine_name(cls, name, key=None):
        # Inverse of split_name().

        # convert underscores to dashes
        #name = name.replace('_', '-')

        if key is None:
            return name
        else:
            return '%s.%s' % (name, key)

    # write_summary() {{{2
    @classmethod
    def write_summary(cls):
        # present all account values that are not explicitly secret to the user

        def fmt_field(key, value='', level=0):
            if '\n' in value:
                value = indent(dedent(value), INDENT).strip('\n')
                sep = '\n'
            elif value:
                sep = ' '
            else:
                sep = ''
            key = str(key).upper().replace('_', ' ')
            return indent(LabelColor(key + ':') + sep + value, level*INDENT)

        def reveal(name, key=None):
            return "<reveal with 'avendesora %s %s'>" % (
                cls.get_name(), cls.combine_name(name, key)
            )

        def extract_collection(name, collection):
            lines = [fmt_field(key)]
            for k, v in items(collection):
                if hasattr(v, '_initiate'):
                    # is a secret, get description if available
                    v = v.get_name() if hasattr(v, 'get_name') else reveal(name, k)
                lines.append(fmt_field(k, v, level=1))
            return lines

        # preload list with the names associated with this account
        names = [cls.get_name()]
        if hasattr(cls, 'aliases'):
            names += [cls.get_name()] + cls.aliases
        lines = [fmt_field('names', ', '.join(names))]

        for key, value in cls.values():
            if key in TOOL_FIELDS:
                # is an Avendesora field
                pass
            elif is_collection(value):
                lines += extract_collection(key, value)
            elif hasattr(value, '_initiate'):
                lines.append(fmt_field(key, reveal(key)))
            else:
                lines.append(fmt_field(key, value))
        output(*lines, sep='\n')

    # open_browser() {{{2
    @classmethod
    def open_browser(cls, name):
        browser = cls.get_value('browser', default=None)
        if browser is None or is_str(browser):
            browser = StandardBrowser(name)
        url = cls.get_value('url', default=None)
        browser.run(url)
