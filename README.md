# model-railway-signalling

A DCC model railway signalling application written in Python, enabling automated and interlocked layout 
signalling schemes to be designed and configured via the UI without the need to write any code. The
application is primarily intended for the Raspberry Pi, but will also run on other platforms (albeit 
without some of the Raspberry-Pi specific interfacing functions). 

* Enables layout schematics to be created with signals, points, track sections and block instruments.
* Supports automation of signals based on track occupancy and state of signals on the route ahead.
* Supports "one touch" configuration of routes (signals and points) with route highlighting.
* Supports virtual DCC switches on the schematic for the control of other DCC layout accessories.
* Supports most types of UK colour light signals, semaphore signals, and ground signals.
* Interfaces with the Pi-SPROG DCC command station to drive the signals and points out on the layout.
* Uses the Raspberry Pi GPIO inputs to provide train detection in support of signalling automation.
* Incorporates MQTT networking to allow multiple signalling applications to be linked for larger layouts.
* Supports virtual Block Instruments (with networking)for coordinating movements between signal boxes
* Provides a [Public API](https://github.com/johnrm174/model-railway-signalling/blob/main/PUBLIC_API.md) 
to support custom layout control interfaces.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)

Configured / pre-installed systems are now available to purchase from:
[https://www.model-railway-signalling.co.uk/](https://www.model-railway-signalling.co.uk/)
The website also included a number of user guides that can be downloaded (in PDF format).

My youTube channel also has a number of videos demonstrating the use of the application:
[https://www.youtube.com/@DCCModelRailwaySignalling](https://www.youtube.com/@DCCModelRailwaySignalling)

## What's new for Release x.x.x:

* New 'Signalbox Levers' feature - enables you to achieve a fully prototypical simulation of a signalbox:
    * Levers can be added to the schematic and 'connected' to the signals and points they control.
    * Seperate levers can be assigned to a point's blades and Facing Point Lock (FPL). 
    * Seperate levers can be asigned to each signal 'route' (i.e. semaphore signal arm or colour light signal route). 
    * Full interlocking is preserved, with a clear indication on the Signalbox lever as to the state of the interlocking.
* Keyboard 'keycode' events can be mapped to Signalbox Levers:
    * Enables easy integration with physical levers (such as the DCC Concepts S lever) via readily available keyboard encoders. 
    * Interlocking can either be preserved (recommended) or disabled (if you want the signals/points to reflect the state of the physical levers).
    * Options are provide to display pop-up warnings if the user switches an external lever is switched whilst the lever is locked.
* Schematic Object bulk renumbering utility:
    * An easy way to consolidate your Signal, Point and Signalbox Lever numbering
    * Most other schematic object types can also be renumbered as required
* Improvements to the operation of Momentary DCC Switches:
    * DCC Commands can now be specified for both the 'press' and 'release' events
    * A fixed 'release delay' can now be specified to 'hold' the momentary switch on
* New SPROG DCC Address Mode settings option - to cater for the 'DCC Address offsets of 4' issue sometimes
experienced when transitioning from one DCC System to another (where the NMRA specification has been interpreted
differently by different DCC system manufacturers/suppliers)
* The 'Reset Layout' function now preserves track occupancy and incorporates a user-configurable switching 
delay so point and signal changes can now be sequenced (to avoid overloading the DCC accessory bus on larger
layouts which may require a large number of points and/or signals to be reset back to their default states).
* Improved display of Signal Passed at Danger (SPAD warnings) - subsequent warnings are now added to the
existing pop-up window (rather than appearing in a new pop-up). This can now be left open without affecting
the normal operation of the application.
* GPIO sensor events (e.g. 'signal passed', 'sensor passed' etc) are now only processed in Run Mode.
* Bugfix to Block Instruments sound file selection (due to breaking change in 'importlib' package).
* Bugfix to the display of validation messages in the 'settings' windows on Apply/OK.

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
