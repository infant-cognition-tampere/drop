"""Experiment-class."""

import glib
from Section import Section


class Experiment:
    """
    Experiment class.

    Takes care of the experiment presentation
    (window, ... control) will work one experiment file and control the
    flow of sections. "Experiment"-level stuff.
    """

    def __init__(self, views, ctrl, experiment_data, filename, mediadir,
                 on_experiment_done):
        """Constructor."""
        self.experiment_id = filename
        self.data = experiment_data
        self.ctrl = ctrl
        self.on_experiment_done = on_experiment_done
        self.section_num = -1
        self.section = None

        self.views = views
        self.mediadir = mediadir
        self.section_prepare(0)

    def stop(self):
        """Stop experiment."""
        if self.section is not None:
            self.section.stop()

    def next_phase(self):
        """Jump to next phase."""
        if self.section is not None:
            self.section.next_phase()

    def section_prepare(self, nextsection):
        """Perform pre-section opearations."""
        # end experiment?
        if nextsection >= len(self.data):
            glib.idle_add(self.on_experiment_done)
            return False

        self.section_num = nextsection

        sectioninfo = self.data[self.section_num]

        if "collect_data" in sectioninfo["options"]:
            # check if the user wanted to start data collection on all devices
            # or just one?

            self.ctrl.start_collecting_data(sectioninfo["name"])

        glib.idle_add(self.section_start)

    def section_start(self):
        """Create new section instance and start it."""
        sectioninfo = self.data[self.section_num]

        # generate the object for the next section
        self.section = Section(self.mediadir, sectioninfo.copy(),
                               self.on_section_end, self.ctrl.timestamp)
        self.ctrl.add_model(self.section)

        for view in self.views:
            view.add_model(self.section)

        self.section.run()

    def on_section_end(self):
        """Callback for section_end."""

        for view in self.views:
            view.remove_model(self.section)

        self.section = None
        sectioninfo = self.data[self.section_num]

        if "collect_data" in sectioninfo["options"]:
            glib.idle_add(self.ctrl.stop_collecting_data,
                          self.on_saving_data_completed)
        else:
            glib.idle_add(self.on_saving_data_completed)

    def on_saving_data_completed(self):
        """Callback for saving_data_completed."""
        sectioninfo = self.data[self.section_num]

        # check if next section to begin automatically
        if "autocontinue" in sectioninfo["options"] and \
                self.section_num != len(self.data):
            self.section_prepare(self.section_num+1)
        else:
            self.ctrl.on_section_completed(self.section_num, len(self.data))

    def __del__(self):
        """Destructor for the experiment class."""
        for view in self.views:
            view.stop()
            view.remove_model(self.section)
        self.views = None

        print "Experiment finished."
