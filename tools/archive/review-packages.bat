@echo off
REM Review packages directory structure
REM Run this after restructure.bat to verify everything is in place

echo ================================================
echo Package Structure Review
echo ================================================
echo.

echo [1/4] Checking packages/fmtools...
if exist packages\fmtools\src\fmtools (
    echo   [OK] Python source found
) else (
    echo   [MISSING] Python source not found
)

if exist packages\fmtools\rust (
    echo   [OK] Rust source found
) else (
    echo   [MISSING] Rust source not found
)

if exist packages\fmtools\docs (
    echo   [OK] Documentation found
) else (
    echo   [MISSING] Documentation not found
)

if exist packages\fmtools\pyproject.toml (
    echo   [OK] pyproject.toml found
) else (
    echo   [MISSING] pyproject.toml not found
)

echo.
echo [2/4] Checking packages/media-catcher...
if exist packages\media-catcher\src (
    echo   [OK] Source code found
) else (
    if exist media-catcher\src (
        echo   [INFO] media-catcher in root, needs to be moved to packages/
    ) else (
        echo   [MISSING] Source code not found
    )
)

if exist packages\media-catcher\dist\media-catcher.user.js (
    echo   [OK] Built UserScript found
) else (
    if exist media-catcher\dist\media-catcher.user.js (
        echo   [INFO] Built file in root media-catcher/
    ) else (
        echo   [MISSING] Built UserScript not found
    )
)

echo.
echo [3/4] Checking packages/linux-automation...
if exist packages\linux-automation\scripts (
    echo   [OK] Scripts found
) else (
    echo   [MISSING] Scripts not found
)

if exist packages\linux-automation\nginx (
    echo   [OK] Nginx configs found
) else (
    echo   [MISSING] Nginx configs not found
)

echo.
echo [4/4] Checking packages/scripts...
if exist packages\scripts\python (
    echo   [OK] Python scripts found
) else (
    echo   [MISSING] Python scripts not found
)

echo.
echo ================================================
echo Review Complete
echo ================================================
echo.
echo Next steps:
echo   1. Fix any [MISSING] items above
echo   2. Run: .\tools\test-packages.bat
echo   3. Update import paths if needed
echo.
pause

