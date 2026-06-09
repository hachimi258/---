@echo off
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
REM 下面这行中的 PYTHON_CMD_PLACEHOLDER 会被 setup.py 自动替换为正确的 Python 路径
PYTHON_CMD_PLACEHOLDER zhidao.py
if errorlevel 1 (
    echo 运行出错，按任意键退出...
    pause
    exit /b 1
)
pause
