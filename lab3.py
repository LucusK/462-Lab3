import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

print('Raw ADC Value: ', chan0.value)
print('ADC Voltage: ' + str(chan0.voltage) + 'V')



while True:
    #sample the voltages per second, 1000x a second
    samples = []
    start = time.perf_counter()
    for _ in range(1000):
        samples.append(chan0.voltage)
        time.sleep(1/1000)
    end = time.perf_counter()
    total_time = end - start
    
    #small smoothing (3-point average) to reduce noise
    smoothing = []
    smoothing.append(samples[0])
    for i in range(1, len(samples) - 1):
        smoothing.append((samples[i-1] + samples[i] + samples[i+1]) / 3)
    smoothing.append(samples[-1])
    

    #find slope of samples
    slopes = []
    for i in range(len(samples) - 1):
        slopes.append(samples[i+1]-samples[i])

    #find average slopes
    sum_slopes = 0
    for k in slopes:
        sum_slopes += abs(k)
    avg_slope = sum_slopes / len(slopes)

    #define type
    type = ""

    #find min max and difference
    minVoltage = min(samples)
    maxVoltage = max(samples)
    height = maxVoltage - minVoltage
    middle = (minVoltage + maxVoltage) / 2

    if height < 0.05:
        print("type is ", "")
        print("frequency is ", 0)
        continue
    
    #find flat regions
    count_flat_region = 0
    for j in smoothing:
        if(abs(j-minVoltage) < 0.08*height or abs (j - maxVoltage) < 0.08*height):
            count_flat_region += 1
    


    if count_flat_region > 0.8 * len(smoothing):
        type = "square"
    elif avg_slope > 0.005 * height:
        type = "triangle"
    else:
        type = "sine"

    #determine frequency, where counting number times cross midline in second
    frequency = 0
    for m in range(1,len(smoothing)):
        if(smoothing[m-1] < middle and smoothing[m] > middle):
            frequency += 1
    frequency = frequency / total_time

    #print result
    print("type is ", type)
    print("frequency is ", frequency)