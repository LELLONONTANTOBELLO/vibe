from flask import Flask, render_template_string, jsonify, request
import requests as http_requests
import time
import threading

app = Flask(__name__)

SERVER_URL = "https://www.crashando.it/vibe/vibra.php"

PATTERNS = {
    'a': '1 vibration',
    'b': '2 vibrations', 
    'c': '3 vibrations',
    'd': '4 vibrations'
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibration Controller</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }
        
        .status {
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 30px;
            font-size: 14px;
            min-height: 20px;
        }
        
        .status.success {
            color: #51cf66;
        }
        
        .status.error {
            color: #ff6b6b;
        }
        
        .section-title {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 30px;
        }
        
        .btn {
            background: white;
            border: none;
            border-radius: 12px;
            padding: 20px;
            font-size: 16px;
            font-weight: bold;
            color: #667eea;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .btn span {
            display: block;
            font-size: 12px;
            font-weight: normal;
            color: #888;
            margin-top: 5px;
        }
        
        .poll-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
        }
        
        .poll-btn {
            width: 100%;
            padding: 15px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .poll-btn.start {
            background: #51cf66;
            color: white;
        }
        
        .poll-btn.stop {
            background: #ff6b6b;
            color: white;
        }
        
        .poll-status {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 10px;
            font-size: 12px;
        }
        
        .last-received {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            text-align: center;
            color: white;
            font-size: 14px;
        }
        
        .info-box {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Vibration Controller</h1>
        <div id="status" class="status">Ready</div>
        
        <div class="section-title">SEND VIBRATION TO ALL</div>
        <div class="button-grid">
            <button class="btn" onclick="sendVibration('a')">A<span>1 vib</span></button>
            <button class="btn" onclick="sendVibration('b')">B<span>2 vib</span></button>
            <button class="btn" onclick="sendVibration('c')">C<span>3 vib</span></button>
            <button class="btn" onclick="sendVibration('d')">D<span>4 vib</span></button>
        </div>
        
        <div class="poll-section">
            <div class="section-title">RECEIVE VIBRATIONS</div>
            <button id="pollBtn" class="poll-btn start" onclick="togglePolling()">START POLLING</button>
            <div id="pollStatus" class="poll-status">Polling stopped</div>
            <div id="lastReceived" class="last-received" style="display: none;"></div>
        </div>
        
        <div class="info-box">
            This is a web version of the Android Vibration Controller app.
            It connects to the same server but cannot vibrate your device 
            (browser limitation).
        </div>
    </div>
    
    <script>
        let isPolling = false;
        let pollInterval = null;
        let lastVibrateId = null;
        
        async function sendVibration(pattern) {
            const statusEl = document.getElementById('status');
            statusEl.textContent = 'Sending...';
            statusEl.className = 'status';
            
            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pattern: pattern})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusEl.textContent = `OK ${pattern.toUpperCase()} sent!`;
                    statusEl.className = 'status success';
                } else {
                    statusEl.textContent = 'Error: ' + (data.error || 'Unknown error');
                    statusEl.className = 'status error';
                }
                
                setTimeout(() => {
                    statusEl.textContent = 'Ready';
                    statusEl.className = 'status';
                }, 2000);
                
            } catch (error) {
                statusEl.textContent = 'Error: ' + error.message;
                statusEl.className = 'status error';
            }
        }
        
        function togglePolling() {
            const btn = document.getElementById('pollBtn');
            const pollStatus = document.getElementById('pollStatus');
            
            if (isPolling) {
                isPolling = false;
                clearInterval(pollInterval);
                btn.textContent = 'START POLLING';
                btn.className = 'poll-btn start';
                pollStatus.textContent = 'Polling stopped';
            } else {
                isPolling = true;
                btn.textContent = 'STOP POLLING';
                btn.className = 'poll-btn stop';
                pollStatus.textContent = 'Listening for vibrations...';
                poll();
                pollInterval = setInterval(poll, 150);
            }
        }
        
        async function poll() {
            try {
                const response = await fetch('/poll');
                const data = await response.json();
                
                if (data.pattern && data.id !== lastVibrateId) {
                    lastVibrateId = data.id;
                    const lastReceived = document.getElementById('lastReceived');
                    lastReceived.style.display = 'block';
                    lastReceived.textContent = `Received: Pattern ${data.pattern.toUpperCase()}`;
                    
                    if ('vibrate' in navigator) {
                        const patterns = {
                            'a': [400],
                            'b': [400, 200, 400],
                            'c': [400, 200, 400, 200, 400],
                            'd': [400, 200, 400, 200, 400, 200, 400]
                        };
                        navigator.vibrate(patterns[data.pattern] || [400]);
                    }
                }
            } catch (error) {
                console.error('Poll error:', error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send', methods=['POST'])
def send_vibration():
    try:
        data = request.get_json()
        pattern = data.get('pattern', 'a')
        
        response = http_requests.post(
            SERVER_URL,
            data={'vibrate': pattern},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': f'Server returned {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/poll')
def poll():
    try:
        response = http_requests.get(
            f'{SERVER_URL}?poll&t={int(time.time() * 1000)}',
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
