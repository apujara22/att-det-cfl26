from enum import IntEnum
import smbus2
import time
import numpy as np

class AD7998():
    """
    Simple driver for AD7998-1 operation in command mode operation

    Other functionalities not used but implementable in software:
        - Alert functionality
        - Cyclic conversion operation
    """
    _device_addr = None
    _available_addr = [0x20, 0x23, 0x24]
    _conversionFuncs = ["X", "X", "X", "(X - 1.8663) / (-0.01169)"]
    _conversionUnits = ["V", "V", "V", "C"]

    def __init__(self, address=0x20, smbus_num=1):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x20, 0x23, and 0x24")
        
        self._device_addr = address
        self._i2c_bus = smbus2.SMBus(smbus_num)

    def change_address(self, address):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x20, 0x23, and 0x24")
        
        self._device_addr = address

    def get_data(self):
        """
        Returns a list containing raw results in the following order: [Vin1, Vin2, Vin3, Vin4, Vin5, Vin6, Vin7, Vin8]
        Result need to be converted to a voltage, then the appropriate conversion function must 
        be applied to convert the raw voltage to the correct units.
        """
        self._i2c_bus.write_i2c_block_data(self._device_addr, 0x02, [0x0F, 0xF8])
        data = self._i2c_bus.read_i2c_block_data(self._device_addr, 0x70, 16)

        newdata = []
        for i in range(0,len(data), 2):
            newdata.append((data[i]<<8) + data[i+1])
    
        #self._printConverted(newdata)

        rawCounts = [(channelBytes & 0xfff) for channelBytes in newdata]

        return rawCounts

    def set_single(self, channel = 1):
        """
        ***NEEDS DEBUGGING***
        Enables a single channel for measurement
        """
        if channel <1 or channel >8:
            raise Exception("Channel needs to be between 1 and 8")

        if channel <5:
            bottom_bytes = 0x01 << (3 + channel)
            bottom_bytes = bottom_bytes | 0x08
            config_bytes = [0x00, bottom_bytes]

        if channel >=5:
            top_bytes = 0x01 << (channel - 5)
            config_bytes = [top_bytes, 0x08]

        #print([int.to_bytes(x).hex() for x in config_bytes])
        self._i2c_bus.write_i2c_block_data(self._device_addr, 0x02, config_bytes)
        print(self._i2c_bus.read_i2c_block_data(self._device_addr, 0x02, 2))

    def get_single(self, channel = 1):
        """
        ***NEEDS DEBUGGING***
        Returns a measurement of the requested channel
        Result are raw counts and need to be convereted to a voltage
        """

        if channel <1 or channel >8:
            raise Exception("Channel needs to be between 1 and 8")

        Cbytes = (channel-1) << 4
        Cbytes = Cbytes | 0x80
        
        #self._i2c_bus.write_byte(self._device_addr, Cbytes)
        data = self._i2c_bus.read_i2c_block_data(self._device_addr, Cbytes, 2)
        newdata = data[0]<<8 + data[1]

        rawCount = newdata & 0xfff
        
        return rawCount

    def _printConverted(self, data):
        #results = self._conversionFuncs.copy()

        for channelBytes in data:
            cID = (channelBytes & 0x7000) >> 12
            rawCounts = channelBytes & 0xfff
            rawVolts = round((rawCounts/4096) * 3.0, 3)
            rawVolts = str(rawVolts)

            #results[cID] = round(eval(results[cID].replace("X", rawVolts)),4)
            #print(f"Vin{cID + 1}: {rawVolts}V \t|\tConverted: {results[cID]}{self._conversionUnits[cID]}")
            print(f"Vin{cID + 1}: {rawVolts}V")
        print("\n")
        return None

    def _debugPrint(self, data):
        print(f"RAW BYTES: {hex(data)}")
        print(f"Alert bit: {(data >> 15)}")
        print(f"Zero bit: {((data & 0x6000) >> 14)}")
        print(f"Channel ID: {((data & 0x3000) >> 12)}")
        print(f"Data: {(data>>2) & 0x3ff}")
        print(f"Should be Zeroes: {data & 0x3}\n")
        
ADCObject = AD7998(0x20)

"""
measurements = []
first = True
max = 0
min = 0
for i in range(100):
    measurement = ADCObject.get_data()
    measurement = measurement[1]
    if first:
        max = measurement
        min = measurement
        measurements.append(measurement)
        first = False
    else:
        measurements.append(measurement)
        if measurement < min:
            min = measurement
        if measurement > max:
            max = measurement
    time.sleep(0.1)

print(f"Average: {np.mean(measurements)}counts, Max: {max}counts, Min: {min}counts")
print(f"Average: {round(np.mean(measurements)*3.0/4096, 2)}V, Max: {round(max*3.0/4096,2)}V, Min: {round(min*3.0/4096,2)}V")
"""
"""
while True:
    ADCObject.get_data()
    time.sleep(1)
"""
