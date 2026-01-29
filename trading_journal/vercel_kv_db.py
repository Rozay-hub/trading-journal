"""
Vercel KV (Redis) database module for Trading Journal
"""
import os
from datetime import datetime

try:
    from vercel_kv import kv
    KV_AVAILABLE = True
except ImportError:
    KV_AVAILABLE = False

def is_configured():
    """Check if KV is configured"""
    if not KV_AVAILABLE:
        return False
    try:
        # Test connection
        kv.get('test_key')
        return True
    except:
        return False

def _get_date_only():
    return datetime.utcnow().strftime('%Y-%m-%d')

def add_trade(symbol, direction, entry_price, exit_price, size, session_notes=''):
    """Add a new trade to KV"""
    if not is_configured():
        return False
    
    from datetime import datetime
    
    pnl = (exit_price - entry_price) * size if direction == 'long' else (entry_price - exit_price) * size
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100 if direction == 'long' else ((entry_price - exit_price) / entry_price) * 100
    
    trade = {
        'symbol': symbol.upper(),
        'direction': direction,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'size': size,
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'session_notes': session_notes or '',
        'created_at': datetime.utcnow().isoformat(),
        'date_only': _get_date_only()
    }
    
    # Store trade and add to list
    trade_id = f"trade_{datetime.utcnow().timestamp()}"
    kv.set(trade_id, trade)
    
    # Add to trades list
    trades = kv.get('trades') or []
    trades.append(trade_id)
    kv.set('trades', trades)
    
    return True

def get_all_trades(limit=50):
    """Get all trades from KV"""
    if not is_configured():
        return []
    
    trade_ids = kv.get('trades') or []
    trades = []
    for tid in trade_ids[-limit:]:
        trade = kv.get(tid)
        if trade:
            trade['id'] = tid
            trades.append(trade)
    return trades[::-1]  # Most recent first

def get_stats(start_date=None, end_date=None):
    """Get trading statistics from KV"""
    if not is_configured():
        return _empty_stats()
    
    trades = get_all_trades(100)
    
    # Filter by date
    if start_date:
        trades = [t for t in trades if t.get('date_only', '') >= start_date]
    if end_date:
        trades = [t for t in trades if t.get('date_only', '') <= end_date]
    
    if not trades:
        return _empty_stats()
    
    pnl_list = [t['pnl'] for t in trades]
    wins = [p for p in pnl_list if p > 0]
    losses = [p for p in pnl_list if p <= 0]
    
    total_pnl = sum(pnl_list)
    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0
    
    return {
        'total_trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': round((len(wins) / len(trades)) * 100, 1) if trades else 0,
        'total_pnl': round(total_pnl, 2),
        'avg_win': round(sum(wins) / len(wins), 2) if wins else 0,
        'avg_loss': round(sum(losses) / len(losses), 2) if losses else 0,
        'profit_factor': round(gross_profit / gross_loss, 2) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0,
        'current_streak': 0,
        'longest_win_streak': 0,
        'longest_loss_streak': 0
    }

def _empty_stats():
    return {
        'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
        'total_pnl': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0,
        'current_streak': 0, 'longest_win_streak': 0, 'longest_loss_streak': 0
    }

def delete_trade(trade_id):
    """Delete a trade from KV"""
    if not is_configured():
        return False
    
    # Remove from list
    trades = kv.get('trades') or []
    trades = [t for t in trades if t != trade_id]
    kv.set('trades', trades)
    
    # Delete trade
    kv.delete(trade_id)
    return True

def init_db():
    """Initialize database"""
    return is_configured()
