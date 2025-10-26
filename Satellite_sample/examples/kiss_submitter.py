#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: KISS client telemetry submitter
# Author: Daniel Estevez
# Description: KISS client telemetry submitter
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks, gr
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import network
import satellites
import threading



class kiss_submitter(gr.top_block, Qt.QWidget):

    def __init__(self, callsign='', host='localhost', latitude=0, longitude=0, norad=0, port='8001', recstart=''):
        gr.top_block.__init__(self, "KISS client telemetry submitter", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("KISS client telemetry submitter")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "kiss_submitter")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.callsign = callsign
        self.host = host
        self.latitude = latitude
        self.longitude = longitude
        self.norad = norad
        self.port = port
        self.recstart = recstart

        ##################################################
        # Blocks
        ##################################################

        self.satellites_print_timestamp_0 = satellites.print_timestamp('%Y-%m-%d %H:%M:%S', True)
        self.satellites_pdu_to_kiss_0 = satellites.pdu_to_kiss(control_byte = True, include_timestamp = False)
        self.satellites_kiss_to_pdu_0 = satellites.kiss_to_pdu(True)
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_1 = network.socket_pdu('TCP_SERVER', 'localhost', '52002', 10000, True)
        self.network_socket_pdu_0 = network.socket_pdu('TCP_CLIENT', host, port, 10000, False)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.satellites_kiss_to_pdu_0, 'out'), (self.satellites_pdu_to_kiss_0, 'in'))
        self.msg_connect((self.satellites_kiss_to_pdu_0, 'out'), (self.satellites_print_timestamp_0, 'in'))
        self.msg_connect((self.satellites_pdu_to_kiss_0, 'out'), (self.network_socket_pdu_1, 'pdus'))
        self.msg_connect((self.satellites_print_timestamp_0, 'out'), (self.blocks_message_debug_0, 'print_pdu'))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.satellites_kiss_to_pdu_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "kiss_submitter")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_callsign(self):
        return self.callsign

    def set_callsign(self, callsign):
        self.callsign = callsign

    def get_host(self):
        return self.host

    def set_host(self, host):
        self.host = host

    def get_latitude(self):
        return self.latitude

    def set_latitude(self, latitude):
        self.latitude = latitude

    def get_longitude(self):
        return self.longitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def get_norad(self):
        return self.norad

    def set_norad(self, norad):
        self.norad = norad

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_recstart(self):
        return self.recstart

    def set_recstart(self, recstart):
        self.recstart = recstart



def argument_parser():
    description = 'KISS client telemetry submitter'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--callsign", dest="callsign", type=str, default='',
        help="Set your callsign [default=%(default)r]")
    parser.add_argument(
        "--host", dest="host", type=str, default='localhost',
        help="Set Host [default=%(default)r]")
    parser.add_argument(
        "--latitude", dest="latitude", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set latitude (format 00.000 or -00.000) [default=%(default)r]")
    parser.add_argument(
        "--longitude", dest="longitude", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set longitude (format 00.000 or -00.000) [default=%(default)r]")
    parser.add_argument(
        "--norad", dest="norad", type=intx, default=0,
        help="Set NORAD ID [default=%(default)r]")
    parser.add_argument(
        "-p", "--port", dest="port", type=str, default='8001',
        help="Set Port [default=%(default)r]")
    parser.add_argument(
        "--recstart", dest="recstart", type=str, default='',
        help="Set start of recording, if processing a recording (format YYYY-MM-DD HH:MM:SS) [default=%(default)r]")
    return parser


def main(top_block_cls=kiss_submitter, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(callsign=options.callsign, host=options.host, latitude=options.latitude, longitude=options.longitude, norad=options.norad, port=options.port, recstart=options.recstart)

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
