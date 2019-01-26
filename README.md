# yaws
Yet Another Weather Station for Raspberry Pi ;p

Installing BME680 sensor:

Follow the instructions of the pimoroni/bme680-python repository to install its python libraries. Basically, clone the repo and execute the `sudo python setup.py install` in the library directory of the repository. 

## Installing the influxDB

All the information can be found in: https://www.influxdata.com/blog/running-the-tick-stack-on-a-raspberry-pi/ 

* Get the VERSION (code is in parentheses) of the OS: `sudo cat /etc/os-releases`. In this case VERSION="9 (stretch)".
* Add the key: `curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -`
* Add the repo. Remember to adapt the OS version `echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list`
* Update the packages `sudo apt-get update`
* And finally install the TICK stack. At least the influxdb to be used with python. The other are optional (not recommended):
`sudo apt-get install telegraf influxdb chronograf kapacitor python-influxdb`

## Testing with python

Start the influx db service: `sudo service influxdb start`
Take a look on the following web: https://www.influxdata.com/blog/getting-started-python-influxdb/

## Chronograf

First of all download, install and run the program. Then start the server and connect the web browser: `http://localhost:8888` and finally connect the raspberry using the IP or the host name.
