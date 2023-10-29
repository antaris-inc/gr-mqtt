#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Antaris, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import base64
import json

import paho.mqtt.client as paho_mqtt
import pmt
from gnuradio import gr


class mqtt_sink(gr.sync_block):

    def __init__(self, host, port, topic, username, password):
        gr.sync_block.__init__(self,
            name="mqtt_sink",
            in_sig=None,
            out_sig=None)

        self.topic = topic

        self.message_port_register_in(pmt.intern('message'))
        self.set_msg_handler(pmt.intern('message'), self.handle)

        self.client = paho_mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.connect(host, port, 30)
        self.client.loop_start()

    def handle(self, msg):
        raw_msg = pmt.to_python(msg).tobytes()
        b64_msg = base64.b64encode(raw_msg).decode('ascii')
        env = {"message" : b64_msg}
        enc = json.dumps(env)
        self.client.publish(self.topic, enc)
