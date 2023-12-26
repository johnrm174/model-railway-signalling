# model-railway-signalling

A DCC model railway signalling application written in Python, enabling automated and interlocked layout 
signalling schemes to be designed and configured via the UI without the need to write any code. The 
application is primarily intended for the Raspberry Pi, but will also run on other platforms (albeit 
without some of the Raspberry-Pi specific interfacing functions).

* Enables layout schematics to be created with signals, points, track sections and block instruments
* Supports most types of UK colour light signals, semaphore signals, and ground signals.
* Interfaces with the Pi-SPROG DCC command station to drive the signals and points out on the layout
* Uses the Raspberry Pi GPIO inputs to provide train detection in support of signalling automation
* Incorporates MQTT networking to allow multiple signalling applications to be linked for larger layouts

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)

## What's new for Release 4.0:

* Application documentation in the form of a 'quick-start' guide (see below for link)
* 'Arrow keys' will 'nudge' objects in edit mode (or scroll canvas if nothing selected)
* 'Escape' key can be used to cancel 'in progress' object moves and area selections
* 'Cntl-r' will reset the main window to fit the specified canvas size (after user re-sizing)
* 'Cntl-m' is now the keyboard shortcut for toggling Edit/Run mode (for consistency)
* Improvements to layout load - errors/warnings simplified (no more spam messages)
* Text boxes - Ability to add/edit text boxes on the schematic to annotate the layout
* Canvas configuration - Ability to change the grid size and toggle 'snap-to-grid'
* Toggle signal automation - Be an active signalman or just watch the trains go by
* Signals can be overridden (to DANGER) on up to 3 track sections ahead
* Signals can be interlocked with up to 3 occupied track sections ahead
* Basic DCC Programming - 'one touch' and Configuration Variable (CV) programming
* Consolidation of library functions (deprecated library API functions removed)
* Minor bugfixes and application enhancements to improve the overall user experience

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

## Running the application

The python package should be run as a module (note underscores):
<pre>
$ python3 -m model_railway_signals
</pre>
If required, a layout schematic can be loaded at startup
<pre>
$ python3 -m model_railway_signals -f layout_file.sig
</pre>

Documentation, in the form of a Quick-Start guide can be found in the 'user_guide' folder: 
[https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide](https://github.com/johnrm174/model-railway-signalling/tree/main/user_guide)

Some example layout configuration files can be found in the 'configuration_examples' folder:
[https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples](https://github.com/johnrm174/model-railway-signalling/tree/main/configuration_examples)

