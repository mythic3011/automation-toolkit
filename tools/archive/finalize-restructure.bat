@echo off
REM Final steps to complete the restructure
REM Replaces README and prepares for git commit

echo ================================================
echo Finalize Restructure
echo ================================================
echo.

echo [1/4] Replacing README.md with README_NEW.md...
if exist README_NEW.md (
    if exist README.md (
        echo   Backing up old README...
        copy README.md README_OLD.md >nul
        echo   [OK] Backup created: README_OLD.md
    )
    
    echo   Replacing README...
    copy /y README_NEW.md README.md >nul
    echo   [OK] README.md updated with new monorepo version
    
    del README_NEW.md
    echo   [OK] Removed README_NEW.md
) else (
    echo   [ERROR] README_NEW.md not found!
    pause
    exit /b 1
)

echo.
echo [2/4] Moving media-catcher to packages/ (if needed)...
if exist media-catcher (
    if not exist packages\media-catcher (
        echo   Moving media-catcher to packages/...
        move media-catcher packages\ >nul
        echo   [OK] media-catcher moved to packages/
    ) else (
        echo   [INFO] media-catcher already in packages/
    )
) else (
    echo   [INFO] media-catcher not in root (probably already moved)
)

echo.
echo [3/4] Creating .gitignore backup...
if exist .gitignore (
    copy .gitignore .gitignore.bak >nul
    echo   [OK] Backup created: .gitignore.bak
)

echo.
echo [4/4] Checking git status...
git status --short
echo.

echo ================================================
echo Finalization Complete!
echo ================================================
echo.
echo Project is now ready for commit!
echo.
echo Recommended commit commands:
echo   git add -A
echo   git commit -m "feat: restructure entire project into monorepo v3.0"
echo   git tag v3.0.0
echo.
echo Or review changes first:
echo   git status
echo   git diff --stat
echo.
pause

