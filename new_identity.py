from stem.control import Controller
from stem import Signal
import requests
from writer import writer
import time


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


# signal TOR for a new connection
def renew_connection():
    print("new Identity requested")
    writer("new Identity requested",starting=False)
    session = get_tor_session()
    try:
        old_ip=session.get("https://icanhazip.com/").text.strip()
    except:
        writer("exceptuion occured in icanhazip.com")
        print("exceptuion occured in icanhazip.com")    
        old_ip=session.get("https://checkip.amazonaws.com/").text.strip()

    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="tor password")
        controller.signal(Signal.NEWNYM)
        time.sleep(1)
        session = get_tor_session()
        
        try:
            new_ip=session.get("https://icanhazip.com/").text.strip()
        except:
            writer("exceptuion occured in icanhazip.com")
            print("exceptuion occured in icanhazip.com")
            new_ip=session.get("https://checkip.amazonaws.com/").text.strip()
    tries = 0        
    while old_ip==new_ip:
        tries += 1
        if tries>5:
            renew_connection()
        print("trying again")
        time.sleep(1)
        session = get_tor_session()
        try:
            new_ip=session.get("https://icanhazip.com/").text
        except:
            writer("exceptuion occured in icanhazip.com")
            print("exceptuion occured in icanhazip.com")        
            new_ip=session.get("https://checkip.amazonaws.com/").text.strip()

    
    print("new Ip: ",new_ip)
    writer("new Ip: "+str(new_ip))