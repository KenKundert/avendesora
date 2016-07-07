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
    SEARCH_FIELDS, DEFAULT_FIELD, DEFAULT_VECTOR_FIELD, LABEL_COLOR, INDENT
)
from .recognizers import Recognizer
from inform import Error, is_collection, log, output, Color
from textwrap import indent, dedent
import re
import sys


# Globals {{{1
VECTOR_PATTERN = re.compile(r'\A(\w+)\[(\w+)\]\Z')
LabelColor = Color(LABEL_COLOR, enable=Color.isTTY())

# Account Class {{{1
class Account:
    # all_accounts() {{{2
    @classmethod
    def all_accounts(cls):
        for sub in cls.__subclasses__():
            yield sub
            for sub in sub.all_accounts():
                yield sub

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
        if target in cls.get_name():
            return True
        try:
            for alias in cls.aliases:
                if target in alias:
                    return True
        except AttributeError:
            pass
        return False

    # account_contains() {{{2
    @classmethod
    def account_contains(cls, target):
        if cls.id_contains(target):
            return True
        for field in SEARCH_FIELDS:
            try:
                if target in cls.__dict__[field]:
                    return True
            except KeyError:
                pass
        return False

    # recognize() {{{2
    @classmethod
    def recognize(cls, data):
        plugins = getattr(cls, 'plugins', ())
        for plugin in plugins:
            if isinstance(plugin, Recognizer):
                secret = plugin.match(data, cls)
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
    def get_value(cls, name, key=None):
        value = cls.__dict__.get(name)
        if value is None:
            raise Error('not found.', culprit=cls.combine_name(name, key))
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

    # write_value() {{{2
    # @classmethod
    # def write_value(cls, name=None, writer=None):
    #     # passes value to user using selected writer.
    #     nm, key = cls.split_name(name)
    #     name = cls.combine_name(nm, key)
    #     try:
    #         value = cls.get_value(nm, key)
    #     except Error as err:
    #         if err.is_collection:
    #             output('is a collection, choose from:', culprit=name)
    #             value = err.collection
    #             try:
    #                 items = value.items()
    #             except AttributeError:
    #                 items = enumerate(value)
    #             for k, v in items:
    #                 try:
    #                     alt_name = v.get_name()
    #                 except AttributeError:
    #                     alt_name = None
    #                 if alt_name:
    #                     output('    %s: %s' % (k, alt_name))
    #                 else:
    #                     output('    %s' % k)
    #             return
    #         else:
    #             raise
    #     if value:
    #         if writer:
    #             raise NotImplementedError
    #         else:
    #             try:
    #                 alt_name = value.get_name()
    #                 if alt_name:
    #                     name = '%s (%s)' % (name, alt_name)
    #             except AttributeError:
    #                 pass
    #             output('%s = %s' % (name, value))
    #     else:
    #         raise Error('not found.', culprit=name)

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

        def extract_collection(name, collection):
            lines = [fmt_field(key)]
            try:
                items = collection.items()
            except AttributeError:
                items = enumerate(collection)
            for k, v in items:
                if hasattr(v, '_initiate'):
                    # is a secret, get description if available
                    v = v.get_name() if hasattr(v, 'get_name') else '<secret>'
                lines.append(fmt_field(k, v, level=1))
            return lines

        # preload list with the names associated with this account
        names = [cls.get_name()]
        if hasattr(cls, 'aliases'):
            names += [cls.get_name()] + cls.aliases
        lines = [fmt_field('names', ', '.join(names))]

        for key, value in cls.values():
            if key in ['aliases', 'default', 'master', 'plugins']:
                # is an Avendesora field
                pass
            elif is_collection(value):
                lines += extract_collection(key, value)
            elif hasattr(value, '_initiate'):
                lines.append(fmt_field(key, '<secret>'))
            else:
                lines.append(fmt_field(key, value))
        output(*lines, sep='\n')

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
                raise Error('not found.', culprit=name)

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
            name = cls.get_value('default')
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
            name, key = name.split('/')
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
            return '%s[%s]' % (name, key)
