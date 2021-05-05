#resources
#https://github.com/hoffstadt/DearPyGui/blob/master/DearPyGui/dearpygui/core.pyi
#https://github.com/hoffstadt/DearPyGui/wiki/Examples
#https://github.com/Pcothren/DearPyGui-Examples/blob/main/plots/cvs_to_plot_pandas.py

from dearpygui.core import *
from dearpygui.simple import *
import pandas as pd

def plot_callback(sender, data):
    file_path = "C:\\Users\\zinex\\Documents\\Python\\hist_data\\hist_data.cvs"
    data = pd.read_csv(file_path)
    print(data)
    time_data = list(int(x) for x in data.loc[:, 'TimeStamp'])
    print(time_data)
    opens = list(int(x) for x in data.loc[:, 'Open'])
    closes = list(int(x) for x in data.loc[:, 'Close'])
    highs = list(int(x) for x in data.loc[:, 'High'])
    lows = list(int(x) for x in data.loc[:, 'Low'])

    clear_plot("Plot")
    add_candle_series("Plot", dates=time_data, opens=opens, closes=closes, lows=lows, highs=highs)


set_main_window_size(800, 800)
with window(name='Main Window'):
    add_button("Plot Data", callback = plot_callback)
    add_plot("Plot", height=-1)

    # printing the widgets unique id
    id=add_button("Press me")
    print(id)

start_dearpygui(primary_window='Main Window')
