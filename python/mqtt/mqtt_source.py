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


class mqtt_source(gr.sync_block):
    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_DELAY = 60

    def __init__(self, host, port, topic, username, password):
        gr.sync_block.__init__(self,
            name="mqtt_source",
            in_sig=None,
            out_sig=None)
        self.logger = gr.logger(self.alias())
        self.host = host
        self.port = port
        self.topic = topic

        self.message_port_register_out(pmt.intern('message'))


        self.client = paho_mqtt.Client()
        self.client.username_pw_set(username, password)

        #NOTE(bcwaldon): temporary until we have real TLS config
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.mqtt_connect_fail
        self.client.on_disconnect = self.mqtt_disconnect
        self.client.connect(host, port, 30)
        self.client.loop_start()
        self.client.on_message = self.handle

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0 and client.is_connected():
            self.logger.info(f"MQTT source connected to MQTT broker: {self.host}:{self.port}")
            result, mid = client.subscribe(self.topic)
            if result == paho_mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"MQTT source subscribed to topic: {self.topic}")
            else:
                print(f"Subscription failed with error code: {result.name}") 
        else:
            self.logger(f'Failed to connect, return code {rc}')

    def handle(self, _client, _userdata, mqtt_msg):
        env = json.loads(mqtt_msg.payload)
        b64_msg = env["message"]
        raw_msg = bytearray(base64.b64decode(b64_msg))

        self.message_port_pub(
            pmt.intern("message"),
            pmt.init_u8vector(len(raw_msg), raw_msg)
        )

    def mqtt_connect_fail(self, client, userdata, rc):
        try:
            reason_text = paho_mqtt.error_string(rc) 
        except ValueError:
            reason_text = f"Unknown reason code: {rc}"
        raise MQTTConnectionError(f"Disconnected from MQTT broker: {reason_text}")
    
    def mqtt_disconnect(self, client, userdata, rc):
        self.logger.info(f"Disconnected with result code: {paho_mqtt.error_string(rc)}" )
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY
        while True:
            self.logger.info(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                self.logger.info("MQTT source reconnected successfully!")
                return
            except Exception as err:
                self.logger.error(f"MQTT source reconnect failed. Retrying. previous error: {err}")

            reconnect_delay *= self.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, self.MAX_RECONNECT_DELAY)
