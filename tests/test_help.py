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
            avendesora [options] add [<template>]
            avendesora [options] a   [<template>]

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

        The available accounts files are:
            accounts
            templates
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
            avendesora A

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
            avendesora [options] browse <account> [<key>]
            avendesora [options] b      <account> [<key>]

        Options:
            -b <browser>, --browser <browser>
                                    Open account in specified browser.

        The account is examined for URLS, a URL is chosen, and then that URL
        is opened in the chosen browser.  First URLS are gathered from the
        'urls' account attribute, which can be a string containing one or
        more URLS, a list, or a dictionary.  If 'urls' is a dictionary, the
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
                username = 'viscount-placebo'
                url = 'http://silkroad6ownowfk.onion'
                browser = 't'

        The available browsers are:
            c  google-chrome
            f  firefox
            t  torbrowser
            x  xdg-open
    """).strip()
    assert result.decode('utf-8') == expected

# test_changed() {{{1
def test_changed():
    try:
        result = run('avendesora help changed')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Identify any changes that have occurred since the archive was created.

        Usage:
            avendesora changed
            avendesora C

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

# test_conceal() {{{1
def test_conceal():
    try:
        result = run('avendesora help conceal')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
        Conceal text by encoding it.

        Usage:
            avendesora [options] conceal [<text>]
            avendesora [options] c       [<text>]

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when concealing information.
            -s, --symmetric         Encrypt with a passphrase rather than using your
                                    GPG key (only appropriate for gpg encodings).

        Possible encodings include (default encoding is base64):

        base64:
            This encoding obscures but does not encrypt the text. It can
            protect text from observers that get a quick glance of the
            encoded text, but if they are able to capture it they can easily
            decode it.

        gpg:
            This encoding fully encrypts/decrypts the text with GPG key.
            By default your GPG key is used, but you can specify symmetric
            encryption, in which case a passphrase is used.

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
            avendesora e    <account>

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
            avendesora f    <text>
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
            avendesora help [<topic>]
            avendesora h    [<topic>]
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
            avendesora ident    [<name> [<challenge>...]]
            avendesora i        [<name> [<challenge>...]]

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
        but it is important that you not use the same challenge twice. As
        such, it is recommended that you not provide the challenge. In this
        situation, one is generated for you based on the time and date.

        Consider an example that illustrates the process. In this example,
        Ahmed is confirming the identity of Reza, where both Ahmed and Reza
        are assumed to have shared Avendesora accounts.  Ahmed runs
        Avendesora as follows and remembers the response:

            avendesora identity reza
            challenge: slouch emirate bedeck brooding
            response: spear disable local marigold

        This assumes that reza is the name, with any extension removed, of
        the file that Ahmed uses to contain their shared accounts.

        Ahmed communicates the challenge to Reza but not the response.  Reza
        then runs Avendesora with the given challenge:

            avendesora identity ahmed slouch emirate bedeck brooding
            challenge: slouch emirate bedeck brooding
            response: spear disable local marigold

        In this example, ahmed is the name of the file that Reza uses to
        contain their shared accounts.

        To complete the process, Reza returns the response to Ahmed, who
        compares it to the response he received to confirm Reza's identity.
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
            avendesora initialize [--gpg-id <id>]... [options]
            avendesora I          [--gpg-id <id>]... [options]

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
            -h <path>, --gpg-home <path>
                                    GPG home directory (default is ~/.gnupg).

        Create Avendesora data directory (~/.config/avendesora) and populate
        it with initial versions of all essential files.

        It is safe to run this command even after the data directory and
        files have been created. Doing so will simply recreate any missing
        files.  Existing files are not modified.
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
            avendesora new [--gpg-id <id>]... <name>
            avendesora N   [--gpg-id <id>]... <name>

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.

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
            avendesora r      [<text>]

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
            avendesora s      <text>
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
            avendesora value [options] [--stdout | --clipboard] [<account> [<field>]]
            avendesora val   [options] [--stdout | --clipboard] [<account> [<field>]]
            avendesora v     [options] [--stdout | --clipboard] [<account> [<field>]]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -s, --stdout            Write output to the standard output without
                                    any annotation or protections.
            -S, --seed              Interactively request additional seed for
                                    generated secrets.
            -v, --verbose           Add additional information to log file to
                                    help identify issues in account discovery.
            -t <title>, --title <title>
                                    Use account discovery on this title.

        You request a scalar value by specifying its name after the account.
        For example:

            avendesora value pin

        If is a composite value, you should also specify a key that indicates
        which of the composite values you want. For example, if the 'accounts'
        field is a dictionary, you specify accounts.checking or
        accounts[checking] to get information on your checking account. If the
        value is an array, you give the index of the desired value. For example,
        questions.0 or questions[0]. If you only specify a number, then the name
        is assumed to be 'questions', as in the list of security questions (this
        can be changed by specifying the desired name as the
        'default_vector_field' in the account or the config file).

        If no value is requested the result produced is determined by the value
        of the 'default' attribute. If no value is given for 'default', then the
        'passcode' attribute is produced (this can be changed by specifying
        'default_field' in the config file).  If 'default' is a script (see
        'avendesora help scripts') then the script is executed. A typical script
        might be 'username: {username}, password: {passcode}'. It is best if the
        script produces a one line output if it contains secrets. If not a
        script, the value of 'default' should be the name of another attribute,
        and the value of that attribute is shown.
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
            avendesora values <account>
            avendesora vals   <account>
            avendesora V      <account>
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
    assert result.decode('utf-8') == expected

# test_accounts() {{{1
def test_accounts():
    try:
        result = run('avendesora help accounts')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""
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
        the secret stored in in the archive will not be the true value, it
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

        To use it, one creates a file that contains information about each
        of his or her non-stealth accounts.  Among that information would be
        information that controls how the passwords are generated. This file
        is generally not encrypted, though you can encrypt it if you like).
        Another file is created that contains one or more master seeds.
        This file is always GPG encrypted.

        The intent is for these files to not include the passwords for your
        accounts.  Rather, the passwords are regenerated when needed from
        the account information and from the master seed. This makes it
        easy to share passwords with others without having to pass the
        passwords back and forth.  It is only necessary to create a shared
        master seed in advance. Then new passwords can be created on the
        fly by either party.
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
        attributes including: {tab}, {return}, and {sleep N}.  {tab} is
        replaced by a tab character, {return} is replaced by a carriage
        return character, and {sleep N} causes a pause of N seconds. The
        sleep function is only active when autotyping after account
        discovery.
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
        that contains the stealth account if it exists, or the users key if
        it does not. By default the stealth accounts file does not contain a
        master seed, which makes it difficult to share stealth accounts.
        You can create additional stealth account files that do contain
        master seeds that you can share with your associates.
    """).strip()
    assert result.decode('utf-8') == expected

# test_security_questions() {{{1
def test_security_questions():
    try:
        result = run('avendesora help questions')
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
    assert result.decode('utf-8') == expected

