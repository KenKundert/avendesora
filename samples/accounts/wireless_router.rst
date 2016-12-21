Wireless Router
---------------

Wireless routers typically have two or more secrets consisting of the admin 
password and the passwords for one or more wireless networks. For example, the 
router in this example supports two networks, a privileged network that allows 
connections to the various devices on the local network and the guest network 
that that only access to the internet.  In this case all three employ pass 
phrases. The admin password is held in *passcode* and the network names and 
passwords are held in the *network_passwords* array. To make the information 
about each network easy to access from the command line, two scripts are 
defined, *guest* and *privileged*, and each produces both the network name and 
the network password for the corresponding networks.

Secret discovery handles two distinct cases. The first case is when from within 
your browser you navigate to your router (ip=192.168.1.1). In this situation, 
the URL is matched and the script is run that produces the administrative 
username and password.  The second case is when you attempt to connect to 
a wireless network and a dialog box pops up requesting the SSID and password of 
the network you wish to connect to.  Running *xwininfo* shows that the title of 
the dialog box is 'Wi-Fi Network Authentication Required'. When this title is 
seen, both the title recognizers match, meaning that both the privileged and the 
guest credentials are offered as choices.

.. code-block:: python

    class NetgearAC1200_WirelessRouter(Account):
        NAME = 'home-router'
        aliases = 'wifi'
        admin_username = 'admin'
        admin_password = Passphrase()
        default = 'admin_password'
        networks = ["Occam's Router", "Occam's Router (guest)"]
        network_passwords = [Passphrase(), Passphrase()]
        privileged = Script('SSID: {networks.0}, password: {network_passwords.0}')
        guest = Script('SSID: {networks.1}, password: {network_passwords.1}')
        discovery = [
            RecognizeURL(
                'http://192.168.1.1',
                script='{admin_username}{tab}{admin_password}{return}'
            ),
            RecognizeTitle(
                'Wi-Fi Network Authentication Required',
                script='{networks.0}{tab}{network_passwords.0}{return}',
                name='home router (privileged)'
            ),
            RecognizeTitle(
                'Wi-Fi Network Authentication Required',
                script='{networks.1}{tab}{network_passwords.1}{return}',
                name='home router (guest)'
            ),
        ]
        model_name = "Netgear AC1200 wireless router"
