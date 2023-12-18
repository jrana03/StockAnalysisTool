import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates 
from mplfinance.original_flavor import candlestick_ohlc
import json #for testing with local data
import numpy as np
from tkinter import *
from tkinter.ttk import *
from bs4 import BeautifulSoup
import pandas_ta as ta
import os
import yfinance as yf
#symbol = (input("Enter a symbol: ")).upper()
#symbol = 'AAPL'
#print("Stock Selected: " + symbol)
function = 'TIME_SERIES_DAILY'

df = pd.DataFrame()

def timeSeriesVisualizations_closingPrice(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order
    #df_subset['Date'] = df_subset['Date'].apply(lambda x: np.datetime64(x))
    df_subset.plot.line(x='Date', y='Close', color="black") 

    #plt.xticks([])
    plt.xlabel('', fontsize=15)
    plt.legend().remove()
    plt.ylabel('Closing Price ($)')
    plt.title(f'Time Series Visualization')
    plt.show()

def volumeAnalysis(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order
    #df_subset['Date'] = df_subset['Date'].apply(lambda x: np.datetime64(x))

    #creating multiple plots
    fig, axes = plt.subplots(nrows=2, ncols=1)
    axes[0].set_title(f'Volume Analysis on Closing Prices')

    #showing closing prices as a scatter plot above the respective volume count
    df_subset.plot.line(x='Date', y='Close', ax=axes[0], color="black")

    #axes[0].set_xticks([])
    axes[0].set_xlabel('')
    axes[0].get_legend().remove()
    axes[0].set_ylabel('Closing Price ($)')

    df_subset.plot.bar(x='Date', y='Volume', ax=axes[1])
    axes[1].set_xticks([])
    axes[1].set_xlabel('')
    axes[1].get_legend().remove()
    axes[1].set_ylabel('Traded Volume')

    fig.tight_layout()
    plt.show()

def volatilityAnalysis(numDays):
    global df
    dailyreturns_arr = []
    num = int(numDays)
    df_subset = df[:num]
    for i in range(num):
        value = (df_subset.loc[i]['Close'] - df_subset.loc[i]['Open'])/df_subset.loc[i]['Open']
        dailyreturns_arr.append(value)
    
    df_subset.insert(6, 'Daily Return', dailyreturns_arr)
    df_subset = df_subset.iloc[::-1] #chronological order
    #df_subset['Date'] = df_subset['Date'].apply(lambda x: np.datetime64(x))

    df_subset['Date'] = df_subset['Date'].apply(mpl_dates.date2num)
    df_subset = df_subset.astype(float)

    fig, axes = plt.subplots(nrows=2)
    candlestick_ohlc(axes[0], df_subset.values, width=0.6, colorup='green', colordown='red', alpha=0.4)
    axes[0].set_title(f'Volatility Anaysis')
    #df_subset.plot.line(x='Date', y='Close', ax=axes[0])
    axes[0].set_xticks([])
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Price ($)')

    df_subset.plot.line(x='Date', y='Daily Return', ax=axes[1], color="black") 
    #axes[1].set_xticks([])
    axes[1].set_xlabel('')
    axes[1].get_legend().remove()
    axes[1].set_ylabel('Daily Return')
    axes[1].axhline(y=0.0, color='blue', linestyle='dashed')
    date_format = mpl_dates.DateFormatter('%m-%d-%Y') 
    axes[1].xaxis.set_major_formatter(date_format) 
    fig.autofmt_xdate()

    fig.tight_layout()
    plt.show()

def simpleMovingAverage(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order
    #df_subset['Date'] = df_subset['Date'].apply(lambda x: np.datetime64(x))
    day_size = 20

    windows = df_subset['Close'].rolling(day_size)
    moving_averages = windows.mean()
    df_subset.insert(6, 'Moving Averages', moving_averages) 
    df_subset.plot.line(x='Date', y='Close', label='Closing Prices', color='black')
    plt.plot(df_subset['Date'], df_subset['Moving Averages'], label='Moving Averages', color='blue')
    
    #plt.xticks([])
    plt.xlabel('', fontsize=15)
    plt.ylabel('Price ($)')
    plt.legend(['Closing Price', 'Moving Average'])
    plt.title(f'Simple Moving Average')
    plt.show()

def relativeStrengthIndex(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order

    df_subset.ta.rsi(append=True)

    df_subset['Date'] = df_subset['Date'].apply(mpl_dates.date2num)
    df_subset = df_subset.astype(float)

    fig, axes = plt.subplots(nrows=2)
    candlestick_ohlc(axes[0], df_subset.values, width=0.6, colorup='green', colordown='red', alpha=0.4)
    axes[0].set_title(f'Relative Strength Index')
    #df_subset.plot.line(x='Date', y='Close', ax=axes[0])
    axes[0].set_xticks([])
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Price ($)')
    date_format = mpl_dates.DateFormatter('%m-%d-%Y')
    axes[0].xaxis.set_major_formatter(date_format) 
    fig.autofmt_xdate() 

    df_subset.plot.line(x='Date', y='RSI_14', ax=axes[1], color="black")
    axes[1].set_xlabel('', fontsize=15)
    axes[1].set_ylabel('RSI')
    axes[1].axhline(y=70.0, color='red', linestyle='dashed')
    axes[1].axhline(y=30.0, color='green', linestyle='dashed')
    axes[1].get_legend().remove()
    date_format = mpl_dates.DateFormatter('%m-%d-%Y') 
    axes[1].xaxis.set_major_formatter(date_format) 
    fig.autofmt_xdate()
    plt.show()

def MACD(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order

    shortterm_period = 12
    longterm_period = 26

    # Calculate the Short-Term EMA (Exponential Moving Average)
    short_ema = df_subset['Close'].ewm(span=shortterm_period, adjust=False).mean()
    # Calculate the Long-Term EMA (Exponential Moving Average)
    long_ema = df_subset['Close'].ewm(span=longterm_period, adjust=False).mean()
    macd_line = short_ema-long_ema
    signal_period = 9
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd_line-signal_line
    df_subset['MACD Line'] = macd_line
    df_subset['Signal Line'] = signal_line
    df_subset['MACD Histogram'] = macd_histogram

    #changing date fromat to float format
    df_subset['Date'] = df_subset['Date'].apply(mpl_dates.date2num)
    df_subset = df_subset.astype(float)

    fig, axes = plt.subplots(nrows=2)
    candlestick_ohlc(axes[0], df_subset.values, width=0.6, colorup='green', colordown='red', alpha=0.4)
    axes[0].set_title(f'MACD')
    #df_subset.plot.line(x='Date', y='Close', ax=axes[0])
    axes[0].set_xticks([])
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Price ($)')
    date_format = mpl_dates.DateFormatter('%m-%d-%Y')
    axes[0].xaxis.set_major_formatter(date_format) 
    fig.autofmt_xdate() 

    x = df_subset['Date']
    y1 = df_subset['MACD Line']
    y2 = df_subset['Signal Line']
    y3 = df_subset['MACD Histogram']
    axes[1].plot(x, y1, label="MACD")
    axes[1].plot(x, y2,label="Signal Line", linestyle='dashed')

    #graphing the histo
    colours = ['green' if x >= 0 else 'red' for x in df_subset['MACD Histogram']]
    axes[1].bar(x, y3, color=colours)
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('MACD & Histogram Value')
    #axes[1].set_title('Multiple Data Values in Subplot')
    axes[1].legend(['MACD', 'Signal Line'])
    date_format = mpl_dates.DateFormatter('%m-%d-%Y') 
    axes[1].xaxis.set_major_formatter(date_format) 
    axes[1].axhline(y=0.0, color='black', linestyle='dashed')
    fig.autofmt_xdate()
    

    fig.tight_layout()
    plt.show()

def ai_Analysis(numDays):
    global df
    num = int(numDays)
    df_subset = df[:num]
    df_subset = df_subset.iloc[::-1] #chronological order

    # Calculate technical indicators using pandas-ta
    df_subset.ta.macd(append=True)
    df_subset.ta.rsi(append=True)

    # Calculate additional technical indicators
    df_subset.ta.sma(length=20, append=True)
    df_subset.ta.ema(length=50, append=True)

    df_subset.rename(columns={'MACD_12_26_9':'MACD', 'MACDh_12_26_9':'MACD Histogram', 'MACDs_12_26_9':'MACD Signal Line'}, inplace=True)

    global saved_symbol
    
    # Summarize technical indicators for the last day
    last_day_summary = df_subset.iloc[-1][['Close', 'MACD', 'MACD Histogram', 'RSI_14', 'SMA_20', 'EMA_50']]
    

    sys_prompt = """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors. \
    Your expertise extends to practical tools like the pandas_ta module, \
    allowing you to navigate data intricacies with ease. \
    As a TA authority, your role is to decipher market trends, make informed predictions, and offer valuable perspectives.

    given {} TA data as below on the last trading day, what will be the next few days possible stock price movement? 

    Summary of Technical Indicators for the Last Day:
    {}""".format(saved_symbol,last_day_summary.to_string())

    newWindow = Toplevel(root)
    newWindow.title("AI Prompt")
    newWindow.geometry('600x350')
    newWindow.title('Stock Analysis Tool')
    T = Text(newWindow, height=15, width=70, wrap=WORD)
    T.insert(END, sys_prompt)
    T.configure(state="disabled")

    Label(newWindow, text='Plese enter the following prompt into chatGPT: ', font=('Arial 14')).grid(row=0, sticky=W)
    T.grid(row=1, column=0)

    newWindow.mainloop()


root = Tk()
root.geometry('750x400')
root.title('Stock Analysis Tool')

#Setting up general labels for error checks
search_label=Label(root, text="")
search_label.grid(row=1, column=1, sticky=W)

data_label=Label(root, text="")
data_label.grid(row=2, column=1, sticky=W)


def searchData(event=None): #event for enter key binding below
    search_label.configure(text="Searching for stock...")
    #symbol_entry.configure(state="readonly")
    global saved_symbol
    saved_symbol = symbol_entry.get().upper()

    global df
    df = yf.download(saved_symbol)
    df = df.iloc[::-1]
    #capturing data
    #time_series = data['Time Series (Daily)']
    #df = pd.DataFrame.from_dict(time_series, orient='index')
    df = df.reset_index()
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    df['Volume'] = df['Volume'].astype(int)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Date'] = df['Date'].apply(lambda x: np.datetime64(x))
    if df.empty:
        data_label.configure(text=f"Could not import for {saved_symbol}. Please check console for error.")
    else:
        #enabling fields & buttons
        time_entry.configure(state="enabled")
        timesseries_button.configure(state="enabled")
        volume_analysis_button.configure(state="enabled")
        volat_analysis_button.configure(state="enabled")
        sma_button.configure(state="enabled")
        rsi_button.configure(state="enabled")
        macd_button.configure(state="enabled")
        aiprompt_button.configure(state="enabled")
        data_label.configure(text=f"Successfully imported for {saved_symbol}.")

#creating stock search frame
choices_frame = LabelFrame(root, text="Please enter a symbol below")
choices_frame.grid(row=0, sticky=W)

#search for symbol
Label(choices_frame, text='Symbol: ').grid(row=0, sticky=W)
symbol_entry = Entry(choices_frame)
symbol_entry.grid(row=0, column=1, sticky=W)
search_button = Button(choices_frame, text = 'Search', command=searchData)
search_button.grid(row=0, column=2)

root.bind('<Return>', searchData)

#time selection frame
time_selec_frame = LabelFrame(root, text="Please select the number of years")
time_selec_frame.grid(row=1, sticky=W)

Label(time_selec_frame, text="Years:").grid(row=0, sticky=W)
default_val = "1"
default_entry_val = StringVar()
default_entry_val.set(default_val)
time_entry = Entry(time_selec_frame, textvariable=default_entry_val, state="disabled")
time_entry.grid(row=1, column=0, sticky=W)

#data analysis frame
data_analysis_frame = LabelFrame(root, text="Data Analysis")
data_analysis_frame.grid(row=2, sticky=W)

timesseries_button = Button(data_analysis_frame, text = 'Time Series Visualization', command=lambda: timeSeriesVisualizations_closingPrice(float(time_entry.get())*365), state="disabled")
timesseries_button.grid(row=0, column=0, sticky=W)

volume_analysis_button = Button(data_analysis_frame, text = 'Volume Analysis', command=lambda: volumeAnalysis(float(time_entry.get())*365), state="disabled")
volume_analysis_button.grid(row=1, column=0, sticky=W)

volat_analysis_button = Button(data_analysis_frame, text = 'Volatility Analysis', command=lambda: volatilityAnalysis(float(time_entry.get())*365), state="disabled")
volat_analysis_button.grid(row=2, column=0, sticky=W)

#technical analysis frame
tech_analysis_frame = LabelFrame(root, text="Technical Analysis")
tech_analysis_frame.grid(row=3, sticky=W)

sma_button = Button(tech_analysis_frame, text="Simple Moving Average", command=lambda: simpleMovingAverage(float(time_entry.get())*365), state="disabled")
sma_button.grid(row=0, sticky=W)

rsi_button = Button(tech_analysis_frame, text="Relative Strength Index", command=lambda: relativeStrengthIndex(float(time_entry.get())*365), state="disabled")
rsi_button.grid(row=1, sticky=W)

macd_button = Button(tech_analysis_frame, text="MACD", command=lambda: MACD(float(time_entry.get())*360), state="disabled")
macd_button.grid(row=2, sticky=W)

aiprompt_button = Button(tech_analysis_frame, text="Generate AI Prompt", command=lambda: ai_Analysis(float(time_entry.get())*360), state="disabled")
aiprompt_button.grid(row=3, sticky=W)

root.mainloop()