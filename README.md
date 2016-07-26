# drop
drop - data recording open-source platform

### What is drop?

drop is an open-source platform for projects that aim to a present a task on computer screen and collect time-locked data from sensors during the task. drop was born from the need to collect data from multiple sensors synchronously during psychology research and to share experiments between testing sites and colleagues. drop is designed to be open source and modular platform to easily add new modules such as recording devices. It has been programmed on python.

### Why drop?
* Open source, programmed in python
* JSON-scripting schema to present stimuli on a screen (movies, images, sounds)
* Modular interface that allows user to attach sensors that are being synchronized and record their own data streams receiving tags from the presentation module
* Interface that allows user to monitor the recording devices during the task

### Platforms
Drop is developed in python and currently works at least on following platforms (compatibility may vary with different os-versions):
* Linux (primary platform, tested on Linux Mint 17)
* Os X El capitan

### License
drop uses MIT licence.

### Reference
The project was started by researchers from Infant Cognition Lab, University of Tampere, Finland. Please cite us if you publish using drop.

Home page [ICL Tampere](http://uta.fi/med/icl)

## Usage

### Terms
* Experiment file = a JSON-file that formally describes the structure of an experiment. See later for more info of the file format.
* Section = part of the experiment that repeats the similar sequence of stimuli with specified variation. Experiment is a series of sections.
* Trial = one round of presented stimuli. Section consists of trials.
* AOI = Area Of Interest, a square-shape area that is defined by coordinates x1,y1,x2,y2.
* Sensor = a sensor element that can be used to record data during experiment on drop. Each sensor needs a plug-in that matches with drop sensor-API.

### Basics
If drop has been installed using pip it can be started by typing `drop` on terminal. A window with program controls should appear. Window acts as a control interface during experiment. On the left the user must select an experiment, connect necessary sensors and input user-id. On the top-right the user is presented with a black window which displays information from the experiment and possibly from the sensors during experiment-session.

#### Controls


### Experiment file structure
Experiment files presented by drop are stored under the work folder tasks/. Experiments are automatically discovered by drop and presented on the user interface. Experiments need to follow JSON-syntax and have a suffix .json in order to work.
An experiment is created by defining list of “sections”. A section is an instance, which is created by defining a python-dictionary with certain keywords an values. Sections are run on the order of appearance.

The possible keywords are:

* name: identifier of the node [required]
* mediafolder: string representing media folder [required]
* trialcount: integer [required]
* options: list of strings [required]
* trial: defined later [required]
* images: list of strings, needed if images are presented on the node
* orders: dict of items, integers, strings etc. that are indexed by the round number
* aois: list of lists of four elements [x1, x2, y1, y2]
* permutations: list of lists of order keys that are permuted with the same permutation


#### Example experiment
```
[
    {
        "name": "calibration",
        "mediafolder": "my_media",
        "images": ["wallpaper.png", "cat.png"],
        "orders": {"nudgedp":[[0.1,0.1], [0.9,0.1], [0.5,0.5], [0.1,0.9], [0.9,0.9]]},
        "trialcount": 10,
        "aois" : [
            [0.0, 1.0, 0.0, 1.0],
            [0.85, 0.95,0.85, 0.95]
        ],
        "options": ["collect_data"],
        "trial": [
            {
                "duration":2000,
                "tag":"wait",
                "extratags":{
                    "stim": 0,
                    "aoi" : 0,
                },
                "stimuli":[
                    {"type":"image", "id":0, "aoi":0}
                ]
            },
            {
                "gc_aois":1,
                "tag":"cat",
                "extratags":{
                    "stim": 0,
                    "aoi" : 1
                "stimuli":[
                    {"type":"image", "id":0, "aoi":0}, {"type":"image", "id":1, "aoi":1}
            }
        ]
    }
]
```

### Development
