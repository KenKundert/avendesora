Google and Gmail
----------------

Google always seems to keep futzing with there security protocols in order to 
make them more secure, but at the same time also seem to make them more 
annoying. As such, I have gone through several approaches to making the Google 
login work with Avendesora. The latests, as of 2017, is shown below. Google uses 
a different page when requesting your username or email, your passcode, and the 
answer to your challenge questions. So the current approach is to simply 
recognize each of those pages individually.  You can use something like this for 
your Gmail/Google account entry::

    class Gmail(Account):
        aliases = 'gmail google'
        username = '_YOUR_USERNAME_'
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
                script='{passcode}{return}',
                name='passcode',
            ),
            RecognizeURL(
                'https://accounts.google.com/signin/challenge',
                script='{questions}{return}',
                name='challenge',
            ),
        ]
