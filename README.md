# model-railway-signalling
A model railway signalling system written in Python for the Raspberry Pi with a DCC control of Signals and Points and train 
detection via the GPIO ports on the Pi

This has been created to provide a representation of my layout, complete with points, signals and "track occupancy" sections
A simple interface to the Pi-SPROG-3 DCC Command station enables DCC control of the signals and points out on the layout. 
The GPIO interface allows external train detectors such as the BlockSignalling BOD2-NS to be connected in via opto-isolators.

All of the functions for creating and managing 'signals', 'points' and 'sections' have been developed as a Python Package 
to promote re-use across other layouts. This includes functions to support the interlocking of signals and points to enable 
fully prototypical signalling schemes to be developed. The signals and points opjects can be easily mapped to one or more DCC 
addresses in a manner that should be compatible with the majority of DCC signal/points decoders currently on the market. 
Track sensors can also be easily integrated (via the Raspberry Pi's GPIO interface) to enable full automatic control.

Most types of colour light signals (and ground position light signals) are supported. Semaphores are still on my TODO list.

Note that the software is fully stand alone and can be used without the Pi-SPROG-3 or any external track sensors connected.
This allows you to fully develop and test a particular signalling scheme prior to interfacing it out to the layout.


As far as the code is concerned, I've tried to keep it simple - and readable to those that aren't intimately familiar with
some of the "advanced" aspects of the python language (e.g. I've avoided most of the object-oriented constructs where possible)

To give it a go, just clone the repository and and run one of the following:

'test_simple_example.py' - a simple example of how to use the "signals" and "points" modules to create a basic track 
                           schematic with interlocked signals/points. Also includes a simple DCC Mapping example 
                           (1 signal and 2 points ) and an external track sensor to provide a "signal passed" event.

'test_approach_control.py' - an example of using automated "approach control" for junction signals. This is where a signal
                            displays a more restrictive aspect (either red or yellow) when a lower-speed divergent route is
                            set, forcing the approaching train to slow down and be prepared to stop. As the train approaches, 
                            the signal is "released", allowing the train to proceed past the signal and onto the divergent route
                            Examples of "Approach on Red" and "Approach on Yellow" are provided. For "Approach on yellow", the
                            signals behind will show the correct single and double flashing yellow aspects.

'test_dcc_signal_control.py'- developed primarily for testing using the Harmann Signallist SC1 decoder. Enables the various
                              modes to be selected (includes programming of the required CVs) and then tested. I used this
                              decoder as it seemed to provide the most flexibility for some of my more complex signal types.
                              Note that some of the modes will be similar/identical to other manufacturer's DCC signals

'test_colour_light_signals.py'- developed primarily for testing, but it does provide an example of every signal type and all
                                the control features currently supported

'my_layout'- Still very much work in progress but should give a good example of how a fully interlocked (and relatively
              complex) signalling system can be built using the generic functions provided by the core software functions
              As my layout is still DC (rather than DCC) it also includes layout power switching. At the moment I have no
              plans to include this as a feature in the core "model_railway_signalling" package 


Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)
