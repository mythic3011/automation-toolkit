@echo off
REM Safely remove old files after successful restructure
REM ONLY run this after verifying packages/ works correctly!

echo ================================================
echo Old Files Cleanup
echo ================================================
echo.
echo [WARNING] This will DELETE old files from the root!
echo [WARNING] Only run this after verifying packages/ works!
echo.
echo Files/folders to be removed:
echo   - fmtools/           (moved to packages/fmtools/src/fmtools/)
echo   - rust_tools/        (moved to packages/fmtools/rust/)
echo   - scripts/           (moved to packages/scripts/python/)
echo   - linux/             (moved to packages/linux-automation/)
echo   - examples/          (moved to packages/fmtools/examples/)
echo   - exe/               (moved to packages/fmtools/dist/)
echo   - build-config/      (moved to packages/fmtools/build-config/)
echo   - Old config files   (pyproject.toml, requirements.txt, etc.)
echo.
set /p confirm="Are you ABSOLUTELY SURE you want to delete these? (type YES): "

if not "%confirm%"=="YES" (
    echo.
    echo [CANCELLED] Cleanup cancelled. No files were deleted.
    pause
    exit /b 0
)

echo.
echo [INFO] Starting cleanup...
echo.

REM Remove old directories
echo [1/8] Removing old fmtools/...
if exist fmtools (
    rmdir /s /q fmtools
    echo   [OK] Removed fmtools/
) else (
    echo   [SKIP] fmtools/ not found
)

echo [2/8] Removing old rust_tools/...
if exist rust_tools (
    rmdir /s /q rust_tools
    echo   [OK] Removed rust_tools/
) else (
    echo   [SKIP] rust_tools/ not found
)

echo [3/8] Removing old scripts/...
if exist scripts (
    rmdir /s /q scripts
    echo   [OK] Removed scripts/
) else (
    echo   [SKIP] scripts/ not found
)

echo [4/8] Removing old linux/...
if exist linux (
    rmdir /s /q linux
    echo   [OK] Removed linux/
) else (
    echo   [SKIP] linux/ not found
)

echo [5/8] Removing old examples/...
if exist examples (
    rmdir /s /q examples
    echo   [OK] Removed examples/
) else (
    echo   [SKIP] examples/ not found
)

echo [6/8] Removing old exe/...
if exist exe (
    rmdir /s /q exe
    echo   [OK] Removed exe/
) else (
    echo   [SKIP] exe/ not found
)

echo [7/8] Removing old build-config/...
if exist build-config (
    rmdir /s /q build-config
    echo   [OK] Removed build-config/
) else (
    echo   [SKIP] build-config/ not found
)

echo [8/8] Removing old config files...
if exist pyproject.toml (
    del /q pyproject.toml
    echo   [OK] Removed pyproject.toml
)
if exist requirements.txt (
    del /q requirements.txt
    echo   [OK] Removed requirements.txt
)
if exist setup.py (
    del /q setup.py
    echo   [OK] Removed setup.py
)
if exist MANIFEST.in (
    del /q MANIFEST.in
    echo   [OK] Removed MANIFEST.in
)
if exist install.sh (
    del /q install.sh
    echo   [OK] Removed install.sh
)
if exist install.bat (
    del /q install.bat
    echo   [OK] Removed install.bat
)
if exist build_all.sh (
    del /q build_all.sh
    echo   [OK] Removed build_all.sh
)

REM Remove old documentation (scattered files)
echo.
echo [INFO] Cleaning up old documentation...
if exist TROUBLESHOOTING.md (
    del /q TROUBLESHOOTING.md
    echo   [OK] Removed TROUBLESHOOTING.md (moved to media-catcher/docs/)
)
if exist ZOOM_VTT_SUPPORT.md (
    del /q ZOOM_VTT_SUPPORT.md
    echo   [OK] Removed ZOOM_VTT_SUPPORT.md
)
if exist PERFORMANCE_IMPROVEMENTS.md (
    del /q PERFORMANCE_IMPROVEMENTS.md
    echo   [OK] Removed PERFORMANCE_IMPROVEMENTS.md
)
if exist MODERN_UI_IMPROVEMENTS.md (
    del /q MODERN_UI_IMPROVEMENTS.md
    echo   [OK] Removed MODERN_UI_IMPROVEMENTS.md
)
if exist panopto-xhr-catcher-README.md (
    del /q panopto-xhr-catcher-README.md
    echo   [OK] Removed panopto-xhr-catcher-README.md
)
if exist panopto-xhr-catcher.user.js (
    del /q panopto-xhr-catcher.user.js
    echo   [OK] Removed old panopto-xhr-catcher.user.js
)

REM Remove logs
echo.
echo [INFO] Cleaning up logs...
if exist logs (
    rmdir /s /q logs
    echo   [OK] Removed logs/
)

REM Remove egg-info
if exist fmtools.egg-info (
    rmdir /s /q fmtools.egg-info
    echo   [OK] Removed fmtools.egg-info/
)

echo.
echo ================================================
echo Cleanup Complete!
echo ================================================
echo.
echo [SUCCESS] Old files have been removed
echo [INFO] Your project now has a clean monorepo structure
echo.
echo Next steps:
echo   1. Replace README.md with README_NEW.md
echo   2. Review the changes: git status
echo   3. Commit: git add -A && git commit -m "feat: restructure to monorepo"
echo.
pause

