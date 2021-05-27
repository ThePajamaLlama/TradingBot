#This program is used to backtest
import sys
import time
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

from ws_trader3 import Trader
from kucoinKeys import sandbox_keys as keys
minute = 60
hour = minute * 60
day = hour * 24
week = day * 7

now = time.time()

bbb = Trader(api_key=keys['apiKey'], api_secret=keys['apiSecret'], api_passphrase=keys['apiPassphrase'], candle_points=1500, ticker_len = 30*minute, cs_length='30min', backtest=True)
bbb.init_wallets(bbb.coin1.symbol, bbb.coin2.symbol)
#print(now)
#print(now  - bbb.candle_points*15*minute)
#print(now - 2*bbb.candle_points*15*minute)
#data  = bbb.client.get_kline_data(bbb.ticker, bbb.cs_length, now - 2*bbb.candle_points*15*minute, now  - bbb.candle_points*15*minute)
#print(data)
#bbb.kline_data = np.append(np.array(bbb.client.get_kline_data(bbb.ticker, bbb.cs_length, now - 2*bbb.candle_points*15*minute, now  - bbb.candle_points*15*minute)))
#bbb.historical_data = pd.DataFrame(bbb.kline_data, columns=['TimeStamp', 'Open', 'Close', 'High', 'Low', 'Tx Amount', 'Tx Volume'])
export_file_path = "C:\\Users\\zinex\\Documents\\Python\\hist_data\\hist_data.cvs"
bbb.historical_data.to_csv(export_file_path, header=True, index=True)
ts = list(int(x) for x in bbb.historical_data.loc[:, 'TimeStamp'])
op = bbb.op
cp = bbb.cp
sma = bbb.sma
ema = bbb.ema

for pos in range(len(ts) - 3):
    #print(f'POS: {pos}')
    indicators = {'Opening' : op[pos:pos+3],'Closing' : cp[pos:pos+3], 'EMA' : ema[pos:pos+3], 'SMA' : sma[pos:pos+3], 'TimeStamp' : ts[pos:pos+3]}
    bbb.trade_logic(indicators)

print(f'{bbb.coin1.symbol}: {bbb.coin1.available}')
print(f'{bbb.coin2.symbol}: {bbb.coin2.available}')
buys = [trade['Price'] for trade in bbb.list_of_trades if trade['Action'] == 'Buy']
buys_ts = [trade['TimeStamp'] for trade in bbb.list_of_trades if trade['Action'] == 'Buy']
sells = [trade['Price'] for trade in bbb.list_of_trades if trade['Action'] == 'Sell']
sells_ts = [trade['TimeStamp'] for trade in bbb.list_of_trades if trade['Action'] == 'Sell']
print(bbb.historical_data)
plt.plot(buys_ts, buys, 'b^')
plt.plot(sells_ts, sells, 'rv')
plt.plot(ts, cp, 'g--', linewidth=0.5)
plt.plot(ts, op, 'g', linewidth=0.5)
plt.plot(ts, sma)
plt.plot(ts, ema)
plt.legend(['Buys', 'Sells','Closing', 'Opening', 'SMA', 'EMA'])
plt.show(block=True)
