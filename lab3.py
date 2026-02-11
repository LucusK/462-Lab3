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
    #sample the voltages
    samples = []
    for _ in range(200):
        samples.append(chan0.voltage)
        time.sleep(1/1000)
    
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

    
    
    #check if square
    count_flat_region = 0
    for j in samples:
        if(abs(j-minVoltage) < 0.25 or abs (j - maxVoltage) < 0.25):
            count_flat_region += 1
    
    if (count_flat_region > 0.75 * len(samples)):
        type = "square"

    #check if triangle
    if ((avg_slope > 0.05) and (count_flat_region < 0.75 * len(samples))):
        type = "triangle"
    
    #check if sin
    if minVoltage != maxVoltage:
        type = "sine"
    
    #print result
    print("type is ", type)