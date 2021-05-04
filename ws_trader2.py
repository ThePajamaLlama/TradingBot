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
from matplotlib import pyplot as plt

from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
from kucoinKeys import sandbox_keys as keys


base_url = 'https://api.kucoin.com'#'https://openapi-sandbox.kucoin.com'

api_key = keys['apiKey']
api_secret = keys['apiSecret']
api_passphrase = keys['apiPassphrase']
#get historical data for 20 candle sticks

ticker_span = 100
client = Client(api_key, api_secret, api_passphrase, sandbox=False)
now = int(time.time())
kline_data = np.array(client.get_kline_data('BTC-USDT', '1min', (now - ticker_span*60), now))
historical_data = pd.DataFrame(kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])

#print(historical_data)
print("Last Time Stamp: ", historical_data.loc[0, 'TimeStamp'])
print("Current unixtimestamp: ", time.time())

async def return_EMA_data(data_set, period=10):
    closing_price = []
    for items in reversed(list(data_set.loc[:,'Close'])):
        closing_price.append(float(items))#Gives a list
    var = np.array(closing_price)
    #var =  np.ndarray(shape=(len(closing_price)), buffer=np.array(closing_price))
    ema = np.flip(talib.EMA(var, timeperiod=period))
    return(ema)

async def return_SMA_data(data_set, period=10):
    closing_price = []
    for items in reversed(list(data_set.loc[:,'Close'])):
        closing_price.append(float(items))#Gives a list
    var = np.array(closing_price)
    #var = np.ndarray(shape=(len(closing_price)), buffer=np.array(closing_price))
    sma = np.flip(talib.SMA(var, timeperiod=period))
    return(sma)

async def return_CLOSE_data(data_set):
    closing_price = []
    for items in reversed(list(data_set.loc[:,'Close'])):
        closing_price.append(float(items))#Gives a list
    return(np.flip(closing_price))

ema = return_EMA_data(historical_data, period=10)
sma = return_SMA_data(historical_data, period=20)
cp = return_CLOSE_data(historical_data)


async def main(historical_data, kline_data, client):
    global loop
    global new_table
    new_table = False
    global candle_stick #Single array of all parameters we are interested in.
    candle_stick = kline_data[0]

    async def update_plot(fig, time, cp, sma, ema):
        fig.clf()
        plt.plot(time, cp)
        plt.plot(time, sma)
        plt.plot(time, ema)
        last_time_stamp = dt.time.fromtimestamp(time[0][0])
        plt.title('Last time stamp:%s'%last_time_stamp)
        plt.xlabel('Minutes Since T=0')
        plt.ylabel('Price')
        plt.legend(['CLOSE', 'SMA', 'EMA'])
        plt.show()

    async def update_stats(data):
        global kline_data
        global new_table
        kline_data[1:] = kline_data[:-1]; kline_data[0] = data
        new_table = True
        return(pd.DataFrame(kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume']))

    async def on_msg(msg):
        global historical_data
        global candle_stick
        if msg['topic'] == '/market/candles:BTC-USDT_1min':
            msg_ts = int(msg['data']['candles'][0]) #Socket time stamp
            cs_ts = int(candle_stick[0]) #previous kline time stamp we read
            if (msg_ts > cs_ts): #Indicates we are moving onto a new candle
                historical_data = await update_stats(candle_stick)
            candle_stick = msg['data']['candles'] #Update info on current kline
        else:
            print(msg) #implement error handling later lol

    sock_manager = await KucoinSocketManager.create(loop, client, on_msg)
    await sock_manager.subscribe('/market/candles:BTC-USDT_1min')
    print('Connection Secured at: ', time.time())
    fig = plt.figure()
    while True:
        if new_table:
            print('Current Timestamp at: ', time.time())
            print(historical_data)
            timeframe = list(int(x) for x in historical_data.loc[:, 'TimeStamp'])
            #time_data = np.array(timeframe)
            cp = await return_CLOSE_data(historical_data)
            sma = await return_SMA_data(historical_data, period = 20)
            ema = await return_EMA_data(historical_data, period = 20)
            await update_plot(fig, timeframe, cp, sma, ema)
            new_table = False
        await asyncio.sleep(2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(historical_data, kline_data, client))
    except KeyboardInterrupt:
        print('You quitter')

#Stamp potential buy or sell locations for the bot on the graph using plt.text(x, y, s, fontdict=None)
