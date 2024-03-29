# Error

# License {{{1
# Copyright (C) 2016-2024 Kenneth S. Kundert
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
from inform import Error


# Exceptions {{{1
class PasswordError(Error):
    """Password error.

    This exception subclasses
    `Inform.Error <https://github.com/KenKundert/inform#exception>`_.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
