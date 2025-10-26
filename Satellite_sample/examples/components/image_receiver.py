#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Image receiver component example
# Author: Daniel Estevez
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import satellites.components.datasinks
import satellites.components.transports
import satellites.core
import threading




class image_receiver(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Image receiver component example", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 48000

        ##################################################
        # Blocks
        ##################################################

        self.satellites_satellite_decoder_0 = satellites.core.gr_satellites_flowgraph(name = 'LilacSat-1', samp_rate = samp_rate, grc_block = True, iq = False, options = "")
        self.satellites_kiss_transport_0 = satellites.components.transports.kiss_transport(control_byte=False, options="")
        self.satellites_image_receiver_0 = satellites.components.datasinks.file_receiver('by70_1', '/tmp/', True, display=True, fullscreen=True, options="")
        self.blocks_wavfile_source_0 = blocks.wavfile_source('../../satellite-recordings/lilacsat1-image.wav', False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.satellites_kiss_transport_0, 'out'), (self.satellites_image_receiver_0, 'in'))
        self.msg_connect((self.satellites_satellite_decoder_0, 'out'), (self.satellites_kiss_transport_0, 'in'))
        self.connect((self.blocks_throttle_0, 0), (self.satellites_satellite_decoder_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_throttle_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)




def main(top_block_cls=image_receiver, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()
