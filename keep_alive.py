from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return '''
    
    
    
        Discord Bot Status
        
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .container {
                background: white;
                padding: 40px 60px;
                border-radius: 20px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                text-align: center;
            }
            .status {
                width: 20px;
                height: 20px;
                background: #10b981;
                border-radius: 50%;
                display: inline-block;
                margin-right: 10px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            h1 { color: #1f2937; margin: 0 0 10px 0; }
            p { color: #6b7280; margin: 0; }
        
    
    
        
            Bot is Online!
            Discord bot is running successfully.
        
    

    
    '''

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Web server started on port 8080")