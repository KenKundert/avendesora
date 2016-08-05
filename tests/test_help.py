import pytest
from inform import os_error
from textwrap import dedent
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

# test_add() {{{1
def test_add():
    try:
        result = subprocess.check_output('avendesora help add'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Add a new account.

        Usage:
            avendesora [options] add [<template>]

        Options:
            -f <file>, --file <file>
                                    Add account to specified file.

        The default template is bank. The available templates are:
        bank, command and website
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_browse() {{{1
def test_browse():
    try:
        result = subprocess.check_output('avendesora help browse'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Open account URL in web browser.

        Usage:
            avendesora [options] browse <account> [<key>]

        Options:
            -b <browser>, --browser <browser>
                                    Open account in specified browser.

        The default browser is x. The available browsers are:
            f  firefox
            g  google-chrome
            t  torbrowser
            x  xdg-open
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_conceal() {{{1
def test_conceal():
    try:
        result = subprocess.check_output('avendesora help conceal'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Conceal text by encoding it.

        Usage:
            avendesora [options] hide <text>
            avendesora [options] conceal <text>

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when concealing information.

        Possible encodings include:
            base64

        base64 (default):
            This encoding obscures but does not encrypt the text. It can
            protect text from observers that get a quick glance of the
            encoded text, but if they are able to capture it they can easily
            decode it.
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_edit() {{{1
def test_edit():
    try:
        result = subprocess.check_output('avendesora help edit'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Edit an account.

        Usage:
            avendesora edit <account>
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_find() {{{1
def test_find():
    try:
        result = subprocess.check_output('avendesora help find'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Find an account.

        Find accounts whose name contains the search text.

        Usage:
            avendesora find <text>
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_help() {{{1
def test_help():
    try:
        result = subprocess.check_output('avendesora help help'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Give information about commands or other topics.

        Usage:
            avendesora help [<topic>]
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_init() {{{1
def test_init():
    try:
        result = subprocess.check_output('avendesora help init'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Create initial set of Avendesora files.

        Usage:
            avendesora init [--gpg-id <id>]... [options]
            avendesora initialize [--gpg-id <id>]... [options]

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
            -h <path>, --gpg-home <path>
                                    GPG home directory (default is ~/.gnupg).

        Initial configuration and accounts files are created only if they
        do not already exist.  Existing files are not modified.
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_new() {{{1
def test_new():
    try:
        result = subprocess.check_output('avendesora help new'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Create new accounts file.

        Usage:
            avendesora new [--gpg-id <id>]... <name>

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.

        Creates a new accounts file. Accounts that share the same file share
        the same master password by default and, if the file is encrypted,
        can be decrypted by the same recipients.

        Generally you would create a new accounts file for each person or
        group with which you wish to share accounts. You would use separate
        files for passwords with different security domains. For example, a
        high-value passwords might be placed in an encrypted file that would
        only be placed highly on protected computers. Conversely, low-value
        passwords might be contained in perhaps an unencrypted file that is
        found on many computers.

        Add a '.gpg' extension to <name> to encrypt the file.
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_reveal() {{{1
def test_reveal():
    try:
        result = subprocess.check_output('avendesora help reveal'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Reveal concealed text.

        Transform concealed text to reveal its original form.

        Usage:
            avendesora [options] unhide <text>
            avendesora [options] reveal <text>

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when revealing information.

        Possible encodings include:
            base64

        base64 (default):
            This encoding obscures but does not encrypt the text. It can
            protect text from observers that get a quick glance of the
            encoded text, but if they are able to capture it they can easily
            decode it.
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_search() {{{1
def test_search():
    try:
        result = subprocess.check_output('avendesora help search'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Search accounts.

        Search for accounts whose values contain the search text.

        Usage:
            avendesora search <text>
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_show() {{{1
def test_show():
    try:
        result = subprocess.check_output('avendesora help show'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Show an account value.

        Produce an account value. If the value is secret, it is produced only
        temporarily unless --stdout is specified.

        Usage:
            avendesora show [--stdout | --clipboard] [<account> [<field>]]
            avendesora s [--stdout | --clipboard] [<account> [<field>]]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -s, --stdout            Write output to the standard output without
                                    any annotation or protections.
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_summary() {{{1
def test_summary():
    try:
        result = subprocess.check_output('avendesora help summary'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Display all account values.

        Show all account values.

        Usage:
            avendesora sum <account>
            avendesora summary <account>
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_version() {{{1
def test_version():
    try:
        result = subprocess.check_output('avendesora help version'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Display Avendesora version.

        Usage:
            avendesora version
    """).strip()
    assert result == bytes(expected, encoding='ascii')

# test_overview() {{{1
def test_overview():
    try:
        result = subprocess.check_output('avendesora help overview'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        combinations for him to try (this represents a mini‐ mum entropy of
        53 bits).  Using six words results in 80 bits of entropy, which
        meets the threshold recommended by NIST for the most secure pass
        phrases. For more on this, see 'How Much Entropy is Enough' below.

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
    assert result == bytes(expected, encoding='utf8')
