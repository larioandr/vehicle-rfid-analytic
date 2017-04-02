from enum import Enum
import collections


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
    def __init__(self, dr=DivideRatio.DR_8, m=TagEncoding.FM0, trext=False,
                 sel=SelFlag.ALL, session=Session.S0, target=InventoryFlag.A,
                 q=0, crc=0x00):
        super().__init__(CommandCode.QUERY)
        self.dr = dr
        self.m = m
        self.trext = trext
        self.sel = sel
        self.session = session
        self.target = target
        self.q = q
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
    def __init__(self, session=Session.S0):
        super().__init__(CommandCode.QUERY_REP)
        self.session = session

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
    def __init__(self, bank=MemoryBank.RESERVED, word_ptr=0, word_count=0,
                 rn=0x0000, crc=0x0000):
        super().__init__(CommandCode.READ)
        self.bank = bank
        self.word_ptr = word_ptr
        self.word_count = word_count
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
# Reader frames
#######################################################################
#

#
#######################################################################
# Tag replies
#######################################################################
#
class Reply:
    def __init__(self):
        super().__init__()

    @property
    def bitlen(self):
        raise NotImplementedError()


class QueryReply(Reply):
    def __init__(self, rn=0x0000):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
        self.rn = rn
        self.crc = crc

    @property
    def bitlen(self):
        return 32

    def __str__(self):
        return "Reply{{RN(0x{o.rn:04X}),CRC(0x{o.crc:04X})}}".format(o=self)


class ReadReply(Reply):
    def __init__(self, data="", rn=0x0000, crc=0x0000, header=False):
        super().__init__()
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
