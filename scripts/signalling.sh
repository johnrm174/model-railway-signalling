#!/bin/sh
# signalling.sh
#
# Shell script to run up the model railway signalling application
# Will also re-direct the logs to a file based on the current time and date
# Script should be saved as: /home/<user>/.config/autostart/signalling.sh
# Remember to change instances of 'signalbox' to your user name in the script below
# Permissions should be set to make the script executable: chmod 755 signalling.sh
# Note we give ourselves a delay before application startup and shutdown to intervene if required
##
echo "Starting signalling application in 5 seconds - Hit <CNTL-C> to abort"
sleep 5
filename=signalling.log
current_time=$(date "+%Y%m%d-%H%M%S")
logfilename=$current_time-$filename
echo $logfilename >> /home/signalbox/"Signalling Logs"/$logfilename 2>&1
#
# Modify the filename after the -f flag to load a different layout file on startup
# eg: python3 -m model_railway_signals -f /home/signalbox/my_layout.sig
# You can also specify a different logging level if required (DEBUG, INFO, WARNING or ERROR)
# eg: python3 -m model_railway_signals -f /home/signalbox/my_layout.sig -l DEBUG
#
python3 -m model_railway_signals -f /home/signalbox/sensor_node.sig >> /home/signalbox/"Signalling Logs"/$logfilename 2>&1
#
# Comment out the following lines if you don't want to shut down the Raspberry Pi on application exit
#
echo "Shutting down Raspberry Pi in 5 seconds - Hit <CNTL-C> to abort"
sleep 5
echo "Shutting down Raspberry Pi now"
shutdown -h now