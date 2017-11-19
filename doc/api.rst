Python API
==========

A Simple Example
----------------

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
        name = account.get_value('name')
        username = account.get_username()
        passcode = account.get_passcode()
        url = account.get_value('ofxurl')
    except PasswordError as e:
        e.terminate()

    try:
        curl = Run(f'curl --user {username!s}:{passcode!s} {url!s}', 'sOEW0')
        Path(f'{name!s}.ofx').write_text(curl.stdout)
    except OSError as e:
        fatal(os_error(e))

Bascially, the approach is to open the password generator, open an account, and 
then accessing values of that account. The various components of the Avendesora 
programming interface are described next.


Components
----------

PasswordGenerator():

    Initializes the password generator. You should pass no arguments.
    Calling this class causes Avendesora to open all the various account files 
    and returns an object that allows you access to the accounts. Specifically 
    you can use the *get_account()* or *all_accounts()* methods to access an 
    account or all the accounts.

PasswordError():

    *Avendesora* uses `Inform <http://nurdletech.com/linux-utilities/inform>`_ 
    for messaging, and Avendesora's *PasswordError* is actually Inform's *Error* 
    class. So *PasswordError* provides all of the features that Inform's *Error* 
    class does. Specifically it provides the *report* and *terminate* methods 
    that prints the message or prints a message and terminates.
    *PasswordError* also provides get_message() and get_culprit() methods, which 
    return the message and the culprit. You can also cast the exception to 
    a string to get a string that contains both the message and the culprit 
    formatted so that it can be shown to the user.

PasswordGenerator.all_accounts():

    Iterates through all normal accounts (no stealth accounts are returned.

PasswordGenerator.get_account(name, request_seed=False, stealth_name=None):

    Accesses a particular account. Takes a string for the account name or alias.  
    Optionally takes a second string that is used as an additional seed (see: 
    :ref:`misdirection`).

    The stealth name is used as account name if the account is a stealth 
    account.

Account.get_name():

    Returns the primary account name. This is generally the class name converted 
    to lower case unless it was overridden with the NAME attribute.

Account.get_value(field):

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
        answer1 = account.get_value('questions.1')
        answer2 = account.get_value('questions[2]')

    The value is returned as an object that contains six attributes, *value* 
    (the actual value), *is_secret* (whether the value is secret or contains 
    a secret), *name* (the name of the value), *desc* (the description, contains 
    the actual question of the answer to a question is requested), *field* (the 
    field name) and *key* (the key name, if any).  Converting the object to 
    a string returns the value rendered as a string.  There is also the render() 
    method that returns a string that combines the name and the description with 
    the value. You can pass in a collection of format strings into render() 
    where the following attributes are replaced by the corresponding values:

      | n -- name (identifier for the first level of a field)
      | k -- key (identifier for the second level of a field)
      | f -- field (name.key)
      | d -- description
      | v -- value

    If a format string references an attribute that is not set, it is skipped.  
    The first format string that has all of the interpolated values is used.

Account.get_scalar(name, key=None, default=False):

    A lower level interface than *get_value()* that given a name and perhaps 
    a key returns a scalar value.  Also takes an optional default value that is 
    returned if the value is not found. Unlike *get_value()*, the actual value 
    is returned, not a object that contains multiple facets of the value.

    The *name* is the field name, and the *key* would identity which value is 
    desired if the field is a composite. If default is False, an error is raised 
    if the value is not present, otherwise the default value itself is returned.

Account.get_composite(name):

    A lower level interface than *get_value()* that given a name returns the 
    value of the associated field, which may be a scalar (string or integer) or 
    a composite (array of dictionary).  Unlike *get_value()*, the actual value 
    is returned, not a object that contains multiple facets of the value.

Account.get_username():

    Like *get_value()*, but tries the *credential_ids* in order and returns the 
    first found. *credential_ids* is an Avendesora configuration setting that by 
    default is *username* and *email*.

Account.get_passcode():

    Like *get_value()*, but tries the *credential_secrets* in order and returns 
    the first found. *credential_secrets* is an Avendesora configuration setting 
    that by default is *password*, *passphrase* and *passcode*.

Account.get_fields():

    Iterates through the field returning 2-tuple that contains both field name 
    and the key names.  None is returned for the key names if the field holds 
    a scalar value.

Account.get_values(name):
    Iterates through each value of a particular field, returning the key and the 
    value. The value is an AccountValue. If field is a scalar, the key is None.


The following example prints out all account values for account whose name are 
found in a list.

.. code-block:: python

    from avendesora import PasswordGenerator
    from inform import display, indent, Error

    accounts = ['bank', 'credit-union', 'brokerage']

    try:
        pw = PasswordGenerator()

        for account_name in accounts:
            account = pw.get_account(account_name)
            description = account.get_scalar('desc', None, account_name)
            display(description, len(description)*'=', sep='\n')

            for name, keys in account.get_fields():
                if keys:
                    display(name + ':')
                    for key, value in account.get_values(name):
                        display(indent(
                            value.render(('{k}) {d}: {v}', '{k}: {v}'))
                        ))
                else:
                    value = account.get_value(name)
                    display(value.render('{n}: {v}'))
            display()
    except Error as e:
        e.terminate()


.. index::
    single: ssh key example

.. _ssh:

Example: Add SSH Keys
---------------------

.. code-block:: python

    #!/usr/bin/env python3
    """
    Add SSH keys

    Add SSH keys to SSH agent.
    The following keys are added: {keys}.

    Usage:
        addsshkeys [options]

    Options:
        -v, --verbose    list the keys as they are being added
    """
    # This assumes that the Avendesora account that contains the ssh key's 
    # passphrase has a name or alias of the form <name>-ssh-key. It also assumes 
    # that the account contains a field named 'keyfile' or 'keyfiles' that contains 
    # an absolute path or paths to the ssh key files in a string.

    from avendesora import PasswordGenerator, PasswordError
    from inform import Inform, codicil, error, fatal, narrate
    from docopt import docopt
    from pathlib import Path
    import pexpect

    SSHkeys = ['primary', 'github', 'backups']
    SSHadd = 'ssh-add'

    cmdline = docopt(__doc__.format(keys = ', '.join(SSHkeys)))
    Inform(narrate=cmdline['--verbose'])

    try:
        pw = PasswordGenerator()
    except PasswordError as e:
        e.terminate()

    for key in SSHkeys:
        name = key + '-ssh-key'
        try:
            account = pw.get_account(name)
            passphrase = account.get_passcode().value
            if account.has_field('keyfiles'):
                keyfiles = account.get_value('keyfiles').value
            else:
                keyfiles = account.get_value('keyfile').value
            for keyfile in keyfiles.split():
                path = Path(keyfile).expanduser()
                narrate('adding.', culprit=keyfile)
                try:
                    sshadd = pexpect.spawn(SSHadd, [str(path)])
                    sshadd.expect('Enter passphrase for %s: ' % (path), timeout=4)
                    sshadd.sendline(passphrase)
                    sshadd.expect(pexpect.EOF)
                    sshadd.close()
                    response = sshadd.before.decode('utf-8')
                    if 'identity added' in response.lower():
                        continue
                except (pexpect.EOF, pexpect.TIMEOUT):
                    pass
                error('failed.', culprit=path)
                codicil('response:', sshadd.before.decode('utf8'), culprit=SSHadd)
                codicil('exit status:', sshadd.exitstatus , culprit=SSHadd)
        except PasswordError as e:
            fatal(e, culprit=path)


.. index::
    single: postmortem letter example

.. _postmortem letter:

Example: Postmortem Letter
---------------------------

This is a program that generates messages for a person's children and business 
partners. It is assumed that these messages would be placed into a safe place to 
be found and read upon the person's death.

Modify the program so that it goes through all accounts and look for 
a particular fields, such as target and value. The target would be a string that 
contains the name of the person for which it is a message, and value would 
contain an estimate of the total account value.

It generates an encrypted file for each of the recipients that contains accounts 
that contain an *postmortem_recipient* whose value matches the recipient.

.. code-block:: python

    #!/bin/env python3

    from avendesora import PasswordGenerator
    from inform import done, Error, indent, os_error, terminate
    import gnupg

    recipients = dict(
        kids='dominique@chappell.name lonny@chappell.name tabatha@chappell.name',
        henry='dominique@chappell.name  lynna.titus625@gmail.com',
    )

    try:
        pw = PasswordGenerator()

        for recipient, idents in recipients.items():
            # extract account information
            accounts = []
            for account in pw.all_accounts():
                if recipient == account.get_scalar('postmortem_recipient', default=None):
                    account_name = account.get_name()
                    description = account.get_scalar('desc', None, account_name)
                    lines = [description, len(description)*'=']

                    for name, keys in account.get_fields():
                        if name == 'postmortem_recipient':
                            continue
                        if keys:
                            lines.append(name + ':')
                            for key, value in account.get_values(name):
                                lines += indent(
                                    value.render(('{k}) {d}: {v}', '{k}: {v}'))
                                ).split('\n')
                        else:
                            value = account.get_value(name)
                            lines += value.render('{n}: {v}').split('\n')
                    accounts.append('\n'.join(lines))

            # write GPG file containing accounts
            gpg = gnupg.GPG(gpgbinary='gpg2')
            encrypted = gpg.encrypt('\n\n\n'.join(accounts), idents.split())
            if not encrypted.ok:
                raise Error(
                    'unable to encrypt:', encrypted.stderr, culprit=recipient
                )
            try:
                filename = recipient + '.gpg'
                with open(filename, 'w') as file:
                    file.write(str(encrypted))
                narrate("created.", culprit=filename)
            except OSError as e:
                raise Error(os_error(e))

    except KeyboardInterrupt:
        terminate('Killed by user')
    except Error as e:
        e.terminate()
