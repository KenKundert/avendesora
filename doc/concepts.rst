Conceptual Underpinnings
========================

.. index::
    single: generated secrets

.. _generated secrets:

Generated Secrets
-----------------

Account secrets can be saved in encrypted form, as with password vaults, or 
generated from a root secret.  Generated secrets have several important 
benefits.  First, they are produced from a random seed, and so are quite 
unpredictable.  This is important, because predictability can be exploited when 
cracking passwords.  Second, if the root secret is shared with another trusted 
party, then you both can generate new shared secrets without passing any further 
secrets.  Furthermore, if you keep a copy of the root secret, say in a safe 
deposit box, then there is a good chance you can resurrect your secrets if you 
happen to lose your accounts files.  Finally, with generated secrets, it is 
possible to have :ref:`stealth secrets <stealth accounts>`, which are secrets 
for which there is absolutely no evidence.

Secrets are generated from a collection of seeds, one of which must be random 
with a very high degree of entropy. The random seed is referred to as the 
'master seed'.  It is extremely important that the master seed remain completely 
secure.  Never disclose a master seed to anyone except for a person you wish to 
collaborate with, and then only use the shared master seed for shared secrets.  
Each file that contains accounts will contain a master seed for the accounts it 
holds.  Typically, you would have one file to hold your private accounts, and 
then one file for every group of people you collaborate with.

A secret is generated by combining a master seed with several other seeds, such 
as the account name, the secret name, and perhaps a version name.  The 
combination is then hashed to form a long binary number that is unique to your 
secret. From there the number is transformed into a usable form by one of the 
Secrets classes. PIN() converts it to a sequence of digits, Password() converts 
it to a sequence of characters, Passphrase converts it to a sequence of words, 
etc.

For example, consider the following rather abbreviated accounts file:

.. code-block:: python

    from avendesora import Account, Passphrase

    master_seed = 'c2VjcmV0IG1lc3NhZ2UsIHN1Y2Nlc3NmdWxseSBkZWNvZGVkIQ'

    class Login(Account):
        username = 'rand'
        passcode = Passphrase()

This file contains one secret, the login passphrase for Rand.  In this case, the 
master seed is combined with the words 'login' (the account name, down cased) 
and 'passcode' (the attribute name); the combination is hashed, and the hash is 
used to generate the passphrase.  The words in the passphrase are chosen at 
random from a dictionary of roughly 10,000 words.  The first word is chosen by 
taking the first 14 bits from the hash and using that number to select a word. 
The second word is chosen using the next 14 bits, and so on.  The hash is 
constructed such that even the smallest changes in any seed results in 
a completely different hash. As such, the resulting passphrase is quite 
unpredictable::

    > avendesora login
    username: rand
    passcode: dither estate cockroach flavoring

The passcode itself is not stored, rather it is the seeds that are stored and 
the passcode is regenerated when needed. Notice that all the seeds except the 
master seed need not be kept secure. Thus, once you have shared a master seed 
with a collaborator, all you need to do is share the remaining seeds and your 
collaborator can generate exactly the same passcode.

Another important thing to notice is that the generated passcode is dependent on 
the account and secret names. Thus if you rename your account or your secret, 
the passcode will change.  So you should be careful when you first create your 
account to choose names appropriately so you don't feel the need to change them 
later.

.. index::
    single: entropy

.. _entropy:

Entropy
-------
A 4 word Avendesora password provides 53 bits of entropy, which seems like 
a lot, but NIST is recommending 80 bits for your most secure passwords.  So, how 
much is actually required? It is worth exploring this question.

Entropy is a measure of how hard the password is to guess. Specifically, it is 
the base two logarithm of the likelihood of guessing the password in a single 
guess. Every increase by one in the entropy represents a doubling in the 
difficulty of guessing your password. The actual entropy is hard to pin down, so 
generally we talk about the minimum entropy, which is the likelihood of an 
adversary guessing the password if he or she knows everything about the scheme 
used to generate the password but does not know the password itself.  So in this 
case the minimum entropy is the likelihood of guessing the password if it is 
known that we are using 4 space separated words as our passphrase where the 
words are selected at random with a uniform distribution from a known list.  
This is very easy to compute.  There are roughly 10,000 words in our dictionary, 
so if there was only one word in our passphrase, the chance of guessing it would 
be one in 10,000 or 13 bits of entropy.  If we used a two word passphrase the 
chance of guessing it in a single guess is one in 10,000*10,000 or one in 
100,000,000 or 26 bits of entropy.

The probability of guessing our passphrase in one guess is not our primary 
concern. Really what we need to worry about is given a determined attack, how 
long would it take to guess the password. To calculate that, we need to know how 
fast our adversary could try guesses. If they are trying guesses by typing them 
in by hand, their rate is so low, say one every 10 seconds, that even a one word 
passphrase may be enough to deter them.  This is why bank PINs can be so short.  
Our one word passphrase provides roughly the same security as a four digit PIN.  
Alternatively, they may have a script that automatically tries passphrases 
through a login interface.  Again, generally the rate is relatively slow.  
Perhaps at most they can get is 1000 tries per second. In this case they would 
be able to guess a one word passphrase in 10 seconds and a two word passphrase 
in a day, but a 4 word passphrase would require 300,000 years to guess in this 
way.

The next important thing to think about is how your password is stored by the 
machine or service you are logging into. The worst case situation is if they 
save the passwords in plain text. In this case if someone were able to break in 
to the machine or service, they could steal the passwords. Saving passwords in 
plain text is an extremely poor practice that was surprisingly common, but is 
becoming less common as companies start to realize their liability when their 
password files get stolen.  Instead, they are moving to saving passwords as 
hashes.  A hash is a transformation that is very difficult to reverse, meaning 
that if you have the password it is easy to compute its hash, but given the hash 
it is extremely difficult to compute the original password. Thus, they save the 
hashes (the transformed passwords) rather than the passwords. When you log in 
and provide your password, it is transformed with the hash and the result is 
compared against the saved hash. If they are the same, you are allowed in. In 
that way, your password is not stored and so is no longer available to thieves 
that break in.  However, they can still steal the file of hashed passwords, 
which is not as good as getting the plain text passwords, but it is still 
valuable because it allows thieves to greatly increase the rate that they can 
try passwords. If a poor hash was used to hash the passwords, then passwords can 
be tried at a very high rate.  For example, it was recently reported that 
password crackers were able to try 8 billion passwords per second when passwords 
were hashed with the MD5 algorithm. This would allow a 4 word passphrase to be 
broken in 14 days, whereas a 6 word password would still require 4,000,000 years 
to break.  The rate for the more computational intensive sha512 hash was only 
2,000 passwords per second. In this case, a 4 word passphrase would require 
160,000 years to break.

In most cases you have no control over how your passwords are stored on the 
machines or services that you log into.  Your best defense against the 
notoriously poor security practices of most sites is to always use a unique 
password for sites where you are not in control of the secrets.  That way the 
poor security practices of one site would not compromise your other accounts.  
For example, you might consider using the same passphrase for your login 
password and the passphrase for an ssh key on a machine that you administer, but 
never use the same password for two different websites unless you do not care if 
the content of those sites become public.

So, if we return to the question of how much entropy is enough, you can say that 
for important passwords where you are in control of the password database and it 
is extremely unlikely to get stolen, then four randomly chosen words from 
a reasonably large dictionary is plenty.  If what the passphrase is trying to 
protect is very valuable and you do not control the password database (ex., your 
brokerage account) you might want to follow the NIST recommendation and use 
6 words to get 80 bits of entropy. If you are typing passwords on your work 
machine, many of which employ keyloggers to record your every keystroke, then no 
amount of entropy will protect you from anyone that has or gains access to the 
output of the keylogger.  In this case, you should consider things like one-time 
passwords or two-factor authentication. Or better yet, only access sensitive 
accounts from your home machine and not from any machine that you do not 
control.
