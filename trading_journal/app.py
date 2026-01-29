from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from supabase_db import add_trade, get_all_trades, get_stats, delete_trade
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.errorhandler(500)
def internal_error(e):
    return f"Internal Server Error: {str(e)}", 500

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.template_filter('format_date')
def format_date(date_str):
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %H:%M')
        return date_str
    except:
        return str(date_str)

@app.route('/')
def index():
    stats = get_stats()
    today = date.today().isoformat()
    today_stats = get_stats(start_date=today, end_date=today)
    recent_trades = get_all_trades(limit=10)
    return render_template('index.html', stats=stats, today_stats=today_stats, recent_trades=recent_trades)

@app.route('/log', methods=['GET', 'POST'])
def log_trade():
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').strip().upper()
        direction = request.form.get('direction', 'long')
        entry_price = float(request.form.get('entry_price', 0))
        exit_price = float(request.form.get('exit_price', 0))
        size = float(request.form.get('size', 1.0))
        session_notes = request.form.get('session_notes', '').strip()
        
        if symbol and entry_price and exit_price:
            success = add_trade(symbol, direction, entry_price, exit_price, size, session_notes)
            if success:
                flash('Trade logged successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to log trade. Please check your Supabase configuration.', 'error')
        else:
            flash('Please fill in all required fields.', 'error')
    
    return render_template('log.html')

@app.route('/history')
def history():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    symbol = request.args.get('symbol', '').strip().upper()
    
    trades = get_all_trades(limit=100)
    
    # Filter trades
    if start_date:
        trades = [t for t in trades if t.get('created_at', '').startswith(start_date)]
    if end_date:
        trades = [t for t in trades if t.get('created_at', '').startswith(end_date)]
    if symbol:
        trades = [t for t in trades if t.get('symbol', '').upper() == symbol]
    
    stats = get_stats(start_date=start_date, end_date=end_date)
    
    return render_template('history.html', trades=trades, stats=stats, start_date=start_date, end_date=end_date, symbol=symbol)

@app.route('/delete/<int:trade_id>')
def delete(trade_id):
    success = delete_trade(trade_id)
    if success:
        flash('Trade deleted.', 'success')
    else:
        flash('Failed to delete trade.', 'error')
    return redirect(url_for('history'))

@app.route('/api/stats')
def api_stats():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    stats = get_stats(start_date=start_date, end_date=end_date)
    return jsonify(stats)

@app.route('/debug')
def debug():
    import os
    return jsonify({
        'supabase_url_set': bool(os.environ.get('SUPABASE_URL')),
        'supabase_key_set': bool(os.environ.get('SUPABASE_KEY')),
        'supabase_url': os.environ.get('SUPABASE_URL', '')[:20] + '...',
    })

if __name__ == '__main__':
    app.run()
