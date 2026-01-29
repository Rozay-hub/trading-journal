"""
SQLite database module for Trading Journal
With fallback for ephemeral filesystems (Vercel)
"""
import sqlite3
import os
from datetime import datetime

DATABASE = os.environ.get('DATABASE_PATH', '/tmp/trades.db')

_db_initialized = False

@staticmethod
def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    global _db_initialized
    if _db_initialized:
        return True
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('long', 'short')),
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                size REAL NOT NULL,
                pnl REAL,
                pnl_pct REAL,
                session_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_only TEXT DEFAULT (strftime('%Y-%m-%d', 'now'))
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(date_only)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)')
        conn.commit()
        conn.close()
        _db_initialized = True
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

def calculate_pnl(entry, exit_price, direction, size):
    if direction == 'long':
        return (exit_price - entry) * size
    else:
        return (entry - exit_price) * size

def calculate_pnl_pct(entry, exit_price, direction):
    if direction == 'long':
        return ((exit_price - entry) / entry) * 100
    else:
        return ((entry - exit_price) / entry) * 100

def add_trade(symbol, direction, entry_price, exit_price, size, session_notes=''):
    if not init_db():
        return False
    
    pnl = calculate_pnl(entry_price, exit_price, direction, size)
    pnl_pct = calculate_pnl_pct(entry_price, exit_price, direction)
    date_only = datetime.utcnow().strftime('%Y-%m-%d')
    created_at = datetime.utcnow().isoformat()
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute('''
            INSERT INTO trades (symbol, direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol.upper(), direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Add trade error: {e}")
        return False

def get_all_trades(limit=50):
    if not init_db():
        return []
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.execute('SELECT * FROM trades ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except:
        return []

def get_trades_by_date(start_date=None, end_date=None):
    if not init_db():
        return []
    
    query = 'SELECT * FROM trades WHERE 1=1'
    params = []
    
    if start_date:
        query += ' AND date_only >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date_only <= ?'
        params.append(end_date)
    
    query += ' ORDER BY created_at DESC'
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except:
        return []

def get_stats(start_date=None, end_date=None):
    trades = get_trades_by_date(start_date, end_date)
    
    if not trades:
        return {
            'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
            'total_pnl': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0,
            'current_streak': 0, 'longest_win_streak': 0, 'longest_loss_streak': 0
        }
    
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    
    total_pnl = sum(t['pnl'] for t in trades)
    avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
    
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    
    # Calculate streaks
    streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    current_streak_type = None
    current_streak = 0
    
    for t in trades:
        is_win = t['pnl'] > 0
        if is_win:
            if current_streak_type == 'win':
                current_streak += 1
            else:
                if current_streak_type == 'loss':
                    max_loss_streak = max(max_loss_streak, current_streak)
                current_streak_type = 'win'
                current_streak = 1
            max_win_streak = max(max_win_streak, current_streak)
        else:
            if current_streak_type == 'loss':
                current_streak += 1
            else:
                if current_streak_type == 'win':
                    max_win_streak = max(max_win_streak, current_streak)
                current_streak_type = 'loss'
                current_streak = 1
            max_loss_streak = max(max_loss_streak, current_streak)
    
    return {
        'total_trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': round((len(wins) / len(trades)) * 100, 1) if trades else 0,
        'total_pnl': round(total_pnl, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'profit_factor': round(gross_profit / gross_loss, 2) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0,
        'current_streak': current_streak if current_streak_type == 'win' else -current_streak if current_streak_type == 'loss' else 0,
        'longest_win_streak': max_win_streak,
        'longest_loss_streak': max_loss_streak
    }

def delete_trade(trade_id):
    if not init_db():
        return False
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False
