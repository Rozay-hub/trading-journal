#!/usr/bin/env python3
"""
Migrate trades from SQLite to Vercel KV
"""
import sqlite3
from datetime import datetime

try:
    from vercel_kv import kv
    KV_AVAILABLE = True
except ImportError:
    KV_AVAILABLE = False

SQLITE_DB = '/root/clawd/trading_journal/trades.db'

def parse_date(s):
    if not s:
        return datetime.utcnow().isoformat()
    if isinstance(s, str):
        try:
            return datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S').isoformat()
        except:
            return datetime.utcnow().isoformat()
    return s.isoformat() if hasattr(s, 'isoformat') else datetime.utcnow().isoformat()

def migrate():
    if not KV_AVAILABLE:
        print("❌ vercel-kv not installed. Run: pip install vercel-kv")
        return
    
    # Check if KV is configured
    try:
        test = kv.get('test')
    except Exception as e:
        print(f"❌ KV not configured: {e}")
        print("   Make sure KV_REST_API_URL and KV_REST_API_TOKEN are set")
        return
    
    print("Connected to KV ✓")
    
    # Read from SQLite
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cur.execute('SELECT symbol, direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only FROM trades')
    trades = cur.fetchall()
    conn.close()
    
    print(f"Found {len(trades)} trades to migrate")
    
    # Clear existing
    existing = kv.get('trades') or []
    for tid in existing:
        kv.delete(tid)
    kv.delete('trades')
    
    migrated = 0
    for trade in trades:
        symbol, direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only = trade
        
        trade_id = f"trade_{created_at}" if created_at else f"trade_{datetime.utcnow().timestamp()}"
        
        data = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'session_notes': session_notes or '',
            'created_at': parse_date(created_at),
            'date_only': str(date_only) if date_only else datetime.utcnow().strftime('%Y-%m-%d')
        }
        
        kv.set(trade_id, data)
        
        # Add to list
        trades_list = kv.get('trades') or []
        trades_list.append(trade_id)
        kv.set('trades', trades_list)
        
        print(f"✓ {symbol} ${pnl:.2f}")
        migrated += 1
    
    print(f"\n✅ Migrated {migrated} trades to Vercel KV!")

if __name__ == '__main__':
    migrate()
