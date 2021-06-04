@ECHO OFF

cd C:\Program Files\Azure Kinect SDK v1.2.0\tools\

START k4arecorder.exe -l 30 --imu OFF "D:\Kinect\file.mkv"

TIMEOUT 40

cd D:\Kinect

ren "file.mkv" "Clip - %date:/=-% %time::=-%.mkv"

pause