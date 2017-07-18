print "-------------------------------------"
print " CRYPTOMON - Crypto Currency monitor v1.0:16.07.2017"
print " By Martin Georgiev email: geeorgiev[at]gmail.com"
print " All rights reserved, GNU General Public License v3.0"
print "----------------------------------------------------"
print "loading assets...",
from coinbase.wallet.client import Client
from decimal import Decimal, ROUND_05UP, ROUND_HALF_UP
from datetime import datetime
from colorama import init
from colorama import Fore, Back, Style
import requests
import threading
import smtplib
import time
import sys
import math
# Assets that may be needed for future development
#import json
#import hmac,hashlib

print " done"
print "------------------------------------------"
init()

# APP PARAMETERS
ETH_ADDRESS = ''  # Ethereum wallet address
ETHERSCAN_API_KEY = ''  # Etherscan API KEY

# ETHEREUM MARGIN ALERTS (ETH\EUR)
ETH_HIGH = 200  # High value alert
ETH_LOW = 150  # Low value alert

# LITECOIN INVESTMENT SETTINGS (LTC\EUR)
LTC_BUY = 1  # LTC Volume

# EMAIL settings
MAIL_SERVER = 'smtp.example.com:465'  # SSL server:port
MAIL_LOGIN = ''  # SMTP username
MAIL_PASSWORD = ''  # SMTP password
MAIL_FROM = 'your name <email@example.com>'
MAIL_TO = ["email@example.com"]  # Must be an array

# Coinbase client
client = Client(
    'api_key',
    'secret',
    api_version=str('2017-07-02')
)

# Retrieving account information
try:
    accounts = client.get_accounts()
except Exception, e:
    print 'Oops! There was a problem connecting to Coinbase. ' \
        + str(e)
    print 'Please, check your configuration settings.'
    sys.exit(0)

for account in accounts.data:
    balance = account.balance
    print "%s: %s %s" % (account.name, balance.amount, balance.currency)

# TO DO
# print(account.get_transactions())

# Currency
currency_code = 'EUR'


def color_red(text):
    return Fore.RED+text+Fore.WHITE


def color_cyan(text):
    return Fore.CYAN+text+Fore.WHITE


def color_green(text):
    return Fore.GREEN+text+Fore.WHITE


def send_mail(sender, text):
    server = smtplib.SMTP_SSL(MAIL_SERVER)

    # login to mail server
    try:
        server.login(MAIL_LOGIN, MAIL_PASSWORD)
    except Exception, e:
        print color_red('Failed to authenticate with mail server. ') \
            + str(e)
        print 'Please, check your mail settings.'

    SUBJECT = "Python Crypto Currency BOT ALERT"

    message = """\
From: %s
To: %s
Subject: %s

  %s
  """ % (sender+" "+MAIL_FROM, ", ".join(MAIL_TO), SUBJECT, text)

    # Send the mail
    try:
        # In case of debug needed
        #server.set_debuglevel(1)
        server.sendmail(MAIL_FROM, MAIL_TO, message)
    except Exception, e:
        print color_red('Failed to send email alert. ') \
            + str(e)
        print 'Please, check your mail settings.'
        print color_red('failed')
    else:
        server.quit()
        print color_green('done')


# ETH/EUR sell price getter
def get_etheur_sell_price():
    etheur_sell_price = float(
        client.get_sell_price(currency_pair='ETH-EUR')['amount'])
    return etheur_sell_price


# ETH/EUR buy price getter
def get_etheur_buy_price():
    etheur_buy_price = float(
        client.get_buy_price(currency_pair='ETH-EUR')['amount'])
    return etheur_buy_price


# ETH/EUR buy price getter
def get_btceur_sell_price():
    btceur_sell_price = float(
        client.get_sell_price(currency_pair='BTC-EUR')['amount'])
    return btceur_sell_price


# Collects ETH balance
def get_eth_balance():
    url = 'https://api.etherscan.io/api?' \
        'module=account&action=balance&address='+ETH_ADDRESS+'&' \
        'tag=latest&apikey='+ETHERSCAN_API_KEY
    try:
        r = requests.get(url)
    except Exception, e:
        print color_red('Failed to connect to Etherscan.io: ') \
            + str(e)
        return 0
    else:
        return round(int(r.json()['result'])/math.pow(10, 18), 6)


# Converts ETH balance in EUR
def get_etheur_balance(price):
    return round(get_eth_balance() * price, 2)


def printit():
    global eth_dropped
    global old_price

    eth_dropped = 0

    # Print LTC balance and prices
    ltc_price = client.get_sell_price(currency_pair='LTC-EUR')
    ltc_pricy = float(ltc_price['amount'])
    sum = round(ltc_pricy * float(balance.amount) * 1.955, 2)
    print "LTC sell price:", ltc_price['amount'], "BGN"
    print "LTC BGN", sum, "(", sum - LTC_BUY, ")"

    # Print ETH price
    etheur_sell_price = get_etheur_sell_price()

    print color_cyan("ETH sell price:"), etheur_sell_price,
    print color_cyan("EUR,"), etheur_sell_price * 1.955, color_cyan("BGN")
    print color_cyan('Account balance: ') \
        + str(get_eth_balance())+color_cyan(' ETH')
    print color_cyan('Account balance: ') \
        + str(get_etheur_balance(etheur_sell_price))+color_cyan(' EUR')
    print "------------------------------------------"
    print color_cyan('Monitoring ETH... ')

    # Delay next requests
    # time.sleep(2)

    # Print BTC price
    #btc_price = client.get_sell_price(currency_pair = 'BTC-EUR')
    #print "BTC sell price:", btc_price['amount'], "EUR"
    old_price = etheur_sell_price

printit()


def eth_monitor():
    global eth_dropped
    global etheur_sell_price
    if eth_dropped == 0:
        if etheur_sell_price <= ETH_LOW or etheur_sell_price >= ETH_HIGH:
            eth_dropped = 1
            print color_cyan('ETH reached price: ') \
                + str(etheur_sell_price)+color_cyan(' EUR') \
                + color_cyan(' sending mail... '),
            send_mail('Ethereum Monitor',
                      'ETH sell price: '+str(etheur_sell_price))


def loopeth():
    global clock
    global old_price
    global etheur_sell_price

  # Current local time getter
    clock = datetime.now().strftime('[%Y-%m-%d %H:%M]')

  # Print LOOP ETH price
    etheur_sell_price = get_etheur_sell_price()
    etheur_buy_price = get_etheur_buy_price()

    """ print colors
    Fore.GREEN
    Fore.RED
    Fore.CYAN """

    if old_price < etheur_sell_price:
        print clock+color_green(" ETH sell price raised: "
                                + str(etheur_sell_price)+" EUR,"),
        print color_cyan('Balance: ') \
            + str(get_etheur_balance(etheur_sell_price))+color_cyan(' EUR') \
            + color_cyan(', BUY: ') \
            + str(get_etheur_buy_price())+color_cyan(' EUR')
    elif old_price > etheur_sell_price:
        print clock+color_red(" ETH sell price dropped: "
                              + str(etheur_sell_price)+" EUR,"),
        print color_cyan('Balance: ') \
            + str(get_etheur_balance(etheur_sell_price))+color_cyan(' EUR') \
            + color_cyan(', BUY: ') \
            + str(get_etheur_buy_price())+color_cyan(' EUR')

  #else:
    # Optional tick for the current price
    #print clock+color_cyan(" ETH sell price: ")+str(etheur_sell_price),
    color_cyan("EUR, ")+str(etheur_sell_price * 1.955)+color_cyan(" BGN")
    eth_monitor()
    old_price = etheur_sell_price
    threading.Timer(60, loopeth).start()

loopeth()

#print client.get_buy_price(currency_pair = 'ETH-EUR')

# Make the request
#price = client.get_spot_price(currency=currency_code)
#print 'Current bitcoin price in %s: %s' % (currency_code, price.amount)

#k=input("press close to exit")
