Releases
========

.. currentmodule:: avendesora

Latest Development Version
--------------------------
| Version: 1.26
| Released: 2024-08-28


1.26 (2024-08-28)
-----------------
- added :class:`Base58` secrets class.
- improved error checking


1.25 (2023-04-22)
-----------------
- minor refinements.


1.24 (2022-11-04)
-----------------
- minor refinements.


1.23 (2022-08-31)
-----------------
- enhanced *bw-export* scripts.
- with :ref:`value command <value command>`, only the first few characters of
  the field name need be specified.
- when ``?`` is passed as *field* to the :ref:`value command <value command>`, 
  the list of available fields is displayed.
- added :ref:`additional_account_templates <additional_account_templates 
  setting>` setting.


1.22 (2021-11-10)
-----------------
- Allow remind commands in :class:`Script`.


1.21 (2021-08-08)
-----------------
- Added *fold_level* to :meth:`Account.export()`.
- Added *paste* attribute to scripts that might help avoid captchas.


1.20 (2021-02-13)
-----------------
- added :ref:`hidden_fields <hidden_fields setting>` setting.


1.19 (2021-01-03)
-----------------
- Make :class:`OTP` less persnickety about form of shared secrets.
- Automatically fix file permission issues when found.


1.18 (2020-11-12)
-----------------
- Deprecate Python 2.7 and Python 3.5.
- Add :meth:`PasswordGenerator.get_value()`, a method of getting an account 
    value from a string that includes the account and field names.
- Add hidden account attributes.
- Require secondary arguments on secrets to be passed by name.
- Renamed *alphabet* argument to :class:`Passphrase` and :class:`Question` 
    to *dictionary*.

    .. warning::

        This change is not backward compatible and may require you to change
        entries in your account files.

- This release requires *secrets_hash* to be updated.


1.17 (2020-04-15)
-----------------
- Enhance :ref:`conceal command <conceal command>` so that it can read text 
    from a file.
- Add :class:`WriteFile`; allows the contents of a file to be held as an 
    account field. When requested, the contents are written to the file 
    system.


1.16 (2019-12-25)
-----------------
- Added :ref:`ms_per_char <ms_per_char setting>` setting that allows user to 
  slow autotyping.
- Added *rate* attribute to scripts that allows user to slow autotyping.
- Added :ref:`command_aliases <command_aliases setting>` setting to allow user 
  to define their own command short-cuts. As part of this the built-in short 
  cuts were removed. See description of *command_aliases* in 
  :ref:`configuring_avendesora` to get them back.
- :ref:`interactive command <interactive command>` now accepts '*'.


1.15 (2019-09-28)
-----------------
- Add *remind* script command.


1.14 (2019-04-28)
-----------------
- Allow title recognizers to be functions.
- Add --all option to :ref:`values command <values command>`.
- Add *vs* alias to :ref:`values command <values command>`.
- Add instructions on how to mimic Symantec VIP authentication app.


1.13 (2019-02-06)
-----------------
- Added :ref:`interactive command <interactive command>`.
- Added looping to :ref:`questions command <questions command>`.
- Retargeted *i* and *I* command aliases.
- Use natural sort order by default.
- Refactored code to speed up start up with account discovery.


1.12 (2019-01-17)
-----------------
- Updated the *networth* API example.
- Incorporated *shlib* package into *Avendesora* for better security.
- Added :ref:`questions command <questions command>`.
- Refactored code to speed up start up.


1.11 (2018-06-14)
-----------------
- Added *is_secret* argument to Secret classes.
- Added support for *dmenu* as alternative to built-in selection utility.
- Added --delete option to log command.
- Rename *master* and *seed* *Account* attributes to *master_seed* and *account_seed*.
- Improve  *portmortem* and *networth* api examples.
- Improve the account value formatting.


1.10 (2018-02-18)
-----------------
- Added support for *qutebrowser*.


1.9 (2017-12-25)
----------------
- Adds :ref:`one-time passwords <otp>` (an alternative to Google Authenticator).
- Added 'vc' command as an alias for 'value --clipboard'.


1.8 (2017-11-23)
----------------
- Created the manual.
- Use keyboard writer if there is no access to TTY.
- Shifted to skinny config file.
- Warn the user if the archive is missing or stale.
- Improved get_value(), added add get_values(), add get_fields().
- Canonicalize names.
- Allow account name to be given even if TTY is not available.
- Allow :ref:`default_field setting <default_field setting>` to be a list.
- Add render method to AccountValue.
- Changed the way multiple gpg ids are specified.
- Improved :ref:`browse command <browse command>`.
- Added shift_sort to password generators.
- Added :ref:`log command <log command>`.
- Added :ref:`phonetic command <phonetic command>`.
- Added browser version of :ref:`help command <help command>`.

It is recommended that in this release you trim your 
~/.config/avendesora/config file to only include those settings that you 
explicitly wish to override.


1.7 (2017-06-01)
----------------
- add :ref:`credentials command <credentials command>`.


1.6 (2017-04-07)
----------------
- Fix issues in sleep feature in autotype scripts.


1.5 (2017-03-01)
----------------
- Fixed bug in account discovery for URLs.
- Added get_composite, renamed get_field to get_scalar.


1.4 (2017-01-09)
----------------
- Improved error reporting on encrypted files.
- Added RecognizeFile().


1.3 (2017-01-08)
----------------
- Warn about duplicate account names.


1.2 (2017-01-05)
----------------


1.1 (2017-01-03)
----------------


1.0 (2017-01-01)
----------------
- Initial production release.
