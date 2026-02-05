from flask import Flask, jsonify
from threading import Thread
from datetime import datetime, timezone

app = Flask('')
start_time = datetime.now(timezone.utc)

@app.route('/')
def home():
    uptime = datetime.now(timezone.utc) - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Status</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: rgba(255,255,255,0.05);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
            }}
            .status {{ color: #10b981; font-size: 14px; margin-bottom: 10px; }}
            h1 {{ color: white; margin-bottom: 20px; }}
            .uptime {{ color: #a0a0a0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">● ONLINE</div>
            <h1>Bot is Running</h1>
            <p class="uptime">{hours}h {minutes}m {seconds}s</p>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return jsonify({{'status': 'ok'}})

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Web server started on port 8080")