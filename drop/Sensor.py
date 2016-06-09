'''
Sensor-class.

Master class to inherit sensor classes. Python also allows to use objects
of different classes in list so inheritance is not mandatory.

Device objects must close all references to them so that they are removed by
garbage collector on disconnect(). Be sure to close all (glib, etc.) loops
too.
'''

from pyee import EventEmitter
import random


class Sensor(EventEmitter):

    def __init__(self):

        # run the superclass constructor
        EventEmitter.__init__(self)
        self.type = None
        self.control_elements = []
        self.data_conditions = []

        # sensor_id should be unique
        rndnum = random.randint(0, high=100000)
        self.sensor_id = "sensor" + str(rndnum)

    def trial_started(self, tn, tc):
        '''
        Function is called when the trial is started. Parameters are
        tn = trial number (int)
        tc = trial count (int)
        '''

        return False

    def trial_completed(self, name, tn, tc, misc):
        return False

    def tag(self, tag):
        print "FUNCTION NOT IMPLEMENTED"

    def action(self, action_id):
        ''' Perform actions for the control elements defined. '''
        return False

    def get_type(self):
        ''' Returns sensor type. '''
        return self.type

    def set_data_condition(self, condition):
        ''' Insert new data condition. '''
        self.data_conditions.append(condition)

    def clear_data_conditions(self):
        ''' Clear existing data conditions. '''
        self.data_conditions = []

    def get_sensor_id(self):
        ''' Returns the sensor-id-string. '''
        return self.sensor_id

    def get_control_elements(self):
        ''' Returns the list of sensors control-elements. '''
        return self.control_elements

    def stop_recording(self):
        print "FUNCTION NOT IMPLEMENTED"

    def start_recording(self, rootdir, participant_id, experiment_file,
                        section_id):
        print "FUNCTION NOT IMPLEMENTED"

    def disconnect(self):
        self.emit("clear_screen")
        self.remove_all_listeners()
        return False

    def __del__(self):
        print self.sensor_id + " disconnected."
        return False
