Credit Card Information
-----------------------

Many websites offer to store your credit card information. Of course, we have 
all heard of the massive breeches that have occurred on such websites, often 
resulting in the release of credit card information.  So all careful denizens of 
the web are reluctant to let the websites keep their information. This results 
in you being forced into the tedious task of re-entering this information.

Avendesora can help with this. If you have a website that you find yourself 
entering credit card information into routinely, then you can use the account 
discovery and autotype features of Avendesora to enter the information for you.

For example, imagine that you have a Citibank credit card that you use routinely 
on the Costco website.  You can configure Avendesora to automatically enter your 
credit card information into the Costco site with by adding an account discovery 
entry to your Citibank account as follows::

    class CostcoCitiVisa(Account):
        aliases = 'citi costcovisa'
        username = 'giddy2050'
        email = 'herbie@telegen.com'
        account = '1234 5678 8901 2345'
        expiration = '03/2019'
        cvv = '233'
        passcode = PasswordRecipe('12 2u 2d 2s')
        verbal = Question('Favorite pet?', length=1)
        questions = [
            Question("Fathers profession?"),
            Question("Last name of high school best friend?"),
            Question("Name of first pet?"),
        ]
        discovery = [
            RecognizeURL(
                'https://online.citi.com',
                script='{username}{tab}{passcode}{return}',
                name='login'
            ),
            RecognizeURL(
                'https://www.costco.com/CheckoutPaymentView',
                script='{account}{tab}{expiration}{tab}{cvv}{tab}Herbie Thudpucker{return}',
                name='card holder information'
            ),
        ]

This represents a relatively standard Avendesora description of an account.  
Notice that it contains the credit card number (*account*), the expiration date 
(*expriration*) and the CVV number (*cvv*). This is raw information the autotype 
script will pull from. The credit card and the CVV values are sensitive 
information and should probably be concealed.

Also notice the two *RecognizeURL* entries in *discovery*. The first recognizes 
the CitiBank website. The second recognizes the Costco check-out page. When it 
does, it runs the following script::

    {account}{tab}{expiration}{tab}{cvv}{tab}Herbie Thudpucker{return}

That script enters the account number, tabs to the next field, enters the 
expiration date, tabs to the next field, enters the CVV, tabs to the next field, 
enters the account holders name, and finally types return to submit the 
information (you might want to delete the {return} so that you have a chance to 
review all the information before you submit manually. Or you could continue the 
script and give more information, such as billing address.

Conceptually this script should work, but Costco, like many websites, uses 
Javascript helpers to interpret the fields. These helpers are intended to give 
you immediate feedback if you typed something incorrectly, but they are slow and 
can get confused if you type too fast. As is, the first one or two fields would 
be entered properly, but the rest would be empty because they were entered by 
Avendesora before the page was ready for them. To address this issue, you can 
put delays in the script::

    {account}{tab}{sleep 0.5}{expiration}{tab}{sleep 0.5}{cvv}{tab}{sleep 0.5}Herbie Thudpucker{return},

Now the account can be given in its final form. This differs from the one above 
in that the *account* and *cvv* values are concealed and the delays were added 
to the Costco script.

    class CostcoCitiVisa(Account):
        aliases = 'citi costcovisa'
        username = 'giddy2050'
        email = 'herbie@telegen.com'
        account = Hidden('MTIzNCA1Njc4IDg5MDEgMjM0NQ==')
        expiration = '03/2019'
        cvv = Hidden('MjMz')
        passcode = PasswordRecipe('12 2u 2d 2s')
        verbal = Question('Favorite pet?', length=1)
        questions = [
            Question("Fathers profession?"),
            Question("Last name of high school best friend?"),
            Question("Name of first pet?"),
        ]
        discovery = [
            RecognizeURL(
                'https://online.citi.com',
                script='{username}{tab}{passcode}{return}',
                name='login'
            ),
            RecognizeURL(
                'https://www.costco.com/CheckoutPaymentView',
                script='{account}{tab}{sleep 0.5}{expiration}{tab}{sleep 0.5}{cvv}{tab}{sleep 0.5}Herbie Thudpucker{return}',
                name='card holder information'
            ),
        ]

