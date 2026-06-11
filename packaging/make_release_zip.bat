@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
set "VERSION=%~1"
if "%VERSION%"=="" set "VERSION=0.1.0"

pushd "%PROJECT_DIR%" || exit /b 1

set "DIST_DIR=%PROJECT_DIR%\dist\Decisive20"
set "EXE_PATH=%DIST_DIR%\Decisive20.exe"
set "RELEASE_DIR=%PROJECT_DIR%\release"
set "ZIP_PATH=%RELEASE_DIR%\Decisive20-Windows-v%VERSION%.zip"

if not exist "%EXE_PATH%" (
    echo Missing "%EXE_PATH%". Run packaging\build_exe.bat first.
    popd
    exit /b 1
)

if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
if exist "%ZIP_PATH%" del "%ZIP_PATH%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath '%ZIP_PATH%' -CompressionLevel Optimal -ErrorAction Stop"
if errorlevel 1 goto fail

echo.
echo Release zip created: %ZIP_PATH%
echo Upload this file to GitHub Releases.
popd
exit /b 0

:fail
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
