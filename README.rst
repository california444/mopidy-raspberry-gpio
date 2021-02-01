****************************
Mopidy-Raspberry-GPIO
****************************

Copy of original Mopidy-Raspberry-GPIO project with the following changes:

- added sounds, for Play/Pause, Next, preview, VolumeUp & VolumeDown
- dirty changed GPIO set mode from BCM to BOARD as other plugins already set up BOARD
- better debounce GPIO events, allow only one action per second for the same pin
