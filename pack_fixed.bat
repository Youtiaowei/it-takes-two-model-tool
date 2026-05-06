@echo off
title Cody Mod - Fixed Pack

echo ========================================
echo  Cody Mod - Corrected .pak Creator
echo ========================================
echo.

set UE4_DIR=F:\Epic\UE_4.26
set COOKED=D:\ÎÄµµ\Unreal Projects\ITT_Modding\Saved\Cooked\WindowsNoEditor\ITT_Modding\Content
set GAME_DIR=G:\SteamLibrary\steamapps\common\ItTakesTwo
set PAK_OUT=D:\ÎÄµµ\Unreal Projects\ITT_Modding\Cody_Azusa.pak
set T=C:\PakTemp_Cody

echo [1/3] Prepare temp...
if exist "%T%" rmdir /S /Q "%T%"
mkdir "%T%\Nuts\Content\Characters\Cody\Materials"
mkdir "%T%\Nuts\Content\Characters\Cody\Textures"

echo [2/3] Copy files...
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3.uasset" "%T%\Nuts\Content\Characters\Cody\Cody.uasset" /Y
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3.uexp" "%T%\Nuts\Content\Characters\Cody\Cody.uexp" /Y

REM Skeleton with ORIGINAL name (CRITICAL - game needs this name!)
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3_Skeleton.uasset" "%T%\Nuts\Content\Characters\Cody\Azusa_retargeted_v3_Skeleton.uasset" /Y
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3_Skeleton.uexp" "%T%\Nuts\Content\Characters\Cody\Azusa_retargeted_v3_Skeleton.uexp" /Y

copy "%COOKED%\Mods\Materials\Cody\M_Azusa_body.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_body.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume_2.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume_2.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_emotion.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_emotion.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_hair.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_hair.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_head.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_head.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_underwear.uasset" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_underwear.uexp" "%T%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uexp" /Y

copy "%COOKED%\Mods\Textures\Cody\Azusa_body.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_body.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_body.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_body.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_head.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.uasset" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.uexp" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.ubulk" "%T%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.ubulk" /Y

echo.
echo Checking that both mesh AND skeleton exist:
if exist "%T%\Nuts\Content\Characters\Cody\Cody.uasset" (echo  Mesh: Cody.uasset OK) else (echo  Mesh: MISSING!)
if exist "%T%\Nuts\Content\Characters\Cody\Azusa_retargeted_v3_Skeleton.uasset" (echo  Skeleton: Azusa_retargeted_v3_Skeleton.uasset OK) else (echo  Skeleton: MISSING!)

echo.
echo [3/3] Create filelist and pack...
set MP=..\..\..\Nuts\Content\Characters\Cody\
set FL=%T%\fl.txt
if exist "%FL%" del "%FL%"

echo "%T%\Nuts\Content\Characters\Cody\Cody.uasset" "%MP%Cody.uasset" > "%FL%"
echo "%T%\Nuts\Content\Characters\Cody\Cody.uexp" "%MP%Cody.uexp" >> "%FL%"
echo "%T%\Nuts\Content\Characters\Cody\Azusa_retargeted_v3_Skeleton.uasset" "%MP%Azusa_retargeted_v3_Skeleton.uasset" >> "%FL%"
echo "%T%\Nuts\Content\Characters\Cody\Azusa_retargeted_v3_Skeleton.uexp" "%MP%Azusa_retargeted_v3_Skeleton.uexp" >> "%FL%"

for %%f in (M_Azusa_body M_Azusa_costume M_Azusa_costume_2 M_Azusa_emotion M_Azusa_hair M_Azusa_head M_Azusa_underwear) do (
    echo "%T%\Nuts\Content\Characters\Cody\Materials\%%f.uasset" "%MP%Materials\%%f.uasset" >> "%FL%"
    echo "%T%\Nuts\Content\Characters\Cody\Materials\%%f.uexp" "%MP%Materials\%%f.uexp" >> "%FL%"
)

for %%f in (Azusa_body Azusa_costume Azusa_costume2 Azusa_emotion Azusa_hair Azusa_head Azusa_underwear) do (
    echo "%T%\Nuts\Content\Characters\Cody\Textures\%%f.uasset" "%MP%Textures\%%f.uasset" >> "%FL%"
    echo "%T%\Nuts\Content\Characters\Cody\Textures\%%f.uexp" "%MP%Textures\%%f.uexp" >> "%FL%"
    echo "%T%\Nuts\Content\Characters\Cody\Textures\%%f.ubulk" "%MP%Textures\%%f.ubulk" >> "%FL%"
)

"%UE4_DIR%\Engine\Binaries\Win64\UnrealPak.exe" "%PAK_OUT%" -Create="%FL%" -Compress

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo  PAK Created! Installing to game...
    echo ========================================
    if not exist "%GAME_DIR%\Nuts\Content\Paks\~mods" mkdir "%GAME_DIR%\Nuts\Content\Paks\~mods"
    copy /Y "%PAK_OUT%" "%GAME_DIR%\Nuts\Content\Paks\~mods\"
    echo  Done! Launch the game!
)

echo.
pause
