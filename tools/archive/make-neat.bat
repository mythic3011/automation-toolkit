@echo off
REM Make Project Neat - Comprehensive cleanup and organization
REM This script organizes the project for a clean, professional structure

echo ================================================
echo Making Project Neat and Clean
echo ================================================
echo.

REM Navigate to project root if in tools/
if exist ..\README.md (
    cd ..
)

echo [STEP 1] Cleaning up temporary files...
echo.

REM Remove temporary/backup files
if exist README_OLD.md (
    del /q README_OLD.md
    echo   [OK] Removed README_OLD.md
)

if exist .gitignore.bak (
    del /q .gitignore.bak
    echo   [OK] Removed .gitignore.bak
)

REM Clean up Python cache
echo   Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d" 2>nul
    echo   [OK] Removed %%d
)

REM Clean up .pyc files
for /r . %%f in (*.pyc) do @if exist "%%f" (
    del /q "%%f" 2>nul
    echo   [OK] Removed %%f
)

REM Clean up .pyo files
for /r . %%f in (*.pyo) do @if exist "%%f" (
    del /q "%%f" 2>nul
)

echo.
echo [STEP 2] Organizing documentation...
echo.

REM Ensure docs/master exists
if not exist docs\master (
    mkdir docs\master
    echo   [OK] Created docs/master/
)

REM Move restructure docs to docs/master if they exist in root
if exist PROJECT_RESTRUCTURE_PLAN.md (
    move PROJECT_RESTRUCTURE_PLAN.md docs\master\ >nul 2>&1
    echo   [OK] Moved PROJECT_RESTRUCTURE_PLAN.md to docs/master/
)

if exist RESTRUCTURE_README.md (
    move RESTRUCTURE_README.md docs\master\ >nul 2>&1
    echo   [OK] Moved RESTRUCTURE_README.md to docs/master/
)

if exist RESTRUCTURE_COMPLETE_SUMMARY.md (
    move RESTRUCTURE_COMPLETE_SUMMARY.md docs\master\ >nul 2>&1
    echo   [OK] Moved RESTRUCTURE_COMPLETE_SUMMARY.md to docs/master/
)

echo.
echo [STEP 3] Organizing packages...
echo.

REM Ensure all package directories exist
if not exist packages (
    mkdir packages
    echo   [OK] Created packages/
)

REM Move media-catcher to packages if it's in root
if exist media-catcher (
    if not exist packages\media-catcher (
        echo   Moving media-catcher to packages/...
        move media-catcher packages\ >nul 2>&1
        echo   [OK] Moved media-catcher to packages/
    )
) else (
    if not exist packages\media-catcher (
        echo   [INFO] media-catcher directory not found anywhere
    )
)

REM Ensure package subdirectories exist
if not exist packages\fmtools (
    mkdir packages\fmtools
    echo   [OK] Created packages/fmtools/
)

if not exist packages\linux-automation (
    mkdir packages\linux-automation
    echo   [OK] Created packages/linux-automation/
)

if not exist packages\scripts (
    mkdir packages\scripts
    echo   [OK] Created packages/scripts/
)

echo.
echo [STEP 4] Cleaning up empty directories...
echo.

REM This will be handled by git automatically for tracked directories

echo   [INFO] Empty directories will be cleaned by git

echo.
echo [STEP 5] Organizing tools...
echo.

REM Ensure all tools are in place
if exist tools (
    echo   [OK] Tools directory exists
    echo   [INFO] Tools available:
    dir /b tools\*.bat 2>nul | findstr /v /i ".bat" >nul || (
        for /f %%f in ('dir /b tools\*.bat 2^>nul') do echo     - %%f
    )
) else (
    echo   [WARN] Tools directory not found
)

echo.
echo [STEP 6] Verifying .gitignore...
echo.

if exist .gitignore (
    echo   [OK] .gitignore exists
    
    REM Check if it has comprehensive rules
    findstr /i "__pycache__" .gitignore >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Python rules present
    ) else (
        echo   [WARN] Consider updating .gitignore with Python rules
    )
    
    findstr /i "node_modules" .gitignore >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Node rules present
    ) else (
        echo   [WARN] Consider updating .gitignore with Node rules
    )
    
    findstr /i "target/" .gitignore >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Rust rules present
    ) else (
        echo   [WARN] Consider updating .gitignore with Rust rules
    )
) else (
    echo   [ERROR] .gitignore missing!
)

echo.
echo [STEP 7] Creating README index if needed...
echo.

if not exist docs\master\INDEX.md (
    echo Creating documentation index...
    (
        echo # 📚 Documentation Index
        echo.
        echo ## Master Documentation
        echo.
        echo - [Getting Started](GETTING_STARTED.md^)
        echo - [Project Structure](PROJECT_RESTRUCTURE_PLAN.md^)
        echo - [Restructure Guide](RESTRUCTURE_README.md^)
        echo - [Complete Summary](RESTRUCTURE_COMPLETE_SUMMARY.md^)
        echo.
        echo ## Package Documentation
        echo.
        echo - [fmtools](../../packages/fmtools/README.md^)
        echo - [media-catcher](../../packages/media-catcher/README.md^)
        echo - [linux-automation](../../packages/linux-automation/README.md^)
        echo - [scripts](../../packages/scripts/README.md^)
        echo.
        echo ## Quick Links
        echo.
        echo - [Contributing](CONTRIBUTING.md^)
        echo - [Troubleshooting](TROUBLESHOOTING.md^)
        echo - [Changelog](CHANGELOG.md^)
    ) > docs\master\INDEX.md
    echo   [OK] Created docs/master/INDEX.md
) else (
    echo   [OK] INDEX.md already exists
)

echo.
echo [STEP 8] Final verification...
echo.

echo   Checking project structure...
if exist README.md (
    echo   [OK] Root README.md exists
) else (
    echo   [WARN] Root README.md missing
)

if exist LICENSE (
    echo   [OK] LICENSE file exists
) else (
    echo   [WARN] LICENSE file missing
)

if exist packages (
    echo   [OK] packages/ directory exists
) else (
    echo   [ERROR] packages/ directory missing!
)

if exist docs\master (
    echo   [OK] docs/master/ directory exists
) else (
    echo   [WARN] docs/master/ directory missing
)

if exist tools (
    echo   [OK] tools/ directory exists
) else (
    echo   [WARN] tools/ directory missing
)

echo.
echo ================================================
echo Project Cleanup Complete!
echo ================================================
echo.
echo Current structure:
echo   myCustomScript/
echo   ├── packages/          [Organized sub-projects]
echo   ├── docs/master/       [Master documentation]
echo   ├── tools/             [Development tools]
echo   ├── README.md          [Project overview]
echo   ├── LICENSE            [MIT License]
echo   └── .gitignore         [Git rules]
echo.
echo The project is now neat and organized!
echo.
echo Next steps:
echo   1. Review: git status
echo   2. Test packages: .\tools\test-packages.bat
echo   3. Commit changes: git add -A ^&^& git commit
echo.
pause

