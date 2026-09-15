@echo off
setlocal
if "%~1"=="" goto help
if "%~1"=="model" python -m src.model
if "%~1"=="server" python -m src.server
if "%~1"=="demo" python -m src.demo_rpc
if "%~1"=="test" coverage run --branch -m pytest && coverage report -m
goto end
:help
echo Usage: run.bat model^|server^|demo^|test
:end
endlocal
