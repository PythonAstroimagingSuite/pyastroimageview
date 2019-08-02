#!/bin/bash

# Linux
PYUIC5="pyuic5"

# Windows
#PYIC5=/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat 

echo "Making uic python files for pyastroimageview"
for i in 'focuser' 'mount' 'camera' 'filterwheel' 'general' 'sequence' 'phd2'; do
echo $i
"$PYUIC5" ${i}_settings.ui > ../../../pyastroimageview/uic/${i}_settings_uic.py
done

echo "imagearea"
"$PYUIC5"  imagearea_info.ui > ../../../pyastroimageview/uic/imagearea_info_uic.py

echo "cameraroidialog"
"$PYUIC5"  camera_roidialog.ui > ../../../pyastroimageview/uic/camera_roidialog_uic.py

echo "phd2settingsdialog"
"$PYUIC5"  phd2_settings_dialog.ui > ../../../pyastroimageview/uic/phd2_settings_dialog_uic.py

echo "sequencetitlehelp"
"$PYUIC5" sequence_title_help.ui > ../../../pyastroimageview/uic/sequence_title_help_uic.py
