#!/bin/bash
echo "Making uic python files for pyastroimageview"
for i in 'focuser' 'mount' 'camera' 'filterwheel' 'general'; do 
echo $i
/c/Anaconda3/Library/bin/pyuic5.bat pyastroimageview_${i}_settings.ui > ../../../pyastroimageview/uic/pyastroimageview_${i}_settings_uic.py
done

echo "imagearea"
/c/Anaconda3/Library/bin/pyuic5.bat pyastroimageview_imagearea_info.ui > ../../../pyastroimageview/uic/pyastroimageview_imagearea_info_uic.py

echo "cameraroidialog"
/c/Anaconda3/Library/bin/pyuic5.bat pyastroimageview_camera_roidialog.ui > ../../../pyastroimageview/uic/pyastroimageview_camera_roidialog_uic.py

