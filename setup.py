#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署脚本 - 自动检测 Python 环境、安装依赖、配置 run.bat
用法：在文件夹中双击运行此脚本，或执行 `python setup.py`
"""

import os
import sys
import subprocess
import shutil

TEMPLATE_BAT = r"""@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在请求管理员权限...
    set "vbs=%temp%\getadmin.vbs"
    echo Set UAC = CreateObject^("Shell.Application"^) > "%vbs%"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%vbs%"
    "%vbs%"
    del "%vbs%"
    exit /b
)

cd /d "%~dp0"
REM 下面这行中的 PYTHON_CMD_PLACEHOLDER 会被替换为实际的 Python 路径
PYTHON_CMD_PLACEHOLDER zhidao.py
if errorlevel 1 (
    echo 运行出错，按任意键退出...
    pause
    exit /b 1
)
pause
"""

def find_python():
    """返回可用的 Python 解释器路径（优先使用当前脚本的 Python）"""
    # 优先使用当前运行的 python
    current_python = sys.executable
    if current_python and os.path.isfile(current_python):
        return current_python
    # 否则在 PATH 中查找
    for cmd in ['python', 'python3']:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def install_keyboard(python_path):
    """通过 pip 安装 keyboard 库（使用清华源，--user 避免权限）"""
    print("正在检查 keyboard 库...")
    try:
        subprocess.run(
            [python_path, '-c', 'import keyboard'],
            check=True, capture_output=True, text=True
        )
        print("keyboard 库已安装。")
        return True
    except subprocess.CalledProcessError:
        print("keyboard 库未安装，正在从清华源安装...")
        try:
            subprocess.run(
                [python_path, '-m', 'pip', 'install', '--user',
                 '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple', 'keyboard'],
                check=True
            )
            print("安装成功。")
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装失败：{e}")
            print("请手动执行：pip install keyboard")
            return False

def ensure_zhidao_txt():
    """确保 zhidao.txt 存在，若不存在则创建一个示例文件"""
    txt_path = os.path.join(os.path.dirname(__file__), 'zhidao.txt')
    if not os.path.exists(txt_path):
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("这是示例内容，请替换为你需要输入的文字。\n支持中文和特殊符号。")
        print(f"已创建示例文件：{txt_path}")
        print("请编辑该文件，填入你要自动输入的内容。")
    else:
        print(f"文件已存在：{txt_path}")

def configure_run_bat(python_path):
    """修改 run.bat 中的 Python 路径，如果不存在则创建"""
    bat_path = os.path.join(os.path.dirname(__file__), 'run.bat')
    backup_path = bat_path + '.bak'

    # 备份原 run.bat（如果存在且不是备份本身）
    if os.path.exists(bat_path) and not os.path.exists(backup_path):
        shutil.copy2(bat_path, backup_path)
        print(f"已备份原 run.bat 到 {backup_path}")

    # 生成新的 run.bat 内容，替换占位符
    new_content = TEMPLATE_BAT.replace('PYTHON_CMD_PLACEHOLDER', f'"{python_path}"')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"已配置 run.bat，使用 Python 路径：{python_path}")

def main():
    print("===== 知到智慧树工具部署脚本 =====")
    print("正在检测 Python 环境...")
    python_path = find_python()
    if not python_path:
        print("错误：未找到 Python。请确保 Python 已安装并添加到 PATH。")
        input("按 Enter 退出...")
        sys.exit(1)
    print(f"找到 Python：{python_path}")

    # 安装依赖
    if not install_keyboard(python_path):
        print("依赖安装失败，请检查网络或手动安装。")
        input("按 Enter 退出...")
        sys.exit(1)

    # 确保输入文件存在
    ensure_zhidao_txt()

    # 配置 run.bat
    configure_run_bat(python_path)

    print("\n部署完成！")
    print("使用方法：")
    print("1. 编辑 zhidao.txt，填入你要自动输入的内容。")
    print("2. 双击 run.bat（将以管理员身份运行）。")
    print("3. 按下快捷键（默认 ~ 键），即可将文件内容输入到当前光标位置。")
    input("\n按 Enter 退出...")

if __name__ == "__main__":
    main()
