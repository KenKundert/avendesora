.. index::
    single: upgrading

.. _upgrading:

Upgrading
==========

Avendesora is primarily a password generator. As a result, there is always 
a chance that something could change in the password generation algorithm that 
causes the generated passwords to change. Of course, the program is thoroughly 
tested to assure this does not happen, but there is still a small chance that 
something slips through.  To assure that you are not affected by this, you 
should archive your passwords before you upgrade with::

   avendesora changed
   avendesora archive

The :ref:`changed command <changed command>` should always be run before an 
:ref:`archive command <archive command>`.  It allows you to review all the 
changes that have occurred so that you can verify that they were all 
intentional.  Once you are comfortable, run the :ref:`archive command <archive 
command>` to save all the changes.  This creates a file 
(~/.config/avendesora/archive.gpg) that contains all of your account 
information, including the secrets. Be sure to keep it safe.

Once you have created/updated your archive, you can upgrade Avendesora with::

   pip install -upgrade --user avendesora

Finally, run::

   avendesora version

to confirm that your version of *Avendesora* was updated and::

   avendesora changed

to confirm that none of your generated passwords have changed.

It is a good idea to run 'avendesora changed' and 'avendesora archive' on 
a routine basis to keep your archive up to date.

Upon updating you may find that Avendesora produces a message that a 'hash' has 
changed.  This is an indication that something has changed in the program that 
could affect the generated secrets.  Again, care is taken when developing 
Avendesora to prevent this from happening.  But it is an indication that you 
should take extra care.  Specifically you should follow the above procedure to 
assure that the value of your generated secrets have not changed.  Once you have 
confirmed that the upgrade has not affected your generated secrets, you should 
follow the directions given in the warning and update the appropriate hash 
contained in ~/.config/avendesora/.hashes.
