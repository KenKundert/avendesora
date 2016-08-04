Avendesora Collaborative Password Utility
=========================================

Introduction
------------
Avendesora is currently in alpha. Please report all bugs and suggestions to 
avendesora@nurdletech.com


Installation
------------

Install with::

    pip install --user avendesora

.. image:: https://travis-ci.org/KenKundert/avendesora.svg?branch=master
    :target: https://travis-ci.org/KenKundert/avendesora


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
a particular account is 





