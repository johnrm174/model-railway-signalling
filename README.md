# model-railway-signalling
A model railway signalling system written in Python for the raspberry Pi

This has been created to provide a representation of my layout, complete with points, signals and the switchable "power sections" 
(yep - its all still analogue at the moment). I have also provided "track occupancy sections" and a means of triggering "signal 
passed" events to support future automation.  A simple interface to the Pi-SPROG-3 DCC Command station enables DCC control of
the signals and points out on the layout

Although most of the code is specific to my particular layout, I have tried to write the underlying modules and functions 
('signals', 'points' 'switches' - and the DCC interface) to promote re-use in other layouts. Currently most types of
colour light signals (and position light signals) are supported. Semaphores are still on my TODO list

As far as the code is concerned, I've tried to keep it simple - and readable to those that aren't intimately familiar with
some of the "advanced" aspects of the python language (e.g. I've avoided most of the object-oriented constructs where possible)

To give it a go, just download the files and run 'my_layout'

For a simple example of how to use the "signals" and "points" modules with the tkinter graphics package to create a basic 
track schematic with interlocked signals/points see the 'simple_example.py'

For examples of all the currently supported signal types see 'test_colour_light_signals.py'

For an example of how DCC signals and points can be "mapped" into the system - see 'test_dcc_signal_control.py'

Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)
