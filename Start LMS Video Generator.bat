@echo off
rem Starts the LMS Video Generator (API + web page) and opens it in the browser.
rem Keep this window open while you use the app; closing it stops the app.
title LMS Video Generator (npm run dev)
cd /d "%~dp0"

rem Already running? Then just open the page.
netstat -ano | findstr /R /C:":3000 .*LISTENING" >nul
if not errorlevel 1 (
    netstat -ano | findstr /R /C:":8765 .*LISTENING" >nul
    if not errorlevel 1 (
        start "" http://127.0.0.1:3000
        exit /b
    )
)

rem Open the page once the app has had time to start (about 15 seconds).
start "" /min cmd /c "timeout /t 15 /nobreak >nul & start http://127.0.0.1:3000"
npm run dev
echo.
echo The app has stopped. Press any key to close this window.
pause >nul
