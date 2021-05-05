#resources
#https://www.unixtimestamp.com/
#https://code.tutsplus.com/tutorials/create-a-algorithm-trading-robot-the-basics-of-writing-a-expert-advisor-in-mql4--cms-27984
#https://docs.kucoin.cc/#apply-connect-token
#https://stackoverflow.com/questions/64757209/how-to-stop-asyncio-loop-with-multiple-tasks
#cd C:\Users\Luis\Documents\Python Projects\SelfProjects\TradingBot

"""
New variation will accumilate all datapoints as they pass rather than limit it to 100.
    Later:
        Upon exit, we will save data to CSV so we can pick up where we left off when we run again.
        We will check last time stamp saved and request all data beyond that point to present day
        This will let us keep track of the trades we make so we can plot them long with the candles and MA

send sandbox keys for phonenumber account to work, we should only be using one pair of sandbox and real keys
"""

import sys
import time
import datetime as dt
import asyncio
import nest_asyncio
nest_asyncio.apply()
import talib
import pandas as pd
import numpy as np
import matplotlib
#%matplotlib notebook
matplotlib.interactive(True)
from matplotlib import pyplot as plt
from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
from kucoinKeys import sandbox_keys as keys

class Trader:
    coin1 = 'BTC'
    coin2 = 'USDT'
    ticker = coin1 + '-' + coin2
    cs_length = '1min'
    subscription_url = '/market/candles:{0}_{1}'.format(ticker, cs_length)
    new_table = False
    SMA_PERIOD = 20
    EMA_PERIOD = 10

    def __init__(self, api_key=None, api_secret=None, api_passphrase=None, ticker_span=100):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.client = Client(api_key, api_secret, api_passphrase, sandbox=True)
        self.ticker_span = ticker_span #Number of candlestick data points to acquire
        self.kline_data = []
        self.historical_data = []
        now = int(time.time())
        self.kline_data = np.array(self.client.get_kline_data(self.ticker, self.cs_length, (now - self.ticker_span*60), now))
        self.historical_data = pd.DataFrame(self.kline_data,
                            columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])
        self.candle_stick = self.kline_data[0] #Most recenr candle stick info
        self.update_indicators()
        self.user_accounts = self.client.get_accounts()
        print(self.user_accounts)
        self.init_wallets()


    def update_indicators(self): #Call this to update the CP, SMA, and EMA arrays
        self.get_cp()
        self.get_sma()
        self.get_ema()
        return self.cp, self.sma, self.ema

    def init_wallets(self):
        try:
            for account in self.user_accounts:
                if account['type'] == 'trade':
                    if account['currency'] == coin1:
                        self.coin1_id = account['id']
                        self.coin1_balance = int(account['balance'])
                    elif account['currency'] == coin2:
                        self.coin2_balance = int(account['balance'])
                        self.coin2_id = account['id']
                    else:
                        pass
        except:
            print('Could no retrieve desired account balances')
        return self.coin1_balance, self.coin1_id, self.coin2_balance, self.coin2_id


    def get_ema(self, period=EMA_PERIOD):
        closing_price = []
        for items in reversed(list(self.historical_data.loc[:,'Close'])):
            closing_price.append(float(items))#Gives a list
        var =  np.array(closing_price)
        self.ema = np.flip(talib.EMA(var, timeperiod=period)).tolist()

    def get_sma(self, period=SMA_PERIOD):
        closing_price = []
        for items in reversed(list(self.historical_data.loc[:,'Close'])):
            closing_price.append(float(items))#Gives a list
        var =  np.array(closing_price)
        self.sma = np.flip(talib.SMA(var, timeperiod=period)).tolist()

    def get_cp(self):
        closing_price = []
        for items in reversed(list(self.historical_data .loc[:,'Close'])):
            closing_price.append(float(items))#Gives a list
        self.cp = np.flip(closing_price).tolist()

    def get_coin_balance(self, coin):
        pass

def update_plot(fig, time, cp, sma, ema):
    fig.clf()
    plt.plot(time, cp)
    plt.plot(time, sma)
    plt.plot(time, ema)
    plt.xlabel('Minutes Since T=0')
    plt.ylabel('Price')
    plt.legend(['CLOSE', 'SMA', 'EMA'])
    plt.draw()
    plt.pause(10)
    #plt.show()

def trade_logic(hist_data, indicators): #takes historical_data (pd.DataFrame) and indicators (dictionary of indicators) (list of ints)
    decision = {
        'Buy' : False,
        'Sell' : False,
        'Amount' : 0
    }

    return decision


async def main():
    global loop

    async def update_stats(data):
        bot.kline_data = np.insert(bot.kline_data, 0, data, axis=0)
        bot.new_table = True
        bot.historical_data = pd.DataFrame(bot.kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])

    async def on_msg(msg):
        if msg['data']['symbol'] == bot.ticker:
            msg_ts = int(msg['data']['candles'][0]) #Socket time stamp
            cs_ts = int(bot.candle_stick[0]) #previous kline time stamp we read
            if (msg_ts > cs_ts): #Indicates we are moving onto a new candle #Try changing to == rather than >
                await update_stats(bot.candle_stick)
            bot.candle_stick = msg['data']['candles'] #Update info on current kline
        else:
            print(msg) #implement error handling later lol

    bot = Trader(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)
    print("Last Time Stamp: ", bot.historical_data.loc[0, 'TimeStamp'])
    print("Current unixtimestamp: ", time.time())

    sock_manager = await KucoinSocketManager.create(loop, bot.client, on_msg)
    await sock_manager.subscribe(bot.subscription_url)
    print('Connection Secured at: ', time.time())
    print(bot.historical_data)
    print('{0} Wallet Balance: {1}, Acc ID: {2}'.format(bot.coin1, bot.coin1_balance, bot.coin1_id))
    print('{0} Wallet Balance: {1}, Acc ID: {2}'.format(bot.coin2, bot.coin1_balance, bot.coin1_id))

    while True:
        if bot.new_table:
            print('Current unixtimestamp: ', time.time())
            print(bot.historical_data)
            time_data = np.array(object=list(int(x) for x in bot.historical_data.loc[:, 'TimeStamp']))
            cp, sma, ema = bot.update_indicators()
            indicators = {'TimeStamp':time_data, 'Closing':cp, 'SMA': sma, 'EMA': ema}
            indicator_df = pd.DataFrame(indicators)
            print(indicator_df)
            #decision = trade_logic(bot.historical_data, indicators) #returns dictionary with 'Buy', 'Sell', 'Amount' that gets passed into a function which executes trade
            #execute_trade(decision)
            #export_file_path = "C:\\Users\\zinex\\Documents\\Python\\hist_data\\hist_data.cvs"
            #bot.historical_data.to_csv(export_file_path, header=True, index=False)
            bot.new_table = False
        await asyncio.sleep(1)


api_key = keys['apiKey']
api_secret = keys['apiSecret']
api_passphrase = keys['apiPassphrase']

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('You quitter')
        sys.exit(0)
