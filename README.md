# Project 4: Brevet time calculator with Ajax

A reimplemention of the RUSA ACP controle time calculator with flask and ajax. This program also includes a Dockerfile for easier running on varying hardware.

Credits to Michal Young for the initial version of this code.

## ACP controle times

That's "controle" with an 'e', because it's French, although "control" is also accepted. Controls are points where a rider must obtain proof of passage, and control[e] times are the minimum and maximum times by which the rider must arrive at the location.   

This website uses RUSA open/closing speeds for brevets to report proper timings. The Distance field is filled by a drop down. From that, it determines the opening time by dividing the length by the max speed. The closing time is determined by dividing the length by the minimum speed. The exception is that the final close is predetermined by the length of the brevet and an incredibly early control point having a slightly different closing time so that it closes after the race could have been started.

## AJAX and Flask reimplementation

Every time a distance is put in, this website executes AJAX to only execute necessary sections.

## Testing

There are test cases based on an interpretation of rules here (https://rusa.org/pages/acp-brevet-control-times-calculator).

I have added a few test cases. I am running Python 3.13, so I'm running nosetests instead of nose.