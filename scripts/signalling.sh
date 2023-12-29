#!/bin/sh
# signalling.sh
#
# Example shell script to run up the model railway signalling application
# Will also re-direct the logs to a file based on the current time and date
# Script should be saved as: /home/pi/.config/autostart/signalling.sh
# Permissions should be set to make the script executable: chmod 755 signalling.sh
#
filename=signalling.log
current_time=$(date "+%Y%m%d-%H%M%S")
logfilename=$current_time-$filename
echo $logfilename >> /home/pi/.config/autostart/$logfilename 2>&1
#
# Modify the following to use the -f <filename> option to load a layout on startup
# eg: python3 -m model_railway_signals -f /home/pi/my_layout.sig
#
python3 -m model_railway_signals >> /home/pi/.config/autostart/$logfilename 2>&1
#
# Uncomment the following lines to shut down the Raspberry Pi on application exit
# Useful for when remote nodes are being used to publish networked track sensors
# Note we give ourselves a minute before shutdown to intervene if things go wrong
#
#echo "Shutting down in 60 seconds" >> /home/pi/.config/autostart/$logfilename 2>&1
#sleep 60
#echo "Shutting down now" >> /home/pi/.config/autostart/$logfilename 2>&1
#shutdown -h now