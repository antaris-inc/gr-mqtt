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


class mqtt_source(gr.sync_block):

    def __init__(self, host, port, topic, username, password):
        gr.sync_block.__init__(self,
            name="mqtt_source",
            in_sig=None,
            out_sig=None)

        self.host = host
        self.port = port
        self.topic = topic

        self.message_port_register_out(pmt.intern('message'))

        self.client = paho_mqtt.Client()
        self.client.username_pw_set(username, password)

        #NOTE(bcwaldon): temporary until we have real TLS config
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        self.client.connect(host, port, 30)
        self.client.loop_start()

        self.client.on_message = self.handle
        self.client.subscribe(topic)

    def handle(self, _client, _userdata, mqtt_msg):
        env = json.loads(mqtt_msg.payload)
        b64_msg = env["message"]
        raw_msg = bytearray(base64.b64decode(b64_msg))

        self.message_port_pub(
            pmt.intern("message"),
            pmt.init_u8vector(len(raw_msg), raw_msg)
        )
