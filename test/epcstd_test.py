import unittest
from model import epcstd


class TestDataTypes(unittest.TestCase):

    def test_divide_ratio_encoding(self):
        self.assertEqual(epcstd.DivideRatio.DR_8.code, "0")
        self.assertEqual(epcstd.DivideRatio.DR_643.code, "1")

    def test_divide_ratio_eval(self):
        self.assertAlmostEqual(epcstd.DivideRatio.DR_8.eval(), 8.0)
        self.assertAlmostEqual(epcstd.DivideRatio.DR_643.eval(), 64.0/3)

    def test_session_encoding(self):
        self.assertEqual(epcstd.Session.S0.code, "00")
        self.assertEqual(epcstd.Session.S1.code, "01")
        self.assertEqual(epcstd.Session.S2.code, "10")
        self.assertEqual(epcstd.Session.S3.code, "11")

    def test_session_number(self):
        self.assertEqual(epcstd.Session.S0.index, 0)
        self.assertEqual(epcstd.Session.S1.index, 1)
        self.assertEqual(epcstd.Session.S2.index, 2)
        self.assertEqual(epcstd.Session.S3.index, 3)

    def test_tag_encoding_encoding(self):
        self.assertEqual(epcstd.TagEncoding.FM0.code, '00')
        self.assertEqual(epcstd.TagEncoding.M2.code, '01')
        self.assertEqual(epcstd.TagEncoding.M4.code, '10')
        self.assertEqual(epcstd.TagEncoding.M8.code, '11')

    def test_tag_encoding_symbols_per_bit(self):
        self.assertEqual(epcstd.TagEncoding.FM0.symbols_per_bit, 1)
        self.assertEqual(epcstd.TagEncoding.M2.symbols_per_bit, 2)
        self.assertEqual(epcstd.TagEncoding.M4.symbols_per_bit, 4)
        self.assertEqual(epcstd.TagEncoding.M8.symbols_per_bit, 8)

    def test_inventory_flag_encoding(self):
        self.assertEqual(epcstd.InventoryFlag.A.code, '0')
        self.assertEqual(epcstd.InventoryFlag.B.code, '1')

    def test_sel_flag_encoding(self):
        self.assertIn(epcstd.SelFlag.ALL.code, ['00', '01'])
        self.assertEqual(epcstd.SelFlag.NOT_SEL.code, '10')
        self.assertEqual(epcstd.SelFlag.SEL.code, '11')

    def test_memory_bank_encoding(self):
        self.assertEqual(epcstd.MemoryBank.RESERVED.code, '00')
        self.assertEqual(epcstd.MemoryBank.EPC.code, '01')
        self.assertEqual(epcstd.MemoryBank.TID.code, '10')
        self.assertEqual(epcstd.MemoryBank.USER.code, '11')

    def test_command_code_encoding(self):
        self.assertEqual(epcstd.CommandCode.QUERY.code, '1000')
        self.assertEqual(epcstd.CommandCode.QUERY_REP.code, '00')
        self.assertEqual(epcstd.CommandCode.ACK.code, '01')
        self.assertEqual(epcstd.CommandCode.REQ_RN.code, '11000001')
        self.assertEqual(epcstd.CommandCode.READ.code, '11000010')


class TestEncodingFunctions(unittest.TestCase):

    def test_encode_bool(self):
        self.assertEqual(epcstd.encode_bool(True), '1')
        self.assertEqual(epcstd.encode_bool(False), '0')

    def test_encode_int(self):
        self.assertEqual(epcstd.encode_int(0, 4), '0000')
        self.assertEqual(epcstd.encode_int(0xF, 4), '1111')
        self.assertEqual(epcstd.encode_byte(0xA5), '10100101')
        self.assertEqual(epcstd.encode_word(0xAB3C), '1010101100111100')

    def test_ebv(self):
        self.assertEqual(epcstd.encode_ebv(0), '00000000')
        self.assertEqual(epcstd.encode_ebv(1), '00000001')
        self.assertEqual(epcstd.encode_ebv(127), '01111111')
        self.assertEqual(epcstd.encode_ebv(128), '1000000100000000')
        self.assertEqual(epcstd.encode_ebv(16383), '1111111101111111')
        self.assertEqual(epcstd.encode_ebv(16384), '100000011000000000000000')


class TestCommands(unittest.TestCase):

    def test_query_command_encoding(self):
        cmd1 = epcstd.Query(dr=epcstd.DivideRatio.DR_8,
                            m=epcstd.TagEncoding.FM0, trext=False,
                            sel=epcstd.SelFlag.ALL,
                            session=epcstd.Session.S0,
                            target=epcstd.InventoryFlag.A, q=0,
                            crc=0x00)
        self.assertEqual(cmd1.encode(), '1000000000000000000000')
        self.assertEqual(cmd1.bitlen, 22)
        cmd2 = epcstd.Query(dr=epcstd.DivideRatio.DR_643,
                            m=epcstd.TagEncoding.M8, trext=True,
                            sel=epcstd.SelFlag.SEL,
                            session=epcstd.Session.S3,
                            target=epcstd.InventoryFlag.B, q=6,
                            crc=0x0B)
        self.assertEqual(cmd2.encode(), '1000111111111011001011')

    def test_query_rep_command_encoding(self):
        cmd1 = epcstd.QueryRep(session=epcstd.Session.S0)
        self.assertEqual(cmd1.encode(), '0000')
        self.assertEqual(cmd1.bitlen, 4)
        cmd2 = epcstd.QueryRep(session=epcstd.Session.S3)
        self.assertEqual(cmd2.encode(), '0011')

    def test_ack_command_encoding(self):
        cmd1 = epcstd.Ack(rn=0x0000)
        self.assertEqual(cmd1.encode(), '010000000000000000')
        self.assertEqual(cmd1.bitlen, 18)
        cmd2 = epcstd.Ack(rn=0xFFFF)
        self.assertEqual(cmd2.encode(), '011111111111111111')

    def test_req_rn_command_encoding(self):
        cmd1 = epcstd.ReqRN(rn=0x0000, crc=0x0000)
        self.assertEqual(cmd1.encode(),
                         '1100000100000000000000000000000000000000')
        self.assertEqual(cmd1.bitlen, 40)
        cmd2 = epcstd.ReqRN(rn=0xAAAA, crc=0x5555)
        self.assertEqual(cmd2.encode(),
                         '1100000110101010101010100101010101010101')

    def test_read_command_encoding(self):
        cmd1 = epcstd.Read(bank=epcstd.MemoryBank.RESERVED, word_ptr=0,
                           word_count=0, rn=0x0000, crc=0x0000)
        self.assertEqual(cmd1.encode(), '11000010' + '0' * 50)
        self.assertEqual(cmd1.bitlen, 58)
        cmd2 = epcstd.Read(bank=epcstd.MemoryBank.USER, word_ptr=0x80,
                           word_count=255, rn=0xAAAA, crc=0x5555)
        self.assertEqual(cmd2.encode(), '11000010' + '11' + '1000000100000000'
                         + '1' * 8 + '1010' * 4 + '0101' * 4)
