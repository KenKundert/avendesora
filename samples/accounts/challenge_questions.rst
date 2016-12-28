Challenge Questions
-------------------

Websites originally used challenge questions to allow you to re-establish your 
identity if you lose your user name or password, so it was enough to simply save 
the answers so that they were available if needed. But now many websites require 
you to answer the challenge questions if the site does not recognize your 
browser because your cookie expired or was deleted. As such, people need to 
answer their challenge questions with much more frequency. Generally the site 
will save your answers to 4 or 5 challenge questions, and will present you with 
1 or 2 at random. You must answer them correctly before you are allowed to 
login.  To accommodate these needs, Avendesora saves the challenge questions and 
either stores or generates the answers. It is also makes it easy for you to 
autotype the answer to any of your questions.

The following shows how to configure an account to support challenge questions.

.. code-block:: python

    class BankOfAmerica(Account):
        aliases = 'boa bankamerica'
        username = 'sheldoncooper'
        passcode = PasswordRecipe('12 2l 2u 2d 2s)
        questions = [
            Question('elementary school?'),
            Question('favorite foreign city?'),
            Question('first pet?'),
            Question('what year was your father born?'),
            Question('favorite movie?'),
        ]
        discovery = [
            RecognizeURL(
                'https://www.bankofamerica.com/',
                script='{username}{tab}{passcode}{return}'
            ),
            RecognizeURL(
                'https://secure.bankofamerica.com',
                script='{questions}{tab}',
            ),
        ]

In this case 5 questions are supported. When you are first required to set up 
your challenge questions the website generally presents you with 20 or 30 to 
choose form.  Simply choose the first few and add them to your account.

Then use the *value* command to generate the answers and copy them into the 
website.  You need not enter the questions into Avendesora exactly, but once you 
provide your website with the generated answers you must not change the 
questions in any way because doing so would change the answers.  Finally, the 
first time you are required to enter answers to the challenge questions, take 
note of the URL and add a discovery entry that matches the url and generates the 
questions. In most cases you will not be able to specify a single question, so 
simply specify the array and Avendesora will allow you to choose a particular 
question when you request an answer. Specifically, when the website takes you to 
the challenge question page, click in the field for the first answer and type 
the hotkey that runs Avendesora in autotype mode.  Avendesora should recognize 
the page and allow you to identify the question. It will then autotype the 
answer into the field and then move to the next field.  Alternately, if you 
terminate the script with '{return}' rather than '{tab}', it will take you to 
the next page.

In some cases the website makes you choose from a fixed set of answers. In this 
case you would save the answer with the question as follows:

.. code-block:: python

    class BankOfAmerica(Account):
        ...
        questions = [
            Question('elementary school?', answer='MLK Elementary'),
            Question('favorite foreign city?', answer='Kashmir'),
            Question('first pet?', answer='Spot'),
            Question('what year was your father born?', answer='1950'),
            Question('favorite movie?', answer='A boy and his dog'),
        ]
        ...
