#This program is used to backtest
import sys
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

from ws_trader3 import Trader
from kucoinKeys import sandbox_keys as keys
minute = 60
hour = minute * 60
day = hour * 24
week = day * 7
bbb = Trader(api_key=keys['apiKey'], api_secret=keys['apiSecret'], api_passphrase=keys['apiPassphrase'], candle_points=1500, ticker_len = 15*minute, backtest=True)

export_file_path = "C:\\Users\\zinex\\Documents\\Python\\hist_data\\hist_data.cvs"
bbb.historical_data.to_csv(export_file_path, header=True, index=True)
#print(bbb.historical_data)
ts = np.array(object=list(int(x) for x in bbb.historical_data.loc[:, 'TimeStamp']))
cp = bbb.cp
sma = bbb.sma
ema = bbb.ema
print(shape(ts))
print(shape(cp))
plt.ion()
plt.plot(ts, cp)
plt.show()
