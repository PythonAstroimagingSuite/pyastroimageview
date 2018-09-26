echo "BUILD SCRIPT RUNNING"

:: add to path to find whatever bash we're going to use!
:: SET PATH=%PATH%;C:\Users\msf\AppData\Local\Programs\Git\bin
:: bash -c "echo 'BASH RUN TEST'"

echo %PKG_BUILDNUM%
echo %PKG_NAME%
echo %PKG_VERSION%
echo %PKG_HASH%
echo %CONDA_PY%

::mkdir %PREFIX%\Scripts
mkdir %PREFIX%\Lib\site-packages\pyastroimageview
mkdir %PREFIX%\Lib\site-packages\pyastrobackend

:: copy without extension so conda-build will make .bat file for it!
copy Scripts\pyastroimageview_main.py %PREFIX%\Scripts\pyastroimageview_main

xcopy /s pyastroimageview %PREFIX%\Lib\site-packages\pyastroimageview
xcopy /s pyastrobackend %PREFIX%\Lib\site-packages\pyastrobackend

:: put version in sources so we can report it when program is run
echo VERSION='%PKG_VERSION%-py%CONDA_PY%%GIT_DESCRIBE_HASH%_%GIT_DESCRIBE_NUMBER%' >> %PREFIX%\Lib\site-packages\pyastroimageview\build_version.py
