from flask import Flask
from threading import Thread
from datetime import datetime, timezone

app = Flask('')
start_time = datetime.now(timezone.utc)

@app.route('/')
def home():
    uptime = datetime.now(timezone.utc) - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'<h1>Bot is Running</h1><p>Uptime: {hours}h {minutes}m {seconds}s</p>'

@app.route('/health')
def health():
    return {'status': 'ok'}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Web server started on port 8080")