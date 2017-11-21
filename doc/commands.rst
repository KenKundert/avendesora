Command Reference
=================

.. index::
    single: add command
    single: command; add

.. _add command:

**add** -- Add a new account
----------------------------

Usage::

    avendesora add [options] [<template>]
    avendesora a   [options] [<template>]

Options:

    ======================== =======================================
    -f <file>, --file <file> Add account to specified accounts file.
    ======================== =======================================

Creates a new account starting from a template. The template consists of
boilerplate code and fields. The fields take the from _NAME_. They
should be replaced by appropriate values or deleted if not needed. If
you are using the Vim editor, it is preconfigured to jump to the next
field when you press 'n'.  If the field is surrounded by '<<' and '>>',
as in '<<_ACCOUNT_NUMBER_>>', the value you enter will be concealed.

You can create your own templates by adding them to 'account_templates'
in the ~/.config/avendesora/config file.

You can change the editor used when adding account by changing the
'edit_template', also found in the ~/.config/avendesora/config file.

The default template is bank. The available templates are: bank, shell, and 
website.


.. index::
    single: archive command
    single: command; archive
    single: archive file

.. _archive command:

**archive** -- Generates archive of all account information
-----------------------------------------------------------

Usage::

    avendesora archive
    avendesora A

This command creates an encrypted archive that contains all the information in 
your accounts files, including the fully generated secrets.  You should never 
need this file, but its presence protects you in case you lose access to 
Avendesora. To access your secrets without Avendesora, simply decrypt the 
archive file with GPG.  The

without Avendesora. When hidden, the secrets are encoded in base64.  You can 
decode it by running 'base64 -d -' and pasting the encoded secret into the 
terminal.

When you run this command it overwrites the existing archive. If you have 
accidentally deleted an account or changed a secret, then replacing the archive 
could cause the last copy of the original information to be lost. To prevent 
this from occurring it is a good practice to run the :ref:`changed command 
<changed command>` before regenerating the archive.  It describes all of the 
changes that have occurred since the last time the archive was generated. You 
should only regenerate the archive once you have convinced yourself all of the 
changes are as expected.


.. index::
    single: browse command
    single: browse; add

.. _browse command:

**browse** -- Open account URL in web browser
---------------------------------------------

Usage::

    avendesora browse [options] <account> [<key>]
    avendesora b      [options] <account> [<key>]

Options:

    ================================= =======================================
    -b <browser>, --browser <browser> Open account in specified browser.
    -l, --list                        List available URLs rather than open 
                                      first.
    ================================= =======================================

The account is examined for URLS, a URL is chosen, and then that URL is opened 
in the chosen browser.  First URLS are gathered from the 'urls' account 
attribute, which can be a string containing one or more URLS, a list, or 
a dictionary.  If 'urls' is a dictionary, the desired URL can be chosen by 
entering the key as an argument to the :ref:`browse command <browse command>`. 
If a key is not given, then the 'default_url' account attribute is used to 
specify the key to use by default. If 'urls' is not a dictionary, then the first 
URL specified is used.  URLs are also taken from RecognizeURL objects in the 
'discovery' account attribute.  If the 'name' argument is specified, the 
corresponding URL can be chosen using a key.

The default browser is x. You can override the default browser on a per-account 
basis by adding an attribute named 'browser' to the account.  An example of when 
you would specify the browser in an account would be an account associated with 
Tor hidden service, which generally can only be accessed using torbrowser:

.. index::
    single: changed command
    single: changed; add
    single: archive file

.. code-block:: python

    class SilkRoad(Account):
        passcode = Passphrase()
        username = Passphrase(length=2, sep='-')
        url = 'http://silkroad6ownowfk.onion'
        browser = 't'


.. _changed command:

**changed** -- Show changes since archive was created
-----------------------------------------------------

Usage:

|   avendesora changed
|   avendesora C

When you run the :ref:`archive command <archive command>` it overwrites the 
existing archive. If you have accidentally deleted an account or changed 
a secret, then replacing the archive could cause the last copy of the original 
information to be lost. To prevent this from occurring it is a good practice to 
run the :ref:`changed command <changed command>` before regenerating the 
archive.  It describes all of the changes that have occurred since the last time 
the archive was generated.  You should only regenerate the archive once you have 
convinced yourself all of the changes are as expected.


.. index::
    single: conceal command
    single: command; conceal

.. _conceal command:

**conceal** -- Conceal text by encoding it
------------------------------------------

Usage::

    avendesora conceal [options] [<text>]
    avendesora c       [options] [<text>]

Options:

    ==================================== ======================================
    -e <encoding>, --encoding <encoding> Encoding used when concealing 
                                         information.
    -g <id>, --gpg-id <id>               Use this ID when creating any missing
                                         encrypted files.  Use commas with no
                                         spaces to separate multiple IDs.
    -h <path>, --gpg-home <path>         GPG home directory (default is
                                         ~/.gnupg).
    -s, --symmetric                      Encrypt with a passphrase rather than 
                                         using your GPG key (only appropriate 
                                         for gpg encodings).
    ==================================== ======================================

Possible encodings include (default encoding is base64):

gpg:
    This encoding fully encrypts/decrypts the text with GPG key.
    By default your GPG key is used, but you can specify symmetric
    encryption, in which case a passphrase is used.

base64:
    This encoding obscures but does not encrypt the text. It can
    protect text from observers that get a quick glance of the
    encoded text, but if they are able to capture it they can easily
    decode it.

scrypt:
    This encoding fully encrypts the text with your user key. Only
    you can decrypt it, secrets encoded with scrypt cannot be shared.

Though available as an option for convenience, you should not pass
the text to be hidden as an argument as it is possible for others to
examine the commands you run and their argument list. For any
sensitive secret, you should simply run 'avendesora conceal' and
then enter the secret text when prompted.


.. index::
    single: credentials command
    single: login command
    single: command; credentials
    single: command; login

.. _credentials command:

**credentials** -- Show login credentials
-----------------------------------------

Displays the account's login credentials, which generally consist of an
identifier and a secret.

Usage::

    avendesora credentials [options] <account>
    avendesora login       [options] <account>
    avendesora l           [options] <account>

Options:

    ======================= ==========================================
    -S, --seed              Interactively request additional seed for
                            generated secrets.
    ======================= ==========================================

The credentials can be specified explicitly using the credentials
setting in your account. For example::

    credentials = 'usernames.0 usernames.1 passcode'

If credentials is not specified then the first of the following will
be used if available:

|   id: username or email
|   secret: passcode, password or passphrase


.. index::
    single: edit command
    single: command; edit

.. _edit command:

**edit** -- Edit an account
---------------------------

Usage::

    avendesora edit <account>
    avendesora e    <account>

Opens an existing account in your editor.

You can specify the editor by changing the 'edit_account' setting in
the config file (~/.config/avendesora/config).


.. index::
    single: find command
    single: command; find

.. _find command:

**find** -- Find an account
---------------------------

Find accounts whose name contains the search text.

Usage::
    avendesora find <text>
    avendesora f    <text>


.. index::
    single: help command
    single: command; help

.. _help command:

**help** -- Give information about commands or other topics
-----------------------------------------------------------

Usage::
    avendesora help [options] [<topic>]
    avendesora h    [options] [<topic>]

Options:

    ======================= ==================================================
    -s, --search            list topics that include <topic> as a search term.
    -b, --browse            open the topic in your default browser.
    ======================= ==================================================


.. index::
    single: identity command
    single: command; identity

.. _identity command:

**identity** -- Generate an identifying response to a challenge
---------------------------------------------------------------

Usage::

    avendesora identity [<name> [<challenge>...]]
    avendesora ident    [<name> [<challenge>...]]
    avendesora i        [<name> [<challenge>...]]

This command allows you to generate a response to any challenge.
The response identifies you to a partner with whom you have shared
an account.

If you run the command with no arguments, it prints the list of
valid names. If you run it with no challenge, one is created for you
based on the current time and date.

If you have a remote partner to whom you wish to prove your
identity, have that partner use avendesora to generate a challenge
and a response based on your shared secret. Then the remote partner
provides you with the challenge and you run avendesora with that
challenge to generate the same response, which you provide to your
remote partner to prove your identity.

You are free to explicitly specify a challenge to start the process,
but it is important that it be unpredictable and that you not use
the same challenge twice. As such, it is recommended that you not
provide the challenge. In this situation, one is generated for you
based on the time and date.

Consider an example that illustrates the process. In this example,
Ahmed is confirming the identity of Reza, where both Ahmed and Reza
are assumed to have shared Avendesora accounts.  Ahmed runs
Avendesora as follows and remembers the response::

    > avendesora identity reza
    challenge: slouch emirate bedeck brooding
    response: spear disable local marigold

This assumes that reza is the name, with any extension removed, of
the file that Ahmed uses to contain their shared accounts.

Ahmed communicates the challenge to Reza but not the response.  Reza
then runs Avendesora with the given challenge::

    > avendesora identity ahmed slouch emirate bedeck brooding
    challenge: slouch emirate bedeck brooding
    response: spear disable local marigold

In this example, ahmed is the name of the file that Reza uses to
contain their shared accounts.

To complete the process, Reza returns the response to Ahmed, who compares it to 
the response he received to confirm Reza's identity.  If Ahmed has forgotten the 
desired response, he can also specify the challenge to the :ref:`identity 
command <identity command>` to regenerate the expected response.


.. index::
    single: initialize command
    single: command; initialize

.. _initialize command:

**initialize** -- Create initial set of Avendesora files
--------------------------------------------------------

Usage::

    avendesora initialize [options]
    avendesora init       [options]
    avendesora I          [options]

Options:
    ============================ ==============================================
    -g <id>, --gpg-id <id>       Use this ID when creating any missing encrypted 
                                 files.  Use commas with no spaces to separate 
                                 multiple IDs.
    -h <path>, --gpg-home <path> GPG home directory (default is ~/.gnupg).
    ============================ ==============================================

Create Avendesora data directory (~/.config/avendesora) and populate
it with initial versions of all essential files.

It is safe to run this command even after the data directory and
files have been created. Doing so will simply recreate any missing
files.  Existing files are not modified.


.. index::
    single: log command
    single: command; log
    single: log file

.. _log command:

**log** -- Open the logfile
---------------------------

Usage::

    avendesora log

Opens the logfile in your editor.

You can specify the editor by changing the 'edit_account' setting in the config 
file (~/.config/avendesora/config).


.. index::
    single: new command
    single: command; new

.. _new command:

**new** -- Create new accounts file
-----------------------------------

Usage::

    avendesora new [options] <name>
    avendesora N   [options] <name>

Options:

    ======================= ======================================================
    -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
                            Use commas with no spaces to separate multiple IDs.
    ======================= ======================================================

Creates a new accounts file. Accounts that share the same file share
the same master seed by default and, if the file is encrypted,
can be decrypted by the same recipients.

Generally you create new accounts files for each person or group
with which you wish to share accounts. You also use separate files
for passwords with different security domains. For example, a
high-value passwords might be placed in an encrypted file that would
only be placed highly on protected computers. Conversely, low-value
passwords might be contained in perhaps an unencrypted file that is
found on many computers.

Add a '.gpg' extension to <name> to encrypt the file.


.. index::
    single: phonetic command
    single: command; phonetic
    single: alphabet command
    single: command; alphabet

.. _phonetic command:

**phonetic** -- Display NATO phonetic alphabet
----------------------------------------------

Usage::

    avendesora alphabet [<text>]
    avendesora phonetic [<text>]
    avendesora p [<text>]

If <text> is given, any letters are converted to the phonetic alphabet. If not 
given the entire phonetic is displayed.

Example::

    > avendesora phonetic 2WQI1T
    two whiskey quebec india one tango

    > avendesora phonetic
    Phonetic alphabet:
        Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
        Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
        Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
        Delta     Hotel     Lima      Papa      Tango     X-ray


.. index::
    single: reveal command
    single: command; areveal

.. _reveal command:

**reveal** -- Reveal concealed text
-----------------------------------

Transform concealed text to reveal its original form.

Usage::

    avendesora reveal [<text>]
    avendesora r      [<text>]

Options:
    ==================================== =========================================
    -e <encoding>, --encoding <encoding> Encoding used when revealing information.
    ==================================== =========================================

Though available as an option for convenience, you should not pass
the text to be revealed as an argument as it is possible for others
to examine the commands you run and their argument list. For any
sensitive secret, you should simply run 'avendesora reveal' and then
enter the encoded text when prompted.


.. index::
    single: search command
    single: command; search

.. _search command:

**search** -- Search accounts
-----------------------------

Search for accounts whose values contain the search text.

Usage::

    avendesora search <text>
    avendesora s      <text>


.. index::
    single: value command
    single: command; value

.. _value command:

**value** -- Show an account value
----------------------------------

Produce an account value. If the value is secret, it is produced only
temporarily unless --stdout is specified.

Usage::

    avendesora value [options] [<account> [<field>]]
    avendesora val   [options] [<account> [<field>]]
    avendesora v     [options] [<account> [<field>]]

Options:
    =========================== =============================================
    -c, --clipboard             Write output to clipboard rather than stdout.
    -s, --stdout                Write output to the standard output without
                                any annotation or protections.
    -S, --seed                  Interactively request additional seed for
                                generated secrets.
    -v, --verbose               Add additional information to log file to
                                help identify issues in account discovery.
    -T <title>, --title <title> Use account discovery on this title.
    =========================== =============================================

You request a scalar value by specifying its name after the account.
For example::

    avendesora value bank pin

If the requested value is composite (an array or dictionary), you should
also specify a key that indicates which of the composite values you
want. For example, if the 'accounts' field is a dictionary, you specify
accounts.checking or accounts[checking] to get information on your
checking account. If the value is an array, you give the index of the
desired value. For example, questions.0 or questions[0]. If you only
specify a number, then the name is assumed to be 'questions', as in the
list of security questions (this can be changed by specifying the
desired name as the 'default_vector_field' in the account or the config
file).

The field may be also be a script, with is nothing but a string that it
output as given except that embedded attributes are replaced by account
field values. For example::

    avendesora value bank '{accounts.checking}: {passcode}'

If no value is requested the result produced is determined by the value
of the 'default' attribute. If no value is given for 'default', then the
'passcode' attribute is produced (this can be changed by specifying
'default_field' in the config file).  If 'default' is a script (see
'avendesora help scripts') then the script is executed. A typical script
might be 'username: {username}, password: {passcode}'. It is best if the
script produces a one line output if it contains secrets. If not a
script, the value of 'default' should be the name of another attribute,
and the value of that attribute is shown.

If no account is requested, then Avendesora attempts to determine the
appropriate account through discovery (see 'avendesora help discovery').
Normally Avendesora is called in this manner from your window manager.
You would arrange for it to be run when you type a hot key. In this case
Avendesora determines which account to use from information available
from the environment, information like the title on active window. In
this mode, Avendesora mimics the keyboard when producing its output.

The verbose and title options are used when debugging account
discovery. The verbose option adds more information about the
discovery process to the logfile (~/.config/avendesora/log.gpg). The
title option allows you to override the active window title so you can
debug title-based discovery. Specifying the title option also scrubs
the output and outputs directly to the standard output rather than
mimicking the keyboard so as to avoid exposing your secret.


.. index::
    single: values command
    single: command; values

.. _values command:

**values** -- Display all account values
----------------------------------------

Show all account values.

Usage::

    avendesora values <account>
    avendesora vals   <account>
    avendesora V      <account>


.. index::
    single: add command
    single: None

.. _version command:

**version** -- Display Avendesora version
-----------------------------------------

Usage::

    avendesora version
