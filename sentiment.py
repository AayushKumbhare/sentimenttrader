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
from uuid import UUID
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
        self.portfolio_id = portfolio_id
        self.db = TraderDatabase()

    def get_sentiment(self):
        try:
            article = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.symbol}"
            feed = feedparser.parse(article)
            sentiments = [
                TextBlob(entry.title + " " + getattr(entry, 'summary', '')).sentiment.polarity
                for entry in feed.entries[:10]
            ]
            sentiment_score = sum(sentiments) / len(sentiments) if sentiments else 0
            print(f"Sentiment score for {self.symbol}: {sentiment_score:.4f}")
            return sentiment_score
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
                print(f"Timed SELL {self.position.size} shares at ${self.data.close[0]:.2f}")
                self.hold_counter = 0
                
        elif signal == 'buy':
            # Calculate position size based on available cash
            cash = self.broker.getcash()
            price = self.data.close[0]
            size = int(cash * 0.95 / price)  # Use 95% of available cash
            
            if size > 0:
                self.order = self.buy(size=size)
                self.db.execute_buy_order(
                    self.portfolio_id, 
                    self.symbol, 
                    size,
                    price
                )
                print(f"BUY {size} shares at ${price:.2f}")
                self.hold_counter = 0

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            if order.status == order.Completed:
                if order.isbuy():
                    print(f" BUY ORDER COMPLETED: {order.executed.size} shares at ${order.executed.price:.2f}")
                else:
                    print(f"✅ SELL ORDER COMPLETED: {order.executed.size} shares at ${order.executed.price:.2f}")
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
                'created_at': datetime.now().isoformat()
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
                'created_at': datetime.now().isoformat()
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
            for portfolio in result.data:
                print(f"Retrieved Portfolio {portfolio['name']}")
            return result.data
        except Exception as e:
            print(f"Error getting portfolios for {email}: {e}")
            return None
        
    def update_portfolio_cash(self, portfolio_id, cash_value):
        try:
            result = supabase.table('portfolios').update({
                'cash_balance': cash_value,
                'updated_at': datetime.now().isoformat()
            }).eq('portfolio_id', portfolio_id).execute()

            if result.data and len(result.data) > 0:
                print(f"Updated portfolio to hold: {cash_value}")
                return result.data[0]
            else:
                return None
        except Exception as e:
            print(f"Error updating portfolio: {portfolio_id}")
            return None
        
    def get_portfolio_holdings(self, portfolio_id):
        try:
            result = supabase.table('holdings').select('*').eq('portfolio_id', portfolio_id).execute()
            
            if result.data:
                holdings = {holding['symbol']: holding for holding in result.data}
                print(f"Retrieved {len(holdings)} holdings for portfolio {portfolio_id}")
                return holdings
            else:
                print(f"No holdings found for portfolio {portfolio_id}")
                return {}
                
        except Exception as e:
            print(f"Error getting holdings for portfolio {portfolio_id}: {e}")
            return {}
    
    def get_portfolio_by_id(self, portfolio_id):
        try:
            result = supabase.table('portfolios').select('*').eq('portfolio_id', portfolio_id).execute()
            if result.data:
                return result.data[0]
            else:
                print(f"No portfolio with id {portfolio_id} was found")
                return None
        except Exception as e:
            print(f'Error: {e}')
            return None
        
    def transactions_by_portfolio(self, portfolio_id):
        try:
            result = supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).execute()
            transaction_names = set()
            if result.data:
                for transaction in result.data:
                    transaction_names.add(transaction['symbol'])
                return transaction_names
            else:
                print(f"No transactions found in portfolio: {portfolio_id}")
                return set()  # Return empty set instead of None
        except Exception as e:
            print(f'Error: {e}')
            return set()
                

    def update_holding(self, portfolio_id, symbol, quantity, avg_price):
        """Update or create a holding entry"""
        try:
            # First, try to get existing holding
            existing = supabase.table('holdings').select('*').eq('portfolio_id', portfolio_id).eq('symbol', symbol).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing holding
                result = supabase.table('holdings').update({
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'updated_at': datetime.now().isoformat()
                }).eq('portfolio_id', portfolio_id).eq('symbol', symbol).execute()
                print(f"Updated holding: {symbol} - {quantity} shares at ${avg_price:.2f}")
            else:
                # Create new holding
                result = supabase.table('holdings').insert({
                    'portfolio_id': portfolio_id,
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'created_at': datetime.now().isoformat()
                }).execute()
                print(f"Created new holding: {symbol} - {quantity} shares at ${avg_price:.2f}")
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating holding for {symbol}: {e}")
            return None

    def add_stock(self, symbol):
        try:
            result = supabase.table('watchlist').insert({
                'symbol': symbol,
                'added_at': datetime.now().isoformat()
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
                'timestamp': datetime.now().isoformat()
            }).execute()

            self.update_holding(portfolio_id, symbol, quantity, price)
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
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error updating sell transaction: {e}")
            return None
    

class BacktestRunner:
    def __init__(self):
        self.db = TraderDatabase()
    
    def setup_test_environment(self, test_email="test@example.com", test_password="testpass123"):
        """Setup test user and portfolio for backtesting"""
        print("Setting up test environment...")
        
        # Create test user if doesn't exist
        existing_user = self.db.get_user_by_email(test_email)
        if not existing_user:
            user_id = self.db.create_user(test_email, test_password)
        else:
            user_id = existing_user['user_id']
            print(f"Using existing user: {test_email}")
        
        # Create test portfolio
        portfolio = self.db.create_portfolio(
            email=test_email,
            name="Backtest Portfolio",
            cash_balance=10000.0,
            created_at=datetime.now()
        )
        
        if portfolio:
            portfolio_id = portfolio['portfolio_id']
            print(f"Created test portfolio with ID: {portfolio_id}")
            return portfolio_id
        else:
            print("Failed to create test portfolio")
            return None
    
    def clean_test_data(self, portfolio_id):
        """Clean up test transactions and holdings"""
        try:
            # Delete test transactions
            self.db.supabase.table('transactions').delete().eq('portfolio_id', portfolio_id).execute()
            print("Cleaned test transactions")
            
            # Delete test holdings
            self.db.supabase.table('holdings').delete().eq('portfolio_id', portfolio_id).execute()
            print("Cleaned test holdings")
            
        except Exception as e:
            print(f"Error cleaning test data: {e}")
    
    def run_backtest(self, symbol, start_date='2023-01-01', end_date='2024-01-01', 
                    sentiment_threshold=0.01, hold_days=365, initial_cash=10000.0, existing_portfolio_id=None):
        """Run a complete backtest with database integration"""
        
        # Use existing portfolio or setup test environment
        if existing_portfolio_id:
            portfolio_id = existing_portfolio_id
            print(f"Using existing portfolio: {portfolio_id}")
        else:
            portfolio_id = self.setup_test_environment()
            if not portfolio_id:
                print("Failed to setup test environment")
                return None
            # Clean previous test data only for new portfolios
            self.clean_test_data(portfolio_id)
        
        # Prepare data
        print(f"Downloading data for {symbol} from {start_date} to {end_date}...")
        data = SentimentTrader.prepare_backtrading(symbol, start_date, end_date)
        
        if data.empty:
            print(f"No data found for {symbol}")
            return None
        
        # Setup Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.set_cash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # Add data and strategy
        bt_data = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(bt_data)
        cerebro.addstrategy(
            SentimentTrader, 
            symbol=symbol, 
            portfolio_id=portfolio_id,
            sentiment_threshold=sentiment_threshold,
            hold_days=hold_days
        )
        
        # Print initial state
        print('=' * 60)
        print('STARTING BACKTEST')
        print('=' * 60)
        print(f'Symbol: {symbol}')
        print(f'Period: {start_date} to {end_date}')
        print(f'Sentiment Threshold: {sentiment_threshold}')
        print(f'Hold Days: {hold_days}')
        print(f'Portfolio ID: {portfolio_id}')
        print(f'Initial Cash: ${initial_cash:.2f}')
        print('=' * 60)
        
        # Run backtest
        print("Running backtest...")
        results = cerebro.run()
        
        # Calculate results
        final_value = cerebro.broker.getvalue()
        final_cash = cerebro.broker.getcash()
        total_return = final_value - initial_cash
        return_percentage = (total_return / initial_cash) * 100
        
        # Print results
        print('=' * 60)
        print('BACKTEST RESULTS')
        print('=' * 60)
        print(f'Initial Cash: ${initial_cash:.2f}')
        print(f'Final Portfolio Value: ${final_value:.2f}')
        print(f'Final Cash: ${final_cash:.2f}')
        print(f'Total Return: ${total_return:.2f}')
        print(f'Return Percentage: {return_percentage:.2f}%')
        
        if total_return > 0:
            print(f' PROFIT: You made ${total_return:.2f}!')
        else:
            print(f' LOSS: You lost ${abs(total_return):.2f}')
        
        print('=' * 60)
        
        # Verify database updates
        self.verify_database_updates(portfolio_id)
        
        return {
            'portfolio_id': portfolio_id,
            'initial_cash': initial_cash,
            'final_value': final_value,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'symbol': symbol
        }
    
    def verify_database_updates(self, portfolio_id):
        """Verify that database was updated correctly"""
        print("\n" + "=" * 40)
        print("VERIFYING DATABASE UPDATES")
        print("=" * 40)
        
        try:
            # Check transactions
            transactions = self.db.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).execute()
            print(f"Total transactions recorded: {len(transactions.data)}")
            
            buy_count = len([t for t in transactions.data if t['tx_type'] == 'buy'])
            sell_count = len([t for t in transactions.data if t['tx_type'] == 'sell'])
            print(f"Buy orders: {buy_count}")
            print(f"Sell orders: {sell_count}")
            
            # Show transaction details
            for i, tx in enumerate(transactions.data):
                print(f"  {i+1}. {tx['tx_type'].upper()}: {tx['quantity']} shares of {tx['symbol']} at ${tx['price']:.2f}")
            
            # Check holdings
            holdings = self.db.get_portfolio_holdings(portfolio_id)
            print(f"Current holdings: {len(holdings)}")
            
            for symbol, holding in holdings.items():
                print(f"  {symbol}: {holding['quantity']} shares at avg ${holding['avg_price']:.2f}")
            
        except Exception as e:
            print(f"Error verifying database: {e}")

# Simplified usage functions
def run_backtest_with_db(symbol='WDAY', start_date='2023-01-01', end_date='2024-01-01', hold_days=365, initial_cash=10000.0):
    """Run backtest and save everything to database"""
    runner = BacktestRunner()
    return runner.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        hold_days=hold_days,
        initial_cash=initial_cash,
        existing_portfolio_id=None  # Create new portfolio
    )

def run_active_backtest(symbol='WDAY', hold_days=30, initial_cash=10000.0):
    """Run backtest with shorter hold period for more activity"""
    runner = BacktestRunner()
    return runner.run_backtest(
        symbol=symbol,
        start_date='2023-01-01',
        end_date='2024-06-01',  # Longer period
        hold_days=hold_days,
        initial_cash=initial_cash,
        existing_portfolio_id=None  # Create new portfolio
    )

def run_portfolio_backtest(symbol, portfolio_id, hold_days=30):
    """Run backtest using a specific portfolio's cash balance"""
    db = TraderDatabase()
    portfolio = db.get_portfolio_by_id(portfolio_id)
    
    if not portfolio:
        print(f"Portfolio {portfolio_id} not found")
        return None
    
    cash_balance = portfolio['cash_balance']
    print(f"Running backtest for portfolio {portfolio_id} with cash balance: ${cash_balance}")
    
    runner = BacktestRunner()
    return runner.run_backtest(
        symbol=symbol,
        start_date='2023-01-01',
        end_date='2024-06-01',
        hold_days=hold_days,
        initial_cash=cash_balance,
        existing_portfolio_id=portfolio_id  # Pass the existing portfolio ID
    )

# Example usage:
if __name__ == "__main__":
    # Test with shorter hold period to see more trades
    print("Running active backtest...")
    results = run_active_backtest(symbol='WDAY', hold_days=60)
    
    if results:
        print(f"\nBacktest completed! Portfolio ID: {results['portfolio_id']}")
        print(f"Check your database for transaction records.")