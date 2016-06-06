''' Section-class. '''

import os
import random
import glib
from pyee import EventEmitter


class Section(EventEmitter):
    '''
    Section class will handle execution of one section from the experiment
    file.
    '''

    def __init__(self, mediapath, sectioninfo, on_destroy, timestamp):

        # run the superclass constructor
        super(Section, self).__init__()

        self.timestamp = timestamp
        self.stopme = False
        self.mediadir = os.path.join(mediapath, sectioninfo["mediafolder"])
        self.trial = 0
        self.phase_running = False

        self.sectioninfo = sectioninfo
        self.on_destroy = on_destroy
        self.htimeout_event = None

        print "Starting section " + sectioninfo["name"] + "..."

    def run(self):
        self.initialize_media()
        glib.idle_add(self.trial_start)

    def next_phase(self):
        if self.phase_running:
            glib.idle_add(self.phase_end, priority=glib.PRIORITY_HIGH)

    def initialize_media(self):
        '''
        Loads all the necessary files and stores their handles to containers.
        '''

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
                listlen = len(sectioninfo["orders"][perm[0]])

                # make a range from 0..listlen
                newordernums = range(0, listlen)

                # shuffle range
                random.shuffle(newordernums)

                # for each order to be permutated in this round
                for order in perm:

                    old_order = sectioninfo["orders"][order]
                    new_order = old_order[:]

                    k = 0
                    for j in newordernums:
                        new_order[k] = old_order[j]
                        k = k + 1

                    sectioninfo["orders"][order] = new_order

        if "orders" in sectioninfo:
            # after permutations, perform the "list addition operations"
            orders = sectioninfo["orders"]
            for o in orders:
                if not isinstance(orders[o], list):
                    # order is not a list -> order is assumed to be
                    # concatenation of lists

                    lists = orders[o].split("+")

                    newlist = []
                    for l in lists:
                        newlist = newlist + orders[l.strip()]

                    # put concatenated list on top of the other
                    orders[o] = newlist

    def trial_start(self):
        ''' Start next trial.  trial 0..len(trials)-1 '''

        self.phase = -1
        self.emit("trial_started", self.trial, self.sectioninfo["trialcount"])
        glib.idle_add(self.phase_start)
        return False

    def trial_end(self):

        # construct the informative text to display to user,
        # needs info from orders too
        misc = ""
        for key in self.sectioninfo["trial"][-1]["extratags"]:
            misc = misc + key[0:5] + ":" + str(
                self.get_order_num(
                    self.sectioninfo["trial"][-1]["extratags"][key])) + " "

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

    def phase_start(self):
        ''' perform actions when a new phase starts '''

        self.phase += 1
        phaseinfo = self.sectioninfo["trial"][self.phase]
        self.emit("phase_started", self.phase, len(self.sectioninfo["trial"]),
                  phaseinfo["tag"])

        if "gc_aois" in phaseinfo:
            aoinums = phaseinfo["gc_aois"].split("|")

            # get the corresponding aois to list and put it in the tracstatus
            for i in aoinums:
                aoi = self.sectioninfo["aois"][self.get_order_num(i)]
                # self.emit("gc_aoi_added", i, aoi)
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

            stimnum = self.get_order_num(i["id"])

            if i["type"] == "sound":
                self.emit("play_sound", stimnum)

            elif i["type"] == "image":
                aoinum = self.get_order_num(i["aoi"])
                aoi = self.sectioninfo["aois"][aoinum]
                self.emit("play_image", stimnum, aoi)

            elif i["type"] == "movie":
                aoinum = self.get_order_num(i["aoi"])
                aoi = self.sectioninfo["aois"][aoinum]

                self.emit("play_movie", stimnum, aoi)

        # send start tag for the phase
        self.emit("tag", self.create_tag("start"))

        if "duration" in phaseinfo:
            phase_duration = phaseinfo["duration"]
            self.htimeout_event = glib.timeout_add(phase_duration,
                                                   self.phase_end,
                                                   priority=glib.PRIORITY_HIGH)
        self.phase_running = True

    def phase_end(self):
        ''' Actions when phase ends. '''

        self.phase_running = False

        # clear the timeout event for phase end
        if self.htimeout_event is not None:
            glib.source_remove(self.htimeout_event)
            self.htimeout_event = None

        self.emit("phase_ended")

        # send end tag for the phase
        self.emit("tag", self.create_tag("end"))

        if self.phase == len(self.sectioninfo["trial"])-1 or self.stopme:
            # last phase completed

            glib.idle_add(self.trial_end)
            return False

        glib.idle_add(self.phase_start, priority=glib.PRIORITY_HIGH)
        return False

    def create_tag(self, secondary_tag):
        '''
        Function which defines actions to take when creating a tag.
        Returns tag-dict.
        '''

        timestamp = self.timestamp()
        phaseinfo = self.sectioninfo["trial"][self.phase]

        tag = {}
        tag["id"] = str(phaseinfo["tag"])
        tag["timestamp"] = timestamp
        tag["secondary_id"] = str(secondary_tag)
        tag["trialnumber"] = str(self.trial)

        # Add extra tags
        for t in phaseinfo["extratags"]:
            tag[str(t)] = str(self.get_order_num(phaseinfo["extratags"][t]))

        return tag

    def get_order_num(self, testvalue):
        ''' Returns integer: if testvalue was integer -> returns testvalue
        if testvalue was string -> returns an integer that is recovered
        from orders with key testvalue and current trial as an index.
        '''

        value = str(testvalue)
        if value == "none" or value == "None":
            return None
        elif value.isdigit():
            # value was defined with a digit
            return int(value)
        else:
            # value was defined with a string pointing to orders
            return self.sectioninfo["orders"][value][self.trial]

    def stop(self):
        self.stopme = True
        glib.idle_add(self.phase_end)

    def __del__(self):

        # clear any references
        self.remove_all_listeners()
        self.on_destroy = None

        print "Section finished."
