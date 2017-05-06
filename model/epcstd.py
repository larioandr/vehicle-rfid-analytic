from enum import Enum
import random
import collections
import numpy as np


#
#######################################################################
# Data Types
#######################################################################
#
class DivideRatio(Enum):
    DR_8 = ('0', 8.0, '8')
    DR_643 = ('1', 64.0/3, '64/3')

    # noinspection PyInitNewSignature
    def __init__(self, code, value, string):
        self._code = code
        self._value = value
        self._string = string

    @property
    def code(self):
        return self._code

    def eval(self):
        return self._value

    def __str__(self):
        return self._string


class Session(Enum):
    S0 = ('00', 0, "S0")
    S1 = ('01', 1, "S1")
    S2 = ('10', 2, "S2")
    S3 = ('11', 3, "S3")

    # noinspection PyInitNewSignature
    def __init__(self, code, index, string):
        self._code = code
        self._index = index
        self._string = string

    @property
    def code(self):
        return self._code

    @property
    def index(self):
        return self._index

    def __str__(self):
        return self._string


class TagEncoding(Enum):
    FM0 = ('00', 1, "FM0")
    M2 = ('01', 2, "M2")
    M4 = ('10', 4, "M4")
    M8 = ('11', 8, "M8")

    # noinspection PyInitNewSignature
    def __init__(self, code, symbols_per_bit, string):
        self._code = code
        self._symbols_per_bit = symbols_per_bit
        self._string = string

    @property
    def code(self):
        return self._code

    @property
    def symbols_per_bit(self):
        return self._symbols_per_bit

    def __str__(self):
        return self._string

    @staticmethod
    def get(m):
        if m == 1:
            return TagEncoding.FM0
        elif m == 2:
            return TagEncoding.M2
        elif m == 4:
            return TagEncoding.M4
        elif m == 8:
            return TagEncoding.M8
        else:
            raise ValueError("m must be 1,2,4 or 8, but {} found".format(m))


class InventoryFlag(Enum):
    A = ('0', "A")
    B = ('1', "B")

    # noinspection PyInitNewSignature
    def __init__(self, code, string):
        self._code = code
        self._string = string

    @property
    def code(self):
        return self._code

    def __str__(self):
        return self._string


class SelFlag(Enum):
    ALL = ('00', "All")
    NOT_SEL = ('10', "~SL")
    SEL = ('11', "SL")

    # noinspection PyInitNewSignature
    def __init__(self, code, string):
        self._code = code
        self._string = string

    @property
    def code(self):
        return self._code

    def __str__(self):
        return self._string


class MemoryBank(Enum):
    RESERVED = ('00', 'Reserved')
    EPC = ('01', 'EPC')
    TID = ('10', 'TID')
    USER = ('11', 'User')

    # noinspection PyInitNewSignature
    def __init__(self, code, string):
        self._code = code
        self._string = string

    @property
    def code(self):
        return self._code

    def __str__(self):
        return self._string


class CommandCode(Enum):
    QUERY = ('1000', 'Query')
    QUERY_REP = ('00', 'QueryRep')
    ACK = ('01', 'ACK')
    REQ_RN = ('11000001', 'Req_RN')
    READ = ('11000010', 'Read')

    # noinspection PyInitNewSignature
    def __init__(self, code, string):
        self._code = code
        self._string = string

    @property
    def code(self):
        return self._code

    def __str__(self):
        return self._string


class TempRange(Enum):
    NOMINAL = (False, "nominal")
    EXTENDED = (True, "extended")

    # noinspection PyInitNewSignature
    def __init__(self, extended, string):
        self._extended = extended
        self._string = string

    @property
    def extended(self):
        return self._extended

    def __str__(self):
        return self._string


#
#######################################################################
# Default system-wide Reader Parameters
#######################################################################
#
class ModelParams:
    tari = 6.25e-6
    rtcal = 1.5625e-05
    trcal = 3.125e-05
    delim = 12.5e-6
    Q = 4
    divide_ratio = DivideRatio.DR_8
    tag_encoding = TagEncoding.FM0
    sel = SelFlag.ALL
    session = Session.S0
    target = InventoryFlag.A
    trext = False
    read_default_bank = MemoryBank.TID
    read_default_word_ptr = 0
    read_default_word_count = 4  # FIXME: check this!
    temp_range = TempRange.NOMINAL
    access_ops = []  # this list contains reader commands for tag access
    default_epc = "FF" * 12
    default_read_data = "FF" * 8


modelParams = ModelParams()


#
#######################################################################
# Tag Operations
#######################################################################
#
class TagOp:
    pass


class TagReadOp(TagOp):
    bank = MemoryBank.TID
    word_ptr = 0
    word_count = 0

    def __init__(self):
        super().__init__()


#
#######################################################################
# API for encoding basic types
#######################################################################
#
def encode_bool(value):
    return '1' if value else '0'


def encode_int(value, n_bits):
    value %= 2 ** n_bits
    return "{:0{width}b}".format(value, width=n_bits)


def encode_word(value):
    return encode_int(value, 16)


def encode_byte(value):
    return encode_int(value, 8)


def encode_ebv(value, first_block=True):
    prefix = '0' if first_block else '1'
    if value < 128:
        return prefix + format(value, '07b')
    else:
        return encode_ebv(value >> 7, first_block=False) + \
               encode_ebv(value % 128, first_block=first_block)


#
#######################################################################
# Commands
#######################################################################
#
class Command:
    def __init__(self, code):
        super().__init__()
        self._code = code

    @property
    def code(self):
        return self._code

    def encode(self):
        raise NotImplementedError

    @property
    def bitlen(self):
        s = self.encode()
        return len(s)


class Query(Command):
    def __init__(self, dr=None, m=None, trext=None, sel=None, session=None,
                 target=None, q=None, crc=0x00):
        super().__init__(CommandCode.QUERY)
        self.dr = dr if dr is not None else modelParams.divide_ratio
        self.m = m if m is not None else modelParams.tag_encoding
        self.trext = trext if trext is not None else modelParams.trext
        self.sel = sel if sel is not None else modelParams.sel
        self.session = session if session is not None else modelParams.session
        self.target = target if target is not None else modelParams.target
        self.q = q if q is not None else modelParams.Q
        self.crc = crc

    def encode(self):
        return (self.code.code + self.dr.code + self.m.code +
                encode_bool(self.trext) + self.sel.code + self.session.code +
                self.target.code + encode_int(self.q, 4) +
                encode_int(self.crc, 5))

    def __str__(self):
        return "{o.code}{{DR({o.dr}),{o.m},TRext({trext}),{o.sel}," \
               "{o.session},{o.target},Q({o.q}),CRC(0x{o.crc:02X})}}" \
               "".format(o=self, trext=(1 if self.trext else 0))


class QueryRep(Command):
    def __init__(self, session=None):
        super().__init__(CommandCode.QUERY_REP)
        self.session = session if session is not None else modelParams.session

    def encode(self):
        return self.code.code + self.session.code

    def __str__(self):
        return "{o.code}{{{o.session}}}".format(o=self)


class Ack(Command):
    def __init__(self, rn):
        super().__init__(CommandCode.ACK)
        self.rn = rn

    def encode(self):
        return self.code.code + encode_int(self.rn, 16)

    def __str__(self):
        return "{o.code}{{0x{o.rn:04X}}}".format(o=self)


class ReqRN(Command):
    def __init__(self, rn=0x0000, crc=0x0000):
        super().__init__(CommandCode.REQ_RN)
        self.rn = rn
        self.crc = crc

    def encode(self):
        return self.code.code + encode_word(self.rn) + encode_word(self.crc)

    def __str__(self):
        return "{o.code}{{RN(0x{o.rn:04X}),CRC(0x{o.crc:04X})}}".format(o=self)


class Read(Command):
    def __init__(self, bank=None, word_ptr=None, word_count=None,
                 rn=0x0000, crc=0x0000):
        super().__init__(CommandCode.READ)
        self.bank = (bank if bank is not None
                     else modelParams.read_default_bank)
        self.word_ptr = (word_ptr if word_ptr is not None
                         else modelParams.read_default_word_ptr)
        self.word_count = (word_count if word_count is not None
                           else modelParams.read_default_word_count)
        self.rn = rn
        self.crc = crc

    def encode(self):
        return (self.code.code + self.bank.code + encode_ebv(self.word_ptr) +
                encode_byte(self.word_count) + encode_word(self.rn) +
                encode_word(self.crc))

    def __str__(self):
        return "{o.code}{{{o.bank},WordPtr(0x{o.word_ptr:02X})," \
               "WordCount({o.word_count}),RN(0x{o.rn:04X})," \
               "CRC(0x{o.crc:04X})}}".format(o=self)


#
#######################################################################
# Tag replies
#######################################################################
#
class ReplyType(Enum):
    QUERY_REPLY = 0
    ACK_REPLY = 1
    REQRN_REPLY = 2
    READ_REPLY = 3


class Reply:
    def __init__(self, reply_type):
        super().__init__()
        self.__type = reply_type

    @property
    def bitlen(self):
        raise NotImplementedError()

    @property
    def reply_type(self):
        return self.__type



class QueryReply(Reply):
    def __init__(self, rn=0x0000):
        super().__init__(ReplyType.QUERY_REPLY)
        self.rn = rn

    @property
    def bitlen(self):
        return 16

    def __str__(self):
        return "Reply(0x{o.rn:04X})".format(o=self)


def to_bytes(value):
    if isinstance(value, str):
        return list(bytearray.fromhex(value))
    elif isinstance(value, collections.Iterable):
        value = list(value)
        for b in value:
            if not isinstance(b, int) or not (0 <= b < 256):
                raise ValueError("each array element must represent a byte")
        return value
    else:
        raise ValueError("value must be a hex string or bytes collections")


class AckReply(Reply):
    def __init__(self, epc="", pc=0x0000, crc=0x0000):
        super().__init__(ReplyType.ACK_REPLY)
        self._data = to_bytes(epc)
        self.pc = pc
        self.crc = crc

    @property
    def bitlen(self):
        return 32 + len(self._data) * 8

    @property
    def epc(self):
        return self._data

    def get_epc_string(self, byte_separator=""):
        return byte_separator.join("{:02X}".format(b) for b in self._data)

    def __str__(self):
        return "Reply{{PC(0x{o.pc:04X}),EPC({epc})," \
               "CRC(0x{o.crc:04X})}}".format(
                o=self, epc=self.get_epc_string())


class ReqRnReply(Reply):
    def __init__(self, rn=0x0000, crc=0x0000):
        super().__init__(ReplyType.REQRN_REPLY)
        self.rn = rn
        self.crc = crc

    @property
    def bitlen(self):
        return 32

    def __str__(self):
        return "Reply{{RN(0x{o.rn:04X}),CRC(0x{o.crc:04X})}}".format(o=self)


class ReadReply(Reply):
    def __init__(self, data="", rn=0x0000, crc=0x0000, header=False):
        super().__init__(ReplyType.READ_REPLY)
        self.rn = rn
        self.crc = crc
        self.header = header
        self._data = to_bytes(data)

    @property
    def memory(self):
        return self._data

    def get_memory_string(self, byte_separator=""):
        return byte_separator.join("{:02X}".format(b) for b in self._data)

    @property
    def bitlen(self):
        return 33 + len(self.memory) * 8

    def __str__(self):
        return "Reply{{Header({header}),Memory({data}),RN(0x{o.rn:04X})," \
               "CRC(0x{o.crc:04X})}}".format(
                header=int(self.header), data=self.get_memory_string(), o=self)


#
#######################################################################
# Preambles and frames
#######################################################################
#
class ReaderSync:
    DELIM = 12.5e-6

    def __init__(self, tari, rtcal, delim=DELIM):
        super().__init__()
        self.tari = tari
        self.rtcal = rtcal
        self.delim = delim

    @property
    def data0(self): return self.tari

    @property
    def data1(self): return self.rtcal - self.tari

    @property
    def duration(self): return self.delim + self.tari + self.rtcal

    def __str__(self):
        return "{{(Delim({}us),Tari({}us),RTcal({}us)}}".format(
            self.delim * 1e6, self.tari * 1e6, self.rtcal * 1e6)


class ReaderPreamble(ReaderSync):
    def __init__(self, tari, rtcal, trcal, delim=ReaderSync.DELIM):
        super().__init__(tari=tari, rtcal=rtcal, delim=delim)
        self.trcal = trcal

    @property
    def duration(self): return super().duration + self.trcal

    def __str__(self):
        return "{{Delim({}us),Tari({}us),RTcal({}us)," \
               "TRcal({}us)}}".format(self.delim * 1e6, self.tari * 1e6,
                                      self.rtcal * 1e6, self.trcal * 1e6)


class TagPreamble:
    def __init__(self, extended=False):
        super().__init__()
        self.extended = extended

    @property
    def bitlen(self):
        raise NotImplementedError

    @property
    def encoding(self):
        raise NotImplementedError

    def get_duration(self, blf):
        return (self.bitlen * self.encoding.symbols_per_bit) / blf


class FM0Preamble(TagPreamble):
    def __init__(self, extended=False):
        super().__init__(extended)

    @property
    def bitlen(self):
        return 18 if self.extended else 6

    @property
    def encoding(self):
        return TagEncoding.FM0

    def __str__(self):
        return "{{({}){},{},trext({})}}".format(
            self.bitlen, "0..01010v1" if self.extended else "1010v1",
            self.encoding, 1 if self.extended else 0)


class MillerPreamble(TagPreamble):
    def __init__(self, m, extended=False):
        super().__init__(extended)
        self._encoding = MillerPreamble._get_and_validate_encoding(m)

    @property
    def m(self):
        return self._encoding.symbols_per_bit

    @m.setter
    def m(self, value):
        self._encoding = MillerPreamble._get_and_validate_encoding(value)

    @property
    def bitlen(self):
        return 22 if self.extended else 10

    @property
    def encoding(self): return self._encoding

    @staticmethod
    def _get_and_validate_encoding(m):
        enc = TagEncoding.get(m)
        if enc not in [TagEncoding.M2, TagEncoding.M4, TagEncoding.M8]:
            raise ValueError("Miller encodings supported are M2, M4, M8")
        return enc

    def __str__(self):
        return "{{({}){},{},trext({})}}".format(
            self.bitlen, "DD..DD010111" if self.extended else "DDDD010111",
            self.encoding, 1 if self.extended else 0)


def create_tag_preamble(encoding, extended=False):
    if encoding == TagEncoding.FM0:
        return FM0Preamble(extended)
    else:
        return MillerPreamble(m=encoding.symbols_per_bit, extended=extended)


class ReaderFrame:
    def __init__(self, preamble, command):
        super().__init__()
        self.preamble = preamble
        self.command = command

    @property
    def body_duration(self):
        encoded_string = (self.command if isinstance(self.command, str)
                          else self.command.encode())
        n_bits = {'0': 0, '1': 0}
        for b in encoded_string:
            n_bits[b] += 1
        d0 = self.preamble.data0
        d1 = self.preamble.data1
        return n_bits['0'] * d0 + n_bits['1'] * d1

    @property
    def preamble_duration(self):
        return self.preamble.duration

    @property
    def duration(self):
        return self.body_duration + self.preamble.duration

    def __str__(self):
        return "Frame{{{o.preamble}{o.command}}}".format(o=self)


class TagFrame:
    def __init__(self, preamble, reply):
        super().__init__()
        self.preamble = preamble
        self.reply = reply

    def get_body_duration(self, blf):
        m = self.preamble.encoding.symbols_per_bit
        return (self.reply.bitlen * m) / blf

    def get_duration(self, blf):
        m = self.preamble.encoding.symbols_per_bit
        t_preamble = self.preamble.get_duration(blf)
        t_body = self.get_body_duration(blf)
        t_suffix = m / blf
        return t_preamble + t_body + t_suffix

    def __str__(self):
        return "Frame{{{o.preamble}{o.reply}}}".format(o=self)


# TODO: not tested
# FIXME: not vectorized
def tag_preamble_bitlen(encoding=None, trext=None):
    encoding = encoding if encoding is not None else modelParams.tag_encoding
    trext = trext if trext is not None else modelParams.trext
    if encoding is TagEncoding.FM0:
        return 18 if trext else 6
    else:
        return 22 if trext else 10


# TODO: not tested
def tag_preamble_duration(blf=None, encoding=None, trext=None):
    blf = blf if blf is not None else get_blf()
    bitlen = tag_preamble_bitlen(encoding, trext)
    return bitlen / blf


#
#######################################################################
# Reader and Tag frames helpers and accessors
#######################################################################
#
def get_reader_frame_duration(command, tari=None, rtcal=None, trcal=None,
                              delim=None):
    tari = tari if tari is not None else modelParams.tari
    rtcal = rtcal if rtcal is not None else modelParams.rtcal
    trcal = trcal if trcal is not None else modelParams.trcal
    delim = delim if delim is not None else modelParams.delim

    if isinstance(command, Query) or (
                isinstance(command, str) and
                command.startswith(CommandCode.QUERY.code)):
        preamble = ReaderPreamble(tari, rtcal, trcal, delim)
    else:
        preamble = ReaderSync(tari=tari, rtcal=rtcal, delim=delim)
    frame = ReaderFrame(preamble, command)
    return frame.duration


def get_tag_frame_duration(reply, blf=None, encoding=None, trext=None):
    blf = blf if blf is not None else get_blf()
    encoding = encoding if encoding is not None else modelParams.tag_encoding
    trext = trext if trext is not None else modelParams.trext

    preamble = create_tag_preamble(encoding, trext)
    frame = TagFrame(preamble, reply)
    return frame.get_duration(blf)


# TODO: no test
def command_duration(code,
                     tari=None, rtcal=None, trcal=None, delim=None, dr=None,
                     m=None, trext=None, sel=None, session=None, target=None,
                     q=None, rn=None, bank=None, word_ptr=None,
                     word_count=None, crc5=0, crc16=0):
    if code is CommandCode.QUERY:
        return query_duration(tari, rtcal, trcal, delim, dr, m, trext, sel,
                              session, target, q, crc5)
    elif code is CommandCode.QUERY_REP:
        return query_rep_duration(tari, rtcal, trcal, delim, session)
    elif code is CommandCode.ACK:
        return ack_duration(tari, rtcal, trcal, delim, rn)
    elif code is CommandCode.REQ_RN:
        return reqrn_duration(tari, rtcal, trcal, delim, rn, crc16)
    elif code is CommandCode.READ:
        return read_duration(tari, rtcal, trcal, delim, bank, word_ptr,
                             word_count, rn, crc16)
    else:
        raise ValueError("unrecognized command code = {}".format(code))


# TODO: no test
# noinspection PyTypeChecker
def query_duration(tari=None, rtcal=None, trcal=None, delim=None, dr=None,
                   m=None, trext=None, sel=None, session=None, target=None,
                   q=None, crc=0x00):
    return get_reader_frame_duration(Query(dr, m, trext, sel, session, target,
                                           q, crc), tari, rtcal, trcal, delim)


# TODO: no test
# noinspection PyTypeChecker
def query_rep_duration(tari=None, rtcal=None, trcal=None, delim=None,
                       session=None):
    return get_reader_frame_duration(QueryRep(session), tari, rtcal, trcal,
                                     delim)


# TODO: no test
# noinspection PyTypeChecker
def ack_duration(tari=None, rtcal=None, trcal=None, delim=None, rn=None):
    return get_reader_frame_duration(Ack(rn), tari, rtcal, trcal, delim)


# TODO: no test
# noinspection PyTypeChecker
def reqrn_duration(tari=None, rtcal=None, trcal=None, delim=None, rn=None,
                   crc=0):
    return get_reader_frame_duration(ReqRN(rn, crc), tari, rtcal, trcal, delim)


# TODO: no test
# noinspection PyTypeChecker
def read_duration(tari=None, rtcal=None, trcal=None, delim=None, bank=None,
                  word_ptr=None, word_count=None, rn=None, crc=0x00):
    return get_reader_frame_duration(Read(bank, word_ptr, word_count, rn, crc),
                                     tari, rtcal, trcal, delim)


# TODO: no test
def reply_duration(reply_type, dr=None, trcal=None, encoding=None, trext=None,
                   epc=None, words_count=None):
    if reply_type is ReplyType.QUERY_REPLY:
        return query_reply_duration(dr, trcal, encoding, trext)
    elif reply_type is ReplyType.ACK_REPLY:
        return ack_reply_duration(dr, trcal, encoding, trext, epc)
    elif reply_type is ReplyType.REQRN_REPLY:
        return reqrn_reply_duration(dr, trcal, encoding, trext)
    elif reply_type is ReplyType.READ_REPLY:
        return read_reply_duration(dr, trcal, encoding, trext, words_count)
    else:
        raise ValueError("unrecognized reply type = {}".format(reply_type))


def __reply_duration(bs=0, dr=None, trcal=None, encoding=None, trext=None):
    bitrate = get_tag_bitrate(dr, trcal, encoding)
    preamble_bs = tag_preamble_bitlen(encoding, trext)
    suffix_bs = 1
    return (preamble_bs + bs + suffix_bs) / bitrate


# TODO: no test
def query_reply_duration(dr=None, trcal=None, encoding=None, trext=None):
    return __reply_duration(16, dr, trcal, encoding, trext)


# TODO: no test
def ack_reply_duration(dr=None, trcal=None, encoding=None, trext=None,
                       epc=None):
    return __reply_duration(32 + len(epc) * 8, dr, trcal, encoding, trext)


# TODO: no test
def reqrn_reply_duration(dr=None, trcal=None, encoding=None, trext=None):
    return __reply_duration(16, dr, trcal, encoding, trext)


# TODO: no test
def read_reply_duration(dr=None, trcal=None, encoding=None, trext=None,
                        words_count=None):
    return __reply_duration(words_count * 16 + 33, dr, trcal, encoding, trext)


#
#######################################################################
# Link timings estimation
#######################################################################
#
def get_blf(dr=None, trcal=None):
    dr = dr if dr is not None else modelParams.divide_ratio
    trcal = trcal if trcal is not None else modelParams.trcal
    return dr.eval() / trcal


def get_tag_bitrate(dr=None, trcal=None, encoding=None):
    blf = get_blf(dr, trcal)
    return blf / encoding.symbols_per_bit


def get_frt(trcal=None, dr=None, temp_range=None):
    trcal = trcal if trcal is not None else modelParams.trcal
    dr = dr if dr is not None else modelParams.divide_ratio
    temp_range = (temp_range if temp_range is not None
                  else modelParams.temp_range)

    if dr is DivideRatio.DR_643:
        if temp_range is TempRange.EXTENDED:
            f = [(33.633, 0.15), (66.033, 0.22), (82.467, 0.15),
                 (84.133, 0.10), (131.967, 0.12), (198.00, 0.07),
                 (227.25, 0.05)]
        else:
            f = [(33.633, 0.15), (66.033, 0.22), (67.367, 0.10),
                 (82.467, 0.12), (131.967, 0.10), (198.00, 0.07),
                 (227.25, 0.05)]
    else:
        if temp_range is TempRange.EXTENDED:
            f = [(24.7500, 0.19), (30.9375, 0.15), (49.50, 0.10),
                 (75.0000, 0.07), (202.0, 0.04)]
        else:
            f = [(24.75, 0.19), (25.25, 0.10), (30.9375, 0.12),
                 (49.50, 0.10), (75.00, 0.07), (202.000, 0.04)]
    for highest_trcal, frt in f:
        if trcal < highest_trcal * 1e-6:
            return frt
    return f[-1][1]


def get_pri(trcal=None, dr=None):
    trcal = trcal if trcal is not None else modelParams.trcal
    dr = dr if dr is not None else modelParams.divide_ratio
    return trcal / dr.eval()


def min_link_t(param_index, rtcal=None, trcal=None, dr=None, temp=None):
    rtcal = rtcal if rtcal is not None else modelParams.rtcal
    trcal = trcal if trcal is not None else modelParams.trcal
    dr = dr if dr is not None else modelParams.divide_ratio
    temp = temp if temp is not None else modelParams.temp_range
    if param_index is not None:
        if param_index in [1, 5, 6]:
            pri = get_pri(trcal, dr)
            frt = get_frt(trcal, dr, temp)
            return max(rtcal, pri * 10.0) * (1.0 - frt) - 2e-6
        elif param_index == 2:
            return 3.0 * get_pri(trcal, dr)
        elif param_index == 3:
            return 0.0
        elif param_index == 4:
            return 2.0 * rtcal
        elif param_index == 7:
            return max(link_t2_max(trcal, dr), 250e-6)
        else:
            raise ValueError("1 <= n <= 7, but n={} found".format(param_index))
    else:
        return [min_link_t(n, rtcal, trcal, dr, temp) for n in range(1, 8)]


def max_link_t(param_index, rtcal=None, trcal=None, dr=None, temp=None):
    rtcal = rtcal if rtcal is not None else modelParams.rtcal
    trcal = trcal if trcal is not None else modelParams.trcal
    dr = dr if dr is not None else modelParams.divide_ratio
    temp = temp if temp is not None else modelParams.temp_range
    if param_index is not None:
        if param_index == 1:
            pri = get_pri(trcal, dr)
            frt = get_frt(trcal, dr, temp)
            return max(rtcal, pri * 10.0) * (1.0 + frt) + 2e-6
        elif param_index == 2:
            return 20.0 * get_pri(trcal, dr)
        elif 5 <= param_index <= 7:
            return 0.02
        elif param_index == 3 or param_index == 4:
            return float('inf')
        else:
            raise ValueError("1 <= param_index <= 7, but param_index={} found"
                             "".format(param_index))
    else:
        return [max_link_t(n, rtcal, trcal, dr, temp) for n in range(1, 8)]


def link_t(param_index=None, rtcal=None, trcal=None, dr=None, temp=None):
    if param_index is None:
        return [link_t(n, rtcal, trcal, dr, temp) for n in range(1, 8)]
    else:
        return (min_link_t(param_index, rtcal, trcal, dr, temp),
                max_link_t(param_index, rtcal, trcal, dr, temp))


def link_t1_min(rtcal=None, trcal=None, dr=None, temp=None):
    return min_link_t(1, rtcal, trcal, dr, temp)


def link_t1_max(rtcal=None, trcal=None, dr=None, temp=None):
    return max_link_t(1, rtcal, trcal, dr, temp)


def link_t2_min(trcal=None, dr=None):
    return min_link_t(2, trcal=trcal, dr=dr)


def link_t2_max(trcal=None, dr=None):
    return max_link_t(2, trcal=trcal, dr=dr)


def link_t3():
    return min_link_t(3)


def link_t4(rtcal=None):
    return min_link_t(4, rtcal=rtcal)


def link_t5_min(rtcal=None, trcal=None, dr=None, temp=None):
    return min_link_t(1, rtcal, trcal, dr, temp)


def link_t5_max():
    return max_link_t(5)


def link_t6_min(rtcal=None, trcal=None, dr=None, temp=None):
    return min_link_t(1, rtcal, trcal, dr, temp)


def link_t6_max():
    return max_link_t(6)


def link_t7_min(trcal=None, dr=None):
    return min_link_t(7, trcal=trcal, dr=dr)


def link_t7_max():
    return max_link_t(7)


#
#######################################################################
# Slot duration estimation
#######################################################################
#
class SlotType(Enum):
    EMPTY = 0
    COLLISION = 1
    INVENTORY = 2
    ACCESS = 3


def slot_duration(slot_type, access_ops=None, tari=None, rtcal=None,
                  trcal=None, delim=None, dr=None, temp=None, m=None,
                  trext=None, sel=None, session=None, target=None, q=None,
                  rn=None, epc=None, crc5=None, crc16=None, is_first=False):
    rn = rn if rn is not None else random.randint(0x0000, 0xFFFF)

    t4 = link_t4(rtcal)
    if is_first:
        t_query = query_duration(tari, rtcal, trcal, delim, dr, m, trext, sel,
                                 session, target, q, crc5)
    else:
        t_query = query_rep_duration(tari, rtcal, trcal, delim, session)

    if slot_type is SlotType.EMPTY:
        t1 = link_t1_max(rtcal, trcal, dr, temp)
        t3 = link_t3()
        return t_query + np.maximum(t1 + t3, t4)

    t1_min = link_t1_min(rtcal, trcal, dr, temp)
    t2 = link_t2_min(trcal, dr)
    t_rn16 = query_reply_duration(dr, trcal, m, trext)

    t_inventory_rn16 = t_query + np.maximum(t1_min + t_rn16 + t2, t4)
    if slot_type is SlotType.COLLISION:
        return t_inventory_rn16

    t_ack = ack_duration(tari, rtcal, trcal, delim, rn)
    t_ack_reply = ack_reply_duration(dr, trcal, m, trext, epc)
    t_inventory = (t_inventory_rn16 + t_ack +
                   np.maximum(t1_min + t_ack_reply + t2, t4))

    if slot_type is SlotType.INVENTORY or (
                    slot_type is SlotType.ACCESS and access_ops is None):
        return t_inventory

    assert slot_type is SlotType.ACCESS
    # From here on, assume that slot_type is ACCESS

    t_access = 0
    for op in access_ops:
        if isinstance(op, TagReadOp):
            t_read_cmd = read_duration(tari, rtcal, trcal, delim, op.bank,
                                       op.word_ptr, op.word_count, rn, crc16)
            t_read_reply = read_reply_duration(dr, trcal, m, trext,
                                               op.word_count)
            t_access += np.maximum(t_read_cmd + t1_min + t_read_reply + t2, t4)
        else:
            raise ValueError("unrecognized tag operation = {}".format(op))

    return t_inventory + t_access


def slot_duration_min(slot_type, access_ops=None, tari=None, rtcal=None,
                      trcal=None, delim=None, dr=None, temp=None, epc=None,
                      is_first=False):
    return slot_duration(
        slot_type, access_ops, tari, rtcal, trcal, delim, dr, temp,
        m=TagEncoding.FM0, trext=False, sel=SelFlag.ALL, session=Session.S0,
        target=InventoryFlag.A, q=0, rn=0, epc=epc, crc5=0, crc16=0,
        is_first=is_first)


def slot_duration_max(slot_type, access_ops=None, tari=None, rtcal=None,
                      trcal=None, delim=None, dr=None, temp=None, epc=None,
                      is_first=False):
    return slot_duration(
        slot_type, access_ops, tari, rtcal, trcal, delim, dr, temp,
        m=TagEncoding.M8, trext=True, sel=SelFlag.SEL, session=Session.S3,
        target=InventoryFlag.B, q=15, rn=0xFFFF, epc=epc, crc5=0x1F,
        crc16=0xFFFF, is_first=is_first)


#
#######################################################################
# Round duration estimation
#######################################################################
#
def estimate_inventory_round():
    pass


def estimate_inventory_round_min():
    pass


def estimate_inventory_round_max():
    pass


def estimate_inventory_round_pmf():
    pass


#
#######################################################################
#
#######################################################################
#

#
#######################################################################
# Various helpers
#######################################################################
#


# noinspection PyTypeChecker
def get_elementary_timings(tari=None, rtcal=None, trcal=None, delim=None,
                           temp=None, dr=None, m=None, trext=None, sel=None,
                           session=None, target=None, q=None, bank=None,
                           word_ptr=None, word_count=None, rn=0, crc=0,
                           epc="00112233445566778899AABB",
                           mem="FFEEDDCCBBAA", pc=0):
    tari = tari if tari is not None else modelParams.tari
    rtcal = rtcal if rtcal is not None else modelParams.rtcal
    trcal = trcal if trcal is not None else modelParams.trcal
    delim = delim if delim is not None else modelParams.delim
    temp = temp if temp is not None else modelParams.temp_range
    dr = dr if dr is not None else modelParams.divide_ratio
    m = m if m is not None else modelParams.tag_encoding
    trext = trext if trext is not None else modelParams.trext
    sel = sel if sel is not None else modelParams.sel
    session = session if session is not None else modelParams.session
    target = target if target is not None else modelParams.target
    q = q if q is not None else modelParams.Q
    bank = bank if bank is not None else modelParams.read_default_bank
    word_ptr = word_ptr if word_ptr is not None else \
        modelParams.read_default_word_ptr
    word_count = word_count if word_count is not None else \
        modelParams.read_default_word_count

    query = Query(dr, m, trext, sel, session, target, q, crc)
    query_rep = QueryRep(session)
    ack = Ack(rn)
    req_rn = ReqRN(rn, crc)
    read = Read(bank, word_ptr, word_count, rn, crc)
    query_reply = QueryReply(rn)
    ack_reply = AckReply(epc, pc, crc)
    req_rn_reply = ReqRnReply(rn, crc)
    read_reply = ReadReply(mem, rn, crc)
    blf = get_blf(dr, trcal)

    ret = {
        'Tari': tari,
        'TRcal': trcal,
        'RTcal': rtcal,
        'Delim': delim,
        'TempRange': temp,
        'TRext': trext,
        'Q': q,
        'DR': dr,
        'M': m,
        'Target': target,
        'Sel': sel,
        'Session': session,
        'Bank':  bank,
        'WordPtr': word_ptr,
        'WordCount': word_count,
        'Query': get_reader_frame_duration(query, tari, rtcal, trcal, delim),
        'QueryRep': get_reader_frame_duration(query_rep, tari, rtcal, trcal,
                                              delim),
        'ACK': get_reader_frame_duration(ack, tari, rtcal, trcal, delim),
        'ReqRN': get_reader_frame_duration(req_rn, tari, rtcal, trcal, delim),
        'Read': get_reader_frame_duration(read, tari, rtcal, trcal, delim),
        'RN16': get_tag_frame_duration(query_reply, blf, m, trext),
        'Response': get_tag_frame_duration(ack_reply, blf, m, trext),
        'Handle': get_tag_frame_duration(req_rn_reply, blf, m, trext),
        'Data': get_tag_frame_duration(read_reply, blf, m, trext)
    }

    for timer_index in range(1, 8):
        t = link_t(timer_index, rtcal=rtcal, trcal=trcal, dr=dr, temp=temp)
        ret["T{}(min)".format(timer_index)] = t[0]
        ret["T{}(max)".format(timer_index)] = t[1]

    return ret


def prettify_elementary_timings(timings):
    timings_fields = tuple(elem for tupl in
                           (("T{}(min)".format(n), "T{}(max)".format(n))
                            for n in range(1, 8))
                           for elem in tupl)
    us_fields = ('Tari', 'TRcal', 'RTcal', 'Delim', 'Query', 'QueryRep', 'ACK',
                 'ReqRN', 'Read', 'RN16', 'Response', 'Handle', 'Data'
                 ) + timings_fields
    ordered_fields = (
        'Tari', 'RTcal', 'TRcal', 'Delim', 'TempRange', 'TRext',
        'Q', 'DR', 'M', 'Target', 'Sel', 'Session', 'Bank',
        'WordPtr', 'WordCount') + timings_fields + (
        'Query', 'QueryRep', 'ACK',
        'ReqRN', 'Read', 'RN16', 'Response', 'Handle', 'Data')
    ret = []
    for k in ordered_fields:
        s = "{:12s}: ".format(k)
        if k in us_fields:
            s += "{:>14.8f} us".format(timings[k] / 1e-6)
        else:
            s += str(timings[k])
        ret.append(s)
    return "\n".join(ret)

