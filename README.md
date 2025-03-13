# model-railway-signalling

A DCC model railway signalling application written in Python, enabling automated and interlocked layout 
signalling schemes to be designed and configured via the UI without the need to write any code. The
application is primarily intended for the Raspberry Pi, but will also run on other platforms (albeit 
without some of the Raspberry-Pi specific interfacing functions). 

* Enables signalling schematics to be easily created with route lines, points and signals:
    * Supports most types of UK colour light signals, semaphore signals, and ground signals.
    * Supports complex trackwork formations such as crossovers, slips and 3-way points.
    * Get the schematic looking how you want by changing the styles of objects as required.
* Interfaces with the Pi-SPROG DCC command station to drive all of your DCC Accessories:
    * Uses a DCC Accessory bus (seperate from the track bus) to control your layout.
    * Supports all standard DCC signals, point motors and other DCC accessory decoders.
    * Signals and points are simply operated via their control buttons on the schematic.
    * Add virtual 'DCC Switches' to the schematic to control other DCC accessories.
    * Includes a DCC programming utility for both 'one touch' and CV Programming.
* Enables full signalbox simulations to be realised for your layout:
    * Add virtual 'Signal box Levers' to the schematic to control your signals/points.
    * Supports integration with external switches (Such as the DCC Concepts Cobalt S Levers).
    * Add virtual 'Block Instruments' for communication and coordination between signal boxes.
* Uses the RPi GPIO inputs (connected to external track sensors) to detect train movements:
    * Add 'Track Sections' to the schematic to provide a mimic diagram of train location.
    * Train designators then 'move' through the schematic based on 'signal passed' events.
    * Track occupancy can then be used to support signal automation (see below).
* Provides full prototypical operation of your layout - just like the real thing.
    * Signals can be interlocked with points, other signals and Track Sections ahead.
    * Points are interlocked with the signals that control movements across them.
    * Multiple aspect signals will always reflect the state of the signal ahead.
    * Signals can be automated based on the 'occupancy' of Track Sections ahead.
* Provides "one click" set-up and clear-down routes through your layout:
    * Interlocking is preserved - Routes are disabled if conflicting movements are set.
    * Routes are highlighted on the schematic to show they have been successfully set.
    * Supports automated set-up and clear-down of routes based on GPIO sensor events.
* Incorporates MQTT networking to allow multiple signalling applications to be linked.
    * Allows multiple signalling areas or signal boxes to be created for larger layouts
    * Multiple applications use the same DCC command station for control of your layout.
    * Provides easy expansion of the number of external Track Sensors that can be used.
* Full documentation and several example layout files are packaged with the application.

The application also provides a [Public API](https://github.com/johnrm174/model-railway-signalling/blob/main/PUBLIC_API.md) 
to support custom layout control interfaces.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)

Configured / pre-installed systems are now available to purchase from:
[https://www.model-railway-signalling.co.uk/](https://www.model-railway-signalling.co.uk/)
The website also included a number of user guides that can be downloaded (in PDF format).

My youTube channel also has a number of videos demonstrating the use of the application:
[https://www.youtube.com/@DCCModelRailwaySignalling](https://www.youtube.com/@DCCModelRailwaySignalling)

## What's new for Release 5.x.x:

> [!IMPORTANT]
> Release 5.x.x will only support the loading of layout files created by Release 5.0.0 or later.
> If you have layout files created by an earlier version of the application then you should first
> upgrade to Release 5.0.0 and then load/re-save your files before upgrading to Release 5.x.x.
> You have been warned!

* Bugfix to Bulk Renumbering - State is now saved so subsequent Undos/Redos work properly.
* Bugfix to applying line configuration changes in Run Mode - Selection circles are now hidden.
* Improvement - Line width can now be edited in the Line and Point configuration dialogs.
* Improvement - To the synchronisation of state across networked layouts on MQTT broker connect.
* New Feature - New 'dashed' options for points and route lines (to represent hidden trackwork).
* New Feature - Route lines & points can be added to Track Sections (to highlight when occupied).
* New Feature - Support for 'track circuit' train detection as an alternative to event-based sensors.
* GPIO Sensors - Are now enabled in all Modes (inhibiting them in Edit mode wasn't a good idea).
* GPIO Sensors - New 'circuit breaker' functionality to lock out 'noisy' GPIO inputs.
* GPIO Sensors - Settings window now provides an indication of the state of each GPIO input.
* TBD, TBD

![Example Screenshot2](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot1.png)

Bug reports and feedback is welcome and appreciated:
* What aspects are intuitive? What aspects aren't?
* What aspects do you particularly like?
* What aspects particularly irritate you?
* What new features would you like to see?

email: enquiries@model-railway-signalling.co.uk
(if reporting bugs then please attach the sig file, application logs and any relevant screenshots)

## Installing the application

For a first time installation use:
<pre>
$ pip install model-railway-signals             <== This should work for most python installations
or
$ python -m pip install model-railway-signals   <== If the command line version of pip is not installed/enabled
or
$ python3 -m pip install model-railway-signals  <== If you have multiple major versions of python installed
</pre>
When installing the application on later versions of python you may get the following error:
<pre>
error: externally-managed-environment
</pre>
To overcome this, add the '--break-system-packages' argument to the command - e.g.
<pre>
$ pip install --break-system-packages model-railway-signals 
</pre>
To upgrade to the latest version use:
<pre>
$ pip install --upgrade model-railway-signals            <== This should work for most python installations
or
$ python -m pip install --upgrade model-railway-signals  <== If the command line version of pip is not installed/enabled
or
$ python3 -m pip install --upgrade model-railway-signals <== If you have multiple major versions of python installed
</pre>
To remove the application:
<pre>
$ pip uninstall model-railway-signals                    <== This should work for most python installations
or
$ python -m pip uninstall model-railway-signals          <== If the command line version of pip is not installed/enabled
or
$ python3 -m pip uninstall model-railway-signals         <== If you have multiple major versions of python installed
</pre>
To install a specific version of the application the application:
<pre>
$ pip install model-railway-signals==4.5.0               <== This should work for most python installations
or
$ python -m pip install model-railway-signals==4.5.0     <== If the command line version of pip is not installed/enabled
or
$ python3 -m pip install model-railway-signals==4.5.0    <== If you have multiple major versions of python installed
</pre>
The application has minimum external dependencies (over and above the 'standard' python installation),
'pyserial' and 'paho-mqtt', both of which should automatically get installed with the application.
If for some reason this doesn't happen (I've been made aware of one instance on a Windows platform) then
these packages can be installed seperately (prior to installing the model-railway-signals package):
<pre>
$ pip install paho-mqtt
$ pip install pyserial
</pre>
If you want to use Block Instruments with full sound enabled (bell rings and telegraph key sounds)
then you will also need to install the 'simpleaudio' package. If 'simpleaudio' is not installed then 
the application will still function correctly (just without sound).
<pre>
$ pip install simpleaudio
</pre>
If you are running on a later version of Python you may need to install libasound2 before the simpleaudio pip install will work.
<pre>
$ sudo apt-get install libasound2-dev
</pre>
Note that for Windows, the 'simpleaudio' it has a dependency  on Microsoft Visual C++ 14.0 or greater 
(so you will need to ensure Visual Studio 2015 is installed first).

## Running the application

The python package should be run as a module (note underscores):
<pre>
$ python -m model_railway_signals  <== This should work for most python installations
or
$ python3 -m model_railway_signals <== If you have multiple major versions of python installed
</pre>
If required, a layout schematic can be loaded at startup:
<pre>
$ python -m model_railway_signals -f layout_file.sig
</pre>
If required, the logging level can be specified at startup (ERROR, WARNING, INFO or DEBUG)
<pre>
$ python -m model_railway_signals -f layout_file.sig -l DEBUG
</pre>

Application documentation, can be found in the 'user_guide' folder: 
[https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide](https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide)

Some example layout configuration files can be found in the 'configuration_examples' folder:
[https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples](https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples)

My youTube channel also has a number of videos demonstrating the use of the application:
[https://www.youtube.com/@DCCModelRailwaySignalling](https://www.youtube.com/@DCCModelRailwaySignalling)

And finally, a top tip for running the application on the latest Debian Bookworm release which uses Wayland as the GUI backend
rather than X11 (which was the backend for previous Debian releases). I found that with Wayland, the Tkinter GUI performance
was terrible for some reason (not just my application - python/Tkinter performance in general) - and that was running on a
Raspberry Pi 5 which I would have expected to improve overall performance. Anyway, I found that the fix is to switch the GUI
backend of the Raspberry Pi back to X11 - performance of the user interface is now lightning quick!

To change the backend - Run "sudo raspi-config", select 'Advanced Options' then 'Wayland' and select X11.

An additional benifit was that some of the other applications I use (such as the kazam video capture software)
will now work as normal on the Raspberry Pi 5.

