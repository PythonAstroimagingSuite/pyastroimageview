#!/bin/bash
echo "Making uic python files for pyastroimageview"
for i in 'focuser' 'mount' 'camera' 'filterwheel' 'general'; do 
echo $i
/c/Anaconda3/Library/bin/pyuic5.bat ${i}_settings.ui > ../../../pyastroimageview/uic/${i}_settings_uic.py
done

echo "imagearea"
/c/Anaconda3/Library/bin/pyuic5.bat imagearea_info.ui > ../../../pyastroimageview/uic/imagearea_info_uic.py

echo "cameraroidialog"
/c/Anaconda3/Library/bin/pyuic5.bat camera_roidialog.ui > ../../../pyastroimageview/uic/camera_roidialog_uic.py

