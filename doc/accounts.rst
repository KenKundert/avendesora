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
using ':ref:`avendesora new <new command>`', but to delete an accounts file, you 
must manually remove it from accounts_files. Once an accounts file exists, you 
may add accounts to it using ':ref:`avendesora add <add command>`'. Use the 
``-f`` option to specify which file is to contain the new account.  Modifying or 
deleting an account is done with ':ref:`avendesora edit account_name <edit 
command>`'.  To delete the account, simply remove all lines associated with the 
account.

An account is basically a collection of attributes organized as a subclass of 
the Python :class:`avendesora.Account` class. For example:

.. code-block:: python

    class ManetherenTimes(Account):
        aliases = 'times mt'
        username = 'nynaeve'
        email = 'nynaeve@gmail.com'
        passcode = PasswordRecipe('12 2u 2d 2s')
        discovery = RecognizeURL(
            'https://myaccount.manetherentimes.com',
            script='{email}{tab}{passcode}{return}'
        )

One creates an account using::

    > avendesora add <type>

where *<type>* is either *shell*, *website* or *bank*.  Choose the template that 
seems most appropriate (see :ref:`overview <avendesora overview>` and :ref:`add 
command <add command>` for more information) and edit it to your needs.

If after configuring your account you feel the need to change it, you can use 
the :ref:`edit command <edit command>` to do so::

    > avendesora edit manetherentimes

The account name is case insenstive and can be replaced by one of the aliases.
Once created, most of the field values can be retrieved simply by asking for 
them.  For example::

    > avendesora value times username
    username: nynaeve

In general, values can be strings, arrays, dictionaries, and special Avendesora 
classes. For example, you could have an array of security questions:

.. code-block:: python

    questions = [
        Question("What is your mother's maiden name?"),
        Question("What city were you born?"),
        Question("What is first pet's name?"),
    ]

Then you can request the answer to a particular question using its
index::

    > avendesora value times questions.0
    questions.0 (What is your mother's maiden name?): portrayal tentacle fanlight

*questions* is the default array field, so you could have shortened your request 
by using '0' rather than 'questions.0'.  You might be thinking, hey, that is not 
my mother's maiden name. That is because *Question* is a 'generated secret'.  It 
produces a completely random answer that is impossible to predict. Thus, even 
family members cannot know the answers to your security questions.

A dictionary is often used to hold account numbers:

.. code-block:: python

    class TwoRiversCU(Account):
        accounts = {
            'checking': '1234-56-7890',
            'savings': '0123-45-6789',
        }

You then access its values using::

    > avendesora value tworiverscu accounts.checking
    accounts.checking: 1234-56-7890

You might consider your account numbers as sensitive information. In this case 
you can hide them with:

.. code-block:: python

    class TwoRiversCU(Account):
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

    class TwoRiversCU(Account):
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
:class:`avendesora.ObscuredSecret` class (:class:`avendesora.Hide`, 
:class:`avendesora.Hidden`, :class:`avendesora.GPG`, ...) is considered 
sensitive.  It is only given out in a controlled manner. For example, running 
the :ref:`values command <values command>` displays all fields, but the values 
that are sensitive are replaced by instructions on how to view them. They can 
only be viewed individually::

    > avendesora values times
    names: manetherentimes, times, mt
    email: nynaeve@gmail.com
    passcode: <reveal with 'avendesora value manetherentimes passcode'>
    username: nynaeve

Notice the passcode is not shown. You can circumvent this protection by adding 
*is_secret=False* to the argument list of the secret.

The *aliases* and *discovery* fields are not shown because they are considered 
tool fields (see :ref:`discovery` for more information on discovery).  Other 
tool fields include *NAME*, *default*, *browser*, and *default_url*.  *default* 
is the name of the default field, which is the field you get if you do not 
request a particular field. Its value defaults to *password*, *pasphrase*, or 
*passcode* (as set by *default_field* setting), but it can be set to any account 
attribute name or it can be a :ref:`script <scripts>`.  *browser* is the default 
browser to use when opening the account, run the :ref:`browse command <browse 
command>` to see a list of available browsers.

The value of *passcode* is considered sensitive because it is an instance of 
:class:`PasswordRecipe`, which is a subclass of :class:`GeneratedSecret`.  If 
you wish to see the *passcode*, use::

    > avendesora value mt
    passcode: TZuk8:u7qY8%

This value will be displayed for a minute and is then hidden. If you would like 
to hide it early, simply type Ctrl-C.

An attribute value can incorporate other attribute values through use of the 
:class:`avendesora.Script` class as described in :ref:`scripts`. For example, 
consider an account for your wireless router that contains the following:

.. code-block:: python

    class EmondsFieldInnWifi(Account):
        aliases = 'wifi'
        ssid = {
            'emonds_field_inn_guests': Passphrase(),
            'emonds_field_inn_private': Passphrase(),
        }
        guest = Script('SSID: emonds_field_inn_guests{return}password: {ssid.emonds_field_inn_guests}')
        private = Script('SSID: emonds_field_inn_private{return}password: {ssid.emonds_field_inn_private}')

The *ssid* field is a dictionary that contains the SSID and passphrases for each 
of the wireless networks provided by the router.  This is a natural and compact 
representation for this information, but accessing it as a user in this form 
requires two steps to access the information, one to get the SSID and another to 
get the passphrase. This issue is addressed by adding the guest and private 
attributes. The guest and private attributes are scripts that gives the SSID and 
interpolate the passphrase. Now both can easily accessed at once with::

    > avendesora value wifi guest
    SSID: emonds_field_inn_guests
    password: delimit ballcock fibber levitate

Use of *Avendesora* secrets classes (:class:`avendesora.GeneratedSecret` or 
:class:`avendesora.ObscuredSecret`) is confined to the top two levels of account 
attributes, meaning that they can be the value of the top-level attributes, or 
the top-level attributes may be arrays or dictionaries that contain objects of 
these classes, but it can go no further.

It is important to remember that generated secrets use the account name and the 
field name when generating their value, so if you change the account name or 
field name you will change the value of the secret.  For this reason is it 
important to choose a good account and field names up front and not change them.  
It should be very specific to avoid conflicts with similar accounts created 
later.  For example, rather than choosing *Gmail* as your account name, you 
might want to include your username, ex.  *GmailThomMerrilin*.  This would allow 
you to create additional gmail accounts later without ambiguity.  Then just add 
*gmail* as an alias to the account you use most often.

Account and field names are case insensitive. So you can use *Gmail* or *gmail*.  
Also, if the account or field names contains an underscore, you can substitute 
a dash. So if the account name is *Gmail_Thom_Merrilin*, you can use 
*gmail-thom-merrilin* instead.

Normally the user need not specify any of the seeds used when generating 
passwords. However, it is possible to override the master seed and the account 
seed.  To do so, specify these seeds using the *master_seed* and *account_seed* 
attributes on the account. This would allow you to change the account file or 
account name without disturbing the generated secrets.  The values of 
*master_seed* and *account_seed* are not accessible using either the command 
line or the API interfaces.

Account attributes that start with underscore (_) are hidden, meaning that they 
are not shown by the :ref:`values <values command>` or :ref:`interactive 
<interactive command>` commands.  However, you can access their value by
explicitly requesting them using the :ref:`value <value command>` command.
Account attributes should not have a trailing underscore.
Use of a trailing leading underscore creates the risk of collision with an 
attribute added by Avendesora itself.
