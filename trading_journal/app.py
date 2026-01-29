from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from supabase_db import add_trade, get_all_trades, get_stats, delete_trade
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
