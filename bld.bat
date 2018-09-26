echo "BUILD SCRIPT RUNNING"

:: add to path to find whatever bash we're going to use!
:: SET PATH=%PATH%;C:\Users\msf\AppData\Local\Programs\Git\bin
:: bash -c "echo 'BASH RUN TEST'"

echo %PREFIX%

::mkdir %PREFIX%\Scripts
mkdir %PREFIX%\Lib\site-packages\pyastroimageview
mkdir %PREFIX%\Lib\site-packages\pyastrobackend

:: copy without extension so conda-build will make .bat file for it!
copy Scripts\pyastroimageview_main.py %PREFIX%\Scripts\pyastroimageview_main

dir %PREFIX%\Scripts\

xcopy /s pyastroimageview %PREFIX%\Lib\site-packages\pyastroimageview
xcopy /s pyastrobackend %PREFIX%\Lib\site-packages\pyastrobackend
