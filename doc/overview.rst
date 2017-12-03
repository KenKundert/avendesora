.. _overview:

Overview
========

Use of *Avendesora* will be illustrated through a series of examples.  However, 
before starting it is helpful to know that *Avendesora* provides several 
commands to help you use it. First, it provides a :ref:`help command <help 
command>`::

    > avendesora help

This lists the available help topics. You can ask about a specific topic 
using:

    > avendesora help <topic>

Adding the --browse option allows you to access the online version of the manual 
through your web browser. For example,

    > avendesora help -b accounts

When things go wrong, you can use :ref:`log command <log command>` to quickly 
view the log file::

    > avendesora log

The logfile is kept in the ~/.config/avendesora directory and this command opens 
it directly in your editor.  It can be very helpful in debugging account 
discovery issues.

At this point you should have :ref:`initialized your accounts <initializing 
avendesora>` and :ref:`configured your window manager <configure window 
manager>` and done the :ref:`initial configuration <initial configuration>` of 
*Avendesora*.


.. index::
    single: shell account

Shell Account
-------------

In this example an account is provisioned to hold your Unix login password. You 
will not be able to use *Avendesora* to autotype your passcode when you login 
into your account, but you will be able to use it to enter the passcode when 
running shell commands like *sudo*.

To start, run the command to add an account. By default, three account templates 
are available. They are, in order of complexity: shell, website, and bank. The 
shell template assumes that there is only a passcode and any account discovery 
would be through the window title rather than by examining a URL.

To provision the new account use::

    > avendesora add shell

Your editor should open with something that looks like this:

.. code-block:: python

    class _NAME_(Account):
        desc = '_DESCRIPTION_'
        aliases = '_ALIAS1_ _ALIAS2_'
        passcode = Passphrase()
    # Avendesora: Alternatively use PasswordRecipe('12 2u 2d 2s')
    # Avendesora: or '12 2u 2d 2c!@#$&' to specify valid symbol characters.
        discovery = RecognizeTitle(
            '_TITLE1_', '_TITLE2_',
            script='{passcode}{return}'
        )

    # Avendesora: Tailor the account entry to suit you needs.
    # Avendesora: You can add or delete class attributes as you see fit.
    # Avendesora: The 'n' key should take you to the next field name.
    # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
    # Avendesora: Fields surrounded by << and >> will be hidden.
    # Avendesora: All lines that begin with '# Avendesora:' are deleted.

In this example it is assumed that your editor is Vim. You would jump to the 
first field by typing 'n' (next) and then modify the field by typing 'cw' 
(change word). In this example the first 'n' takes you to *_NAME_* and you would 
use 'cw' to change it to *LinuxLogin*.  You should choose your account name 
carefully. Once set, you should never change an account name because it will 
result in the generated secrets associated with the account changing. If there 
is a chance that you might have more than one linux login, you should add more 
to the account name to make it unique. You can always provide a short easy to 
type alternative as an alias. For example, in this case the account username is 
x57107048, so you might want to add that to the account name to make it unique.
Once you have entered the account name, hit 'Esc' to exit insert mode and type 
'n' to go to the next field, *_DESCRIPTION_*.  The account name is probably all 
the description we need, so you can simply delete this whole field by typing 
'dd' (delete line).  Moving on, you can replace the aliases with 'login' and 
'linux'.  You can add additional aliases or delete the ones you don't need.  We 
will assume that you want to add your username, which was not anticipated by the 
template. To do so type 'o' to open a new line and type:

.. code-block:: python

    username = 'x57107048'

In general using passphrases is preferred to using passwords, the reason being 
that they are much easier to remember and type. That is important in this case 
because you will need to remember and enter your passcode when you login to your 
account, *Avendesora* cannot help you in that case. The template was configured 
to use a passphrase for the passcode, so no change is needed here.

Finally replace the titles with 'sudo \*'.  Once you have something that looks 
like this, you can exit the editor with 'ZZ':

.. code-block:: python

    class LinuxLogin(Account):
        aliases = 'linux login'
        username = 'x57107048'
        passcode = Passphrase()
    # Avendesora: Alternatively use PasswordRecipe('12 2u 2d 2s')
    # Avendesora: or '12 2u 2d 2c!@#$&' to specify valid symbol characters.
        discovery = RecognizeTitle(
            'sudo *',
            script='{passcode}{return}'
        )

    # Avendesora: Tailor the account entry to suit you needs.
    # Avendesora: You can add or delete class attributes as you see fit.
    # Avendesora: The 'n' key should take you to the next field name.
    # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
    # Avendesora: Fields surrounded by << and >> will be hidden.
    # Avendesora: All lines that begin with '# Avendesora:' are deleted.

There is no need to delete the embedded *Avendesora* instructions, they are 
deleted automatically when you save the file.

If you were to immediately edit the account again with::

    > avendesora edit linuxlogin

you should see something like this:

.. code-block:: python

    class LinuxLogin(Account):
        aliases = 'linux login'
        username = 'x57107048'
        passcode = Passphrase()
        discovery = RecognizeTitle(
            'sudo *',
            script='{passcode}{return}'
        )

Notice that all the *Avendesora* instructions were removed.

You can show all the values associated with this account using the :ref:`values 
command <values command>`::

    > avendesora values LinuxLogin
    names: linuxlogin, linux, login
    passcode: <reveal with 'avendesora value linuxlogin passcode'>
    username: x57107048

Notice that the passcode is considered secret, so *Avendesora* does not actually 
show it when displaying all of the values. To see it, use::

    > avendesora value LinuxLogin passcode
    passcode: wigwam mistrust afflict refit

The value command will also write the secret directly to the clipboard::

    > avendesora value --clipboard LinuxLogin passcode

By default *Avendesora* is configured to use the primary clipboard.  You use the 
middle mouse button to paste from the primary clipboard. You can also modify the 
*xsel_executable* to modify this behavior.

You can also write directly to the standard output (normally *Avendesora* writes 
to the TTY so that it can erase any secrets after a minute has elapsed).  In 
this way you can use *Avendesora* within shell scripts (but you should consider 
rewriting you script in Python using the :ref:`Avendesora API <api>`)::

    > pw value -s login 'user="{username}:{passcode}"' | curl -K - https://mywork.com/~x57107048/latest

In this example, I needed to create a arbitrary string containing the username 
and password, so I combined *Avendesora's* :ref:`script <scripts>` feature with 
the --stdout (-s) option to produce and pass the needed string to curl through 
a pipe.

You can also have *Avendesora* attempt to show you your :ref:`login credentials 
<credentials command>` for the account using::

    > avendesora login LinuxLogin
    username: x57107048
    passcode: wigwam mistrust afflict refit

To show the login credentials *Avendesora* looks for candidate usernames 
(username, email) and candidate passcodes (passcode, password, passphrase).

.. index::
    single: typing, reducing
    single: abbreviations

*Avendesora* offers many ways to allow you to reduce or simplify your typing. In 
particular:

1. The account name is case insensitive::

    > avendesora login linuxlogin
    username: x57107048
    passcode: wigwam mistrust afflict refit

2. You can give an alias rather than the account name::

    > avendesora login linux
    username: x57107048
    passcode: wigwam mistrust afflict refit

3. You can replace many command names with a single letter abbreviation::

    > avendesora l linux
    username: x57107048
    passcode: wigwam mistrust afflict refit

4. On the :ref:`value command <value command>`, if you do not specify a field, 
   it will offer the passcode, password, or passphrase if available::

    > avendesora v linux
    passcode: wigwam mistrust afflict refit

5. If the first argument is not recognized as a command name, it is treated as 
   the account name and your login credentials are displayed::

    > avendesora linux
    username: x57107048
    passcode: wigwam mistrust afflict refit

6. Finally, people often alias 'pw' to 'avendesora' in their shell to make 
   running *Avendesora* easier::

    > pw linux
    username: x57107048
    passcode: wigwam mistrust afflict refit

You *LinuxLogin* account was provisioned with account discovery by way of the 
window title. This assumes that your shell adds the currently running command to 
the window title. Most shells are configured to do this by default, or can be 
configured to do so, though it may take some digging on the web to find the 
magic incantation to do so. Notice that one window title was given: 'sudo \*'.  
This matches a sudo command with arguments ('\*' is a wildcard character that 
matches any string of characters). To try out the account discovery, type::

    > sudo make me a sandwich
    [sudo] password for x57107048: <Alt-p>

Here <Alt-p> indicates that you should type your *Avendesora* hot key (hopefully 
you :ref:`set this up earlier<configure window manager>`).  It should run 
'avendesora value'. Since no account was given with this command, *Avendesora* 
attempts to discover which account should be used. It does so by offering the 
window title to each account provisioned with account discovery to see which 
account it matches.  Assume it only matches LinuxLogin. Then the corresponding 
discovery script is run, in which case is '{passcode}{return}'. This script 
simulates the keyboard and types the passcode and then types the enter key, 
which should authenticate you with sudo and allow the command to run.  If the 
window title matches several accounts, then each is offered up in a selection 
box and you choose the one you want.


.. index::
    single: website account

Website Account
"""""""""""""""

In this example an account is provisioned to hold information typical to 
a website::

    > avendesora add website

Your editor should open with something that looks like this:

.. code-block:: python

    class _NAME_(Account):
        desc = '_DESCRIPTION_'
        aliases = '_ALIAS1_ _ALIAS2_'
        username = '_USERNAME_'
        email = '_EMAIL_'
        passcode = PasswordRecipe('12 2u 2d 2s')
    # Avendesora: length is 12, includes 2 upper, 2 digits and 2 symbols
    # Avendesora: Alternatively use '12 2u 2d 2c!@#$&' to specify valid symbol characters.
    # Avendesora: Alternatively use Passphrase()
        questions = [
            Question("_QUESTION1_?"),
            Question("_QUESTION2_?"),
            Question("_QUESTION3_?"),
        ]
        urls = '_URL_'
    # Avendesora: specify urls if there are multiple recognizers.
        discovery = RecognizeURL(
            'https://_URL_',
            script='{email}{tab}{passcode}{return}'
        )
    # Avendesora: Specify list of urls to recognizer if multiple pages need same script.
    # Avendesora: Specify list of recognizers if multiple pages need different scripts.

    # Avendesora: Tailor the account entry to suit you needs.
    # Avendesora: You can add or delete class attributes as you see fit.
    # Avendesora: The 'n' key should take you to the next field name.
    # Avendesora: Use 'cw' to specify a field name, or delete it if unneeded.
    # Avendesora: Fields surrounded by << and >> will be hidden.
    # Avendesora: All lines that begin with '# Avendesora:' are deleted.

Use 'n' to step through the various fields and 'cw' to change the field. You can 
delete any fields that you do not need, or add any that you do.  Here is an 
example of what it might look like when filled out completely after the 
instructions have been removed:

.. code-block:: python

    class Elevate84932153377(Account):
        desc = 'Virgin America frequent flier plan'
        aliases = 'elevate virgin virginamerica'
        phone = '1.877.FLY.VIRGIN'
        account = '8493-215-3377'
        email = 'catharine.stephens658@gmail.com'
        passcode = PasswordRecipe('12 2u 2d 2s')
        questions = [
            Question('mothers maiden name?')),
            Question('fathers middle name?')),
        ]
        urls = 'https://www.virginamerica.com/cms/elevate-frequent-flyer'
        discovery = RecognizeURL(
            'https://virginamerica.com',
            'https://www.virginamerica.com',
            script='{email}{tab}{passcode}{return}'
        )

Notice that a very specific name was given to the account. This was done to 
allow additional Elevate accounts to be created, which might be needed for other 
family members or in case your account was ever compromised. Once you generate 
secrets from an account it is important that you not change the account name as 
that will change the values used for the secrets. Thus, if you choose a very 
selective account name you are less likely to need to change its name in the 
future.  Of course, that name would be difficult to type, so you should give 
simpler names in the account aliases.

You can specify any information you feel is appropriate. Generally that includes 
the account number and the email you gave when creating the account.

You can give your passcode as password using PasswordRecipe. In this case you 
give a string that describes the characteristics of the password you want. The 
first value is the length of the password (12 characters), and then number of 
required characters of each type (2 upper case, 2 digits, and 2 symbols). If you 
are restricted to a specific set of symbols, such as +=_-, you can use '2c+=_-' 
to signify that two of the specified characters should be included (ex: 
PasswordRecipe('12 2u 2d 2c+=_-').  Alternatively, you can specify Passphrase() 
like in the shell account above.  Or, you can explicitly specify the password.  
In this case you should indicate that the value is a secret so it is somewhat 
protected.  There are two ways of doing that.

1. You specify the password as an argument to Hide(). Example: Hide('catch22').
   In this case *Avendesora* protects the value as a secret, but it will show up 
   unconcealed when viewing your account file.
2. You can specify the password embedded in << and >>. For example: <<catch22>>.  
   If you do that, the value is converted to base64 and passed as an argument to 
   Hidden(). Thus, when you view the account file you will see: 
   Hidden("Y2F0Y2gyMg=="). This makes it harder for anybody that happens to 
   glance over your shoulder while you have your account file open to recognize 
   and remember your password. In this case the encoded password is not 
   encrypted, and it is easy to recover using *Avendesora*'s :ref:`reveal 
   command <reveal command>` or the linux base64 command.

Many websites ask 'security' questions. These questions represent a back door 
into your account. If you forget your password, you can access your account by 
answering these questions. However, anybody else that happens to know the 
answers to these questions, such as your evil twin, can also use them to access 
your account. *Avendesora* defeats your evil twin by generating completely 
random answers to these personal questions. By default, Question() takes 
a string and turns it into three random words (be careful not to change the 
string after you have given the website the answers; doing so changes the 
answers). You can specify as many questions needed.

If you are not free to give arbitrary answers to your questions, such as if the 
website gives you a small set of acceptable answers, then you can give the 
answer along with the question:

.. code-block:: python

    questions = [
        Question('favorite subject in school?', answer=<<recess>>)),
        Question('favorite composer?' answer=<<chuck berry>>)),
    ]

Lastly this account sets up the web interface by specifying *urls* and 
*discovery*. The *urls* field is used by the :ref:`browse command <browse 
command>`, which opens your browser and navigates to the login page.  For 
example::

    > avendesora browse virgin

This can generally be done directly from your window manager, allowing your to 
open your account without needing to use a shell.  In Gnome you can do so with 
Alt-F2 (Run Command).  You can get the same functionality from other window 
managers by installing and assigning *dmenu* to a keyboard shortcut.

The *discovery* field is used to recognize that this is the account to use when 
*Avendesora* is asked to login into the *virginamerica.com* site. Notice that 
several URLs are given to RecognizeURL(), this is necessary when the website 
allows you to login using different domain names. RecognizeURL() is a variant of 
RecognizeTitle() that is attuned to the titles generated by browsers that have 
been configured to place the URL in the window title bar. This makes it more 
robust in this particular case. Also notice that the expected protocol is given 
with the URLs (https). In this way, *Avendesora* will refuse to send your login 
credentials if the connection is not encrypted using https protocol.  The final 
argument to RecognizeURL() is the script that logs you in. In this case the 
script specifies that the value of the email field should be typed into the 
browser, followed by a tab, then the passcode, then a return.

It is possible to configure account discovery to support several secrets. To do 
so, place the recognizers in a list and specify different scripts for each. For 
example, many websites ask you to answer your security questions in order to 
confirm you are really you. This becomes easier with:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'https://virginamerica.com',
            'https://www.virginamerica.com',
            script='{email}{tab}{passcode}{return}',
            name='login'
        ),
        RecognizeURL(
            'https://virginamerica.com',
            'https://www.virginamerica.com',
            script='{questions}{return}'
            name='challenge question'
        ),
    ]

In this case if you trigger *Avendesora* (using :ref:`Alt-p<configure window 
manager>`) while on the Virgin America website, it will respond by asking you if 
you want to login or answer a challenge question (in this case both recognizers 
trigger, forcing the choice). You can give different URLs for each case so that 
the choice is made automatically for you:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'https://www.virginamerica.com/cms/elevate-frequent-flyer',
            script='{email}{tab}{passcode}{return}',
            name='login'
        ),
        RecognizeURL(
            'https://www.virginamerica.com/cms/challenge',
            script='{questions}{return}'
            name='challenge question'
        ),
    ]


.. index::
    single: bank account

Bank Account
""""""""""""

Bank accounts are similar to web accounts, but generally contain multiple 
account numbers and even more secrets.  Create a bank account using::

    > avendesora add bank

After you edit the various fields you may end up with something like this:

.. code-block:: python

    class MechanicsBank(Account):
        aliases = 'mb bank'
        username = Passphrase(length=2)
        email = 'regina.hale481@aol.com'
        checking = <<008860636145>>,
        savings = <<029370021509>>,
        creditcard = <<5251-0148-2064-4156>>,
        ccv = <<588>>
        expiration = <<03/2020>>
        ccn = Script('{account.creditcard}{tab}{ccv}{tab}')
        passcode = PasswordRecipe('16 2u 2l 2d 2c#%=:_-<>')
        verbal = Passphrase(length=2)
        questions = [
            Question('mothers maiden name?')),
            Question('fathers middle name?')),
        ]
        routing = '013521325'
        customer_support = '''
            credit cards: 800-730-6259
            banking: 800-861-5715
        '''
        urls = 'https://secure.mechanicsbank.com/login'
        discovery = RecognizeURL(
            'https://mechanicsbank.com',
            'https://www.mechanicsbank.com',
            'https://secure.mechanicsbank.com',
            'https://online.mechanicsbank.com',
            script='{username}{tab}{passcode}{return}'
        )

In this case, since this account holds real money, a bit more attention is given 
to security. For example, the username was specified as a 2 word passphrase, 
making very unlikely that anyone could guess your username. Furthermore, your 
account numbers and your credit-cards CCV number are hidden by decorating them 
with << >> (you could also just use Hide()).

Also, a verbal password is include. Many financial institutions allow you to set 
up a verbal password that you use when calling in. This is an important 
protection in that it stops people that know you well, such as your ex, from 
calling in and impersonating you. A short passphrase is perfect for this use as 
it is easy to communicate to someone over the phone.

In this example separate fields are used for each account number. If you have 
access to the accounts of several people, for example you and your children, you 
might use a dictionary for the accounts of each person, as follows:

.. code-block:: python

    regina = dict(
        checking = <<008860636145>>,
        savings = <<029370021509>>,
        creditcard = <<5251-0148-2064-4156>>,
    )
    timmy = dict(
        checking = <<275137908190>>,
        savings = <<874647693848>>,
    )
    katie = dict(
        checking = <<718467200674>>,
        savings = <<623691894130>>,
    )

Now to get Timmy's checking account number you would use::

    avendesora bank timmy.checking

Security questions and account discovery are handled as given above.

The *ccn* or credit card number field is given as a script.
With this you can navigate to any website that needs your credit card number and 
CCV and enter it by typing::

    <Alt-F2> avendesora bank ccn

Here <Alt-F2> is assumed to be the hot key sequence that runs a shell command 
directly from the window manager (Gnome uses Alt-F2, but yours may be 
different).  Doing so causes your credit card number, followed by a tab, 
followed by your CCV, and followed by another tab to be typed into the page. You 
could conceivably start by typing your name and follow with your address, but 
there is enough variability in websites that this would likely not work on all 
of them, so it is generally best to limit the script to a small number of the 
most helpful fields.


.. _finding accounts:

Finding Accounts
----------------

*Avendesora* provides two ways of finding account names if you do not remember 
them.  First is the :ref:`find command <find command>`, which given a bit of 
text lists all of the accounts that contain that text in their names or their 
aliases. For example::

    > avendesora find bank
    bank-america (ba, boa, bofa)
    citibank-mastercard (mc, mastercard, citibank)
    mechanicsbank (mb bank)

The next is the :ref:`search command <search command>`, which given a bit of 
text lists all of the accounts that contain that text in any of the non-secret 
account values.  For example::

    > avendesora search bank
    bank-america (ba, boa, bofa)
    capitalone (co, ing)
    citibank-mastercard (mc, mastercard, citibank)
    mechanicsbank (mb bank)
    wellsfargo (wf)

In both cases the name of the account is listed first followed by the account 
aliases (within parentheses).


.. _modifying accounts:

Modifying Accounts
------------------

Once an account exists, it can modified using the :ref:`edit command <edit 
command>`::

    > avendesora edit bank

This opens the MechanicsBank account in your editor (you can select your editor 
by modifying the *edit_account* setting).  Once you modify your account, you 
should save the file and exit the editor. The change will be checked and if 
there are any errors, you will be given a chance to reopen the account file and 
fix the account.


Additional Features
-------------------

In addition what has already been introduced, *Avendesora* provides a collection 
of advanced features. Those include ...

-  The :ref:`archive <archive command>` and :ref:`changed <changed command>` 
   commands provide an ability to create a backup copy of all your passwords.  
   These command are described in the section on :ref:`upgrading <upgrading>`.
-  Two techniques that provide an extra measure of security for accounts are 
   :ref:`stealth accounts <stealth accounts>` and :ref:`misdirection 
   <misdirection>`.
-  *Avendesora* provides several ways that help protect you from :ref:`phishing 
   <phishing>`. You should be aware of these methods to make sure you use them.
-  *Avendesora* allows you to share master seeds with a partner, and once done 
   allow you to easily and securely create new shared secrets. This is described 
   in the section on :ref:`collaboration <collaboration>`.
-  Once you share a master seed, you can use the :ref:`identity command 
   <identity command>` as described in :ref:`confirming identity <confirming 
   identity>` to securely verify that you are communicating with your partner.
-  You can quickly print out the :ref:`NATO phonetic alphabet <phonetic>`, which 
   can be useful when trying to communicate complex character sequences over the 
   phone.
