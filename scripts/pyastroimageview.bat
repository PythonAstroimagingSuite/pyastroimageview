@echo off
echo Running DEBUG mode from git checkout

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

set PATH=../../pystarutils/scripts/;%PATH%
set PYTHONPATH=../../pystarutils;..;%PYTHONPATH%

echo PATH=%PATH%
echo PYTHONPATH=%PYTHONPATH%

python.exe -u pyastroimageview_main.py %*
