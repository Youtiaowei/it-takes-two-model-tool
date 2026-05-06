@echo off
title Cody Mod - Check Cooked Files

echo ========================================
echo  Check cooked files in project
echo ========================================
echo.

set PROJECT_DIR=D:\文档\Unreal Projects\ITT_Modding
set COOKED_DIR=%PROJECT_DIR%\Saved\Cooked\WindowsNoEditor\ITT_Modding\Content

echo === Cooked Meshes/Cody ===
dir "%COOKED_DIR%\Mods\Meshes\Cody\"

echo.
echo === Cooked Materials/Cody ===
dir "%COOKED_DIR%\Mods\Materials\Cody\"

echo.
echo === Cooked Textures/Cody ===
dir "%COOKED_DIR%\Mods\Textures\Cody\"

echo.
pause
