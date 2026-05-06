@echo off
title UnrealPak Test - Single File

echo Check if Cody.uasset exists:
if exist "C:\PakTemp_Cody\Nuts\Content\Characters\Cody\Cody.uasset" (
    echo YES - file exists at: C:\PakTemp_Cody\Nuts\Content\Characters\Cody\Cody.uasset
    dir "C:\PakTemp_Cody\Nuts\Content\Characters\Cody\Cody.uasset"
) else (
    echo NO - file NOT found!
    echo Current directory: %cd%
    dir "C:\PakTemp_Cody\Nuts\Content\Characters\Cody\" 2>nul || echo Cannot list directory
    pause
    exit /b 1
)

echo.
echo Create filelist with 1 entry...
echo "../../../Nuts/Content/Characters/Cody/Cody.uasset" "C:\PakTemp_Cody\Nuts\Content\Characters\Cody\Cody.uasset" > "C:\PakTemp_Cody\test_single.txt"
echo Done.

echo.
echo Run UnrealPak with single file...
"F:\Epic\UE_4.26\Engine\Binaries\Win64\UnrealPak.exe" "C:\PakTemp_Cody\test_single.pak" -Create="C:\PakTemp_Cody\test_single.txt" -Compress

echo.
echo Check if pak was created:
if exist "C:\PakTemp_Cody\test_single.pak" (
    echo YES - pak created
    dir "C:\PakTemp_Cody\test_single.pak"
) else (
    echo NO - pak NOT created
)

echo.
pause
