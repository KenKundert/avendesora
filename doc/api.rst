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

This section documents the programming interface for *Avendesora*.  You can view 
the *Avendesora* source code, particularly :mod:`avendesora.command`, for 
further examples on how to use this interface.

PasswordGenerator Class
"""""""""""""""""""""""

This is the entry class to *Avendesora*. It is the only class you need 
instantiate directly. By instantiating it you cause *Avendesora* to read the 
user's account files.

.. autoclass:: avendesora.PasswordGenerator
    :members:


Account Class
"""""""""""""

.. autoclass:: avendesora.Account
    :members:
        get_name, get_value, get_username, get_passcode, get_fields, get_values, 
        get_scalar, get_composite


AccountValue Class
""""""""""""""""""

.. autoclass:: avendesora.AccountValue
    :members:


PasswordError Exception
"""""""""""""""""""""""

.. autoexception:: avendesora.PasswordError
    :members: get_message, get_culprit, report, terminate
    :inherited-members:

    This exception subclasses `inform.Error <https://github.com/KenKundert/inform#exception>`_.



Example: Displaying Account Values
----------------------------------

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
