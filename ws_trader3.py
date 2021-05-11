#resources
#https://www.unixtimestamp.com/
#https://code.tutsplus.com/tutorials/create-a-algorithm-trading-robot-the-basics-of-writing-a-expert-advisor-in-mql4--cms-27984
#https://docs.kucoin.cc/#apply-connect-token
#https://stackoverflow.com/questions/64757209/how-to-stop-asyncio-loop-with-multiple-tasks
#cd C:\Users\Luis\Documents\Python Projects\SelfProjects\TradingBot
#https://towardsdatascience.com/making-a-trade-call-using-simple-moving-average-sma-crossover-strategy-python-implementation-29963326da7a


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
    symbol1 = 'BTC'
    symbol2 = 'USDT'
    ticker = symbol1 + '-' + symbol2
    cs_length = '1min'
    subscription_url = '/market/candles:{0}_{1}'.format(ticker, cs_length)
    new_table = False
    SMA_PERIOD = 20
    EMA_PERIOD = 10

    #Lets make some variables if we want to change the length of a candle
    minute = 60
    hour = 60 * minute
    day = hour * 24

    #candle_points
    def __init__(self, api_key=None, api_secret=None, api_passphrase=None, candle_points=100, ticker_len = minute, backtest=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.client = Client(api_key, api_secret, api_passphrase, sandbox=True)
        self.backtest = backtest
        #self.kline_data = []
        #self.historical_data = []
        self.candle_points = candle_points #Number of candlestick data points to acquire
        now = int(time.time())
        #Kline data is a list of candle stick info. Each element contains timestamp, open, close, high, low, tx amount and tx volume
        self.kline_data = np.array(self.client.get_kline_data(self.ticker, self.cs_length, (now - self.candle_points*ticker_len), now))
        #historical data is the pandas datafram version of klin_data. Use to access column sof values like just time, or open price
        self.historical_data = pd.DataFrame(self.kline_data,
                            columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])
        self.update_indicators()
        self.user_accounts = self.client.get_accounts()
        self.list_of_trades = []

        class Coin:
            def __init__(self, symbol):
                self.symbol = symbol
                self.balance = 0
                self.available = 0
                self.id = ''

        self.coin1 = Coin(symbol=self.symbol1)
        self.coin2 = Coin(symbol=self.symbol2)


    def update_indicators(self): #Call this to update the CP, SMA, and EMA arrays
        self.get_cp()
        self.get_sma()
        self.get_ema()
        return self.cp, self.sma, self.ema

    def update_wallet(self, coin, amount=0):
        if self.backtest:
            if abs(amount) > 0:
                #Amount should be positive for buys, negative for sells
                if amount > 0:
                    print('Adding {0} to {1} wallet...'.format(amount, coin.symbol))
                else:
                    print('Deducting {0} from {1} wallet...'.format(amount, coin.symbol))
                coin.available = coin.available + amount
                coin.balance = coin.available
            else:
                return coin.available
        else:
            acc = coin.id
            account = self.client.get_account(acc)
            coin.available = float(account['available'])
        print('{0} Wallet Balance: {1}'.format(coin.symbol, coin.balance))
        return coin.available


    def init_wallets(self, coin1=symbol1, coin2=symbol2):
        try:
            for account in self.user_accounts:
                if account['currency'] == coin1:
                    if account['type'] == 'trade':
                        self.coin1.id = account['id']
                        self.coin1.available = float(account['available'])
                        self.coin1.balance = float(account['balance'])
                elif account['currency'] == coin2:
                    if account['type'] == 'trade':
                        self.coin2.balance = float(account['balance'])
                        self.coin2.available = float(account['available'])
                        self.coin2.id = account['id']
                else:
                    pass
            print('{0} Wallet Balance: {1} - Acc ID: {2}'.format(self.coin1.symbol, self.coin1.balance, self.coin1.id))
            print('{0} Wallet Balance: {1} - Acc ID: {2}'.format(self.coin2.symbol, self.coin2.balance, self.coin2.id))
        except Exception as e:
            print('ERROR:', e)
        #return self.coin1_balance, self.coin1_id, self.coin2_balance, self.coin2_id


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

    #def trade_logic(self, sma=self.sma[0], ema=self.ema[0], last_sma=self.sma[1], last_ema=self.ema[1]): #takes kline_df (pd.DataFrame) and indicators (dictionary of indicators) (list of ints)
    def trade_logic(self, indicators=None):
        #try:
        sma = indicators['SMA'][:3]
        ema = indicators['EMA'][:3]
        cp = indicators['Closing'][:3]
        ts = indicators['TimeStamp'][:3]
        print(f'SMA: {sma}\nEMA: {ema}\nCP: {cp}\nTimeStamp: {ts}')
        #trade logic should maximize coin1 amount.
        decision = {
            'Buy' : False,
            'Sell' : False,
            'Amount' : 0,
            'Price' : 0
        }
        up_multiplier = 0.0 #Use later to adjust the amount that we buy depending on strength of trend
        down_multiplier = 0.0

        tb = 0.0005 #Seted to define the tolerance at what price we want to buy or sell
        #implement stop_loss variable that is adjusted as price rises and falls
        #look into Part Time Larry Supertrend indicator
        self.update_wallet(coin=self.coin1)
        self.update_wallet(coin=self.coin2)
        price = cp[0] # COIN1 / COIN2 (BTC/USDT for example)
        decision['Price'] = price
        print(f"Percentage change: {(100*(ema[0]-sma[0])/sma[0]):.3f}%")
        #price = float(self.kline_data[0][3])
        #if ema above sma and ema-sma > 0.5% of sma: (don't waste a trade on a hairtriggerq)'
        #use numpy where: https://www.quantstart.com/articles/Backtesting-a-Moving-Average-Crossover-in-Python-with-pandas/
#        try:
        if self.backtest:
            if ema[0] > (1 + tb)*sma[0]:#EMA is 3% above SMA, place large BUY order
                if self.coin2.available > 0.01: #If we do not have a newar empty wallet. (CHANGE SO IT HAS TO BE GREATER THAN FEE, THEN IF IT PROFITABLE OR NOT)
                    decision['Buy'] = True
                    amount = (self.coin2.balance * 0.8)/price
                    if ema[1] >= sma[1]:
                        amount = amount * 0.6
                        if ema[2] >= (1 + tb)*sma[2]:
                            amount = amount * 0.5
                    decision['Amount'] = amount
                    print('Placing a BUY order for {}'.format(amount))
                else:
                    print('NOT ENOUGH FUNDS IN {} WALLET'.format(self.coin2.symbol))
            elif ema[0] < (1-tb)*sma[0]:
                if self.coin1.available * price > .01:#If we do not have a newar empty wallet. (CHANGE SO IT HAS TO BE GREATER THAN FEE, THEN IF IT PROFITABLE OR NOT)
                    decision['Sell'] = True
                    amount = self.coin1.balance
                    decision['Amount'] = amount #AMOUNT OF BTC BEING SOLD, NOT USDT
                    print(f'Placing a SELL order for {amount}')
                else:
                    print('NOT ENOUGH FUNDS IN {} WALLET'.format(self.coin1.symbol))
            #If we are running in a real market, try using market orders before using limit orders
            else:
                print('Nothing to do')
                pass
#        except Exception as e:
#            print('You dun fucked up')
#            print(e)
        self.execute_trade(decision, ts=ts[0])

    def execute_trade(self, decision, ts=None):
        try:
            price = decision['Price']
            amount = decision['Amount']
            if ts and self.backtest:
                #Gives index of timestamp of that datapoint
                #index = self.historical_data.loc[self.historical_data['TimeStamp'] == str(ts)].index[0]
                #price = self.historical_data.loc[index, 'Close']
                if decision['Buy']:
                    #self.coin1.balance += decision['Amount']
                    #self.coin2.balance -= decision['Amount']/decision['Price']
                    cb1 = self.update_wallet(self.coin1, amount=amount)
                    cb2 = self.update_wallet(self.coin2, amount=(-1)*(price*amount))
                    self.list_of_trades.append([ts, 'Buy', amount, price, cb1, cb2])
                elif decision['Sell']:
                    cb1 = self.update_wallet(self.coin1, amount=(-1)*amount)
                    cb2 = self.update_wallet(self.coin2, amount=price*amount)
                    self.list_of_trades.append([ts, 'Sell', amount, price, cb1, cb2])
        except Exception as e:
            print(e)
            print("Could not place order")
            #place limit or market order depending on trend
        print(decision)
        print('Trade Data')
        try:
            if len(self.list_of_trades) >= 1:
                print(self.list_of_trades[0])
                print(pd.DataFrame(data=np.array(self.list_of_trades.split()), columns=['TimeStamp', 'Side', 'BTCAmount', 'BTC' 'NetBTC', 'NetUSD']))
            else:
                print('No trades to list because some crazy shit happened')
        except Exception as e:
            print(f'No trades to list because {e}')

        print("{0} Balance: {1}".format(self.coin1.symbol, self.coin1.balance))
        print("{0} Balance: {1}".format(self.coin2.symbol, self.coin2.balance))

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
    #plt.show()


async def main():
    global loop

    async def update_stats(data):
        bot.historical_data = pd.DataFrame(bot.kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])
        bot.kline_data = np.insert(bot.kline_data, 0, data, axis=0)
        #Comment out line below if we want to keep all of our candle stick data rather than using sliding averages
        #bot.kline_data = np.delete(bot.kline_data, -1, 0)
        bot.update_indicators()
        bot.new_table = True

    async def on_msg(msg):
        if msg['data']['symbol'] == bot.ticker:
            msg_ts = int(msg['data']['candles'][0]) #Socket time stamp
            cs_ts = int(bot.kline_data[0][0]) #previous kline time stamp we read
            if (msg_ts > cs_ts): #Indicates we are moving onto a new candle #Try changing to == rather than >
                await update_stats(msg['data']['candles'])
            bot.kline_data[0] = msg['data']['candles']
            #print(bot.kline_data[:5]) #Update info on current kline
        else:
            print(msg) #implement error handling later lol

    bot = Trader(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase, candle_points=100)
    print("Last Time Stamp: ", bot.historical_data.loc[0, 'TimeStamp'])
    print("Current unixtimestamp: ", time.time())
    sock_manager = await KucoinSocketManager.create(loop, bot.client, on_msg)
    await sock_manager.subscribe(bot.subscription_url)
    print('Connection Secured at: ', time.time())
    #print(bot.historical_data)
    bot.init_wallets()
    plt.ion()

    while True:
        if bot.new_table:
            print('Current unixtimestamp: ', time.time())
            #print(bot.historical_data)
            """vvv ONLY FOR PRINTING AND GRAPHING vvv"""
            time_data = np.array(object=list(int(x) for x in bot.historical_data.loc[:, 'TimeStamp']))
            cp, sma, ema = bot.update_indicators()
            indicators = {'TimeStamp':time_data, 'Closing':cp, 'SMA': sma, 'EMA': ema}
            indicator_df = pd.DataFrame(indicators)
            #print(indicator_df)
            fig = plt.gcf()
            update_plot(fig, time_data, cp, sma, ema)
            """^^^ ONLY FOR PRINTING AND GRAPHING ^^^"""
            decision = bot.trade_logic(indicators) #returns dictionary with 'Buy', 'Sell', 'Amount' and 'Price' that gets passed into a function which executes trade
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
        sys.exit(1)
