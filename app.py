"""
Professional Trading Backtest Frontend
--------------------------------------
Modern, minimalistic gray/blue design with professional aesthetics
"""

from fasthtml.common import *
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import pandas as pd

# =============================================================================
# BACKEND CONNECTION
# =============================================================================
try:
    from sentiment import BacktestRunner, TraderDatabase, SentimentTrader
    print("✅ Successfully connected to your trading backend!")
    
    db = TraderDatabase()
    backtest_runner = BacktestRunner()
    
except ImportError as e:
    print("❌ Could not import your trading backend.")
    print(f"Error: {e}")
    exit()

# =============================================================================
# MODERN PROFESSIONAL STYLING
# =============================================================================
PROFESSIONAL_CSS = """
:root {
    --primary-blue: #3B82F6;
    --primary-blue-dark: #1E40AF;
    --secondary-blue: #60A5FA;
    --accent-blue: #DBEAFE;
    --gray-50: #F9FAFB;
    --gray-100: #F3F4F6;
    --gray-200: #E5E7EB;
    --gray-300: #D1D5DB;
    --gray-400: #9CA3AF;
    --gray-500: #6B7280;
    --gray-600: #4B5563;
    --gray-700: #374151;
    --gray-800: #1F2937;
    --gray-900: #111827;
    --success: #10B981;
    --success-light: #D1FAE5;
    --danger: #EF4444;
    --danger-light: #FEE2E2;
    --warning: #F59E0B;
    --warning-light: #FEF3C7;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, var(--gray-50) 0%, var(--accent-blue) 100%);
    min-height: 100vh;
    color: var(--gray-800);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Navigation */
.navbar {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--gray-200);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-blue) !important;
    text-decoration: none;
    transition: all 0.3s ease;
}

.navbar-brand:hover {
    transform: translateY(-1px);
    color: var(--primary-blue-dark) !important;
}

.nav-link {
    color: var(--gray-600) !important;
    font-weight: 500;
    padding: 0.75rem 1rem !important;
    border-radius: 8px;
    transition: all 0.3s ease;
    text-decoration: none;
    margin: 0 0.25rem;
}

.nav-link:hover {
    color: var(--primary-blue) !important;
    background: var(--accent-blue);
    transform: translateY(-2px);
}

/* Cards */
.card {
    background: white;
    border: none;
    border-radius: 16px;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
}

.card-header {
    background: var(--primary-blue);
    color: white;
    font-weight: 600;
    font-size: 1.1rem;
    padding: 1.5rem;
    border: none;
}

.card-body {
    padding: 2rem;
}

/* Buttons */
.btn {
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.875rem 2rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.btn:hover::before {
    left: 100%;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
    color: white;
    box-shadow: var(--shadow);
}

.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
    background: linear-gradient(135deg, var(--primary-blue-dark), var(--primary-blue));
}

.btn-outline-primary {
    background: transparent;
    color: var(--primary-blue);
    border: 2px solid var(--primary-blue);
}

.btn-outline-primary:hover {
    background: var(--primary-blue);
    color: white;
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}

.btn-success {
    background: linear-gradient(135deg, var(--success), #059669);
    color: white;
}

.btn-success:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}

.btn-outline-secondary {
    background: transparent;
    color: var(--gray-600);
    border: 2px solid var(--gray-300);
}

.btn-outline-secondary:hover {
    background: var(--gray-600);
    color: white;
    transform: translateY(-3px);
}

/* Forms */
.form-control {
    border: 2px solid var(--gray-300);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: white;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    transform: translateY(-1px);
}

.form-label {
    font-weight: 600;
    color: var(--gray-700);
    margin-bottom: 0.5rem;
}

/* Statistics Cards */
.stat-card {
    background: white;
    border: none;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-blue), var(--secondary-blue));
}

.stat-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

.stat-card.success::before {
    background: linear-gradient(90deg, var(--success), #059669);
}

.stat-card.danger::before {
    background: linear-gradient(90deg, var(--danger), #DC2626);
}

.stat-card.warning::before {
    background: linear-gradient(90deg, var(--warning), #D97706);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--gray-800);
    margin: 1rem 0 0.5rem 0;
    line-height: 1;
}

.stat-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.stat-sublabel {
    font-size: 0.75rem;
    color: var(--gray-400);
}

.stat-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.8;
}

/* Login Page Specific */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.login-card {
    background: white;
    border-radius: 24px;
    box-shadow: var(--shadow-xl);
    padding: 3rem;
    width: 100%;
    max-width: 400px;
    text-align: center;
}

.login-title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--gray-800);
    margin-bottom: 0.5rem;
}

.login-subtitle {
    color: var(--gray-500);
    margin-bottom: 2rem;
}

/* Tables */
.table {
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow);
}

.table th {
    background: var(--gray-800);
    color: white;
    font-weight: 600;
    padding: 1rem;
    border: none;
}

.table td {
    padding: 1rem;
    border-bottom: 1px solid var(--gray-200);
    background: white;
}

.table tbody tr:hover {
    background: var(--gray-50);
}

/* Badges */
.badge {
    padding: 0.5rem 1rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.bg-success {
    background: var(--success) !important;
    color: white;
}

.bg-danger {
    background: var(--danger) !important;
    color: white;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.fade-in-up-delay-1 { animation-delay: 0.1s; animation-fill-mode: both; }
.fade-in-up-delay-2 { animation-delay: 0.2s; animation-fill-mode: both; }
.fade-in-up-delay-3 { animation-delay: 0.3s; animation-fill-mode: both; }
.fade-in-up-delay-4 { animation-delay: 0.4s; animation-fill-mode: both; }

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 0 1rem;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    .stat-card {
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .btn {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .navbar-nav {
        flex-direction: column;
        gap: 0.5rem;
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--gray-100);
}

::-webkit-scrollbar-thumb {
    background: var(--gray-400);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gray-500);
}
"""

# =============================================================================
# WEB APP SETUP
# =============================================================================
app, rt = fast_app(
    hdrs=[
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=True),
        Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap", rel="stylesheet"),
        Script(src="https://cdn.plot.ly/plotly-latest.min.js"),
        Style(PROFESSIONAL_CSS)
    ]
)

# Session storage (in production, use proper session management)
sessions = {}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_page_layout(title, content, show_nav=True):
    """Creates the basic layout for all pages"""
    nav_content = ""
    if show_nav:
        nav_content = Nav(
            Div(
                A("📊 TradingPro", href="/dashboard", cls="navbar-brand"),
                Div(
                    A("🏠 Dashboard", href="/dashboard", cls="nav-link"),
                    A("🚀 Backtest", href="/backtest", cls="nav-link"),
                    A("💼 Portfolios", href="/portfolios", cls="nav-link"),
                    A("📊 Transactions", href="/transactions", cls="nav-link"),
                    A("🚪 Logout", href="/", cls="nav-link"),
                    cls="navbar-nav ms-auto d-flex flex-row"
                ),
                cls="container d-flex justify-content-between align-items-center py-3"
            ),
            cls="navbar"
        )
    
    return Html(
        Head(
            Title(f"{title} - TradingPro"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1")
        ),
        Body(
            nav_content,
            content
        )
    )

def create_stat_card(title, value, subtitle, color="primary", icon="📊", delay=0):
    """Creates professional statistics cards"""
    color_class = color if color in ['success', 'danger', 'warning'] else 'primary'
    
    return Div(
        Div(icon, cls="stat-icon"),
        Div(title, cls="stat-label"),
        Div(value, cls="stat-value"),
        Div(subtitle, cls="stat-sublabel"),
        cls=f"stat-card {color_class} fade-in-up fade-in-up-delay-{delay}"
    )

def get_user_stats(email):
    """Get real user statistics from database"""
    try:
        # Get portfolios
        portfolios = db.get_user_portfolios(email)
        
        # Get recent transactions
        result = db.supabase.table('transactions').select('*').eq('email', email).limit(100).execute()
        transactions = result.data if result.data else []
        
        # Calculate stats
        total_portfolio_value = sum(p['cash_balance'] for p in portfolios) if portfolios else 0
        
        # Calculate total return from transactions
        total_spent = sum(abs(t['quantity'] * t['price']) for t in transactions if t.get('tx_type') == 'buy')
        total_gained = sum(abs(t['quantity'] * t['price']) for t in transactions if t.get('tx_type') == 'sell')
        total_return = total_gained - total_spent
        
        # Calculate win rate
        buy_trades = [t for t in transactions if t.get('tx_type') == 'buy']
        sell_trades = [t for t in transactions if t.get('tx_type') == 'sell']
        win_rate = 0
        if len(buy_trades) > 0:
            profitable_trades = len([t for t in sell_trades if t.get('price', 0) > 0])  # Simplified
            win_rate = (profitable_trades / len(buy_trades)) * 100 if len(buy_trades) > 0 else 0
        
        # Active positions (simplified - count recent buy transactions without corresponding sells)
        active_trades = len(buy_trades) - len(sell_trades)
        active_trades = max(0, active_trades)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'active_trades': active_trades,
            'portfolio_value': total_portfolio_value,
            'recent_transactions': transactions[:5]  # Last 5 transactions
        }
        
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            'total_return': 0,
            'win_rate': 0,
            'active_trades': 0,
            'portfolio_value': 0,
            'recent_transactions': []
        }

# =============================================================================
# PAGE ROUTES
# =============================================================================

@rt("/")
def login_page():
    """Professional login page"""
    content = Div(
        Div(
            Div(
                H1("Welcome to TradingPro", cls="login-title fade-in-up"),
                P("Enter your email to access your trading dashboard", cls="login-subtitle fade-in-up fade-in-up-delay-1"),
                
                Form(
                    Div(
                        Input(
                            type="email",
                            name="email",
                            placeholder="Enter your email address",
                            cls="form-control fade-in-up fade-in-up-delay-2",
                            required=True,
                            style="margin-bottom: 1.5rem;"
                        ),
                        Button(
                            "🚀 Access Dashboard",
                            type="submit",
                            cls="btn btn-primary btn-lg fade-in-up fade-in-up-delay-3",
                            style="width: 100%;"
                        )
                    ),
                    method="post",
                    action="/login"
                ),
                cls="login-card fade-in-up"
            ),
            cls="login-container"
        )
    )
    
    return create_page_layout("Login", content, show_nav=False)

@rt("/login", methods=["POST"])
def handle_login(email: str):
    """Handle login and create session"""
    # Store email in session (in production, use proper session management)
    session_id = f"session_{len(sessions)}"
    sessions[session_id] = {"email": email, "created_at": datetime.now()}
    
    # In a real app, you'd set a secure cookie here
    # For now, we'll pass the email as a parameter
    return RedirectResponse(f"/dashboard?email={email}")

@rt("/dashboard")
def dashboard_page(email: str = None):
    """Professional dashboard with real user data"""
    if not email:
        return RedirectResponse("/")
    
    # Get real user statistics
    stats = get_user_stats(email)
    
    content = Div(
        Div(
            # Welcome Section
            Div(
                H1(f"Welcome back! 👋", cls="display-4 mb-2 fade-in-up", 
                   style="font-weight: 800; color: var(--gray-800);"),
                P(f"Trading dashboard for {email}", cls="lead text-muted fade-in-up fade-in-up-delay-1"),
                cls="text-center py-5"
            ),
            
            # Statistics Cards
            Div(
                Div(
                    create_stat_card(
                        "Total Return", 
                        f"${stats['total_return']:,.2f}", 
                        "All-time performance",
                        "success" if stats['total_return'] >= 0 else "danger",
                        "💰",
                        1
                    ),
                    cls="col-lg-3 col-md-6 mb-4"
                ),
                Div(
                    create_stat_card(
                        "Win Rate", 
                        f"{stats['win_rate']:.1f}%", 
                        "Success percentage",
                        "primary",
                        "🎯",
                        2
                    ),
                    cls="col-lg-3 col-md-6 mb-4"
                ),
                Div(
                    create_stat_card(
                        "Active Positions", 
                        str(stats['active_trades']), 
                        "Current trades",
                        "warning",
                        "📈",
                        3
                    ),
                    cls="col-lg-3 col-md-6 mb-4"
                ),
                Div(
                    create_stat_card(
                        "Portfolio Value", 
                        f"${stats['portfolio_value']:,.2f}", 
                        "Total assets",
                        "success",
                        "💎",
                        4
                    ),
                    cls="col-lg-3 col-md-6 mb-4"
                ),
                cls="row mb-5"
            ),
            
            # Quick Actions
            Div(
                Div(
                    H3("Quick Actions", cls="mb-4 fade-in-up", style="font-weight: 700;"),
                    Div(
                        A("🚀 New Backtest", href=f"/backtest?email={email}", 
                          cls="btn btn-primary btn-lg me-3 mb-3 fade-in-up fade-in-up-delay-1"),
                        A("💼 View Portfolios", href=f"/portfolios?email={email}", 
                          cls="btn btn-outline-primary btn-lg me-3 mb-3 fade-in-up fade-in-up-delay-2"),
                        A("📊 Transactions", href=f"/transactions?email={email}", 
                          cls="btn btn-outline-secondary btn-lg mb-3 fade-in-up fade-in-up-delay-3"),
                        cls="text-center"
                    ),
                    cls="card-body"
                ),
                cls="card mb-5 fade-in-up fade-in-up-delay-1"
            ),
            
            # Recent Activity
            Div(
                H4("📋 Recent Activity", cls="card-header"),
                Div(
                    *[
                        Div(
                            f"{'📈' if tx.get('tx_type') == 'buy' else '📉'} "
                            f"{tx.get('tx_type', 'N/A').upper()} {abs(tx.get('quantity', 0))} "
                            f"{tx.get('symbol', 'N/A')} @ ${tx.get('price', 0):.2f}",
                            cls="border-bottom pb-3 mb-3",
                            style="color: var(--gray-700);"
                        ) for tx in stats['recent_transactions']
                    ] if stats['recent_transactions'] else [
                        Div("No recent activity. Start trading to see your activity here!", 
                            cls="text-center text-muted py-4")
                    ],
                    cls="card-body"
                ),
                cls="card fade-in-up fade-in-up-delay-2"
            ),
            
            cls="container py-4"
        )
    )
    
    return create_page_layout("Dashboard", content)

@rt("/backtest")
def backtest_page(email: str = None):
    """Modern backtest configuration page"""
    if not email:
        return RedirectResponse("/")
    
    content = Div(
        Div(
            H2("🚀 Create New Backtest", cls="text-center mb-2 fade-in-up", 
               style="font-weight: 800; font-size: 2.5rem;"),
            P("Configure your AI-powered sentiment trading strategy", 
              cls="text-center text-muted mb-5 fade-in-up fade-in-up-delay-1"),
            
            Div(
                Form(
                    # Hidden email field
                    Input(type="hidden", name="email", value=email),
                    
                    # Stock Symbol
                    Div(
                        Label("📈 Stock Symbol", fr="symbol", cls="form-label"),
                        Input(
                            type="text", 
                            name="symbol", 
                            id="symbol", 
                            value="AAPL",
                            placeholder="Enter ticker symbol (e.g., AAPL, TSLA, GOOGL)",
                            cls="form-control",
                            required=True
                        ),
                        P("💡 Popular choices: AAPL, GOOGL, TSLA, MSFT, NVDA", 
                          cls="text-muted small mt-2"),
                        cls="mb-4 fade-in-up fade-in-up-delay-2"
                    ),
                    
                    # Date Range
                    Div(
                        H5("📅 Backtest Period", cls="mb-3"),
                        Div(
                            Div(
                                Label("Start Date", fr="start_date", cls="form-label"),
                                Input(
                                    type="date", 
                                    name="start_date", 
                                    id="start_date",
                                    value="2023-01-01", 
                                    cls="form-control",
                                    required=True
                                ),
                                cls="col-md-6"
                            ),
                            Div(
                                Label("End Date", fr="end_date", cls="form-label"),
                                Input(
                                    type="date", 
                                    name="end_date", 
                                    id="end_date",
                                    value="2024-01-01", 
                                    cls="form-control",
                                    required=True
                                ),
                                cls="col-md-6"
                            ),
                            cls="row"
                        ),
                        cls="mb-4 fade-in-up fade-in-up-delay-3"
                    ),
                    
                    # Strategy Settings
                    Div(
                        H5("⚙️ Strategy Configuration", cls="mb-3"),
                        Div(
                            Div(
                                Label("Sentiment Threshold", fr="sentiment_threshold", cls="form-label"),
                                Input(
                                    type="number", 
                                    name="sentiment_threshold", 
                                    id="sentiment_threshold",
                                    value="0.01", 
                                    step="0.001", 
                                    min="-1", 
                                    max="1",
                                    cls="form-control",
                                    required=True
                                ),
                                P("Minimum sentiment score to trigger buy signal (-1 to 1)", 
                                  cls="text-muted small mt-2"),
                                cls="col-md-6"
                            ),
                            Div(
                                Label("Hold Period (Days)", fr="hold_days", cls="form-label"),
                                Input(
                                    type="number", 
                                    name="hold_days", 
                                    id="hold_days",
                                    value="30", 
                                    min="1", 
                                    max="365",
                                    cls="form-control",
                                    required=True
                                ),
                                P("Maximum days to hold each position", 
                                  cls="text-muted small mt-2"),
                                cls="col-md-6"
                            ),
                            cls="row"
                        ),
                        cls="mb-5 fade-in-up fade-in-up-delay-4"
                    ),
                    
                    # Submit Buttons
                    Div(
                        Button(
                            "🚀 Run Backtest", 
                            type="submit", 
                            cls="btn btn-primary btn-lg me-3 mb-3"
                        ),
                        A("← Back to Dashboard", href=f"/dashboard?email={email}", 
                          cls="btn btn-outline-secondary btn-lg mb-3"),
                        cls="text-center fade-in-up fade-in-up-delay-5"
                    ),
                    
                    method="post", 
                    action="/run_backtest"
                ),
                cls="card-body"
            ),
            cls="card fade-in-up"
        ),
        cls="container py-5"
    )
    
    return create_page_layout("New Backtest", content)

@rt("/run_backtest", methods=["POST"])
def execute_backtest(email: str, symbol: str, start_date: str, end_date: str, 
                    sentiment_threshold: float, hold_days: int):
    """Execute backtest with modern results display"""
    import matplotlib
    matplotlib.use('Agg')
    
    try:
        print(f"🚀 Running backtest for {symbol} (User: {email})...")
        
        results = backtest_runner.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            sentiment_threshold=sentiment_threshold,
            hold_days=hold_days
        )
        
        if not results:
            content = Div(
                Div(
                    Div(
                        H1("❌ Backtest Failed", cls="text-center mb-4 fade-in-up"),
                        P("We encountered an issue running your backtest. Please try again with different parameters.", 
                          cls="text-center text-muted mb-4 fade-in-up fade-in-up-delay-1"),
                        A("🔄 Try Again", href=f"/backtest?email={email}", 
                          cls="btn btn-primary btn-lg fade-in-up fade-in-up-delay-2"),
                        cls="card-body text-center py-5"
                    ),
                    cls="card"
                ),
                cls="container py-5"
            )
            return create_page_layout("Backtest Failed", content)
        
        # Enhanced chart data
        chart_data = {
            'data': [{
                'x': ['Start', 'End'],
                'y': [results['initial_cash'], results['final_value']],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Portfolio Value',
                'line': {
                    'color': '#3B82F6',
                    'width': 4,
                    'shape': 'spline'
                },
                'marker': {
                    'size': 15,
                    'color': ['#3B82F6', '#10B981' if results['total_return'] > 0 else '#EF4444'],
                    'line': {'width': 3, 'color': 'white'}
                },
                'fill': 'tonexty',
                'fillcolor': 'rgba(59, 130, 246, 0.1)'
            }, {
                'x': ['Start', 'End'],
                'y': [results['initial_cash'], results['initial_cash']],
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Baseline',
                'line': {'color': '#9CA3AF', 'width': 2, 'dash': 'dash'},
                'showlegend': True
            }],
            'layout': {
                'title': {
                    'text': f'Portfolio Performance - {symbol}',
                    'font': {'size': 24, 'family': 'Inter', 'color': '#1F2937'},
                    'x': 0.5
                },
                'xaxis': {
                    'title': 'Timeline',
                    'gridcolor': '#F3F4F6',
                    'showgrid': True,
                    'zeroline': False
                },
                'yaxis': {
                    'title': 'Portfolio Value ($)',
                    'gridcolor': '#F3F4F6',
                    'showgrid': True,
                    'tickformat': ',.0f'
                },
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'font': {'family': 'Inter'},
                'height': 450,
                'margin': {'t': 80, 'b': 60, 'l': 80, 'r': 40},
                'hovermode': 'x unified',
                'legend': {
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1
                }
            }
        }
        
        chart_json = json.dumps(chart_data)
        
        # Determine performance indicators
        is_positive = results['total_return'] > 0
        performance_color = "success" if is_positive else "danger"
        performance_icon = "🚀" if results['return_percentage'] > 10 else "📈" if is_positive else "📉"
        
        content = Div(
            Div(
                # Hero Section
                Div(
                    H1(f"{performance_icon} Backtest Complete!", 
                       cls="text-center mb-3 fade-in-up",
                       style="font-weight: 800; font-size: 3rem;"),
                    H3(f"Results for {symbol}", 
                       cls="text-center text-muted mb-4 fade-in-up fade-in-up-delay-1"),
                    cls="text-center py-4"
                ),
                
                # Performance Metrics
                Div(
                    Div(
                        create_stat_card(
                            "Total Return", 
                            f"${results['total_return']:,.2f}", 
                            "Profit/Loss",
                            performance_color,
                            "💰",
                            1
                        ),
                        cls="col-lg-4 mb-4"
                    ),
                    Div(
                        create_stat_card(
                            "Return Percentage", 
                            f"{results['return_percentage']:.1f}%", 
                            "Performance",
                            performance_color,
                            "📊",
                            2
                        ),
                        cls="col-lg-4 mb-4"
                    ),
                    Div(
                        create_stat_card(
                            "Final Value", 
                            f"${results['final_value']:,.2f}", 
                            "Portfolio Worth",
                            "primary",
                            "💎",
                            3
                        ),
                        cls="col-lg-4 mb-4"
                    ),
                    cls="row mb-5"
                ),
                
                # Performance Chart
                Div(
                    H4("📈 Performance Visualization", cls="card-header"),
                    Div(
                        Div(id="performance-chart", style="padding: 2rem;"),
                        Script(f"""
                            var chartData = {chart_json};
                            Plotly.newPlot('performance-chart', chartData.data, chartData.layout, {{responsive: true}});
                        """),
                        cls="card-body p-0"
                    ),
                    cls="card mb-5 fade-in-up fade-in-up-delay-2"
                ),
                
                # Strategy Details
                Div(
                    H4("⚙️ Strategy Configuration", cls="card-header"),
                    Div(
                        Div(
                            Div(
                                H6("Trading Parameters", cls="mb-3 text-primary fw-bold"),
                                P(f"📈 Symbol: {symbol}", cls="mb-2"),
                                P(f"📅 Period: {start_date} to {end_date}", cls="mb-2"),
                                P(f"🧠 Strategy: AI Sentiment Trader", cls="mb-2"),
                                P(f"🎯 Sentiment Threshold: {sentiment_threshold}", cls="mb-0"),
                                cls="col-md-6"
                            ),
                            Div(
                                H6("Results Summary", cls="mb-3 text-primary fw-bold"),
                                P(f"⏰ Hold Period: {hold_days} days", cls="mb-2"),
                                P(f"💰 Initial Cash: ${results['initial_cash']:,.2f}", cls="mb-2"),
                                P(f"🆔 Portfolio ID: {results.get('portfolio_id', 'N/A')}", cls="mb-2"),
                                P("✅ Status: Completed Successfully", cls="mb-0 text-success fw-semibold"),
                                cls="col-md-6"
                            ),
                            cls="row"
                        ),
                        cls="card-body"
                    ),
                    cls="card mb-5 fade-in-up fade-in-up-delay-3"
                ),
                
                # Action Buttons
                Div(
                    A("🚀 Run Another Backtest", href=f"/backtest?email={email}", 
                      cls="btn btn-primary btn-lg me-3 mb-3 fade-in-up fade-in-up-delay-4"),
                    A("💼 View Portfolios", href=f"/portfolios?email={email}", 
                      cls="btn btn-outline-primary btn-lg me-3 mb-3 fade-in-up fade-in-up-delay-5"),
                    A("📊 View Transactions", href=f"/transactions?email={email}", 
                      cls="btn btn-outline-secondary btn-lg me-3 mb-3 fade-in-up fade-in-up-delay-6"),
                    A("🏠 Dashboard", href=f"/dashboard?email={email}", 
                      cls="btn btn-outline-secondary btn-lg mb-3 fade-in-up fade-in-up-delay-7"),
                    cls="text-center pb-5"
                ),
                
                cls="container py-4"
            )
        )
        
        return create_page_layout(f"Results: {symbol}", content)
        
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        content = Div(
            Div(
                Div(
                    H1("❌ Something Went Wrong", cls="text-center mb-4 fade-in-up"),
                    P(f"Error: {str(e)}", cls="text-center text-muted mb-4 fade-in-up fade-in-up-delay-1"),
                    A("🔄 Try Again", href=f"/backtest?email={email}", 
                      cls="btn btn-primary btn-lg fade-in-up fade-in-up-delay-2"),
                    cls="card-body text-center py-5"
                ),
                cls="card"
            ),
            cls="container py-5"
        )
        return create_page_layout("Error", content)

@rt("/portfolios")
def portfolios_page(email: str = None):
    """Professional portfolios page"""
    if not email:
        return RedirectResponse("/")
    
    try:
        portfolios = db.get_user_portfolios(email)
        if not portfolios:
            portfolios = []
    except Exception as e:
        print(f"Error fetching portfolios: {e}")
        portfolios = []
    
    content = Div(
        Div(
            H2("💼 Your Portfolio Collection", cls="text-center mb-2 fade-in-up",
               style="font-weight: 800; font-size: 2.5rem;"),
            P("Manage and track your investment portfolios", 
              cls="text-center text-muted mb-5 fade-in-up fade-in-up-delay-1"),
            
            # Portfolio Cards
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                H4(portfolio['name'], cls="card-title text-primary mb-3"),
                                H2(f"${portfolio['cash_balance']:,.2f}", 
                                   cls="text-success mb-3", style="font-weight: 800;"),
                                P(f"ID: {portfolio['portfolio_id']}", 
                                  cls="text-muted small mb-4"),
                                A("👁️ View Details", 
                                  href=f"/portfolio/{portfolio['portfolio_id']}?email={email}", 
                                  cls="btn btn-primary"),
                                cls="card-body text-center"
                            ),
                            cls="card h-100"
                        ),
                        cls=f"col-md-4 mb-4 fade-in-up fade-in-up-delay-{min(i+2, 6)}"
                    ) for i, portfolio in enumerate(portfolios)
                ] if portfolios else [
                    Div(
                        Div(
                            H4("No Portfolios Yet", cls="text-muted mb-3"),
                            P("Create your first portfolio to get started with trading!", 
                              cls="text-muted mb-4"),
                            cls="card-body text-center py-5"
                        ),
                        cls="card col-12 fade-in-up fade-in-up-delay-2"
                    )
                ],
                cls="row mb-5"
            ),
            
            # Create New Portfolio
            Div(
                H4("➕ Create New Portfolio", cls="card-header"),
                Div(
                    Form(
                        # Hidden email field
                        Input(type="hidden", name="email", value=email),
                        
                        Div(
                            Div(
                                Label("Portfolio Name", fr="name", cls="form-label"),
                                Input(
                                    type="text", 
                                    name="name", 
                                    placeholder="e.g., Growth Portfolio, Tech Stocks, etc.", 
                                    cls="form-control",
                                    required=True
                                ),
                                cls="col-md-6 mb-3"
                            ),
                            Div(
                                Label("Initial Cash", fr="cash_balance", cls="form-label"),
                                Input(
                                    type="number", 
                                    name="cash_balance", 
                                    placeholder="10000", 
                                    cls="form-control",
                                    min="100",
                                    step="100",
                                    required=True
                                ),
                                cls="col-md-6 mb-3"
                            ),
                            cls="row"
                        ),
                        Div(
                            Button("✨ Create Portfolio", type="submit", 
                                   cls="btn btn-success btn-lg me-3"),
                            A("← Back to Dashboard", href=f"/dashboard?email={email}", 
                              cls="btn btn-outline-secondary btn-lg"),
                            cls="text-center"
                        ),
                        method="post", 
                        action="/create_portfolio"
                    ),
                    cls="card-body"
                ),
                cls="card fade-in-up fade-in-up-delay-3"
            ),
            
            cls="container py-4"
        )
    )
    
    return create_page_layout("Portfolios", content)

@rt("/create_portfolio", methods=["POST"])
def create_new_portfolio(email: str, name: str, cash_balance: float):
    """Create new portfolio"""
    try:
        portfolio = db.create_portfolio(
            email=email,
            name=name,
            cash_balance=cash_balance,
            created_at=datetime.now()
        )
        
        print(f"✅ Created portfolio: {name} for {email}")
    except Exception as e:
        print(f"❌ Error creating portfolio: {e}")
    
    return RedirectResponse(f"/portfolios?email={email}")

@rt("/transactions")
def transactions_page(email: str = None):
    """Professional transactions page"""
    if not email:
        return RedirectResponse("/")
    
    try:
        result = db.supabase.table('transactions').select('*').eq('email', email).limit(50).order('timestamp', desc=True).execute()
        transactions = result.data if result.data else []
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        transactions = []
    
    content = Div(
        Div(
            H2("📊 Transaction History", cls="text-center mb-2 fade-in-up",
               style="font-weight: 800; font-size: 2.5rem;"),
            P("Complete history of your trading activity", 
              cls="text-center text-muted mb-5 fade-in-up fade-in-up-delay-1"),
            
            # Transactions Table
            Div(
                H4("Recent Transactions", cls="card-header"),
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Date"),
                                Th("Type"),
                                Th("Symbol"),
                                Th("Quantity"),
                                Th("Price"),
                                Th("Total Value"),
                                Th("Portfolio")
                            )
                        ),
                        Tbody(
                            *[
                                Tr(
                                    Td(tx.get('timestamp', 'N/A')[:10] if tx.get('timestamp') else 'N/A'),
                                    Td(
                                        Span(
                                            tx.get('tx_type', 'N/A').upper(),
                                            cls=f"badge bg-{'success' if tx.get('tx_type') == 'buy' else 'danger'}"
                                        )
                                    ),
                                    Td(Strong(tx.get('symbol', 'N/A'))),
                                    Td(f"{abs(tx.get('quantity', 0)):.2f}"),
                                    Td(f"${tx.get('price', 0):.2f}"),
                                    Td(f"${abs(tx.get('quantity', 0) * tx.get('price', 0)):,.2f}"),
                                    Td(tx.get('portfolio_id', 'N/A')[:8] + '...' if tx.get('portfolio_id') else 'N/A')
                                ) for tx in transactions
                            ] if transactions else [
                                Tr(
                                    Td("No transactions found. Start trading to see your history here!", 
                                       colspan="7", cls="text-center text-muted py-4")
                                )
                            ]
                        ),
                        cls="table table-hover mb-0"
                    ),
                    cls="card-body p-0 table-responsive"
                ),
                cls="card fade-in-up fade-in-up-delay-2"
            ),
            
            # Back Button
            Div(
                A("← Back to Dashboard", href=f"/dashboard?email={email}", 
                  cls="btn btn-outline-primary btn-lg mt-4 fade-in-up fade-in-up-delay-3"),
                cls="text-center"
            ),
            
            cls="container py-4"
        )
    )
    
    return create_page_layout("Transactions", content)

# =============================================================================
# START THE SERVER
# =============================================================================

if __name__ == "__main__":
    print("🚀 Starting TradingPro - Professional Trading Platform...")
    print("📱 Visit: http://localhost:5001")
    print("🎯 Modern • Professional • Responsive")
    print("🛑 Press Ctrl+C to stop")
    serve(port=5001)