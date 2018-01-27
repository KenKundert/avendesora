.. index::
    single: installing

.. _installing:

Installing and First Use
========================

Install with::

   pip3 install --user avendesora

This will place avendesora in ~/.local/bin, which should be added to your path.

You will also need to install some operating system commands. On Redhat systems 
(Fedora, Centos, Redhat) use::

   yum install gnupg2 xdotool xsel

You should also install python-gobject. Conceivably this could be installed with 
the above pip command, but gobject appears broken in pypi, so it is better use 
the operating system's package manager to install it.  See the setup.py file for 
more information.  On Redhat systms use::

   yum install python3-gobject

If you would like to use scrypt as a way of encrypting fields, you will need to 
install scrypt by hand using::

   pip3 install --user scrypt


GPG Key
-------

To use *Avendesora*, you will need GPG and you will need a GPG ID that is 
associated with a private key. That GPG ID could be in the form of an email 
address or an ID string that can be found using 'gpg --list-keys'.

If you do not yet have a GPG key, you can get one using::

   $ gpg --gen-key

You should probably choose 4096 RSA keys. Now, edit ~/.gnupg/gpg-conf and add 
the line::

   use-agent

That way, you generally need to give your GPG key passphrase less often. The 
agent remembers the passphrase for you for a time. Ten minutes is the default, 
but you can configure gpg-agent to cache passphrases for as long as you like.

If you use the agent, be sure to also use screen locking so your passwords are 
secure when you walk away from your computer.


Vim
---

If you use Vim, it is very helpful for you to install GPG support in Vim. To do 
so first download::

    http://www.vim.org/scripts/script.php?script_id=3645

Then copy the file into your Vim configuration hierarchy::

    cp gnupg.vim ~/.vim/plugin


.. _initializing avendesora:

Initializing Avendesora
-----------------------

To operate, *Avendesora* needs a collection of configuration and accounts files 
that are stored in ~/.config/avendesora. To create this directory and the 
initial versions of these files, run::

    avendesora init -g <gpg_id>

For example::

    avendesora init -g rand@dragon.com

or::

    avendesora init -g 1B2AFA1C

If you would like to have more than one person access your passwords, you should 
give GPG IDs for everyone::

    avendesora init -g rand@dragon.com,lews.therin@dragon.com

After initialization, there should be several files in ~/.config/avendesora. In 
particular, you should see at least an initial accounts files and a config file.


.. index::
    single: initial configuration
    single: configuring

.. _initial configuration:

Initial Configuration
---------------------

The config file (~/.config/avendesora/config) allows you to personalize 
*Avendesora* to your needs. The available configuration settings are documented 
in ~/.config/avendesora/config.doc. After initializing your account you should 
take the time to review your configuration and adjust it to fit your needs. You 
should be very thoughtful in this initial configuration, because some decisions 
(or non-decisions) you make can be very difficult to change later.  The reason 
for this is that they may affect the passwords you generate, and if you change 
them you may change existing generated passwords. In particular, be careful with 
*dictionary_file*.  Changing this value when first initializing *Avendesora* is 
fine, but should not be done or done very carefully once you start creating 
accounts and secrets.

During an initial configuration is also a convenient time to determine which of 
your files should be encrypted with GPG. To assure that a file is encrypted, 
give it a GPG file suffix (.gpg or .asc). The appropriate settings to adjust 
are: *archive_file*, *log_file*, both of which are set in the config file, and 
the accounts files, which are found in ~/.config/avendesora/.accounts_files. For 
security reasons it is highly recommended that the archive file be encrypted, 
and any accounts file that contain sensitive accounts. If you change the suffix 
on an accounts file and you have not yet placed any accounts in that file, you 
can simply delete the existing file and then regenerate it using::

    avendesora init -g <gpg_id>

Any files that already exist will not be touched, but any missing files will be 
recreated, and this time they will be encrypted or not based on the extensions 
you gave.

More information on the various configuration options can be found in 
:ref:`configuring`.

.. index::
    single: configuring window manager
    single: window manager

.. _configure window manager:

Configuring Your Window Manager
-------------------------------

You will want to configure your window manager to run *Avendesora* when you type 
a special hot key, such as ``Alt p``.  The idea is that when you are in 
a situation where you need a secret, such as visiting your bank's website in 
your browser, you can click on the username field with your mouse and type your 
hot key.  This runs *Avendesora* without an account name. In this case, 
*Avendesora* uses :ref:`account discovery <discovery>` to determine which secret 
to use and the script that should be used to produce the required information.  
Generally the script would be to enter the username or email, then tab, then the 
passcode, and finally return, but you can configure the script as you choose.  
This is all done as part of configuring discovery. The method for associating 
*Avendesora* to a particular hot key is dependent on your window manager.

Gnome:

    With Gnome, you must open your Keyboard Shortcuts preferences and create 
    a new shortcut. When you do this, choose 'avendesora value' as the command 
    to run.

I3:

    Add the following to your I3 config file (~/.config/i3/config)::

        bindsym $mod+p exec --no-startup-id avendesora value


OpenBox:

    Key bindings are found in the <keyboard> section of your rc.xml 
    configuration file. Add a key binding for *Avendesora* like this::

        <keyboard>
        ...
            <keybind key="A-p">
                <action name="Execute">
                    <command>avendesora value</command>
                </action>
            </keybind>
        ...
        </keyboard>


Configuring Your Browser
------------------------

Finally, to improve account discovery, it is recommended that you add a plugin 
to your web browser that puts the URL into the window title. How to do so is 
described in :ref:`discovery`.

