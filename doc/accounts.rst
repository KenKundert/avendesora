.. index::
    single: adding account file
    single: deleting account file
    single: adding account
    single: deleting account

.. _accounts:

Accounts
========

Account information is stored in account files. The list of account files is 
given in ~/.config/avendesora/accounts_files.  New account files are created 
using ``avendesora new``, but to delete an accounts file, you must manually 
remove it from accounts_files. Once an accounts file exists, you may add 
accounts to it using ``account add``. Use the -f option to specify which file is 
to contain the new account.  Modifying or deleting an account is done with 
``account edit <account_name>``.  To delete the account, simply remove all lines 
associated with the account.

An account is basically a collection of attributes organized as a subclass of 
the Python Account class. For example:

.. code-block:: python

    class NewYorkTimes(Account):
        aliases = 'nyt'
        username = 'derrickAsh'
        email = 'derrickAsh@gmail.com'
        passcode = PasswordRecipe('12 2u 2d 2s')
        discovery = RecognizeURL(
            'https://myaccount.nytimes.com',
            script='{email}{tab}{passcode}{return}'
        )

One creates an account using::

    > avendesora add <type>

where *<type>* is either *shell*, *website* or *bank*.  Choose the template that 
seems most appropriate (see :ref:`overview <overview>` and :ref:`add command 
<add command>` for more information) and edit it to your needs.

If after configuring your account you feel the need to change it, you can use 
the :ref:`edit command <edit command>` to do so::

    > avendesora edit nyt

Most of the field values can be retrieved simply by asking for them.  For 
example::

    > avendesora value newyorktimes username
    username: derrickAsh

In general, values can be strings, arrays, dictionaries, and special Advendesora 
classes. For example, you could have an array of security questions:

.. code-block:: python

    questions = [
        Question("What is your mother's maiden name?"),
        Question("What city were you born?"),
        Question("What is first pet's name?"),
    ]

Then you can request the answer to a particular question using its
index::

    > avendesora value newyorktimes questions.0
    questions.0 (What is your mother's maiden name?): portrayal tentacle fanlight

*questions* is the default array field, so you could have shortened your request 
by using '0' rather than 'questions.0'.  You might be thinking, hey, that is not 
my mother's maiden name. That is because *Question* is a 'generated secret'.  It 
produces a completely random answer that is impossible to predict. Thus, even 
family members cannot know the answers to your security questions.

A dictionary is often used to hold account numbers:

.. code-block:: python

    class MyBank(Account):
        accounts = {
            'checking': '1234-56-7890',
            'savings': '0123-45-6789',
        }

You then access its values using::

    > avendesora value mybank accounts.checking
    accounts.checking: 1234-56-7890

You might consider your account numbers as sensitive information. In this case 
you can hide them with:

.. code-block:: python

    class MyBank(Account):
        accounts = {
            'checking': Hide('1234-56-7890'),
            'savings': Hide('0123-45-6789'),
        }

Doing so means that *Avendesora* will try to protect them from accidental 
disclosure. For example, it will attempt to erase the screen after displaying 
them for a minute. You may also be concerned with someone looking over your 
shoulders when you are editing your accounts file and stealing your secrets. To 
reduce the chance, you can encode the secrets:

.. code-block:: python

    class MyBank(Account):
        accounts = {
            'checking': Hidden('MTIzNC01Ni03ODkw'),
            'savings': Hidden('MDEyMy00NS02Nzg5'),
        }

The values are now hidden, but not encrypted. They are simply encoded with 
base64. Any knowledgeable person with the encoded value can decode it back to 
its original value. Using Hidden makes it harder to recognize and remember the 
value given only a quick over-the-shoulder glance. It also marks the value as 
sensitive, so it will only be displayed for a minute. You generate the encoded 
value using the :ref:`conceal command <conceal command>`.

If this is not enough security, you can encrypt the values and access them using 
:class:`avendesora.GPG` or :class:`avendesora.Scrypt`.

You can find the specifics of how to specify or generate your secrets in 
:ref:`helpers`.

Any value that is an instance of the :class:`avendesora.GeneratedSecret` class 
(:class:`avendesora.Password`, :class:`avendesora.Passphrase`, ...) or the 
:class:`avendesora.ObscuredSecret` class (:class:`avendesora.Hidden`, 
:class:`avendesora.GPG`, ...) are considered sensitive.  They are given out only 
in a controlled manner. For example, running the :ref:`values command <values 
command>` displays all fields, but the values that are sensitive are replaced by 
instructions on how to view them. They can only be viewed individually::

    > avendesora values newyorktimes
    names: newyorktimes, nyt
    email: derrickAsh@gmail.com
    passcode: <reveal with 'avendesora value newyorktimes passcode'>
    username: derrickAsh

The *aliases* and *discovery* fields are not shown because they are considered 
tool fields. Other tool fields include *NAME*, *default*, *master*, *browser*, 
and *default_url*. See :ref:`discovery` for more information on discovery.  
*default* is the name of the default field, which is the field you get if you do 
not request a particular field. Its value defaults to *password*, *pasphrase*, 
or *passcode* (as set by *default_field* setting), but it can be set to any 
account attribute name or it can be a :ref:`script <scripts>`.  *browser* is the 
default browser to use when opening the account, run the :ref:`browse command 
<browse command>` to see a list of available browsers.

The value of *passcode* is considered sensitive because it is an instance of 
*PasswordRecipe*, which is a subclass of *GeneratedSecret*.  If you wish to see 
the *passcode*, use::

    > avendesora value nyt
    passcode: TZuk8:u7qY8%

This value will be displayed for a minute and then hidden. If you would like to 
hide it early, simply type Ctrl-C.

An attribute value can incorporate other attribute values through use of the 
:class:`avendesora.Script` class as described in :ref:`scripts`. For example, 
consider an account for your wireless router that contains the following:

.. code-block:: python

    class Router(Account):
        aliases = 'wifi'
        ssid = {
            'huron_guests': Passphrase(),
            'huron_drugs': Passphrase(),
        }
        guest = Script('SSID: huron_guests, password: {ssid.huron_guests}')
        privileged = Script('SSID: huron_drugs, password: {ssid.huron_drugs}')

The *ssid* field is a dictionary that contains the SSID and passphrases for each 
of the wireless networks provided by the router.  This is a natural an compact 
representation for this information, but accessing it as a user in this form 
would require two steps to access the information, one to get the SSID and 
another to get the passphrase. This issue is addressed by adding the guest and 
privileged attributes. The guest and privileged attributes are a script that 
gives the SSID and interpolate the passphrase. Now both can easily accessed at 
once with::

    > avendesora value wifi guest
    SSID: huron_guests, password: delimit ballcock fibber levitate

Use of *Avendesora* classes (:class:`avendesora.GeneratedSecret` or 
:class:`avendesora.ObscuredSecret`) is confined to the top two levels of account 
attributes, meaning that they can be the value of the top-level attributes, or 
the top-level attributes may be arrays or dictionaries that contain objects of 
these classes, but it can go no further.

It is important to remember that any generated secrets use the account name and 
the field name when generating their value, so if you change the account name or 
field name you will change the value of the secret.  For this reason is it 
important to choose a good account and field names up front and not change them.  
It should be very specific to avoid conflicts with similar accounts created 
later.  For example, rather than choosing Gmail as your account name, you might 
want to include your username, ex.  GmailPaulBunyan.  This would allow you to 
create additional gmail accounts later without ambiguity.  Then just add *gmail* 
as an alias to the account you use most often.

Account and field names are case insensitive. So you can use Gmail or gmail.  
Also, if the account or field names contains an underscore, you can substitute 
a dash. So if the account name is Gmail_Paul_Bunyon, you can use 
gmail-paul-bunyon instead.
