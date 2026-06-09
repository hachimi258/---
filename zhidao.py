# ====== 可修改的配置 ======
HOTKEY = '~'                          # 触发快捷键，例如 'ctrl+shift+z'
TYPE_DELAY = 0.02                     # 字符间输入延迟（秒），过小可能丢字
HOTKEY_DELAY = 0.2                    # 按下热键后等待（秒），避免干扰
# ==========================

import os
import time
import ctypes
from ctypes import wintypes
import keyboard

# ---------- Win32 API 模拟 Unicode 输入 ----------
INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP   = 0x0002

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk",         wintypes.WORD),
        ("wScan",       wintypes.WORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM)
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          wintypes.LONG),
        ("dy",          wintypes.LONG),
        ("mouseData",   wintypes.DWORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM)
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg",    wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u",    INPUT_UNION)
    ]

def press_unicode_char(ch: str) -> bool:
    """发送一个 Unicode 字符（按下+释放），返回是否成功"""
    code_point = ord(ch)
    down = INPUT()
    down.type = INPUT_KEYBOARD
    down.u.ki.wVk = 0
    down.u.ki.wScan = code_point
    down.u.ki.dwFlags = KEYEVENTF_UNICODE
    down.u.ki.time = 0
    down.u.ki.dwExtraInfo = 0

    up = INPUT()
    up.type = INPUT_KEYBOARD
    up.u.ki.wVk = 0
    up.u.ki.wScan = code_point
    up.u.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
    up.u.ki.time = 0
    up.u.ki.dwExtraInfo = 0

    events = (INPUT * 2)(down, up)
    ret = ctypes.windll.user32.SendInput(2, events, ctypes.sizeof(INPUT))
    return ret == 2

def type_unicode_string(text: str):
    """逐字输入整个字符串"""
    for ch in text:
        if not press_unicode_char(ch):
            print(f"警告：字符 '{ch}' (U+{ord(ch):04X}) 发送失败")
        time.sleep(TYPE_DELAY)

def get_target_file_path() -> str:
    """返回与脚本同目录下的 zhidao.txt 的完整路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "zhidao.txt")

def read_file_content() -> str:
    target_file = get_target_file_path()
    if not os.path.exists(target_file):
        raise FileNotFoundError(f"文件不存在：{target_file}\n请创建该文件并填入要输入的内容。")
    with open(target_file, "r", encoding="utf-8") as f:
        return f.read()

def on_hotkey():
    try:
        time.sleep(HOTKEY_DELAY)          # 等待热键完全释放
        content = read_file_content()
        print(f"已读取文件，共 {len(content)} 个字符，开始输入...")
        type_unicode_string(content)
        print("输入完成。")
    except Exception as e:
        print(f"错误：{e}")

if __name__ == "__main__":
    print(f"监听热键 '{HOTKEY}'，按下后将输入文件 {get_target_file_path()} 的内容")
    print("请以管理员身份运行本程序，按 Ctrl+C 退出\n")
    keyboard.add_hotkey(HOTKEY, on_hotkey)
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n程序已退出。")
