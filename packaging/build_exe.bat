@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
pushd "%PROJECT_DIR%" || exit /b 1

python -m pip install -e ".[web,exe]"
if errorlevel 1 goto fail

python -m PyInstaller --clean --noconfirm packaging\Decisive20.spec
if errorlevel 1 goto fail

echo.
echo Build complete: %PROJECT_DIR%\dist\Decisive20\Decisive20.exe
popd
exit /b 0

:fail
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
