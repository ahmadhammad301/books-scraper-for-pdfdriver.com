import requests
from stem import Signal
from stem.control import Controller

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


# signal TOR for a new connection
def renew_connection():

    session = get_tor_session()
    old_ip=session.get("https://icanhazip.com/").text
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="Hammad")
        controller.signal(Signal.NEWNYM)
        session = get_tor_session()
        new_ip=session.get("https://icanhazip.com/").text
    if old_ip==new_ip:
        renew_connection()

renew_connection()
session = get_tor_session()
print("my tor ip: ", session.get("https://icanhazip.com/").text)


print("my real_ip: ",requests.get("https://icanhazip.com/").text)

# cm._get_connection()
# # cm.request('google.com').text
# print(requests.get('https://httpbin.org/ip').text)