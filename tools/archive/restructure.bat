@echo off
REM myCustomScript Complete Project Restructure Script (Windows)
REM This script reorganizes the entire project into a monorepo structure

setlocal enabledelayedexpansion

echo ================================================
echo myCustomScript Project Restructure
echo ================================================
echo.

REM Auto-navigate to project root if we're in tools/
if exist ..\README.md (
    echo [INFO] Detected running from tools directory, navigating to project root...
    cd ..
)

REM Check if we're in the right directory
if not exist README.md (
    echo [ERROR] Cannot find project root. Please ensure you're in the project directory.
    echo [ERROR] Expected to find README.md in current directory.
    echo.
    echo [INFO] Current directory: %CD%
    echo [INFO] Try: cd path\to\myCustomScript
    pause
    exit /b 1
)

echo [INFO] Starting restructure process...
echo.

REM ===================================================================
REM PHASE 1: media-catcher (already completed)
REM ===================================================================
echo [INFO] Phase 1: media-catcher already restructured
echo.

REM ===================================================================
REM PHASE 2: Restructure fmtools
REM ===================================================================
echo [INFO] Phase 2: Restructuring fmtools...

REM Create fmtools subdirectories
if not exist packages\fmtools\src mkdir packages\fmtools\src
if not exist packages\fmtools\rust mkdir packages\fmtools\rust
if not exist packages\fmtools\docs mkdir packages\fmtools\docs
if not exist packages\fmtools\tests mkdir packages\fmtools\tests
if not exist packages\fmtools\examples mkdir packages\fmtools\examples
if not exist packages\fmtools\scripts mkdir packages\fmtools\scripts
if not exist packages\fmtools\dist mkdir packages\fmtools\dist

REM Move Python source
if exist fmtools (
    if not exist packages\fmtools\src\fmtools (
        echo [INFO] Copying Python source code...
        xcopy fmtools packages\fmtools\src\fmtools\ /E /I /Y >nul 2>&1
    )
)

REM Move Rust source
if exist rust_tools (
    echo [INFO] Copying Rust implementations...
    xcopy rust_tools\* packages\fmtools\rust\ /E /I /Y >nul 2>&1
)

REM Move Python scripts
if exist scripts (
    echo [INFO] Copying standalone scripts...
    xcopy scripts\*.py packages\fmtools\scripts\ /Y >nul 2>&1
)

REM Move configuration files
for %%f in (pyproject.toml requirements.txt setup.py MANIFEST.in) do (
    if exist %%f (
        echo [INFO] Copying %%f...
        copy %%f packages\fmtools\ >nul 2>&1
    )
)

REM Move installation scripts
for %%f in (install.sh install.bat build_all.sh) do (
    if exist %%f (
        echo [INFO] Copying %%f...
        copy %%f packages\fmtools\ >nul 2>&1
    )
)

REM Move examples
if exist examples (
    echo [INFO] Copying examples...
    xcopy examples\* packages\fmtools\examples\ /E /I /Y >nul 2>&1
)

REM Move build configs
if exist build-config (
    echo [INFO] Copying build configs...
    if not exist packages\fmtools\build-config mkdir packages\fmtools\build-config
    xcopy build-config\* packages\fmtools\build-config\ /E /I /Y >nul 2>&1
)

REM Move exe files
if exist exe (
    echo [INFO] Copying executables to dist...
    xcopy exe\* packages\fmtools\dist\ /E /I /Y >nul 2>&1
)

echo [INFO] Phase 2 complete
echo.

REM ===================================================================
REM PHASE 3: Restructure linux-automation
REM ===================================================================
echo [INFO] Phase 3: Restructuring linux-automation...

if exist linux (
    echo [INFO] Copying linux configuration...
    xcopy linux\* packages\linux-automation\ /E /I /Y >nul 2>&1
)

echo [INFO] Phase 3 complete
echo.

REM ===================================================================
REM PHASE 4: Restructure scripts
REM ===================================================================
echo [INFO] Phase 4: Organizing standalone scripts...

if exist scripts (
    if not exist packages\scripts\python mkdir packages\scripts\python
    xcopy scripts\*.py packages\scripts\python\ /Y >nul 2>&1
)

echo [INFO] Phase 4 complete
echo.

REM ===================================================================
REM PHASE 5: Organize Documentation
REM ===================================================================
echo [INFO] Phase 5: Organizing documentation...

REM Move fmtools docs
for %%d in (INSTALL.md QUICK_START.md USAGE_EXAMPLES.md COMMAND_REFERENCE.md USE_RUST_GUIDE.md) do (
    if exist docs\%%d (
        copy docs\%%d packages\fmtools\docs\ >nul 2>&1
    )
)

REM Move project-wide docs
for %%d in (INDEX.md GETTING_STARTED.md PROJECT_COMPLETE.md WHATS_NEW.md CHANGELOG.md) do (
    if exist docs\%%d (
        copy docs\%%d docs\master\ >nul 2>&1
    )
)

REM Move scattered documentation
for %%d in (TROUBLESHOOTING.md ZOOM_VTT_SUPPORT.md PERFORMANCE_IMPROVEMENTS.md MODERN_UI_IMPROVEMENTS.md panopto-xhr-catcher-README.md) do (
    if exist %%d (
        copy %%d media-catcher\docs\ >nul 2>&1
    )
)

echo [INFO] Phase 5 complete
echo.

REM ===================================================================
REM PHASE 6: Create Package READMEs
REM ===================================================================
echo [INFO] Phase 6: Creating package READMEs...

REM Create README files (content created in separate step)
echo # fmtools - File Management Tools > packages\fmtools\README.md
echo # Linux Automation Toolkit > packages\linux-automation\README.md
echo # Utility Scripts Collection > packages\scripts\README.md

echo [INFO] Phase 6 complete
echo.

REM ===================================================================
REM SUMMARY
REM ===================================================================
echo.
echo ================================================
echo Restructure Complete!
echo ================================================
echo.
echo [INFO] New structure created in packages/:
echo   - packages\fmtools\          (File management tools)
echo   - packages\media-catcher\    (UserScript for media capture)
echo   - packages\linux-automation\ (Linux server tools)
echo   - packages\scripts\          (Standalone utilities)
echo.
echo [WARN] IMPORTANT: Old files are still in place!
echo [WARN] Review the new structure, then manually remove old files.
echo.
echo [INFO] Next steps:
echo   1. Review packages\ directory
echo   2. Test each package
echo   3. Update import paths if needed
echo   4. Remove old files when confident
echo   5. Commit changes
echo.
echo ================================================

pause

