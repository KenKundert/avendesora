# Collections
#
# Provides common interface for dictionaries and lists. If a string is passed
# in, it is split and then treated as a list. Optimized for convenience rather
# than for large collections. Sorting versus the key is used to avoid randomness
# in the ordering of the dictionary-based collections.

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
from inform import is_str, is_collection


# Collection {{{1
class Collection(object):
    def __init__(self, collection, splitter=None):
        if splitter is not False and is_str(collection):
            # strings will be split unless splitter is False
            self.collection = collection.split(splitter)
        elif is_collection(collection):
            self.collection = collection
        elif collection is None:
            self.collection = []
        else:
            # is scalar
            self.collection = {None: collection}

    def keys(self):
        try:
            return self.collection.keys()
        except AttributeError:
            return range(len(self.collection))

    def values(self):
        try:
            return [self.collection[k] for k in sorted(self.collection.keys())]
        except AttributeError:
            return self.collection

    def items(self):
        try:
            return [(k, self.collection[k]) for k in sorted(self.collection.keys())]
        except AttributeError:
            return enumerate(self.collection)

    def render(self, fmt='{v}', sep=', '):
        """Convert the collection into a string

        fmt (str):
            fmt is a format string applied to each of the items in the
            collection where {k} is replaced with the key and {v} replaced with
            the value.
        sep (str):
            The string used to join the formatted items.
        the value.  The second component is the separator. Thus:

            >>> dogs = Collection({'collie': 3, 'beagle':1, 'sheppard': 2})
            >>> print('dogs: {}.'.format(c.render('{k} ({v})', ', ')))
            dogs: collie (3), beagle (1), sheppard (2).
        """
        return sep.join([tmpl.format(k=k, v=v) for k, v in self.items()])

    def __format__(self, template):
        """Convert the collection into a string

        The template consists of two components separated by a vertical bar. The
        first component specifies the formatting from each item. The key and
        value are interpolated using \k to represent the key and \v to represent
        the value.  The second component is the separator. Thus:

            >>> dogs = Collection({'collie': 3, 'beagle':1, 'sheppard': 2})
            >>> print('dogs: {dogs:\k (\v)|, }.'.format(names=c))
            dogs: collie (3), beagle (1), sheppard (2).
        """
        components = template.split('|')
        if len(components) == 2:
            tmpl, sep = components
        elif len(components) == 1:
            tmpl, sep = components[0], ', '
        else:
            raise ValueError('invalid format string for {!r}', self)

        return sep.join([
            tmpl.replace('\k', str(k)).replace('\v', str(v))
            for k, v in self.items()
        ])

    def __contains__(self, item):
        return item in self.values()

    def __iter__(self):
        return iter(self.values())

    def __len__(self):
        return len(self.collection)

    def __getitem__(self, key):
        return self.collection[key]
