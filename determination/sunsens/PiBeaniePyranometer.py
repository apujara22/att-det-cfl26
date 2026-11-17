# Revised "Pyranometer_revise_to_run"
# For collecting pyranometer data with PiBeanie

# Temp measuring software omitted for now

import time

from AD7998_instructor import AD7998

PYRO_CAL_CONST = 66.18/1000 # units = µA / (W/m^2)
PYRO_GAIN = 0.025
PYRO_CONV_FUNC = 1/(PYRO_CAL_CONST*PYRO_GAIN) # multiply by meaas. volt. for irradiance in W/m^2
AD7998_ADDR = 0x23
AVG_SAMPLE = 5
SAVE = False

ADC = AD7998(AD7998_ADDR)

print("Recording data for channels 2-7:")

# ADC_CH = int(input("Enter channel pyranometer is hooked up to [2:7]: "))
# if ADC_CH < 2 or ADC_CH > 7:
#     raise Exception("*2 TO 7, INCLUSIVE*")

ADC_CH2 = 2
ADC_CH3 = 3
ADC_CH4 = 4
ADC_CH5 = 5
ADC_CH6 = 6
ADC_CH7 = 7

save = float(input("Save file? 1 for yes, 0 for no: "))
if save > 0:
    SAVE = True

interval = float(input("Enter the data collection interval in seconds: "))
if interval < 0 or interval > 10:
    raise Exception("bro quit playing. 0 <= interval <= 10 seconds")

fileName = "/home/pi/Desktop/"+str(time.time())+".csv"
header = "unixTime,v_ch2,v_ch3,v_ch4,v_ch5,v_ch6,v_ch7\n"

if SAVE:
    print(f"files will be saved to {fileName}")
    with open(fileName, 'a') as f:
        f.write(header)

print("ctrl-C to exit")
time.sleep(0.5)

samps = 1
startTime = time.time()
while 1:
    sampleTime = time.time()
    data2 = 0
    data3 = 0
    data4 = 0
    data5 = 0
    data6 = 0
    data7 = 0

    for i in range(AVG_SAMPLE):
        rawCounts = ADC.get_data()

        rawVolts2 = (rawCounts[ADC_CH2]/4096) * 3.0
        rawVolts3 = (rawCounts[ADC_CH3]/4096) * 3.0
        rawVolts4 = (rawCounts[ADC_CH4]/4096) * 3.0
        rawVolts5 = (rawCounts[ADC_CH5]/4096) * 3.0
        rawVolts6 = (rawCounts[ADC_CH6]/4096) * 3.0
        rawVolts7 = (rawCounts[ADC_CH7]/4096) * 3.0

        data2 += rawVolts2
        data3 += rawVolts3
        data4 += rawVolts4
        data5 += rawVolts5
        data6 += rawVolts6
        data7 += rawVolts7
    
    data2 = round(data2 / AVG_SAMPLE, 3)
    data3 = round(data3 / AVG_SAMPLE, 3)
    data4 = round(data4 / AVG_SAMPLE, 3)
    data5 = round(data5 / AVG_SAMPLE, 3)
    data6 = round(data6 / AVG_SAMPLE, 3)
    data7 = round(data7 / AVG_SAMPLE, 3)

    if SAVE:
        with open(fileName, 'a') as f:
            f.write(f"{sampleTime},{data2},{data3},{data4},{data5},{data6},{data7}\n")
            # f.write(f"{sampleTime},{data2}\n")
    
    print(f"{samps}\t\t{data2}\t{data3}\t{data4}\t{data5}\t{data6}\t{data7} V") 
    # print(f"{samps}\t\t{data2} V") 
    samps += 1
    diffTime = time.time() - (sampleTime + interval)
    if (diffTime) < 0:
        time.sleep(-diffTime)

        
    
