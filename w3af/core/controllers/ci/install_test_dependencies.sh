#!/bin/bash -x

#
# Install all libs required to run our tests (which are available at pypi)
#
pip install pylint mock httpretty psutil logilab-astng SOAPpy PIL SimpleCV==1.3

#
# Install xpresser
#
if [ ! -d xpresser ]; then
    bzr branch lp:xpresser
    cd xpresser/
    python setup.py install
    cd ..
fi

#
# Required the guys from circleci to add gir1.2-notify-0.7 python-pyatspi2 to
# my build for the xpresser tests to work well, also I need to link to the
# system library from my virtualenv:
#
if [ ! -L venv/lib/python2.7/dist-packages/pyatspi ]; then
    ln -s /usr/lib/python2.7/dist-packages/pyatspi/ venv/lib/python2.7/dist-packages/
fi

# Module requirement tree: xpresser => pyatspi => dbus
pip install dbus-python==0.84.0