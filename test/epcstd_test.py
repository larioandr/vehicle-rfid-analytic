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
