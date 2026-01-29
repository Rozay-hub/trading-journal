"""
Supabase database module - minimal version
"""
import os
import requests
from datetime import datetime

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

def is_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY and 'your-project' not in SUPABASE_URL)

def _request(method, path, data=None):
    if not is_configured():
        return None
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    return requests.request(method, url, headers=headers, json=data)

def add_trade(symbol, direction, entry_price, exit_price, size, session_notes=''):
    if not is_configured():
        return False
    
    pnl = (exit_price - entry_price) * size if direction == 'long' else (entry_price - exit_price) * size
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100 if direction == 'long' else ((entry_price - exit_price) / entry_price) * 100
    
    data = {
        'symbol': symbol.upper(),
        'direction': direction,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'size': size,
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'session_notes': session_notes or '',
        'created_at': datetime.utcnow().isoformat(),
        'date_only': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    resp = _request('POST', 'trades', data)
    return resp and resp.status_code in [200, 201]

def get_all_trades(limit=50):
    if not is_configured():
        return []
    
    resp = _request('GET', f'trades?select=*&order=created_at.desc&limit={limit}')
    if resp and resp.status_code == 200:
        return resp.json()
    return []

def get_stats(start_date=None, end_date=None):
    if not is_configured():
        return {
            'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
            'total_pnl': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0,
            'current_streak': 0, 'longest_win_streak': 0, 'longest_loss_streak': 0
        }
    
    query = 'trades?select=pnl,date_only'
    if start_date:
        query += f'&date_only=gte.{start_date}'
    if end_date:
        query += f'&date_only=lte.{end_date}'
    
    resp = _request('GET', query)
    if not resp or resp.status_code != 200:
        return {
            'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
            'total_pnl': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0,
            'current_streak': 0, 'longest_win_streak': 0, 'longest_loss_streak': 0
        }
    
    trades = resp.json()
    if not trades:
        return {
            'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
            'total_pnl': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0,
            'current_streak': 0, 'longest_win_streak': 0, 'longest_loss_streak': 0
        }
    
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

def delete_trade(trade_id):
    if not is_configured():
        return False
    resp = _request('DELETE', f'trades?id=eq.{trade_id}')
    return resp and resp.status_code in [200, 204]
