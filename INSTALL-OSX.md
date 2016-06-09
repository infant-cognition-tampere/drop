DROP Installation instructions for OS X
=======================================

At the time of writing these are mostly useful for developers but providing
instructions anyway.

El Capitan (the latest at the moment of writing) is the "officially" supported
OS X version. Older versions have not been tested by developers, but might
still work.

- Install Xcode from App Store
- Install Xcode Command Line Tools:
xcode-select --install
- Install XQuartz
https://www.xquartz.org/
- Install MacPorts
- From MacPorts, install packages:
`sudo port install py27-pygtk py27-numpy py27-pip py27-scipy liblo py27-pyglet py27-game`

`sudo port select --set python python2`

`sudo port select --set pip pip27`
- Install newer PsychoPy version than currently in PyPi:
`pip install https://github.com/psychopy/psychopy/releases/download/1.83.04/PsychoPy-1.83.04.zip`

- When you have installed MacPorts packages, you can install Drop with
`pip install .` on the repository directory.


For The Eye Tribe tracker, you need to get SDK from The Eye Tribe site:
https://theeyetribe.com/download/

Install and then run The Eye Tribe server on the background.

You also need separate Eye Tribe plugin for DROP (not implemented yet).
