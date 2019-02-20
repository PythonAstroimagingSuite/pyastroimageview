@echo off

REM Find Anaconda3

REM First as user then global
if exist %HOMEDRIVER%%HOMEPATH%\Anaconda3 (
  echo Found in user path
  set ANACONDA_LOC=%HOMEDRIVE%%HOMEPATH%\Anaconda3
) else (
    if exist %HOMEDRIVE%Anaconda3 (
       echo Found in root path
       set ANACONDA_LOC=%HOMEDRIVE%Anaconda3
    ) else (
       start "" /wait cmd /c "echo Cannot find Anaconda3!&echo(&pause"
       exit
    )
)

echo Anaconda location is %ANACONDA_LOC%
call %ANACONDA_LOC%\Scripts\activate.bat %ANACONDA_LOC%

echo Running DEBUG mode from git checkout

REM Expects env on command line

if ["%~1"]==[""] (
  start "" /wait cmd /c "echo Pass ENV name in shortcut!&echo(&pause"
  exit
)
echo Activating %1
call activate %1

set PATH=../../pystarutils/scripts/;%PATH%
set PYTHONPATH=../../pystarutils;..;%PYTHONPATH%

python.exe -u pyastroimageview_main.py

call deactivate

pause
