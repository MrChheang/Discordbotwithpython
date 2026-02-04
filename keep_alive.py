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



        Premium Bot Status



            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 50px;
                border-radius: 30px;
                text-align: center;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            .logo {{
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #5865F2, #EB459E);
                border-radius: 30px;
                margin: 0 auto 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 20px 40px rgba(88, 101, 242, 0.4);
                animation: float 3s ease-in-out infinite;
            }}
            @keyframes float {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            .logo svg {{ width: 60px; height: 60px; fill: white; }}
            .status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.2);
                border: 1px solid rgba(16, 185, 129, 0.5);
                padding: 10px 20px;
                border-radius: 50px;
                margin-bottom: 20px;
            }}
            .status-dot {{
                width: 12px;
                height: 12px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
                50% {{ opacity: 0.8; box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
            }}
            .status-text {{ color: #10b981; font-weight: 600; font-size: 14px; }}
            h1 {{ color: white; font-size: 28px; margin-bottom: 10px; font-weight: 700; }}
            .subtitle {{ color: #a0a0b0; font-size: 16px; margin-bottom: 30px; }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 30px;
            }}
            .stat {{
                background: rgba(255, 255, 255, 0.05);
                padding: 20px 15px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .stat-value {{ color: white; font-size: 24px; font-weight: 700; }}
            .stat-label {{ color: #a0a0b0; font-size: 12px; margin-top: 5px; text-transform: uppercase; }}
            .premium-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #f59e0b, #ef4444, #ec4899);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 700;
                color: white;
                margin-top: 30px;
            }}









                OPERATIONAL

            Premium Bot Online
            All systems running smoothly


                    {hours}
                    Hours


                    {minutes}
                    Minutes


                    {seconds}
                    Seconds


            ✨ PREMIUM BOT




    '''

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'uptime': str(datetime.now(timezone.utc) - start_time)}})

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Premium web server started on port 8080")