# One-Time Passwords
#
# GeneratedSecret is a base class that can be used to easily generate various
# types of secretes. Basically, it gathers together a collection of strings (the
# arguments of the constructor and the generate function) that are joined
# together and hashed. The 512 bit hash is then used to generate passwords,
# passphrases, and other secrets.
#

# License {{{1
# Copyright (C) 2016-2021 Kenneth S. Kundert
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
from .error import PasswordError
from .secrets import GeneratedSecret
from .utilities import error_source
from base64 import b32decode
from binascii import Error as BinasciiError


# OTP {{{1
try:
    from pyotp import TOTP

    class OTP(GeneratedSecret):
        """One Time Password

        Generates a secret that changes over time that generally is used
        as a second factor when authenticating.  It can act as a replacement
        for, and is fully compatible with, Google Authenticator or Authy.  You
        would provide the text version of the shared secret that is presented to
        you when first configuring your second factor authentication. See
        :ref:`otp` for more information.

        Only available if pyotp is installed (pip install pyotp).

        Args:
            shared_secret (str):
                The shared secret in base32.
            interval (int):
                Update interval in seconds.
                Use 30 to mimic Google Authenticator, 10 to mimic Authy.
            digits (int):
                Number of digits to output, choose between 6, 7, or 8.
                Use 6 to mimic Google Authenticator, 7 to mimic Authy.
        """

        def __init__(self, shared_secret, *, interval=30, digits=6):
            self.interval = interval
            self.digits = digits

            # convert original secret to string (for archives)
            try:
                shared_secret = shared_secret.render()
            except AttributeError:
                pass
            shared_secret = str(shared_secret)

            # strip spaces and convert to bytes
            secret = shared_secret.replace(' ', '').encode('utf-8')

            # add padding if needed
            secret += b'='*((8 - len(secret)) % 8)

            # check validity
            try:
                b32decode(secret, casefold=True)
                # don't need return value, only checking for errors
            except BinasciiError:
                raise PasswordError(
                    f'invalid value specified to OTP: {shared_secret}.',
                    culprit = error_source()
                )

            # save results
            self.shared_secret = shared_secret
            self.secret = secret
            self.is_secret = False
                # no need to conceal OTPs as they are ephemeral

        def initialize(self, account, field_name, field_key=None):
            self.totp = TOTP(
                self.secret, interval=self.interval, digits=self.digits
            )

        def render(self):
            return self.totp.now()

        # __repr__() {{{2
        def __repr__(self):
            # this is used to create the archive
            # archive the shared secret rather than OTP
            return "OTP({!r})".format(self.shared_secret)


except ImportError:
    pass
