Brewberry-&pi; [![Build Status](https://travis-ci.org/amolenaar/brewberry-pi.svg?branch=master)](https://travis-ci.org/amolenaar/brewberry-pi) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/b536d80a821849d8a5d504e18d0bf3ef)](https://www.codacy.com/app/gaphor/brewberry-pi) [![BCH compliance](https://bettercodehub.com/edge/badge/amolenaar/brewberry-pi)](https://bettercodehub.com)
===========

Raspberry Pi based homebrew automation.

Given a DS18B20 temperature sensor, a solid state relays and a wifi connector, automate the mash process. At least, that's the plan.

Resources:
 - http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing
 - http://en.wikipedia.org/wiki/Solid-state\_relay


Starting the application
------------------------

To start the application, from this directory execute:

    python -m brewberry [--fake]

The --fake option can be given to start the fake (non raspberry) io driver.

The web server will be listening on port 9080.

To start the application at boot time, add the following lines to /etc/rc.local:

    echo "Starting Brewberry-PI"
    (cd /home/pi/brewberry-pi && /usr/bin/python -m brewberry; ) &

