BrewGear-&pi;
===========

Raspberry Pi based home brewing automation kit.

Given a DS18B20 temperature sensor, a bunch of solid state relays and a wifi connector, automate the mashing process. At least, that's the plan.

Resources:
 - http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing
 - http://en.wikipedia.org/wiki/Solid-state_relay


Starting the application
------------------------

To start the application, from this directory execute:

    python -m brewgearpi [--fake]

The --fake option can be given to start the fake (non raspberry) io driver.

