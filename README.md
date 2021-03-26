# model-railway-signalling
A model railway signalling system written in Python for the raspberry Pi with a DCC control of Signals and Points

This has been created to provide a representation of my layout, complete with points, signals and "track occupancy" sections
A simple interface to the Pi-SPROG-3 DCC Command station enables DCC control of the signals and points out on the layout. 

All of the functions for creating and managing 'signals', 'points', 'sections' have been developed as a Python Package 
to promote re-use across other layouts. This includes generic functions for mapping the signals and points to one or more
DCC addresses such that the majority of DCC decoder types and DCC signal types can be easily integrated (note that the 
software can be used without the Pi-SPROG-3). Functions are provided to support interlocking of signals and points to 
enable fully prototypical signalling schemes to be developed 

Most types of colour light signals (and ground position light signals) are supported. Semaphores are still on my TODO list.

As far as the code is concerned, I've tried to keep it simple - and readable to those that aren't intimately familiar with
some of the "advanced" aspects of the python language (e.g. I've avoided most of the object-oriented constructs where possible)

To give it a go, just clone the repository and and run one of the following:

'test_simple_example.py' - a simple example of how to use the "signals" and "points" modules to create a basic track 
                           schematic with interlocked signals/points. Also includes a simple DCC Mapping example.

'test_dcc_signal_control.py'- developed primarily for testing using the Harmann Signallist SC1 decoder. Enables the various
                              modes to be selected (includes programming of the required CVs) and then tested. I used this
                               decoder as it seemed to provide the most flexibility for some of my more complex signal types

'test_colour_light_signals.py'- developed primarily for testing, but it does provide an example of every signal type and all
                                the control features currently supported

'my_layout'- Still very much work in progress but should give a good example of how a fully interlocked (and relatively
              complex) signalling system can be built using the generic functions provided by the core software functions 


Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)
