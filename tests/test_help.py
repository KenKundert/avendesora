# vim: filetype=python sw=4 sts=4 et ai ff=unix fileencoding=utf8 :
import pytest
from inform import os_error
from textwrap import dedent
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.
os.environ['HOME'] = 'home'

# change the current working directory to the test directory
cwd = os.getcwd()
if not cwd.endswith('/tests'):
    os.chdir('tests')

# Run avendesora
# Cannot determine whether coverage analysis is needed, so simply always do it
# Whoops, not so fast. The python coverage analysis is broken when it comes to
# the exit status, it always returns 1. So instead, never do it.
def run(args):
    #return subprocess.check_output(['coverage', 'run', '-m'] + args.split())
    return subprocess.check_output(args.split())

# test_add() {{{1
def test_add():
    try:
        result = run('avendesora help add')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Add a new account.

        Usage:
            avendesora add [options] [<template>]

        Options:
            -f <file>, --file <file>
                                    Add account to specified accounts file.

        Creates a new account starting from a template. The template consists of
        boilerplate code and fields. The fields take the from _NAME_. They
        should be replaced by appropriate values or deleted if not needed. If
        you are using the Vim editor, it is preconfigured to jump to the next
        field when you press 'n'.  If the field is surrounded by '<<' and '>>',
        as in '<<_ACCOUNT_NUMBER_>>', the value you enter will be concealed.

        You can create your own templates by adding them to 'account_templates'
        in the ~/.config/avendesora/config file.

        You can change the editor used when adding account by changing the
        'edit_template', also found in the ~/.config/avendesora/config file.

        The default template is bank. The available templates are:
            bank
            shell
            website

        The available accounts files are (the default is given first):
            accounts
            stealth_accounts
    """).strip()
    assert result.decode('utf-8') == expected

# test_archive() {{{1
def test_archive():
    try:
        result = run('avendesora help archive')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Generates archive of all account information.

        Usage:
            avendesora archive

        This command creates an encrypted archive that contains all the
        information in your accounts files, including the fully generated
        secrets.  You should never need this file, but its presence protects
        you in case you lose access to Avendesora. To access your secrets
        without Avendesora, simply decrypt the archive file with GPG.  The
        actual secrets will be hidden, but it easy to retrieve them even
        without Avendesora. When hidden, the secrets are encoded in base64.
        You can decode it by running 'base64 -d -' and pasting the encoded
        secret into the terminal.

        When you run this command it overwrites the existing archive. If you
        have accidentally deleted an account or changed a secret, then
        replacing the archive could cause the last copy of the original
        information to be lost. To prevent this from occurring it is a good
        practice to run the 'changed' command before regenerating the
        archive.  It describes all of the changes that have occurred since
        the last time the archive was generated. You should only regenerate
        the archive once you have convinced yourself all of the changes are
        as expected.
    """).strip()
    assert result.decode('utf-8') == expected

# test_browse() {{{1
def test_browse():
    try:
        result = run('avendesora help browse')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Open account URL in web browser.

        Usage:
            avendesora browse [options] <account> [<key>]

        Options:
            -b <browser>, --browser <browser>
                                    Open account in specified browser.
            -l, --list              List available URLs rather than open first.

        The account is examined for URLs, a URL is chosen, and then that URL
        is opened in the chosen browser.  First URLs are gathered from the
        'urls' account attribute, which can be a string containing one or
        more URLs, a list, or a dictionary.  If 'urls' is a dictionary, the
        desired URL can be chosen by entering the key as an argument to the
        browse command. If a key is not given, then the 'default_url'
        account attribute is used to specify the key to use by default. If
        'urls' is not a dictionary, then the first URL specified is used.
        URLs are also taken from RecognizeURL objects in the 'discovery'
        account attribute.  If the 'name' argument is specified, the
        corresponding URL can be chosen using a key.

        The default browser is x. You can override the default
        browser on a per-account basis by adding an attribute named
        'browser' to the account.  An example of when you would specify the
        browser in an account would be an account associated with Tor hidden
        service, which generally can only be accessed using torbrowser:

            class SilkRoad(Account):
                passcode = Passphrase()
                username = Passphrase(length=2, sep='-')
                url = 'http://silkroad6ownowfk.onion'
                browser = 't'

        The available browsers are:
            c      google-chrome {url}
            ci     google-chrome --incognito {url}
            f      firefox -new-tab {url}
            fp     firefox -private-window {url}
            q      qutebrowser {url}
            t      torbrowser {url}
            x      xdg-open {url}

    """).strip()
    assert result.decode('utf-8') == expected

# test_changed() {{{1
def test_changed():
    try:
        result = run('avendesora help changed')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Show changes since archive was created.

        Usage:
            avendesora changed

        When you run the 'archive' command it overwrites the existing
        archive. If you have accidentally deleted an account or changed a
        secret, then replacing the archive could cause the last copy of the
        original information to be lost. To prevent this from occurring it
        is a good practice to run the 'changed' command before regenerating
        the archive.  It describes all of the changes that have occurred
        since the last time the archive was generated. You should only
        regenerate the archive once you have convinced yourself all of the
        changes are as expected.
    """).strip()
    assert result.decode('utf-8') == expected

# test_collaborate() {{{1
def test_collaborate():
    try:
        result = run('avendesora help collaborate')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        generate the secrets, but now both partners can. At a minimum you
        would need to share only the account name and the user name if one
        is needed. With that, the other partner can generate the passcode.

        Once you have shared an accounts file, you can also use the identity
        command to prove your identity to your partner.

        You cannot share secrets encrypted with Scrypt. Also, you cannot
        share stealth accounts unless the file that contains the account
        templates has a master_seed specified, which they do not by
        default. You would need to create a separate file for shared stealth
        account templates and add a master seed to that file manually.
    """).strip()
    assert result.decode('utf-8') == expected

# test_conceal() {{{1
def test_conceal():
    try:
        result = run('avendesora help conceal')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Conceal text by encoding it.

        Usage:
            avendesora conceal [options] [<text>]

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when concealing information.
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
                                    Use commas with no spaces to separate multiple IDs.
            -h <path>, --gpg-home <path>
                                    GPG home directory (default is ~/.gnupg).
            -s, --symmetric         Encrypt with a passphrase rather than using your
                                    GPG key (only appropriate for gpg encodings).

        Possible encodings include (default encoding is base64):

        gpg:
            This encoding fully encrypts/decrypts the text with GPG key.
            By default your GPG key is used, but you can specify symmetric
            encryption, in which case a passphrase is used.

        base64:
            This encoding obscures but does not encrypt the text. It can
            protect text from observers that get a quick glance of the
            encoded text, but if they are able to capture it they can easily
            decode it.

        scrypt:
            This encoding fully encrypts the text with your user key. Only
            you can decrypt it, secrets encoded with scrypt cannot be shared.

        Though available as an option for convenience, you should not pass
        the text to be hidden as an argument as it is possible for others to
        examine the commands you run and their argument list. For any
        sensitive secret, you should simply run 'avendesora conceal' and
        then enter the secret text when prompted.
    """).strip()
    assert result.decode('utf-8') == expected

# test_credentials() {{{1
def test_credentials():
    try:
        result = run('avendesora help credentials')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Show login credentials.

        Displays the account's login credentials, which generally consist of an
        identifier and a secret.

        Usage:
            avendesora credentials [options] <account>

        Options:
            -S, --seed              Interactively request additional seed for
                                    generated secrets.

        The credentials can be specified explicitly using the credentials
        setting in your account. For example::

            credentials = 'usernames.0 usernames.1 passcode'

        If credentials is not specified then the first of the following will
        be used if available:

            id: username or email
            secret: passcode, password or passphrase

        If your credentials include more than one secret they will be
        presented one at a time for one minute each. You can cut the minute
        short by typing Ctrl-C.
    """).strip()
    assert result.decode('utf-8') == expected

# test_edit() {{{1
def test_edit():
    try:
        result = run('avendesora help edit')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Edit an account.

        Usage:
            avendesora edit <account>

        Opens an existing account in your editor.

        You can specify the editor by changing the 'edit_account' setting in
        the config file (~/.config/avendesora/config).
    """).strip()
    assert result.decode('utf-8') == expected

# test_find() {{{1
def test_find():
    try:
        result = run('avendesora help find')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Find an account.

        Find accounts whose name contains the search text.

        Usage:
            avendesora find <text>
    """).strip()
    assert result.decode('utf-8') == expected

# test_help() {{{1
def test_help():
    try:
        result = run('avendesora help help')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Give information about commands or other topics.

        Usage:
            avendesora help [options] [<topic>]

        Options:
            -s, --search            list topics that include <topic> as a search term.
            -b, --browse            open the topic in your default browser.
    """).strip()
    assert result.decode('utf-8') == expected

# test_identity() {{{1
def test_identity():
    try:
        result = run('avendesora help identity')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Generate an identifying response to a challenge.

        Usage:
            avendesora identity [<name> [<challenge>...]]

        This command allows you to generate a response to any challenge.
        The response identifies you to a partner with whom you have shared
        an account.

        If you run the command with no arguments, it prints the list of
        valid names. If you run it with no challenge, one is created for you
        based on the current time and date.

        If you have a remote partner to whom you wish to prove your
        identity, have that partner use avendesora to generate a challenge
        and a response based on your shared secret. Then the remote partner
        provides you with the challenge and you run avendesora with that
        challenge to generate the same response, which you provide to your
        remote partner to prove your identity.

        You are free to explicitly specify a challenge to start the process,
        but it is important that it be unpredictable and that you not use
        the same challenge twice. As such, it is recommended that you not
        provide the challenge. In this situation, one is generated for you
        based on the time and date.

        Consider an example that illustrates the process. In this example,
        Siuan is confirming the identity of Moiraine, where both Siuan and
        Moiraine are assumed to have shared *Avendesora* accounts.  Siuan
        runs *Avendesora* as follows and remembers the response::

            > avendesora identity moiraine
            challenge: slouch emirate bedeck brooding
            response: spear disable local marigold

        This assumes that moiraine is the name, with any extension removed,
        of the file that Siuan uses to contain their shared accounts.

        Siuan communicates the challenge to Moiraine but not the response.
        Moiraine then runs *Avendesora* with the given challenge::

            > avendesora identity siuan slouch emirate bedeck brooding
            challenge: slouch emirate bedeck brooding
            response: spear disable local marigold

        In this example, siuan is the name of the file that Moiraine uses to
        contain their shared accounts.

        To complete the process, Moiraine returns the response to Siuan, who
        compares it to the response she received to confirm Moiraine's
        identity.  If Siuan has forgotten the desired response, she can also
        specify the challenge to the :ref:`identity command <identity
        command>` to regenerate the expected response.

        Alternately, when Siuan sends a message to Moiraine, she can
        proactively prove her identity by providing both the challenge and
        the response. Moiraine could then run the *identity* command with
        the challenge and confirm that she gets the same response. Other
        than herself, only Siuan could predict the correct response to any
        challenge.  However, this is not recommended as it would allow
        someone with brief access to Suian's Avendesora, perhaps Leane her
        Keeper, to generate and store multiple challenge/response pairs.
        Leane could then send messages to Moiraine while pretending to be
        Siuan using the saved challenge/response pairs.  The subterfuge
        would not work if Moiraine generated the challenge unless Leane
        currently has access to Siuan's Avendesora.
    """).strip()
    assert result.decode('utf-8') == expected

# test_initialize() {{{1
def test_initialize():
    try:
        result = run('avendesora help initialize')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Create initial set of Avendesora files.

        Usage:
            avendesora initialize [options]

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
                                    Use commas with no spaces to separate multiple IDs.
            -h <path>, --gpg-home <path>
                                    GPG home directory (default is ~/.gnupg).

        Create Avendesora data directory (~/.config/avendesora) and populate
        it with initial versions of all essential files.

        It is safe to run this command even after the data directory and
        files have been created. Doing so will simply recreate any missing
        files.  Existing files are not modified.
    """).strip()
    assert result.decode('utf-8') == expected

# test_interactive() {{{1
def test_interactive():
    try:
        result = run('avendesora help interactive')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Interactively query account values.

        Usage:
            avendesora interactive [options] <account>

        Options:
            -S, --seed              Interactively request additional seed for
                                    generated secrets.

        Interactively display values of account fields.  Type the first few
        characters of the field name, then <Tab> to expand the name.
        <Tab><Tab> shows all remaining choices. <Enter> selects and shows
        the value. Use '*' to display all names and values. Type <Ctrl-c> to
        cancel the display of a secret. Type <Ctrl-d> or enter empty field
        name to terminate command.
    """).strip()
    assert result.decode('utf-8') == expected

# test_log() {{{1
def test_log():
    try:
        result = run('avendesora help log')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Open the logfile.

        Usage:
            avendesora [options] log

        Options:
            -d, --delete   Delete the logfile rather than opening it.

        Opens the logfile in your editor.

        You can specify the editor by changing the 'edit_account' setting in
        the config file (~/.config/avendesora/config).
    """).strip()
    assert result.decode('utf-8') == expected

# test_new() {{{1
def test_new():
    try:
        result = run('avendesora help new')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Create new accounts file.

        Usage:
            avendesora new [options] <name>

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
                                    Use commas with no spaces to separate multiple IDs.

        Creates a new accounts file. Accounts that share the same file share
        the same master seed by default and, if the file is encrypted,
        can be decrypted by the same recipients.

        Generally you create new accounts files for each person or group
        with which you wish to share accounts. You also use separate files
        for passwords with different security domains. For example, a
        high-value passwords might be placed in an encrypted file that would
        only be placed highly on protected computers. Conversely, low-value
        passwords might be contained in perhaps an unencrypted file that is
        found on many computers.

        Add a '.gpg' extension to <name> to encrypt the file.
    """).strip()
    assert result.decode('utf-8') == expected

# test_phonetic() {{{1
def test_phonetic():
    try:
        result = run('avendesora help phonetic')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Display NATO phonetic alphabet.

        Usage:
            avendesora phonetic [<text>]

        If <text> is given, it is converted character by character to the
        phonetic alphabet. If not given, the entire phonetic alphabet is
        displayed.
    """).strip()
    assert result.decode('utf-8') == expected

# test_questions() {{{1
def test_questions():
    try:
        result = run('avendesora help questions')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Answer a security question.

        Displays the security questions and then allows you to select one
        to be answered.

        Usage:
            avendesora questions [options] <account> [<field>]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -S, --seed              Interactively request additional seed for
                                    generated secrets.

        Request the answer to a security question by giving the account name to
        this command.  For example:

            avendesora questions bank

        It will print out the security questions for *bank* account along with
        an index. Specify the index of the question you want answered. You can
        answer any number of questions. Type <Ctrl-d> or give an empty
        selection to terminate.

        By default *Avendesora* looks for the security questions in the
        *questions* field.  If your questions are in a different field, just
        specify the name of the field on the command line:

            avendesora questions bank verbal
    """).strip()
    assert result.decode('utf-8') == expected

# test_reveal() {{{1
def test_reveal():
    try:
        result = run('avendesora help reveal')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Reveal concealed text.

        Transform concealed text to reveal its original form.

        Usage:
            avendesora reveal [<text>]

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when revealing information.

        Though available as an option for convenience, you should not pass
        the text to be revealed as an argument as it is possible for others
        to examine the commands you run and their argument list. For any
        sensitive secret, you should simply run 'avendesora reveal' and then
        enter the encoded text when prompted.
    """).strip()
    assert result.decode('utf-8') == expected

# test_search() {{{1
def test_search():
    try:
        result = run('avendesora help search')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Search accounts.

        Search for accounts whose values contain the search text.

        Usage:
            avendesora search <text>
    """).strip()
    assert result.decode('utf-8') == expected

# test_value() {{{1
def test_value():
    try:
        result = run('avendesora help value')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Show an account value.

        Produce an account value. If the value is secret, it is produced only
        temporarily unless --stdout is specified.

        Usage:
            avendesora value [options] [<account> [<field>]]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -s, --stdout            Write output to the standard output without
                                    any annotation or protections.
            -S, --seed              Interactively request additional seed for
                                    generated secrets.
            -v, --verbose           Add additional information to log file to
                                    help identify issues in account discovery.
            -T <title>, --title <title>
                                    Use account discovery on this title.

        You request a scalar value by specifying its name after the account.
        For example:

            avendesora value bank pin

        If the requested value is composite (an array or dictionary), you should
        also specify a key that indicates which of the composite values you
        want. For example, if the 'accounts' field is a dictionary, you specify
        accounts.checking or accounts[checking] to get information on your
        checking account. If the value is an array, you give the index of the
        desired value. For example, questions.0 or questions[0]. If you only
        specify a number, then the name is assumed to be 'questions', as in the
        list of security questions (this can be changed by specifying the
        desired name as the 'default_vector_field' in the account or the config
        file).

        The field may be also be a script, with is nothing but a string that it
        output as given except that embedded attributes are replaced by account
        field values. For example:

            avendesora value bank '{accounts.checking}: {passcode}'

        If no value is requested the result produced is determined by the value
        of the 'default' attribute (this can be changed by specifying
        'default_field' in the config file). If no value is given for 'default',
        then the *passcode*, *password*, or *passphrase* attribute is produced
        (this can be changed by specifying the 'default_field' in the account or
        the config file).  If 'default' is a script (see 'avendesora help
        scripts') then the script is executed. A typical script might be
        'username: {username}, password: {passcode}'. It is best if the script
        produces a one line output if it contains secrets. If not a script, the
        value of 'default' should be the name of another attribute, and the
        value of that attribute is shown.

        Normally the value command attempts to protects secrets. It does so
        clearing the screen after a minute. If multiple secrets are requested,
        you must either wait a minute to see each subsequent secret or type
        Ctrl-C to clear the current secret and move on.  If you use --clipboard,
        the clipboard is cleared after a minute.  However, if you use --stdout
        this clearing of the secret does not occur. The --stdout option is
        generally used with communicating with other Linux commands.  For
        example, you can send a passcode to the standard input of a command as
        follows:

            avendesora value --stdout gpg | gpg --passphrase-fd 0 ...

        You can place the username and password on a command line as follows:

            curl --user `avendesora value -s apache '{username}:{passcode}'` ...

        Be aware that it is possible for other users on shared Linux machines to
        see the command line arguments of your commands, so passing secrets as
        command arguments should only be used for low value secrets.

        If no account is requested, then Avendesora attempts to determine the
        appropriate account through discovery (see 'avendesora help discovery').
        Normally Avendesora is called in this manner from your window manager.
        You would arrange for it to be run when you type a hot key. In this case
        Avendesora determines which account to use from information available
        from the environment, information like the title on active window. In
        this mode, Avendesora mimics the keyboard when producing its output.

        The verbose and title options are used when debugging account
        discovery. The verbose option adds more information about the
        discovery process to the logfile (~/.config/avendesora/log.gpg). The
        title option allows you to override the active window title so you can
        debug title-based discovery. Specifying the title option also scrubs
        the output and outputs directly to the standard output rather than
        mimicking the keyboard so as to avoid exposing your secret.

        If the --stdout option is not specified, the value command still writes
        to the standard output if it is associated with a TTY (if Avendesora is
        outputting directly to a terminal). If standard output is not a TTY,
        Avendesora mimics the keyboard and types the desired value directly into
        the active window.  There are two common situations where standard
        output is not a TTY: when Avendesora is being run by your window manager
        in response to you pressing a hot key or when the output of Avendesora
        is fed into a pipeline.  In the second case, mimicking the keyboard is
        not what you want; you should use --stdout to assure the chosen value is
        sent to the pipeline as desired.
    """).strip()
    assert result.decode('utf-8') == expected

# test_values() {{{1
def test_values():
    try:
        result = run('avendesora help values')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Display all account values.

        Show all account values.

        Usage:
            avendesora values [options] <account>

        Options:
            -a, --all    show all fields, including tool fields
            -s, --sort   sort the fields
    """).strip()
    assert result.decode('utf-8') == expected

# test_version() {{{1
def test_version():
    try:
        result = run('avendesora help version')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Display Avendesora version.

        Usage:
            avendesora version
    """).strip()
    assert result.decode('utf-8') == expected

# test_abraxas() {{{1
def test_abraxas():
    try:
        result = run('avendesora help abraxas')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Avendesora generalizes and replaces Abraxas, its predecessor.  To
        transition from Abraxas to Avendesora, you will first need to
        upgrade Abraxas to version 1.8 or higher (use 'abraxas -v' to
        determine version). Then run:

            abraxas --export

        It will create a collection of Avendesora accounts files in
        ~/.config/abraxas/avendesora. You need to manually add these files
        to your list of accounts files in Avendesora. Say one such file is
        created: ~/.config/abraxas/avendesora/accounts.gpg.  This could be
        added to Avendesora as follows:

        1. create a symbolic link from
           ~/.config/avendesora/abraxas_accounts.gpg to
           ~/.config/abraxas/avendesora/accounts.gpg:

            cd ~/.config/avendesora
            ln -s ../abraxas/avendesora/accounts.gpg abraxas_accounts.gpg

        2. add abraxas_accounts.gpg to account_files list in accounts_files.

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
    assert result.decode('utf-8') == expected

# test_accounts() {{{1
def test_accounts():
    try:
        result = run('avendesora help accounts')
    except OSError as err:
        result = os_error(err)
    expected = dedent(r"""
        Account information is stored in account files. The list of account
        files is given in ~/.config/avendesora/accounts_files.  New account
        files are created using 'avendesora new', but to delete an accounts
        file, you must remove it from accounts_files. Once an accounts file
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

            class Bank(Account):
                accounts = {
                    'checking': '1234-56-7890',
                    'savings': '0123-45-6789',
                }

        You then access its values using:

            > avendesora value bank accounts.checking
            accounts.checking: 1234-56-7890

        You might consider your account numbers as sensitive information. In
        this case you can hide them with:

            class Bank(Account):
                accounts = {
                    'checking': Hidden('MTIzNC01Ni03ODkw'),
                    'savings': Hidden('MDEyMy00NS02Nzg5'),
                }

        The values are now hidden, but not encrypted. They are simply
        encoded with base64. Any knowledgeable person with the encoded value
        can decode it back to its original value. Using Hidden makes it
        harder to recognize and remember the value given only a quick
        over-the-shoulder glance. It also marks the value as sensitive, so
        it will only be displayed for a minute. You generate the encoded
        value using 'avendesora conceal'.

        You can find the specifics of how to specify or generate your
        secrets by running 'avendesora help secrets'.

        Any value that is an instance of the GeneratedSecret class (Password,
        Passphrase, ...) or the ObscuredSecret class (Hidden, GPG, ...) are
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
        instance of PasswordRecipe, which is a subclass of GeneratedSecret.
        If we wish to see the passcode, use:

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

        Use of Avendesora classes (GeneratedSecret, ObscuredSecret, or
        Script) is confined to the top two levels of account attributes,
        meaning that they can be the value of the top-level attributes, or
        the top-level attributes may be arrays or dictionaries that contain
        objects of these classes, but it can go no further.

        By default the account name is taken to be the class name converted
        to lower case.  So the name for the NewYorkTimes account given above
        would be newyorktimes. You can override the name with the NAME
        field. This allows you to create account names that contain dashes
        or any other character that would not be acceptable in a class name
        (best to avoid characters that are meaningful to your shell, such as
        !$&*()|<>'"{}\;`.  For example:

            class Root_Work(Account):
                NAME = 'root@work'

        It is important to remember that any generated secrets use the
        account name when generating their value, so if you change the
        account name you will change the secret.  For this reason is it
        important to choose a good account name up front and not change it.
        It should be very specific to avoid conflicts with similar accounts
        created later.  For example, rather than choosing gmail as your
        account name, you might want to include your username, ex.
        gmail-paul-bunyan. This would allow you to create additional gmail
        accounts later without ambiguity. Then just add 'gmail' as an alias
        to the account you use most often.
    """).strip()
    assert result.decode('utf-8') == expected

# test_browsing() {{{1
def test_browsing():
    try:
        result = run('avendesora help browsing')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Avendesora provides the browse command to allow you to easily open
        the website for your account in your browser. To do so, it needs two
        things: a URL and a browser.

        Avendesora looks for URLs in the urls and discovery account
        attributes, with urls being preferred if both exist.  urls may
        either be a string, a list, or a dictionary. If it is a string, it
        is split at white spaces to make it a list.  If urls is a list, the
        URLs are considered unnamed and the first one given is used. If it a
        dictionary, the URLs are named.  When named, you may specify the URL
        you wish to use by specifying the name to the browse command.  For
        example, consider a urls attribute that looks like this:

            class Dragon(Account):
                username = 'rand'
                passcode = Passphrase()
                urls = dict(
                    email = 'https://webmail.dragon.com',
                    vpn = 'https://vpn.dragon.com',
                )
                default_url = 'email'

        You would access vpn with:

            avendesora browse dragon vpn

        By specifying default_url you indicate which URL is desired when you
        do not explicitly specify which you want on the browse command. In
        this way, you can access your email with either of the following:

            avendesora browse dragon email
            avendesora browse dragon

        If urls is not given, Avendesora looks for URLs in RecognizeURL
        members in the discovery attribute.  If the name argument is
        provided to RecognizeURL, it is treated as a named URL, otherwise it
        is treated as an unnamed URL.

        If named URLs are found in both urls and discovery they are all
        available to browse command, with those given in *urls* being
        preferred when the same name is found in both attributes.

        You can configure browsers for use by Avendesora using the browsers
        setting.  By default, browsers contains the following:

            browsers = dict(
                f = 'firefox -new-tab {url}',
                fp = 'firefox -private-window {url}',
                c = 'google-chrome {url}',
                ci = 'google-chrome --incognito {url}',
                q =  'qutebrowser {url}',
                t = 'torbrowser {url}',
                x = 'xdg-open {url}',
            )

        Each entry pairs a key with a command. The command will be run with {url}
        replaced by the selected URL when the browser is selected. You can choose which
        browser is used by specifying the --browser command line option on the
        browse command, by adding the browser attribute to the account, or by
        specifying the default_browser setting in the :ref:`config file
        <configuring>`.  If more than one is specified, the command line option
        dominates over the account attribute, which dominates over the setting.  By
        default, the default browser is x, which uses the default browser for your
        account.
    """).strip()
    assert result.decode('utf-8') == expected

# test_collaborate() {{{1
def test_collaborate():
    try:
        result = run('avendesora help collaborate')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        generate the secrets, but now both partners can. At a minimum you
        would need to share only the account name and the user name if one
        is needed. With that, the other partner can generate the passcode.

        Once you have shared an accounts file, you can also use the identity
        command to prove your identity to your partner.

        You cannot share secrets encrypted with Scrypt. Also, you cannot
        share stealth accounts unless the file that contains the account
        templates has a master_seed specified, which they do not by
        default. You would need to create a separate file for shared stealth
        account templates and add a master seed to that file manually.
    """).strip()
    assert result.decode('utf-8') == expected

# test_discovery() {{{1
def test_discovery():
    try:
        result = run('avendesora help discovery')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        extension.  It is a plugin that makes discovery easier and more
        robust by adding the URL to the title.  For Chrome the appropriate
        plugin is  is 'URL in Title'.  It is recommended that you install
        the appropriate one into your browser.  For AddURLToWindowTitle, set
        the following options:

            show full URL = yes
            separator string = '-'
            show field attributes = no

        For URLinTitle, set:

            tab title format = '{title} - {protocol}://{hostname}{port}/{path}'

        RecognizeURL designed to recognize such titles. Once you have
        deployed the appropriate plugin, you can use:

            discovery = RecognizeURL(
                'https://chaseonline.chase.com',
                'https://www.chase.com',
                script='{username}{tab}{passcode}{return}'
            )

        When giving the URL, anything specified must match and globbing is
        not supported. If you give a partial path, by default Avendesora
        will match up to what you have given, but you can require an exact
        match of the entire path by specifying exact_path=True to
        RecognizeURL.  If you do not give the protocol, the default_protocol
        (https) is assumed.

        In general you should use RecognizeURL() rather than
        RecognizeTitle() for websites if you can. Doing so will help protect
        you from phishing attacks by carefully examining the URL.

        When account discovery fails it can be difficult to determine what
        is going wrong. When this occurs, you should first examine the log
        file. It should show you the window title and the recognized title
        components. You should first assure the title is as expected. If Add
        URL to Window Title generated the title, then the various title
        components should also be shown.  Then run Avendesora as follows:

            avendesora value --verbose --title '<title>'

        The title should be copied from the log file. The verbose option
        causes the result of each test to be included in the log file, so
        you can determine which recognizer is failing to trigger.  You can
        either specify the verbose option on the command line or in the
        config file.

        The following recognizers are available:

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

        RecognizeAll() and RecognizeAny() can be used to combine several
        recognizers. For example:

            discovery = RecognizeAll(
                RecognizeTitle('sudo *'),
                RecognizeUser('hhyde'),
                script='{passcode}{return}'
            )

        If the recognizers are given in an array, all are tried, and each
        that match are offered. For example:

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

        If there is a need to distinguish URLs where one is a substring
        of another, you can use *exact_path*::

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

        Some similar URLs can be distinguished by their fragment. If the
        URL contains '#', then anything that follows is considered its
        fragment.  For example::

            discovery = [
                RecognizeURL(
                    'https://mybank.com/auth',
                    script='{username}{tab}{passcode}{return}',
                    fragment='/',
                ),
                RecognizeURL(
                    'https://mybank.com/auth',
                    script='{passcode}{return}',
                    fragment='/password',
                ),
            ]

        In this example, the URL 'https://mybank.com/auth/#/' would match
        the first entry, which outputs both the username and password, and a
        URL of 'https://mybank.com/auth/#/password' would match the second,
        which only outputs the password.

        RecognizeFile checks to determine whether a particular file has been
        created recently.  This can be use in scripts to force secret
        recognition.  For example, the titles used by Firefox and
        Thunderbird when collecting the master password is either
        non-existent or undistinguished.  These programs also produce a
        large amount of uninteresting chatter on their output, so it is
        common to write a shell script to run the program that redirects
        their output to /dev/null.  Such a script can be modified to
        essentially notify Avendesora that a particular password is desired.
        For example, for Thunderbird:

            #!/bin/sh
            touch /tmp/thunderbird-1024
            /usr/bin/thunderbird > /dev/null

        Here I have adding my user id (uid=1024) to make the filename unique
        so I am less likely to clash with other users. Alternately, you
        could choose a path that fell within your home directory. Then,
        adding:

            class Firefox(Account):
                desc = 'Master password for Firefox and Thunderbird'
                passcode = Password()
                discovery = RecognizeFile(
                    '/tmp/thunderbird-1024', wait=60, script='{passcode}{return}'
                )

        If the specified file exists and has been updated within the last 60
        seconds, then secret is recognized.  You can specify the amount of
        time you can wait in between running the script and running
        Avendesora with the 'wait' argument, which takes a number of
        seconds.  It defaults to 60.

        Using this particular approach, every secret would need its own
        file. But you can share a file by specifying the file contents.
        Then the script could be rewritten as:

            #!/bin/sh
            echo thunderbird > ~/.avendesora-password-request
            /usr/bin/thunderbird > /dev/null

        Then you would add something like the following to your accounts file:

            class Firefox(Account):
                desc = 'Master password for Firefox and Thunderbird'
                passcode = Password()
                discovery = RecognizeFile(
                    '~/.avendesora-password-request',
                    contents='thunderbird',
                    script='{passcode}{return}'
                )
    """).strip()
    assert result.decode('utf-8') == expected

# test_entropy() {{{1
def test_entropy():
    try:
        result = run('avendesora help entropy')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        that we are using 4 space separated lower case words as our pass
        phrase.  This is very easy to compute.  There are roughly 10,000
        words in our dictionary, so if there was only one word in our pass
        phrase, the chance of guessing it would be one in 10,000 or 13 bits
        of entropy.  If we used a two word pass phrase the chance of
        guessing it in a single guess is one in 10,000*10,000 or one in
        100,000,000 or 26 bits of entropy.

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
    assert result.decode('utf-8') == expected

# test_misdirection() {{{1
def test_misdirection():
    try:
        result = run('avendesora help misdirection')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        the secret stored in the archive will not be the true value, it
        will instead be the misdirected value.
    """).strip()
    assert result.decode('utf-8') == expected

# test_overview() {{{1
def test_overview():
    try:
        result = run('avendesora help overview')
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
        combinations for him to try (this represents a minimum entropy of 53
        bits).  Using six words results in 80 bits of entropy, which meets
        the threshold recommended by NIST for the most secure pass phrases.
        For more on this, see 'avendesora help entropy'.

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
    assert result.decode('utf-8') == expected

# test_phishing() {{{1
def test_phishing():
    try:
        result = run('avendesora help phishing')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Phishing is a very common method used on the web to get people to
        unknowingly divulge sensitive information such as account
        credentials.  It is generally accomplished by sending misleading
        URLs in email or placing them on websites. When you visit these
        URLs you are taken to a site that looks identical to the site you
        were expecting to go to in the hope that you are tricked into giving
        up your account credentials.  It used to be that if you carefully
        inspected the url you could spot deception, but even that is no
        longer true.

        Avendesora helps you avoid phishing attacks in two ways. First, you
        should never go to one of your secure sites by clicking on a link.
        Instead, you should use Avendesora's browse command:

            avendesora browse chase

        In this way you use the URL stored in Avendesora rather than
        trusting a url link provided by a third party. Second, you should
        auto-type the account credentials using Avendesora's account
        discovery based on RecognizeURL() (be sure to use RecognizeURL() for
        websites rather than RecognizeTitle() when configuring account
        discovery). RecogniseURL() will not be fooled by a phishing site).
    """).strip()
    assert result.decode('utf-8') == expected

# test_questions() {{{1
def test_security_questions():
    try:
        result = run('avendesora help sec_quest')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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

            > avendesora values <accountname>
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
    assert result.decode('utf-8') == expected

# test_scripts() {{{1
def test_scripts():
    try:
        result = run('avendesora help scripts')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        attributes including: {tab}, {return}, {sleep N}, {rate N} and
        {remind <message>}.  {tab} is replaced by a tab character, {return}
        is replaced by a carriage return character, {sleep N} causes a pause
        of N seconds, {rate N} sets the autotype rate to one keystroke every
        N milliseconds, and {remind <message>} displays message as a
        notification.  The sleep and rate functions are only active when
        auto-typing in account discovery.
    """).strip()
    assert result.decode('utf-8') == expected

# test_secrets() {{{1
def test_secrets():
    try:
        result = run('avendesora help secrets')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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

            Hidden(encoded_text, secure=True, encoding=None)

            encoded_text (str):
                The secret encoded in base64.
            secure (bool):
                Indicates that this secret should only be contained in an
                encrypted accounts file. Default is True.
            encoding (str):
                The encoding to use for the deciphered text.

        Example:

            account = Hidden('NTIwNi03ODQ0')

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
            secret = Scrypt(c2NyeXB0ABAAAAAIAAAAASfBZvtYnHvgdts2jrz5RfbYlFYj/EQgiM1IYTnXKHhMkleZceDg0yUaOWa9PzmZueppNIzVdawAOd9eSVgGeZAIh4ulPHPBGAzXGyLKc/vo8Fe24JnLr/RQBlTjM9+r6vbhi6HFUHD11M6Ume8/0UGDkZ0=)

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
            shift_sort(bool):
                If true, the characters in the password will be sorted so that
                the characters that require the shift key when typing are placed
                last, making it easier to type. Use this option if you expect to
                be typing the password by hand.
            sep (str):
                A string that is placed between each symbol in the generated
                password.
            prefix (str):
                A string added to the front of the generated password.
            suffix (str):
                A string added to the end of the generated password.

        Example:

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

        Example:

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

        Example:

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

        Example:

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
            shift_sort(bool):
                If true, the characters in the password will be sorted so that
                the characters that require the shift key when typing are placed
                last, making it easier to type. Use this option if you expect to
                be typing the password by hand.

        Example:

            passcode = PasswordRecipe('12 2u 2d 2c!@#$%^&*')


        BirthDate
        ---------

        Generates an arbitrary birthdate for someone in a specified age range.


            BirthDate(
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

        Example:

            birthdate = BirthDate(2015, 21, 55)


        OTP
        ---

        Generates a secret that changes once per minute that generally is used
        as a second factor when authenticating.  It can act as a replacement
        for, and is fully compatible with, Google Authenticator.  You would
        provide the text version of the shared secret (the backup code) that is
        presented to you when first configuring your second factor authentication.

            OTP(shared_secret, interval=30, digits=6)

            shared_secret (base32 string):
                The shared secret, it will be provided by the account provider.
            interval (int):
                Update interval in seconds.
            max_age (int):
                The number of digits to output.

        Example:

            otp = OTP('JBSWY3DPEHPK3PXP')


        Changing a Generated Secret
        ---------------------------

        It is sometimes necessary to change a generated secret. Perhaps because
        it was inadvertently exposed, or perhaps because the account provider
        requires you change your secret periodically.  To do so, you would
        simply add the *version* argument to the secret and then update its
        value.  *version* may be a number or a string. You should choose a way
        of versioning that is simple, easy to guess and would not
        repeat. For example, if you expect that updating the version would be
        extremely rare, you can simply number them sequentially. Or, if you you
        need to update them every month or every quarter, you can name them
        after the month or quarter (ex: jan19 or 19q1).

        Examples:
            passcode = PasswordRecipe('16 1d', version=2)
            passcode = PasswordRecipe('16 1d', version='19q2')
    """).strip()
    assert result.decode('utf-8') == expected

# test_stealth() {{{1
def test_stealth():
    try:
        result = run('avendesora help stealth')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        for example word4 generates a 4-word pass phrase (also referred as
        the xkcd pattern):

            > avendesora value word4
            account: my_secret_account
            gulch sleep scone halibut

        The predefined accounts are kept in
        ~/.config/avendesora/stealth_accounts.  You are free to add new
        accounts or modify the existing accounts.

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
    assert result.decode('utf-8') == expected

# test_urls() {{{1
def test_urls():
    # these tests are important because the documentation and the program may
    # have different ideas on what the URL for this help topics is.
    import requests
    from avendesora.command import Command
    from avendesora.help import HelpMessage
    base_url = 'https://avendesora.readthedocs.io/en/latest'

    def url_exists(url):
        anchor = url.split('#')[-1] if '#' in url else None

        # I have no idea why sphinx decides to use the target rather than the title 
        # for the anchor for the identity command, but here is a workaround.
        exceptions = {
            'identity-generate-an-identifying-response-to-a-challenge':
                'identity-command',
        }
        anchor = exceptions.get(anchor, anchor)

        try:
            r = requests.get(url)
            if r.status_code != 200:
                return False
            if anchor and 'href="#{anchor}"'.format(anchor=anchor) in r.text:
                return True
            return not anchor
        except:
            return False

    for cmd in Command.commands():
        path = cmd.get_help_url()
        url = base_url + path
        assert url_exists(url), url
    for topic in HelpMessage.topics():
        path = topic.URL
        if path:
            url = base_url + path
            assert url_exists(url), url

