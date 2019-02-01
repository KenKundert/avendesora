.. _api:

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
        curl = Run(
            f'curl -K - {url!s}',
            stdin = f'user="{username!s}:{passcode!s}"',
            modes='sOEW0'
        )
        Path(f'{name!s}.ofx').write_text(curl.stdout)
    except OSError as e:
        fatal(os_error(e))

Basically, the approach is to open the password generator, open an account, and 
then access values of that account. The various components of the Avendesora 
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

    from avendesora import PasswordGenerator, PasswordError
    from inform import display, indent

    accounts = ['bank', 'credit-union', 'brokerage']

    try:
        pw = PasswordGenerator()

        for account_name in accounts:
            account = pw.get_account(account_name)
            description = account.get_scalar('desc', None, account_name)
            display(description, len(description)*'=', sep='\n')

            for name, keys in account.get_fields():
                if keys == [None]:
                    value = account.get_value(name)
                    display(value.render('{n}: {v}'))
                else:
                    display(name + ':')
                    for key, value in account.get_values(name):
                        display(indent(
                            value.render(('{k}) {d}: {v}', '{k}: {v}'))
                        ))
            display()
    except PasswordError as e:
        e.terminate()


.. index::
    single: ssh key example

.. _ssh:

Example: Add SSH Keys
---------------------

This example adds SSH keys to your SSH agent. It uses *pexpect* to manage the 
interaction between this script and *ssh-add*.

The updated source code for `addsshkeys
<https://github.com/KenKundert/avendesora/tree/master/samples/api/addsshkeys>`_
can be found on Github.

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

    A description of how to configure and use this program can be found at 
    `<https://avendesora.readthedocs.io/en/latest/api.html#example-add-ssh-keys>_.
    """
    # Assumes that the Avendesora account that contains the ssh key's passphrase 
    # has a name or alias of the form <name>-ssh-key. It also assumes that the 
    # account contains a field named 'keyfile' or 'keyfiles' that contains an 
    # absolute path or paths to the ssh key files in a string.

    from avendesora import PasswordGenerator, PasswordError
    from inform import Inform, codicil, error, narrate
    from docopt import docopt
    from pathlib import Path
    import pexpect

    SSHkeys = 'primary github backups'.split()
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
            passphrase = str(account.get_passcode().value)
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
                error('failed.', culprit=key)
                codicil('response:', sshadd.before.decode('utf8'), culprit=SSHadd)
                codicil('exit status:', sshadd.exitstatus , culprit=SSHadd)
        except PasswordError as e:
            e.report(culprit=key)


.. index::
    single: bitwarden export

.. _bitwarden:

Example: Export to BitWarden
----------------------------

This program exports selected accounts from *Avendesora* to *BitWarden*.  
*BitWarden* is a multi-platform open-source password manager.  Using *BitWarden* 
you can extend the reach of *Avendesora* to your phone or other non-Unix 
platform.

To use *bw-export* you would add a special field named *bitwarden* to those 
accounts that you wish to export. It must contain a dictionary that gives the 
values of each of the fields exported for each account. For example:

.. code-block:: python

    bitwarden = dict(
        type='login',
        name='Andor Airlines',
        login_uri='{urls}',
        login_username='{email}',
        login_password='{passcode}',
        fields='account: {account}\ncustomer service: {customer_service}',
    )

The exported fields are described on the `BitWarden website 
<https://help.bitwarden.com/article/import-data>`_.  The values for the fields 
are either simple strings, as in *type* and *name*, or *Avendesora* scripts, as 
in *login_username* and *fields*.  Scripts allow you to interpolate 
*Advendesora* account field value into *BitWarden* fields.  Any field that is 
supported but not given will be blank.

This script produces a file named *bw.csv* that contains the exported accounts, 
It can be imported into *BitWarden* from their website. You should delete any 
previously imported accounts before importing this file to avoid duplicates.
You should all take care to delete this file after you have completed the import 
as it contains the passcodes in plain text.

The updated source code for `bw-export
<https://github.com/KenKundert/avendesora/tree/master/samples/api/bw-export>`_
can be found on Github.

.. code-block:: python

    #!/usr/bin/env python3
    # Description
    """Export Accounts to BitWarden

    Generates a CSV file (bw.csv) suitable for uploading to BitWarden.

    Usage:
        bw-export

    Only those accounts with 'bitwarden' field are exported. The "bitwarden' field 
    is expected to be a dictionary that may contain the following fields: folder, 
    favorite, type, name, notes, fields, login_uri, login_username, login_password, 
    login_totp. If not given, they are left blank. Each value may be a simple string 
    or it may be a script.

    Once created, it can be imported from the BitWarden website 
    (vault.bitwarden.com).  You should delete existing accounts before re-importing 
    to avoid duplicate accounts. When importing, use 'Bitwarden (csv)' as the file 
    format.
    """

    # Imports
    from avendesora import PasswordGenerator, PasswordError, Script
    from inform import conjoin, os_error, terminate
    from docopt import docopt
    import csv

    # Globals
    fieldnames='''
        folder
        favorite
        type
        name
        notes
        fields
        login_uri
        login_username
        login_password
        login_totp
    '''.split()

    # Program
    try:
        # Read command line and process options
        cmdline = docopt(__doc__)

        # Scan accounts and gather accounts to export
        pw = PasswordGenerator()
        accounts = {}
        with open('bw.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # visit each account
            for account in pw.all_accounts():
                account_name = account.get_name()
                class_name = account.__name__
                description = account.get_scalar('desc', None, None)

                # process bitwarden field if it exists
                fields = account.get_composite('bitwarden')
                if fields:
                    # expand fields
                    for k, v in fields.items():
                        value = Script(v)
                        value.initialize(account)
                        fields[k] = str(value)
                    writer.writerow(fields)

    # Process exceptions
    except KeyboardInterrupt:
        terminate('Killed by user.')
    except PasswordError as e:
        e.terminate()
    except OSError as e:
        terminate(os_error(e))


.. index::
    single: postmortem summary example

.. _postmortem api example:

Example: Postmortem Summaries
-----------------------------

This is a program that generates a summary of selected accounts for a person's 
children and partners.  It is assumed that these messages would be placed into 
a safe place to be found and read upon the person's death.

It examines all accounts looking for a special field, *postmortem_recipients*.  
If the field exists, then that account is included in the file of accounts sent 
to that recipient.  The script also looks for another special field, 
*estimated_value*. It includes this value in the message and prints the values 
to the standard output when generating the messages. This gives you a chance to 
review the values and update them if they are stale. The generated files are 
encrypted so that only the intended recipients can read them.

Here is an example of the fields you would add to an account to support 
*postmortem*:

.. code-block:: python

    postmortem_recipients = 'kids'
    estimated_value = dict(
        updated = 'January 2019',
        equities = '$23k',
        cash = '$1.7k',
        retirement = '$41,326'
    )

The *estimated_value* field should be a dictionary where one item is 'updated',
which contains the date of when the values were last updated, and the remaining 
items should give an investment class and value.  The values may be specified as 
strings (commas, units and SI scale factors allowed) or as a real number or 
expression.

You configure *postmortem* by creating ~/.config/postmortem/config. This file 
contains Python code that specifies the various settings. At a minimum it should 
include the GPG IDs for yourself and your recipients. For example:

.. code-block:: python

    my_gpg_ids = 'morgase@andor.gov'
    recipients = dict(
        kids='galad@trakand.name gawyn@trakand.name elayne@trakand.name',
        partners='taringail.damodred@andor.gov',
    )

The updated source code for `postmortem
<https://github.com/KenKundert/avendesora/tree/master/samples/api/postmortem>`_
can be found on Github. A more advanced version can be found `here 
<https://github.com/KenKundert/postmortem>`_.

.. code-block:: python

    #!/usr/bin/env python3

    # Description
    """Postmortem

    Generate an account summary that includes complete account information, 
    including secrets, for selected accounts. This summary should allow the 
    recipients to access your accounts. The summaries are intended to be given to 
    the recipients after you die.

    Usage:
        postmortem [options] [<recipients>...]

    Choose from: {available}.  If no recipients are specified, then summaries will 
    be generated for all recipients.

    A description of how to configure and use this program can be found at 
    `<https://avendesora.readthedocs.io/en/latest/api.html#example-postmortem-summaries>_.
    """

    # Imports
    from avendesora import PasswordGenerator, PasswordError
    from avendesora.gpg import PythonFile
    from inform import (
        Error, conjoin, cull, display, indent, os_error, terminate, warn
    )
    from docopt import docopt
    from appdirs import user_config_dir
    from pathlib import Path
    import gnupg

    # Settings
    prog_name = 'postmortem'
    config_filename = 'config'

    # these can be overridden in the settings file: ~/.config/postmortem
    my_gpg_ids = ''
    recipients = dict()
    avendesora_value_fieldname = 'estimated_value'
    avendesora_recipients_fieldname = 'postmortem_recipients'

    try:
        # Read settings
        config_filepath = Path(user_config_dir(prog_name), config_filename)
        if config_filepath.exists():
            settings = PythonFile(config_filepath)
            settings.initialize()
            locals().update(settings.run())
        else:
            warn('no configuration file found.')

        # Read command line and process options
        cmdline = docopt(__doc__.format(available=conjoin(recipients)))
        who = cmdline['<recipients>']
        if not who:
            who = recipients

        # Scan accounts and gather information for recipients
        pw = PasswordGenerator()
        accounts = {}
        for account in pw.all_accounts():
            account_name = account.get_name()
            class_name = account.__name__
            description = account.get_scalar('desc', None, None)

            # summarize account values
            data = account.get_composite(avendesora_value_fieldname)
            postmortem_recipients = account.get_scalar(avendesora_recipients_fieldname, default=None)
            if data and not postmortem_recipients:
                warn('no recipients.', culprit= account.get_name())
                continue
            if not postmortem_recipients:
                continue
            postmortem_recipients = postmortem_recipients.split()

            # gather information for recipients
            for recipient in recipients:
                if recipient in postmortem_recipients:
                    # output title
                    title = ' - '.join(cull([class_name, description]))
                    lines = [title, len(title)*'=']

                    # output avendesora names
                    aliases = account.get_composite('aliases')
                    names = [account_name] + (aliases if aliases else [])
                    lines.append('avendesora names: ' + ', '.join(names))

                    # output user fields
                    for name, keys in account.get_fields():
                        if name in [avendesora_recipients_fieldname, 'desc', 'NAME']:
                            continue
                        if keys == [None]:
                            value = account.get_value(name)
                            lines += value.render('{n}: {v}').split('\n')
                        else:
                            lines.append(name + ':')
                            for key, value in account.get_values(name):
                                lines += indent(
                                    value.render(('{k}) {d}: {v}', '{k}: {v}'))
                                ).split('\n')
                    if recipient not in accounts:
                        accounts[recipient] = []
                    accounts[recipient].append('\n'.join(lines))


        # generate encrypted files than contain about accounts for each recipient
        gpg = gnupg.GPG(gpgbinary='gpg2')
        for recipient, idents in recipients.items():
            if recipient in accounts:
                content = accounts[recipient]
                num_accounts = len(content)
                encrypted = gpg.encrypt(
                    '\n\n\n'.join(content),
                    idents.split() + my_gpg_ids.split()
                )
                if not encrypted.ok:
                    raise Error(
                        'unable to encrypt:', encrypted.stderr, culprit=recipient
                    )
                try:
                    filename = recipient + '.gpg'
                    with open(filename, 'w') as file:
                        file.write(str(encrypted))
                    display(f'contains {num_accounts} accounts.', culprit=filename)
                except OSError as e:
                    raise Error(os_error(e))
            else:
                warn('no accounts found.', culprit=recipient)

    # process exceptions
    except KeyboardInterrupt:
        terminate('Killed by user.')
    except (PasswordError, Error) as e:
        e.terminate()


.. index::
    single: networth example

.. _networth api example:

Example: Net Worth
------------------

If you have added *estimated_value* to all of your accounts that hold 
significant value as proposed in the previous example, then *networth* 
summarizes the values and estimates your net worth.

You configure *networth* by creating ~/.config/networth/config. This file 
contains Python code that specifies the various settings. You do not need this 
file, but there is a few things you might wish to configure with this file.  
First, you can arrange to report the networth of multiple people.  Generally you 
would be interested in your own networth, but you might also be interested in 
the networth of someone such as a child or a parent if you are their financial 
custodian. Second, you can rename accounts if you have obscure or excessively 
long account names. Finally, you can add a list of cryptocurrencies, in which 
case *networth* will download the latest prices to give you an up-to-date view 
of your networth.

Here is an example of what your configuration file might look like.

.. code-block:: python

    default_who='me'

    avendesora_fieldnames = dict(
        me='estimated_value',
        parents='parents_estimated_value',
    )

    aliases = dict(
        me = {
            'princeton-capital': 'home mortgage',
        },
        parents = {
            'parents-bankamerica': 'bank america',
            'parents-schwab': 'schwab',
            'premierlending': 'home mortgage',
        }
    )

    coins = 'BTC ETH'.split()

    # bar settings
    screen_width = 110

The updated source code for `networth
<https://github.com/KenKundert/avendesora/tree/master/samples/api/networth>`_ 
can be found on Github. A more advanced version can be found `here 
<https://github.com/KenKundert/networth>`_.

.. code-block:: python

    #!/usr/bin/env python3
    # Description
    """Networth

    Show a summary of the networth of the specified person.

    Usage:
        networth [options] [<profile>]

    Options:
        -u, --updated           show the account update date rather than breakdown

    {available_profiles}
    Settings can be found in: {settings_dir}.
    Typically there is one file for generic settings named 'config' and then one 
    file for each profile whose name is the same as the profile name with a '.prof' 
    suffix.  Each of the files may contain any setting, but those values in 'config' 
    override those built in to the program, and those in the individual profiles 
    override those in 'config'. The following settings are understood. The values 
    are those before an individual profile is applied.

    Profile values:
        default_profile = {default_profile}

    Account values:
        avendesora_fieldname = {avendesora_fieldname}
        value_updated_subfieldname = {value_updated_subfieldname}
        date_formats = {date_formats}
        max_account_value_age = {max_account_value_age}  (in days)
        aliases = {aliases}
            (aliases is used to fix account names to make them more readable)

    Cryptocurrency values:
        coins = {coins}
        prices_filename = {prices_filename}
        max_coin_price_age = {max_coin_price_age}  (in seconds)

    Bar graph values:
        screen_width = {screen_width}
        asset_color = {asset_color}
        debt_color = {debt_color}

    The prices and log files can be found in {cache_dir}.

    A description of how to configure and use this program can be found at 
    `<https://avendesora.readthedocs.io/en/latest/api.html#example-net-worth>`_.
    """

    # Imports
    from avendesora import PasswordGenerator, PasswordError
    from avendesora.gpg import PythonFile
    from inform import (
        conjoin, display, done, error, fatal, is_str, join, narrate, os_error, 
        render_bar, terminate, warn, Color, Error, Inform,
    )
    from quantiphy import Quantity
    from docopt import docopt
    from appdirs import user_config_dir, user_cache_dir
    from pathlib import Path
    import arrow

    # Settings
    # These can be overridden in ~/.config/networth/config
    prog_name = 'networth'
    config_filename = 'config'

    # Avendesora settings
    default_profile = 'me'
    avendesora_fieldname = 'estimated_value'
    value_updated_subfieldname = 'updated'
    aliases = {}

    # cryptocurrency settings (empty coins to disable cryptocurrency support)
    proxy = None
    prices_filename = 'prices'
    coins = None
    max_coin_price_age = 86400  # refresh cache if older than this (seconds)

    # bar settings
    screen_width = 79
    asset_color = 'green'
    debt_color = 'red'
        # currently we only colorize the bar because ...
        # - it is the only way of telling whether value is positive or negative
        # - trying to colorize the value really messes with the column widths and is 
        #     not attractive

    # date settings
    date_formats = [
        'MMMM YYYY',
        'YYMMDD',
    ]
    max_account_value_age = 120  # days

    # Utility functions
    # get the age of an account value
    def get_age(date, profile):
        if date:
            for fmt in date_formats:
                try:
                    then = arrow.get(date, fmt)
                    age = arrow.now() - then
                    return age.days
                except:
                    pass
        warn(
            'could not compute age of account value',
            '(updated missing or misformatted).',
            culprit=profile
        )

    # colorize text
    def colorize(value, text = None):
        if text is None:
            text = str(value)
        return debt_color(text) if value < 0 else asset_color(text)


    try:
        # Initialization
        settings_dir = Path(user_config_dir(prog_name))
        cache_dir = user_cache_dir(prog_name)
        Quantity.set_prefs(prec=2)
        Inform(logfile=Path(cache_dir, 'log'))
        display.log = False   # do not log normal output

        # Read generic settings
        config_filepath = Path(settings_dir, config_filename)
        if config_filepath.exists():
            narrate('reading:', config_filepath)
            settings = PythonFile(config_filepath)
            settings.initialize()
            locals().update(settings.run())
        else:
            narrate('not found:', config_filepath)

        # Read command line and process options
        available=set(p.stem for p in settings_dir.glob('*.prof'))
        available.add(default_profile)
        if len(available) > 1:
            choose_from = f'Choose <profile> from {conjoin(sorted(available))}.'
            default = f'The default is {default_profile}.'
            available_profiles = f'{choose_from} {default}\n'
        else:
            available_profiles = ''

        cmdline = docopt(__doc__.format(
            **locals()
        ))
        show_updated = cmdline['--updated']
        profile = cmdline['<profile>'] if cmdline['<profile>'] else default_profile
        if profile not in available:
            fatal(
                'unknown profile.', choose_from, template=('{} {}', '{}'), 
                culprit=profile
            )

        # Read profile settings
        config_filepath = Path(user_config_dir(prog_name), profile + '.prof')
        if config_filepath.exists():
            narrate('reading:', config_filepath)
            settings = PythonFile(config_filepath)
            settings.initialize()
            locals().update(settings.run())
        else:
            narrate('not found:', config_filepath)

        # Process the settings
        if is_str(date_formats):
            date_formats = [date_formats]
        asset_color = Color(asset_color)
        debt_color = Color(debt_color)

        # Get cryptocurrency prices
        if coins:
            import requests

            cache_valid = False
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            prices_cache = Path(cache_dir, prices_filename)
            if prices_cache and prices_cache.exists():
                now = arrow.now()
                age = now.timestamp - prices_cache.stat().st_mtime
                cache_valid = age < max_coin_price_age
            if cache_valid:
                contents = prices_cache.read_text()
                prices = Quantity.extract(contents)
                narrate('coin prices are current:', prices_cache)
            else:
                narrate('updating coin prices')
                # download latest asset prices from cryptocompare.com
                currencies = dict(
                    fsyms=','.join(coins),     # from symbols
                    tsyms='USD',               # to symbols
                )
                url_args = '&'.join(f'{k}={v}' for k, v in currencies.items())
                base_url = f'https://min-api.cryptocompare.com/data/pricemulti'
                url = '?'.join([base_url, url_args])
                try:
                    r = requests.get(url, proxies=proxy)
                except KeyboardInterrupt:
                    done()
                except Exception as e:
                    # must catch all exceptions as requests.get() can generate 
                    # a variety based on how it fails, and if the exception is not 
                    # caught the thread dies.
                    raise Error('cannot access cryptocurrency prices:', codicil=str(e))

                try:
                    data = r.json()
                except:
                    raise Error('cryptocurrency price download was garbled.')
                prices = {k: Quantity(v['USD'], '$') for k, v in data.items()}

                if prices_cache:
                    contents = '\n'.join('{} = {}'.format(k,v) for k,v in 
                    prices.items())
                    prices_cache.write_text(contents)
                    narrate('updating coin prices:', prices_cache)
            prices['USD'] = Quantity(1, '$')
        else:
            prices = {}

        # Build account summaries
        narrate('running avendesora')
        pw = PasswordGenerator()
        totals = {}
        accounts = {}
        total_assets = Quantity(0, '$')
        total_debt = Quantity(0, '$')
        grand_total = Quantity(0, '$')
        width = 0
        for account in pw.all_accounts():

            # get data
            data = account.get_composite(avendesora_fieldname)
            if not data:
                continue
            if type(data) != dict:
                error(
                    'expected a dictionary.',
                    culprit=(account_name, avendesora_fieldname)
                )
                continue

            # get account name
            account_name = account.get_name()
            account_name = aliases.get(account_name, account_name)
            account_name = account_name.replace('_', ' ')
            width = max(width, len(account_name))

            # sum the data
            updated = None
            contents = {}
            total = Quantity(0, '$')
            odd_units = False
            for k, v in data.items():
                if k == value_updated_subfieldname:
                    updated = v
                    continue
                if k in prices:
                    value = Quantity(v*prices[k], prices[k])
                    k = 'cryptocurrency'
                else:
                    value = Quantity(v, '$')
                if value.units == '$':
                    total = total.add(value)
                else:
                    odd_units = True
                contents[k] = value.add(contents.get(k, 0))
                width = max(width, len(k))
            for k, v in contents.items():
                totals[k] = v.add(totals.get(k, 0))

            # generate the account summary
            age = get_age(data.get(value_updated_subfieldname), account_name)
            if show_updated:
                desc = updated
            else:
                desc = ', '.join('{}={}'.format(k, v) for k, v in contents.items() if v)
                if len(contents) == 1 and not odd_units:
                    desc = k
                if age and age > max_account_value_age:
                    desc += f' ({age//30} months old)'
            accounts[account_name] = join(
                total, desc.replace('_', ' '),
                template=('{:7q} {}', '{:7q}'), remove=(None,'')
            )

            # sum assets and debts
            if total > 0:
                total_assets = total_assets.add(total)
            else:
                total_debt = total_debt.add(-total)
            grand_total = grand_total.add(total)

        # Summarize by account
        display('By Account:')
        for name in sorted(accounts):
            summary = accounts[name]
            display(f'{name:>{width+2}s}: {summary}')

        # Summarize by investment type
        display('\nBy Type:')
        largest_share = max(v for v in totals.values() if v.units == '$')
        barwidth = screen_width - width - 18
        for asset_type in sorted(totals, key=lambda k: totals[k], reverse=True):
            value = totals[asset_type]
            if value.units != '$':
                continue
            share = value/grand_total
            bar = colorize(value, render_bar(value/largest_share, barwidth))
            asset_type = asset_type.replace('_', ' ')
            display(f'{asset_type:>{width+2}s}: {value:>7s} ({share:>5.1%}) {bar}')
        display(
            f'\n{"TOTAL":>{width+2}s}:',
            f'{grand_total:>7s} (assets = {total_assets}, debt = {total_debt})'
        )

    # Handle exceptions
    except OSError as e:
        error(os_error(e))
    except KeyboardInterrupt:
        terminate('Killed by user.')
    except (PasswordError, Error) as e:
        e.terminate()
    done()

Here is a typical output of this script::

    By Account:
            betterment:    $22k equities=$9k, cash=$3k, retirement=$9k
                 chase:     $7k cash
             southwest:      $0 miles=78kmiles
              coindesk:  $15.3k cryptocurrency

    By Type:
        cryptocurrency:  $15.3k (35.3%) ██████████████████████████████████████████
                  cash:    $10k (23.1%) ███████████████████████████████
              equities:     $9k (20.8%) ███████████████████████████
            retirement:     $9k (20.8%) ███████████████████████████

                TOTAL:  $43.3k (assets = $43.3k, debt = $0)
