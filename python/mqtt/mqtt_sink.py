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
import time
from .mqtt_exceptions import MQTTConnectionError, MQTTDisconnectError


class mqtt_sink(gr.sync_block):
    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_DELAY = 60

    def __init__(self, host, port, topic, username, password):
        gr.sync_block.__init__(self,
            name="mqtt_sink",
            in_sig=None,
            out_sig=None)
        self.logger = gr.logger(self.alias())
        self.host = host
        self.port = port
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
        self.logger.info(f"Disconnected with result code: {paho_mqtt.error_string(rc)}" )
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY
        while 1 > 0:
            self.logger.info(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                self.logger.info("MQTT sink reconnected successfully!")
                return
            except Exception as err:
                self.logger.error(f"MQTT sink reconnect failed. Retrying. previous error: {err}")

            reconnect_delay *= self.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, self.MAX_RECONNECT_DELAY)
