# Trading Journal - Supabase Setup Guide

## Step 1: Create Free Supabase Account
1. Go to https://supabase.com
2. Sign up (free - no credit card)
3. Create a new project
4. Wait ~1 minute for the project to provision

## Step 2: Get Your Credentials
1. Go to **Project Settings** (⚙️ icon) > **API**
2. Copy:
   - **Project URL** (e.g., `https://xyzabc123.supabase.co`)
   - **anon public key** (starts with `eyJ...`)

## Step 3: Set Up Database Table
1. Go to **SQL Editor** in Supabase
2. Copy & paste contents of `supabase_setup.sql`
3. Click **Run** to create the table

## Step 4: Set Environment Variables

### For Vercel Deployment:
1. Go to https://vercel.com/rozays-projects/trading_journal/settings/environment-variables
2. Add:
   - `SUPABASE_URL` = your Project URL
   - `SUPABASE_KEY` = your anon public key
3. Redeploy the app

### For Local Development:
Create a `.env` file:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 5: Import Your Existing Trades
Run this to import from your current SQLite database:
```bash
python3 migrate_to_supabase.py
```

## That's It! 🎉
Your trades will now persist permanently across deploys.
