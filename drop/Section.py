"""Section-class."""

import os
import random
import glib
import utils
from pyee import EventEmitter


class Section(EventEmitter):
    """
    Section class.

    Will handle execution of one section from the experiment file.
    """

    def __init__(self, mediapath, sectioninfo, on_destroy, timestamp):
        """Constructor."""
        # run the superclass constructor
        super(Section, self).__init__()

        self.timestamp = timestamp
        self.stopme = False
        self.mediadir = os.path.join(mediapath, sectioninfo["mediafolder"])
        self.trial = 0
        self.phase_running = False

        # if the aoi-list is list of lists, choose randomly one list and
        # replace "aois" with that list.
        # TODO: make more general later
        if utils.list_depth(sectioninfo["aois"]) > 2:
            aoilist = random.randrange(0, len(sectioninfo["aois"]))
            sectioninfo["aois"] = sectioninfo["aois"][aoilist]
            sectioninfo["aoilist"] = aoilist

        self.sectioninfo = sectioninfo
        self.on_destroy = on_destroy
        self.htimeout_event = None

        print "Starting section " + sectioninfo["name"] + "..."

    def run(self):
        """Method that starts section process."""
        self.initialize_media()
        glib.idle_add(self.trial_start)

    def next_phase(self):
        """Method that jumps to next phase."""
        if self.phase_running:
            glib.idle_add(self.phase_end, priority=glib.PRIORITY_HIGH)

    def initialize_media(self):
        """Load all the necessary files and store handles to containers."""
        sectioninfo = self.sectioninfo

        # TODO: change draweyes to more general
        if "draweyes" in self.sectioninfo["options"]:
            self.emit("draw_diagnostics", True)
        else:
            self.emit("draw_diagnostics", False)

        # load stimuluses
        if "movies" in sectioninfo:
            self.emit("moviefiles_added", self.mediadir, sectioninfo["movies"])

        if "images" in sectioninfo:
            self.emit("imagefiles_added", self.mediadir, sectioninfo["images"])

        if "sounds" in sectioninfo:
            self.emit("soundfiles_added", self.mediadir, sectioninfo["sounds"])

        # apply permutations, if available
        if "permutations" in sectioninfo:
            for perm in sectioninfo["permutations"]:

                # check the length of the first list in the permutation que
                listlen = len(sectioninfo[perm[0]])

                # make a range from 0..listlen
                newordernums = range(0, listlen)

                # shuffle range
                random.shuffle(newordernums)

                # for each order to be permutated in this round
                for order in perm:

                    old_order = sectioninfo[order]
                    new_order = old_order[:]

                    k = 0
                    for j in newordernums:
                        new_order[k] = old_order[j]
                        k = k + 1

                    sectioninfo[order] = new_order

        if "additions" in sectioninfo:
            # after permutations, perform the "list addition operations"
            additions = sectioninfo["additions"]
            for a in additions:
                lists = additions[a].split("+")

                newlist = []
                for l in lists:
                    newlist = newlist + sectioninfo[l.strip()]

                # put concatenated list on top of the other
                sectioninfo[a] = newlist

    def trial_start(self):
        """Start the prepared trial."""
        self.phase = -1
        self.emit("trial_started", self.trial, self.sectioninfo["trialcount"])
        glib.idle_add(self.phase_start, self.trial)
        return False

    def trial_end(self):
        """Callback for trial to be run after execution finished."""
        # construct the informative text to display to user,
        # needs info from orders too
        misc = ""
        extratags = self.sectioninfo["trial"][-1]["extratags"]
        for key in extratags:
            misc = misc + key[0:5] + ":" +\
                   str(self.parse_script_input(extratags[key], self.trial)) +\
                       " "

        self.emit("trial_completed", self.sectioninfo["name"], self.trial,
                  self.sectioninfo["trialcount"], misc)

        self.trial = self.trial + 1

        # check if this is last trial
        if self.trial == self.sectioninfo["trialcount"] or self.stopme:
            # quit section
            self.emit("stimuli_cleared")
            glib.idle_add(self.on_destroy)
        else:
            glib.idle_add(self.trial_start)
            return False

    def phase_start(self, trial):
        """Perform actions when a new phase starts."""
        self.phase += 1
        phaseinfo = self.sectioninfo["trial"][self.phase]
        self.emit("phase_started", self.phase, len(self.sectioninfo["trial"]),
                  phaseinfo["tag"])

        if "gc_aois" in phaseinfo:
            aoinums = phaseinfo["gc_aois"].split("|")

            # get the corresponding aois to list and put it in the tracstatus
            for i in aoinums:
                aoi = self.parse_script_input(i, trial)
                self.emit("data_condition_added", {"type": "aoi",
                                                   "inorout": "in",
                                                   "aoi": aoi})

        if "keyboard_contigency" in phaseinfo:
            keys = phaseinfo["keyboard_contigency"].split("|")
            self.emit("data_condition_added", {"type": "kb", "keys": keys})

        # added here
        self.emit("stimuli_cleared")

        # initialize all the stimuli for this block
        for i in phaseinfo["stimuli"]:

            stimnum = self.parse_script_input(i["id"], trial)

            if i["type"] == "sound":
                self.emit("play_sound", stimnum)

            elif i["type"] == "image":
                aoi = self.parse_script_input(i["aoi"], trial)
                self.emit("play_image", stimnum, aoi)

            elif i["type"] == "movie":
                aoi = self.parse_script_input(i["aoi"], trial)
                self.emit("play_movie", stimnum, aoi)

        # send start tag for the phase
        self.emit("tag", self.create_tag("start", trial))

        if "duration" in phaseinfo:
            phase_duration = phaseinfo["duration"]
            self.htimeout_event = glib.timeout_add(phase_duration,
                                                   self.phase_end,
                                                   priority=glib.PRIORITY_HIGH)
        self.phase_running = True

    def phase_end(self):
        """Callback which is run when phase ends."""
        self.phase_running = False

        # clear the timeout event for phase end
        if self.htimeout_event is not None:
            glib.source_remove(self.htimeout_event)
            self.htimeout_event = None

        self.emit("phase_ended")

        # send end tag for the phase
        self.emit("tag", self.create_tag("end", self.trial))

        if self.phase == len(self.sectioninfo["trial"])-1 or self.stopme:
            # last phase completed

            glib.idle_add(self.trial_end)
            return False

        glib.idle_add(self.phase_start, self.trial, priority=glib.PRIORITY_HIGH)
        return False

    def create_tag(self, secondary_tag, trial):
        """Create a tag-dict with timestamp and state information."""
        timestamp = self.timestamp()
        phaseinfo = self.sectioninfo["trial"][self.phase]

        tag = {}
        tag["id"] = str(phaseinfo["tag"])
        tag["timestamp"] = timestamp
        tag["secondary_id"] = str(secondary_tag)
        tag["trialnumber"] = str(trial)

        # Add extra tags
        for t in phaseinfo["extratags"]:
            tag[str(t)] = str(self.parse_script_input(phaseinfo["extratags"][t], trial))

        return tag

    def parse_script_input(self, ind, trial):

        return utils.recursive_indexing(ind.split("->"),
                                 self.sectioninfo, trial)

    def stop(self):
        """Method that stops the section execution."""
        self.stopme = True
        glib.idle_add(self.phase_end)

    def __del__(self):
        """Destructor."""
        # clear any references
        self.remove_all_listeners()
        self.on_destroy = None

        print "Section finished."
