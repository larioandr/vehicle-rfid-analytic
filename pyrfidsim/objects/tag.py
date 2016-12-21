from enum import Enum
import numpy as np

from pyrfidsim.helpers.geometry import Vec3
from pyrfidsim.helpers.protocol import DivRatio, Protocol
from pyrfidsim.objects.gobject import GObject
from pyrfidsim.sim.dispatcher import Dispatcher
from pyrfidsim.sim.environment import Env


class Tag(GObject):
    class State(Enum):
        OFF = 0
        READY = 1
        ARBITRATE = 2
        REPLY = 3
        ACKNOWLEDGED = 4
        OPEN = 5
        SECURED = 6
        KILLED = 7

    OFF_POWER = -200

    def __init__(self):
        super().__init__()
        self.id = None
        self.epc = '112233445566778899AABBCC'
        self.tid = '0000123456789ABC'
        self.epc_bitlen = 96
        self.tid_bitlen = 64
        self.__antenna__ = None
        self.sensitivity = -18  # dBm
        self.modulation_loss = -6  # dBm
        self.polarization_loss = -5  # dBm
        self.__channel__ = None
        self.__state__ = Tag.State.OFF
        # self.__timeout__ = None
        self.__power__ = Tag.OFF_POWER
        self.__slot__ = 0xFFFF
        self.__trext__ = False
        self.__blf__ = None
        self.__m__ = None
        self.__rn16__ = None

    @property
    def antenna(self):
        return self.__antenna__

    @antenna.setter
    def antenna(self, ant):
        if self.__antenna__ == ant:
            return
        if self.__antenna__ is not None:
            self.__antenna__.owner = None
        if ant is not None:
            ant.owner = self
        self.__antenna__ = ant

    @property
    def channel(self):
        return self.__channel__

    @channel.setter
    def channel(self, value):
        if self.__channel__ == value:
            return
        if self.__channel__ is not None:
            self.__channel__.detach_tag(self)
        if value is not None:
            value.attach_tag(self)
        self.__channel__ = value

    def initialize(self):
        self.__power__ = Tag.OFF_POWER
        self.__slot__ = 0x7FFF
        self.__trext__ = None
        self.__blf__ = None
        self.__m__ = None
        self.__rn16__ = None
        self.__state__ = Tag.State.OFF

    def destroy(self):
        if self.channel is not None:
            self.channel.detach_tag(self)
            self.channel = None
        Dispatcher.remove_entity(self)
        super().destroy()

    @property
    def state(self):
        return self.__state__

    def handle_event(self, sender, event):
        pass

    def update_field(self, reader, tx_power, tx_antenna, velocity=0):
        self.__power__ = self.get_rx_power(tx_power, tx_antenna, velocity)
        Env.log(self, 'power update: {0:.3} dBm [{1}]'.format(self.__power__, self.get_status_string()))
        if self.__power__ < self.sensitivity and self.state != Tag.State.OFF:
            self.handle_turn_off()
        elif self.__power__ >= self.sensitivity and self.state == Tag.State.OFF:
            self.handle_turn_on()
            # Dispatcher.cancel(self.__timeout__)
            # self.__timeout__ = None

    def get_rx_power(self, tx_power, tx_antenna, velocity=0):
        pl = self.channel.get_path_loss(tx_antenna, self.antenna, velocity)
        return tx_power + tx_antenna.gain + pl + self.antenna.gain + self.polarization_loss

    def get_tx_power(self):
        return self.__power__ + self.modulation_loss

    def receive_begin(self, frame):
        Env.log(self, 'started receiving frame: {0}'.format(frame))
        self.update_field(frame.sender, frame.tx_power, frame.tx_antenna, frame.sender_velocity)
        # Dispatcher.cancel(self.__timeout__)
        # self.__timeout__ = None

    def receive_end(self, frame):
        Env.log(self, 'finished receiving frame: {0} [{1}]'.format(frame, self.get_status_string()))
        if self.state != Tag.State.OFF:
            self.handle_command(frame.message)

    def handle_command(self, command):
        if command.name == "Query":
            self.handle_query(command)
        elif command.name == "QueryRep":
            self.handle_qrep(command)
        elif command.name == "ACK":
            self.handle_ack(command)
        elif command.name == "Req_RN":
            self.handle_reqrn(command)
        elif command.name == "Read":
            self.handle_read(command)
        else:
            raise RuntimeError("Command {0} not supported by the tag".format(command.name))

    def handle_query(self, cmd):
        if self.state == Tag.State.OFF:
            return
        q = cmd.fields['q']
        self.__slot__ = np.random.randint(0, 2**q)
        self.__trext__ = cmd.fields['trext']
        self.__m__ = cmd.fields['m']
        self.__blf__ = (8.0 if cmd.fields['dr'] == DivRatio.kDR8 else 64.0/3) / cmd.preamble.trcal
        if self.__slot__ == 0:
            self.set_state(Tag.State.REPLY)
            self.__rn16__ = np.random.randint(0, 0x10000)
            reply = Protocol.build_rn16_reply(self.__m__, self.__trext__, self.__blf__, self.__rn16__)
            self.channel.send(self, reply, self.get_tx_power(), self.antenna)
            # Dispatcher.schedule(self, ("command timeout", None), Protocol.get_t2_max(self.__blf__))
        else:
            self.set_state(Tag.State.ARBITRATE)

    def handle_qrep(self, cmd):
        if self.state in [Tag.State.OFF, Tag.State.READY]:
            return
        self.__slot__ = self.__slot__ - 1 if self.__slot__ > 0 else 0x7FFF
        if self.__slot__ == 0:
            self.set_state(Tag.State.REPLY)
            self.__rn16__ = np.random.randint(0, 0x10000)
            reply = Protocol.build_rn16_reply(self.__m__, self.__trext__, self.__blf__, self.__rn16__)
            self.channel.send(self, reply, self.get_tx_power(), self.antenna)
            # Dispatcher.schedule(self, ("command timeout", None), Protocol.get_t2_max(self.__blf__))
        else:
            self.set_state(Tag.State.ARBITRATE)

    def handle_ack(self, cmd):
        if self.state == Tag.State.REPLY and cmd.fields['rn'] == self.__rn16__:
            self.set_state(Tag.State.ACKNOWLEDGED)
            reply = Protocol.build_ack_reply(self.__m__, self.__trext__, self.__blf__, self.epc, self.epc_bitlen)
            self.channel.send(self, reply, self.get_tx_power(), self.antenna)

    def handle_reqrn(self, cmd):
        if self.state in [Tag.State.ACKNOWLEDGED, Tag.State.SECURED] and cmd.fields['rn'] == self.__rn16__:
            self.set_state(Tag.State.SECURED)
            self.__rn16__ = np.random.randint(0, 0x10000)
            reply = Protocol.build_reqrn_reply(self.__m__, self.__trext__, self.__blf__, self.__rn16__)
            self.channel.send(self, reply, self.get_tx_power(), self.antenna)

    def handle_read(self, cmd):
        if self.state == Tag.State.SECURED and cmd.fields['rn'] == self.__rn16__:
            reply = Protocol.build_read_reply(self.__m__, self.__trext__, self.__blf__,
                                              self.tid, int(np.ceil(self.tid_bitlen / 16)), self.__rn16__)
            self.channel.send(self, reply, self.get_tx_power(), self.antenna)

    def handle_turn_on(self):
        Env.log(self, "turned on")
        self.set_state(Tag.State.READY)

    def handle_turn_off(self):
        Env.log(self, "turned off")
        if self.state != Tag.State.OFF:
            # Dispatcher.cancel(self.__timeout__)
            # self.__timeout__ = None
            self.__power__ = Tag.OFF_POWER
            self.__blf__ = None
            self.__trext__ = None
            self.__m__ = None
            self.__rn16__ = None
            self.set_state(Tag.State.OFF)

    def set_state(self, new_state):
        if self.__state__ != new_state:
            Env.log(self, 'change state: {0} --> {1}'.format(self.__state__, new_state))
            self.__state__ = new_state

    def __str__(self):
        return "tag-{0}".format(self.id)

    def get_status_string(self):
        return "state={0}, rx-power={1}, rn16={2}, pos={3}".format(self.state, self.__power__, self.__rn16__,
                                                                   self.position)