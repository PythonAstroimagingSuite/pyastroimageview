Introduction
============



What is Runastroseq Suite (RASS)?
---------------------------------

Runastroseq Suite (RASS) is a group of Python tools written to support automated
data collection using astronomical CCD/CMOS cameras on modern GOTO enabled mounts.
Some of the features of RASS are:

    - Support for automated collection including scheduling observations of objects
    - Support for a local horizon when scheduling objects
    - Precise positioning of a GOTO mount using plate solving
    - Autofocus with automatic focus star acquisition
    - Automated meridian flips
    - Restart incomplete observations to acquire needed data to complete
    - Web browser monitoring of session progress
    - Control hardware with either ASCOM (Windows) or INDI (Linux/Mac?)

Components
----------

RASS is composed of the following components:

- runastroseq
    + runastroseq_main.py:
        Core server which controls hardware and manages observations
    + automate_nightrun_project.py
        Acts as client to runastroseq_main.py and handles scheduling
        observations from a project definition and running them through runastroseq_main.py
- pyastrobackend
    Abstraction layer for hardware access for ASCOM/INDI/MaximDL (camera only)
- pyastrometry
    Local and online plate solving support including precision slews
- pyastroprofile
    Data structures for persistent storage of settings for equipment and programs
- phd2control
    Python module for interacting with PHD2
- pyastroviewer
    UI for displaying FITS images and star analysis of images
- hfdfocus
    HFD based autofocus including automatic selection and slewing to nearby stars for focusing

All components are written with Python 3.7 and depends on these  Python modules (as well as others):

    - numpy
    - scipy
    - astropy
    - astroplan
    - json
    - yaml

runastroseq
~~~~~~~~~~~

runastroseq_main.py (RASM)
^^^^^^^^^^^^^^^^^^^^^^^^^^

RASM connects to all the imaging hardware as well as PHD2 and then listens for "JSON-RPC"-like requests on a TCP socket.
Usually clients send a sequence request which RASM then manages.  Among the responsibilities of RASM are:

- Check the camera cooler is set and at the correct temperature
- Point the telescope at the desired object (optionally using plate solving)
- Autofocus the telescope
- Instruct PHD2 to find a guide star and start guiding
- Acquire the desired number of images using the specified parameters (exposure, filter, etc)
- Manage meridian flips and stopping the mount when idle
- Monitor constrains for the sequence like start and stop time or altitudes

RASM also has a built in webserver which allows using a browser to monitor the internal
state as well as the progress of a sequence.  Otherwise RASM is completely a command line (CLI)
program with no GUI component.

automate_nightrun_project.py (ANP)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ANP is responsible for taking a project definition and connecting to RASM and determine a schedule for
the requested observations and converting them to sequences which it sends to RASM.  The scheduling is
based on trying to get more Western targets images first but allows for priorities to be specified to
guarantee some observations occur at the expense of lower priority but further West observations.  It is
also possible to specify a start time or altitude as well as a stop time or altitude.  Observations with
these constraints will be given preference over other observations of the same or lower priority with such
constraints.

A web browser can be used to monitor the progress of ANP via its build in web server.

A simulation mode is available which tries to incorporate how long different operations like autofocus, dithering
and slewing to the target will take in order to determine the order in which observations will occur.  This
allows checking out a project before nightfall and checking that the desired results will be achieved.

pyastrobackend
^^^^^^^^^^^^^^

Pyastrobackend is a abstraction later which presents a singular API to Python
applications allowing the use of ASCOM, MaximDL or INDI device driver frameworks underneath.
The goal is allow one to have a single source tree for an astronomical application
and be able to run it on a system using ASCOM, MaximDL or INDI.

How does it work?
+++++++++++++++++

An application first determines which "backend" (ASCOM or INDI) is required for
the given system using the :func:`get_backend_for_os` function.

Then the application imports the appropriate backend and device control modules
for the system.

Once the backend and devices are connected then all api calls are uniform between
the ASCOM and INDI implementations.  This allows a single code base to work on both.

See the pyastrobackend documentation for more details.

pyastrometry
^^^^^^^^^^^^

Pyastrometry supports plate solving FITS images using local plate solvers or an online plate solver.

The supported plate solve engines are:

- PlateSolver2 (Windows)
- astrometry.net local (Linux)
- astrometry.net online blind solver (Windows/Linux)

The primary interface is using the "pyastrometry_cli_main.py" Python script which supports:

- slews with or without plate solving
- solve and optionally syncing position using a local or online plate solve engine

RASM uses "pyastrometry_cli_main.py" for all its operations involving slews and determining the
position of the telescope.

pyastroprofile
^^^^^^^^^^^^^^

Pyastroprofile consists of YAML configuration files which store configuration
data persistently for RASS.  The following are the types of configuration
data which are stored:

- EquipmentProfile
    Information about the drivers to use for hardware as well as auxiliary information
    such as the size and focal length of the telescope.
- SettingsProfile
    Program settings which control autofocus, plate solving and guiding operations.
    Examples of settings would be the size of dither used or the V-Curve slope details for autofocus.
- ObservatoryProfile
    Information about the observing location and horizon.
- AstroProfile
    This is a special configuration file which specifies the equipment, settings,
    and observatory profile for a particular imaging configuration.  Most the
    RASS components expect an astroprofile to be specified.

The configuration files are stored in a configuration directory CONFIG_DIR which
depends on the host OS:

- Linux: $HOME/.config/astroprofiles
- Windows: %APPDATA%/astroprofiles

Underneath CONFIG_DIR the hierarchy is:

- equipment
- observatories
- settings

Here is an example configuration:

- CONFIG_DIR/equipment/SCT_imaging_rig.yaml
    EquipmentProfile for setup
- CONFIG_DIR/observatories/my_obs.yaml
    ObservatoryProfile for observing location
- CONFIG_DIR/settings/SCT_imaging_rig.yaml
    Program settings for setup
- CONFIG_DIR/SCT_imaging_rig.yaml
    Astroprofile specification for this setup which contains:
    equipment: SCT_imaging_rig.yaml
    observatory: my_obs.yaml
    settings: SCT_imaging_rig.yaml

When running RASM or ANP one specifies the command line option "--profile SCT_imaging_rig"
and all the relevant configuration data will be loaded.

phd2control
^^^^^^^^^^^

Phd2control acts as a client to PHD2 and allows using its JSON-RPC interface to control
PHD2 and handles notification from PHD2 as well.  The main use is it allows controlling guiding, dithering and
guide star selection while also determining when a star is lost due to clouds or
other environmental factors.

pyastroviewer
^^^^^^^^^^^^^

Pyastroviewer is a Python/Qt application which connects to RASM and received notifications when
a new image is available.  The image is loaded into a FITS viewer which supports stretching the
image as well as star analysis which shows star sizes across the frame.  The primary
goal is to allow monitoring of image data as it is collected.

hfdfocus
^^^^^^^^

Hfdfocus is responsible for autofocus for RASS.  It uses the technique described by Larry Weber and Steve Brady
to use the slope of the V-Curve to determine best focus.  It requires first collecting many V-Curves which
are analyzed to determine the slope and intercepts of both sides of the V-Curve.  Then
using measurements of an actual star and noting the size versus focuser position
one can determine the position of best focus.

Utilities are included to collect and analyze V-Curves to determine the required
parameters.  These tools are run from the command line and should only need to
be run once for a given imaging setup.

The autofocus routine supports finding a nearby star of sufficient brightness
for the autofocus routine to run and then slewing to the selected star and then
back to the original position.  By using a nearby bright star it is possible to
get adequate signal to noise for the focus star with short exposures which
speeds up the focusing process, especially when using narrow band filters.

