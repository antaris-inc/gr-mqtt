find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_MQTT gnuradio-mqtt)

FIND_PATH(
    GR_MQTT_INCLUDE_DIRS
    NAMES gnuradio/mqtt/api.h
    HINTS $ENV{MQTT_DIR}/include
        ${PC_MQTT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_MQTT_LIBRARIES
    NAMES gnuradio-mqtt
    HINTS $ENV{MQTT_DIR}/lib
        ${PC_MQTT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-mqttTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_MQTT DEFAULT_MSG GR_MQTT_LIBRARIES GR_MQTT_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_MQTT_LIBRARIES GR_MQTT_INCLUDE_DIRS)
