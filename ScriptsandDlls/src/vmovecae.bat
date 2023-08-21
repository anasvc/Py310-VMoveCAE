@echo off
setlocal

if "%2" == "" goto usage

set VC_MACH=%2
if /i %2 == x86 goto x86
if /i %2 == amd64 goto amd64
goto usage

:usage
echo Error in script usage. The correct usage is:
echo     %0 [run/build] [x86/amd64]
echo:
echo For example:
echo     %0 run x86
echo     %0 build amd64
goto :eof

:x86
set VC_PLAT=win32
goto runpython

:amd64
set VC_PLAT=x64
goto runpython

:runpython
if /i %1 == run goto run
if /i %1 == build goto build
goto usage

:run
set PATH=%VMDEP%\dlls;%VCDEP%\RuntimeDlls;%ABADIR12%\%VC_PLAT%;%PATH%
if "%3" == "" goto run_gui
goto run_batch
goto :eof

:run_gui
%PYTHONDIR%\%VC_PLAT%\python.exe VMoveCAE.py
goto :eof

:run_batch
shift
shift
set "args="
:parse_args
if "%~1" neq "" (
    set args=%args% %1
    shift
    goto :parse_args
)
if defined args set args=%args:~1%
%PYTHONDIR%\%VC_PLAT%\python.exe VMoveCAEBatch.py %args%
echo %ERRORLEVEL%
goto :eof

:build
set VC80REDIST=C:\Program Files (x86)\Microsoft Visual Studio 8\VC\redist
set PATH=%VMDEP%\dlls;%VCDEP%\RuntimeDlls;%ABADIR12%\%VC_PLAT%;%PATH%
copy lib-extra\%VC_PLAT%\*.dll .
%PYTHONDIR%\%VC_PLAT%\python.exe setup.py py2exe
del *.dll
REM move /y dist\VcApp.exe dist\VMoveCAE.exe
copy "%ABADIR12%\%VC_PLAT%\*.dll" dist
if /i %2 == amd64 copy /y lib64-compat\psapi.dll dist
del *.pyc
goto :eof

