from abc import ABC, abstractmethod
import backtrader as bt
import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import feedparser
import numpy as np
from datetime import datetime, timedelta


class SentimentTrader(bt.Strategy):
    def __init__(self, symbol, sentiment_threshold=0.01, hold_days=365):
        self.symbol = symbol
        self.sentiment_threshold = sentiment_threshold
        self.hold_days = hold_days
        self.hold_counter = 0
        self.order = None

    def get_sentiment(self):
        try:
            article = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.symbol}"
            feed = feedparser.parse(article)
            sentiments = [
                TextBlob(entry.title + " " + getattr(entry, 'summary', '')).sentiment.polarity
                for entry in feed.entries[:10]
            ]
            return sum(sentiments) / len(sentiments) if sentiments else 0
        except Exception as e:
            print(f"Sentiment error: {e}")
            return 0

    def generate_signal(self):
        score = self.get_sentiment()
        return 'buy' if score > self.sentiment_threshold else 'hold'

    def next(self):
        if self.order:
            return

        signal = self.generate_signal()

        if self.position:
            self.hold_counter += 1
            if self.hold_counter >= self.hold_days:
                self.order = self.sell()
                print(f"Timed SELL at {self.data.close[0]}")
                self.hold_counter = 0
        elif signal == 'buy':
            self.order = self.buy()
            print(f"BUY at {self.data.close[0]}")
            self.hold_counter = 0

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    @staticmethod
    def prepare_backtrading(symbol, start_date='2023-01-01', end_date='2024-01-01'):
        data = yf.download(symbol, start=start_date, end=end_date)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns.values]
            print("Columns flattened")
        data = data.dropna()
        data.columns = [col.lower() for col in data.columns]
        if 'volume' in data.columns:
            data = data[data['volume'] > 0]
        return data

    

def run_strategy(strategy_type, symbol):
    data = strategy_type.prepare_backtrading(symbol)
    
    cerebro = bt.Cerebro()
    # Set initial cash and commission
    initial_cash = 10000.0  # Starting with $10,000
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)
    bt_data = bt.feeds.PandasData(dataname=data)
    print('=' * 50)
    print(f'Starting Portfolio Value: ${cerebro.broker.getvalue():.2f}')
    print(f'Starting Cash: ${cerebro.broker.getcash():.2f}')
    print('=' * 50)
    
    cerebro.adddata(bt_data)
    cerebro.addstrategy(strategy_type, symbol=symbol)
    
    
    # Run backtest
    print("Running backtest...")
    results = cerebro.run()
    
    # Get final values
    final_value = cerebro.broker.getvalue()
    final_cash = cerebro.broker.getcash()
    
    # Calculate performance metrics
    total_return = final_value - initial_cash
    return_percentage = (total_return / initial_cash) * 100
    
    # Print results
    print('=' * 50)
    print('BACKTEST RESULTS')
    print('=' * 50)
    print(f'Initial Cash: ${initial_cash:.2f}')
    print(f'Final Portfolio Value: ${final_value:.2f}')
    print(f'Final Cash: ${final_cash:.2f}')
    print(f'Total Return: ${total_return:.2f}')
    print(f'Return Percentage: {return_percentage:.2f}%')
    
    if total_return > 0:
        print(f'✅ PROFIT: You made ${total_return:.2f}!')
    else:
        print(f'❌ LOSS: You lost ${abs(total_return):.2f}')
    
    print('=' * 50)
    
    print("Generating plot...")
    cerebro.plot()

run_strategy(SentimentTrader, 'WDAY')

