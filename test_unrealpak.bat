@echo off
title UnrealPak Test

echo Creating minimal test PAK with 1 file...

set UE4_DIR=F:\Epic\UE_4.26
set TEST_FILE=C:\PakTemp_Cody\Nuts\Content\Characters\Cody\Cody.uasset
set OUTPUT=D:\文档\Unreal Projects\ITT_Modding\test_pak.pak

echo File to pack: %TEST_FILE%
if exist "%TEST_FILE%" (
    echo File EXISTS on disk
    echo File size:
    dir "%TEST_FILE%"
) else (
    echo File NOT FOUND!
    pause
    exit /b 1
)

echo.
echo Running UnrealPak with single file...
echo "%OUTPUT%" -Create="%TEST_FILE%" -Compress

"%UE4_DIR%\Engine\Binaries\Win64\UnrealPak.exe" "%OUTPUT%" -Create="%TEST_FILE%" -Compress

echo.
echo Done. Check test_pak.pak in project folder.
pause
