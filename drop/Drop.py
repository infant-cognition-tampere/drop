"""DropController-class."""

import os
import time
import glib
import utils
from pyee import EventEmitter
from DropPygtkView import DPV
from Experiment import Experiment
from yapsy.PluginManager import PluginManager


class DropController(EventEmitter):
    """Main controller of the class. Views+ui separated to different files."""

    def __init__(self):
        """Constructor."""
        # run the superclass constructor
        EventEmitter.__init__(self)

        # Model initialization code
        self.participant_id = ""
        self.experiment_file = None
        self.sensors = []
        self.experiment = None

        # define important directories for external (not program code) files
        homedir = os.environ['HOME']
        drop_home = os.path.join(homedir, "Documents", "drop_data")
        self.savedir = os.path.join(drop_home, "recordings")
        self.experimentdir = os.path.join(drop_home, 'experiments')
        self.mediadir = os.path.join(drop_home, 'media')
        self.plugindir = os.path.join(drop_home, 'plugins')

        # check that saving, experiment etc directories are present
        utils.dircheck(self.savedir)
        utils.dircheck(self.experimentdir)
        utils.dircheck(self.mediadir)

        # temporary? keyboard-contigency list
        self.keyboard_contigency = []

        # initialize plugin manager
        self.pluginmanager = PluginManager()
        self.pluginmanager.setPluginPlaces([self.plugindir])
        self.pluginmanager.collectPlugins()

        # initialize pygtk-view
        self.ec = DPV(self, self.mediadir, self.experimentdir)
        self.ec.main()

    def addsensor(self):
        """Callback for addeeg-button."""
        # TODO: missing feature
        pass

    def get_sensors(self):
        """Return list of sensors."""
        return self.sensors

    def on_recorder_error(self, msg):
        """Sensor error-handler."""
        self.emit("error", msg)

    def on_recorder_created(self, rhandle):
        """Callback for sensor initialization."""
        self.sensors.append(rhandle)
        self.ec.add_recorder(rhandle)
        self.emit("sensorcount_changed")

        # add model to hear calls from recorders, such as data_condition met
        self.add_model(rhandle)

    def recorder_action(self, sensor_id, action_id):
        """Perform action that is listed on sensors control elements."""
        for sensor in self.sensors:
            if sensor.get_sensor_id() == sensor_id:
                sensor.action(action_id)

    def remove_sensor(self, sensor_id):
        """Disconnect the sensor with the provided sensor_id."""
        for sensor in self.sensors:
            if sensor.get_sensor_id() == sensor_id:
                sensor.disconnect()
                self.sensors.remove(sensor)
        self.emit("sensorcount_changed")

    def set_participant_id(self, pid):
        """Method for setting participant_id."""
        self.participant_id = pid

    def get_participant_id(self):
        """Return participant_id."""
        return self.participant_id

    def set_experiment_file(self, filename):
        """Method for setting experiment-file."""
        self.experiment_file = filename

    def get_experiment_file(self):
        """Return experiment file."""
        return self.experiment_file

    def play(self, debug):
        """Start the experiment."""
        if self.experiment is None and self.experiment_file is not None:
            self.experiment_start(debug)

    def get_experiment_information(self):
        """Display info of the selected experiment."""
        if self.experiment_file is None:
            return None

        # load experiment data from JSON-dictlist
        return utils.load_JSON(os.path.join(self.experimentdir,
                               self.experiment_file))

    def start_section(self, section_number):
        """Start section with parameter section_number[int]."""
        if self.experiment is not None:
            self.experiment.section_prepare(section_number)

    def continue_experiment(self):
        """Callback for continuebutton click."""
        for sensor in self.sensors:
            sensor.clear_data_conditions()

        # self.emit("continue")
        if self.experiment is not None:
            self.experiment.next_phase()

    def stop(self):
        """Callback for stopbutton click."""
        if self.experiment is not None:
            self.experiment.stop()

    def add_model(self, model):
        """Add a model to listen for."""
        model.on("tag", self.on_tag)
        model.on("data_condition_added", self.on_data_condition_added)
        model.on("data_condition_met", self.continue_experiment)
        model.on("trial_completed", self.on_trial_completed)
        model.on("trial_started", self.on_trial_started)

    def on_trial_started(self, tn, tc):
        """Callback for trial_started signal."""
        for r in self.sensors:
            r.trial_started(tn, tc)

    def on_trial_completed(self, name, tn, tc, misc):
        """Callback for trial_completed signal."""
        self.emit("trial_completed", name, tn, misc)

        for r in self.sensors:
            r.trial_completed(name, tn, tc, misc)

    def timestamp(self):
        """Return a local timestamp in microsecond accuracy."""
        return time.time()

    def on_tag(self, tag):
        """
        Send a tag to all sensors.

        Tag might not come instantly here so the
        timestamp is taken in advance. The sensor must sync itself with the
        computer. Tag consists of:
        id = string, identifier of the tag
        timestamp = timestamp in ms of the localtime clock
        secondary_id = string, defines "start", "end", or "impulse", as a start
        of perioid, end of it or single impulse
        misc = other possible information (depends on the sensor how to use)
        """
        for sensor in self.sensors:
            # send a copy of the dict to each sensor
            sensor.tag(tag.copy())

    def on_keypress(self, keyname):
        """Callback for keypress."""
        if keyname in self.keyboard_contigency:
            self.keyboard_contigency = []
            self.emit("continue")
            tag = {"id": keyname, "secondary_id": "keypress",
                   "timestamp": self.timestamp()}
            self.on_tag("tag", tag)

    def experiment_start(self, debug):
        """Method to start experiment."""
        # load experiment data from JSON-dictlist
        experiment_data = self.get_experiment_information()

        # initialize the experiment object
        from ExperimentPsychopyView import ExperimentPsychopyView
        self.exp_view = ExperimentPsychopyView(debug)
        self.experiment = Experiment([self.exp_view, self.ec.trackstatus],
                                     self, experiment_data,
                                     self.experiment_file, self.mediadir,
                                     self.on_experiment_completed)

        for r in self.sensors:
            self.exp_view.add_model(r)

        self.emit("experiment_started")

    def on_experiment_completed(self):
        """Callback for experiment finished."""
        # clear view references
        for r in self.sensors:
            self.exp_view.remove_model(r)
        self.exp_view = None

        # clear experiment object pointer
        self.experiment = None

    def on_section_completed(self, prevsection, len_sections):
        """Callback for section completion if no autocontinue enabled."""
        self.emit("section_completed", prevsection, len_sections)

    def on_data_condition_added(self, data_condition):
        """Callback for data_condition_added. Singal datacond. to sensors."""
        if data_condition["type"] == "kb":
            self.keyboard_contigency += data_condition["keys"]

        for sensor in self.sensors:
            sensor.set_data_condition(data_condition)

    def start_collecting_data(self, section_id):
        """Function starts data collection on all sensors."""
        for sensor in self.sensors:
            sensor.start_recording(self.savedir, self.participant_id,
                                   self.experiment_file, section_id)

    def stop_collecting_data(self, callback):
        """Stop data collection on all sensors and run callback."""
        for sensor in self.sensors:
            sensor.stop_recording()
        glib.idle_add(callback)

    def close(self):
        """Method that closes the drop controller."""
        # disconnect all the sensors from the host
        for sensor in self.sensors:
            sensor.stop_recording()
            sensor.disconnect()

        self.remove_all_listeners()

    def __del__(self):
        """Destructor."""
        print "Exitting Drop."
