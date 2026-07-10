@echo off
title WhatsApp Username Checker
cd /d "%~dp0"

echo ============================================
echo   WhatsApp Username Checker
echo ============================================
echo.

:: Configurar Android SDK automaticamente
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set ANDROID_SDK_ROOT=%LOCALAPPDATA%\Android\Sdk

:: Iniciar Appium em segundo plano
echo [1/2] Iniciando servidor Appium...
start "Servidor Appium" cmd /k "set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk && set ANDROID_SDK_ROOT=%LOCALAPPDATA%\Android\Sdk && appium"

:: Aguardar Appium iniciar
timeout /t 5 /nobreak > nul

:: Rodar o verificador
echo [2/2] Iniciando verificador de usernames...
echo.
python main.py

echo.
echo Programa finalizado. Verifique o arquivo results.csv para os resultados.
pause
