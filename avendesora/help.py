# Help
# Output a help topic.
#
# To Do:  Output the obscured text within a class instantiation. So rather than
# just outputting obscured text, output 'Hidden('obscured-text'). Also, accept
# obscured text within its class and try to decode it using the class name, so
# if GPG("ciphertext") then it will use GPG to decode it even if user does not
# provide the encoding.
#
# Also implement script class that uses a personal password. Call this Encrypt
# or PersonalEncrypt.

# License {{{1
# Copyright (C) 2016 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from .command import Command
from .config import get_setting
from .obscure import Obscure
from .utilities import pager, two_columns
from inform import error, output
from textwrap import dedent

# HelpMessage base class {{{1
class HelpMessage(object):
    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.name.lower()
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to
            # dashes.
            return cls.__name__.lower()

    # topics {{{2
    @classmethod
    def topics(cls):
        for sub in cls.__subclasses__():
            yield sub

    # show {{{2
    @classmethod
    def show(cls, name=None):
        if name:
            command = Command.find(name)
            if command:
                return pager(command.help())
            for topic in cls.topics():
               if name == topic.get_name():
                   return pager(topic.help())
            error('topic not found.', culprit=name)
        else:
            cls.help()

    # summarize {{{2
    @classmethod
    def summarize(cls, width=16):
        summaries = []
        for topic in sorted(cls.topics(), key=lambda topic: topic.get_name()):
            summaries.append(two_columns(topic.get_name(), topic.DESCRIPTION))
        return '\n'.join(summaries)

    # help {{{2
    @classmethod
    def help(cls):
        output('Available commands:')
        output(Command.summarize())

        output('\nAvailable topics:')
        output(cls.summarize())


# Abraxas class {{{1
class Abraxas(HelpMessage):
    DESCRIPTION = "exporting accounts from Abraxas"

    @staticmethod
    def help():
        text = dedent("""
            Avendesora generalizes and replaces Abraxas, its predecessor.  To
            transition from Abraxas to Avendesora, you will first need to
            upgrade Abraxas to version 1.8 or higher (use 'abraxas -v' to
            determine version). Then run:

                abraxas --export

            It will create a collection of Avendesora accounts files in
            ~/.config/abraxas/avendesora. You need to manually add these files
            to your list of accounts files in Avendesora. Say one such file in
            created: ~/.config/abraxas/avendesora/accounts.gpg.  This could be
            added to Avendesora as follows:

            1. create a symbolic link from
               ~/.config/avendesora/abraxas_accounts.gpg to
               ~/.config/abraxas/avendesora/accounts.gpg:

                cd ~/.config/avendesora
                ln -s ../abraxas/avendesora/accounts.gpg abraxas_accounts.gpg

            2. add abraxas_accounts.gpg to account_files list in .accounts_files.

            Now all of the Abraxas accounts contained in abraxas_accounts.gpg
            should be available though Avendesora and the various features of
            the account should operate as expected. However, secrets in accounts
            exported by Abraxas are no longer generated secrets. Instead, the
            actual secrets are placed in a hidden form in the exported accounts
            files.

            If you would like to enhance the imported accounts to take advantage
            of the new features of Avendesora, it is recommended that you do not
            manually modify the imported files. Instead, copy the account
            information to one of your own account files before modifying it.
            To avoid conflict, you must then delete the account from the
            imported file. To do so, create ~/.config/abraxas/do-not-export if
            it does not exist, then add the account name to this file, and
            reexport your accounts from Abraxas.
        """).strip()
        return text


# Accounts class {{{1
class Accounts(HelpMessage):
    DESCRIPTION = "describing an account"

    @staticmethod
    def help():
        text = dedent("""
            Account information is stored in account files. The list of account
            files is given in ~/.config/avendesora/.accounts_files.  New account
            files are created using 'avendesora new', but to delete an accounts
            file, you must remove it from .accounts_files. Once an accounts file
            exists, you may add accounts to it using 'account add'. Use the -f
            option to specify which file is to contain the new account.

            An account is basically a collection of attributes organized as a
            subclass of the Python Account class. For example:

                class NewYorkTimes(Account):
                    aliases = 'nyt'
                    username = 'derrickAsh'
                    email = 'derrickAsh@gmail.com'
                    passcode = PasswordRecipe('12 2u 2d 2s')
                    discovery = RecognizeURL(
                        'https://myaccount.nytimes.com',
                        script='{email}{tab}{passcode}{return}'
                    )

            Most of the field values can be retrieved simply by asking for them.
            For example,

                > avendesora value newyorktimes username
                username: derrickAsh

            In general, values can be strings, arrays, dictionaries, and special
            Advendesora classes. For example, you could have an array of
            security questions:

                questions = [
                    Question("What is your mother's maiden name?"),
                    Question("What city were you born?"),
                    Question("What is first pet's name?"),
                ]

            Then you can request the answer to a particular question using its
            index:

                > avendesora value newyorktimes questions.0
                questions.0 (What is your mother's maiden name?): portrayal tentacle fanlight

            'questions' is the default array field, so you could have shortened
            your request by using '0' rather than 'questions.0'.  You might be
            thinking, hey, that is not my mother's maiden name. That is because
            Question is a 'generated secret'.  It produces a completely arbitrary
            answer that is impossible to predict. Thus, even family members
            cannot know the answers to your security questions.

            A dictionary is often used to hold account numbers:

                accounts = [
                    'checking': '1234-56-7890',
                    'savings': '0123-45-6789',
                ]

            You then access its values using:

                > avendesora value newyorktimes accounts.checking 
                accounts.checking: 1234-56-7890

            You might consider your account numbers as sensitive information. In
            this case you can hide them with:

                accounts = [
                    'checking': Hidden('MTIzNC01Ni03ODkw'),
                    'savings': Hidden('MDEyMy00NS02Nzg5'),
                ]

            The values are now hidden, but not encrypted. They are simply
            encoded with base64. Any knowledgable person with the encoded value
            can decode it back to its original value. Using Hidden makes it
            harder to recognize and remember the value given only a quick
            over-the-shoulder glance. It also marks the value as sensitive, so
            it will only be displayed for a minute. You generate the encoded
            value using 'avendesora conceal'.

            You can find the specifics of how to specify or generate your
            secrets by running 'avendesora help secrets'.

            Any value that is an instance of the Secret class (Password,
            Passphrase, ...) or the Obscure class (Hidden, GPG, ...) are
            considered sensitive. They are given out only in a controlled
            manner. For example, running 'avendesora values' displays all
            fields, but the values that are sensitive are replaced by
            instructions on how to view them. They can only be viewed
            individually:

                > avendesora values newyorktimes
                names: newyorktimes, nyt
                email: derrickAsh@gmail.com
                passcode: <reveal with 'avendesora value newyorktimes passcode'>
                username: derrickAsh

            The 'aliases' and 'discovery' fields are not shown because they are
            considered tool fields. Other tool fields include 'NAME', 'default',
            'master', 'browser', and 'default_url'. For more information on
            discovery, run 'avendesora help discovery'.  'default' is the name
            of the default field, which is the field you get if you do not
            request a particular field. Its value defaults to 'passcode' but it
            can be set to any account attribute name or it can be a script (see
            'avendesora help scripts').  'browser' is the default browser to use
            when opening the account, run 'avendesora help browse' to see a list
            of available browsers.

            The value of passcode is considered sensitive because it is an
            instance of PasswordRecipe, which is a subclass of Secret.  If we
            wish to see the passcode, use:

                > avendesora value nyt
                passcode: TZuk8:u7qY8%

            This value will be displayed for a minute and then hidden. If you
            would like to hide it early, simply type Ctrl-C.

            An attribute value can incorporate other attribute values through
            use of the Script class. For example, consider an account for your
            wireless router that contains the following:

                ssid = {
                    'huron_guests': Passphrase(),
                    'huron_drugs': Passphrase(),
                }
                guest = Script('SSID: huron_guests, password: {ssid.huron_guests}')
                privileged = Script('SSID: huron_drugs, password: {ssid.huron_drugs}')

            The ssid field is a dictionary that contains the SSID and pass
            phrases for each of the wireless networks provided by the router.
            This is a natural an compact representation for this information,
            but accessing it as a user in this form would require two steps to
            access the information, one to get the SSID and another to get the
            passphrase. This issue is addressed by adding the guest and
            privileged attributes. The guest and privileged attributes are a
            script that gives the SSID and interpolate the pass phrase. Now both
            can easily accessed at once with:

                > avendesora value wifi guest
                SSID: huron_guests, password: delimit ballcock fibber levitate

            Use of Avendesora classes (Secret, Obscure, or Script) is confined
            to the top two levels of account attributes, meaning that they can
            be the value of the top-level attributes, or the top-level
            attributes may be arrays or dictionaries that contain objects of
            these classes, but it can go no further.
        """).strip()
        return text


# Collaborate class {{{1
class Collaborate(HelpMessage):
    DESCRIPTION = "collaborate"

    @staticmethod
    def help():
        text = dedent("""
            If you share an accounts file with a partner, then either partner
            can create new secrets and the other partner can reproduce their
            values once a small amount of relatively non-confidential
            information is shared. This works because the security of the
            generated secrets is based on the master seed, and that seed is
            contained in the accounts file that is shared in a secure manner
            once at the beginning.  For example, imagine one partner creates an
            account at the US Postal Service website and then informs the
            partner that the name of the new account is usps and the username is
            justus.  That is enough information for the second partner to
            generate the password and login. And notice that the necessary
            information can be shared over an insecure channel. For example, it
            could be sent in a text message or from a phone where trustworthy
            encryption is not available.

            The first step in using Avendesora to collaborate with a partner is
            for one of the partners to generate and then share an accounts file
            that is dedicated to the shared accounts.  This file contains the
            master seed, and it is critical to keep this value secure. Thus, it
            is recommended that the shared file be encrypted.

            Consider an example where you, Alice, are sharing accounts with your
            business partner, Bob.  You have hired a contractor to run your
            email server, Eve, who unbeknownst to you is reading your email in
            order to steal valuable secrets.  Together, you and Bob jointly run
            Teneya Enterprises. Since you expect more people will need access to
            the accounts in the future, you choose to the name the file after
            the company rather than your partner.  To share accounts with Bob,
            you start by getting Bob's public GPG key.  Then, create the new
            accounts file with something like:

                avendesora new -g alice@teneya.com -g bob@teneya.com teneya.gpg

            This generates a new accounts file, ~/.config/avendesora/teneya.gpg,
            and encrypts it so only you and Bob can open it.  Mail this file to
            Bob. Since it is encrypted, it is to safe to send the file through
            email.  Even though Eve can read this message, the accounts file is
            encrypted so Eve cannot access the master seed it contains.  Bob
            should put the file in ~/.config/avendesora and then add it to
            accounts_files in ~/.config/avendesora/accounts_files.  You are now
            ready to share accounts.

            Then, one partner creates a new account and mails the account entry
            to the other partner.  This entry does not contain enough
            information to allow an eavesdropper such as Eve to be able to
            generate the secrets, but now both partners can.

            Once you have shared an accounts file, you can also use the identity
            command to prove your identity to your partner.
        """).strip()
        return text


# Discovery class {{{1
class Discovery(HelpMessage):
    DESCRIPTION = "account discovery"

    @staticmethod
    def help():
        text = dedent("""
            If you do not give an account to 'avendesora value', Avendesora will
            try to determine the account by simply asking each account. An
            account can look at the window title, the user name, the host name,
            the working directory, and the environment variables to determine if
            it is suitable. If so, it nominates itself. If there is only one
            account nominated, that account is used. If there are multiple
            nominees, then a small window pops up allowing you to choose
            which account you wish to use.

            To configure an account to trigger when a particular window title is
            seen, use:

                discovery = RecognizeTitle(
                    'Chase Online *',
                    script='{username}{tab}{passcode}{return}'
                )

            The title is a glob string, meaning that '*' matches any combination
            of characters. The script describes what Avendesora should output
            when their is a match. In this case it outputs the username field,
            then a tab, then the passcode field, then a return (see 'avendesora
            help scripts').

            Matching window titles can be fragile, especially for websites
            because the titles can vary quite a bit across the site and over
            time. To accommodate this variation, you can give multiple glob
            patterns:

                discovery = RecognizeTitle(
                    'CHASE Bank*',
                    'Chase Online*',
                    script='{username}{tab}{passcode}{return}'
                )

            If you use Firefox, you can install the 'Add URL to Window Title'
            extension. Doing so adds the website URL to the Firefox window
            title, which can make account discovery more robust. In this case
            you can use:

                discovery = RecognizeURL(
                    'https://chaseonline.chase.com',
                    'https://www.chase.com',
                    script='{username}{tab}{passcode}{return}'
                )

            When giving the URL, anything specified must match and globbing is
            not supported. If you give a partial path, by default Avendesora
            will match up to what you have given, but you can require an exact
            match of the entire path by specifying exact_path=True to
            RecognizeURL.  If you do not give the protocol, https is assumed.

            The following recognizers are available:

                RecognizeAll(<recognizer>..., [script=<script>])
                RecognizeAny(<recognizer>..., [script=<script>])
                RecognizeTitle(<title>..., [script=<script>])
                RecognizeURL(<title>..., [script=<script>, [name=<name>]], [exact_path=<bool>])
                RecognizeHost(<host>..., [script=<script>])
                RecognizeUser(<user>..., [script=<script>])
                RecognizeCWD(<cwd>..., [script=<script>])
                RecognizeEnvVar(<name>, <value>, [script=<script>])
                RecognizeNetwork(<mac>..., [script=<script>])

            RecognizeAll() and RecognizeAny() can be used to combine several
            recognizers. For example:

                discovery = RecognizeAll(
                    RecognizeTitle('sudo *'),
                    RecognizeUser('hhyde'),
                    script='{passcode}{return}'
                )

            To make secret discovery easier and more robust it is helpful to add
            a plugin to your web browser to make its title more informative. For
            Firefox, the best plugin to use is AddURLToWindowTitle. For Chrome
            it is URLinTitle. It is recommended that you install the appropriate
            one into your browser.  For AddURLToWindowTitle, set the following
            options:

                show full URL = yes
                separator string = '-'
                show field attributes = no

            For URLinTitle, set:

                tab title format = '{title} - {protocol}://{hostname}{port}/{path}'

            When account discovery fails it can be difficult to determine what
            is going wrong. When this occurs, you should first examine the log
            file. It should show you the window title and the recognized title
            components. You should first assure the title is as expected. If Add
            URL to Window Title generated the title, then the various title
            components should also be shown.  Then run Avendesora as follows:

                avendesora value --verbose --title '<title>'

            The title should be copied from the log file. The verbose option
            causes the result of each test to be included in the log file, so
            you can determine which recognizer is failing to trigger.

            If the recognizers are given in an array, all are tried. For
            example:

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

            In this case, both recognizers recognize the same URL, thus they
            will both be offered for this site.  But each has a different
            script. The name allows the user to distinguish the available
            choices.
        """).strip()
        return text


# Entropy class {{{1
class Entropy(HelpMessage):
    DESCRIPTION = "how much entropy is enough?"

    @staticmethod
    def help():
        text = dedent("""
            A 4 word Avendesora password provides 53 bits of entropy, which
            seems like a lot, but NIST is recommending 80 bits for your most
            secure passwords.  So, how much is actually required. It is worth
            exploring this question.  Entropy is a measure of how hard the
            password is to guess. Specifically, it is the base two logarithm of
            the likelihood of guessing the password in a single guess. Every
            increase by one in the entropy represents a doubling in the
            difficulty of guessing your password. The actual entropy is hard to
            pin down, so generally we talk about the minimum entropy, which is
            the likelihood of an adversary guessing the password if he or she
            knows everything about the scheme used to generate the password but
            does not know the password itself.  So in this case the minimum
            entropy is the likelihood of guessing the password if it is known
            that we are using 4 space separated words as our pass phrase.  This
            is very easy to compute.  There are roughly 10,000 words in our
            dictionary, so if there was only one word in our pass phrase, the
            chance of guessing it would be one in 10,000 or 13 bits of entropy.
            If we used a two word pass phrase the chance of guessing it in a
            single guess is one in 10,000*10,000 or one in 100,000,000 or 26
            bits of entropy.

            The probability of guessing our pass phrase in one guess is not our
            primary concern. Really what we need to worry about is given a
            determined attack, how long would it take to guess the password. To
            calculate that, we need to know how fast our adversary could try
            guesses. If they are trying guesses by typing them in by hand, their
            rate is so low, say one every 10 seconds, that even a one word pass
            phrase may be enough to deter them.  Alternatively, they may have a
            script that automatically tries pass phrases through a login
            interface.  Again, generally the rate is relatively slow.  Perhaps
            at most the can get is 1000 tries per second. In this case they
            would be able to guess a one word pass phrase in 10 seconds and a
            two word pass phrase in a day, but a 4 word pass phrase would
            require 300,000 years to guess in this way.

            The next important thing to think about is how your password is
            stored by the machine or service you are logging into. The worst
            case situation is if they save the passwords in plain text. In this
            case if someone were able to break in to the machine or service,
            they could steal the passwords. Saving passwords in plain text is an
            extremely poor practice that was surprisingly common, but is
            becoming less common as companies start to realize their liability
            when their password files get stolen.  Instead, they are moving to
            saving passwords as hashes.  A hash is a transformation that is very
            difficult to reverse, meaning that if you have the password it is
            easy to compute its hash, but given the hash it is extremely
            difficult to compute the original password. Thus, they save the
            hashes (the transformed passwords) rather than the passwords. When
            you log in and provide your password, it is transformed with the
            hash and the result is compared against the saved hash. If they are
            the same, you are allowed in. In that way, your password is no
            longer available to thieves that break in.  However, they can still
            steal the file of hashed passwords, which is not as good as getting
            the plain text passwords, but it is still valuable because it allows
            thieves to greatly increase the rate that they can try passwords. If
            a poor hash was used to hash the passwords, then passwords can be
            tried at a very high rate.  For example, it was recently reported
            that password crackers were able to try 8 billion passwords per
            second when passwords were hashed with the MD5 algorithm. This would
            allow a 4 word pass phrase to be broken in 14 days, whereas a 6 word
            password would still require 4,000,000 years to break.  The rate for
            the more computational intensive sha512 hash was only 2,000
            passwords per second. In this case, a 4 word pass phrase would
            require 160,000 years to break.

            In most cases you have no control over how your passwords are stored
            on the machines or services that you log into.  Your best defense
            against the notoriously poor security practices of most sites is to
            always use a unique password for sites where you are not in control
            of the secrets.  For example, you might consider using the same pass
            phrase for you login password and the pass phrase for an ssh key on
            a machine that you administer, but never use the same password for
            two different websites unless you do not care if the content of
            those sites become public.

            So, if we return to the question of how much entropy is enough, you
            can say that for important passwords where you are in control of the
            password database and it is extremely unlikely to get stolen, then
            four randomly chosen words from a reasonably large dictionary is
            plenty.  If what the pass phrase is trying to protect is very
            valuable and you do not control the password database (ex., your
            brokerage account) you might want to follow the NIST recommendation
            and use 6 words to get 80 bits of entropy. If you are typing
            passwords on your work machine, many of which employ keyloggers to
            record your every keystroke, then no amount of entropy will protect
            you from anyone that has or gains access to the output of the
            keylogger.  In this case, you should consider things like one-time
            passwords or two-factor authentication. Or better yet, only access
            sensitive accounts from your home machine and not from any machine
            that you do not control.
        """).strip()
        return text


# Misdirection class {{{1
class Misdirection(HelpMessage):
    DESCRIPTION = "misdirection in secrets generation"

    @staticmethod
    def help():
        text = dedent("""
            One way to avoid being compelled to disclose a secret is to disavow
            any knowledge of the secret.  However, the presence of an account in
            Avendesora that pertains to that secret undercuts this argument.
            This is the purpose of stealth accounts. They allow you to generate
            secrets for accounts for which Avendesora has no stored information.
            In this case Avendesora asks you for the minimal amount of
            information that it needs to generate the secret. However in some
            cases, the amount of information that must be retained is simply too
            much to keep in your head. In that case another approach, referred
            to as secret misdirection, can be used.

            With secret misdirection, you do not disavow any knowledge of the
            secret, instead you say your knowledge is out of date. So you would
            say something like "I changed the password and then forgot it", or
            "The account is closed". To support this ruse, you must use the
            --seed (or -S) option to 'avendsora value' when generating your
            secret (secrets misdirection only works with generated passwords,
            not stored passwords). This causes Avendesora to ask you for an
            additional seed at the time you request the secret. If you do not
            use --seed or you do and give the wrong seed, you will get a
            different value for your secret.  In effect, using --seed when
            generating the original value of the secret causes Avendesora to
            generate the wrong secret by default, allowing you to say "See, I
            told you it would not work". But when you want it to work, you just
            interactively provide the correct seed.

            You would typically only use misdirection for secrets you are
            worried about being compelled to disclose. So it behooves you to use
            an unpredictable additional seed for these secrets to reduce the
            chance someone could guess it.

            Be aware that when you employ misdirection on a secret, the value of
            the secret stored in in the archive will not be the true value, it
            will instead be the misdirected value.
        """).strip()
        return text


# Overview class {{{1
class Overview(HelpMessage):
    DESCRIPTION = "overview of Avendesora"

    @staticmethod
    def help():
        text = dedent("""
            Avendesora is password utility that can store your account
            information and generate account passwords and produce them from the
            command line.  It can also be configured to autotype your username
            and password into the current window so that you can log in with a
            simple keystroke.

            Avendesora is capable of generating passwords (character-based
            passcodes) or pass phrases (word-based passcodes).  Pass phrases are
            generally preferred if you have a choice, but many websites will not
            take them.  The benefit of pass phrases is that they are relatively
            easy to remember and type, and they are very secure.  The pass
            phrases generated by Avendesora generally consist of four words,
            each word is drawn from a dictionary of 10,000 words.  Thus, even if
            a bad guy knew that four lower case words were being used for your
            pass phrase, there are still 10,000,000,000,000,000 possible
            combinations for him to try (this represents a minimum entropy of 53
            bits).  Using six words results in 80 bits of entropy, which meets
            the threshold recommended by NIST for the most secure pass phrases.
            For more on this, see 'avendesora help entropy' below.

            For another perspective on the attractiveness of pass phrases, see
            http://xkcd.com/936/.

            Unlike password vaults, Avendesora produces a highly unpredictable
            password from a master seed and the name of the account for which
            the password is to be used. The process is completely repeatable. If
            you give the same master seed and account name, you will get the
            same password. As such, the passwords do not have to be saved;
            instead they are regenerated on the fly.

            As a password generator, Avendesora provides three important
            advantages over conventional password vaults.  First, it allows
            groups of people to share access to accounts without having to
            securely share each password.  Instead, one member of the group
            creates a master seed that is securely shared with the group once.
            From then on any member of the group can create a new account, share
            the name of the account, and all members will know the password
            needed to access the account. The second advantage is that it opens
            up the possibility of using high-quality passwords for stealth
            accounts, which are accounts where you remember the name of the
            account but do not store any information about even the existence of
            the account on your computer.  With Avendesora, you only need to
            remember the name of the account and it will regenerate the password
            for you. This is perfect for your TrueCrypt hidden volume password.
            Finally, by securely storing a small amount of information, perhaps
            on a piece of paper in your safe-deposit box, you can often recover
            most if not all of your passwords even if you somehow lose your
            accounts file. You can even recover passwords that were created
            after you created your backup. This is because Avendesora combines
            the master seed with some easily reconstructed information, such as
            the account name, to create the password. If you save the master
            seed, the rest should be recoverable.

            To use Avendesora, one creates one or more accounts files. At a
            minimum, there is should be one for your private accounts, and one
            each for all the people with whom you hold shared accounts.  These
            files contain information about each of your non-stealth accounts.
            Avendesora then provides access to that information.  The
            information will include both secrets and non-secrets. The secrets
            can be given explicitly, or information could be provided to specify
            how to generate the secret.
        """).strip()
        return text


# Questions class {{{1
class Questions(HelpMessage):
    DESCRIPTION = "security questions"

    @staticmethod
    def help():
        text = dedent("""
            Security questions are form of security theater imposed upon you by
            many websites. The claim is that these questions increase the
            security of your account. In fact they often do the opposite by
            creating additional avenues of access to your account. Their real
            purpose is to allow you to regain access to your account in case you
            lose your password. If you are careful, this is not needed (you do
            back up your Avendesora accounts, right?). In this case it is better
            to randomly generate your answers.

            Security questions are handled by adding something like the
            following to your account:

                questions = [
                    Question('oldest aunt'),
                    Question('title of first job'),
                    Question('oldest uncle'),
                    Question('savings goal'),
                    Question('childhood vacation spot'),
                ]

            The string identifying the question does not need to contain the
            question verbatim, a abbreviated version is sufficient as long as it
            allows you to distinguish the question.  The questions are given as
            an array, and so are accessed with an index that starts at 0. Thus,
            to get the answer to who is your 'oldest aunt', you would use:

                > avendesora value <accountname> 0
                questions.0 (oldest aunt): ampere reimburse duster

            You can get a list of your questions so you can identify which index
            to use with:

                > avenedesora values <accountname>
                ...
                questions:
                    0: oldest aunt <reveal with 'avendesora value <accountname> questions.0'>
                    1: title of first job <reveal with 'avendesora value <accountname> questions.1'>
                    2: oldest uncle <reveal with 'avendesora value <accountname> questions.2'>
                    3: savings goal <reveal with 'avendesora value <accountname> questions.3'>
                    4: childhood vacation spot <reveal with 'avendesora value <accountname> questions.4'>
                ...

            By default, Avendesora generates a response that consists of 3
            random words. This makes it easy to read to a person over the phone
            if asked to confirm your identity.  Occasionally you will not be
            able to enter your own answer, but must choose one that is offered
            to you. In this case, you can specify the answer as part of the
            question:

                questions = [
                    Question('favorite fruit', answer='grapes'),
                    Question('first major city visited', answer='paris'),
                    Question('favorite subject', answer='history'),
                ]

            When giving the answers you may want to conceal them to protect them
            from casual observation.

            Be aware that the question is used as a seed when generating the
            answer, so if you change the question in any way it changes the
            answer.
        """).strip()
        return text


# Scripts class {{{1
class Scripts(HelpMessage):
    DESCRIPTION = "scripts"

    @staticmethod
    def help():
        text = dedent("""
            Scripts are strings that contain embedded account attributes.  For
            example:

                'username: {username}, password: {passcode}'

            When processed by Advendesora the attributes are replaced by their
            value from the chosen account.  For example, this script might
            be rendered as:

                username: jman, password: R7ibHyPjWtG2

            Scripts are useful if you need to combine an account value with
            other text, if you need to combine more than one account value, or
            if you want quick access to something that would otherwise need an
            additional key.

            For example, consider an account for your wireless router, which
            might hold several passwords, one for administrative access and one
            or more for the network passwords.  Such an account might look like:

                class WiFi(Account):
                    username = 'admin'
                    passcode = Passphrase()
                    networks = ["Occam's Router", "Occam's Router (guest)"]
                    network_passwords = [Passphrase(), Passphrase()]
                    privileged = Script('SSID: {networks.0}, password: {network_passwords.0}')
                    guest = Script('SSID: {networks.1}, password: {network_passwords.1}')

            Now the credentials for the privileged network are accessed with:

                > avendesora value wifi privileged
                SSID: Occam's Router, password: overdraw cactus devotion saying

            Most account attributes that expect a string can also accept a
            script given in this manner.

            You can also give a script rather than a field on the command line
            when running the value command:

                > avendesora value scc '{username}: {passcode}'
                jman: R7ibHyPjWtG2

            It is also possible to specify a script for the value of the
            *default* attribute. This attribute allows you to specify the
            default field (which attribute name and key to use if one is not
            given on the command line).  It also accepts a script rather than a
            field, but in this case it should be a simple string and not an
            instance of the Script class.  If you passed it as a Script, it
            would be expanded before being interpreted as a field name, and so
            would result in a 'not found' error.

                class SCC(Acount):
                    aliases = 'scc'
                    username = 'jman'
                    password = PasswordRecipe('12 2u 2d 2s')
                    default = 'username: {username}, password: {password}'

            You can access the script by simply not providing a field.

                > avendesora value scc
                username: jman, password: *m7Aqj=XBAs7

            Finally, you pass a script to the account discovery recognizers.
            They specify the action that should be taken when a particular
            recognizer triggers. These scripts would also be simple strings and
            not instances of the Script class. For example, this recognizer
            could be used to recognize Gmail:

                discovery = [
                    RecognizeURL(
                        'https://accounts.google.com/ServiceLogin',
                        script='{username}{return}{sleep 1.5}{passcode}{return}'
                    ),
                    RecognizeURL(
                        'https://accounts.google.com/signin/challenge',
                        script='{questions.0}{return}'
                    ),
                ]

            Besides the account attributes, you can use several other special
            attributes including: {tab}, {return}, and {sleep N}.  {tab} is
            replaced by a tab character, {return} is replaced by a carriage
            return character, and {sleep N} causes a pause of N seconds. The
            sleep function is only active when autotyping after account
            discovery.
        """).strip()
        return text


# Secrets class {{{1
class Secrets(HelpMessage):
    DESCRIPTION = "secrets"

    @staticmethod
    def help():
        text = dedent("""
        Secrets can either by obscured or generated.

        Obscured Secrets
        ================

        Obscured secrets are secrets that are those that are given to Avendesora
        to securely hold. The may be things like account numbers or existing
        passwords.  There are several ways for Avendesora to hold a secret,
        presented in order of increasing security.

        Hide
        ----

        This marks a value as being confidential, meaning that it will be
        protected when shown to the user, but value is not encoded or encrypted
        in any way.  Rather, it accounts on the protections afforded the
        accounts file to protect its secret.

            Hide(plaintext, secure=True)

            plaintext (str):
                The secret in plain text.
            secure (bool):
                Indicates that this secret should only be contained in an
                encrypted accounts file. Default is True.

        Example:

            account = Hide('5206-7844')


        Hidden
        -------

        This obscures but does not encrypt the text. It can protect the secret from 
        observers that get a quick glance of the encoded text, but if they are able to 
        capture it they can easily decode it.

            Hidden(encodetext, secure=True, encoding=None)

            plaintext (str):
                The secret encoded in base64.
            secure (bool):
                Indicates that this secret should only be contained in an
                encrypted accounts file. Default is True.
            encoding (str):
                The encoding to use for the deciphered text.

        Example:

            account = Hidden("NTIwNi03ODQ0")

        To generate the encoded text, use:

            > avendesora conceal


        GPG
        ---

        The secret is fully encrypted with GPG. Both symmetric encryption and
        key-based encryption are supported.  This can be used to protect a
        secret held in an unencrypted account file, in which case encrypting
        with your key is generally preferred. It can also be used to further
        protect a extremely valuable secret, in which case symmetric encryption
        is generally used.

            GPG(ciphertext, encoding=None)

            ciphertext (str):
                The secret encrypted and armored by GPG.
            encoding (str):
                The encoding to use for the deciphered text.

        Example:

            secret = GPG('''
                -----BEGIN PGP MESSAGE-----
                Version: GnuPG v2.0.22 (GNU/Linux)

                jA0ECQMCwG/vVambFjfX0kkBMfXYyKvAuCbT3IrEuEKD//yuEMCikciteWjrFlYD
                ntosdZ4WcPrFrV2VzcIIcEtU7+t1Ay+bWotPX9pgBQcdnSBQwr34PuZi
                =4on3
                -----END PGP MESSAGE-----
            ''')

        To generate the cipher text, use:

            > avendesora conceal -e gpg

        The benefit of using symmetric GPG encryption on a secret that is
        contained in an encrypted account file is that the passphrase will
        generally not be found in the GPG agent, in which case someone could not
        walk up to your computer while your screen is unlocked and successfully
        request the secret.  However, the GPG agent does retain the password for
        a while after you decrypt the secret. If you are concerned about that,
        you should follow your use of Avendesora with the following command,
        which clears the GPG agent:

            > killall gpg-agent


        Scrypt
        ------

        The secret is fully encrypted with Scrypt. You personal Avendesora
        encryption key is used (contained in ~/.config/avendesora/.key.gpg). As
        such, these secrets cannot be shared. This encryption method is only
        available if you have installed scrypt on your system (pip3 install
        --user scrypt). Since the Scrypt class only exists if you have installed
        scrypt, it is not imported into your accounts file. You would need to
        import it yourself before using it.

            Script(ciphertext, encoding=None)

            ciphertext (str):
                The secret encrypted by scrypt.
            encoding (str):
                The encoding to use for the deciphered text.

        Example:
            from avendesora import Scrypt
            ...
            secret = Scrypt("""
                "c2NyeXB0ABAAAAAIAAAAASfBZvtYnHvgdts2jrz5RfbYlFYj/EQgiM1IYTnX"
                "KHhMkleZceDg0yUaOWa9PzmZueppNIzVdawAOd9eSVgGeZAIh4ulPHPBGAzX"
                "GyLKc/vo8Fe24JnLr/RQBlTjM9+r6vbhi6HFUHD11M6Ume8/0UGDkZ0="
            """)

        To generate the cipher text, use:

            > avendesora conceal -e scrypt


        Generated Secrets
        =================

        Generated secrets are secrets for which the actual value is arbitrary,
        but it must be quite unpredictable. Generated secrets are generally used
        for passwords and pass phrases, but it can also be used for things like
        personal information requested by institutions that they have no need to
        know. For example, a website might request your birth date to assure
        that you are an adult, but then also use it as a piece of identifying
        information if you ever call and request support.  In this case they do
        not need your actual birth date, they just need you to give the same
        date every time you call in.


        Password
        --------

        Generates an arbitrary password by selecting symbols from the given
        alphabet at random. The entropy of the generated password is
        length*log2(len(alphabet)).

            Password(
                length=12, alphabet=DISTINGUISHABLE, master=None, version=None,
                sep='', prefix='', suffix=''
            )

            length (int):
                The number of items to draw from the alphabet when creating the
                password.  When using the default alphabet, this will be the
                number of characters in the password.
            alphabet (str):
                The reservoir of legal symbols to use when creating the
                password. By default the set of easily distinguished
                alphanumeric characters are used. Typically you would use the
                pre-imported character sets to construct the alphabet. For
                example, you might pass:
                    ALPHANUMERIC + '+=_&%#@'
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                password.
            sep (str):
                A string that is placed between each symbol in the generated
                password.
            prefix (str):
                A string added to the front of the generated password.
            suffix (str):
                A string added to the end of the generated password.

        Examples:

            passcode = Password(10)


        Passphrase
        ----------

        Similar to Password in that it generates an arbitrary pass phrase by
        selecting symbols from the given alphabet at random, but in this case
        the default alphabet is a dictionary containing about 10,000 words.

            Passphrase(
                length=4, alphabet=None, master=None, version=None, sep=' ', prefix='', 
                suffix=''
            )

            length (int):
                The number of items to draw from the alphabet when creating the
                password.  When using the default alphabet, this will be the
                number of words in the passphrase.
            alphabet (str):
                The reservoir of legal symbols to use when creating the
                password. By default, this is a predefined list of 10,000 words.
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                pass phrase.
            sep (str):
                A string that is placed between each symbol in the generated
                password.
            prefix (str):
                A string added to the front of the generated password.
            suffix (str):
                A string added to the end of the generated password.

        Examples:

            passcode = Passphrase()


        PIN
        ---

        Similar to Password in that it generates an arbitrary PIN by selecting
        symbols from the given alphabet at random, but in this case the default
        alphabet is the set of digits (0-9).

            PIN(length=4, alphabet=DIGITS, master=None, version=None)

            length (int):
                The number of items to draw from the alphabet when creating the
                password.  When using the default alphabet, this will be the
                number of digits in the PIN.
            alphabet (str):
                The reservoir of legal symbols to use when creating the
                password. By default the digits (0-9) are used.
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                PIN.

        Examples:

            passcode = PIN()


        Question
        --------

        Generates an arbitrary answer to a given question. Used for website
        security questions. When asked one of these security questions it can be
        better to use an arbitrary answer. Doing so protects you against people
        who know your past well and might be able to answer the questions.

        Similar to Passphrase() except a question must be specified when created
        and it is taken to be the security question. The question is used rather
        than the field name when generating the secret.

            Question(
                question, length=3, alphabet=None, master=None, version=None,
                sep=' ', prefix='', suffix='', answer=None
            )

            question (str):
                The question to be answered. Be careful. Changing the question
                in any way will change the resulting answer.
            length (int):
                The number of items to draw from the alphabet when creating the
                password. When using the default alphabet, this will be the
                number of words in the answer.
            alphabet (list of strs):
                The reservoir of legal symbols to use when creating the
                password. By default, this is a predefined list of 10,000 words.
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                answer.
            sep (str):
                A string that is placed between each symbol in the generated
                password.
            prefix (str):
                A string added to the front of the generated password.
            suffix (str):
                A string added to the end of the generated password.
            answer:
                The answer. If provided, this would override the generated
                answer.  May be a string, or it may be an Obscured object.

        Examples:

            questions = [
                Question('Favorite foreign city'),
                Question('Favorite breed of dog'),
            ]


        PasswordRecipe
        --------------

        Generates passwords that can conform to the restrictive requirements
        imposed by websites. Allows you to specify the length of your password,
        and how many characters should be of each type of character using a
        recipe. The recipe takes the form of a string that gives the total
        number of characters that should be generated, and then the number of
        characters that should be taken from particular character sets. The
        available character sets are:

        l - lower case letters (a-z)
        u - upper case letters (A-Z)
        d - digits (0-9)
        s - punctuation symbols
        c - explicitly given set of characters

        For example, '12 2u 2d 2s' is a recipe that would generate a
        12-character password where two characters would be chosen from the
        upper case letters, two would be digits, two would be punctuation
        symbols, and the rest would be alphanumeric characters. It might
        generate something like: *m7Aqj=XBAs7

        Using '12 2u 2d 2c!@#$%^&*' is similar, except the punctuation symbols
        are constrained to be taken from the given set that includes !@#$%^&*.
        It might generate something like: YO8K^68J9oC!

            PasswordRecipe(
                recipe, def_alphabet=ALPHANUMERIC, master=None, version=None,
            )

            recipe (str):
                A string that describes how the password should be constructed.
            def_alphabet (list of strs):
                The alphabet to use when filling up the password after all the
                constraints are satisfied.
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                answer.

        Examples:

            passcode = PasswordRecipe('12 2u 2d 2c!@#$%^&*')


        BirthDate
        ---------

        Generates an arbitrary birthdate for someone in a specified age range.


            BrithDate(
                year, min_age=18, max_age=65, fmt='YYYY-MM-DD',
                master=None, version=None,
            )

            year (int):
                The year the age range was established.
            min_age (int):
                The lower bound of the age range.
            max_age (int):
                The upper bound of the age range.
            fmt (str):
                Specifies the way the date is formatted. Consider an example
                date of 6 July 1969. YY and YYYY are replaced by the year (69 or
                1969). M, MM, MMM, and MMMM are replaced by the month (7, 07,
                Jul, or July). D and DD are replaced by the day (6 or 06).
            master (str):
                Overrides the master seed that is used when generating the
                password.  Generally, there is one master seed shared by all
                accounts contained in an account file.  This argument overrides
                that behavior and instead explicitly specifies the master seed
                for this secret.
            version (str):
                An optional seed. Changing this value will change the generated
                answer.

        Examples:

            birthdate = BirthDate(2015, 21, 55))
        """).strip()
        return text


# Stealth class {{{1
class Stealth(HelpMessage):
    DESCRIPTION = "stealth secrets"

    @staticmethod
    def help():
        text = dedent("""
            Normally Avendesora uses information from an account that is
            contained in an account file to generate the secrets for that
            account. In some cases, the presence of the account itself, even
            though it is contained within an encrypted file can be problematic.
            The mere presence of an encrypted file may result in you being
            compelled to open it. For the most damaging secrets, it is best if
            there is no evidence that the secret exists at all. This is the
            purpose of stealth accounts. (Misdirection is an alternative to
            stealth accounts; see 'avendesora help misdirection').

            Generally one uses the predefined stealth accounts, which all have
            names that are descriptive of the form of the secret they generate,
            for example Word6 generates a 6-word pass phrase. The predefined
            accounts are kept in ~/.config/avendesora/stealth_accounts.

            Stealth accounts are subclasses of the StealthAccount class. These
            accounts differ from normal accounts in that they do not contribute
            the account name to the secrets generators for use as a seed.
            Instead, the user is requested to provide the account name every
            time the secret is generated. The secret depends strongly
            on this account name, so it is essential you give precisely the same
            name each time. The term 'account name' is being use here, but you
            can enter any text you like.  Best to make this text very difficult
            to guess if you are concerned about being compelled to disclose your
            GPG keys.

            The secret generator will combine the account name with the master
            seed before generating the secret. This allows you to use simple
            predictable account names and still get an unpredictable secret.
            The master seed used is taken from master_seed in the file
            that contains the stealth account if it exists, or the user_key if
            it does not. By default the stealth accounts file does not contain a
            master seed, which makes it difficult to share stealth accounts.
            You can create additional stealth account files that do contain
            master seeds that you can share with your associates.
        """).strip()
        return text


