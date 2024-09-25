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
* Provides a [Public API](https://github.com/johnrm174/model-railway-signalling/blob/main/PUBLIC_API.md) 
to support custom layout control interfaces.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)

Configured / pre-installed systems are now available to purchase from:
[https://www.model-railway-signalling.co.uk/](https://www.model-railway-signalling.co.uk/)
The website also included a number of user guides that can be downloaded (in PDF format).

My youTube channel also has a number of videos demonstrating the use of the application:
[https://www.youtube.com/@DCCModelRailwaySignalling](https://www.youtube.com/@DCCModelRailwaySignalling)

## What's new for Release 4.6.1:

* HOTFIX - Removed GPIO sensor de-bounce as this was causing sensor triggering issues
* Improvement - Reduced scroll rate when scrolling canvas via mouse (drag and drop) in Run Mode
* Improvement - Increased fontsize and padding for Route Buttons (easier to select via touchscreen)

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
$ pip install model-railway-signals <== This should work for most python installations
or
$ python -m pip install model-railway-signals <== If the command line version of pip is not installed/enabled
or
$ python -m pip install model-railway-signals <== If you have multiple major versions of python installed
</pre>
When installing the application on later versions of python you may get the following error:
<pre>
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.11/README.venv for more information.
</pre>
To overcome this, remove the 'EXTERNALLY-MANAGED' file from the default python installation and then re-attempt the install (as above).
Note that this is the file location for the Raspberry Pi python 3.11 installation. Other platforms may use a different location for this file:
<pre>
$ sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
</pre>
To upgrade to the latest version use:
<pre>
$ pip install --upgrade model-railway-signals            <== This should work for most python installations
or
$ python -m pip install --upgrade model-railway-signals  <== If the command line version of pip is not installed/enabled
or
$ python -m pip install --upgrade model-railway-signals  <== If you have multiple major versions of python installed
</pre>
To remove the application:
<pre>
$ pip uninstall model-railway-signals <== This should work for most python installations
or
$ python -m pip uninstall model-railway-signals          <== If the command line version of pip is not installed/enabled
or
$ python -m pip uninstall model-railway-signals          <== If you have multiple major versions of python installed
</pre>
To install a specific version of the application the application:
<pre>
$ pip install model-railway-signals==4.5.0               <== This should work for most python installations
or
$ python -m pip install model-railway-signals==4.5.0     <== If the command line version of pip is not installed/enabled
or
$ python -m pip install model-railway-signals==4.5.0     <== If you have multiple major versions of python installed
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
