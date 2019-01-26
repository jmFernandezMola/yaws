#!/usr/bin/env python
import bme680
import time

def initSensor():
  try:
      sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
  except IOError:
      sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

  # These calibration data can safely be commented
  # out, if desired.

  print('Calibration data:')
  for name in dir(sensor.calibration_data):

      if not name.startswith('_'):
          value = getattr(sensor.calibration_data, name)

          if isinstance(value, int):
              print('{}: {}'.format(name, value))

  # These oversampling settings can be tweaked to
  # change the balance between accuracy and noise in
  # the data.

  sensor.set_humidity_oversample(bme680.OS_2X)
  sensor.set_pressure_oversample(bme680.OS_4X)
  sensor.set_temperature_oversample(bme680.OS_8X)
  sensor.set_filter(bme680.FILTER_SIZE_3)
  sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
  
  print('\n\nInitial reading:')
  for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
      print('{}: {}'.format(name, value))
  return(sensor)
      
def readBme680(sensor):
  if sensor.get_sensor_data():
    return([sensor.data.temperature, sensor.data.humidity, sensor.data.pressure])
