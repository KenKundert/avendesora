.. _advanced usage:

Advanced Usage
==============

.. index::
    single: phishing

.. _phishing:

Avoiding Phishing Attacks
-------------------------

Phishing is a very common method used on the web to get people to unknowingly 
divulge sensitive information such as account credentials.  It is generally 
accomplished by sending misleading URLs in email or placing them on websites. 
When you visit these URLs you are taken to a site that looks identical to the 
site you were expecting to go to in the hope that you are tricked into giving up 
your account credentials.  It used to be that if you carefully inspected the URL 
you could spot deception, but even that is no longer true.

*Avendesora* helps you avoid phishing attacks in two ways. First, you should 
never go to one of your secure sites by clicking on a link.  Instead, you should 
use *Avendesora*'s :ref:`browse command <browse command>`::

    avendesora browse chase

In this way you use the URL stored in *Avendesora* rather than trusting a URL 
link provided by a third party. Second, you should auto-enter the account 
credentials using *Avendesora*'s account discovery based on 
:class:`avendesora.RecognizeURL` (be sure to use 
:class:`avendesora.RecognizeURL` for websites rather than 
:class:`avendesora.RecognizeTitle` when configuring account discovery, 
:class:`avendesora.RecognizeURL` is not fooled by phishing sites).


.. index::
    single: discovery
    single: account discovery
    single: configuring browser
    single: browser configuration

.. _discovery:

Account Discovery
-----------------

If you do not give an account to ':ref:`avendesora value <value command>`', 
*Avendesora* tries to determine the account by simply asking each account if it 
is suitable.  An account can look at the window title, the user name, the host 
name, the working directory, and the environment variables to determine if it is 
suitable.  If so, it nominates itself. If there is only one account nominated, 
that account is used. If there are multiple nominees, then a small window pops 
up allowing you to choose which account you wish to use.

.. index::
    single: RecognizeTitle

To configure an account to trigger when a particular window title is
seen, use:

.. code-block:: python

    discovery = RecognizeTitle(
        'Chase Online *',
        script='{username}{tab}{passcode}{return}'
    )

The title can either be a glob string or a function.  For glob strings, '*' 
matches any combination of characters and '?' matches any single character (see 
`fnmatch <https://docs.python.org/3.6/library/fnmatch.html>`_ for a complete 
description of the glob syntax).  In this way, the entire title must be 
matched.  For functions, the argument is the title and the return value must be 
truthy if the title matched and falsey otherwise.  The script describes what 
*Avendesora* should output when there is a match. In this case it outputs the 
username field, then a tab, then the passcode field, then a return (see 
:ref:`scripts`).

Matching window titles can be fragile, especially for websites
because the titles can vary quite a bit across the site and over
time. To accommodate this variation, you can give multiple glob
patterns:

.. code-block:: python

    discovery = RecognizeTitle(
        'CHASE Bank*',
        'Chase Online*',
        script='{username}{tab}{passcode}{return}'
    )

.. index::
    single: RecognizeURL

.. index::
    single: Firefox browser
    single: Chrome browser
    single: browsers

However, in general, it is better to match the URL. This can be done in Firefox
and Chrome by adding extensions that place the URL in the window title and then
using :class:`avendesora.RecognizeURL` to do the recognition.

If you use Firefox, you should install the `Add URL to Window Title
<https://addons.mozilla.org/en-US/firefox/addon/add-url-to-window-title>`_
extension by Eric.  It is a plugin that makes discovery easier and more robust
by adding the URL to the title.  For *Chrome* the appropriate plugin is  is `URL
in Title
<https://chrome.google.com/webstore/detail/url-in-title/ignpacbgnbnkaiooknalneoeladjnfgb>`_
by Guillaume Ryder.  It is recommended that you install the appropriate one into
your browser.  For *Add URL To Window Title*, set the following options::

    show full URL = yes
    separator string = '-'
    show field attributes = no

For *URL in Title*, set::

    tab title format = '{title} - {protocol}://{hostname}{port}/{path}'

.. index::
    single: qutebrowser

If you use `qutebrowser <https://qutebrowser.org>`_ as your browser, you should 
add the following to your ~/.config/qutebrowser/config.py file:

.. code-block:: python

    c.window.title_format = '{title} - {current_url} - qutebrowser'

:class:`avendesora.RecognizeURL` is designed to recognize such titles. Once you 
have
deployed the appropriate plugin, you can use:

.. code-block:: python

    discovery = RecognizeURL(
        'https://chaseonline.chase.com',
        'https://www.chase.com',
        script='{username}{tab}{passcode}{return}'
    )

When giving the URL, anything specified must match and globbing is
not supported. If you give a partial path, by default *Avendesora*
matches up to what you have given, but you can require an exact
match of the entire path by specifying ``exact_path=True`` to
:class:`avendesora.RecognizeURL`.  If you do not give the protocol, the
default_protocol (https) is assumed.

In general you should use :class:`avendesora.RecognizeURL` rather than
:class:`avendesora.RecognizeTitle` for websites if you can. Doing so helps
protect you from phishing attacks by carefully examining the URL.

When account discovery fails it can be difficult to determine what is going
wrong. When this occurs, you should first examine the log file::

    > avendesora log

It should show you the window title and the recognized title components. You
should first assure the title is as expected. If *Add URL to Window Title* or
*URL in Title* generated the title, then the various title components should
also be shown.  Then run *Avendesora* as follows::

    > avendesora value --verbose --title '<title>'

The title should be copied from the log file. The verbose option
causes the result of each test to be included in the log file, so
you can determine which recognizer is failing to trigger.  You can
either specify the verbose option on the command line or in the
config file.


Recognizers
"""""""""""

The following recognizers are available::

    RecognizeAll(<recognizer>..., [script=<script>])
    RecognizeAny(<recognizer>..., [script=<script>])
    RecognizeTitle(<title>..., [script=<script>])
    RecognizeURL(<title>..., [script=<script>, [name=<name>,]] [exact_path=<bool>])
    RecognizeHost(<host>..., [script=<script>])
    RecognizeUser(<user>..., [script=<script>])
    RecognizeCWD(<cwd>..., [script=<script>])
    RecognizeEnvVar(<name>, <value>, [script=<script>])
    RecognizeNetwork(<mac>..., [script=<script>])
    RecognizeFile(<path>, [<contents>,] [<ttl>,] [script=<script>])

.. index::
    single: RecognizeAll
    single: RecognizeAny

:class:`avendesora.RecognizeAll` and :class:`avendesora.RecognizeAny` can be 
used to combine several recognizers. For example:

.. code-block:: python

    discovery = RecognizeAll(
        RecognizeTitle('sudo *'),
        RecognizeUser('hhyde'),
        script='{passcode}{return}'
    )

If the recognizers are given in an array, all are tried, and each
that match are offered. For example:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'http://www.querty-forum.org',
            script='admin{tab}{passcode}{return}',
            name='admin',
        ),
        RecognizeURL(
            'http://www.querty-forum.org',
            script='thecaretaker{tab}{passcode}{return}',
            name='thecaretaker',
        ),
    ]

In this case, both recognizers recognize the same URL, thus they are both be 
offered for this site.  But each has a different script. The name allows the 
user to distinguish the available choices.

If there is a need to distinguish URLs where is one is a substring of another, 
you can use *exact_path*:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'https://mybank.com/Authentication',
            script='{username}{return}',
            exact_path=True,
        ),
        RecognizeURL(
            'https://mybank.com/Authentication/Password',
            script='{passcode}{return}',
            exact_path=True,
        ),
    ]

The URL may contain the # character. This character separates the 'fragment' 
from the rest of the URL. You can distinguish two otherwise indistinguishable 
URLs by their fragment. For example, *BitWarden* requests the username and 
password on a page with a URL of https://vault.bitwarden.com/#/ and it request 
only the password on a page with a URL of https://vault.bitwarden.com/#/lock.  
Normally the fragment (the part of the URL that follows the #) is ignored when 
determining whether a URL matches, however you can explicitly specify that it 
should be included as follows:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'https://vault.bitwarden.com',
            script='{email}{tab}{passcode}{return}',
            fragment='/',
        ),
        RecognizeURL(
            'https://vault.bitwarden.com',
            script='{passcode}{return}',
            fragment='/lock',
        ),
    ]


.. index::
    single: RecognizeFile

:class:`avendesora.RecognizeFile` checks to determine whether a particular file 
has been created recently.  This can be use in scripts to force secret 
recognition.  For example, the titles used by Firefox and Thunderbird when 
collecting the master password is either non-existent or undistinguished.  These 
programs also produce a large amount of uninteresting chatter on their output, 
so it is common to write a shell script to run the program that redirects their 
output to /dev/null.  Such a script can be modified to essentially notify 
*Avendesora* that a particular password is desired.  For example, for 
Thunderbird::

    #!/bin/sh
    touch /tmp/thunderbird-1024
    /usr/bin/thunderbird > /dev/null

Here I have adding my user id (uid=1024) to make the filename unique
so I am less likely to clash with other users. Alternately, I could have simply 
placed the file in my home directory.

Then, *Avendesora* will recognize *Thunderbird* if you add the following 
*discovery* field to your *Thunderbird* account:

.. code-block:: python

    class Thunderbird(Account):
        desc = 'Master password for Thunderbird'
        passcode = Password()
        discovery = RecognizeFile(
            '/tmp/thunderbird-1024', wait=60, script='{passcode}{return}'
        )

If the specified file exists and has been updated within the last 60 seconds, 
then secret is recognized.  You can specify the amount of time you can wait in 
between running the script and running *Avendesora* with the 'wait' argument, 
which takes a number of seconds.  It defaults to 60.

Using this particular approach, every secret needs its own file. But you can 
share a file by specifying the file contents.  Then the script could be 
rewritten as::

    #!/bin/sh
    echo thunderbird > ~/.avendesora-password-request
    /usr/bin/thunderbird > /dev/null

Then you would add something like the following to your *Thunderbird* account 
entry:

.. code-block:: python

    class Thunderbird(Account):
        desc = 'Master password for Thunderbird'
        passcode = Password()
        discovery = RecognizeFile(
            '~/.avendesora-password-request',
            contents='thunderbird',
            script='{passcode}{return}'
        )


Terminal Windows
""""""""""""""""

.. index::
    single: terminal windows
    single: shell windows

It is generally possible to configure you terminal emulator to put the currently
running command in the window title, which makes it available to Avendesora's
account discovery.

For this to work you need a terminal emulator that supports xterm's special
characters for setting the window title, which is quite common.  In this case,
sending a string to the window that starts with ``esc-]0;`` and ends with
``ctrl-g`` will set the window title.  How you generate these codes depends on
which shell you use.


Tcsh
''''

Tcsh runs *postcmd* after it has read the command but before it is run. You can
change *postcmd* by creating an alias of the same name. Here is a version that
sets the window title to the currently running command::

    alias postcmd 'echo -n "\033]2;${USER}@${HOST:r:r}: \!#\007"'

``${USER}`` is replaced by the username and ``${HOST:r:r}`` is replaced with the 
hostname with two extensions removed. The ``\!#`` is replaced by the currently 
running command.

Running this alias command causes the window title to be set as a command
starts.  Still needed is to update the window title after the command completes.
This is realized using the *precmd* command. Tcsh calls this command before
generating a prompt.  Here is a version that sets the window title to contain
the hostname and the current working directory::

    alias precmd 'echo -n "^[[]2;${USER}@${HOST:r:r}:${cwd}^G"'

Place both of these aliases in your ~/.cshrc file to configure your shell to
keep your window title up-to-date. They should be placed at the end of the file 
and should only be executed for interactive shells::

    if ($?prompt) then
        alias precmd 'echo -n "^[]2;${USER}@${HOST:r:r}:${cwd}^G"'
        alias postcmd 'echo -n "^[]2;${USER}@${HOST:r:r}: \!#^G"'
    endif

With these aliases in place, you can add the following to the account that
contains your login password:

.. code-block:: python

    discovery = RecognizeTitle(
        '*@*: sudo *',
        script='{passcode}{return}'
    )

With this, you can run a *sudo* command in your shell, and trigger Avendesora
when *sudo* requests your password.  Avendesora will recognize the title and
enter your login password.  By placing the username and the host name in the 
window title along with the command you give Avendesora the ability to tailor 
its response accordingly. For example, you match a specific user and host names 
with the following:

.. code-block:: python

    discovery = RecognizeTitle(
        'elayne@andor: sudo *',
        script='{passcode}{return}'
    )


Bash
''''

The following code added to your ~/.bashrc file will accomplish pretty much the 
same thing if you use Bash as your shell::

    HOST=$(echo "$HOSTNAME" | cut -f 1 -d '.')
    trap 'printf "\033]0;${USER}@${HOST}: %s\007" "${BASH_COMMAND//[^[:print:]]/}"' DEBUG


.. index::
    single: questions
    single: security questions
    single: challenge questions

.. _questions:

Security Questions
------------------

Security questions are form of security theater imposed upon you by
many websites. The claim is that these questions increase the
security of your account. In fact they often do the opposite by
creating additional avenues of access to your account. Their real
purpose is to allow you to regain access to your account in case you
lose your password. If you are careful, this is not needed (you do
back up your *Avendesora* accounts, right?). In this case it is better
to randomly generate your answers.

Security questions are handled by adding something like the
following to your account:

.. code-block:: python

    questions = [
        Question('oldest aunt?'),
        Question('title of first job?'),
        Question('oldest uncle?'),
        Question('savings goal?'),
        Question('childhood vacation spot?'),
    ]

The string identifying the question does not need to contain the
question verbatim, a abbreviated version is sufficient as long as it
allows you to distinguish the question. However, once set, you should not change 
the question in the slightest; doing so changes the generated answer.

The questions are given as an array, and so are accessed with an index that 
starts at 0. Thus, to get the answer to who is your 'oldest aunt', you would 
use::

    > avendesora value <accountname> 0
    questions.0 (oldest aunt): ampere reimburse duster

You can get a list of your questions and then select which one you want answered 
using the :ref:`questions command <questions command>`.  Specifically, if 
Citibank asks for the name of your oldest uncle you can use the following to 
find the answer::

    > avendesora questions citi
    0: oldest aunt?
    1: title of first job?
    2: oldest uncle?
    3: savings goal?
    4: childhood vacation spot?
    Which question? 2
    questions (oldest uncle?): discomfit correct contact

By default, *Avendesora* generates a response that consists of 3
random words. This makes it easy to read to a person over the phone
if asked to confirm your identity.  Occasionally you will not be
able to enter your own answer, but must choose one that is offered
to you. In this case, you can specify the answer as part of the
question:

.. code-block:: python

    questions = [
        Question('favorite fruit?', answer='grapes'),
        Question('first major city visited?', answer='paris'),
        Question('favorite subject?', answer='history'),
    ]

When giving the answers you may want to conceal them to protect them
from casual observation.


.. index::
    single: browse

.. _browse:

Opening Accounts in your Browser
--------------------------------

*Avendesora* provides the :ref:`browse command <browse command>` to allow you to 
easily open the website for your account in your browser. To do so, it needs two 
things: a URL and a browser.

Selecting the URL
"""""""""""""""""

*Avendesora* looks for URLs in the *urls* and *discovery* account attributes, 
with *urls* being preferred if both exist.  *urls* may either be a string, 
a list, or a dictionary. If it is a string, it is split at white spaces to make 
it a list.  If *urls* is a list, the URLs are considered unnamed and the first 
one given is used. If it a dictionary, the URLs are named.  When named, you may 
specify the URL you wish to use by specifying the name to the :ref:`browse 
command <browse command>`.  For example, consider a *urls* attribute that looks 
like this:

.. code-block:: python

    class Dragon(Account):
        username = 'rand'
        passcode = Passphrase()
        urls = dict(
            email = 'https://webmail.dragon.com',
            vpn = 'https://vpn.dragon.com',
        )
        default_url = 'email'

You would access *vpn* with::

    avendesora browse dragon vpn

By specifying *default_url* you indicate which URL is desired when you do not 
explicitly specify which you want on the :ref:`browse command <browse command>`. 
In this way, you can access your email with either of the following::

    avendesora browse dragon email
    avendesora browse dragon

If *urls* is not given, *Avendesora* looks for URLs in 
:class:`avendesora.RecognizeURL` members in the *discovery* attribute.  If the 
*name* argument is provided to :class:`avendesora.RecognizeURL`, it is treated 
as a named URL, otherwise it is treated as an unnamed URL.

If named URLs are found in both *urls* and *discovery* they are all available to 
:ref:`browse command <browse command>`, with those given in *urls* being 
preferred when the same name is found in both attributes.


Selecting the Browser
"""""""""""""""""""""

You can configure browsers for use by *Avendesora* using the *browsers* setting.  
By default, *browsers* contains the following:

.. code-block:: python

    browsers = dict(
        f = 'firefox -new-tab {url}',
        fp = 'firefox -private-window {url}',
        c = 'google-chrome {url}',
        ci = 'google-chrome --incognito {url}',
        q =  'qutebrowser {url}',
        t = 'torbrowser {url}',
        x = 'xdg-open {url}',
    )

Each entry pairs a key with a command. The command will be run with *{url}* 
replaced by the selected URL when the browser is selected. You can choose which 
browser is used by specifying the *--browser* command line option on the
:ref:`browse command <browse command>`, by adding the *browser* attribute to the 
account, or by specifying the *default_browser* setting in the :ref:`config file 
<configuring_avendesora>`.  If more than one is specified, the command line 
option dominates over the account attribute, which dominates over the setting.  
By default, the default browser is *x*, which uses the default browser for your 
account.


.. index::
    single: interactive queries

.. _interactive:

Interactive Queries
-------------------

Occasionally you may need several account values or you may be talking to an 
account services representative on the phone and may want to quickly respond to 
their questions such as 'what is your account number?' or 'what is your verbal 
password?'. In these cases using the :ref:`value command <value command>` is 
cumbersome. *Avendesora* provides two interactive commands that can help out.

The :ref:`questions command <questions command>` allows you to quickly see the 
available security questions and then answer them on demand.  For example::

    > avendesora questions bank
    0: Mothers profession?
    1: Last name of high school best friend?
    2: Name of first pet?
    Which question? 1
    questions.1 (Last name of high school best friend?): dirge revel oboist
    Which question?

You are presented the available questions and asked to choose one. In the
example, 1 is entered and that question is answered by *Avendesora*. You can
then request the answer to another question.  This continues until you give an
empty selection.

As a short cut, you can use *q* as the name of the command rather than
*questions*.

By default the *default_vector_field* is queried, which is generally
*questions*, however you can request any composite field::

    > avendesora q bank accounts
    checking:
    savings:
    credit:
    Which question? checking
    accounts.checking: 7610-40-9891
    Which question?

The :ref:`questions command <questions command>` is useful when confronting one 
or more unexpected challenge questions, but it only handles one composite field 
at a time. More convenient when chatting on the phone to an account 
representative is the *interactive* or *i* command.  This command allows you to 
interactively query the value of any account field::

    > avendesora interactive bank
    which field? accounts.checking
    accounts.checking: 7610-40-9891
    which field?

An empty selection or <Ctrl-d> terminates the command. The command supports
name completion using the <Tab> key. Simply type the first few characters of
the name and type <Tab> to complete the name.  Type <Tab><Tab> to get a list of
available completions::

    > avendesora i bank
    which field? acc<Tab>.c<Tab>
    accounts.checking: 7610-40-9891
    which field?

If the value is a secret, it is displayed for a minute and then erased. To
erase it early, type <Ctrl-c>.


.. index::
    single: OTP
    single: One-time passwords
    single: second factor
    single: 2FA

.. _otp:

One-Time Passwords
------------------

One-time passwords are often used as a second factor to provide an additional 
level of protection. They are especially useful when you are concerned about 
keyloggers.

*Avendesora* supports time-based one-time passwords (TOTP) that are fully 
compatible with, and can act as an alternative to or a replacement for, the 
*Google Authenticator*, *Authy*, or *Symantec VIP* apps.


.. index::
    single: Google Authenticator

Google Authenticator
""""""""""""""""""""

When first enabling one-time passwords with *Google Authenticator* you are 
generally presented with a QR code. Also included is a string of characters that 
are often referred to as the backup code.  You would provide this string of 
characters to the OTP class to configure an account for a one-time password. For 
example, here is an account that requests your username and password on one 
page, and your one time password on another:

.. code-block:: python

    class AndorSavings(Account):
        email = 'lini.eltring@yahoo.com'
        passcode = PasswordRecipe('16 2u 2d 2s')
        otp = OTP('JBSWY3DPEHPK3PXP')
        credentials = 'email passcode otp'
        urls = 'https://www.andorsavings.com/login.html'
        discovery = [
            RecognizeURL(
                'https://www.andorsavings.com/login.html',
                script='{email}{tab}{passcode}{return}',
                name='email & password',
            ),
            RecognizeURL(
                'https://www.andorsavings.com/googleVerify.html',
                script='{otp}{return}',
                name='authentication token',
            ),
        ]

Or, if you are lucky enough that they allow you to enter the OTP on the same 
page as your username and password, you might have:

.. code-block:: python

    class AndorSavings(Account):
        email = 'lini.eltring@yahoo.com'
        passcode = PasswordRecipe('16 2u 2d 2s')
        otp = OTP('JBSWY3DPEHPK3PXP')
        credentials = 'email passcode otp'
        discovery = RecognizeURL(
            'https://www.andorsavings.com/login.html',
            script='{email}{tab}{passcode}{tab}{otp}{return}',
            name='email, passcode and authentication token',
        )

In this case, you only need one recognizer and specifying *urls* is no longer 
necessary because you only have one URL in the account.

This account adds a one time password as *otp*. It adds a *credentials* field 
that adds the one-time password to the output of the :ref:`credentials command 
<credentials command>`. It also adds a URL recognizer to allow semiautomatic 
entry of the one-time password to the browser.

Finally, some sites want you to concatenate the OTP to the end of your password.  
You can do that with:

.. code-block:: python

    script='{email}{tab}{passcode}{otp}{return}',


.. index::
    single: Authy

Authy
"""""

It is easy to mimic *Google Authenticator*. Mimicking *Authy* is more difficult.  
To do so, follow `these instructions 
<https://randomoracle.wordpress.com/2017/02/15/extracting-otp-seeds-from-authy>`_.  
Basically, the idea is to install the *Authy* *Chrome* app, start it, open the 
desired account, then back in *Chrome* open chrome://extensions, select 
*Developer Mode*, then click on  'Inspect views: main.html', search for *totp* 
function, set a break point in that function and wait until it trips, then copy 
the value of the *e* argument (a 32 digit hexadecimal number) to *hex_seed* in 
the code below:

.. code-block:: python

    #!/usr/bin/env python3

    from base64 import b32encode, b32decode
    from pyotp import TOTP
    from time import sleep

    def int_to_bytes(x):
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    hex_seed = 0xNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
    seed = b32encode(int_to_bytes(hex_seed))
    print('SEED: %s' % seed)

    otp = TOTP(seed, interval=10, digits=7)
    print(otp.now())
    sleep(10)
    print(otp.now())
    sleep(10)
    print(otp.now())
    sleep(10)
    print(otp.now())
    sleep(10)
    print(otp.now())

Substitute your number for *NNN...NN* (*hex_seed* should be 0x followed by the 
value of *e*).  Then run the script to display the seed or shared secret.  It 
will also show five codes, one every 10 seconds.  Every other code should match 
the value produced by the *Chrome* app.  Be aware that every *Authy* app has its 
own seed, so the sequence that *Chrome* generates will be different from the 
sequence generated by your phone app or even a different *Chrome* app, and that 
is true even if they are generating tokens for the same account.

Once you are convinced that your seed is correct, add something like the 
following to your account to generate the one-time password:

.. code-block:: python

        otp = OTP('UM0HJVLT4HVWJQJC47Q8YXX4TU======', interval=10, digits=7)

The string passed to *OTP* should be the value of SEED as output by the above 
script.  The *interval* and *digits* are specific to *Authy*.

Be aware that training *Avendesora* to output your *Authy* codes does not 
eliminate your need for the *Authy* application. Occasionally, an authorization 
request will be pushed to your *Authy* application to allow you to approve 
a transaction.  *Avendesora* cannot provide this particular service.  In the 
*Authy* parlance, *Avendesora* supports *Authy Tokens*, but not *Authy 
Requests*.


.. index::
    single: Symantec VIP

Symantec VIP
""""""""""""

You can use `vipaccess <https://github.com/dlenski/python-vipaccess>`_ to 
generate OTP credentials for *Avendesora* that are compatible with the *Symantec 
VIP* authenticator application.  Download and install *vipaccess* using::

    git clone https://github.com/dlenski/python-vipaccess.git
    cd python-vipaccess
    pip3 install --user .

Once installed, you generate the credentials using:

    vipaccess provision

It produces an ID, a secret, and an expiration date and places them into 
~/.vipaccess.
The ID and secret are like a public and private key pair. You keep *secret* 
private and you give the ID to the site when registering your authenticator.  
With *Avendesora* you give the secret as the argument to 
:class:`avendesora.OTP`.

As an example, consider configuring *Avendesora* to provide two-factor 
authentication for a *Schwab* account. Assume that you have run *vipaccess* and 
it generated the following ~/.vipaccess file::

    version 1
    secret AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    id VSST12345678
    expiry 2019-01-15T12:00:00.000Z

You would configure *Avendesora* to generate one-time passwords by adding the 
following to the desired account::

    otp = OTP('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    otp_expires = '2019-01-15T12:00:00.000Z'

The addition of *otp_expires* is not necessary, it just a way of keeping 
a useful piece of information in a convenient place.  It is not necessary to 
save the ID.

You would register your authenticator with *Schwab* by giving them the ID, in 
this case VSST12345678, and the current one-time password, which you get with::

    avendesora schwab otp

Once registered, *Schwab* expects you to add the one-time password to the end of 
your passcode when logging in. You can implement this in account discovery 
using::

    discovery = RecognizeURL(
        'https://client.schwab.com',
        script='{username}{tab}{passcode}{otp}{return}',
    )

You should now be able to login using a single keystroke.

Once you have registered and *Avendesora* is able to authenticate your access to 
Schwab, you can delete the ~/.vipaccess file.

You can add the one-time password to the :ref:`credentials command <credentials 
command>` in two alternate ways.  In the first, you simply list out the one-time 
password along with the username and passcode::

    credentials = 'username otp passcode'

Alternatively, you have *Avendesora* show the one-time password as part of the 
passcode, just as *Schwab* wants it. To accomplish this a new field, 
*ephemeral_passcode*, is created that combines the passcode and the one-time 
password. This field is replaces *passcode* in the *credentials* field::

    ephemeral_passcode = Script('{passcode}{otp}')
    credentials = 'username ephemeral_passcode'

In this example, the *otp*, *otp_expires*, and *ephemeral_passcode* field names 
are arbitrary. You are free to choose names more to your liking.

A variation on this process is used when registering *Avendesora*'s one-time 
password feature as a second-factor with *ETrade*. *Symantec VIP* has several 
types of tokens.  By default, *vipaccess* generates VSST (desktop) tokens, but 
*Etrade* requires a VSMT (mobile) token.  To generate a mobile token, use::

    vipaccess provision -t VSMT

Except for this one detail, the rest of the process is the same as described for 
*Schwab*.


.. index::
    single: scripts
    single: tab (in script)
    single: return (in script)
    single: sleep (in script)
    single: rate (in script)
    single: remind (in script)

.. _scripts:

Scripts
-------

*Scripts* are strings that contain embedded account attributes.  For
example:

.. code-block:: python

    'username: {username}, password: {passcode}'

When processed by *Avendesora* the attributes are replaced by their
value from the chosen account.  For example, this script might
be rendered as::

    username: rand_alThor, password: R7ibHyPjWtG2

You can specify a script directly to the :ref:`value command <value command>`.  
You can specify them as account attributes (in this case then need to be 
embedded in :class:`avendesora.Script`).  Or you can specify them to 
:ref:`account discovery recognizers <discovery>`.

Besides account attributes, there are also some special codes that can be 
inserted in the script surrounded by braces:

============  ============================================================
Code          Meaning
============  ============================================================
tab           insert a tab character
return        insert a carriage return character
sleep *N*     pause for *N* seconds
rate *N*      set the autotype rate to one character per *N* milliseconds.
remind *msg*  show the msg as a notification
============  ============================================================

*tab* and *return* are suitable for all scripts, but *sleep*, *rate* and 
*remind* are only suitable for account discovery scripts.

Scripts are useful if you need to combine an account value with
other text, if you need to combine more than one account value, or
if you want quick access to something that would otherwise need an
additional key.

For example, consider an account for your wireless router, which
might hold several passwords, one for administrative access and one
or more for the network passwords.  Such an account might look like:

.. code-block:: python

    class WiFi(Account):
        username = 'admin'
        passcode = Passphrase()
        networks = ["Occam's Router", "Occam's Router (guest)"]
        network_passwords = [Passphrase(), Passphrase()]
        privileged = Script('''
            SSID: {networks.0}
            password: {network_passwords.0}
        ''')
        guest = Script('''
            SSID: {networks.1}
            password: {network_passwords.1}
        ''')
        credentials = 'privileged guest username passcode'

Notice that *privileged* and *guest* were specified as scripts. Now the 
credentials for the privileged network are accessed with::

    > avendesora value wifi privileged
    SSID: Occam's Router
    password: overdraw cactus devotion saying

You can also give a script rather than a field on the command line
when running the :ref:`value command <value command>`::

    > avendesora value scc '{username}: {passcode}'
    rand_alThor: R7ibHyPjWtG2

For example, a place where this is useful is when specifying a username and 
password to curl::

    > curl --user `avendesora value -s apache '{username}:{passcode}'` ...

It is also possible to specify a script for the value of the *default* 
attribute. This attribute allows you to specify the default field (which 
attribute name and key to use if one is not given on the command line).  It also 
accepts a script rather than a field, but in this case it should be a simple 
string and not an instance of the :class:`avendesora.Script` class.  If you 
passed it as a :class:`avendesora.Script`, it would be expanded before being 
interpreted as a field name, and so would result in a 'not found' error.

.. code-block:: python

    class SCC(Account):
        aliases = 'scc'
        username = 'rand_alThor'
        password = PasswordRecipe('12 2u 2d 2s')
        default = 'username: {username}, password: {password}'

You can access the script by simply not providing a field::

    > avendesora value scc
    username: rand_alThor, password: *m7Aqj=XBAs7

Finally, you pass a script to the account discovery recognizers.  They specify 
the action that should be taken when a particular recognizer triggers. These 
scripts would also be simple strings and not instances of the 
:class:`avendesora.Script` class. For example, this recognizer could be used to 
recognize Gmail:

.. code-block:: python

    discovery = [
        RecognizeURL(
            'https://accounts.google.com/ServiceLogin',
            'https://accounts.google.com/signin/v2/identifier',
            script='{username}{return}{sleep 2}{passcode}{return}'
            name='username and passcode',
        ),
        RecognizeURL(
            'https://accounts.google.com/signin/v2/sl/pwd',
            script='{passcode}{return}',
            name='passcode',
        ),
        RecognizeURL(
            'https://accounts.google.com/signin/challenge',
            script='{questions.0}{return}'
            name='challenge',
        ),
    ]

Besides the account attributes, you can use several other special attributes 
including: *{tab}*, *{return}*, *{sleep <N>}*, *{rate <N>}, and *{remind 
<message>}*.  *{tab}* is replaced by a tab character, *{return}* is replaced by 
a carriage return character, *{sleep <N>}* causes a pause of *N* seconds, *{rate 
<N>} sets the autotype rate to one keystroke every *N* milliseconds, and 
*{remind <message>}* displays message as a notification.  The *sleep* and *rate* 
functions are only active when auto-typing in account discovery.

The *sleep* function is useful with two-page authentication sites as it gives 
the website time to load the second page.

The *rate* function is useful with fields that have javascript helpers. The 
javascript helpers often limit the rate at which you can type characters.  The 
*rate* function allows you to slow down the autotyping to the point where you 
avoid the problems that stem from exceeding the limit.

The *remind* function is used to remind you of next steps. For example, the 
following uses *remind* to instruct you to use your YubiKey to provide the 
second factor that completes the login process:

.. code-block:: python

    RecognizeURL(
        'https://www.kraken.com/en-us/sign-in',
        'https://www.kraken.com/sign-in',
        script='{username}{tab}{passcode}{tab}{remind Use Yubikey as 2nd factor.}',
        name = 'login',
    )


.. index::
    single: files as secrets
    single: writing files

Files as Secrets
----------------

It is possible to place the contents of entire files in *Avendesora*, and then 
when you request an account field that holds the file, that file is written to 
the filesystem.

To see how this would work, consider your SSH private keys.  You would first 
encode each of the keys using the :ref:`conceal command <conceal command>`::

    > avendesora conceal --file ~/ssh/id_rsa
    Hidden(
        'LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnph'
        ...
        'RCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K'
    )
    ...

You would then create an *Avendesora* account for your SSH keys and copy the 
encoded contents in to the arguments of :class:`avendesora.WriteFile` along with 
the path to the file and the desired file mode:

.. code-block:: python

    class SSH_Keys(Account):
        desc = 'ssh private keys'
        aliases = 'sshkeys'
        all = Script('\n    {id_rsa}\n    {github}')
        id_rsa = WriteFile(
            path = '~/.ssh/id_rsa',
            contents = Hidden(
                'LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnph'
                ...
                'RCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K'
            ),
            mode = 0o0600
        )
        github = WriteFile(
            path = '~/.ssh/github',
            contents = Hidden(
                'LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnph'
                ...
                'RXdIK1BWSTFmUUFBQUtpcDZsS1VxZXBTCmxB=='
            ),
            mode = 0o0600
        )

Then, when you run *Avendesora* the contents are decoded and written to the 
specified file::

    > avendesora sshkeys id_rsa
    id-rsa: Contents written to ~/.ssh/id_rsa.

Using :class:`avendesora.Script` allows you to write multiple files at once::

    > avendesora sshkeys all
    all:
        Contents written to ~/.ssh/id_ed25519.
        Contents written to ~/.ssh/id_rsa.


.. index::
    single: stealth accounts

.. _stealth accounts:

Stealth Accounts
----------------

Normally *Avendesora* uses information from an account that is contained in an 
accounts file to generate the secrets for that account. In some cases, the 
presence of the account itself, even though it is contained within an encrypted 
file can be problematic.  The mere presence of an encrypted file may result in 
you being compelled to open it. For the most damaging secrets, it is best if 
there is no evidence that the secret exists at all. This is the purpose of 
stealth accounts. (:ref:`Misdirection` is an alternative to stealth accounts).

The stealth accounts are predefined and have names that are descriptive of the 
form of the secret they generate, for example word4 generates a 4-word pass 
phrase (also referred as the xkcd pattern)::

    > avendesora value word4
    account: my_secret_account
    gulch sleep scone halibut

The predefined accounts are kept in ~/.config/avendesora/stealth_accounts.  You 
are free to add new accounts or modify the existing accounts.

Stealth accounts are subclasses of the :class:`avendesora.StealthAccount` class.  
These accounts differ from normal accounts in that they do not contribute the 
account name to the secrets generators for use as a seed.  Instead, the user is 
requested to provide the account name every time the secret is generated. The 
secret depends strongly on this account name, so it is essential you give 
precisely the same name each time. The term 'account name' is being use here, 
but you can enter any text you like.  Best to make this text very difficult to 
guess if you are concerned about being compelled to disclose your GPG keys.  You 
would not want your spouse simply try 'ashleymadison' after you walk away from 
your computer to gain access to your previously secret account.

The secret generator will combine the account name with the master seed before 
generating the secret. This allows you to use simple predictable account names 
and still get an unpredictable secret.  The master seed used is taken from 
*master_seed* in the file that contains the stealth account if it exists, or the 
*user_key* if it does not. By default the stealth accounts file does not contain 
a master seed, which makes it difficult to share stealth accounts.  You can 
create additional stealth account files that do contain master seeds that you 
can share with your associates.


.. index::
    single: misdirection
    single: duress
    single: compulsion

.. _misdirection:

Misdirection
------------

One way to avoid being compelled to disclose a secret is to disavow
any knowledge of the secret.  However, the presence of an account in
*Avendesora* that pertains to that secret undercuts this argument.
This is the purpose of stealth accounts. They allow you to generate
secrets for accounts for which *Avendesora* has no stored information.
In this case *Avendesora* asks you for the minimal amount of
information that it needs to generate the secret. However in some
cases, the amount of information that must be retained is simply too
much to keep in your head. In that case another approach, referred
to as secret misdirection, can be used.

With secret misdirection, you do not disavow any knowledge of the
secret, instead you say your knowledge is out of date. So you would
say something like "I changed the password and then forgot it", or
"The account is closed". To support this ruse, you must use the
--seed (or -S) option to 'avendesora value' when generating your
secret (secrets misdirection only works with generated passwords,
not stored passwords). This causes *Avendesora* to ask you for an
additional seed at the time you request the secret. If you do not
use --seed or you do and give the wrong seed, you will get a
different value for your secret.  In effect, using --seed when
generating the original value of the secret causes *Avendesora* to
generate the wrong secret by default, allowing you to say "See, I
told you it wouldn't work". But when you want it to work, you just
interactively provide the correct seed.

You would typically only use misdirection for secrets you are
worried about being compelled to disclose. So it behooves you to use
an unpredictable additional seed for these secrets to reduce the
chance someone could guess it.

Be aware that when you employ misdirection on a secret, the value of
the secret stored in the archive will not be the true value, it
will instead be the misdirected value.

Secret misdirection works extremely well with the `ColdCard hardware bitcoin 
wallet <https://coldcardwallet.com>`_.  This wallet expects you to provide a PIN 
when accessing your wallet, but it does not print an error message if you give 
the wrong pin, instead it simply gives you access to a different wallet.  
Putting a small amount of bitcoin into the wallet you access with no seed makes 
the ruse more convincing. In this way, the wallet you get when you run::

    avendesora value coldcard pin

opens a valid and active wallet that contains very little money. At this point 
you can say, "Yeah, its largely all gone. I was hacked. That is why I got this 
secure hardware wallet. However, it's a lesson I learned too late.". Then, when 
you are alone, you can run::

    avendesora value --seed coldcard pin

and give the correct seed to access all your riches.


.. index::
    single: collaboration

.. _collaboration:

Collaborating with a Partner
----------------------------

If you share an accounts file with a partner, then either partner
can create new secrets and the other partner can reproduce their
values once a small amount of relatively non-confidential
information is shared. This works because the security of the
generated secrets is based on the master seed, and that seed is
contained in the accounts file that is shared in a secure manner
once at the beginning.  For example, imagine one partner creates an
account at the US Postal Service website and then informs the
partner that the name of the new account is *USPS* and the username is
*taveren*.  That is enough information for the second partner to
generate the password and login. And notice that the necessary
information can be shared over an insecure channel. For example, it
could be sent in a text message or from a phone where trustworthy
encryption is not available.

The first step in using *Avendesora* to collaborate with a partner is
for one of the partners to generate and then share an accounts file
that is dedicated to the shared accounts.  This file contains the
master seed, and it is critical to keep this value secure. Thus, it
is recommended that the file be shared in person or that it be encrypted in 
transit.

Consider an example where you, Siuan, are sharing accounts with your
business partner, Moiraine.  You have hired a contractor to run your
email server, Elaida, who unbeknownst to you is reading your email in
order to steal valuable secrets.  Together, you and Moiraine jointly run
Aes Sedai Enterprises. Since you expect more people will need access to
the accounts in the future, you choose to the name the file after
the company rather than your partner.  To share accounts with Moiraine,
you start by getting Moiraine's public GPG key.  Then, create the new
accounts file with something like::

    avendesora new -g siuan@aessedai.com,moiraine@aessedai.com aessedai.gpg

This generates a new accounts file, ~/.config/avendesora/aessedai.gpg,
and encrypts it so only you and Moiraine can open it.  Mail this file to
Moiraine. Since it is encrypted, it is to safe to send the file through
email.  Even though Elaida can read this message, the accounts file is
encrypted so she cannot access the master seed it contains.  Moiraine
should put the file in ~/.config/avendesora and then add it to
accounts_files in ~/.config/avendesora/accounts_files.  You are now
ready to share accounts.

Then, when one partner creates a new account they mail the new account entry
to the other partner.  This entry does not contain enough
information to allow an eavesdropper such as Elaida to be able to
generate the secrets, but now both partners can. At a minimum you
would need to share only the account name and the user name if one
is needed. With that, the other partner can generate the passcode.

When creating accounts to share, the fields should either be generated secrets 
or information that is not secret.  Specifically, you should not use 
:class:`avendesora.Hide` or :class:`avendesora.Hidden`.  In addition, you cannot 
share secrets encrypted with :class:`avendesora.Scrypt`. Finally, you cannot 
share stealth accounts unless the file that contains the account templates has 
a *master_seed* specified, which they do not by default. You would need to 
create a separate file for shared stealth account templates and add a master 
seed to that file manually.

Once you have shared an accounts file, you can also use the :ref:`identity
command <identity command>` to prove your identity to your partner (described 
next).


.. index::
    single: challenge response
    single: confirming identity

.. _confirming identity:

Confirming the Identity of a Partner
------------------------------------

The :ref:`identity command <identity command>` allows you to generate a response 
to any challenge.  The response identifies you to a remote partner with whom you 
have shared an account.

If you run the command with no arguments, it prints the list of
valid names. If you run it with no challenge, one is created for you
based on the current time and date.

If you have a remote partner to whom you wish to prove your
identity, have that partner use *Avendesora* to generate a challenge
and a response based on your shared secret. Then the remote partner
provides you with the challenge and you run *Avendesora* with that
challenge to generate the same response, which you provide to your
remote partner to prove your identity.

You are free to explicitly specify a challenge to start the process,
but it is important that it be unpredictable and that you not use
the same challenge twice. As such, it is recommended that you not
provide the challenge. In this situation, one is generated for you
based on the time and date.

Consider an example that illustrates the process. In this example,
Siuan is confirming the identity of Moiraine, where both Siuan and Moiraine
are assumed to have shared *Avendesora* accounts.  Siuan runs
*Avendesora* as follows and remembers the response::

    > avendesora identity moiraine
    challenge: slouch emirate bedeck brooding
    response: spear disable local marigold

This assumes that moiraine is the name, with any extension removed, of the file 
that Siuan uses to contain their shared accounts.

Siuan communicates the challenge to Moiraine but not the response.  Moiraine 
then runs *Avendesora* with the given challenge::

    > avendesora identity siuan slouch emirate bedeck brooding
    challenge: slouch emirate bedeck brooding
    response: spear disable local marigold

In this example, siuan is the name of the file that Moiraine uses to contain 
their shared accounts.

To complete the process, Moiraine returns the response to Siuan, who compares it 
to the response she received to confirm Moiraine's identity.  If Siuan has 
forgotten the desired response, she can also specify the challenge to the 
:ref:`identity command <identity command>` to regenerate the expected response.

Alternately, when Siuan sends a message to Moiraine, she can proactively prove 
her identity by providing both the challenge and the response. Moiraine could 
then run the :ref:`credentials command <credentials command>` with the challenge 
and confirm that she gets the same response. Other than herself, only Siuan 
could predict the correct response to any challenge.  However, this is not 
recommended as it would allow someone with brief access to Suian's Avendesora, 
perhaps Leane her Keeper, to generate and store multiple challenge/response 
pairs. Leane could then send messages to Moiraine while pretending to be Siuan 
using the saved challenge/response pairs.  The subterfuge would not work if 
Moiraine generated the challenge unless Leane currently has access to Siuan's 
Avendesora.


.. index::
    single: phonetic alphabet
    single: alphabet, phonetic

.. _phonetic:

Phonetic Alphabet
-----------------

When on the phone it can be difficult to convey the letters in an account 
identifier or other letter sequences. To help with this *Avendesora* can convert 
the sequence to the NATO phonetic alphabet.  For example, imaging conveying the 
sequence '2WQI1T'. To do so, you can run the following::

    > avendesora phonetic 2WQI1T
    two whiskey quebec india one tango

Alternately, you can run the command without an argument, in which case it 
simply prints out the phonetic alphabet::

    > avendesora p
    Phonetic alphabet:
        Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
        Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
        Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
        Delta     Hotel     Lima      Papa      Tango     X-ray

Now you can easily do the conversion yourself. Having *Avendesora* do the 
conversion for you helps you distinguish similar looking characters such as 
I and 1 and O and 0.


.. index::
    single: abraxas

.. _abraxas:

Upgrading from Abraxas
----------------------

*Avendesora* generalizes and replaces *Abraxas*, its predecessor.  To
transition from *Abraxas* to *Avendesora*, you will first need to
upgrade Abraxas to version 1.8 or higher (use 'abraxas -v' to
determine version). Then run::

    abraxas --export

It will create a collection of *Avendesora* accounts files in
~/.config/abraxas/avendesora. You need to manually add these files
to your list of accounts files in *Avendesora*. Say one such file is
created: ~/.config/abraxas/avendesora/accounts.gpg.  This could be
added to *Avendesora* as follows:

1. create a symbolic link from
   ~/.config/avendesora/abraxas_accounts.gpg to
   ~/.config/abraxas/avendesora/accounts.gpg::

    cd ~/.config/avendesora
    ln -s ../abraxas/avendesora/accounts.gpg abraxas_accounts.gpg

2. add abraxas_accounts.gpg to account_files list in accounts_files.

Now all of the Abraxas accounts contained in abraxas_accounts.gpg
should be available though *Avendesora* and the various features of
the account should operate as expected. However, secrets in accounts
exported by Abraxas are no longer generated secrets. Instead, the
actual secrets are placed in a hidden form in the exported accounts
files.

If you would like to enhance the imported accounts to take advantage
of the new features of *Avendesora*, it is recommended that you do not
manually modify the imported files. Instead, copy the account
information to one of your own account files before modifying it.
To avoid conflict, you must then delete the account from the
imported file. To do so, create ~/.config/abraxas/do-not-export if
it does not exist, then add the account name to this file, and
reexport your accounts from Abraxas.
