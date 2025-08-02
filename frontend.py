from fasthtml.common import *
from monsterui.all import *
from sentiment import *

app, rt = fast_app(hdrs=Theme.blue.headers())
db = TraderDatabase()
runner = BacktestRunner()


def InfoCard(title, content=None, button_text=None, button_href=None, input_name=None, card_class="", is_submit=False):
    if is_submit and input_name:
        # Create a form for submission
        return Form(
            Card(
                Title(title, _class="text-xl font-bold"),
                P(content, _class="text-sm text-neutral-content"),
                Input(
                    name=input_name,
                    placeholder="Enter ticker symbol",
                    _class="input input-bordered w-full mt-4"
                ),
                Button(
                    button_text,
                    type="submit",
                    _class="btn btn-primary btn-sm mt-4 rounded-full px-6"
                ),
                _class=f"max-w-sm p-6 rounded-xl shadow-lg bg-base-100 {card_class}"
            ),
            method="GET"
        )
    else:
        # Regular card without form
        return Card(
            Title(title, _class="text-xl font-bold"),
            P(content, _class="text-sm text-neutral-content"),
            Input(
                name=input_name,
                placeholder="Enter here",
                _class="input input-bordered w-full mt-4"
                ) if input_name else None, 
            A(
                button_text,
                href=button_href,
                _class="btn btn-primary btn-sm mt-4 rounded-full px-6"
            ) if button_text and button_href else None, 
            _class=f"max-w-sm p-6 rounded-xl shadow-lg bg-base-100 {card_class}"
        )

def get_portfolios():
    try: 
        portfolios = db.get_user_portfolios('test@example.com')
        portfolio_names, portfolio_cash_value, portfolio_id = [], [], []
        for portfolio in portfolios:
            portfolio_names.append(portfolio['name'])
            portfolio_cash_value.append(portfolio['cash_balance'])
            portfolio_id.append(str(portfolio['portfolio_id']))
        return portfolio_names, portfolio_cash_value, portfolio_id
    
    except Exception as e:
        print(f'Error: {e}')
        return [],[],[]      


# Home route

@rt('/')
def index():
    names, cash, id = get_portfolios()
    if len(names) != len(cash):
        print("mismatch error")
        return None
    cards = []
    for i in range(len(names)):
        # Add some visual flair based on cash value
        cash_value = float(cash[i])
        if cash_value > 15000:
            card_class = "bg-gradient-to-r from-green-500 to-emerald-500 text-white"
            emoji = "💎"
        elif cash_value > 12000:
            card_class = "bg-gradient-to-r from-blue-500 to-cyan-500 text-white"
            emoji = "🚀"
        elif cash_value > 10000:
            card_class = "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
            emoji = "⭐"
        else:
            card_class = "bg-gradient-to-r from-orange-500 to-red-500 text-white"
            emoji = "📈"
            
        cards.append(InfoCard(
            title=f"{emoji} {names[i]}",
            content=f'💰 Cash Value: ${cash_value:,.2f}',
            button_text=f"View Portfolio",
            button_href=f'/portfolio/{id[i]}',
            card_class=card_class
        ))
    
    return Center(Titled("🏦 Your Trading Portfolios",
                  Center(
                      Div(
                          *cards, 
                          _class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6"
                      )
                  )))

# About route
@rt('/portfolio/{portfolio_id}')
def portfolio(portfolio_id: str):
    try:
        print(f"Accessing portfolio with ID: {portfolio_id}")
        cards = []
        transactions_in_portfolio = db.transactions_by_portfolio(portfolio_id)
        print(f"Transactions returned: {transactions_in_portfolio}")
        # Get portfolio info for header
        portfolio_info = db.get_portfolio_by_id(portfolio_id)
        portfolio_name = portfolio_info['name'] if portfolio_info else "Portfolio"
        current_cash = portfolio_info['cash_balance'] if portfolio_info else 0
        
        # Get most recent sold stock
        recent_sold = db.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).eq('tx_type', 'sell').order('timestamp', desc=True).limit(1).execute()
        
        if transactions_in_portfolio:
            for transaction in transactions_in_portfolio:
                # Get the most recent transaction for this symbol in this portfolio
                result = db.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).eq('symbol', transaction).order('timestamp', desc=True).limit(1).execute()
                if result.data:
                    symbol = result.data[0]['symbol']
                    price = result.data[0]['price']
                    tx_type = result.data[0]['tx_type']
                    quantity = result.data[0]['quantity']
                    timestamp = result.data[0]['timestamp']
                    
                    # Determine card color based on transaction type
                    card_class = 'bg-success text-white' if tx_type == 'sell' else 'bg-info text-white'
                    
                    cards.append(InfoCard(
                        title=f"{symbol.upper()} - {tx_type.upper()}",
                        content=f"{abs(quantity)} shares at ${price:.2f}\n{timestamp[:10]}",
                        card_class=card_class
                    ))
        else:
            cards.append(InfoCard(
                title="No Transactions",
                content="This portfolio has no trading activity yet.",
                card_class="bg-warning text-white"
            ))
        # Add most recent sold stock card if available
        if recent_sold.data:
            sold_tx = recent_sold.data[0]
            cards.append(InfoCard(
                title="🔥 Most Recent Sale",
                content=f"{sold_tx['symbol'].upper()}\n{sold_tx['quantity']} shares at ${sold_tx['price']:.2f}\n{sold_tx['timestamp'][:10]}",
                card_class="bg-gradient-to-r from-red-500 to-pink-500 text-white"
            ))
        
        # Add portfolio summary card
        cards.append(InfoCard(
            title=f"💰 {portfolio_name}",
            content=f"Current Cash: ${current_cash:.2f}",
            card_class="bg-gradient-to-r from-blue-500 to-purple-500 text-white"
        ))
        
        # Add trade button
        cards.append(InfoCard(
            title="🚀 Start Trading",
            content="Run sentiment-based backtests on stocks",
            button_text='Trade Now',
            button_href=f'/trade/{portfolio_id}',
            card_class="bg-gradient-to-r from-green-500 to-teal-500 text-white"
        ))
        
        return Center(Titled(f"📊 {portfolio_name} Dashboard",
                      Center(
                          Div(*cards, _class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6")
                      )))
    except Exception as e:
        print(f"Error: {e}")
        return None
    
@rt('/trade/{portfolio_id}')
def trade(portfolio_id: str, ticker: str = None):
    try:
        print(f"Accessing portfolio with ID: {portfolio_id}")
        print(f"Ticker parameter: {ticker}")
        
        portfolio = db.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            return Titled("Error", P("Portfolio not found."))
        
        cash_balance = portfolio['cash_balance']
        print(f"Ticker from parameter: {ticker}")
        
        results_card = None
        if ticker:
            print(f"Running backtest for ticker: {ticker}")
            try:
                from sentiment import run_portfolio_backtest
                result = run_portfolio_backtest(ticker, portfolio_id)
                print(f"Backtest result: {result}")
                if result:
                    # Determine if it's a profit or loss
                    is_profit = result["return_percentage"] > 0
                    card_class = 'bg-success text-white' if is_profit else 'bg-error text-white'
                    
                    # Update the portfolio's cash balance in the database
                    try:
                        updated_portfolio = db.update_portfolio_cash(portfolio_id, result["final_value"])
                        if updated_portfolio:
                            print(f"Updated portfolio cash balance from ${result['initial_cash']:.2f} to ${result['final_value']:.2f}")
                            
                            # Get the transactions that were created during the backtest
                            transactions = db.supabase.table('transactions').select('*').eq('portfolio_id', portfolio_id).eq('symbol', ticker.upper()).order('timestamp', desc=True).execute()
                            if transactions.data:
                                print(f"Created {len(transactions.data)} transactions for {ticker.upper()}")
                                for tx in transactions.data:
                                    print(f"  {tx['tx_type'].upper()}: {tx['quantity']} shares at ${tx['price']:.2f}")
                        else:
                            print("Failed to update portfolio cash balance")
                    except Exception as e:
                        print(f"Error updating portfolio cash balance: {e}")
                    
                    # Create a more detailed results card
                    profit_emoji = "📈" if is_profit else "📉"
                    results_card = InfoCard(
                        title=f'{profit_emoji} {ticker.upper()} Backtest Results',
                        content=f'''💰 Initial: ${result["initial_cash"]:,.2f}
💵 Final: ${result["final_value"]:,.2f}
📊 Return: ${result["total_return"]:,.2f}
📈 Percentage: {result["return_percentage"]:.2f}%

✅ Portfolio updated!''',
                        button_text="📋 View Updated Portfolio",
                        button_href=f"/portfolio/{portfolio_id}",
                        card_class=card_class
                    )
                else:
                    results_card = InfoCard(
                        title=f'Error for {ticker.upper()}',
                        content='Backtest failed or returned no results',
                        card_class='bg-error text-white'
                    )
            except Exception as e:
                print(f"Error running backtest: {e}")
                results_card = InfoCard(
                    title=f'Error for {ticker.upper()}',
                    content=f'Backtest error: {str(e)}',
                    card_class='bg-error text-white'
                )
        
        return Titled("🎯 Sentiment Trading Simulator",
                      Center(
                          Div(
                              # Back to portfolio button
                              A(
                                  "← Back to Portfolio",
                                  href=f"/portfolio/{portfolio_id}",
                                  _class="btn btn-outline mb-4"
                              ),
                              # Portfolio info card
                              InfoCard(
                                  title="💰 Portfolio Status",
                                  content=f'Available Cash: ${cash_balance:,.2f}',
                                  card_class="bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                              ),
                              # Trade form
                              InfoCard(
                                  title="📊 Enter Stock Symbol",
                                  content="Enter a stock ticker to run sentiment analysis backtest",
                                  input_name='ticker',
                                  button_text="🚀 Run Backtest",
                                  is_submit=True,
                                  card_class="bg-gradient-to-r from-green-500 to-teal-500 text-white"
                              ),
                              # Results card (if exists)
                              results_card if results_card else None,
                              _class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6"
                          )
                      )
                      )
    except Exception as e:
        print(f"Error: {e}")
        return Titled("Error", P("Something went wrong."))
        



serve()
