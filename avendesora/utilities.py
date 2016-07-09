# Utilities

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
from shlib import Run
from inform import error, os_error

# gethostname {{{1
# returns short version of the hostname (the hostname without any domain name)
import socket
def gethostname():
    return socket.gethostname().split('.')[0]

# getusername {{{1
import getpass
def getusername():
    return getpass.getuser()

# generate_random_string {{{1
def generate_random_string(length=64):
    # Generate a random long string to act as the default password

    from string import ascii_letters, digits, punctuation
    import random
    rand = random.SystemRandom()

    # Create alphabet from letters, digits, and punctuation, but 
    # replace double quote with a space so password can be safely 
    # represented as a double-quoted string.
    alphabet = (ascii_letters + digits + punctuation).replace('"', ' ')

    password = ''
    for i in range(length):
        password += rand.choice(alphabet)
    return password


