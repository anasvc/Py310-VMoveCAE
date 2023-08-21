@echo off

SETLOCAL
set BASE_DIR=%~dp0
set INPUT_FILE_PATH=
set OUTPUT_FILE_PATH=

REM set APP_SCRIPT=%1
REM echo %APP_SCRIPT%

:processArgs
if "%~1"=="" (goto usage) else (set INPUT_FILE_PATH=%INPUT_FILE_PATH% "%~1")
if "%~2"=="" (goto usage) else (set OUTPUT_FILE_PATH=%OUTPUT_FILE_PATH% "%~2")
goto execute

:usage
echo:
echo Error in script usage. The correct usage is:
echo:
echo     %0 [input-file-path] [cax-file-path]
echo:
goto :eof

:execute

REM Set Python Virtual Environment Path
set PYDIR=%BASE_DIR%\py310env\Scripts

:runApp
"%PYDIR%\python.exe" "%BASE_DIR%\src\VMoveCAEBatch.py" %INPUT_FILE_PATH% %OUTPUT_FILE_PATH%
