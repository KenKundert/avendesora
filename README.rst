Avendesora Collaborative Password Utility
=========================================

*Avendesora, the leaf of the Tree of Life is the key.*

.. image:: https://img.shields.io/travis/KenKundert/avendesora/master.svg
    :target: https://travis-ci.org/KenKundert/avendesora

.. image:: https://img.shields.io/coveralls/KenKundert/avendesora.svg
    :target: https://coveralls.io/r/KenKundert/avendesora

.. image:: https://img.shields.io/pypi/v/avendesora.svg
    :target: https://pypi.python.org/pypi/avendesora

.. image:: https://img.shields.io/pypi/pyversions/avendesora.svg
    :target: https://pypi.python.org/pypi/avendesora/

.. image:: https://img.shields.io/pypi/dd/avendesora.svg
    :target: https://pypi.python.org/pypi/avendesora/

| Version: 1.0.0
| Released: 2017-01-01
|

Avendesora replaces the Abraxas, which are both alternatives to the traditional 
password vault.

Please report all bugs and suggestions to avendesora@nurdletech.com

Introduction
------------

Avendesora is powerful command-line utility that can securely hold and 
conveniently provide access to a wide variety of information about your online 
accounts, including its secrets such as passwords. Account values can be 
displayed, copied to the clipboard, or automatically typed into running 
applications such as you web browser or terminal windows.  Avendesora can also 
open accounts in your web browser, automatically recognize which account to use 
based on the window title, and warn you if you are not using encryption when you 
go to enter your password.

Account secrets can saved in encrypted form, as with password vaults, or 
generated from a root secret.  Generated secrets have two important benefits.  
First, they are produced from a random seed, and so are quite unpredictable.  
This is important, because the predictability of a passwords can be exploited 
when cracking passwords.  Second, if the root secret is shared with another 
trusted party, then you both can generate new shared secrets without passing any 
further secrets.

Secrets are generated from a collection of seeds, one of which must be random 
with a very high degree of entropy. The random seed is referred to as the 
'master seed'.  It is extremely important that the master seed remain completely 
secure.  Never disclose a master seed to anyone except for a person you wish to 
collaborate with, and then only used the shared master seed for shared secrets.  
All of your private secrets should be generated from private master seeds.  The 
seeds generally include the master seed, the account name, the secret name, and 
perhaps a version name.  For example, imagine having a Gmail account, then the 
account name might simply be 'gmail', and the secret name might be 'passcode'.  
In this case, your master seed is combined with the words 'gmail' and 
'passcode', the combination is hashed, and then password is generated with an 
appropriate recipe that you specify.  There are recipes for passwords, pass 
phrases, PINs, security questions, etc.  The password itself is not stored, 
rather it is the seeds that are stored and the password is regenerated when 
needed. Notice that all the seeds except the master seed need not be kept 
secure. Thus, once you have shared a master seed with a collaborator, all you 
need to do is share the remaining seeds and your collaborator can generate 
exactly the same password. Another important thing to notice is that the 
generated password is dependent on the account and secret names. Thus if you 
rename your account or your secret, the password will change.  So you should be 
careful when you first create your account to name it appropriately so you don't 
feel the need to change it in the future. For example, 'gmail' might not be 
a good account name if you expect to have multiple Gmail accounts. In this case 
you might want to include your username in the account name. You can always make 
the shorter 'gmail' as an account alias to you can still access the account 
quickly.


Installation
------------

Install with::

    pip3 install --user avendesora

This will place avendesora in ~/.local/bin, which should be added to your path.

You will also need to install some operating system commands. On Fedora use::

   yum install gnupg2 xdotool xsel

You should also install python-gobject. Conceivably this could be installed with 
the above pip command, but gobject appears broken in pypi, so it is better use 
the operating system's package manager to install it.  See the setup.py file for 
more information.  On Redhat systms use::

   yum install python3-gobject

If you would like to use scrypt as a way of encrypting fields, you will need to 
install scrypt by hand using::

   pip3 install --user scrypt


Upgrading
---------

Avendesora is a password generator rather than a password vault. As a result, 
there is always a chance that something could change in the password generation 
algorithm that causes the generated passwords to change. Of course, the program 
is thoroughly tested to assure this does not happen, but there is still a small 
chance that something slips through.  To assure that you are not affected by 
this, you should archive your passwords before you upgrade with::

    avendesora changed
    avendesora archive

The *changed* command should always be run before an *archive* command. It 
allows you to review all the changes that have occurred so that you can verify 
that they were all intentional.  Once you are comfortable, run the *archive* 
command to save all the changes.  Then upgrade with::

    pip install -upgrade --user avendesora

Finally, run::

    avendesora changed

to confirm that none of your generated passwords have changed.

It is a good idea to run 'avendesora changed' and 'avendesora archive' on 
a routine basis to keep your archive up to date.

Upon updating you may find that Avendesora produces a message that a 'hash' has 
changed.  This is an indication that something has changed in the program that 
could affect the generated secrets.  Again, care is taken when developing 
Avendesora to prevent this from happening.  But it is an indication that you 
should take extra care.  Specifically you should follow the above procedure to 
assure that the value of your generated secrets have not changed.  Once you have 
confirmed that the upgrade has not affected your generated secrets, you should 
follow the directions given in the warning and update the appropriate hash 
contained in ~/.config/avendesora/.hashes.


Requirements
------------

GPG
"""
To use Avendesora, you will need GPG and you will need a GPG ID that is 
associated with a private key. That GPG ID could be in the form of an email 
address or an ID string that can be found using 'gpg --list-keys'.

If you do not yet have a GPG key, you can get one using::

   $ gpg --gen-key

You should probably choose 4096 RSA keys. Now, edit ~/.gnupg/gpg-conf and add 
the line::

   use-agent

That way, you generally need to give your GPG key pass phrase less often. The 
agent remembers the passphrase for you for a time. So if you use the agent, be 
sure to also use screen locking so your passwords are secure when you walk away 
from your computer.

The ultimate in convenience is to use Gnome Keyring to act as the GPG agent 
because it allows you to unlock the agent simply by logging in.  To do so, make 
sure Keyring is installed::

   yum install gnome-keyring gnome-keyring-pam

If you are using Gnome, it will start Keyring for you. Otherwise, you should 
modify your .xinitrc or .xsession file to add the following::

    # Set ssh and gpg agent environment variables
    export $(gnome-keyring-daemon --start)


Vim
"""

If you use Vim, it is very helpful for you to install GPG support in Vim. To do 
so first download::

    http://www.vim.org/scripts/script.php?script_id=3645

Then copy the file into your Vim configuration hierarchy::

    cp gnupg.vim ~/.vim/plugin


Initialization
--------------

To operate, Avendesora needs a collection of configuration and accounts files 
that are stored in ~/.config/avendesora. To create this directory and the 
initial versions of these files, run::

    avendesora init -g <gpg_id>

For example::

    avendesora init -g bob@nurdletech.com

or::

    avendesora init -g 1B2AFA1C

If you would like to have more than one person access your passwords, you should 
give GPG IDs for everyone::

    avendesora init -g bob@nurdletech.com -g rob@nurdletech.com

After initialization, there should be several files in ~/.config/avendesora. In 
particular, you should see at least an initial accounts files and a config file.


Configuration
-------------

The config file (~/.config/avendesora/config) allows you to personalize 
Avendesora to your needs. After initializing your account you should take the 
time to review the config file and adjust it to fit your needs. You should be 
very thoughtful in this initial configuration, because some decisions (or 
nondecision) you make can be very difficult to change later.  The reason for 
this is that they may affect the passwords you generate, and if you change them 
you may change existing generated passwords. In particular, be careful with 
*dictionary_file* and *default_passphase_separator*. Changing these values when 
first initializing Avendesora is fine, but should not be done or done very 
carefully once you start creating accounts and secrets.

During an initial configuration is also a convenient time to determine which of 
your files should be encrypted with GPG. To assure that a file is encrypted, 
give it a GPG file suffix (.gpg or .asc). The appropriate settings to adjust 
are: *archive_file*, *log_file*, both of which are set in the config file, and 
the accounts files, which are found in ~/.config/avendesora/.accounts_files. For 
security reasons it is highly recommended that the archive file be encrypted, 
and any accounts file that contain sensitive accounts. If you change the suffix 
on an accounts file and you have not yet placed any accounts in that file, you 
can simply delete the existing file and then regenerate it using::

    avendesora init -g <gpg_id>

Any files that already exist will not be touched, but any missing files will be 
recreated, and this time they will be encrypted or not based on the extensions 
you gave.


Accounts
--------

Avendesora holds information about your accounts in accounts files. The list of 
current accounts files is contained in ~/.config/avendesora/.accounts_files.  
Each is a possibly encrypted Python file. All information known about 
a particular account is contained in the attributes of a class that is created 
for that account. For example:

.. code-block:: python

    class BigBank(Account):
        aliases = 'bb'
        username = 'gman33'
        email = 'gman33@pizza.com'
        url = 'https://bigbank.com/login'
        passcode = Password(length=12)
        verbal = Passphrase(length=2)
        pin = PIN()
        accounts = {
            'checking':   Hidden('MTIzNDU2Nzg='),
            'savings':    Hidden('MjM0NTY3ODk='),
            'creditcard': Hidden('MzQ1Njc4OTA='),
        }
        questions = [
            Question('What city were you born in?'),
            Question('What street did you grow up on?'),
            Question('What was your childhood nickname?'),
        ]
        customer_service = '1-866-229-6633'

Each attribute represents a piece of information that can be requested. For 
example, a summary of all information can be requested with::

    > avendesora values bb
    names: bigbank, bb
    accounts:
        checking: <reveal with 'avendesora show bigbank accounts.checking'>
        creditcard: <reveal with 'avendesora show bigbank accounts.creditcard'>
        savings: <reveal with 'avendesora show bigbank accounts.savings'>
    customer service: 1-866-229-6633
    email: gman33@pizza.com
    passcode: <reveal with 'avendesora show bigbank passcode'>
    pin: <reveal with 'avendesora show bigbank pin'>
    questions:
        0: What city were you born in? <reveal with 'avendesora show bigbank questions.0'>
        1: What street did you grow up on? <reveal with 'avendesora show bigbank questions.1'>
        2: What was your childhood nickname? <reveal with 'avendesora show bigbank questions.2'>
    url: https://bigbank.com/login
    username: gman33
    verbal: <reveal with 'avendesora show bigbank verbal'>

The attributes have various levels of confidentiality.  Simple strings are not 
considered sensitive. Those values provided by Python classes inherit the 
confidentiality of the class.  Hide() and Hidden() provides simple concealment.  
GPG() and Scrypt() provides full encryption. And classes like Password(), 
PasswordRecipe(), Passphrase(), PIN() and Question() generate secrets.  
Attributes that are considered sensitive are not shown in the above summary, but 
can be requested individually::

    > avendesora value bb pin
    pin: 7784

Attributes can be simple scalars, such as *pin*. They can be arrays, such as 
*questions*::

    > avendesora value bigbank questions.1
    questions.1 (What street did you grow up on?): lockout insulator crumb

Or they can be dictionaries::

    > avendesora value bb accounts.checking
    accounts.checking: 12345678

The passcode attribute is the default scalar attribute::

    > avendesora value bb
    passcode: Nj3gpqHNfiie

The questions attribute is the default array attribute, which is used if the 
requested field is a number::

    > avendesora value bb 0
    questions.0 (What city were you born in?): muffin favorite boyfriend

You can also use simple scripts as the requested value::

    > avendesora value 'username: {username}, password: {passcode}'
    username: gman33, password: Nj3gpqHNfiie

Finally, you can use a script for the value of the *default* attribute on the 
account, then the script is used to generate the output when no attribute is 
requested::

    > avendesora value
    username: gman33, password: Nj3gpqHNfiie


Adding And Editing Accounts
---------------------------

You add new accounts using the *add* command::

    > avendesora add [<template>]

The available templates can be found using::

    > avendesora help add

You can add new templates or edit the existing templates by changing 
*account_templates* in ~/.config/avendesora/config.

The *add* command will open your editor (set this with the *edit_template* 
setting in the config file). If you are using default version of *edit_template* 
the template will be opened in Vim with the *n* key is mapped to take you to the 
next field. You can edit any part of the template you like, but at a minimum you 
need to edit the fields.

Once an account exists, you can edit it using::

    > avendesora edit [<account>]

This opens the accounts file with your editor (set this with the *edit_account* 
setting in the config file). If you are using default version of *edit_account*, 
which uses VIM, it should take you directly to the account.


Finding Accounts
----------------

There are two ways of finding accounts. First, you can list any accounts whose 
name or aliases contains a text fragment. For example::

    > avendesora find bank
    bank:
        bankofamerica (boa)

Second, you can list any accounts that contain a text fragment in any non-secret 
field. For example::

    > avendesora search 4408
    4408:
        bankofamerica (boa)


Autotyping Passwords
--------------------

There are a couple of things that must be done to enable autotyping of 
passwords. First, at least some secrets must be configured for discovery.  
Discovery allows secrets to determine whether they are good candidates for use 
in a particular situation based on the environment. The environment includes 
such things as with title of the active window, the user name, the host name, 
etc.  If multiple secrets are suitable, a small window pops up and lets you 
choose between them. To see how to configure secrets for discovery, run 
'avendesora help discovery'.

To make secret discovery easier and more robust it is helpful to add a plugin to 
your web browser to make its title more informative. For Firefox, the best 
plugin to use is AddURLToWindowTitle. For Chrome it is URLinTitle. It is 
recommended that you install the appropriate one into your browser. For 
AddURLToWindowTitle, set the following options:

  | show full URL = yes
  | separator string = '-'
  | show field attributes = no

For URLinTitle, set:

  | tab title format = '{title} - {protocol}://{hostname}{port}/{path}'

Finally, you need to configure your window manager to run Avendesora when you 
type a special hot key, such as ``Alt p``.  The idea is that you are in 
a situation where you need a secret, such as visiting your bank's website in 
your browser, then you click on the account name field with your mouse and type 
your hot key. This runs Avendesora without an account name. In this case, 
Avendesora uses secret discovery to determine which secret to use and the script 
that should be used to produce the required information. Generally the script 
would be to enter the account name, then tab, then the password, and finally 
return, but you can configure the script as you choose. This is all done as part 
of configuring discovery. The method for associating Advendesora to a particular 
hot key is dependent on your window manager. With Gnome, it requires that you 
open your Keyboard Shortcuts preferences and create a new shortcut. When you do 
this, choose 'avendesora value' as the command to run.


Python API
----------

You can access account information from Avendesora using Python using a simple 
relatively high-level interface as shown in this example:

.. code-block:: python

    from avendesora import PasswordGenerator, PasswordError
    from inform import display, fatal, os_error
    from shlib import Run
    from pathlib import Path

    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        name = account.get_value('NAME')
        username = account.get_value('username')
        passcode = account.get_value('passcode')
        url = account.get_value('ofxurl')
    except PasswordError as err:
        fatal(err)

    try:
        curl = Run(f'curl --user {username!s}:{passcode!s} {url!s}', 'sOEW0')
        Path(f'{name!s}.ofx').write_text(curl.stdout)
    except OSError as err:
        fatal(os_error(err))


PasswordGenerator:

    Initializes the password generator.

get_account:

    Accesses a particular account. Takes a string for the account name or alias.  
    Optionally takes a second string that is used as an additional seed.

get_value:

    Returns the value of a particular account attribute given a user-oriented 
    string that describes the desired attribute.  The value requested must be 
    a scalar value, meaning that you must individually request members of arrays 
    or dictionary attibutes. Here are some examples that demonstrate the various 
    ways of accessing the various kinds of attributes::

        passcode = account.get_value()
        username = account.get_value('username')
        both = account.get_value('username: {username}, password: {passcode}')
        checking = account.get_value('accounts.checking')
        savings = account.get_value('accounts[checking]')
        answer0 = account.get_value(0)
        answer1 = account.get_field('questions.1')
        answer2 = account.get_value('questions[2]')

    The value is returned as an object that contains three attributes, value 
    (the actual value), is_secret (whether the value is secret or contains 
    a secret) and label (a descriptive name for the value if the value of 
    a simple field is requested). Converting the object to a string returns the 
    value rendered as a string. There is also a render method that returns 
    a string that combines the label with the value.


Getting Help
------------

The *help* command provides information on how to use Avendesora's various 
features.  To get a listing of the topics available, use::

    avendesora help

Then, for information on a specific topic use::

    avendesora help <topic>

It is worth browsing all of the available topics at least once to get a sense of 
all that Avendesora can do.
