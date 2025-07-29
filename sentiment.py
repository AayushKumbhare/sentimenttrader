from abc import ABC, abstractmethod
import backtrader as bt
import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import feedparser
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import hashlib
import os

load_dotenv()

SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
supabase : Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SentimentTrader(bt.Strategy):
    def __init__(self, symbol, portfolio_id, sentiment_threshold=0.01, hold_days=365):
        self.symbol = symbol
        self.sentiment_threshold = sentiment_threshold
        self.hold_days = hold_days
        self.hold_counter = 0
        self.order = None
        self.db = TraderDatabase()
        self.portfolio_id = portfolio_id

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
                self.db.execute_sell_order(
                    self.portfolio_id,
                    self.symbol,
                    self.position.size,
                    self.data.close[0]
                )
                print(f"Timed SELL at {self.data.close[0]}")
                self.hold_counter = 0
        elif signal == 'buy':
            self.order = self.buy()
            self.db.execute_buy_order(
                self.portfolio_id, 
                self.symbol, 
                self.position.size, 
                self.data.close[0]
                )
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

    
class TraderDatabase():
    def __init__(self):
        self.supabase = supabase

    def create_user(self, email, password):
        try:
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            
            user_info = {
                'email': email,
                'password_hash': hashed_pass,
                'created_at': datetime.now()
            }

            result = supabase.table('users').insert(user_info).execute()
            user_id = result.data[0]['user_id']
            print(f"Created user with user_id {user_id}")
            return user_id
        except Exception as e:
            print(f"Failed creating user. Error: {e}")


    def get_user_by_email(self, email):
        try:
            result = supabase.table('users').select('*').eq('email', email).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                print(f"No user with email: {email}")
                return None
        except Exception as e:
            print(f"Failed getting user with email: {email}")
            return None
        
    def get_user_by_id(self, user_id):  
        try:
            result = supabase.table('users').select('*').eq('user_id', user_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                print(f"No user with user_id: {user_id}")
                return None
        except Exception as e:
            print(f"Failed getting user with user_id: {user_id}")
            return None
        
    def create_portfolio(self, email, name, cash_balance, created_at):
        try:
            user = self.get_user_by_email(email)
            if not user:
                print(f"No user found with email: {email}")
            user_id = user['user_id']
            portfolio_info = {
                'user_id': user_id,
                'name' : name,
                'cash_balance': cash_balance,
                'created_at': datetime.now()
            }
            result = supabase.table('portfolios').insert(portfolio_info).execute()
            print(f"Portfolio {name} with cash balance ${cash_balance} created successfully")
            return result.data[0]
        except Exception as e:
            print(f"Error making portfolio {name}: {e}")
            return None
        
    def get_user_portfolios(self, email):
        try:
            user = self.get_user_by_email(email)
            if not user:
                print(f"No users found with email: {email}")
                return None
            user_id = user['user_id']

            result = supabase.table('portfolios').select('*').eq('user_id', user_id).execute()
            for portfolio in result:
                print(f"Retrieved Portfolio {portfolio['name']}")
            return result.data
        except Exception as e:
            print(f"Error getting portfolios for {email}: {e}")
            return None
        
    def update_portfolio_cash(self, cash_value):
        pass

    def get_portfolio_holdings(self):
        pass

    def add_stock(self, symbol):
        try:
            result = supabase.table('watchlist').insert({
                'symbol': symbol,
                'added_at': datetime.now()
            })
            print(f"Added stock {symbol} to watchlist")
            return result.data[0]
        except Exception as e:
            print(f"Error adding stock {symbol} to watchlist: {e}")
            return None
            
    def remove_stock(self, symbol):
        try:
            result = supabase.table('watchlist').delete().eq('symbol', symbol).execute()
            print(f"Removed stock {symbol} from watchlist")
            return result.data[0]
        except Exception as e:
            print(f"Error removing stock {symbol} from watchlist: {e}")

    def execute_buy_order(self, portfolio_id, symbol, quantity, price):
        try:
            transaction_result = supabase.table('transactions').insert({
                'portfolio_id': portfolio_id,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'tx_type': 'buy',
                'timestamp': datetime.now()
            }).execute()
            print(f"BUY transaction recorded for {symbol}")
            return transaction_result.data
        except Exception as e:
            print(f"Error updating buy transaction: {e}")
            return None
        
    def execute_sell_order(self, portfolio_id, symbol, quantity, price):
        try:
            transaction_result = supabase.table('transactions').insert({
                'portfolio_id': portfolio_id,
                'symbol': symbol,
                'quantity': -quantity,
                'price': price,
                'tx_type': 'sell',
                'timestamp': datetime.now()
            }).execute()
        except Exception as e:
            print(f"Error updating sell transaction: {e}")
            return None
    
def run_strategy(strategy_type, symbol, portfolio_id):
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
    cerebro.addstrategy(strategy_type, symbol=symbol, portfolio_id=portfolio_id)
    
    
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

