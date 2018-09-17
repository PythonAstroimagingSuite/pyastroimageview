#!/bin/bash
echo "Making uic python files for pyastroimageview"
for i in 'focuser' 'mount' 'camera' 'filterwheel' 'general' 'sequence' 'phd2'; do
echo $i
/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat ${i}_settings.ui > ../../../pyastroimageview/uic/${i}_settings_uic.py
done

echo "imagearea"
/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat imagearea_info.ui > ../../../pyastroimageview/uic/imagearea_info_uic.py

echo "cameraroidialog"
/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat camera_roidialog.ui > ../../../pyastroimageview/uic/camera_roidialog_uic.py

echo "phd2settingsdialog"
/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat phd2_settings_dialog.ui > ../../../pyastroimageview/uic/phd2_settings_dialog_uic.py

echo "sequencetitlehelp"
/c/Users/msf/Anaconda3/Library/bin/pyuic5.bat sequence_title_help.ui > ../../../pyastroimageview/uic/sequence_title_help_uic.py