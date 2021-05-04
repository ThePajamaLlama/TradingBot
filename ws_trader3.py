#resources
#https://www.unixtimestamp.com/
#https://code.tutsplus.com/tutorials/create-a-algorithm-trading-robot-the-basics-of-writing-a-expert-advisor-in-mql4--cms-27984
#https://docs.kucoin.cc/#apply-connect-token
#https://stackoverflow.com/questions/64757209/how-to-stop-asyncio-loop-with-multiple-tasks
#cd C:\Users\Luis\Documents\Python Projects\SelfProjects\TradingBot
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

    new_table = False
    SMA_PERIOD = 20
    EMA_PERIOD = 10

    def __init__(self, api_key=None, api_secret=None, api_passphrase=None, ticker_span=100):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.client = Client(api_key, api_secret, api_passphrase, sandbox=False)
        self.ticker_span = ticker_span #Number of candlestick data points to acquire
        self.kline_data = [] #
        self.historical_data = []
        now = int(time.time())
        self.kline_data = np.array(self.client.get_kline_data('BTC-USDT', '1min', (now - self.ticker_span*60), now))
        self.historical_data = pd.DataFrame(self.kline_data,
                            columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])
        self.candle_stick = self.kline_data[0] #Most recenr candle stick info
        self.update_indicators()

    def update_indicators(self): #Call this to update the CP, SMA, and EMA arrays
        self.get_cp()
        self.get_sma()
        self.get_ema()
        return self.cp, self.sma, self.ema


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

def update_plot(fig, time, cp, sma, ema):
    fig.clf()
    plt.plot(time, cp)
    plt.plot(time, sma)
    plt.plot(time, ema)
    plt.xlabel('Minutes Since T=0')
    plt.ylabel('Price')
    plt.legend(['CLOSE', 'SMA', 'EMA'])
    plt.draw()
    plt.pause(.001)
    plt.show(block=False)

async def main():
    global loop
    #global historical_data
    #global kline_data
    #global client
    #global new_table
    #new_table = False
    #global candle_stick #Single array of all parameters we are interested in.
    #candle_stick = kline_data[0]

    async def update_stats(data):
        #global kline_data
        #global new_table
        bot.kline_data[1:] = bot.kline_data[:-1]; bot.kline_data[0] = data
        bot.new_table = True
        bot.historical_data = pd.DataFrame(kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])

    async def on_msg(msg):
        #global historical_data
        #global candle_stick
        if msg['topic'] == '/market/candles:BTC-USDT_1min':
            msg_ts = int(msg['data']['candles'][0]) #Socket time stamp
            cs_ts = int(bot.candle_stick[0]) #previous kline time stamp we read
            if (msg_ts > cs_ts): #Indicates we are moving onto a new candle #Try changing to == rather than >
                #bot.historical_data = await update_stats(bot.candle_stick)
                await update_stats(bot.candle_stick)
            bot.candle_stick = msg['data']['candles'] #Update info on current kline
        else:
            print(msg) #implement error handling later lol

    sock_manager = await KucoinSocketManager.create(loop, bot.client, on_msg)
    await sock_manager.subscribe('/market/candles:BTC-USDT_1min')
    print('Connection Secured at: ', time.time())
    #fig = plt.figure()
    #plt.ion()
    #time_data = np.array(object=list(int(x) for x in bot.historical_data.loc[:, 'TimeStamp']))
    #cp, sma, ema = bot.update_indicators()
    #update_plot(fig, time_data[:-20], cp[:-20], sma[:-20], ema[:-20])

    while True:
        if bot.new_table:
            print('Current unixtimestamp: ', time.time())
            print(bot.historical_data)
            time_data = np.array(object=list(int(x) for x in bot.historical_data.loc[:, 'TimeStamp']))
            cp, sma, ema = bot.update_indicators()
            df = pd.DataFrame([[time_data], [cp], [sma], [ema]], columns=['TimeStamp', 'Closing', 'SMA', 'EMA'])
            print(df)
            #print('CP', cp)
            #print('SMA', sma)
            #print('EMA', ema)
            #update_plot(fig, time_data[:-20], cp[:-20], sma[:-20], ema[:-20])
            bot.new_table = False
        await asyncio.sleep(1)



api_key = keys['apiKey']
api_secret = keys['apiSecret']
api_passphrase = keys['apiPassphrase']
#get historical data for 20 candle sticks

bot = Trader(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)
#print(historical_data)
print("Last Time Stamp: ", bot.historical_data.loc[0, 'TimeStamp'])
print("Current unixtimestamp: ", time.time())
#print('CP', bot.cp)
#print('SMA', bot.sma)
#print('EMA', bot.ema)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('You quitter')
