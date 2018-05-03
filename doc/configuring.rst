.. _configuring:

Configuring
===========

Avendesora is configured by way of a collection of files contained in the config 
directory (~/.config/avendesora). This directory may contain the following 
files:

.. index::
    single: accounts_files file

**accounts_files**:

    This file contains the list of known account files. The first file in the 
    list is the default account file (this is where new accounts go by default).  
    You can use the :ref:`new command <new command>` to add additional files to 
    this list, but to delete account file you must manually edit this file and 
    remove them from the list.

.. index::
    single: config file
    single: config.doc file

**config** and **config.doc**:

    You control the behavior of Avendesora through a collection of settings that 
    are specified in *config*. The available settings and their default values 
    are documented in *config.doc*.  Generally you only place values in *config* 
    if you would like to change them from their default value. In that way, you 
    will get the latest values for all other settings when you update 
    Avendesora.

.. index::
    single: hashes file

**hashes**:

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

**stealth_accounts**:

    This file contains the definitions of the available stealth accounts.  
    Stealth accounts allow you to create passwords for accounts that are not 
    kept in an account file.

.. index::
    single: account files

*account files*:

    A file containing a collection of related accounts. All accounts in a file 
    share a common master seed.

.. index::
    single: archive file

*archive file*:

    This file contains all known accounts with any generated secrets expanded.  
    It is used to identify account values that may have inadvertently changed.

.. index::
    single: log file

*log file*:

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

**log_file** = log.gpg:

    The desired location of the log file (relative to config directory).
    Adding a suffix of .gpg or .asc causes the file to be encrypted
    (otherwise it can leak account names). Use None to disable logging.


.. index::
    single: archive_file setting

**archive_file** = archive.gpg:

    The desired location of the archive file (relative to config director).
    End the path in .gpg or .asc. Use None to disable archiving.


.. index::
    single: previous_archive_file setting

**previous_archive_file** = archive.prev.gpg:

    The existing archive file is renamed to this name when updating the archive 
    file. This could be helpful if the archive file is somehow corrupted.


.. index::
    single: archive_stale setting

**archive_stale** = 1:

    The archive file is consider stale if it is this many days older than
    the most recently updated account file.


.. index::
    single: default_field setting

**default_field** = 'passcode password passphrase':

    The name of the field to use for the :ref:`value command <value command>` 
    when one is not given. May be a space separated list of names, in which case 
    the first that is found is used.


.. index::
    single: default_vector_field setting

**default_vector_field** = 'questions':

    The name of the field to use when an integer is given as the argument to the 
    :ref:`value command <value command>`. In this case the field is expected to 
    be a list and the argument is taken to be the index of the desired value.  
    For example, if default_vector_field is 'question' and the argument given 
    with the :ref:`value command <value command>` is 1, then question[1] is 
    produced.


.. index::
    single: dynamic_fields setting

**dynamic_fields = '':

    Fields whose values can change in real time. These fields will not be 
    mentioned by the :ref:`changed command <changed command>`, even if their 
    value differs from when the most recent archive was created.


.. index::
    single: credential_ids setting

**credential_ids** = 'username email':

    A string that contains the field names (space separated) that should be
    considered by the :ref:`credentials command <credentials command>` for the 
    account identity.


.. index::
    single: credential_secrets setting

**credential_secrets** = 'passcode password passphrase':

    A string that contains the field names (space separated) that should be
    considered by the :ref:`credentials command <credentials command>` for the 
    primary account secret.


.. index::
    single: display_time setting

**display_time** = 60:

    The number of seconds that the secret will be displayed before it is
    erase when writing to the TTY or clibboard.


.. index::
    single: encoding setting

**encoding** = 'utf-8':
    The unicode encoding to use when reading or writing files.


.. index::
    single: edit_account setting

**edit_account**:

    The command used when editing an account. The command is given as
    list of strings. The strings may contain {filepath} and {account},
    which are replaced by the path to the file and the name of the
    account.


.. index::
    single: edit_template setting

**edit_template**:

    The command used when creating a new account that has been initialized
    with a template. The command is given as list of strings. The strings
    may contain {filepath}, which is replaced by the path to the file.


.. index::
    single: browsers setting

**browsers**:

    A dictionary containing the supported browsers. For each entry the key
    is the name to be used for the browser, and the value is string that
    contains the command that invokes the browser. The value may contain
    {url}, which is replaced by the URL to open.


.. index::
    single: default_browser setting

**default_browser**:

    The name of the default browser. This name should be one of the keys
    in the browsers dictionary.


.. index::
    single: default_protocol setting

**default_protocol** = 'https':

    The default protocol to use for a URL if the protocol is not specified
    in the requested URL. Generally this should be 'https' or 'http',
    though 'https' is recommended.


.. index::
    single: config_dir_mask setting

**config_dir_mask** = 0o077:

    An integer that determines if the permissions of *Avendesora* configuration 
    directory (~/.config/avendesora) are too loose. If they are, a warning is 
    printed.  A bitwise *and* operation is performed between this value and the 
    actual file permissions, and if the result is nonzero, a warning is printed.  
    Set to 0o000 to disable the warning. Set to 0o077 to generate a warning if 
    the configuration directory is readable or writable by the group or others.  
    Set to 0o007 to generated a warning if the directory is readable or writable 
    by others.


.. index::
    single: label_color setting

**label_color** = 'blue':

    The color of the label use by the value and values commands.
    Choose from black, red, green, yellow, blue, magenta, cyan, white.


.. index::
    single: highlight_color setting

**highlight_color** = 'magenta':

    The color of the highlight use by the value and values commands.
    Choose from black, red, green, yellow, blue, magenta, cyan, white.


.. index::
    single: color_scheme setting

**color_scheme** = 'dark':

    The color scheme used for the label color.  Choose from dark, light.
    If the shell background color is light, use dark.


.. index::
    single: use_pager setting

**use_pager** = True:
    Use a external program to break long output into pages.
    May be either a boolean or a string. If a string the string is taken
    to be a command line use to invoke a paging program (like 'more'). If
    True, the program name is taken from the PAGER environment variable if
    set, or 'less' is used if not set. If False, a paging program is not
    used.


.. index::
    single: selection_utility setting

**selection_utility** = 'gtk':
    Which utility should be used when it becomes necessary for you to 
    interactively make a choice. Two utilities are available: *gtk*, the 
    default,  and *dmenu*.  

    *gtk* is the built-in selection. When needed it pops a small dialog box in 
    the middle of the screen. You can use the 'j' and 'k' to navigate to your 
    selection and 'l' to make the selection or 'h' to cancel.  Alternately you 
    can use the arrow keys and Enter and Esc to navigate, select, and cancel.

    *dmenu* is an external utility, and must be installed. With *dmenu* you type 
    the first few letters of your selection to highlight it, then type 'Enter' 
    to select or 'Esc' to cancel.


.. index::
    single: verbose setting

**verbose** = False:

    Set this to True to generate additional information in the log file
    that can help debug account discovery issues.  Normally it should be
    False to avoid leaking account information into log file.
    This is most useful when debugging account discovery, and in that case
    this setting has largely been superseded by the use of the --title and
    --verbose command line options.


.. index::
    single: account_templates setting

**account_templates**:

    The available account templates. These are used when creating new accounts.  
    The templates are given as a dictionary where the key is the name of the 
    template and the value is the template itself. The template is passed 
    through textwrap.dedent() to remove any leading white space.  Any lines that 
    begin with '# Avendesora: ' represent comments that can contain instructions 
    to the user. They will are removed when the account is created.


.. index::
    single: default_account_template setting

**default_account_template** = 'bank'

    The default account template that is used when creating a new account and 
    the user does not specify a template name.


.. index::
    single: gpg_ids setting

**gpg_ids**:

    The GPG ID or IDs to use by default when creating encrypted files (the
    archive and account files).


.. index::
    single: gpg_armor setting

**gpg_armor** = 'extension':
    In the GPG world, armoring a file means converting it to simple ASCI.
    Choose between 'always', 'never' and 'extension' (.asc: armor, .gpg:
    no).


.. index::
    single: gpg_home setting

**gpg_home** = ~/.gnupg:

    This is your GPG home directory. By default it will be ~/.gnupg.


.. index::
    single: gpg_executable setting

**gpg_executable** = /usr/bin/gpg2:

    Path to the *gpg2* executable.


.. index::
    single: xdotool_executable setting

**xdotool_executable** = /usr/bin/xdotool:

    Path to the *xdotool* executable.


.. index::
    single: xsel_executable setting

**xsel_executable** = /usr/bin/xsel:

    Recommend '/usr/bin/xsel -p' if you wish to use mouse middle click.
    Recommend '/usr/bin/xsel -b' if you wish to use mouse right click then 
    paste.


.. index::
    single: dmenu_executable setting

**dmenu_executable** = /usr/bin/dmenu:

    Path to the *dmenu* executable.  *Avendesora* can be configured to use 
    *dmenu* as selection utility rather than built-in *gtk* version.

