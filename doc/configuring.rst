.. _configuring_avendesora:

Configuring
===========

Avendesora is configured by way of a collection of files contained in the config 
directory (~/.config/avendesora). This directory may contain the following 
files:


Configuration Files
-------------------

.. index::
    single: accounts_files file

.. _accounts_files file:

accounts_files
""""""""""""""

    This file contains the list of known account files. The first file in the 
    list is the default account file (this is where new accounts go by default).  
    You can use the :ref:`new command <new command>` to add additional files to 
    this list, but to delete account file you must manually edit this file and 
    remove them from the list.


.. index::
    single: config file
    single: config.doc file

.. _config file:

config, config.doc
""""""""""""""""""

    You control the behavior of Avendesora through a collection of settings that 
    are specified in *config*. The available settings and their default values 
    are documented in *config.doc*.  Generally you only place values in *config* 
    if you would like to change them from their default value. In that way, you 
    will get the latest values for all other settings when you update 
    Avendesora.


.. index::
    single: hashes file

.. _hashes file:

hashes
""""""

    One of the risks in using a password generator is that changed in the code 
    can result in the passwords changing. Thus there is a risk that when you 
    upgrade Avendesora that your passwords will change. Avendesora provides the 
    :ref:`archive <archive command>` and :ref:`changed <changed command>`  
    commands to help detect these situations.  It also keeps hashes of several 
    key parts of the code that if changed could result in the passwords 
    changing. When Avendesora runs, it recomputes these hashes on itself and 
    compares them to the hashes saved in this file. If any of the hashes have 
    changed a warning message is produced, which can alert you to changes that 
    you might have otherwise missed.

    It is normal that these hashes change when the program is updated. When you 
    see the message that the hashes have changed you should run the 
    :ref:`changed command <changed command>` to assure that none of your 
    generated secrets have changed.  This assumes that you have created an 
    archive file and kept it up to date.


.. index::
    single: stealth_accounts file

.. _stealth_accounts file:

stealth_accounts
""""""""""""""""

    This file contains the definitions of the available stealth accounts.  
    Stealth accounts allow you to create passwords for accounts that are not 
    kept in an account file.


.. index::
    single: account files

.. _accounts file:

<accounts file>
"""""""""""""""

    A file containing a collection of related accounts. All accounts in a file 
    share a common master seed.


.. index::
    single: archive file

.. _archive file:

<archive file>
""""""""""""""

    This file contains all known accounts with any generated secrets expanded.  
    It is used to identify account values that may have inadvertently changed.


.. index::
    single: log file

.. _log file:

<log file>
""""""""""

    The log file is created after each invocation of Avendesora. It provides 
    details about the run that can help understand what happened during the run, 
    which can help you resolve issues when things go wrong.  This file can leak 
    account information, and so it is best if it is encrypted.


.. _settings:
.. index::
    single: settings

Settings
--------

The settings are documented in *config.doc*, and can be overwritten by 
specifying the desired values in the *config* file (found in 
~/.config/avendesora).  The available settings are:


.. index::
    single: log_file setting

.. _log_file setting:

log_file
""""""""

    The desired name of the log file (relative to config directory).
    Adding a suffix of .gpg or .asc causes the file to be encrypted
    (otherwise it can leak account names). Use None to disable logging.

    The default is 'log.gpg'.


.. index::
    single: archive_file setting

.. _archive_file setting:

archive_file
""""""""""""

    The desired name of the archive file (relative to config director).
    End the path in .gpg or .asc. Use None to disable archiving.

    The default is 'archive.gpg'.


.. index::
    single: previous_archive_file setting

.. _previous_archive_file setting:

previous_archive_file
"""""""""""""""""""""

    The existing archive file is renamed to this name when updating the archive 
    file. This could be helpful if the archive file is somehow corrupted.

    The default is 'previous_archive_file'.


.. index::
    single: archive_stale setting

.. _archive_stale setting:

archive_stale
"""""""""""""

    The archive file is consider stale if it is this many days older than
    the most recently updated account file.

    The default is = 1.


.. index::
    single: default_field setting

.. _default_field setting:

default_field
"""""""""""""

    The name of the field to use for the :ref:`value command <value command>` 
    when one is not given. May be a space separated list of names, in which case 
    the first that is found is used.

    The default is 'passcode password passphrase'.


.. index::
    single: default_vector_field setting

.. _default_vector_field setting:

default_vector_field
""""""""""""""""""""

    The name of the field to use when an integer is given as the argument to the 
    :ref:`value command <value command>`. In this case the field is expected to 
    be a list and the argument is taken to be the index of the desired value.  
    For example, if default_vector_field is 'question' and the argument given 
    with the :ref:`value command <value command>` is 1, then question[1] is 
    produced.

    The default is 'questions'.


.. index::
    single: dynamic_fields setting

.. _dynamic_fields setting:

dynamic_fields
""""""""""""""

    Fields whose values can change in real time. These fields will not be 
    mentioned by the :ref:`changed command <changed command>`, even if their 
    value differs from when the most recent archive was created.

    The default is ''.


.. index::
    single: hidden_fields setting

.. _hidden_fields setting:

hidden_fields
"""""""""""""

    Names of fields that should not appear in the summary produced by the 
    :ref:`values <values command>` command unless the ``--all`` option is 
    specified.  A typical value includes *estimated_value*, 
    *postmortem_recipients*, and *bitwarden*.

    The default is ''.


.. index::
    single: credential_ids setting

.. _credential_ids setting:

credential_ids
""""""""""""""

    A string that contains the field names (space separated) that should be
    considered by the :ref:`credentials command <credentials command>` for the 
    account identity.

    The default is 'username email'.


.. index::
    single: credential_secrets setting

.. _credential_secrets setting:

credential_secrets
""""""""""""""""""

    A string that contains the field names (space separated) that should be
    considered by the :ref:`credentials command <credentials command>` for the 
    primary account secret.

    The default is 'passcode password passphrase email'.


.. index::
    single: display_time setting

.. _display_time setting:

display_time
""""""""""""

    The number of seconds that the secret will be displayed before it is
    erased when writing to the TTY or the clipboard.

    The default is 60.


.. index::
    single: ms_per_char setting

.. _ms_per_char setting:

ms_per_char
"""""""""""

    The time between keystrokes when autotyping. The default is 12ms.
    This is the global setting. Generally it is not necessary to change this. 
    Leaving at its default value works in most cases and result in a pleasingly 
    fast response times. However, some websites, particularly those that are 
    infested with javascript helpers, cannot tolerate extremely fast typing 
    rates. In these cases it is better to use the *rate* attribute to the 
    discovery :ref:`script <scripts>` to limit the typing rate. Doing so only 
    slows the entry of your credentials on those websites.

    The default is 12:


.. index::
    single: encoding setting

.. _encoding setting:

encoding
""""""""

    The unicode encoding to use when reading or writing files.

    The default is 'utf-8'.


.. index::
    single: edit_account setting

.. _edit_account setting:

edit_account
""""""""""""

    The command used when editing an account. The command is given as
    list of strings. The strings may contain {filepath} and {account},
    which are replaced by the path to the file and the name of the
    account.

    The default is suitable if you use *Vim*:

    .. code-block:: python

        edit_account = (
            'gvim',                       # use gvim -v so that user can access
            '-v',                         # the X clipboard buffers
            '+silent! /^class {account}(Account):/',
            '+silent! normal zozt',       # open the fold, position near top of screen
            '{filepath}'
        )


.. index::
    single: edit_template setting

.. _edit_template setting:

edit_template
"""""""""""""

    The command used when creating a new account that has been initialized
    with a template. The command is given as list of strings. The strings
    may contain {filepath}, which is replaced by the path to the file.

    The default is suitable if you use *Vim*:

    .. code-block:: python

        edit_template = (
            'gvim',                       # use gvim -v so that user can access
            '-v',                         # the X clipboard buffers
            r'+silent! /_[A-Z0-9_]\+_/',  # matches user modifiable template fields
                                          # fields take the form '_AAA_'
            '+silent! normal zozt',       # open the fold, position near top of screen
            '{filepath}'
        )


.. index::
    single: browsers setting

.. _browsers setting:

browsers
""""""""

    A dictionary containing the supported browsers. For each entry the key
    is the name to be used for the browser, and the value is string that
    contains the command that invokes the browser. The value may contain
    {url}, which is replaced by the URL to open.

    The default is:

    .. code-block:: python

        browsers = {
            'c': 'google-chrome {{url}}',
            'ci': 'google-chrome --incognito {{url}}',
            'f': 'firefox -new-tab {{url}}',
            'fp': 'firefox -private-window {{url}}',
            'q': 'qutebrowser {{url}}',
            't': 'torbrowser {{url}}',
            'x': 'xdg-open {{url}}',
        }


.. index::
    single: default_browser setting

.. _default_browser setting:

default_browser
"""""""""""""""

    The name of the default browser. This name should be one of the keys
    in the browsers dictionary.

    The default value is 'f'.


.. index::
    single: command_aliases setting
    single: command aliases
    single: aliases, command
    single: short cuts, command

.. _command_aliases setting:

command_aliases
"""""""""""""""

    You can create custom short cuts for *Avendesora* commands using the this 
    setting.  By default, *Avendesora* comes with a collection of aliases, but 
    you can change them, delete them, or add others.  Aliases are specified with 
    a dictionary, where the key is the alias, and the value is a list that 
    consists of full command name and an optional set of command line arguments.  
    For example:

    .. code-block:: python

        command_aliases = dict(
            b = ['browse'],
            bc = ['browse', '--browser', 'c'],
        )

    Alternately, you can specify the value of each alias as a string, in which 
    case it is split at white space to provide the command name and options:

    .. code-block:: python

        command_aliases = dict(
            b = 'browse',
            bc = 'browse --browser c',
        )

    In either case, the first item must be the name of a built-in command.

    With this set of aliases, 'b' becomes a short cut for 'browse' and 'bc' 
    becomes a short cut for 'browse --browser c'.

    With the introduction of this setting, the hard-coded command short cuts 
    were removed from *Avendesora* and replaced by the default value of this 
    setting:

    .. code-block:: python

        command_aliases = dict(
            a = 'add',
            A = 'archive',
            b = 'browse',
            bc = 'browse --browser c',
            c = 'conceal',
            C = 'changed',
            e = 'edit',
            f = 'find',
            h = 'help',
            ident = 'identity',
            I = 'identity',
            init = 'initialize',
            i = 'interactive',
            login = 'credentials',
            l = 'credentials',
            N = 'new',
            alphabet = 'phonetic',
            p = 'phonetic',
            quest = 'questions',
            q = 'questions',
            qc = 'questions --clipboard',
            r = 'reveal',
            s = 'search',
            val = 'value',
            v = 'value',
            vc = 'value --clipboard',
            vals = 'values',
            vs = 'values',
            V = 'values',
        )

    Specifying your own value for *command_aliases* overrides the built-in 
    default.  If you would like to add your own aliases, you should consider 
    specifying the above and then add in your new aliases.


.. index::
    single: default_protocol setting

.. _default_protocol setting:

default_protocol
""""""""""""""""

    The default protocol to use for a URL if the protocol is not specified
    in the requested URL. Generally this should be 'https' or 'http',
    though 'https' is recommended.

    The default is 'https'.


.. index::
    single: config_dir_mask setting

.. _config_dir_mask setting:

config_dir_mask
"""""""""""""""

    An integer that determines if the permissions of *Avendesora* configuration 
    directory (~/.config/avendesora) are too loose. If they are, a warning is 
    printed.  A bitwise *and* operation is performed between this value and the 
    actual file permissions, and if the result is nonzero, a warning is printed.  
    Set to 0o000 to disable the warning. Set to 0o077 to generate a warning if 
    the configuration directory is readable or writable by the group or others.  
    Set to 0o007 to generated a warning if the directory is readable or writable 
    by others.

    The default is 0o077.


.. index::
    single: account_file_mask setting

.. _account_file_mask setting:

account_file_mask
"""""""""""""""""

    An integer that determines if the permissions of *Avendesora* account files 
    are too loose. If they are, a warning is printed and the permissions are 
    changed.  A bitwise *and* operation is performed between this value and the 
    actual file permissions, and if the result is nonzero, a warning is printed.  
    Set to 0o000 to disable the warning. Set to 0o077 to generate a warning if 
    the configuration directory is readable or writable by the group or others.  
    Set to 0o007 to generated a warning if the directory is readable or writable 
    by others.

    The default is 0o077.


.. index::
    single: label_color setting

.. _label_color setting:

label_color
"""""""""""

    The color of the label used by the :ref:`value <value command>` and 
    :ref:`values <values command>` commands.
    Choose from 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 
    'white'.

    The default is 'blue'.


.. index::
    single: highlight_color setting

.. _highlight_color setting:

highlight_color
"""""""""""""""

    The color of the highlight used by the :ref:`value <value command>` and 
    :ref:`values <values command>` commands.
    Choose from 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 
    'white'.

    The default is 'magenta'.


.. index::
    single: color_scheme setting

.. _color_scheme setting:

color_scheme
""""""""""""

    The color scheme used for the label color.  Choose from 'dark', 'light' or 
    *None*.  If the shell background color is light, use 'dark'.

    The default is 'dark'.


.. index::
    single: use_pager setting

.. _use_pager setting:

use_pager
"""""""""
    Use a external program to break long output into pages.
    May be either a boolean or a string. If a string the string is taken
    to be a command line use to invoke a paging program (like 'more'). If
    *True*, the program name is taken from the *PAGER* environment variable if
    set, or *less* is used if not set. If *False*, a paging program is not
    used.

    The default is *True*.


.. index::
    single: selection_utility setting

.. _selection_utility setting:

selection_utility
"""""""""""""""""

    Which utility should be used when it becomes necessary for you to 
    interactively make a choice. Two utilities are available: *gtk*, the 
    default,  and *dmenu*.

    *gtk* is the built-in selection. When needed it pops a small dialog box in 
    the middle of the screen. You can use the *j* and *k* to navigate to your 
    selection and *l* to make the selection or *h* to cancel.  Alternately you 
    can use the arrow keys and *Enter* and *Esc* to navigate, select, and 
    cancel.

    *dmenu* is an external utility, and must be installed. With *dmenu* you type 
    the first few letters of your selection to highlight it, then type *Enter* 
    to select or *Esc* to cancel.

    The default is 'gtk'.


.. index::
    single: verbose setting

.. _verbose setting:

verbose
"""""""

    Set this to *True* to generate additional information in the log file
    that can help debug account discovery issues.  Normally it should be
    *False* to avoid leaking account information into log file.
    This is most useful when debugging account discovery, and in that case
    this setting has largely been superseded by the use of the ``--title`` and
    ``--verbose`` command line options.

    The default is *False*.


.. index::
    single: account_templates setting

.. _account_templates setting:

account_templates
"""""""""""""""""

    The available account templates. These are used when creating new accounts.  
    The templates are given as a dictionary where the key is the name of the 
    template and the value is the template itself. The template is passed 
    through *textwrap.dedent()* to remove any leading white space.  Any lines 
    that begin with '# Avendesora: ' represent comments that can contain 
    instructions to the user. They will are removed when the account is created.


.. index::
    single: default_account_template setting

.. _default_account_template setting:

default_account_template
""""""""""""""""""""""""

    The default account template that is used when creating a new account and 
    the user does not specify a template name.


.. index::
    single: gpg_ids setting

.. _gpg_ids setting:

gpg_ids
"""""""

    The GPG ID or IDs to use by default when creating encrypted files (the
    archive and account files).


.. index::
    single: gpg_armor setting

.. _gpg_armor setting:

gpg_armor
"""""""""
    In the GPG world, armoring a file means converting it to simple ASCII.
    Choose between 'always', 'never' and 'extension' (.asc: armor, .gpg:
    no).

    The default is 'extension'.


.. index::
    single: gpg_home setting

.. _gpg_home setting:

gpg_home
""""""""

    This is your GPG home directory. By default it will be ~/.gnupg.


.. index::
    single: gpg_executable setting

.. _gpg_executable setting:

gpg_executable
""""""""""""""

    Path to the *gpg2* executable.

    The default is */usr/bin/gpg2*.


.. index::
    single: xdotool_executable setting

.. _xdotool_executable setting:

xdotool_executable
""""""""""""""""""

    Path to the *xdotool* executable.

    The default is */usr/bin/xdotool*.

.. index::
    single: xsel_executable setting

.. _xsel_executable setting:

xsel_executable
"""""""""""""""

    External command that is used to place a value in the X selection buffer.
    Use '/usr/bin/xsel -p' if you wish to use the primary buffer (mouse middle 
    click).
    Use '/usr/bin/xsel -b' if you wish to use the clipboard buffer (*Ctrl-V* or 
    mouse right click then paste).

    The default is */usr/bin/xsel* (use *xsel* default, which is the primary 
    buffer).


.. index::
    single: dmenu_executable setting

.. _dmenu_executable setting:

dmenu_executable
""""""""""""""""

    Path to the *dmenu* executable.  *Avendesora* can be configured to use 
    *dmenu* as selection utility rather than built-in *gtk* version.

    The default is */usr/bin/dmenu*.
