from pyrfidsim.sim.dispatcher import Dispatcher


class Frame:
    def __init__(self):
        self.duration = None
        self.sender = None
        self.message = None
        self.sender_velocity = None
        self.tx_power = None
        self.tx_antenna = None

    def __str__(self):
        return "FRAME MSG=[{0}] sender={1} TXPower={2} TXAnt={3}".format(self.message, self.sender,
                                                                         self.tx_power, self.tx_antenna)


class Channel:
    def __init__(self, path_loss_model=None):
        self.__reader__ = None
        self.__tags__ = list()
        if path_loss_model is not None:
            self.path_loss_model = path_loss_model
        else:
            self.path_loss_model = lambda tx_pos, tx_orient, tx_rp, rx_pos, rx_orient, rx_rp, velocity: -30  # dB

    def handle_event(self, sender, frame):
        assert sender == self
        if frame.sender == self.__reader__:
            for tag in self.__tags__:
                tag.receive_end(frame)
        elif frame.sender in self.__tags__:
            self.__reader__.receive_end(frame)

    def send(self, sender, msg, tx_power, tx_antenna, sender_velocity=0):
        frame = Frame()
        frame.duration = msg.duration
        frame.sender = sender
        frame.message = msg
        frame.sender_velocity = sender_velocity
        frame.tx_power = tx_power
        frame.tx_antenna = tx_antenna
        if sender == self.__reader__:
            for tag in self.__tags__:
                tag.receive_begin(frame)
        elif sender in self.__tags__:
            self.__reader__.receive_begin(frame)
        Dispatcher.schedule(self, frame, frame.duration)

    def update_field(self, sender, tx_power, tx_antenna):
        if sender == self.__reader__:
            for tag in self.__tags__:
                tag.update_field(sender, tx_power, tx_antenna)
        else:
            raise RuntimeError("only Reader is allowed to call Channel.update_field")

    def get_path_loss(self, tx_antenna, rx_antenna, velocity):
        return self.path_loss_model(tx_antenna.position, tx_antenna.orientation, tx_antenna.radiation_pattern,
                                    rx_antenna.position, rx_antenna.orientation, rx_antenna.radiation_pattern, velocity)

    def attach_reader(self, reader):
        if self.__reader__ is not None:
            raise RuntimeError("reader is already attached")
        else:
            self.__reader__ = reader

    def detach_reader(self, reader):
        if self.__reader__ == reader:
            self.__reader__ = None

    def attach_tag(self, tag):
        if tag not in self.__tags__:
            self.__tags__.append(tag)

    def detach_tag(self, tag):
        if tag in self.__tags__:
            self.__tags__.remove(tag)
