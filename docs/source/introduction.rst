Introduction
============

What is Pyastroimageview?
---------------------------------

Pyastroimageview is an image acquisition program that allows taking images with
a supported astronomy hardware (via ASCOM or INDI) including:

    - cameras
    - mounts
    - focusers
    - filter wheels

Pyastroimageview can take an image sequence and in addition pyastroimageview
will control PHD2 to cause dither events while taking an image sequence.

Pyastroimageview also has an JSON-RPC-like API that allows it to act as a hub
for hardware like cameras which do not always support multiple clients.
