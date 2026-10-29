@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"

rem ---- Cau hinh PATH cho Python tren Windows ----
if exist "%LOCALAPPDATA%\Python\bin" set "PATH=%LOCALAPPDATA%\Python\bin;!PATH!"
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64" set "PATH=%LOCALAPPDATA%\Python\pythoncore-3.14-64;%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts;!PATH!"
if exist "%LOCALAPPDATA%\Programs\Python\Python314" set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;!PATH!"
if exist "%LOCALAPPDATA%\Programs\Python\Python313" set "PATH=%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts;!PATH!"
if exist "%LOCALAPPDATA%\Programs\Python\Python312" set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;!PATH!"
if exist "%LOCALAPPDATA%\Programs\Python\Python311" set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;!PATH!"

set "PYTHONUTF8=1"

echo ========================================================
echo   NUT BAM: TU DONG BUILD GAME (APK + TAR.GZ + INDEX)
echo   VA DAY LEN GIT
echo ========================================================
echo.

rem ---- Tim lenh Python hop le ----
set "PY_CMD="
python -c "import sys; sys.exit(0)" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_CMD=python"
) else (
    py -c "import sys; sys.exit(0)" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_CMD=py"
    ) else if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Python\bin\python.exe"
    ) else if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    )
)

if "!PY_CMD!"=="" (
    echo [LOI] Khong tim thay Python! Vui long cai dat Python hoac tat App execution aliases.
    pause
    exit /b 1
)

rem ---- Tim thu muc goc Git ----
set "GIT_ROOT="
for /f "delims=" %%g in ('git rev-parse --show-toplevel 2^>nul') do set "GIT_ROOT=%%g"
if defined GIT_ROOT (
    set "GIT_ROOT=!GIT_ROOT:/=\!"
) else (
    set "GIT_ROOT=%~dp0"
    if "!GIT_ROOT:~-1!"=="\" set "GIT_ROOT=!GIT_ROOT:~0,-1!"
)

rem ---- Tim thu muc game ----
if exist "%~dp0main.py" (
    for %%I in ("%~dp0.") do set "GAME=%%~nxI"
    set "GAME_DIR=%~dp0"
    if "!GAME_DIR:~-1!"=="\" set "GAME_DIR=!GAME_DIR:~0,-1!"
    echo   [+] Phat hien game tai thu muc hien tai: !GAME!
) else (
    cd /d "!GIT_ROOT!"
    set COUNT=0
    for /d %%D in (*) do (
        if exist "%%D\main.py" (
            set /a COUNT+=1
            set "GAME!COUNT!=%%D"
            echo   [!COUNT!] %%D
        )
    )

    if !COUNT! EQU 0 (
        echo [LOI] Khong tim thay thu muc game nao co file main.py!
        pause
        exit /b 1
    )

    if !COUNT! EQU 1 (
        echo   [+] Phat hien 1 game: !GAME1!
        set "GAME=!GAME1!"
    ) else (
        echo.
        set /p CHOICE=Chon so thu tu game cua ban roi bam Enter: 
        set "GAME=!GAME%CHOICE%!"
        if "!GAME!"=="" (
            echo [LOI] So ban chon khong hop le!
            pause
            exit /b 1
        )
    )
    set "GAME_DIR=!GIT_ROOT!\!GAME!"
)

echo.
set /p MAKEHOME=Dat game nay lam trang chu web (index.html o thu muc goc)? (y/n): 

echo.
echo [1/5] Kiem tra pygbag...
!PY_CMD! -m pip show pygbag >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Chua co pygbag, dang cai dat...
    !PY_CMD! -m pip install pygbag
)

echo [2/5] Dang build game "!GAME!" bang pygbag (cho 1 chut nhe)...
!PY_CMD! -X utf8 -m pygbag --build --disable-sound-format-error "!GAME_DIR!\main.py"
if !ERRORLEVEL! NEQ 0 (
    echo [LOI] Build that bai! Xem loi o phia tren.
    pause
    exit /b 1
)

echo [3/5] Sao chep file apk, tar.gz, index.html ra thu muc game...
copy /Y "!GAME_DIR!\build\web\*" "!GAME_DIR!\" >nul
if /i "!MAKEHOME!"=="y" (
    echo       Sao chep ra thu muc goc lam trang chu...
    copy /Y "!GAME_DIR!\build\web\*" "!GIT_ROOT!\" >nul
)
dir /b "!GAME_DIR!\build\web"

echo [4/5] Commit vao Git...
cd /d "!GIT_ROOT!"
git add .
git commit -m "Build web moi cho !GAME!: %date% %time%" 2>nul || (
    echo       Khong co thay doi moi de commit.
)

echo [5/5] Lay code moi nhat cua cac ban khac roi day len GitHub...
git pull --rebase origin main
if !ERRORLEVEL! NEQ 0 (
    echo [LOI] Bi xung dot khi lay code moi. Nho thay/co giup nhe!
    pause
    exit /b 1
)
git push origin main

if !ERRORLEVEL! EQU 0 (
    echo ========================================================
    echo   DA DAY LEN GIT THANH CONG! Vercel se tu dong cap nhat.
    echo   Game cua ban: /!GAME!/index.html
    echo ========================================================
) else (
    echo [LOI] Khong the push len Git. Kiem tra mang hoac dang nhap Git.
)

pause
