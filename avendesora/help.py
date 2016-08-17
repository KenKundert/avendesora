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
class HelpMessage:
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
    DESCRIPTION = "Exporting accounts from Abraxas"

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


# Discovery class {{{1
class Discovery(HelpMessage):
    DESCRIPTION = "Account discovery"

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
            seen, use::

                discovery = RecognizeTitle(
                    'Chase Online *',
                    script='{username}{tab}{passcode}{return}'
                )

            The title is a glob string, meaning that '*' matches any combination
            of characters. The script describes what Avendesora should output
            when their is a match. In this case it outputs the username field,
            then a tab, then the passcode field, then a return.

            Matching window titles can be fragile, especially for websites
            because the titles can vary quite a bit across the site and over
            time. To accommodate this variation, you can give multiple glob
            patterns::

                discovery = RecognizeTitle(
                    'CHASE Bank*',
                    'Chase Online*',
                    script='{username}{tab}{passcode}{return}'
                )

            If you use Firefox, you can install the 'Add URL to Window Title'
            extension. Doing so adds the website URL to the Firefox window
            title, which can make account discovery more robust. In this case
            you can use::

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

            The following recognizers are available::

                RecognizeAll(<recognizer>..., [script=<script>])
                RecognizeAny(<recognizer>..., [script=<script>])
                RecognizeTitle(<title>..., [script=<script>])
                RecognizeURL(<title>..., [script=<script>, [name=<name>]], [exact_path=<bool>])
                RecognizeHost(<host>..., [script=<script>])
                RecognizeUser(<user>..., [script=<script>])
                RecognizeCWD(<cwd>..., [script=<script>])
                RecognizeEnvVar(<name>, <value>, [script=<script>])

            RecognizeAll() and RecognizeAny() can be used to combine several
            recognizers. For example::

                discovery = RecognizeAll(
                    RecognizeTitle('sudo *'),
                    RecognizeUser('hhyde'),
                    script='{passcode}{return}'
                )

            When account discovery fails it can be difficult to determine what
            is going wrong. When this occurs, you should first examine the log
            file. It should show you the window title and the recognized title
            components. You should first assure the title is as expected. If Add
            URL to Window Title generated the title, then the various title
            components should also be shown.  Then run Avendesora as follows::

                avendesora value --verbose --title '<title>'

            The title should be copied from the log file. The verbose option
            causes the result of each test to be included in the log file, so
            you can determine which recognizer is failing to trigger.

            If the recognizers are given in an array, all are tried. For
            example::

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
    DESCRIPTION = "How much entropy is enough?"

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
            combinations for him to try (this represents a minimum entropy of
            53 bits).  Using six words results in 80 bits of entropy, which
            meets the threshold recommended by NIST for the most secure pass
            phrases. For more on this, see 'avendesora help entropy' below.

            For another perspective on the attractiveness of pass phrases, see
            http://xkcd.com/936/.

            Unlike password vaults, Avendesora produces a highly unpredictable
            password from a master password and the name of the account for
            which the password is to be used. The process is completely
            repeatable. If you give the same master password and account name,
            you will get the same password. As such, the passwords do not have
            to be saved; instead they are regenerated on the fly.

            As a password generator, Avendesora provides three important
            advantages over conventional password vaults.  First, it allows
            groups of people to share access to accounts without having to
            securely share each password.  Instead, one member of the group
            creates a master password that is securely shared with the group
            once.  From then on any member of the group can create a new
            account, share the name of the account, and all members will know
            the password needed to access the account. The second advantage is
            that it opens up the possibility of using high-quality passwords for
            stealth accounts, which are accounts where you remember the name of
            the account but do not store any information about even the
            existence of the account on your computer.  With Avendesora, you
            only need to remember the name of the account and it will regenerate
            the password for you. This is perfect for your TrueCrypt hidden
            volume password.  Finally, by securely storing a small amount of
            infor‐ mation, perhaps on a piece of paper in your safe-deposit box,
            you can often recover most if not all of your passwords even if you
            somehow lose your accounts file. You can even recover passwords that
            were created after you created your backup. This is because
            Avendesora combines the master password with some easily recon‐
            structed information, such as the account name, to create the
            password. If you save the master password, the rest should be
            recoverable.

            To use it, one creates a file that contains information about each
            of his or her non-stealth accounts.  Among that information would be
            information that controls how the passwords are generated. This file
            is generally not encrypted, though you can encrypt it if you like).
            Another file is created that contains one or more master passwords.
            This file is always GPG encrypted.

            The intent is for these files to not include the passwords for your
            accounts.  Rather, the passwords are regenerated when needed from
            the account information and from the master password. This makes it
            easy to share passwords with others without having to pass the
            passwords back and forth.  It is only necessary to create a shared
            master password in advance. Then new passwords can be created on the
            fly by either party.
        """).strip()
        return text


