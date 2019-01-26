#!/usr/bin/env python
import bme680
import time
import datetime
from plotDataEInk import plotData 
from statistics import mean 
from rfc3339 import rfc3339 
import json
from readBME680 import initSensor, readBme680 

SAMPLE_EVERY_SECONDS = 60
TEMPERATURE_HYSTERESIS = 0.2
PRESSURE_HYSTERESIS = 0.05
RELATIVE_HUMIDITY_HYSTERESIS = 0.5
DATA_BASE_NAME = 'weatherDataBase'

temp_tendency = " ="
hum_tendency = " ="
pres_tendency = " ="

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

sensor = initSensor()

def calculate_tendency (T,H,P):
  results = client.query('SELECT mean("temperature") AS "mean_temp"  FROM "weatherDataBase"."autogen"."WeatherData" WHERE time > now() - 6h')
  temp_mean = results.raw["series"][0]["values"][0][1]
  results = client.query('SELECT mean("humidity") AS "mean_hum"  FROM "weatherDataBase"."autogen"."WeatherData" WHERE time > now() - 6h')
  hum_mean = results.raw["series"][0]["values"][0][1]
  results = client.query('SELECT mean("pressure") AS "mean_hum"  FROM "weatherDataBase"."autogen"."WeatherData" WHERE time > now() - 6h')
  pres_mean = results.raw["series"][0]["values"][0][1]

  print [temp_mean, hum_mean, pres_mean]
  
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
	THP = readBme680(sensor)
	print THP
        if not THP:
	    print("THP sensor is not ready")
	else:
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
		    "pressure": THP[2],
	 	    "humidity": THP[1]
		}
	    }]
	    print json_body
 	    client.write_points(json_body)
            calculate_tendency(THP[0],THP[1],THP[2])		
	    plotData(["T: " , '{0:.2f} C'.format(THP[0]), temp_tendency, 
	    	    "H: ", '{0:.2f} %'.format(THP[1]), hum_tendency,
		    "P: ", '{0:.2f} hPa'.format(THP[2]), pres_tendency])
        time.sleep(SAMPLE_EVERY_SECONDS)
except KeyboardInterrupt:
    pass
