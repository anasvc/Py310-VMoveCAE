@echo on

SETLOCAL
set BASE_DIR=%~dp0
set APP_ARGS=
echo %BASE_DIR%


REM Set Python Virtual Environment Path
set PYDIR=%BASE_DIR%\py310env\Scripts

:runApp
"%PYDIR%\python.exe" "%BASE_DIR%\src\VMoveCAE.py" 
