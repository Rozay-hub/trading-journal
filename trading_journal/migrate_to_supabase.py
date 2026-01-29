#!/usr/bin/env python3
"""
Migrate trades from SQLite to Supabase
"""
import sqlite3
from supabase import create_client
from datetime import datetime
import os

# Supabase credentials (set these or use environment variables)
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

SQLITE_DB = '/root/clawd/trading_journal/trades.db'

def parse_date(s):
    """Parse date string to ISO format"""
    if not s:
        return datetime.utcnow().isoformat()
    if isinstance(s, str):
        try:
            dt = datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
            return dt.isoformat()
        except:
            return datetime.utcnow().isoformat()
    elif hasattr(s, 'isoformat'):
        return s.isoformat()
    return datetime.utcnow().isoformat()

def migrate():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("   Example:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_KEY='your-anon-key'")
        return
    
    print("Connecting to Supabase...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Read from SQLite
    print(f"Reading from {SQLITE_DB}...")
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cur.execute('SELECT symbol, direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only FROM trades')
    trades = cur.fetchall()
    conn.close()
    
    print(f"Found {len(trades)} trades to migrate")
    
    migrated = 0
    errors = 0
    
    for trade in trades:
        symbol, direction, entry_price, exit_price, size, pnl, pnl_pct, session_notes, created_at, date_only = trade
        
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
        
        try:
            result = client.table('trades').insert(data).execute()
            if result.data:
                migrated += 1
                print(f"✓ {symbol} {direction} ${pnl:.2f}")
        except Exception as e:
            errors += 1
            print(f"✗ Error importing {symbol}: {e}")
    
    print(f"\n✅ Migration complete!")
    print(f"   Migrated: {migrated}")
    print(f"   Errors: {errors}")

if __name__ == '__main__':
    migrate()
