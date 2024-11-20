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
import ssl
from .mqtt_exceptions import MQTTConnectionError, MQTTDisconnectError


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

        #NOTE(bcwaldon): temporary until we have real TLS config
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.on_connect_fail = self.mqtt_connect_fail
        self.client.on_disconnect = self.mqtt_disconnect

        self.client.connect(host, port, 30)
        self.client.loop_start()            

    def handle(self, msg):
        raw_msg = pmt.to_python(msg).tobytes()
        b64_msg = base64.b64encode(raw_msg).decode('ascii')
        env = {"message" : b64_msg}
        enc = json.dumps(env)
        self.client.publish(self.topic, enc)
    
    def mqtt_connect_fail(self, client, userdata, rc):
        try:
            reason_text = paho_mqtt.error_string(rc) 
        except ValueError:
            reason_text = f"Unknown reason code: {rc}"
        raise MQTTConnectionError(f"Disconnected from MQTT broker: {reason_text}")
    
    def mqtt_disconnect(self, client, userdata, rc):
        try:
            reason_text = paho_mqtt.error_string(rc) 
        except ValueError:
            reason_text = f"Unknown reason code: {rc}"
        raise MQTTDisconnectError(f"Disconnected from MQTT broker: {reason_text}")
