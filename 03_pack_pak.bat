@echo off
title Cody Mod - Pack v2

echo ========================================
echo  Cody (Azusa) Mod - Create .pak (v2)
echo ========================================
echo.

set UE4_DIR=F:\Epic\UE_4.26
set PROJECT_DIR=D:\�ĵ�\Unreal Projects\ITT_Modding
set GAME_DIR=G:\SteamLibrary\steamapps\common\ItTakesTwo
set PAK_OUTPUT=%PROJECT_DIR%\Cody_Azusa.pak
set PAK_TEMP=C:\PakTemp_Cody
set COOKED_DIR=%PROJECT_DIR%\Saved\Cooked\WindowsNoEditor\ITT_Modding\Content

echo [1/3] Preparing file structure...
if exist "%PAK_TEMP%" rmdir /S /Q "%PAK_TEMP%"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures"

echo [2/3] Copying cooked files...
copy "%COOKED_DIR%\Mods\Meshes\Cody\Azusa_retargeted_v3.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uasset" /Y
copy "%COOKED_DIR%\Mods\Meshes\Cody\Azusa_retargeted_v3.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uexp" /Y
copy "%COOKED_DIR%\Mods\Meshes\Cody\cody_original_test_Skeleton.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody_Skeleton.uasset" /Y

if exist "%COOKED_DIR%\Mods\Meshes\Cody\Azusa_retargeted_v3.ubulk" (
    copy "%COOKED_DIR%\Mods\Meshes\Cody\Azusa_retargeted_v3.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.ubulk" /Y
)

for %%f in (M_Azusa_underwear M_Azusa_body M_Azusa_costume M_Azusa_costume_2 M_Azusa_hair M_Azusa_head M_Azusa_emotion) do (
    if exist "%COOKED_DIR%\Mods\Materials\Cody\%%f.uasset" copy "%COOKED_DIR%\Mods\Materials\Cody\%%f.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\%%f.uasset" /Y
    if exist "%COOKED_DIR%\Mods\Materials\Cody\%%f.uexp" copy "%COOKED_DIR%\Mods\Materials\Cody\%%f.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\%%f.uexp" /Y
)

for %%f in (T_Azusa_underwear T_Azusa_body T_Azusa_costume T_Azusa_costume2 T_Azusa_emotion T_Azusa_hair T_Azusa_head) do (
    if exist "%COOKED_DIR%\Mods\Textures\Cody\%%f.uasset" copy "%COOKED_DIR%\Mods\Textures\Cody\%%f.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\%%f.uasset" /Y
    if exist "%COOKED_DIR%\Mods\Textures\Cody\%%f.uexp" copy "%COOKED_DIR%\Mods\Textures\Cody\%%f.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\%%f.uexp" /Y
)

dir "%PAK_TEMP%\Nuts\Content\Characters\Cody\"

echo.
echo [3/3] Creating .pak file using directory...

"%UE4_DIR%\Engine\Binaries\Win64\UnrealPak.exe" "%PAK_OUTPUT%" -Create="%PAK_TEMP%\Nuts\Content\Characters\Cody\*" -Compress -Recurse

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo  PAK created: %PAK_OUTPUT%
    echo ========================================
    echo.
    echo To install: copy to game mods folder...
    if not exist "%GAME_DIR%\Nuts\Content\Paks\~mods" mkdir "%GAME_DIR%\Nuts\Content\Paks\~mods"
    copy /Y "%PAK_OUTPUT%" "%GAME_DIR%\Nuts\Content\Paks\~mods\"
    echo.
    echo  Done! Launch It Takes Two to see Azusa!
) else (
    echo.
    echo  UnrealPak error. Check output above.
)

echo.
pause
