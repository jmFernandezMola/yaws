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

initSensor()

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
	THP = readBme680
        if not THP:
	    print("THP sensor is not ready"
	else:
	    calculate_tendency (THP[0],THP[1],THP[2])
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
		    "temperature": THP[0],
		    "pressure": THP[1],
	 	    "humidity": THP[2]
		}
	    }]
	    print json_body
	    print "\n"

	if (iterations % DISPLAY_EVERY_X_SAMPLES ) == 0: 	   		
	    plotData(["T: " , '{0:.2f} C'.format(THP[0]), temp_tendency, 
	    	    "H: ", '{0:.2f} %'.format(THP[1]), hum_tendency,
		    "P: ", '{0:.2f} hPa'.format(THP[2]), pres_tendency])
	    client.write_points(json_body)
	    print ("Data saved")
	    iterations = 0;
	
	
        time.sleep(SAMPLE_EVERY_SECONDS)
	iterations += 1

except KeyboardInterrupt:
    pass
