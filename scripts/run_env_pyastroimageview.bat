@echo off

call C:\Users\msf\Anaconda3\Scripts\activate.bat C:\Users\msf\Anaconda3

echo Running DEBUG mode from git checkout

REM MUST SET THE PROPER ENV HERE
REM AND UNCOMMENT WARNING!

start "" /wait cmd /c "echo SET ENV VAR FIRST!&echo(&pause"

call activate

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

set PATH=../../pystarutils/scripts/;%PATH%
set PYTHONPATH=../../pystarutils;..;%PYTHONPATH%

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

python.exe -u pyastroimageview_main.py

call deactivate

pause
