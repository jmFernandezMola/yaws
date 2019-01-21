#!/usr/bin/env python
import bme680
import time
from plotDataEInk import plotData 
from statistics import mean 

SAMPLE_EVERY_SECONDS = 10
REGISTERS_TO_KEEP = 720
TEMPERATURE_HYSTERESIS = 0.2
PRESSURE_HYSTERESIS = 0.05
RELATIVE_HUMIDITY_HYSTERESIS = 0.5
DISPLAY_EVERY_X_SAMPLES = 60  

temp_table = [0]*REGISTERS_TO_KEEP
hum_table = [0]*REGISTERS_TO_KEEP
pres_table = [0]*REGISTERS_TO_KEEP
current_index = 0
temp_tendency = " ="
hum_tendency = " ="
pres_tendency = " ="
first_data_available = False

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

#sensor.set_gas_heater_temperature(320)
#sensor.set_gas_heater_duration(150)
#sensor.select_gas_heater_profile(0)


# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

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


print('\n\nPolling:')
try:
    while True:
        if sensor.get_sensor_data():
	    output = '{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity)
	    
	    calculate_tendency (sensor.data.temperature,sensor.data.pressure,sensor.data.humidity)
            if sensor.data.heat_stable:
                print('{0},{1} Ohms'.format(
                    output,
                    sensor.data.gas_resistance))
            else:
                print(output)

	if (iterations % 30) == 0: 
	   		
	    plotData(["T: " , '{0:.2f} C'.format(sensor.data.temperature), temp_tendency, 
	    	    "H: ", '{0:.2f} %'.format(sensor.data.humidity), hum_tendency,
		    "P: ", '{0:.2f} hPa'.format(sensor.data.pressure), pres_tendency])
	    iterations = 0;
        time.sleep(SAMPLE_EVERY_SECONDS)
	iterations += 1

except KeyboardInterrupt:
    pass
