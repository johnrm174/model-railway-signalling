#!/bin/sh
# signalling.sh
#
# Example shell script to run up the model railway signsalling application
# And write the logs to a log file based on the current time and date
# Permissions should be set to make the script executable: chmod 755 signalling.sh
# Script should be saved as: /home/pi/.config/autostart/signalling.sh
#
filename=signalling.log
current_time=$(date "+%Y%m%d-%H%M%S")
logfilename=$current_time-$filename
#
# you can modify the following to use the -f <filename> option to load a layout on startup
# eg: python3 -m model_railway_signals -f /home/pi/my_layout.sig
#
echo $logfilename >> /home/pi/.config/autostart/$logfilename 2>&1
python3 -m model_railway_signals >> /home/pi/.config/autostart/$logfilename 2>&1
#
# Uncomment the following lines to shut down the Raspberry Pi on application exit
# Useful for remote nodes being used to publish networked track sensors
#
#echo "Shutting down in 60 seconds" >> /home/pi/.config/autostart/$logfilename 2>&1
#sleep 60
#echo "Shutting down now" >> /home/pi/.config/autostart/$logfilename 2>&1
#shutdown -h now