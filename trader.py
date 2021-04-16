''' Resources '''
#https://docs.kucoin.com/#get-part-order-book-aggregated
#https://python-kucoin.readthedocs.io/en/latest/kucoin.html?highlight=fiat#kucoin.client.Client.get_fiat_prices

#Kucoin trading bot
import sys
sys.path.append('C:\\Users\\zinex\\Documents\\Python\\Trader')
sys.path.append('C:\\Users\\zinex\\anaconda3\\Lib\\site-packages')
import requests
import numpy as np
import json
from kucoinKeys import sandbox_keys as keys
from kucoin.client import Client


api_key = keys['apiKey']
api_secret = keys['apiSecret']
api_passphrase = keys['apiPassphrase']

#Currencies we will be trading
ticker1 = 'BTC'
ticker2 = 'USDT'
orderID = 0

sandbox_url = 'https://openapi-sandbox.kucoin.com'
account_ext = '/api/v1/accounts'
histories_ext = '/api/v1/market/histories'
orders_ext = '/api/v1/orders'
ledgers_ext = '/api/v1/accounts/ledgers'


def account_balance_value(ticker):
    amount = get_coin_balance(ticker, total_balance=True)
    value = float(amount) * float(user.get_ticker(ticker+'-USDT')['price'])
    return(value)

def get_coin_balance(ticker, total_balance=False):
    response = user.get_accounts()
    for elem in response:
        if elem['currency'] == ticker and elem['type'] == 'trade':
            if not total_balance:
                return elem['available']
            else:
                return elem['balance']

def main():
    global orderID
    orderID += 1 #Increase order number every time main loop executes
    print('Order ID: ', orderID)
    total_account_value = get_coin_balance('USDT')
    btc_balance = get_coin_balance('BTC')
    #print('BTC: ', btc_balance)
    print(account_balance_value('USDT'))
    usdt_balance = get_coin_balance('USDT')
    #print('USDT: ', usdt_balance)
    #print(btc_balance, usdt_balance)


user = Client(api_key, api_secret, api_passphrase, sandbox=True)

main()
#print(user.get_account('6079d3dad48f800006c03bdc'))
