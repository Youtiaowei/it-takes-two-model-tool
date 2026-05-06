@echo off
chcp 65001 >nul
title 《双人成行》模型替换工具 - 打包程序
cd /d "%~dp0"

echo ╔══════════════════════════════════════════════╗
echo ║   《双人成行》角色模型替换工具             ║
echo ║   Windows 一键打包脚本                      ║
echo ╚══════════════════════════════════════════════╝
echo.

:: ──── 检测 Python ────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 Python！
    echo.
    echo 请先安装 Python 3.11+（安装时勾选 "Add Python to PATH"）：
    echo   下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo ✅ 检测到 Python %PY_VER%

:: ──── 升级 pip ────
echo.
echo 📦 正在更新 pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip 已更新

:: ──── 安装 PyInstaller ────
echo.
echo 📦 正在安装 PyInstaller...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ❌ PyInstaller 安装失败！
    pause
    exit /b 1
)
echo ✅ PyInstaller 安装完成

:: ──── 创建图标个资目录 ────
if not exist assets mkdir assets

:: ──── 开始打包 ────
echo.
echo 🔨 开始打包，请耐心等待（约1-3分钟）...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ItTakesTwo_ModelSwapper" ^
    --noconsole ^
    --noconfirm ^
    --clean ^
    --icon "assets\icon.ico" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --add-data "README.md;." ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 打包失败！请检查上面红色错误信息
    pause
    exit /b 1
)

:: ──── 完成 ────
for %%i in (dist\ItTakesTwo_ModelSwapper.exe) do set EXE_SIZE=%%~zi
set /A EXE_SIZE_MB=%EXE_SIZE% / 1024 / 1024

echo.
echo ╔══════════════════════════════════════════════╗
echo ║   ✅ 打包成功！                             ║
echo ║                                            ║
echo ║   输出: dist\ItTakesTwo_ModelSwapper.exe   ║
echo ║   大小: %EXE_SIZE_MB% MB                         ║
echo ║                                            ║
echo ║   双击 .exe 即可运行！                     ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 💡 提示：首次运行可能被 Windows Defender 拦截，
echo   点击"更多信息" → "仍要运行" 即可
echo.
pause
