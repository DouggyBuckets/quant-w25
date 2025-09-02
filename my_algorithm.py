import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class algorithm:
    portfolio = 0
    cash = 1000000
    start_date = "2024-5-01" # to be determined
    end_date = "2024-11-01"  # to be determined
    NASDAQ = "^IXIC"
    market_ticker = yf.download(NASDAQ, start_date, end_date, progress = False)
    fourteen_day_ma = []
    trades = []
    portfolio_vals = []

    def __init__(self, tick):
        self.ticker_symbols = tick
        self.ticker = yf.download(self.ticker_symbols, self.start_date, self.end_date, progress=False)
        return

    def buy(self, tick, day):
        price_on_day = self.ticker.loc[day]["Close"].iloc[-1]

        buy_amt = self.cash / price_on_day
        self.portfolio += buy_amt
        self.cash -= buy_amt * price_on_day

        if buy_amt != 0:
            data = {tick, int(buy_amt), day}
            self.trades.append(data)

    def sell(self, tick, day): 
        price_on_day = self.ticker.loc[day]["Close"].iloc[-1]

        sell_amt = self.portfolio
        self.portfolio -= sell_amt
        self.cash += sell_amt * price_on_day

        if sell_amt != 0:
            data = {tick, -int(sell_amt), day}
            self.trades.append(data)
    
    def getCurrVal(self, day):
        price_on_day = self.ticker.loc[day]["Close"].iloc[-1]
        portfolio_val = price_on_day*self.portfolio + self.cash
        return int(portfolio_val)

    def decide(self, tick, day):
        breakout_period = 20 # we evaluate thresholds for breakout over last 20 days
        df = self.ticker.copy() # df = df[['Close', 'High', 'Low', 'Volume']]
        df['Upper_bound'] = df['High'].shift(1).rolling(window=breakout_period).max()
        df['Lower_bound'] = df['Low'].shift(1).rolling(window=breakout_period).min()
        df['LB_volume'] = df['Volume'].shift(1).rolling(window=breakout_period).mean()

        if df.index.get_loc(day) <= breakout_period:
            return
        
        row = df.loc[day]
        close = row['Close']
        volume = row['Volume']
        upper = row['Upper_bound']
        lower = row['Lower_bound']
        lb_vol = row['LB_volume']

        # Perform the comparison if all values are valid
        if close.iloc[0] > upper.iloc[0] and volume.iloc[0] > lb_vol.iloc[0]:
            self.buy(tick, day)
        elif close.iloc[0] < lower.iloc[0] or volume.iloc[0] < lb_vol.iloc[0]:
            self.sell(tick, day)

        self.portfolio_vals.append(self.getCurrVal(day))