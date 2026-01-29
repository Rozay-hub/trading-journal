# Trading Journal - Vercel KV Setup Guide

## Step 1: Create Vercel KV Store (Free)
1. Go to https://vercel.com/dashboard > **Storage** tab
2. Click **Create Database** > **KV** (Key-Value)
3. Select ** Hobby** (Free) plan
4. Name: `trading-journal-kv`
5. Click **Create**

## Step 2: Connect KV to Your Project
1. Go to https://vercel.com/rozays-projects/trading_journal/settings/integrations
2. Find your KV store and click **Connect**

## Step 3: Environment Variables
The following will be auto-added:
- `KV_REST_API_URL`
- `KV_REST_API_TOKEN`

## Step 4: Deploy
After connecting, Vercel will auto-redeploy with KV support.

---

## Your Permanent URL (when KV is connected):
**https://tradingjournal-rozays-projects.vercel.app**

## Current Fallback (data resets on restart):
**https://30bb7d9fa7344625-138-68-174-198.serveousercontent.com**

---

## To migrate your 21 trades to KV (after setup):
```bash
python3 migrate_kv.py
```
