Avendesora Collaborative Password Utility
=========================================

"Avendesora, the leaf of the Tree of Life is the key."

Avendesora is currently in beta. As a password generator, the generated 
passwords are very sensitive to changes in the algorithms. As the algorithms are 
not set, you should not be using Avendesora to generate and hold your persistent 
passwords.  Instead, Advendesora should only be used to try out the user 
interface.

Please report all bugs and suggestions to avendesora@nurdletech.com

Introduction
------------

Avendesora is powerful command-line utility that can securely hold and 
conveniently provide access to a wide variety of information about your online 
accounts, including its secrets such as passwords. Account values can be 
displayed, copied to the clipboard, or automatically typed into running 
applications such as you web browser or terminal windows, automatically 
recognize which account to use based on the window title.  Avendesora can also 
open accounts in your web browser and warn you if you are not using encryption 
when you go to enter your password.

Account secrets can saved in encrypted form, as with password vaults, or 
generated from a root secret.  Generated secrets have two important benefits.  
First, they are produced from a random seed, and so are quite unpredictable.  
This is important, because the predictability of a passwords can be exploited 
when cracking passwords.  Second, if the root secret is shared with another 
trusted party, then you both can generate new shared secrets without passing any 
further secrets.

Avendesora replaces the Abraxas, which are both alternatives to the traditional 
password vault.  While Avendesora can securely store passwords like a password 
vault, the intent is to regenerate passwords or other secrets when needed rather 
than to store them.  Secrets are generated from a collection of seeds, one of 
which must be random with a very high degree of entropy. The random seed is 
referred to as the 'master password'.  It is extremely important that the master 
password remain completely secure.  Never disclose a master password to anyone 
except for a person you wish to collaborate with, and then only used the shared 
master password for shared secrets.  All of your private secrets should be 
generated from private master passwords. The seeds generally include the master 
password, the account name, the secret name, and perhaps a version name.  For 
example, imagine having a Gmail account, then the account name might simply be 
'gmail', and the secret name might be 'passcode'. In this case, your master 
password is combined with the words 'gmail' and 'passcode', the combination is 
hashed, and then password is generated with an appropriate recipe that you 
specify.  There are recipes for passwords, pass phrases, PINs, etc.  The 
password itself is not stored, rather it is the seeds that are stored and the 
password is regenerated when needed. Notice that all the seeds except the master 
password need not be kept secure. Thus, once you have shared a master password 
with a collaborator, all you need to do is share the remaining seeds and your 
collaborator can generate exactly the same password. Another important thing to 
notice is that the generated password is dependent on the account and secret 
names. Thus if you rename your account or your secret, the password will change.  
So you should be careful when you first create your account to name it 
appropriately so you don't feel the need to change it in the future. For 
example, 'gmail' might not be a good account name if you expect to have multiple 
Gmail accounts. In this case you might want to include your username in the 
account name.



Installation
------------

Install with::

    pip3 install --user avendesora

.. image:: https://travis-ci.org/KenKundert/avendesora.svg?branch=master
    :target: https://travis-ci.org/KenKundert/avendesora


Upgrading
---------

Avendesora is a password generator rather than a password vault. As a result, 
there is always a chance that something could change in the password generation 
algorithm that causes the generated passwords to change. Of course, the program 
is thoroughly tested to assure this does not happen, but there is still a small 
chance that something slips through.  To assure that you are not affected by 
this, you should archive your passwords before you upgrade with::

    avendesora archive

Then upgrade with::

    pip install -U --user avendesora

Finally, run::

    avendesora changed

to confirm that none of your generated passwords have changed.


Requirements
------------

To use Avendesora, you will need GPG and you will need a GPG ID that is 
associated with a private key. That GPG ID could be in the form of an email 
address or an ID string that can be found using 'gpg --list-keys'.


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

####
TODO
####

1. Must describe how to update gnupg.py to avoid the errors. Specifically add 
   "PROGRESS", ..., "WARNING", "KEY_CONSIDERED" to the list near line 250 that 
   contains ...

        elif key in ("RSA_OR_IDEA", "NODATA", "IMPORT_RES", "PLAINTEXT",
                     "PLAINTEXT_LENGTH", "POLICY_URL", "DECRYPTION_INFO",
                     "DECRYPTION_OKAY", "INV_SGNR", "FILE_START", "FILE_ERROR",
                     "FILE_DONE", "PKA_TRUST_GOOD", "PKA_TRUST_BAD", "BADMDC",
                     "GOODMDC", "NO_SGNR", "NOTATION_NAME", "NOTATION_DATA",
                     "IMPORT_OK", "PROGRESS", "PINENTRY_LAUNCHED", "NEWSIG",
                     "WARNING", "KEY_CONSIDERED"):
            pass

2. Must describe how to add GPG support to VIM.

    Download::

        http://www.vim.org/scripts/script.php?script_id=3645

    Copy into::

        cp gnupg.vim ~/.vim/plugin

3. Must install linux utilities::

        dnf install xdotool xsel

3. Must describe how to create a gpg key and how to configure gpg-agent


Configuration
-------------

The config file (~/.config/avendesora/config) allow you to personalize 
Avendesora to your needs. After initializing you account you should take the 
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
for that account. For example::

    class BigBank(Account):
        aliases = ['bb']
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

    > avendesora all bb
    NAMES: bigbank, bb
    ACCOUNTS:
        CHECKING: <reveal with 'avendesora show bigbank accounts.checking'>
        CREDITCARD: <reveal with 'avendesora show bigbank accounts.creditcard'>
        SAVINGS: <reveal with 'avendesora show bigbank accounts.savings'>
    CUSTOMER SERVICE: 1-866-229-6633
    EMAIL: gman33@pizza.com
    PASSCODE: <reveal with 'avendesora show bigbank passcode'>
    PIN: <reveal with 'avendesora show bigbank pin'>
    QUESTIONS:
        0: What city were you born in? <reveal with 'avendesora show bigbank questions.0'>
        1: What street did you grow up on? <reveal with 'avendesora show bigbank questions.1'>
        2: What was your childhood nickname? <reveal with 'avendesora show bigbank questions.2'>
    URL: https://bigbank.com/login
    USERNAME: gman33
    VERBAL: <reveal with 'avendesora show bigbank verbal'>

The attributes have various levels of confidentiality.  Simple strings are not 
considered sensitive. Those values provided by Python classes inherit the 
confidentiality of the class.  Hidden() provides simple concealment. GPG()
provides full encryption. And classes like Password(), Passphrase(), PIN() and 
Question generates secrets.  Attributes that are considered sensitive are not 
shown in the above summary, but can be requested individually::

    > avendesora show bb pin
    PIN: 7784

Attributes can be simple scalars, such as PIN. They can be array memberss, such 
as questions::

    > avendesora show bigbank questions.1
    QUESTIONS.1: contact insulator crumb

Or they can be dictionary members::

    > avendesora show bb accounts.checking
    ACCOUNTS.CHECKING (base64): 12345678

The passcode attribute is the default scalar attribute::

    > avendesora show bb
    PASSCODE: Nj3gpqHNfiie

The questions attribute is the default array attribute, which is used if the 
requested field is a number::

    > avendesora show bb 0
    QUESTIONS.0: muffin favorite boyfriend


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


    > avendesora find 4408
    4408:
        bankofamerica (boa)

