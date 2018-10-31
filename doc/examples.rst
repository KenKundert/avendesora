Examples
========

.. index::
    single: questions
    single: security questions
    single: challenge questions

Challenge Questions
-------------------

Websites originally used challenge questions to allow you to re-establish your 
identity if you lose your user name or password, so it was enough to simply save 
the answers so that they were available if needed. But now many websites require 
you to answer the challenge questions if the site does not recognize your 
browser because your cookie expired or was deleted. As such, people need to 
answer their challenge questions with much more frequency. Generally the site 
will save your answers to 4 or 5 challenge questions, and will present you with 
1 or 2 at random. You must answer them correctly before you are allowed to 
login.  To accommodate these needs, *Avendesora* saves the challenge questions 
and either stores or generates the answers. It is also makes it easy for you to 
autotype the answer to any of your questions.

The following shows how to configure an account to support challenge questions.

.. code-block:: python

    class BankOfAmerica(Account):
        aliases = 'boa bankamerica'
        username = 'matrim'
        passcode = PasswordRecipe('12 2l 2u 2d 2s')
        questions = [
            Question('elementary school?'),
            Question('favorite foreign city?'),
            Question('first pet?'),
            Question('what year was your father born?'),
            Question('favorite movie?'),
        ]
        discovery = [
            RecognizeURL(
                'https://www.bankofamerica.com/',
                script='{username}{tab}{passcode}{return}'
            ),
            RecognizeURL(
                'https://secure.bankofamerica.com',
                script='{questions}{tab}',
            ),
        ]

In this case 5 questions are supported. When you are first required to set up 
your challenge questions the website generally presents you with 20 or 30 to 
choose form.  Simply choose the first few and add them to your account.

Then use the :ref:`value command <value command>` to generate the answers and 
copy them into the website.  You need not enter the questions into *Avendesora* 
exactly, but once you provide your website with the generated answers you must 
not change the questions in any way because doing so would change the answers.  
Finally, the first time you are required to enter answers to the challenge 
questions, take note of the URL and add a discovery entry that matches the url 
and generates the questions. In most cases you will not be able to specify 
a single question, so simply specify the array and *Avendesora* will allow you 
to choose a particular question when you request an answer. Specifically, when 
the website takes you to the challenge question page, click in the field for the 
first answer and type the hotkey that runs *Avendesora* in autotype mode.  
*Avendesora* should recognize the page and allow you to identify the question.  
It will then autotype the answer into the field and then move to the next field.  
Alternately, if you terminate the script with '{return}' rather than '{tab}', it 
will take you to the next page.

In some cases the website makes you choose from a fixed set of answers. In this 
case you would save the answer with the question as follows:

.. code-block:: python

    class BankOfAmerica(Account):
        ...
        questions = [
            Question('elementary school?', answer='MLK Elementary'),
            Question('favorite foreign city?', answer='Kashmir'),
            Question('first pet?', answer='Spot'),
            Question('what year was your father born?', answer='1950'),
            Question('favorite movie?', answer='A boy and his dog'),
        ]
        ...


.. index::
    single: google
    single: gmail
    single: amazon
    single: two page authentication

Two Page Authentication
-----------------------

A new trend in recent years is websites that use two-page authentication.  This 
is where you enter your user name or email on one page, you then submit it and 
get another page that you use to enter your password, which requires a second 
submission.  Google moved to two-page authentication some time ago, and now 
Amazon seems to be switching as well.  Originally this was intended as an 
anti-phishing strategy.  After entering your user name you are shown a site 
image and phrase that you can use to confirm that you are logging in to the 
correct site.  This is unnecessary when using *RecognizeURL* because it will 
only enter your user name and password if the URL is correct. Recently however, 
sites have dispensed with the site image and phrase, but still spread the login 
in process over two pages. It is not clear why they do this. There does not seem 
to be any security benefit. In fact it acts to reduce security by making it more 
difficult to use a password manager.  Unfortunately this is all too common.  
Companies talk a good game when it comes to security, but all to often employ 
practices that are antithetical to good security.

There are two approaches to handling two-page authentication in *Avendesora*.  
The first would be to split the account discovery into two steps. For example:

.. code-block:: python

    class Gmail(Account):
        aliases = 'email'
        username = 'matrim.cauthon'
        passcode = Passphrase()
        urls = 'https://accounts.google.com/signin/v2/identifier'
        discovery = [
            RecognizeURL(
                'https://accounts.google.com/ServiceLogin/identifier',
                'https://accounts.google.com/signin/v2/identifier',
                script='{username}{return}',
                name='username',
            ),
            RecognizeURL(
                'https://accounts.google.com/signin/v2/sl/pwd',
                script='{passphrase}{return}',
                name='passcode',
            ),
        ]

Notice that there are two instances of *RecognizeURL*, both looking for 
different URLs. You would trigger *Avendesora* to enter the user name, then 
trigger it again to enter the passcode. This is the best case situation in that 
the URLs for each page are distinct.  However, some sites make it difficult to 
distinguish what is being asked for just by looking at the URL.  Amazon is one 
of those:

.. code-block:: python

    class Amazon(Account):
        email = 'matrim@tworivers.com'
        passcode = Passphrase()
        discovery = [
            RecognizeURL(
                'https://www.amazon.com/ap/signin',
                script = '{email}{return}',
                name = 'email',
            ),
            RecognizeURL(
                'https://www.amazon.com/ap/signin',
                script = '{passcode}{return}',
                name = 'passcode',
            ),
        ]

Notice that the URL is the same for both recognizers, which causes *Avendesora* 
to ask you which you want each time you request either.  A variation on this is 
to have different URLs for each page, but one URL is a subset of the other. For 
example, 'andorsavings.com/signin' and 'andorsavings.com/signin/pwd'.  By 
default *Avendesora* will offer both when it comes time to enter the password, 
but adding 'exact_path=True' to the username recognizer causes *Avendesora* to 
be more selective.

The second approach is use just one recognizer that outputs both the user name 
and password, but to add a delay between them. For example:

.. code-block:: python

    class Amazon(Account):
        email = 'amazon@shalmirane.com'
        passcode = Passphrase()
        discovery = [
            RecognizeURL(
                'https://www.amazon.com/ap/signin',
                script = '{email}{return}{sleep 2}{passcode}{return}',
                name = 'both',
            ),
        ]

In this way you would only need to trigger *Avendesora* once.
You might have to adjust the sleep time to be able to log in reliably.


.. index::
    single: Chrome

Chrome
~~~~~~

The Chrome browser seems to have a bug that can interfere with its use with 
account discovery. In the two step process used when logging in, the site might 
pre-fill-in your user name so you do not have to enter it explicitly, you just 
have to click *next*. Chrome then takes you to the page where you are expected 
to enter your password, however when it does so it does not update the window 
title to match the new page.  Then Avendesora sees the wrong URL and either 
enters the wrong thing or does not recognize the page. To work around this bug, 
you must refresh the page when you land on the password page before activating 
Avendesora.


.. index::
    single: wireless router

Wireless Router
---------------

Wireless routers typically have two or more secrets consisting of the admin 
password and the passwords for one or more wireless networks. For example, the 
router in this example supports two networks, a privileged network that allows 
connections to the various devices on the local network and the guest network 
that that only access to the internet.  In this case all three employ pass 
phrases. The admin password is held in *passcode* and the network names and 
passwords are held in the *network_passwords* array. To make the information 
about each network easy to access from the command line, two scripts are 
defined, *guest* and *privileged*, and each produces both the network name and 
the network password for the corresponding networks.

Secret discovery handles two distinct cases. The first case is when from within 
your browser you navigate to your router (ip=192.168.1.1). In this situation, 
the URL is matched and the script is run that produces the administrative 
username and password.  The second case is when you attempt to connect to 
a wireless network and a dialog box pops up requesting the SSID and password of 
the network you wish to connect to.  Running *xwininfo* shows that the title of 
the dialog box is 'Wi-Fi Network Authentication Required'. When this title is 
seen, both the title recognizers match, meaning that both the privileged and the 
guest credentials are offered as choices.

.. code-block:: python

    class NetgearAC1200_WirelessRouter(Account):
        NAME = 'home-router'
        aliases = 'wifi'
        admin_username = 'admin'
        admin_password = Passphrase()
        default = 'admin_password'
        networks = ["Occam's Router", "Occam's Router (guest)"]
        network_passwords = [Passphrase(), Passphrase()]
        privileged = Script('SSID: {networks.0}{return}password: {network_passwords.0}')
        guest = Script('SSID: {networks.1}{return}password: {network_passwords.1}')
        discovery = [
            RecognizeURL(
                'http://192.168.1.1',
                script='{admin_username}{tab}{admin_password}{return}'
            ),
            RecognizeTitle(
                'Wi-Fi Network Authentication Required',
                script='{networks.0}{tab}{network_passwords.0}{return}',
                name='privileged network'
            ),
            RecognizeTitle(
                'Wi-Fi Network Authentication Required',
                script='{networks.1}{tab}{network_passwords.1}{return}',
                name='guest network'
            ),
        ]
        model_name = "Netgear AC1200 wireless router"


.. index::
    single: credit cards

Credit Card Information
-----------------------

Many websites offer to store your credit card information. Of course, we have 
all heard of the massive breeches that have occurred on such websites, often 
resulting in the release of credit card information.  So all careful denizens of 
the web are reluctant to let the websites keep their information. This results 
in you being forced into the tedious task of re-entering this information.

*Avendesora* can help with this. If you have a website that you find yourself 
entering credit card information into routinely, then you can use the account 
discovery and autotype features of *Avendesora* to enter the information for 
you.

For example, imagine that you have a Citibank credit card that you use routinely 
on the Costco website.  You can configure *Avendesora* to automatically enter 
your credit card information into the Costco site with by adding an account 
discovery entry to your Citibank account as follows:

.. code-block:: python

    class CostcoCitiVisa(Account):
        aliases = 'citi costcovisa'
        username = 'mcauthon'
        email = 'matrim@gmail.com'
        account = '1234567889012345'
        expiration = '03/2019'
        cvv = '233'
        passcode = PasswordRecipe('12 2u 2d 2s')
        verbal = Question('Favorite pet?', length=1)
        questions = [
            Question("Fathers profession?"),
            Question("Last name of high school best friend?"),
            Question("Name of first pet?"),
        ]
        urls = 'https://online.citi.com'
        discovery = [
            RecognizeURL(
                'https://online.citi.com',
                script='{username}{tab}{passcode}{return}',
                name='login'
            ),
            RecognizeURL(
                'https://www.costco.com/CheckoutPaymentView',
                script='{account}{tab}{expiration}{tab}{cvv}{tab}Matrim Cauthon{return}',
                name='card holder information'
            ),
        ]

This represents a relatively standard *Avendesora* description of an account.  
Notice that it contains the credit card number (*account*), the expiration date 
(*expiration*) and the CVV number (*cvv*). This is raw information the autotype 
script will pull from. The credit card and the CVV values are sensitive 
information and should probably be concealed.

Also notice the two :class:`avendesora.RecognizeURL` entries in *discovery*.  
The first recognizes the CitiBank website. The second recognizes the Costco 
check-out page. When it does, it runs the following script::

    {account}{tab}{expiration}{tab}{cvv}{tab}Matrim Cauthon{return}

That script enters the account number, tabs to the next field, enters the 
expiration date, tabs to the next field, enters the CVV, tabs to the next field, 
enters the account holders name, and finally types return to submit the 
information (you might want to delete the {return} so that you have a chance to 
review all the information before you submit manually. Or you could continue the 
script and give more information, such as billing address.

Conceptually this script should work, but Costco, like many websites, uses 
Javascript helpers to interpret the fields. These helpers are intended to give 
you immediate feedback if you typed something incorrectly, but they are slow and 
can get confused if you type too fast. As is, the first one or two fields would 
be entered properly, but the rest would be empty because they were entered by 
*Avendesora* before the page was ready for them. To address this issue, you can 
put delays in the script::

    {account}{tab}{sleep 0.5}{expiration}{tab}{sleep 0.5}{cvv}{tab}{sleep 0.5}Matrim Cauthon{return},

Now the account can be given in its final form. This differs from the one above 
in that the *account* and *cvv* values are concealed and the delays were added 
to the Costco script.

.. code-block:: python

    class CostcoCitiVisa(Account):
        aliases = 'citi costcovisa'
        username = 'mcauthon'
        email = 'matrim@gmail.com'
        account = Hidden('MTIzNCA1Njc4IDg5MDEgMjM0NQ==')
        expiration = '03/2019'
        cvv = Hidden('MjMz')
        passcode = PasswordRecipe('12 2u 2d 2s')
        verbal = Question('Favorite pet?', length=1)
        questions = [
            Question("Fathers profession?"),
            Question("Last name of high school best friend?"),
            Question("Name of first pet?"),
        ]
        discovery = [
            RecognizeURL(
                'https://online.citi.com',
                script='{username}{tab}{passcode}{return}',
                name='login'
            ),
            RecognizeURL(
                'https://www.costco.com/CheckoutPaymentView',
                script='{account}{tab}{sleep 0.5}{expiration}{tab}{sleep 0.5}{cvv}{tab}{sleep 0.5}Matrim Cauthon{return}',
                name='card holder information'
            ),
        ]

This approach requires that you anticipate those sites into which you well enter 
the credit card information.  Alternatively, you add a script to your credit 
card account that outputs the credit card information, and then run *Avendesora* 
in such a way that the credit card information into the webpage. To do this 
requires two things. First, add a script to the account that combines and 
outputs the credit card information. For example:

.. code-block:: python

        ccn = Script('{account}{tab}{cvv}{tab}')

In this case the amount of information requested is limited to increase the 
chance that the result will be compatible with a large number of websites.  Then 
run *Avendesora* from the window manager::

    Alt-F2 avendesora citi ccn

Here, Alt-F2 is the hot key Gnome uses to execute a command. This causes 
*Avendesora* to run the *ccn* script. Since *Avendesora* running from the window 
manager does not have access to a TTY it will instead mimic the keyboard and 
autotype the credit card information into the active window.


.. index::
    single: swarm accounts

Swarm Accounts
--------------

You might find the need to have many accounts at one website, and for simplicity 
would like to share most of the account information. For example, you would 
share the URL and perhaps the password, but not the usernames.

You might wish to have multiple email addresses from a single email provider 
like gmail, or perhaps you you would multiple accounts at a review site, like 
yelp.

In this case we give the list of account name in the *usernames* attribute. Then 
we use Python list comprehensions that use the *usernames* array to construct 
other values. That way to add a new account, you only need modify *usernames* 
and everything else is updated automatically.

.. code-block:: python

    class YandexMail(Account):
        aliases = 'yandex'
        usernames = 'rand.alThor aviendha rhuarc sorilea amys'.split()
        credentials = ' '.join(
            ['usernames.%d' % i for i in range(len(usernames))] + ['passcode']
        )
        email = [n + '@yandex.com' for n in usernames]
        passcode = PasswordRecipe('12 2u 2d 2s')
        questions = [
            Question('Surname of favorite musician?'),
        ]
        urls = 'https://mail.yandex.com'
        discovery = [
            RecognizeURL(
                'https://mail.yandex.com',
                script='{email[%s]}{tab}{passcode}{return}' % i,
                name=n,
            ) for i, n in enumerate(usernames)
        ]

Now, running the :ref:`credentials command <credentials command>` gives::

    > avendesora yandex
    usernames: rand.alThor
    usernames: aviendha
    usernames: rhuarc
    usernames: sorilea
    usernames: amys
    passcode: B-F?i0z8GcDL

This example shows that the capabilities of the Python language can be used in 
the accounts files to increase the capabilities of *Avendesora* in unexpected 
ways.


.. index::
    single: shell command recognition

Recognizing Shell Commands
--------------------------

Modern shells inform their terminal emulator of the currently running command.  
Modern terminal emulators then use that information to display the command in 
the window title. Generally this happens automatically, but if it is not working 
for you, you may have to manually configure your shell. Generally, you configure 
the shell by changing the value of the variable that sets the command prompt.

If your window manager is configured to not show window titles, you can still 
determine the title using *xwininfo*.

If your shell does not set the window title you can still use the window title 
to trigger *Avendesora* secrets recognition by explicitly setting the window 
title using *xdotool*. For example::

    #!/bin/bash

    original_title=`xdotool getactivewindow getwindowname`
    xdotool getactivewindow set_window --name 'Home email'
    mutt -F ~/.config/mutt/home
    xdotool getactivewindow set_window --name "$original_title"

Once you have desired information in the window title, you can use the use 
:class:`avendesora.RecognizeTitle` to trigger *Avendesora*. For example, you 
might use the following as the entry for you Linux password:

.. code-block:: python

    class Login(Account):
        desc = 'Linux login'
        aliases = 'linux sudo'
        passcode = Passphrase()
        discovery = RecognizeTitle(
            'sudo *',
            script='{passcode}{return}'
        )

You cannot use *Avendesora* to login to Linux, however once you have logged in 
you can use *Avendesora* to deliver your linux password to the sudo command.

An alternative to using window titles is to trigger *Avendesora* secrets 
recognition is to use :class:`avendesora.RecognizeFile` as shown in 
:ref:`discovery`.
