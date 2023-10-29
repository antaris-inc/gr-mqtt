# gr-mqtt

This is an out-of-tree (OTT) gnuradio module that provides blocks for adapting flowgraphs to MQTT brokers.
The blocks are in the `mqtt` group, named `mqtt_source` and `mqtt_sink`.
In both cases, MQTT clients connect to an external MQTT broker to transfer messages using a basic JSON structure:

```
{
  "message": <base64-encoded message>
}
```

## Installation

```
mkdir build
cd build
cmake -DGR_PYTHON_DIR=/usr/lib64/python3.10/site-packages/ ../
make
sudo make install
```

Also ensure that the python requirements (documented in requirements.txt) are available to the gnuradio service.

## Development

This module was generated using `gr_modtool`, which means there is a ton of unused scaffolding code here.
Most ongoing development will focus on files in two locations:

* The actual python code implementing the gnuradio blocks is located in files prefixed with `mqtt_` in `./python/mqtt/`
* The GRC configs located in `./grc`, which allow usage of the blocks in GNU Radio Companion (GRC)
