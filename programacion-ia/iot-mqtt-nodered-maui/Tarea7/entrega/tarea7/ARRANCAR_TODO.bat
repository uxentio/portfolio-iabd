@echo off
REM ---------------------------------------------------------
REM  Esto me arranca todo lo que necesito para la demo:
REM  LM Studio con el modelo cargado, Node-RED y la app MAUI.
REM  Asi no tengo que ir abriendo 3 programas a mano cada vez.
REM  Doble clic y listo.
REM ---------------------------------------------------------
setlocal EnableDelayedExpansion
title Tarea 7 - arrancador

echo.
echo  Arrancando el entorno de la Tarea 7...
echo.

set "RAIZ=%~dp0"
set "MODELO=qwen3.5-0.8b"

REM ---- LM Studio ----
REM Si tengo el CLI "lms" instalado, arranco el server y cargo el modelo
REM con la GPU a tope. Si no lo tengo, aviso y que lo abra a mano.
echo (1) LM Studio con %MODELO%...
where lms >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "LM Studio Server" cmd /k "lms server start && lms load %MODELO% --gpu max"
    echo     ok, server en el 1234
) else (
    echo     no encuentro el CLI de LM Studio.
    echo     abre LM Studio a mano, carga %MODELO% y dale a Start Server.
    pause
)
echo.

REM ---- Node-RED ----
REM Primero intento el ejecutable global, y si no lo pillo tiro de npx.
REM Si tampoco esta npx, aviso de que instale node-red con npm -g.
echo (2) Node-RED...
where node-red >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "Node-RED" cmd /k "node-red"
    echo     ok, en el 1880 (si es la primera vez importa NodeRED\flows.json)
) else (
    where npx >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        start "Node-RED" cmd /k "npx node-red"
        echo     arrancado con npx, en el 1880
    ) else (
        echo     no hay node-red ni npx en el PATH.
        echo     instalalo con:  npm install -g node-red
        pause
    )
)
echo.

REM ---- la app MAUI ----
REM Espero un poco a que LM Studio y Node-RED acaben de arrancar
REM (si la app sale antes, puede dar error al intentar conectar).
echo (3) abriendo la app... (espero 8s a los otros)
timeout /t 8 /nobreak >nul

set "APP=%RAIZ%LucesIoT.MAUI\bin\Debug\net9.0-windows10.0.19041.0\win10-x64\LucesIoT.MAUI.exe"
if exist "%APP%" (
    start "" "%APP%"
    echo     app lanzada
) else (
    echo     la app no esta compilada, la compilo ahora y la abro.
    pushd "%RAIZ%LucesIoT.MAUI"
    dotnet build -c Debug -f net9.0-windows10.0.19041.0 --nologo
    popd
    if exist "%APP%" (
        start "" "%APP%"
        echo     compilada y abierta
    ) else (
        echo     no ha compilado, mira los errores de arriba.
        pause
        exit /b 1
    )
)

echo.
echo  Listo. Las tres ventanas estan abiertas:
echo    LM Studio  - http://127.0.0.1:1234
echo    Node-RED   - http://127.0.0.1:1880
echo    App MAUI   - ventana de MAUI
echo.
echo  No te olvides del ESP32: enchufalo y conectalo al WiFi.
echo  Para cerrar, cierra las 3 ventanas y ya.
echo.
pause
