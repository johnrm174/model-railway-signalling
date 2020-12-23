# model-railway-signalling
A model railway signalling system written in Python for the rasberry Pi

This has been created to provide a representation of my layout, complete with points, signals and the switchable "power sections" 
(yep - its all still analogue at the moment, no DCC here yet). I have also provided "track occupancy sections" and a means of 
triggering "signal passed" events to support future automation. At the moment, the code is self contained - relying solely on
'tkinter' for the user interface. Interfacing out to the layout itself is on the TODO list.

Although most of the code is specific to my particular layout, I have tried to write the underlying modules and functions 
('signals', 'points' 'switches' - and their 'common' functions) to promote re-use in other layouts. Currently most types of
colour light signals (and position light signals) are supported. Semaphores are still on my TODO list

Comments and suggestions welcome - but please be kind - the last time I coded anything it was in Ada96 ;)
