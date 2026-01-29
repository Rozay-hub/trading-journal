-- Supabase SQL Setup for Trading Journal
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql

-- Create the trades table
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('long', 'short')),
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    size REAL NOT NULL,
    pnl REAL,
    pnl_pct REAL,
    session_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    date_only DATE DEFAULT CURRENT_DATE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(date_only);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trades(created_at DESC);

-- Enable Row Level Security (optional - for protection)
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to read/write trades
-- (Adjust based on your security needs)
CREATE POLICY "Allow public access" ON trades
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Done! Your table is ready.
-- Get your credentials from: Project Settings > API
-- - URL: https://your-project.supabase.co
-- - anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
