#!/usr/bin/env python
import bme680
import time
import datetime
from plotDataEInk import plotData 
from statistics import mean 
from rfc3339 import rfc3339 
import json

SAMPLE_EVERY_SECONDS = 10
REGISTERS_TO_KEEP = 720
TEMPERATURE_HYSTERESIS = 0.2
PRESSURE_HYSTERESIS = 0.05
RELATIVE_HUMIDITY_HYSTERESIS = 0.5
DISPLAY_EVERY_X_SAMPLES = 60
DATA_BASE_NAME = 'weatherDataBase'

temp_table = [0]*REGISTERS_TO_KEEP
hum_table = [0]*REGISTERS_TO_KEEP
pres_table = [0]*REGISTERS_TO_KEEP
current_index = 0
temp_tendency = " ="
hum_tendency = " ="
pres_tendency = " ="
first_data_available = False

#Init database
time.sleep(30) #Wait for global initialization
from influxdb import InfluxDBClient
try:
	client = InfluxDBClient(host='localhost', port=8086)
except:
	raise NameError('The service is not running! -> sudo service influxdb start')

dataBaseExistance = False
for elements in client.get_list_database():
    if DATA_BASE_NAME in elements["name"]:
	dataBaseExistance = True

if not dataBaseExistance:
    client.create_database(DATA_BASE_NAME)
    print "Database created for the first time"

client.switch_database(DATA_BASE_NAME)

print("""Display Temperature, Pressure, Humidity and Gas
Press Ctrl+C to exit
""")

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

iterations = 0

def calculate_tendency (T,P,H):
    global temp_table
    global hum_table
    global pres_table
    global current_index
    global temp_tendency
    global hum_tendency
    global pres_tendency
    global first_data_available

    temp_table[current_index] = T
    hum_table[current_index] = H
    pres_table[current_index] = P
    current_index += 1

    if current_index >= REGISTERS_TO_KEEP:
        current_index = 0
        first_data_available = True
	print temp_table

    if first_data_available:
	temp_mean = mean(temp_table) 
        hum_mean = mean(hum_table)
	pres_mean = mean(pres_table)

    	if (T - temp_mean) > TEMPERATURE_HYSTERESIS:
	    temp_tendency = " U"
	elif (T - temp_mean) < -TEMPERATURE_HYSTERESIS:
	    temp_tendency = " D"
	else:
	    temp_tendency = " ="

 	if (P - pres_mean) > PRESSURE_HYSTERESIS:
            pres_tendency = " U"
        elif (P - pres_mean) < -PRESSURE_HYSTERESIS:
            pres_tendency = " D"
        else:
            pres_tendency = " ="

	if (H - hum_mean) > RELATIVE_HUMIDITY_HYSTERESIS:
            hum_tendency = " U"
        elif (H - hum_mean) < -RELATIVE_HUMIDITY_HYSTERESIS:
            hum_tendency = " D"
        else:
            hum_tendency = " ="

try:
    while True:
        if sensor.get_sensor_data():
	    calculate_tendency (sensor.data.temperature,sensor.data.pressure,sensor.data.humidity)
	    timestamp = time.time()
	    d = datetime.datetime.fromtimestamp(timestamp)
	    timestring = rfc3339(d, utc=True, use_system_timezone=False)
	
	    json_body = [
	    {
		"measurement": "WeatherData",
		"tags": {
		    "user": "Txema",
		    "sensor1": "BME680"
		},
		"time": timestring,
		"fields": {
		    "temperature": sensor.data.temperature,
		    "pressure": sensor.data.pressure,
	 	    "humidity": sensor.data.humidity
		}
	    }]
	    print json_body
	    print "\n"

	if (iterations % DISPLAY_EVERY_X_SAMPLES ) == 0: 	   		
	    plotData(["T: " , '{0:.2f} C'.format(sensor.data.temperature), temp_tendency, 
	    	    "H: ", '{0:.2f} %'.format(sensor.data.humidity), hum_tendency,
		    "P: ", '{0:.2f} hPa'.format(sensor.data.pressure), pres_tendency])
	    client.write_points(json_body)
	    print ("Data saved")
	    iterations = 0;
	
	
        time.sleep(SAMPLE_EVERY_SECONDS)
	iterations += 1

except KeyboardInterrupt:
    pass
