"""Sensor-class."""

from pyee import EventEmitter
import random


class Sensor(EventEmitter):
    """
    Master class to inherit sensor classes.

    Python also allows to use objects of different classes in list
    so inheritance is not mandatory.
    Sensor objects must close all references to them so that they are removed
    by garbage collector on disconnect(). Be sure to close all (glib, etc.)
    loops too.
    """

    def __init__(self):
        """Constructor."""
        # run the superclass constructor
        EventEmitter.__init__(self)
        self.type = None
        self.control_elements = []
        self.data_conditions = []

        # sensor_id should be unique
        rndnum = random.randint(0, 100000)
        self.sensor_id = "sensor" + str(rndnum)

    def trial_started(self, tn, tc):
        """
        Function is called when the trial is started.

        Parameters:
        tn: trial number (int)
        tc: trial count (int)
        """
        return False

    def trial_completed(self, name, tn, tc, misc):
        """Method that is called when trial is completed."""
        return False

    def tag(self, tag):
        """Method that is called when a new tag arrives."""
        print "FUNCTION NOT IMPLEMENTED"

    def action(self, action_id):
        """Perform actions for the control elements defined."""
        return False

    def get_type(self):
        """Return sensor type."""
        return self.type

    def set_data_condition(self, condition):
        """Insert new data condition."""
        self.data_conditions.append(condition)

    def clear_data_conditions(self):
        """Clear existing data conditions."""
        self.data_conditions = []

    def get_sensor_id(self):
        """Return sensor-id-string."""
        return self.sensor_id

    def get_control_elements(self):
        """Return the list of sensors control-elements."""
        return self.control_elements

    def stop_recording(self):
        """Method that stops the sensor recording."""
        print "FUNCTION NOT IMPLEMENTED"

    def start_recording(self, rootdir, participant_id, experiment_file,
                        section_id):
        """Method that starts sensor recording."""
        print "FUNCTION NOT IMPLEMENTED"

    def disconnect(self):
        """Method that is called when sensor is disconnected."""
        self.emit("clear_screen")
        self.remove_all_listeners()
        return False

    def __del__(self):
        """Destructor."""
        print self.sensor_id + " disconnected."
        return False
