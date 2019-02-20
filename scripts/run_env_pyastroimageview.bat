@echo off

call C:\Users\msf\Anaconda3\Scripts\activate.bat C:\Users\msf\Anaconda3

echo Running DEBUG mode from git checkout

REM Expects env on command line

if ["%~1"]==[""] (
  start "" /wait cmd /c "echo Pass ENV name in shortcu!&echo(&pause"
  exit
)
echo Activating %1
call activate %1

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

set PATH=../../pystarutils/scripts/;%PATH%
set PYTHONPATH=../../pystarutils;..;%PYTHONPATH%

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

python.exe -u pyastroimageview_main.py

call deactivate

pause
