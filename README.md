# gr-mqtt

This is an out-of-tree (OTT) gnuradio module that provides blocks for adapting flowgraphs to MQTT brokers.

## Quickstart

If you need to make simple changes, you should just focus on the files prefixed with `mqtt_` in `./python/mqtt/` and the GRC configurations in `./grc`.

## Installation

```
mkdir build
cd build
cmake -DGR_PYTHON_DIR=/usr/lib64/python3.10/site-packages/ ../
make
sudo make install
```

Also ensure that the python requirements (documented in requirements.txt) are available to the gnuradio service.
