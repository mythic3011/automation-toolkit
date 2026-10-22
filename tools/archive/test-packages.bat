@echo off
REM Test each package after restructure
REM This verifies that each package can be used independently

echo ================================================
echo Package Testing Suite
echo ================================================
echo.

echo [TEST 1/4] Testing fmtools...
echo.
if exist packages\fmtools\pyproject.toml (
    echo   Checking Python package structure...
    cd packages\fmtools
    
    if exist src\fmtools\__init__.py (
        echo   [PASS] Python package structure is valid
    ) else (
        echo   [FAIL] Missing __init__.py in src/fmtools/
    )
    
    if exist install.sh (
        echo   [PASS] Installation script found
    ) else (
        echo   [WARN] install.sh not found
    )
    
    if exist install.bat (
        echo   [PASS] Windows installation script found
    ) else (
        echo   [WARN] install.bat not found
    )
    
    cd ..\..
) else (
    echo   [FAIL] packages/fmtools not properly structured
)

echo.
echo [TEST 2/4] Testing media-catcher...
echo.
if exist packages\media-catcher\package.json (
    cd packages\media-catcher
    
    echo   Testing if Node.js is installed...
    where node >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [PASS] Node.js found
        echo   Checking package.json...
        node -e "const p=require('./package.json'); console.log('  [INFO] Package:', p.name, 'v'+p.version);"
    ) else (
        echo   [WARN] Node.js not installed, skipping build test
    )
    
    if exist dist\media-catcher.user.js (
        echo   [PASS] Built UserScript exists
    ) else (
        echo   [WARN] UserScript not built yet (run: npm run build)
    )
    
    cd ..\..
) else if exist media-catcher\package.json (
    echo   [INFO] media-catcher in root directory
    echo   [TODO] Move to packages/media-catcher/
) else (
    echo   [FAIL] media-catcher not found
)

echo.
echo [TEST 3/4] Testing linux-automation...
echo.
if exist packages\linux-automation\scripts (
    cd packages\linux-automation
    
    if exist scripts\setup.sh (
        echo   [PASS] Main setup script found
    ) else (
        echo   [WARN] setup.sh not found
    )
    
    if exist nginx\nginx.conf (
        echo   [PASS] Nginx configuration found
    ) else (
        echo   [WARN] Nginx config not found
    )
    
    if exist README.md (
        echo   [PASS] Package README found
    ) else (
        echo   [WARN] README.md not found
    )
    
    cd ..\..
) else (
    echo   [FAIL] packages/linux-automation not properly structured
)

echo.
echo [TEST 4/4] Testing scripts collection...
echo.
if exist packages\scripts\python (
    cd packages\scripts
    
    echo   Counting Python scripts...
    for /f %%i in ('dir /b python\*.py 2^>nul ^| find /c /v ""') do set count=%%i
    echo   [INFO] Found %count% Python scripts
    
    if %count% GTR 0 (
        echo   [PASS] Python scripts found
    ) else (
        echo   [WARN] No Python scripts found
    )
    
    cd ..\..
) else (
    echo   [FAIL] packages/scripts not properly structured
)

echo.
echo ================================================
echo Testing Complete
echo ================================================
echo.
echo Summary:
echo   - Check all [FAIL] and [WARN] messages above
echo   - Fix any structural issues
echo   - Proceed to import path updates
echo.
pause

