from enum import Enum
import numpy as np
from pyrfidsim.helpers.protocol import TagEncoding, DivRatio
from pyrfidsim.objects.antenna import Antenna
from pyrfidsim.objects.channel import Channel
from pyrfidsim.objects.generator import Generator
from pyrfidsim.objects.reader import RFIDReader
from pyrfidsim.sim.dispatcher import Dispatcher


class ReaderAntennaPlacement(Enum):
    FRONT_ONLY = 0
    BACK_ONLY = 1
    FRONT_AND_BACK = 2


class Simulation:
    def __init__(self):
        self.max_time = 10              # seconds
        self.vehicle_speed = 50.0/3     # meters per second
        self.vehicle_interval = 1       # seconds
        self.lanes_num = 1              # number of lanes
        self.lane_width = 3             # meters
        self.num_vehicles = 1           # total number of vehicles per generator
        self.path_loss_model = None     # path loss model
        self.road_length = 40           # meters

        self.reader_altitude = 5        # meters
        self.reader_antenna_gain = 8    # dBi
        self.reader_antenna_placement = ReaderAntennaPlacement.FRONT_ONLY
        self.reader_antenna_radiation_pattern = None
        self.reader_antenna_angle = 45  # vertical angle, degrees
        self.reader_power = 31.5        # dBm
        self.reader_noise = -80         # dBm
        self.read_tid = False           # indicate whether we need to read TID
        self.tari = 6.25 * 1e-6         # seconds
        self.rtcal = 18 * 1e-6          # seconds
        self.trcal = 30 * 1e-6          # seconds
        self.trext = False              # seconds
        self.q = 4                      # 0..15
        self.m = TagEncoding.kFm0
        self.dr = DivRatio.kDR8
        self.ber_model = None                       # BER computation model

        self.plate_tag_gain = 2.15                  # dBi
        self.plate_tag_radiation_pattern = None
        self.plate_tag_modulation_loss = -6         # dB
        self.plate_tag_polarization_loss = -5       # dB

        self.sticker_tag_gain = 0                   # dBi
        self.sticker_tag_radiation_pattern = None
        self.sticker_tag_modulation_loss = -6       # dB
        self.sticker_tag_polarization_loss = -5     # dB

        self.__reader__ = None
        self.__channel__ = None
        self.__generators__ = dict()

    def run(self):
        Dispatcher(self.max_time)
        self.build_model()
        self.__reader__.initialize()
        for lane, gen in self.__generators__.items():
            gen.initialize()
        Dispatcher.run()

    def build_model(self):
        # Creating channel
        self.__channel__ = Channel(self.path_loss_model)

        # Creating reader and antennas
        self.__reader__ = RFIDReader()
        self.__reader__.channel = self.__channel__
        self.__reader__.position = np.array([0, 0, self.reader_altitude])
        self.__reader__.x_axis = np.array([1, 0, 0])
        self.__reader__.y_axis = np.array([0, 1, 0])
        self.__reader__.z_axis = np.array([0, 0, 1])
        self.__reader__.power = self.reader_power
        self.__reader__.q = self.q
        self.__reader__.m = self.m
        self.__reader__.trext = self.trext
        self.__reader__.dr = self.dr
        self.__reader__.data0 = self.tari
        self.__reader__.data1 = self.rtcal - self.tari
        self.__reader__.trcal = self.trcal
        self.__reader__.need_tid = self.read_tid
        self.__reader__.ber_model = self.ber_model
        self.__reader__.noise = self.reader_noise

        reader_antennas = []
        for lane in range(0, self.lanes_num):
            if self.reader_antenna_placement in [ReaderAntennaPlacement.FRONT_ONLY,
                                                 ReaderAntennaPlacement.FRONT_AND_BACK]:
                reader_antennas.append(self.create_reader_antenna(lane, 'front'))
            if self.reader_antenna_placement in [ReaderAntennaPlacement.BACK_ONLY,
                                                 ReaderAntennaPlacement.FRONT_AND_BACK]:
                reader_antennas.append(self.create_reader_antenna(lane, 'back'))
        for i in range(0, len(reader_antennas)):
            reader_antennas[i].index = i
            self.__reader__.attach_antenna(reader_antennas[i])

        # Creating generators
        for lane in range(0, self.lanes_num):
            generator = Generator()
            generator.channel = self.__channel__
            generator.vehicle_initial_position = np.array(
                [-self.road_length/2, (0.5 * (1 - self.lanes_num) + lane) * self.lane_width, 0])
            generator.vehicle_distance = self.road_length
            generator.vehicle_direction = np.array([1, 0, 0])
            generator.vehicle_speed = self.vehicle_speed
            generator.generation_interval = self.vehicle_interval
            generator.plate_tag_modulation_loss = self.plate_tag_modulation_loss
            generator.plate_tag_polarization_loss = self.plate_tag_polarization_loss
            generator.frontplate_antenna_radiation_pattern = self.plate_tag_radiation_pattern
            generator.frontplate_antenna_gain = self.plate_tag_gain
            generator.backplate_antenna_radiation_pattern = self.plate_tag_radiation_pattern
            generator.backplate_antenna_gain = self.plate_tag_gain
            generator.windshield_tag_modulation_loss = self.sticker_tag_modulation_loss
            generator.windshield_tag_polarization_loss = self.sticker_tag_polarization_loss
            generator.windshield_antenna_gain = self.sticker_tag_gain
            generator.windshield_antenna_radiation_pattern = self.sticker_tag_radiation_pattern
            self.__generators__[lane] = generator

    def create_reader_antenna(self, lane, placement):
        antenna = Antenna()
        antenna.gain = self.reader_antenna_gain
        antenna.radiation_pattern = self.reader_antenna_radiation_pattern
        antenna.position = np.array([0, (0.5 * (1 - self.lanes_num) + lane) * self.lane_width, self.reader_altitude])
        antenna.y_axis = np.array([0, 1, 0])
        alpha = self.reader_antenna_angle * np.pi / 180.0
        if placement == 'front':
            antenna.x_axis = np.array([-np.cos(alpha), 0, np.sin(alpha)])
            antenna.z_axis = np.array([-np.sin(alpha), 0, -np.cos(alpha)])
        elif placement == 'back':
            antenna.x_axis = np.array([-np.cos(alpha), 0, np.sin(alpha)])
            antenna.z_axis = np.array([-np.sin(alpha), 0, -np.cos(alpha)])
        else:
            raise ValueError('create_reader_antenna::placement arg must be in ["front", "back"]')
        antenna.orientation = antenna.x_axis
        return antenna
