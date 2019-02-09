import serial
import time
import struct
import RPi.GPIO as GPIO

def getNewDataPM():
    RESET_PIN = 18
    SET_PIN = 4
    ITERATIONS = 30
    PLOT = False

    port = serial.Serial("/dev/serial0", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=3.0)
    buffer = []

#CHECK PINS FOR NON rp3 b+ version
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SET_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setwarnings(False)

    time.sleep(1)

    GPIO.output(SET_PIN, GPIO.HIGH)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(10)

    for X in range(ITERATIONS):
        data = port.read(32)  # read up to 32 bytes
        data = list(data)
    #    print("read: ", data)          # this is a bytearray type

        buffer += data

        while buffer and buffer[0] != str('\x42'):
            buffer.pop(0)

        if len(buffer) > 200:
            buffer = []  # avoid an overrun if all bad data
        if len(buffer) < 32:
            continue

        if buffer[1] != str('\x4d'):
            buffer.pop(0)
            continue

        bufferConcatenated = ""
        for element in buffer:
            bufferConcatenated += element

        frame_len = struct.unpack(">H", bytes(bufferConcatenated[2:4]))[0]
        if frame_len != 28:
            buffer = []
            continue

        frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(bufferConcatenated[4:]))

        pm10_standard, pm25_standard, pm100_standard, pm10_env, \
            pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, \
            particles_25um, particles_50um, particles_100um, skip, checksum = frame

        check = 0

        for element in buffer[0:30]:
    	    check += ord(element)

        if check != checksum:
            buffer = []
            continue
        if PLOT:
            print("Concentration Units (standard)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
                  (pm10_standard, pm25_standard, pm100_standard))
            print("Concentration Units (environmental)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
            print("---------------------------------------")
            print("Particles > 0.3um / 0.1L air:", particles_03um)
            print("Particles > 0.5um / 0.1L air:", particles_05um)
            print("Particles > 1.0um / 0.1L air:", particles_10um)
            print("Particles > 2.5um / 0.1L air:", particles_25um)
            print("Particles > 5.0um / 0.1L air:", particles_50um)
            print("Particles > 10 um / 0.1L air:", particles_100um)
            print("---------------------------------------")

        buffer = buffer[32:]
        # print("Buffer ", buffer)

    GPIO.output(SET_PIN, GPIO.LOW)
    time.sleep(0.5)
    return ([pm10_standard, pm25_standard, pm100_standard])
