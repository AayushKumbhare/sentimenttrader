from abc import ABC, abstractmethod
import backtrader as bt
import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import feedparser
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta


class BaseStrategy(ABC):
    def __init__(self, symbol, mode='backtest', alpaca_api=None):
        self.symbol = symbol
        self.mode = mode
        self.alpaca_api = alpaca_api
    
    @abstractmethod
    def generate_signal(self, data):
        pass

    def trade(self, signal, quantity):
        if self.mode == 'backtest':
            return self.execute_backtest(signal, quantity)
        

    def execute_backtest(self, signal, quantity):
        #implemented in backtesting functionality
        return {"status": "backtest logged", "signal": signal}



class SentimentBacktrader(bt.Strategy):
    def __init__(self):
        symbol = self.data._name
        self.sentiment_strategy = SentimentTrader(symbol=symbol, mode='backtest')

    def next(self):
        signal = self.sentiment_strategy.generate_signal()
        if signal == 'buy' and not self.position:
            self.buy()
        elif signal == 'sell' and self.position:
            self.sell()
        if len(self.data) == len(self.data.close):
            if self.position:
                self.close()
                print(f"{self.datetime.date(0)} | AUTO-CLOSED AT END OF BACKTESTING")

class SentimentTrader(BaseStrategy):
    def __init__(self, symbol, mode, alpaca_api=None, sentiment_threshold = 0.01):
        super().__init__(symbol, mode, alpaca_api)
        self.sentiment_threshold = sentiment_threshold

    def get_sentiment(self):
        try:
            article = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.symbol}"
            feed = feedparser.parse(article)

            sentiments =[]
            for entry in feed.entries[:10]:
                text = entry.title + " " + getattr(entry, 'summary', '')
                sentiment_score = TextBlob(text).sentiment.polarity
                sentiments.append(sentiment_score)
            if not sentiments:
                print(F"No news found for {self.symbol}")
                return 0
            
            print(f"Sentiment Score: {sum(sentiments)/len(sentiments)}")
            return sum(sentiments) / len(sentiments) if sentiments else 0
        except Exception as e:
            print(f"Error: {e}")
            return 0
        
    def generate_signal(self, data=None):
        score = self.get_sentiment()

        if score > self.sentiment_threshold:
            return 'buy'
        
        elif score < -self.sentiment_threshold:
            return 'sell'
        
        else:
            return 'hold'
        

def prepare_data(symbol, start_date='2023-01-01', end_date='2024-01-01'):
    """Download and prepare data for Backtrader"""
    print(f"Downloading data for {symbol}...")
    data = yf.download(symbol, start=start_date, end=end_date)
    
    print(f"Data type: {type(data)}")
    print(f"Original columns: {data.columns}")
    print(f"Data shape: {data.shape}")
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns.values]
        print(f"Flattened columns: {data.columns}")
    
    data.columns = [col.lower() for col in data.columns]
    print(f"Lowercase columns: {data.columns}")
    
    print(f"Before cleaning: {len(data)} rows")
    
    data = data.dropna()
    
    data = data.replace([float('inf'), float('-inf')], float('nan')).dropna()
    
    if 'volume' in data.columns:
        data = data[data['volume'] > 0]
    
    print(f"After cleaning: {len(data)} rows")
    print("Data ready for Backtrader!")
    
    return data

def run_strategy(strategy_type, symbol):
    data = prepare_data(symbol)
    
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
    cerebro.addstrategy(SentimentBacktrader)
    
    
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

# Test it
if __name__ == "__main__":
    run_strategy('sentiment', 'AAPL')




