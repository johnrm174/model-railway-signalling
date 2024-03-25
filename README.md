# model-railway-signalling

A DCC model railway signalling application written in Python, enabling automated and interlocked layout 
signalling schemes to be designed and configured via the UI without the need to write any code. The 
application is primarily intended for the Raspberry Pi, but will also run on other platforms (albeit 
without some of the Raspberry-Pi specific interfacing functions).

* Enables layout schematics to be created with signals, points, track sections and block instruments.
* Supports most types of UK colour light signals, semaphore signals, and ground signals.
* Interfaces with the Pi-SPROG DCC command station to drive the signals and points out on the layout.
* Uses the Raspberry Pi GPIO inputs to provide train detection in support of signalling automation.
* Incorporates MQTT networking to allow multiple signalling applications to be linked for larger layouts.
* Provides a Public API [Public API](https://github.com/johnrm174/model-railway-signalling/blob/main/PUBLIC_API.md) to enable integration with custom layout interfaces.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)

Configured / pre-installed systems are now available to purchase from:
[https://www.model-railway-signalling.co.uk/](https://www.model-railway-signalling.co.uk/)

## What's new for Release 4.2.0:

* New 'Track Sensors' feature - extends track occupancy into non-signalled areas such as goods yards and MPDs.
* Improved 'signal passed' logic - will now detect (and warn the user about) Signal Passed at Danger events.
* New DCC Mappings utility - to display all mapped DCC addresses and the signals/points they are assigned to.
* Improved DCC validation - Prevents DCC addresses being mapped if already assigned to another signal or point.
* Improved GPIO Sensor Settings window -  now includes a back reference to the mapped Signals / 'Track sensors'.
* GPIO library updated - GPIO inputs are now fully functional on the most recent versions of RPi-OS/Python.
* A new Public API - to enable integration of your own custom layout interfaces via the MQTT network.

Bug reports and feedback are welcome and appreciated:
* What aspects are intuitive? What aspects aren't?
* What aspects do you particularly like?
* What aspects particularly irritate you?
* What new features would you like to see?

## Installing the application

For a first time installation use:
<pre>
$ python3 -m pip install model-railway-signals 
</pre>
To upgrade to the latest version use:
<pre>
$ python3 -m pip install --upgrade model-railway-signals 
</pre>
If you want to use Block Instruments with full sound enabled (bell rings and telegraph key sounds)
then you will also need to install the 'simpleaudio' package. Note that for Windows it has a dependency 
on Microsoft Visual C++ 14.0 or greater (so you will need to ensure Visual Studio 2015 is installed first).
If 'simpleaudio' is not installed then the software will still function correctly (just without sound).
<pre>
$ python3 -m pip install simpleaudio
</pre>
Note that if you are running on a later version of Python you may need to install libasound2 before the simpleaudio pip install will work.
<pre>
$ sudo apt-get install libasound2-dev
</pre>

## Running the application

The python package should be run as a module (note underscores):
<pre>
$ python3 -m model_railway_signals
</pre>
If required, a layout schematic can be loaded at startup:
<pre>
$ python3 -m model_railway_signals -f layout_file.sig
</pre>
If required, the logging level can be specified at startup (ERROR, WARNING, INFO or DEBUG)
<pre>
$ python3 -m model_railway_signals -f layout_file.sig -l DEBUG
</pre>

Documentation, in the form of a Quick-Start guide can be found in the 'user_guide' folder: 
[https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide](https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide)

Some example layout configuration files can be found in the 'configuration_examples' folder:
[https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples](https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples)

And finally, a top tip for running the application on the latest Debian Bookworm release which uses Wayland as the GUI backend
rather than X11 (which was the backend for previous Debian releases). I found that with Wayland, the Tkinter GUI performance
was terrible for some reason (not just my application - python/Tkinter performance in general) - and that was running on a
Raspberry Pi 5 which I would have expected to improve overall performance. Anyway, I found that the fix is to switch the GUI
backend of the Raspberry Pi back to X11 - performance of the user interface is now lightning quick!

To change the backend - Run "sudo raspi-config", select 'Advanced Options' then 'Wayland' and select X11.

An additional benifit was that some of the other applications I use (such as the kazam video capture software)
will now work as normal on the Raspberry Pi 5.



