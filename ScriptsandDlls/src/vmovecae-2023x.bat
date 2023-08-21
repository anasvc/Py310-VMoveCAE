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
set PY_PLAT=win32
goto runpython

:amd64
set VC_PLAT=x64
set PY_PLAT=x64
goto runpython

:runpython
if /i %1 == run goto run
if /i %1 == build goto build
goto usage

:run
set PATH=%PATH%;%VMDEPDIR%\license\bin;%VMDEPDIR%\odbapi\2023x\binvm;%VMDEPDIR%\zlib\bin;%VMDEPDIR%\hdf5\1.8.21\bin;%VMDEPDIR%\cgns\vc141\bin;%VMDEPDIR%\ccmio\bin;%VMDEPDIR%\version\bin
if "%3" == "" goto run_gui
goto run_batch
goto :eof

:run_gui
%PYTHON_DIR%\%PY_PLAT%\python.exe VMoveCAE.py --debug
echo "%PYTHON_DIR%\%PY_PLAT%\python.exe VMoveCAE.py --debug"
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
%PYTHON_DIR%\%PY_PLAT%\python.exe VMoveCAEBatch.py %args%
echo %ERRORLEVEL%
goto :eof

:build
set PATH=%PATH%;%VMDEPDIR%\license\bin;%VMDEPDIR%\odbapi\2023x\binvm;%VMDEPDIR%\zlib\bin;%VMDEPDIR%\hdf5\1.8.21\bin;%VMDEPDIR%\cgns\vc141\bin;%VMDEPDIR%\ccmio\bin;%VMDEPDIR%\version\bin
echo "Building setup ..."
%PYTHON_DIR%\%PY_PLAT%\python.exe setup.py py2exe
echo "Building setup ... done"
REM move /y dist\VcApp.exe dist\VMoveCAE.exe
echo "Copying required files ... "
copy "CaxInfo.exe" dist
copy "CaxMerge.exe" dist
REM copy "VMoveCAE.ico" dist
REM copy "VMoveCAE User Guide.chm" dist
xcopy /E /I /Y addtl\ dist\
copy "%VMDEPDIR%\odbapi\2023x\binvm\*.dll" dist
REM if /i %2 == amd64 copy /y lib64-compat\psapi.dll dist
echo "Copying required files ... done"
echo "Deleting unneeded files ... "
del dist\api-ms-win*.*
REM del dist\MSVCP90.dll
REM del dist\MSVCR80.dll
del dist\UxTheme.dll
del dist\dhcpcsvc.DLL
REM del *.pyc
echo "Deleting unneeded files ... done"
echo "Invoking Visual Studio command prompt ... "
set VC141_SCRIPT="C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"
call %VC141_SCRIPT%
echo "Invoking Visual Studio command prompt ... done"
echo "Editing binaries to make them large address aware ..."
editbin /LARGEADDRESSAWARE /STACK:20000000 dist/VMoveCAE.exe dist/VMoveCAEBatch.exe dist/CaeInfo.exe dist/VMoveCAEValidate.exe dist/VMoveCAESubmit.exe
echo "Editing binaries to make them large address aware ...done"
goto :eof

