@echo off
title Cody Mod - Final Pack v3

echo ========================================
echo  Cody (Azusa) Mod - Final .pak Creation
echo ========================================
echo.

set UE4_DIR=F:\Epic\UE_4.26
set PROJECT_DIR=D:\ÎÄµµ\Unreal Projects\ITT_Modding
set GAME_DIR=G:\SteamLibrary\steamapps\common\ItTakesTwo
set PAK_OUTPUT=%PROJECT_DIR%\Cody_Azusa.pak
set PAK_TEMP=C:\PakTemp_Cody
set COOKED=%PROJECT_DIR%\Saved\Cooked\WindowsNoEditor\ITT_Modding\Content

echo [1/3] Prepare temp folder...
if exist "%PAK_TEMP%" rmdir /S /Q "%PAK_TEMP%"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials"
mkdir "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures"

echo [2/3] Copy all cooked files with correct names...
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uasset" /Y
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uexp" /Y
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3_Skeleton.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody_Skeleton.uasset" /Y
copy "%COOKED%\Mods\Meshes\Cody\Azusa_retargeted_v3_Skeleton.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody_Skeleton.uexp" /Y

copy "%COOKED%\Mods\Materials\Cody\M_Azusa_body.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_body.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume_2.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_costume_2.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_emotion.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_emotion.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_hair.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_hair.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_head.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_head.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uexp" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_underwear.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uasset" /Y
copy "%COOKED%\Mods\Materials\Cody\M_Azusa_underwear.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uexp" /Y

copy "%COOKED%\Mods\Textures\Cody\Azusa_body.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_body.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_body.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_costume2.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_emotion.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_hair.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_head.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.ubulk" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uasset" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uexp" /Y
copy "%COOKED%\Mods\Textures\Cody\Azusa_underwear.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.ubulk" /Y

echo [3/3] Generate filelist and create .pak...
set FILELIST=%PAK_TEMP%\filelist.txt
if exist "%FILELIST%" del "%FILELIST%"

echo "../../../Nuts/Content/Characters/Cody/Cody.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uasset" > "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Cody.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Cody_Skeleton.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody_Skeleton.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Cody_Skeleton.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Cody_Skeleton.uexp" >> "%FILELIST%"

echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_body.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_body.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_body.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_costume.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_costume.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_costume_2.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_costume_2.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_costume_2.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_emotion.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_emotion.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_emotion.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_hair.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_hair.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_hair.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_head.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_head.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_head.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_underwear.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Materials/M_Azusa_underwear.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Materials\M_Azusa_underwear.uexp" >> "%FILELIST%"

echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_body.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_body.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_body.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_body.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume2.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume2.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_costume2.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_costume2.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_emotion.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_emotion.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_emotion.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_emotion.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_hair.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_hair.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_hair.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_hair.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_head.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_head.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_head.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_head.ubulk" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_underwear.uasset" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uasset" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_underwear.uexp" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.uexp" >> "%FILELIST%"
echo "../../../Nuts/Content/Characters/Cody/Textures/Azusa_underwear.ubulk" "%PAK_TEMP%\Nuts\Content\Characters\Cody\Textures\Azusa_underwear.ubulk" >> "%FILELIST%"

"%UE4_DIR%\Engine\Binaries\Win64\UnrealPak.exe" "%PAK_OUTPUT%" -Create="%FILELIST%" -Compress

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! PAK created: %PAK_OUTPUT%
    echo ========================================
    if not exist "%GAME_DIR%\Nuts\Content\Paks\~mods" mkdir "%GAME_DIR%\Nuts\Content\Paks\~mods"
    copy /Y "%PAK_OUTPUT%" "%GAME_DIR%\Nuts\Content\Paks\~mods\"
    echo  Installed! Launch It Takes Two to see Azusa!
) else (
    echo UnrealPak error. Check above.
)

echo.
pause
