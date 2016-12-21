from binascii import crc32
from builtins import property, max
from enum import Enum
import numpy as np


class TagEncoding(Enum):
    kFm0 = 1
    kMiller2 = 2
    kMiller4 = 4
    kMiller8 = 8

def get_spb(m):
    if m == TagEncoding.kFm0:
        return 1
    elif m == TagEncoding.kMiller2:
        return 2
    elif m == TagEncoding.kMiller4:
        return 4
    elif m == TagEncoding.kMiller8:
        return 8
    else:
        raise "Unrecognized tag encoding"

class Session(Enum):
    kSession0 = 0
    kSession1 = 1
    kSession2 = 2
    kSession3 = 3


class SelFlag(Enum):
    kSelAll = 0
    kSelNone = 2
    kSelOnly = 3


class Target(Enum):
    kTargetA = 0
    kTargetB = 1


class DivRatio(Enum):
    kDR8 = 0
    kDR643 = 1


class MemoryBank(Enum):
    kReserved = 0
    kEPC = 1
    kTID = 2
    kUser = 3


class Message:
    def __init__(self, name, bitlen):
        self.__name__ = name
        self.__bitlen__ = bitlen
        self.__fields__ = dict()

    @property
    def name(self):
        return self.__name__

    @property
    def bitlen(self):
        return self.__bitlen__

    @property
    def fields(self):
        return self.__fields__


class Command(Message):
    class Preamble:
        class Type(Enum):
            kPreamble = 0
            kSync = 1

        def __init__(self):
            self.type = Command.Preamble.Type.kSync
            self.delim = 12.5 * 1e-6
            self.data0 = None
            self.data1 = None
            self.rtcal = self.data0 + self.data1 if self.data0 is not None and self.data1 is not None else None
            self.trcal = None

        def __str__(self):
            if self.type == Command.Preamble.Type.kPreamble:
                return "PREAMBLE [Delim={0:.2f}us Tari={1:.2f}us RTcal={2:.2f}us TRcal={3:.2f}us]".format(
                    self.delim * 1e6, self.data0 * 1e6, self.rtcal * 1e6, self.trcal * 1e6)
            else:
                return "SYNC [Delim={0:.2f}us Tari={1:.2f}us RTcal={2:.2f}us]".format(
                    self.delim * 1e6, self.data0 * 1e6, self.rtcal * 1e6)

        @property
        def duration(self):
            return self.delim + self.data0 + self.data1 + self.rtcal + (
                self.trcal if self.type == Command.Preamble.Type.kPreamble else 0.0)

    def __init__(self, name, bitlen, code):
        super().__init__(name, bitlen)
        self.code = code
        self.preamble = Command.Preamble()

    def __str__(self):
        return "{0} bitlen={1} {2} {3}".format(self.name, self.bitlen, self.preamble, self.fields)

    @property
    def duration(self):
        return self.bitlen / 2 * (self.preamble.data0 + self.preamble.data1) + self.preamble.duration


class Reply(Message):
    def __init__(self, name, bitlen, m, trext, blf):
        super().__init__(name, bitlen)
        self.m = m
        self.trext = trext
        self.blf = blf

    @property
    def duration(self):
        t_bit = 1.0/self.blf * get_spb(self.m)
        return (self.bitlen + self.preamble_bitlen) * t_bit

    @property
    def preamble_duration(self):
        t_bit = 1.0 / self.blf * get_spb(self.m)
        return self.preamble_bitlen * t_bit

    @property
    def preamble_bitlen(self):
        if self.m == TagEncoding.kFm0:
            return 6 if not self.trext else 18
        else:
            return 10 if not self.trext else 22

    def __str__(self):
        return "{0} bitlen={1} preamble-bitlen={2} {3}".format(self.name, self.bitlen, self.preamble_bitlen, self.fields)


class Protocol:
    def __init__(self):
        pass

    @staticmethod
    def build_query_command(data0, data1, trcal, q, m, session, sel, trext, dr, target, crc5=0b10101):
        cmd = Command('Query', 22, 0b1000)
        cmd.preamble.type = Command.Preamble.Type.kPreamble
        cmd.preamble.data0 = data0
        cmd.preamble.data1 = data1
        cmd.preamble.rtcal = data0 + data1
        cmd.preamble.trcal = trcal
        cmd.fields['dr'] = dr
        cmd.fields['m'] = m
        cmd.fields['trext'] = trext
        cmd.fields['sel'] = sel
        cmd.fields['session'] = session
        cmd.fields['target'] = target
        cmd.fields['q'] = q
        cmd.fields['crc'] = crc5
        return cmd

    @staticmethod
    def build_qrep_command(data0, data1, session):
        cmd = Command('QueryRep', 4, 0b0)
        cmd.preamble.type = Command.Preamble.Type.kSync
        cmd.preamble.data0 = data0
        cmd.preamble.data1 = data1
        cmd.preamble.rtcal = data0 + data1
        cmd.fields['session'] = session
        return cmd

    @staticmethod
    def build_ack_command(data0, data1, rn):
        cmd = Command('ACK', 18, 0b01)
        cmd.preamble.type = Command.Preamble.Type.kSync
        cmd.preamble.data0 = data0
        cmd.preamble.data1 = data1
        cmd.preamble.rtcal = data0 + data1
        cmd.fields['rn'] = rn
        return cmd

    @staticmethod
    def build_reqrn_command(data0, data1, rn, crc16=0b1010101010101010):
        cmd = Comamnd('Req_RN', 40, 0b11000001)
        cmd.preamble.type = Command.Preamble.Type.kSync
        cmd.preamble.data0 = data0
        cmd.preamble.data1 = data1
        cmd.preamble.rtcal = data0 + data1
        cmd.fields['rn'] = rn
        cmd.fields['crc'] = crc16
        return cmd

    @staticmethod
    def build_read_command(data0, data1, membank, wordptr, wordcount, rn, crc16=0b1010101010101010):
        cmd = Command('Read', 52, 0b11000010)
        cmd.preamble.type = Command.Preamble.Type.kSync
        cmd.preamble.data0 = data0
        cmd.preamble.data1 = data1
        cmd.preamble.rtcal = data0 + data1
        cmd.fields['membank'] = membank
        cmd.fields['wordptr'] = wordptr
        cmd.fields['wordcount'] = wordcount
        cmd.fields['rn'] = rn
        cmd.fields['crc'] = crc16
        return cmd

    @staticmethod
    def build_rn16_reply(m, trext, blf, rn):
        reply = Reply("RN16", 16, m, trext, blf)
        reply.fields['rn'] = rn
        return reply

    @staticmethod
    def build_ack_reply(m, trext, blf, epc, epcbitlen, crc16=0b1010101010101010):
        reply = Reply('Response', epcbitlen + 32, m, trext, blf)
        reply.fields['epc'] = epc
        reply.fields['crc'] = crc16
        return reply

    @staticmethod
    def build_reqrn_reply(m, trext, blf, rn, crc16=0b1010101010101010):
        reply = Reply('Handle', 32, m, trext, blf)
        reply.fields['rn'] = rn
        reply.fields['crc'] = crc16
        return reply

    @staticmethod
    def build_read_reply(m, trext, blf, words, wordsnum, rn, crc16=0b1010101010101010):
        reply = Reply('ReadReply', 33 + wordsnum * 16, m, trext, blf)
        reply.fields['header'] = 0
        reply.fields['words'] = words
        reply.fields['rn'] = rn
        reply.fields['crc'] = crc16
        return reply

    @staticmethod
    def get_tpri(trcal, dr):
        return trcal / (8 if dr == DivRatio.kDR8 else 64.0/3)

    @staticmethod
    def get_t1(rtcal, trcal, dr):
        return max(10 * Protocol.get_tpri(trcal, dr), rtcal)

    @staticmethod
    def get_t2(t_now, t_sent, rtcal, trcal, dr):
        dt = t_now - t_sent
        t_pri = Protocol.get_tpri(trcal, dr)
        t4 = Protocol.get_t4(rtcal)
        if dt > t4:
            return 3.0 * t_pri
        else:
            return max(t4 - dt, 3.0 * t_pri)

    @staticmethod
    def get_t2_max(blf):
        t_pri = 1.0 / blf
        return 20 * t_pri

    @staticmethod
    def get_t3(rtcal, trcal, dr):
        return max(0, Protocol.get_t4(rtcal) - Protocol.get_t1(rtcal, trcal, dr))

    @staticmethod
    def get_t4(rtcal):
        return 2 * rtcal
