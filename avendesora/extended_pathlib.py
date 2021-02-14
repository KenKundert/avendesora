# pathlib -- extends system pathlib

# License {{{1
# Copyright (C) 2016-2021 Kenneth S. Kundert
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
# along with this program.  If not, see [http://www.gnu.org/licenses/].


# Imports {{{1
import codecs
import os
import sys
from pathlib import Path, PosixPath
import six

# Globals {{{1
__version__ = "0.5.0"


# is_readable {{{1
def _is_readable(path):
    """
    Tests whether path exists and is readable.

    >>> from extended_pathlib import Path
    >>> Path('/usr/bin/python').is_readable()
    True

    """
    return os.access(str(path), os.R_OK)


PosixPath.is_readable = _is_readable


# is_writable {{{1
def _is_writable(path):
    """
    Tests whether path exists and is writable.

    >>> Path('/usr/bin/python').is_writable()
    False

    """
    return os.access(str(path), os.W_OK)


PosixPath.is_writable = _is_writable


# is_executable {{{1
def _is_executable(path):
    """
    Tests whether path exists and is executable.

    >>> Path('/usr/bin/python').is_executable()
    True

    """
    return os.access(str(path), os.X_OK)


PosixPath.is_executable = _is_executable


# is_hidden {{{1
def _is_hidden(path):
    """
    Tests whether path exists and is hidden.

    >>> Path('/usr/bin/python').is_hidden()
    False

    """
    return path.exists() and path.name.startswith(".")


PosixPath.is_hidden = _is_hidden


# is_newer {{{1
def _is_newer(path, ref):
    """
    Tests whether path is newer than ref where ref is either another path or a
    date.

    >>> Path('/usr/bin/python').is_newer(0)
    True

    """
    mtime = path.stat().st_mtime
    try:
        return mtime > ref
    except TypeError:
        try:
            return mtime > ref.timestamp
        except AttributeError:
            return mtime > ref.stat().st_mtime


PosixPath.is_newer = _is_newer


# path_from {{{1
def _path_from(path, start):
    """
    Returns relative path from start as a path object.
    This differs from Path.relative_to() in that relative_to() will not return a
    path that starts with '..'.

    >>> Path('.').path_from('..')
    PosixPath('tests')

    """
    return Path(os.path.relpath(str(path), str(start)))


PosixPath.path_from = _path_from


# sans_ext {{{1
def _sans_ext(path):
    """
    Removes the file extension.
    This differs from Path.stem, which returns the final path component
    stripped of its extension. This returns the full path stripped of its
    extension.

    >>> Path('a/b.c').sans_ext()
    PosixPath('a/b')

    """
    return path.parent / path.stem


PosixPath.sans_ext = _sans_ext

# Python 3.5 extensions {{{1
if sys.version_info < (3, 5):

    # read_bytes {{{2
    def _read_bytes(self):
        """
        Open the file in binary mode, read it, and close the file.
        """
        with self.open(mode="rb") as f:
            return f.read()

    PosixPath.read_bytes = _read_bytes

    # read_text {{{2
    def _read_text(self, encoding=None, errors=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode="r", encoding=encoding, errors=errors) as f:
            return f.read()

    PosixPath.read_text = _read_text

    # write_bytes {{{2
    def _write_bytes(self, data):
        """
        Open the file in binary mode, write it, and close the file.
        """
        if not isinstance(data, six.binary_type):
            raise TypeError(
                "data must be %s, not %s."
                % (six.binary_type.__name__, data.__class__.__name__)
            )
        with self.open(mode="wb") as f:
            return f.write(data)

    PosixPath.write_bytes = _write_bytes

    # write_text {{{2
    def _write_text(self, text, encoding=None, errors=None):
        """
        Open the file in text mode, write it, and close the file.
        """
        path = str(self)
        with codecs.open(path, mode="w", encoding=encoding, errors=errors) as f:
            return f.write(text)

    PosixPath.write_text = _write_text

    # expand_user {{{2
    def _expanduser(self):
        """
        Return a new path with expanded ~ and ~user constructs.
        """

        path = str(self)
        if path[:1] == "~":
            path = os.path.expanduser(path)
            self = Path(path)
        return self

    PosixPath.expanduser = _expanduser
