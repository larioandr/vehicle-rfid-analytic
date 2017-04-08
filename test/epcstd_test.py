import unittest
from model import epcstd


class TestDataTypes(unittest.TestCase):

    def test_divide_ratio_encoding(self):
        self.assertEqual(epcstd.DivideRatio.DR_8.code, "0")
        self.assertEqual(epcstd.DivideRatio.DR_643.code, "1")

    def test_divide_ratio_str(self):
        self.assertEqual(str(epcstd.DivideRatio.DR_8), '8')
        self.assertEqual(str(epcstd.DivideRatio.DR_643), '64/3')

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

    def test_session_str(self):
        self.assertEqual(str(epcstd.Session.S0).upper(), "S0")
        self.assertEqual(str(epcstd.Session.S1).upper(), "S1")
        self.assertEqual(str(epcstd.Session.S2).upper(), "S2")
        self.assertEqual(str(epcstd.Session.S3).upper(), "S3")

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

    def test_tag_encoding_str(self):
        self.assertEqual(str(epcstd.TagEncoding.FM0).upper(), "FM0")
        self.assertEqual(str(epcstd.TagEncoding.M2).upper(), "M2")
        self.assertEqual(str(epcstd.TagEncoding.M4).upper(), "M4")
        self.assertEqual(str(epcstd.TagEncoding.M8).upper(), "M8")

    def test_inventory_flag_encoding(self):
        self.assertEqual(epcstd.InventoryFlag.A.code, '0')
        self.assertEqual(epcstd.InventoryFlag.B.code, '1')

    def test_inventory_flag_str(self):
        self.assertEqual(str(epcstd.InventoryFlag.A).upper(), "A")
        self.assertEqual(str(epcstd.InventoryFlag.B).upper(), "B")

    def test_sel_flag_encoding(self):
        self.assertIn(epcstd.SelFlag.ALL.code, ['00', '01'])
        self.assertEqual(epcstd.SelFlag.NOT_SEL.code, '10')
        self.assertEqual(epcstd.SelFlag.SEL.code, '11')

    def test_sel_flag_str(self):
        self.assertEqual(str(epcstd.SelFlag.ALL).lower(), "all")
        self.assertEqual(str(epcstd.SelFlag.SEL).lower(), "sl")
        self.assertEqual(str(epcstd.SelFlag.NOT_SEL).lower(), "~sl")

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

    def test_command_code_str(self):
        self.assertEqual(str(epcstd.CommandCode.QUERY).lower(), "query")
        self.assertIn(str(epcstd.CommandCode.QUERY_REP).lower(),
                      ['query_rep', 'qrep', 'queryrep'])
        self.assertEqual(str(epcstd.CommandCode.ACK).lower(), 'ack')
        self.assertIn(str(epcstd.CommandCode.REQ_RN).lower(),
                      ['req_rn', 'reqrn'])
        self.assertEqual(str(epcstd.CommandCode.READ).lower(), 'read')


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

    def test_query_command_str(self):
        cmd = epcstd.Query(dr=epcstd.DivideRatio.DR_8,
                           m=epcstd.TagEncoding.FM0, trext=False,
                           sel=epcstd.SelFlag.ALL,
                           session=epcstd.Session.S0,
                           target=epcstd.InventoryFlag.A, q=13,
                           crc=0x1F)
        string = str(cmd)
        self.assertIn(str(epcstd.CommandCode.QUERY), string)
        self.assertIn(str(epcstd.DivideRatio.DR_8), string)
        self.assertIn(str(epcstd.TagEncoding.FM0), string)
        self.assertIn(str(epcstd.SelFlag.ALL), string)
        self.assertIn(str(epcstd.Session.S0), string)
        self.assertIn(str(epcstd.InventoryFlag.A), string)
        self.assertIn("13", string)
        self.assertIn("1F", string)

    def test_query_command_using_reader_params(self):
        #
        # 1) Setting some initial values for Query fields in readerParams
        #    and making sure they are passed to Query as default values
        #
        epcstd.readerParams.divide_ratio = epcstd.DivideRatio.DR_8
        epcstd.readerParams.tag_encoding = epcstd.TagEncoding.FM0
        epcstd.readerParams.sel = epcstd.SelFlag.SEL
        epcstd.readerParams.session = epcstd.Session.S0
        epcstd.readerParams.target = epcstd.InventoryFlag.A
        epcstd.readerParams.Q = 3
        epcstd.readerParams.trext = False

        query1 = epcstd.Query()

        def assert_query_params(query):
            self.assertEqual(query.dr, epcstd.readerParams.divide_ratio)
            self.assertEqual(query.m, epcstd.readerParams.tag_encoding)
            self.assertEqual(query.sel, epcstd.readerParams.sel)
            self.assertEqual(query.session, epcstd.readerParams.session)
            self.assertEqual(query.target, epcstd.readerParams.target)
            self.assertEqual(query.q, epcstd.readerParams.Q)
            self.assertEqual(query.trext, epcstd.readerParams.trext)

        assert_query_params(query1)

        #
        # 2) Altering values in readerParams and making sure they are
        #    passed to Query
        #
        epcstd.readerParams.divide_ratio = epcstd.DivideRatio.DR_643
        epcstd.readerParams.tag_encoding = epcstd.TagEncoding.M8
        epcstd.readerParams.sel = epcstd.SelFlag.NOT_SEL
        epcstd.readerParams.session = epcstd.Session.S3
        epcstd.readerParams.target = epcstd.InventoryFlag.B
        epcstd.readerParams.Q = 8
        epcstd.readerParams.trext = True

        query2 = epcstd.Query()

        assert_query_params(query2)

    def test_query_rep_command_encoding(self):
        cmd1 = epcstd.QueryRep(session=epcstd.Session.S0)
        self.assertEqual(cmd1.encode(), '0000')
        self.assertEqual(cmd1.bitlen, 4)
        cmd2 = epcstd.QueryRep(session=epcstd.Session.S3)
        self.assertEqual(cmd2.encode(), '0011')

    def test_query_rep_command_str(self):
        cmd = epcstd.QueryRep(session=epcstd.Session.S1)
        string = str(cmd)
        self.assertIn(str(epcstd.CommandCode.QUERY_REP), string)
        self.assertIn(str(epcstd.Session.S1), string)

    def test_query_rep_using_reader_params(self):
        def assert_fields_match_reader_params(query_rep):
            self.assertEqual(query_rep.session, epcstd.readerParams.session)

        # 1) Setting readerParams and checking they were passed to the
        #    command as the default params
        epcstd.readerParams.session = epcstd.Session.S0
        query_rep_1 = epcstd.QueryRep()
        assert_fields_match_reader_params(query_rep_1)

        # 2) Changing readerParams and checking the changed
        #    values were passed to new command as the default params
        epcstd.readerParams.session = epcstd.Session.S3
        query_rep_2 = epcstd.QueryRep()
        assert_fields_match_reader_params(query_rep_2)

    def test_ack_command_encoding(self):
        cmd1 = epcstd.Ack(rn=0x0000)
        self.assertEqual(cmd1.encode(), '010000000000000000')
        self.assertEqual(cmd1.bitlen, 18)
        cmd2 = epcstd.Ack(rn=0xFFFF)
        self.assertEqual(cmd2.encode(), '011111111111111111')

    def test_ack_command_str(self):
        cmd = epcstd.Ack(rn=0xAB)
        string = str(cmd)
        self.assertIn(str(epcstd.CommandCode.ACK), string)
        self.assertIn('0x00AB', string)

    def test_req_rn_command_encoding(self):
        cmd1 = epcstd.ReqRN(rn=0x0000, crc=0x0000)
        cmd2 = epcstd.ReqRN(rn=0xAAAA, crc=0x5555)
        self.assertEqual(cmd1.encode(),
                         '1100000100000000000000000000000000000000')
        self.assertEqual(cmd1.bitlen, 40)
        self.assertEqual(cmd2.encode(),
                         '1100000110101010101010100101010101010101')

    def test_req_rn_command_str(self):
        cmd1 = epcstd.ReqRN(rn=0x1234, crc=0xABCD)
        cmd2 = epcstd.ReqRN(rn=0xAABB, crc=0xCCDD)
        string1 = str(cmd1)
        string2 = str(cmd2)
        self.assertIn('0x1234', string1)
        self.assertIn('0xABCD', string1)
        self.assertIn('0xAABB', string2)
        self.assertIn('0xCCDD', string2)

    def test_read_command_encoding(self):
        cmd1 = epcstd.Read(bank=epcstd.MemoryBank.RESERVED, word_ptr=0,
                           word_count=0, rn=0x0000, crc=0x0000)
        cmd2 = epcstd.Read(bank=epcstd.MemoryBank.USER, word_ptr=0x80,
                           word_count=255, rn=0xAAAA, crc=0x5555)
        self.assertEqual(cmd1.encode(), '11000010' + '0' * 50)
        self.assertEqual(cmd1.bitlen, 58)
        self.assertEqual(cmd2.encode(), '11000010' + '11' + '1000000100000000'
                         + '1' * 8 + '1010' * 4 + '0101' * 4)

    def test_read_using_reader_params(self):
        def assert_fields_match_reader_params(cmd):
            assert isinstance(cmd, epcstd.Read)
            self.assertEqual(cmd.bank, epcstd.readerParams.read_default_bank)
            self.assertEqual(cmd.word_ptr,
                             epcstd.readerParams.read_default_word_ptr)
            self.assertEqual(cmd.word_count,
                             epcstd.readerParams.read_default_word_count)

        # 1) Setting readerParams and checking they were passed to the
        #    command as the default params
        epcstd.readerParams.read_default_bank = epcstd.MemoryBank.EPC
        epcstd.readerParams.read_default_word_ptr = 0
        epcstd.readerParams.read_default_word_count = 10
        cmd1 = epcstd.Read()
        assert_fields_match_reader_params(cmd1)

        # 2) Changing readerParams and checking the changed
        #    values were passed to new command as the default params
        epcstd.readerParams.read_default_bank = epcstd.MemoryBank.TID
        epcstd.readerParams.read_default_word_ptr = 5
        epcstd.readerParams.read_default_word_count = 23
        cmd2 = epcstd.Read()
        assert_fields_match_reader_params(cmd2)

    def test_read_command_str(self):
        cmd1 = epcstd.Read(bank=epcstd.MemoryBank.EPC, word_ptr=2,
                           word_count=5, rn=0xAABB, crc=0xCCDD)
        cmd2 = epcstd.Read(bank=epcstd.MemoryBank.TID, word_ptr=3,
                           word_count=1, rn=0xABCD, crc=0xEFEF)
        string1 = str(cmd1)
        string2 = str(cmd2)
        self.assertIn('EPC', string1.upper())
        self.assertIn('0x02', string1)
        self.assertIn('5', string1)
        self.assertIn('0xAABB', string1)
        self.assertIn('0xCCDD', string1)
        self.assertIn('TID', string2.upper())
        self.assertIn('0x03', string2)
        self.assertIn('1', string2)
        self.assertIn('0xABCD', string2)
        self.assertIn('0xEFEF', string2)


class TestReplies(unittest.TestCase):
    def test_to_bytes(self):
        self.assertEqual(epcstd.to_bytes('1122'), [0x11, 0x22])
        self.assertEqual(epcstd.to_bytes((0xAB,)), [0xAB])
        with self.assertRaises(ValueError):
            epcstd.to_bytes(0xAB)

    def test_query_reply_bitlen(self):
        msg = epcstd.QueryReply(rn=0x0000)
        self.assertEqual(msg.bitlen, 16)

    def test_query_reply_str(self):
        msg1 = epcstd.QueryReply(rn=0xABCD)
        msg2 = epcstd.QueryReply(rn=0x1122)
        string1 = str(msg1)
        string2 = str(msg2)
        self.assertIn('ABCD', string1.upper())
        self.assertNotIn('1122', string1)
        self.assertIn('1122', string2)
        self.assertNotIn('ABCD', string2.upper())

    def test_ack_reply_bitlen(self):
        msg1 = epcstd.AckReply(pc=0x0000, epc='0011223344556677', crc=0x0000)
        msg2 = epcstd.AckReply(pc=0x0000, epc='001122334455', crc=0x0000)
        msg3 = epcstd.AckReply(pc=0x0000, epc=[0x00, 0x11, 0x22], crc=0x0000)
        self.assertEqual(msg1.bitlen, 96)
        self.assertEqual(msg2.bitlen, 80)
        self.assertEqual(msg3.bitlen, 56)

    def test_ack_reply_str(self):
        msg1 = epcstd.AckReply(pc=0xABCD, epc='0011223344556677', crc=0x1234)
        msg2 = epcstd.AckReply(pc=0xDCBA, epc='001122334455', crc=0x4321)
        s1 = str(msg1)
        s2 = str(msg2)
        self.assertIn('ABCD', s1.upper())
        self.assertNotIn('DCBA', s1.upper())
        self.assertIn('1234', s1)
        self.assertNotIn('4321', s1)
        self.assertIn('0011223344556677', s1)
        self.assertIn('DCBA', s2.upper())
        self.assertIn('4321', s2)
        self.assertIn('001122334455', s2)
        self.assertNotIn('6677', s2)

    def test_req_rn_reply_bitlen(self):
        msg = epcstd.ReqRnReply(rn=0x0000, crc=0x0000)
        self.assertEqual(msg.bitlen, 32)

    def test_req_rn_reply_str(self):
        msg1 = epcstd.ReqRnReply(rn=0xABCD, crc=0x1234)
        msg2 = epcstd.ReqRnReply(rn=0xDCBA, crc=0x4321)
        s1 = str(msg1)
        s2 = str(msg2)
        self.assertIn('ABCD', s1.upper())
        self.assertIn('1234', s1)
        self.assertNotIn('DCBA', s1.upper())
        self.assertNotIn('4321', s1)
        self.assertIn('DCBA', s2.upper())
        self.assertIn('4321', s2)

    def test_read_reply_bitlen(self):
        msg1 = epcstd.ReadReply(data='00112233', rn=0x0000, crc=0x0000)
        msg2 = epcstd.ReadReply(data='001122334455', rn=0x0000, crc=0x0000)
        msg3 = epcstd.ReadReply(data=[0x00, 0x11], rn=0x0000, crc=0x0000)
        self.assertEqual(msg1.bitlen, 65)
        self.assertEqual(msg2.bitlen, 81)
        self.assertEqual(msg3.bitlen, 49)

    def test_read_reply_str(self):
        msg1 = epcstd.ReadReply(data='00112233', rn=0x1234, crc=0xABCD)
        msg2 = epcstd.ReadReply(data='AABBCC', rn=0x4321, crc=0xDCBA)
        s1 = str(msg1)
        s2 = str(msg2)
        self.assertIn('00112233', s1)
        self.assertIn('1234', s1)
        self.assertIn('ABCD', s1.upper())
        self.assertNotIn('AABBCC', s1.upper())
        self.assertNotIn('4321', s1)
        self.assertNotIn('DCBA', s1)
        self.assertIn('AABBCC', s2.upper())
        self.assertIn('4321', s2)
        self.assertIn('DCBA', s2.upper())


class TestReaderPreambles(unittest.TestCase):
    def test_reader_preamble_durations(self):
        p = epcstd.ReaderPreamble(tari=6.25e-6, rtcal=18.75e-6, trcal=56.25e-6)
        self.assertAlmostEqual(p.data0, p.tari, 9)
        self.assertAlmostEqual(p.delim, 12.5e-6, 9)
        self.assertAlmostEqual(p.data0, 6.25e-6, 9)
        self.assertAlmostEqual(p.data1, 12.5e-6, 9)
        self.assertAlmostEqual(p.rtcal, 18.75e-6, 9)
        self.assertAlmostEqual(p.trcal, 56.25e-6, 9)
        self.assertAlmostEqual(p.duration, 93.75e-6, 9)

    def test_reader_preamble_str(self):
        p = epcstd.ReaderPreamble(tari=12.5e-6, rtcal=33.45e-6, trcal=60.15e-6,
                                  delim=13.0e-6)
        s = str(p)
        self.assertIn("12.5", s)
        self.assertIn("33.45", s)
        self.assertIn("60.15", s)
        self.assertIn("13.0", s)

    def test_reader_sync_durations(self):
        sync = epcstd.ReaderSync(tari=12.5e-6, rtcal=31.25e-6, delim=13.0e-6)
        self.assertAlmostEqual(sync.tari, sync.data0, 9)
        self.assertAlmostEqual(sync.data0, 12.5e-6, 9)
        self.assertAlmostEqual(sync.data1, 18.75e-6, 9)
        self.assertAlmostEqual(sync.rtcal, 31.25e-6, 9)
        self.assertAlmostEqual(sync.delim, 13.0e-6)
        self.assertAlmostEqual(sync.duration, 56.75e-6, 9)

    def test_reader_sync_str(self):
        sync = epcstd.ReaderSync(tari=25e-6, rtcal=75e-6, delim=12.0e-6)
        s = str(sync)
        self.assertIn("12.0", s)
        self.assertIn("25.0", s)
        self.assertIn("75.0", s)


class TestTagPreambles(unittest.TestCase):
    def test_tag_FM0_preamble_bitlen_and_duration(self):
        short_preamble = epcstd.FM0Preamble(extended=False)
        long_preamble = epcstd.FM0Preamble(extended=True)
        self.assertEqual(short_preamble.bitlen, 6)
        self.assertEqual(long_preamble.bitlen, 18)
        self.assertAlmostEqual(short_preamble.get_duration(blf=320e3),
                               1.875e-5)
        self.assertAlmostEqual(long_preamble.get_duration(blf=320e3),
                               5.625e-5)
        self.assertAlmostEqual(short_preamble.get_duration(blf=40e3), 15e-5)
        self.assertAlmostEqual(long_preamble.get_duration(blf=40e3), 45e-5)

    def test_tag_miller_preamble_bitlen_and_duration(self):
        m2_short = epcstd.MillerPreamble(m=2, extended=False)
        m2_long = epcstd.MillerPreamble(m=2, extended=True)
        m4_short = epcstd.MillerPreamble(m=4)
        m8_long = epcstd.MillerPreamble(m=8, extended=True)
        self.assertEqual(m2_short.bitlen, 10)
        self.assertEqual(m2_long.bitlen, 22)
        self.assertEqual(m4_short.bitlen, 10)
        self.assertEqual(m8_long.bitlen, 22)
        self.assertAlmostEqual(m2_short.get_duration(blf=320e3), 6.25e-5)
        self.assertAlmostEqual(m2_long.get_duration(blf=320e3), 13.75e-5)
        self.assertAlmostEqual(m4_short.get_duration(blf=320e3), 12.5e-5)
        self.assertAlmostEqual(m8_long.get_duration(blf=320e3), 55e-5)
        self.assertAlmostEqual(m2_short.get_duration(blf=64e3), 31.25e-5)

    def test_tag_preamble_factory(self):
        fm0_preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.FM0)
        fm0_extended_preamble = epcstd.create_tag_preamble(
            epcstd.TagEncoding.FM0, True)
        m2_preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.M2)
        m4_preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.M2)
        m8_preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.M2)

        self.assertIsInstance(fm0_preamble, epcstd.FM0Preamble)
        self.assertIsInstance(fm0_extended_preamble, epcstd.FM0Preamble)
        self.assertIsInstance(m2_preamble, epcstd.MillerPreamble)
        self.assertIsInstance(m4_preamble, epcstd.MillerPreamble)
        self.assertIsInstance(m8_preamble, epcstd.MillerPreamble)
        self.assertEqual(fm0_preamble.bitlen, 6)
        self.assertEqual(fm0_extended_preamble.bitlen, 18)

    def test_tag_preamble_has_str(self):
        s1 = str(epcstd.FM0Preamble(True))
        s2 = str(epcstd.MillerPreamble(2, True))
        self.assertNotIn("0x", s1)
        self.assertNotIn("0x", s2)


class TestReaderFrames(unittest.TestCase):
    def setUp(self):
        # The following query will be encoded as 1000011011010001101010
        # number of 1s: 10, number of 0s: 12
        self.query = epcstd.Query(
            dr=epcstd.DivideRatio.DR_8, m=epcstd.TagEncoding.M8, trext=False,
            sel=epcstd.SelFlag.SEL, session=epcstd.Session.S1,
            target=epcstd.InventoryFlag.A, q=3, crc=0xAA)

        # The following QueryRep will be encoded as 0011
        self.query_rep = epcstd.QueryRep(session=epcstd.Session.S3)

        # Now we define a fast preamble, a slow preamble and a SYNC:
        self.fast_preamble = epcstd.ReaderPreamble(
            tari=6.25e-6, rtcal=18.75e-6, trcal=56.25e-6)
        self.slow_preamble = epcstd.ReaderPreamble(
            tari=25e-6, rtcal=75e-6, trcal=225e-6)
        self.fast_sync = epcstd.ReaderSync(tari=12.5e-6, rtcal=31.25e-6)
        self.slow_sync = epcstd.ReaderSync(tari=25e-6, rtcal=62.5e-6)

    def test_query_frame_fast_preamble_duration(self):
        f = epcstd.ReaderFrame(preamble=self.fast_preamble, command=self.query)
        self.assertAlmostEqual(f.duration, 293.75e-6, 9)
        self.assertAlmostEqual(f.body_duration, 200e-6, 9)

    def test_query_frame_slow_preamble_duration(self):
        f = epcstd.ReaderFrame(preamble=self.slow_preamble, command=self.query)
        self.assertAlmostEqual(f.duration, 1137.5e-6, 9)
        self.assertAlmostEqual(f.body_duration, 800.0e-6, 9)

    def test_query_rep_frame_fast_sync_duration(self):
        f = epcstd.ReaderFrame(preamble=self.fast_sync, command=self.query_rep)
        self.assertAlmostEqual(f.body_duration, 62.5e-6, 9)
        self.assertAlmostEqual(f.duration, 118.75e-6, 9)

    def test_query_rep_frame_slow_sync_duration(self):
        f = epcstd.ReaderFrame(preamble=self.slow_sync, command=self.query_rep)
        self.assertAlmostEqual(f.body_duration, 125e-6, 9)
        self.assertAlmostEqual(f.duration, 225e-6, 9)


class TestTagFrames(unittest.TestCase):
    def setUp(self):
        self.ack_reply = epcstd.AckReply(epc="ABCDEF01", pc=0, crc=0)
        self.rn16_reply = epcstd.QueryReply(rn=0)
        self.slow_blf = 120e3
        self.fast_blf = 640e3

    def test_tag_fm0_frame_duration(self):
        pn = epcstd.create_tag_preamble(epcstd.TagEncoding.FM0, extended=False)
        pe = epcstd.create_tag_preamble(epcstd.TagEncoding.FM0, extended=True)

        ne_ack_frame = epcstd.TagFrame(preamble=pn, reply=self.ack_reply)
        ex_ack_frame = epcstd.TagFrame(preamble=pe, reply=self.ack_reply)
        ex_rn16_frame = epcstd.TagFrame(preamble=pe, reply=self.rn16_reply)

        self.assertAlmostEqual(ne_ack_frame.get_body_duration(self.slow_blf),
                               0.00053333333, 8)
        self.assertAlmostEqual(ne_ack_frame.get_duration(self.slow_blf),
                               0.00059166667, 8)
        self.assertAlmostEqual(ex_ack_frame.get_body_duration(self.slow_blf),
                               0.00053333333, 8)
        self.assertAlmostEqual(ex_ack_frame.get_duration(self.slow_blf),
                               0.00069166667, 8)
        self.assertAlmostEqual(ex_rn16_frame.get_body_duration(self.slow_blf),
                               0.00013333333, 8)
        self.assertAlmostEqual(ex_rn16_frame.get_duration(self.slow_blf),
                               0.00029166667, 8)
        self.assertAlmostEqual(ex_rn16_frame.get_body_duration(self.fast_blf),
                               2.5e-05, 8)
        self.assertAlmostEqual(ex_rn16_frame.get_duration(self.fast_blf),
                               5.46875e-05)

    def test_tag_m2_frame_duration(self):
        preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.M2, False)
        ext_preamble = epcstd.create_tag_preamble(epcstd.TagEncoding.M2, True)

        frame = epcstd.TagFrame(preamble, self.rn16_reply)
        ext_frame = epcstd.TagFrame(ext_preamble, self.rn16_reply)

        self.assertAlmostEqual(frame.get_body_duration(self.slow_blf),
                               0.0002666666666666667, 8)
        self.assertAlmostEqual(frame.get_duration(self.slow_blf),
                               0.00045, 8)
        self.assertAlmostEqual(frame.get_body_duration(self.fast_blf),
                               5e-05, 8)
        self.assertAlmostEqual(frame.get_duration(self.fast_blf),
                               8.4375e-05, 8)
        self.assertAlmostEqual(ext_frame.get_body_duration(self.slow_blf),
                               frame.get_body_duration(self.slow_blf), 8)
        self.assertAlmostEqual(ext_frame.get_duration(self.slow_blf),
                               0.00065, 8)


class TestFrameAccessors(unittest.TestCase):

    def setUp(self):
        self.slow_tari = 12.5e-6
        self.slow_rtcal = 37.5e-6
        self.slow_trcal = 112.5e-6
        self.fast_tari = 6.25e-6
        self.fast_rtcal = 15.625e-6
        self.fast_trcal = 46.875e-6

        self.slow_sync = epcstd.ReaderSync(self.slow_tari, self.slow_rtcal)
        self.fast_sync = epcstd.ReaderSync(self.fast_tari, self.fast_rtcal)
        self.slow_preamble = epcstd.ReaderPreamble(
            self.slow_tari, self.slow_rtcal, self.slow_trcal)
        self.fast_preamble = epcstd.ReaderPreamble(
            self.fast_tari, self.fast_rtcal, self.fast_trcal)

        self.ack = epcstd.Ack(0xAAAA)
        self.query_rep = epcstd.QueryRep(epcstd.Session.S1)
        self.query = epcstd.Query()

        self.slow_ack_frame = epcstd.ReaderFrame(self.slow_sync, self.ack)
        self.fast_ack_frame = epcstd.ReaderFrame(self.fast_sync, self.ack)
        self.slow_query_rep_frame = epcstd.ReaderFrame(
            self.slow_sync, self.query_rep)
        self.fast_query_rep_frame = epcstd.ReaderFrame(
            self.fast_sync, self.query_rep)
        self.slow_query_frame = epcstd.ReaderFrame(
            self.slow_preamble, self.query)
        self.fast_query_frame = epcstd.ReaderFrame(
            self.fast_preamble, self.query)

    def test_get_reader_frame_duration_return_equals_sync_frame_getter(self):
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal, command=self.ack),
            self.slow_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal, command=self.ack),
            self.fast_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal,
                command=self.query_rep),
            self.slow_query_rep_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal,
                command=self.query_rep),
            self.fast_query_rep_frame.duration, 8)

    def test_get_reader_frame_duration_return_equals_query_frame_getter(self):
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal,
                trcal=self.slow_trcal, command=self.query),
            self.slow_query_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal,
                trcal=self.fast_trcal, command=self.query),
            self.fast_query_frame.duration, 8)

    def test_get_reader_frame_duration_recognizes_encoded_sync_commands(self):
        encoded_ack = self.ack.encode()
        encoded_query_rep = self.query_rep.encode()
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal,
                command=encoded_ack),
            self.slow_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal,
                command=encoded_ack),
            self.fast_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal,
                command=encoded_query_rep),
            self.slow_query_rep_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal,
                command=encoded_query_rep),
            self.fast_query_rep_frame.duration, 8)

    def test_get_reader_frame_duration_recognizes_encoded_query_command(self):
        encoded_query = self.query.encode()
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.slow_tari, rtcal=self.slow_rtcal,
                trcal=self.slow_trcal, command=encoded_query),
            self.slow_query_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(
                tari=self.fast_tari, rtcal=self.fast_rtcal,
                trcal=self.fast_trcal, command=encoded_query),
            self.fast_query_frame.duration, 8)

    def test_get_reader_frame_duration_uses_default_reader_params(self):
        #
        # 1) Setting readerParams to slow frame type
        #
        epcstd.readerParams.tari = self.slow_tari
        epcstd.readerParams.rtcal = self.slow_rtcal
        epcstd.readerParams.trcal = self.slow_trcal
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.ack),
            self.slow_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.query_rep),
            self.slow_query_rep_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.query),
            self.slow_query_frame.duration, 8)

        #
        # 1) Setting readerParams to fast frame type
        #
        epcstd.readerParams.tari = self.fast_tari
        epcstd.readerParams.rtcal = self.fast_rtcal
        epcstd.readerParams.trcal = self.fast_trcal
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.ack),
            self.fast_ack_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.query_rep),
            self.fast_query_rep_frame.duration, 8)
        self.assertAlmostEqual(
            epcstd.get_reader_frame_duration(self.query),
            self.fast_query_frame.duration, 8)

