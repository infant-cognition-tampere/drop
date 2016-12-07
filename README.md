# drop
drop - data recording open-source platform

### What is drop?

drop is an open-source platform for projects that aim to a present a task on
computer screen and collect time-locked data from sensors during the task.
drop was born from the need to collect data from multiple sensors synchronously
during psychology research and to share experiments between testing sites and
colleagues. drop is designed to be open source and modular platform to easily
add new modules such as recording devices. It has been programmed on python.

### Why drop?
* Open source, programmed in python and expandable by anyone with programming
skills
* JSON-scripting schema to present stimuli on a screen (movies, images, sounds)
* Modular interface that allows user to attach sensors that are being
synchronized and record their own data streams receiving tags from the
presentation module
* Interface that allows user to monitor the recording devices during the task

### Platforms
Drop is developed in python, so technically it should work on any platform which supports python and the required libraries. Currently drop works at least on following platforms
(compatibility may vary with different os-versions):

* Linux (primary platform, tested on Linux Mint 17)
* Os X El capitan

### License
drop uses MIT licence.

### Reference
The project was started by researchers from Infant Cognition Lab, University of
Tampere, Finland. Please cite us if you publish using drop.

Home page [ICL Tampere](http://uta.fi/med/icl)

## Usage

### Terminology
* Experiment file = a JSON-file that formally describes the structure of an
experiment. See later for more info of the file format.
* Section = part of the experiment that repeats the similar sequence of stimuli
with specified variation. Experiment is a series of sections.
* Trial = one round of presented stimuli. Section consists of trials.
* Phase = one set of stimuli played fixed or dynamic time (data condition).
Trial consists of phases.
* AOI = Area Of Interest, a square-shape area that is defined by coordinates
x1,y1,x2,y2.
* Sensor = a sensor element that can be used to record data during experiment
on drop. Each sensor needs a plug-in that matches with drop sensor-API.
* Data condition = A condition in the experiment when phase does
* Working directory = A directory that contains the experiments, media folders
and possible recordings by sensors. The working directory at the moment is
~/Documents/drop_data which contains folders experiments, media and recordings.
The working directory is the source for experiments and media displayed by
drop.

### Basics
If drop has been installed using pip it can be started by typing `drop` on
terminal. A window with program controls should appear. Window acts as a
control interface during experiment. On the left the user must select an
experiment, connect necessary sensors and input user-id. On the top-right the
user is presented with a black window which displays information from the
experiment and possibly from the sensors during experiment-session. Drop is
configured to work in a computer with primary and secondary (non-mirroring)
displays where the experiment is shown on the secondary display and the
leader of the experiment controls the flow of the experiment in the primary
display. Insert your experiments and media on the working directory
(see above).

#### Controls
* Play: starts the selected experiment if all start conditions are met.
* Stop: ends the current section (might proceed to next section or prompt a 
cross-section dialog).
* Continue: forcefully continues to the next phase on the experiment if the
experiment is halted by a data condition or by fixed duration break.
* (Debug/windowed): when enabled, the experiment will be shown in a window
instead of full screen on the secondary display.
* Experiment info: displays a brief overview of the experiment structure and
checks that the JSON-syntax is correct (does not check logical errors or
missing items etc.). Also checks if the files are present on the working
directory. Files that are missing are labeled on red.
* Participant id: A field for the participant identification code - needs to
be filled for the experiment to run.
* Log: the log collects messages sent from the experiment instance and inserts
a new line each time a new trial is completed displaying little information
of the trials variables etc.

### Experiment file structure
Experiment files presented by drop are stored under the work folder tasks/.
Experiments are automatically discovered by drop and presented on the user
interface. Experiments need to follow JSON-syntax and have a suffix .json in
order to work.
An experiment is created by defining list of “sections”. A section is an
instance, which is created by defining a python-dictionary with certain
keywords an values. Sections are run on the order of appearance.

The possible keywords on the section-level are:

* name: identifier of the node [required]
* mediafolder: string representing media folder [required]
* trialcount: integer [required]
* options: list of strings [required]
* trial: defined later [required]
* images: list of strings, needed if images are presented on the node
* orders: dict of items, integers, strings etc. that are indexed by the round
number
* aois: list of lists of four elements [x1, x2, y1, y2]
* permutations: list of lists of order keys that are permuted with the same
permutation

Trial consists of phases which last for a fixed time or until a data condition
is met. "trial" is a list of JSON-dicts that contain keywords. The possible
keywords for phase-level are:

* duration: length of the phase in milliseconds [required]
* tag: phase identifier [required]
* extratags: additional tags for this phase
* stimuli: a list of dicts of stimuli to be played, defined later
[required]

The possible keywords for stimuli-level are:

* type:"image", "movie" or "sound" [required]
* id: number or string of the order - corresponds the stimulus position in
the stimulus list of type [required]
* aoi: number or string of order representing aoi list position
[required if image or movie]
* move: similar to aoi, but where the image is moved during the phase
* pulsate: pulsation factor: image oscillates at rate 1/pulsate between aoi
and move(aoi)
* rotate: rotation speed 1/rotation flips on second, negative for other
direction


#### Example experiment
A simple example of an experiment that displays a sequence of wallpaper and
wallpaper + image "cat.png" for 10 times. The image is first displayed 5 times
on the right edge of the screen and 5 times on the left edge of the screen.
The example experiment should work if it's inserted on the experiment directory
and the working-directory's media folder includes a folder "my_media" which
includes files "wallpaper.png" and "cat.png". If a supported eyetracker is used
the cat disappears when the gaze arrives at the correct aoi. Otherwise the
cat stays for 5 seconds (or as long as the leader presses "continue").

```
[
    {
        "name": "example_section",
        "mediafolder": "my_media",
        "images": ["wallpaper.png", "cat.png"],
        "orders": {"aoi_order":[1,1,1,1,1,2,2,2,2,2]},
        "trialcount": 10,
        "aois" : [
            [0.0, 1.0, 0.0, 1.0],
            [0.85, 0.95,0.45, 0.55],
            [0.05, 0.15,0.45, 0.55]
        ],
        "options": ["collect_data"],
        "trial": [
            {
                "duration":2000,
                "tag":"wait_phase",
                "extratags":{
                    "stim": 0,
                    "aoi" : 0
                },
                "stimuli":[
                    {"type":"image", "id":0, "aoi":0}
                ]
            },
            {
                "duration":5000,
                "gc_aois":"aoi_order",
                "tag":"cat_phase",
                "extratags":{
                    "stim": 1,
                    "aoi" : "aoi_order"
                },
                "stimuli":[
                    {"type":"image", "id":0, "aoi":0}, {"type":"image", "id":1, "aoi":"aoi_order"}
                ]
            }
        ]
    }
]
```

### Development
Program code is documented with docstrings on functions. Sensor API is most
easily understood by examining the sensor superclass from which the
sensor-plugins inherit. Some features are not completed and may miss
functionality or disfunction.
