# model-railway-signalling

A DCC model railway signalling system written in Python. Primarily intended for the Raspberry Pi, but 
will also run on other platforms (albeit without some of the Raspberry-Pi specific interfacing functions). 
Most types of colour light signals, semaphore signals, and ground signals are supported.
* Interfaces with the Pi-SPROG DCC command station to drive the signals and points out on the layout
* Uses the Raspberry Pi GPIO inputs to provide train detection in support of signalling automation

## Layout editor

From Release 3.0.0, the schematic editor application enables automated and interlocked layout signalling 
schemes to be designed and configured without the need to write any code. Note that the editor is in
active development so any comments and suggestions for future features are welcome.

What's supported in Release 3.3.0:
* Draw your layout schematic with lines, points, signals and track occupancy sections
* Define the DCC command sequences to drive the signals and points out on the layout
* Configure the signals and points to implement protototypical interlocking schemes
* Configure GPIO sensors and track sections to provide a 'mimic' display of the layout
* Automation of signals as trains traverse the routes that have been configured
* Save and load your layout schematic and state between running sessions
* Block instruments - with interlocking of starting signals
* Popup error messages when things go wrong (reduced reliance on logs)

What's coming soon:
* MQTT networking (for linking layouts)
* Application documentation

Any bug reports and feedback you may have would be gratefully appreciated - specifically:
* What aspects are intuitive? What aspects aren't?
* What aspects do you particularly like?
* What aspects particularly irritate you?

There are some example layout files in the 'configuration_examples' folder.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot2.png)
## Library functions

All of the functions for creating and managing 'signals', 'points', 'sections', 'sensors' and 'block instruments' 
have been developed as a Python Package to promote re-use across other layouts. This includes functions to support 
the interlocking of signals, points and block instruments, enabling fully prototypical signalling schemes to be 
developed in code.

An interface to a SPROG DCC Command station enables control of the signals and points out on the layout. 
The signals and points can be mapped to one or more DCC addresses in a manner that should be compatible with 
the majority of DCC signal/points decoders currently on the market. A GPIO interface allows external train 
detectors to be connected in via opto-isolators. These sensors can be configured to trigger 'signal approached' 
or 'signal passed' events, enabling full automatic control of the layout signalling. A MQTT interface enables 
multiple signalling applications to be networked together so that complex layouts can be split into different 
signalling sections/areas, with communication between them.

![Example Screenshot](https://github.com/johnrm174/model-railway-signalling/blob/main/README_screenshot1.png)

## Installation

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

## Using the layout editor

To run the editor application:

The python package should be run as a module (note underscores):
<pre>
$ python3 -m model_railway_signals
</pre>
or to load a layout schematic at startup
<pre>
$ python3 -m model_railway_signals -f layout_file.sig
</pre>

## Using the library functions

To use the public API functions for developing your own layout signalling system:
<pre>
from model_railway_signals import * 
</pre>
For details of the API and code examples see the seperate 'PUBLIC_API.md' file.

