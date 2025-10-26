#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Variable Length Packet Test
# Description: A simpmle test case of ASM + variable length packets
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
import satellites
import threading




class rx_asmgolay_vector(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Variable Length Packet Test", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################

        self.satellites_varlen_packet_tagger_1 = satellites.varlen_packet_tagger('syncword', 'packet_len', 55, (255*8), int(gr.GR_MSB_FIRST), True)
        self.satellites_varlen_packet_tagger_1.set_max_output_buffer(40)
        self.pdu_tagged_stream_to_pdu_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.digital_correlate_access_code_tag_xx_0 = digital.correlate_access_code_tag_bb('10010011000010110101000111011110', 6, 'syncword')
        self.digital_additive_scrambler_bb_0_0_0 = digital.additive_scrambler_bb(0xA9, 0xff, 7, count=0, bits_per_byte=1, reset_tag_key="packet_len")
        self.blocks_vector_source_x_0_0_0 = blocks.vector_source_b([1,0,0,1,0,0,1,1,0,0,0,0,1,0,1,1,0,1,0,1,0,0,0,1,1,1,0,1,1,1,1,0,0,1,0,1,1,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], False, 1, [])
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.blocks_tagged_stream_multiply_length_0 = blocks.tagged_stream_multiply_length(gr.sizeof_char*1, 'packet_len', (1/8.0))
        self.blocks_tag_debug_0_0_0 = blocks.tag_debug(gr.sizeof_char*1, 'T1', "")
        self.blocks_tag_debug_0_0_0.set_display(True)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0, 'pdus'), (self.blocks_message_debug_0, 'print_pdu'))
        self.connect((self.blocks_tagged_stream_multiply_length_0, 0), (self.pdu_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.blocks_tagged_stream_multiply_length_0, 0))
        self.connect((self.blocks_vector_source_x_0_0_0, 0), (self.digital_correlate_access_code_tag_xx_0, 0))
        self.connect((self.digital_additive_scrambler_bb_0_0_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0, 0), (self.satellites_varlen_packet_tagger_1, 0))
        self.connect((self.satellites_varlen_packet_tagger_1, 0), (self.blocks_tag_debug_0_0_0, 0))
        self.connect((self.satellites_varlen_packet_tagger_1, 0), (self.digital_additive_scrambler_bb_0_0_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate




def main(top_block_cls=rx_asmgolay_vector, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
