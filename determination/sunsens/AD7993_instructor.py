from enum import IntEnum
import smbus2
import time

class AD7993():
    """
    Simple driver for AD7993 operation in command mode operation

    Other functionalities not used but implementable in software:
        - Alert functionality
        - Cyclic conversion operation
    """
    _device_addr = None
    _available_addr = [0x20, 0x21, 0x22]
    _conversionFuncs = ["X * 1", "X * 111/11", "(X - 1.8663) / (-0.01169)", "X/30"]
    _conversionUnits = ["V", "V", "C", "A"]

    def __init__(self, address=0x20, smbus_num=1):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x20, 0x21, and 0x22")
        
        self._device_addr = address
        self._i2c_bus = smbus2.SMBus(smbus_num)

    def change_address(self, address):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x20, 0x21, and 0x22")
        
        self._device_addr = address

    def get_data(self):
        """
        Returns a list containing raw results in the following order: [Vin1, Vin2, Vin3, Vin4]
        Result need to be converted to a voltage, then the appropriate conversion function must 
        be applied to convert the raw voltage to the correct units.
        """
        data = self._i2c_bus.read_i2c_block_data(self._device_addr, 0xF0, 8)

        newdata = []
        for i in range(0,len(data), 2):
            newdata.append((data[i]<<8) + data[i+1])
    
        self._printConverted(newdata)

        rawCounts = [((channelBytes >> 2) & 0x3ff) for channelBytes in newdata]

        return rawCounts

    def _printConverted(self, data):
        results = self._conversionFuncs.copy()

        for channelBytes in data:
            cID = (channelBytes & 0x3000) >> 12
            rawCounts = (channelBytes >> 2) & 0x3ff
            rawVolts = round((rawCounts/1023) * 3, 3)
            rawVolts = str(rawVolts)

            results[cID] = round(eval(results[cID].replace("X", rawVolts)),4)
            print(f"Vin{cID + 1}: {rawVolts}V \t|\tConverted: {results[cID]}{self._conversionUnits[cID]}")
        
        print("\n")
        return None

    def _debugPrint(self, data):
        print(f"RAW BYTES: {hex(data)}")
        print(f"Alert bit: {(data >> 15)}")
        print(f"Zero bit: {((data & 0x6000) >> 14)}")
        print(f"Channel ID: {((data & 0x3000) >> 12)}")
        print(f"Data: {(data>>2) & 0x3ff}")
        print(f"Should be Zeroes: {data & 0x3}\n")
        
ADCObject = AD7993()

while True:
    ADCObject.get_data()
    time.sleep(0.01)
