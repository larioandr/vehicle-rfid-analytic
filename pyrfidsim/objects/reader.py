import math
import numpy as np

from pyrfidsim.helpers.power import db2ratio
from pyrfidsim.helpers.protocol import Protocol, TagEncoding, SelFlag, DivRatio, Session, Target, MemoryBank, get_spb
from pyrfidsim.objects.gobject import GObject
from pyrfidsim.sim.dispatcher import Dispatcher
from pyrfidsim.sim.environment import Env


class RFIDReader(GObject):
    def __init__(self):
        super().__init__()
        self.__channel__ = None
        self.power = 31.5  # dBm
        self.q = None
        self.m = TagEncoding.kFm0
        self.sel = SelFlag.kSelAll
        self.trext = False
        self.dr = DivRatio.kDR8
        self.target = Target.kTargetA
        self.session = Session.kSession0
        self.data0 = None
        self.data1 = None
        self.trcal = None
        self.slot = 0
        self.need_tid = False
        self.ber_model = None
        self.bandwidth = 1.2e6
        self.noise = -80  # dBm
        self.__antennas__ = list()
        self.__antenna_index__ = 0
        self.__timeout__ = None
        self.__rn16__ = None
        self.__t_sent__ = None
        self.__cached_rx_power__ = None
        self.__cached_epc__ = None
        self.__cached_tid__ = None
        self.__rxops__ = dict()

    @property
    def channel(self):
        return self.__channel__

    @channel.setter
    def channel(self, value):
        if self.__channel__ == value:
            return
        if self.__channel__ is not None:
            self.__channel__.detach_reader(self)
        if value is not None:
            value.attach_reader(self)
        self.__channel__ = value

    @property
    def rtcal(self):
        return self.data0 + self.data1

    def initialize(self):
        Dispatcher.schedule(self, ("start round", None), 0.0)
        print("reader initialized")

    def destroy(self):
        while len(self.__antennas__) > 0:
            self.detach_antenna(self.__antennas__[0])
        if self.channel is not None:
            self.channel.detach_reader(self)
        self.channel = None
        Dispatcher.remove_entity(self)
        super().destroy()

    def handle_event(self, sender, event):
        if sender == self:
            name, cmd = event
            if name == "start round":
                self.handle_round_start()
            elif name == "start slot":
                self.handle_slot_start()
            elif name == "reply timeout":
                self.handle_slot_finished()
            elif name == "send command":
                self.channel.send(self, cmd, self.tx_power, self.antenna)
                self.__t_sent__ = Dispatcher.get_time() + cmd.duration
                self.__timeout__ = Dispatcher.schedule(self, ("reply timeout", None),
                                                       cmd.duration + Protocol.get_t4(self.rtcal))

    def receive_begin(self, frame):
        first = len(self.__rxops__) == 0
        self.__rxops__[frame.sender] = [frame, not first]
        if not first:
            for sender, entry in self.__rxops__.items():
                entry[1] = True

    def receive_end(self, frame):
        if frame.sender not in self.__rxops__:
            print("RXOPS: {0}, sender={1}".format(self.__rxops__, frame.sender))
            raise RuntimeError("receive_end doesn't match receive_begin")
        frame, broken = self.__rxops__.pop(frame.sender)
        if not broken:
            rx_power = self.get_rx_power(frame.tx_power, frame.tx_antenna, frame.sender_velocity)
            t_pri = Protocol.get_tpri(self.trcal, self.dr)
            sync_var = self.get_synchronization_variance(rx_power, frame.message)
            snr = db2ratio(rx_power - self.noise) * get_spb(self.m) * t_pri * self.bandwidth * (math.cos(sync_var)**2)
            ber = self.ber_model(snr)
            assert(0.0 <= ber <= 1.0)
            p = frame.message.bitlen ** (1.0 - ber)
            if np.random.uniform() <= p:
                self.handle_tag_reply(frame.message, rx_power)
            del frame

    def handle_tag_reply(self, reply, rx_power):
        Dispatcher.cancel(self.__timeout__)
        if reply.name == 'RN16':
            self.__rn16__ = reply.fields['rn']
            cmd = Protocol.build_ack_command(self.data0, self.data1, self.__rn16__)
            dt = Protocol.get_t2(Dispatcher.get_time(), self.__t_sent__, self.rtcal, self.trcal, self.dr)
            self.__timeout__ = Dispatcher.schedule(self, ("send command", cmd), dt)
        elif reply.name == 'Response':
            if self.need_tid:
                self.__cached_epc__ = reply.fields['epc']
                self.__cached_rx_power__ = rx_power
                cmd = Protocol.build_reqrn_command(self.data0, self.data1, self.__rn16__)
                dt = Protocol.get_t2(Dispatcher.get_time(), self.__t_sent__, self.rtcal, self.trcal, self.dr)
                self.__timeout__ = Dispatcher.schedule(self, ("send command", cmd), dt)
            else:
                self.handle_slot_finished()
        elif reply.name == 'Handle':
            self.__rn16__ = reply.fields['rn']
            cmd = Protocol.build_read_command(self.data0, self.data1, MemoryBank.kTID, 0, 2, self.__rn16__)
            dt = Protocol.get_t2(Dispatcher.get_time(), self.__t_sent__, self.rtcal, self.trcal, self.dr)
            self.__timeout__ = Dispatcher.schedule(self, ("send command", cmd), dt)
        elif reply.name == 'ReadReply':
            self.__cached_tid__ = reply.fields['words']
            self.handle_slot_finished()

    def handle_round_start(self):
        Env.log(self, '===== started new round =====')
        self.slot = 0
        # FIXME: no interval before Query after tag reply
        cmd = Protocol.build_query_command(self.data0, self.data1, self.trcal,
                                           self.q, self.m, self.session, self.sel,
                                           self.trext, self.dr, self.target)
        self.channel.send(self, cmd, self.tx_power, self.antenna)
        self.__t_sent__ = Dispatcher.get_time()
        self.__timeout__ = Dispatcher.schedule(self, ("reply timeout", None),
                                               cmd.duration + Protocol.get_t4(self.rtcal))

    def handle_slot_start(self):
        self.__cached_epc__ = None
        self.__cached_rx_power__ = None
        self.__cached_tid__ = None

        #FIXME: no interval before QueryRep after tag reply
        cmd = Protocol.build_qrep_command(self.data0, self.data1, self.session)
        self.channel.send(self, cmd, self.tx_power, self.antenna)
        self.__t_sent__ = Dispatcher.get_time()
        self.__timeout__ = Dispatcher.schedule(self, ("reply timeout", None),
                                               cmd.duration + Protocol.get_t4(self.rtcal))

    def handle_slot_finished(self):
        if self.__cached_epc__ is not None:
            print("READ: epc={0} tid={1} rssi={2}".format(
                self.__cached_epc__, self.__cached_rx_power__,
                self.__cached_tid__ if self.__cached_tid__ is not None else ""))

        self.slot += 1
        if self.slot < 2**self.q - 1:
            Dispatcher.schedule(self, ("start slot", None), 0.0)
        else:
            self.handle_round_finished()

    def handle_round_finished(self):
        self.switch_antenna()
        self.channel.update_field(self, self.tx_power, self.antenna)
        Dispatcher.schedule(self, ("start round", None), 0.0)

    def attach_antenna(self, antenna):
        self.__antennas__.append(antenna)
        antenna.index = len(self.__antennas__) - 1
        antenna.owner = self

    def detach_antenna(self, antenna):
        if antenna in self.__antennas__:
            self.__antennas__.remove(antenna)
            antenna.owner = None

    def switch_antenna(self):
        self.__antenna_index__ = (self.__antenna_index__ + 1) % len(self.__antennas__)

    @property
    def antenna(self):
        return self.__antennas__[self.__antenna_index__]

    @property
    def tx_power(self):
        return self.power

    def get_rx_power(self, tx_power, tx_antenna, velocity=0):
        pl = self.channel.get_path_loss(tx_antenna, self.antenna, velocity)
        return tx_power + tx_antenna.gain + pl + self.antenna.gain

    def get_synchronization_variance(self, rx_power, reply):
        return (1.0 / (db2ratio(rx_power - self.noise) * reply.preamble_duration * self.bandwidth)) ** 0.5

    def __str__(self):
        return "reader"
