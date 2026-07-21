# model-railway-signalling

A fully featured DCC Command Station, with a focus on enabling prototypical operation of your model
railway in terms of route setting, signal interlocking and signalling automation. Layout schematics
can be be designed and configured via the UI without the need for any code or bespoke electronics.
The application is primarily intended for the Raspberry Pi, but will also run on other platforms
(albeit without some of the Raspberry-Pi specific interfacing functions).

* Provides a full DCC Command station for your model railway layout:
    * Control your locos via on-screen throttles or via your tablet/smartphone.
    * Control all your DCC accessories intuitively via the on-screen schematic.
    * Includes a DCC programming utility for both 'one touch' and CV Programming.
* Enables signalling schematics to be easily created with route lines, points and signals:
    * Supports most types of UK colour light signals, semaphore signals, and ground signals.
    * Supports complex trackwork formations such as crossovers, slips and 3-way points.
    * Get the schematic looking how you want by changing the styles of objects as required.
* Enables intuitive and prototypical control of your DCC Accessories via the schematic:
    * Supports all standard DCC signals, points and other DCC accessory decoders.
    * Provides full interlocking of the signals and points on your layout.
    * Simply click the schematic to change the signals and points on your layout.
* Enables full signalbox simulations to be realised for your layout:
    * Add virtual 'Signal box Levers' to the schematic to control your signals/points.
    * Add virtual 'Block Instruments' for communication and coordination between signal boxes.
    * Supports integration with physical levers (such as the Cobalt-S Levers)
* Uses the RPi GPIO inputs (connected to external track sensors) to detect train movements:
    * Add 'Track Sections' to the schematic to provide a mimic diagram of train location.
    * Watch the trains 'move' through the schematic based on 'signal passed' events.
    * Alternatively, use 'track circuits' for an absolute indication of block occupancy
* Provides "one click" or 'NX' (Entry/Exit) set-up and clear-down routes:
    * Interlocking is preserved - Routes are disabled if conflicting movements are set.
    * Routes can be highlighted on the schematic to show they have been successfully set.
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

## What's new for Release 6.x.x:

> [!IMPORTANT]
> Release 6.x.x will only support the loading of layout files created by Release 6.0.0 or later.
> If you have layout files created by an earlier version of the application then you should first
> upgrade to Release 6.0.0 and then load/re-save your files before upgrading to Release 6.x.x.
> You have been warned!

* Keyboard shortcuts (see help=>help) will now work for both upper case or lower case keypresses)
* Minot editor performance improvements - when moving large numbers of selected objects


![Example Screenshot2](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot1.png)

Bug reports and feedback is welcome and appreciated:
* What aspects are intuitive? What aspects aren't?
* What aspects do you particularly like?
* What aspects particularly irritate you?
* What new features would you like to see?

email: enquiries@model-railway-signalling.co.uk
(if reporting bugs then please attach the sig file, application logs and any relevant screenshots)

## Installing the application (Raspberry Pi or Linux)

For a first time installation use:
<pre>
$ python3 -m pip install model-railway-signals
</pre>
When installing the application on later versions of python you may get the following error:
<pre>
error: externally-managed-environment
</pre>
To overcome this, add the '--break-system-packages' argument to the command - i.e.
<pre>
$ python3 -m pip install --break-system-packages model-railway-signals 
</pre>
To upgrade to the latest version use:
<pre>
$ python3 -m pip install --upgrade model-railway-signals
</pre>
To remove the application:
<pre>
$ python3 -m pip uninstall model-railway-signals
</pre>
To install a specific version of the application the application:
<pre>
$ python3 -m pip install model-railway-signals==4.5.0
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

Full documentation is packaged with the application (access by selecting Help => Docs from the main menubar).

A number of example layout files are also packaged with the application (access by selecting File => Examples from the main menubar)

My youTube channel also has a number of videos demonstrating the use of the application:
[https://www.youtube.com/@DCCModelRailwaySignalling](https://www.youtube.com/@DCCModelRailwaySignalling)

Note that I have seen problems running the application on some of the more recent Debian releases (such as Bookworm) that use
Wayland as the backend compositor rather than X11 - specifically significant degredation in GUI performance (especially when
editing a schematic), button rendering issues (not fully rendered until the cursor hovers over them) and window management
issues (e.g. windows not being bought to the front when un-minimised). I also saw these issues with other applications/

The fix was to switch the GUI Compositor back to X11 - Run "sudo raspi-config", select 'Advanced Options' then 'Wayland' and select X11.


