import numpy as np

from pyrfidsim.objects.antenna import Antenna
from pyrfidsim.objects.tag import Tag
from pyrfidsim.objects.vehicle import Vehicle
from pyrfidsim.sim.dispatcher import Dispatcher


class Generator:
    def __init__(self):
        self.generation_interval = 1  # seconds
        self.generation_limit = 1  # vehicles
        self.channel = None

        self.vehicle_initial_position = np.array([-20, 0, 0])
        self.vehicle_direction = np.array([1, 0, 0])
        self.vehicle_x_axis = np.array([1, 0, 0])
        self.vehicle_y_axis = np.array([0, 1, 0])
        self.vehicle_z_axis = np.array([0, 0, 1])
        self.vehicle_speed = 50.0/3
        self.vehicle_distance = 40.0

        self.tag_epc_bitlen = 96
        self.tag_tid_bitlen = 64

        self.plate_tag_sensitivity = -18
        self.plate_tag_modulation_loss = -6
        self.plate_tag_polarization_loss = -5

        self.windshield_tag_sensitivity = -18
        self.windshield_tag_modulation_loss = -6
        self.windshield_tag_polarization_loss = -5

        self.frontplate_antenna_position = np.array([2, 0, 0.5])
        self.frontplate_antenna_x_axis = np.array([1, 0, 0])
        self.frontplate_antenna_y_axis = np.array([0, 1, 0])
        self.frontplate_antenna_z_axis = np.array([0, 0, 1])
        self.frontplate_antenna_radiation_pattern = None
        self.frontplate_antenna_gain = 2.15
        self.frontplate_antenna_orientation = np.array([1, 0, 0])

        self.backplate_antenna_position = np.array([-2, 0, 0.5])
        self.backplate_antenna_x_axis = np.array([-1, 0, 0])
        self.backplate_antenna_y_axis = np.array([0, -1, 0])
        self.backplate_antenna_z_axis = np.array([0, 0, 1])
        self.backplate_antenna_radiation_pattern = None
        self.backplate_antenna_gain = 2.15
        self.backplate_antenna_orientation = np.array([-1, 0, 0])

        self.windshield_antenna_position = np.array([1, 0.5, 1])
        self.windshield_antenna_x_axis = np.array([-1, 0, 0])
        self.windshield_antenna_y_axis = np.array([0, -1, 0])
        self.windshield_antenna_z_axis = np.array([0, 0, 1])
        self.windshield_antenna_radiation_pattern = None
        self.windshield_antenna_gain = 2.15
        self.windshield_antenna_orientation = np.array([-1, 0, 0])

        self.__next_tag_index__ = 0
        self.__next_vehicle_index__ = 0

    def initialize(self):
        Dispatcher.schedule(self, ('generate', None), 0)
        print("generator initialized")

    def handle_event(self, sender, event):
        assert(sender == self)
        name, vehicle = event
        if name == 'generate':
            vehicle = self.build_vehicle()
            vehicle.initialize()
            if self.__next_vehicle_index__ < self.generation_limit:
                Dispatcher.schedule(self, ('generate', None), self.generation_interval)
            Dispatcher.schedule(self, ('destroy', vehicle), vehicle.lifetime)
        elif name == 'destroy':
            vehicle.destroy()

    def build_vehicle(self):
        vehicle = Vehicle()
        vehicle.initial_position = self.vehicle_initial_position
        vehicle.x_axis = self.vehicle_x_axis
        vehicle.y_axis = self.vehicle_y_axis
        vehicle.z_axis = self.vehicle_z_axis
        vehicle.speed = self.vehicle_speed
        vehicle.direction = self.vehicle_direction
        vehicle.distance = self.vehicle_distance
        vehicle.id = self.__next_vehicle_index__
        self.__next_vehicle_index__ += 1

        frontplate_tag = self.build_frontplate_tag()
        backplate_tag = self.build_backplate_tag()
        windshield_tag = self.build_windshield_tag()

        frontplate_tag.channel = self.channel
        backplate_tag.channel = self.channel
        windshield_tag.channel = self.channel

        vehicle.add_tag(frontplate_tag)
        vehicle.add_tag(backplate_tag)
        vehicle.add_tag(windshield_tag)

        return vehicle

    def build_frontplate_tag(self):
        epc_bytelength = int(np.ceil(self.tag_epc_bitlen / 8))
        tid_bytelength = int(np.ceil(self.tag_tid_bitlen / 8))

        tag = Tag()
        tag.id = self.__next_tag_index__
        tag.epc_bitlen = self.tag_epc_bitlen
        tag.tid_bitlen = self.tag_tid_bitlen
        tag.epc = ''.join([Generator.get_random_hex_char() for i in range(0, 2*epc_bytelength)])
        tag.tid = ''.join([Generator.get_random_hex_char() for i in range(0, 2*tid_bytelength)])
        tag.sensitivity = self.plate_tag_sensitivity
        tag.modulation_loss = self.plate_tag_modulation_loss
        tag.polarization_loss = self.plate_tag_polarization_loss

        antenna = Antenna()
        antenna.index = 0
        antenna.position = self.frontplate_antenna_position
        antenna.x_axis = self.frontplate_antenna_x_axis
        antenna.y_axis = self.frontplate_antenna_y_axis
        antenna.z_axis = self.frontplate_antenna_z_axis
        antenna.radiation_pattern = self.frontplate_antenna_radiation_pattern
        antenna.gain = self.frontplate_antenna_gain
        antenna.orientation = self.frontplate_antenna_orientation
        tag.antenna = antenna

        self.__next_tag_index__ += 1
        return tag

    def build_backplate_tag(self):
        epc_bytelength = int(np.ceil(self.tag_epc_bitlen / 8))
        tid_bytelength = int(np.ceil(self.tag_tid_bitlen / 8))

        tag = Tag()
        tag.id = self.__next_tag_index__
        tag.epc_bitlen = self.tag_epc_bitlen
        tag.tid_bitlen = self.tag_tid_bitlen
        tag.epc = ''.join([Generator.get_random_hex_char() for i in range(0, 2*epc_bytelength)])
        tag.tid = ''.join([Generator.get_random_hex_char() for i in range(0, 2*tid_bytelength)])
        tag.sensitivity = self.plate_tag_sensitivity
        tag.modulation_loss = self.plate_tag_modulation_loss
        tag.polarization_loss = self.plate_tag_polarization_loss

        antenna = Antenna()
        antenna.index = 0
        antenna.position = self.backplate_antenna_position
        antenna.x_axis = self.backplate_antenna_x_axis
        antenna.y_axis = self.backplate_antenna_y_axis
        antenna.z_axis = self.backplate_antenna_z_axis
        antenna.radiation_pattern = self.backplate_antenna_radiation_pattern
        antenna.gain = self.backplate_antenna_gain
        antenna.orientation = self.backplate_antenna_orientation
        tag.antenna = antenna

        self.__next_tag_index__ += 1
        return tag

    def build_windshield_tag(self):
        epc_bytelength = int(np.ceil(self.tag_epc_bitlen / 8))
        tid_bytelength = int(np.ceil(self.tag_tid_bitlen / 8))

        tag = Tag()
        tag.id = self.__next_tag_index__
        tag.epc_bitlen = self.tag_epc_bitlen
        tag.tid_bitlen = self.tag_tid_bitlen
        tag.epc = ''.join([Generator.get_random_hex_char() for i in range(0, 2*epc_bytelength)])
        tag.tid = ''.join([Generator.get_random_hex_char() for i in range(0, 2*tid_bytelength)])
        tag.sensitivity = self.windshield_tag_sensitivity
        tag.modulation_loss = self.windshield_tag_modulation_loss
        tag.polarization_loss = self.windshield_tag_polarization_loss

        antenna = Antenna()
        antenna.index = 0
        antenna.position = self.windshield_antenna_position
        antenna.x_axis = self.windshield_antenna_x_axis
        antenna.y_axis = self.windshield_antenna_y_axis
        antenna.z_axis = self.windshield_antenna_z_axis
        antenna.radiation_pattern = self.windshield_antenna_radiation_pattern
        antenna.gain = self.windshield_antenna_gain
        antenna.orientation = self.windshield_antenna_orientation
        tag.antenna = antenna

        self.__next_tag_index__ += 1
        return tag

    @staticmethod
    def get_random_hex_char():
        x = np.random.randint(0, 16)
        return chr(ord('0') + x if x < 10 else ord('A') + (x - 10))
