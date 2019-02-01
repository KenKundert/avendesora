Known Issues
============

.. index::
    single: kpns
    single: known issues
    single: Chrome issues

Spotty Account Recognition
--------------------------

When using account discovery you may find that sometimes accounts do not get 
recognized but other times they do. There are two causes for this. Account 
recognition is based on the window title, and browsers tend not to update the 
window title until the page is completely loaded. So generally intermittent 
account recognition occurs because you trigger *Avendesora* before the page has 
completed loaded. This problem is aggravated with modern websites because they 
often continue loading images, scripts, advertisements, etc. even after the page 
initially renders. You can generally work around this issue by simply hitting 
the stop button on the browser or by typing the ESC key, which should do the 
same thing.

The second cause is a bit more problematic.  The Chrome browser, or perhaps the 
URL in Title extension, seems to have a bug that interferes with its use with 
account discovery, and ironically it tends to interfere when logging into your 
Google accounts. The problem is that in some cases Chrome does not update its 
title when you navigate to a new but related page; the title from the previous 
page persists.  This can occur if you give the URL for a particular service, 
like gmail.com or tv.youtube.com, and you get forwarded to the generic login 
page.  It can also happen during the two step login process used when logging in 
where the title occasionally does not update as you go from the username page to 
the password page.  In these cases *Avendesora* sees the wrong URL and either 
enters the wrong thing or does not recognize the page.  Generally, refreshing 
the page allows you to work around this bug.


.. index::
    single: issues, reporting
    single: reporting issues

Reporting Issues
----------------

If you discover any issues with *Avendesora*, or have some suggestions, or 
simply want to help out, please visit `Avendesora issues 
<https://github.com/KenKundert/avendesora/issues>`_.
