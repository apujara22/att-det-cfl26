from enum import IntEnum
import smbus2
import time

class TCA9548A():
    """
    Simple driver for TCA9548A
    """
    _device_addr = None
    _available_addr = [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77]

    def __init__(self, address=0x77, smbus_num=1):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x70 through 0x77")
        
        self._device_addr = address
        self._i2c_bus = smbus2.SMBus(smbus_num)

    def change_address(self, address):
        if address not in self._available_addr:
            raise Exception("Possible addresses are 0x70 through 0x77")
        
        self._device_addr = address

    def allOff(self):
        """
        Writes all 0s to control register to turn all channels off.
        This is also the default bootup state.
        """

        self._i2c_bus.write_byte(self._device_addr, 0x00)
    
    def allOn(self):
        """
        Writes all 1s to control register to turn all channels on.
        """

        self._i2c_bus.write_byte(self._device_addr, 0xFF)
    
    def singleOn(self, channel):
        """
        Turns off all channels, then enables a single selected channel.
        Available channels are 0 through 7.
        """

        if channel < 0 or channel > 7:
            raise Exception("Channel out of range. Select channel between 0 and 7")

        self.allOff()

        channelByte = 0x1 << channel
        self._i2c_bus.write_byte(self._device_addr, channelByte)

    def singleOff(self, channel):
        """
        Turns off specific channel.
        Available channels are 0 through 7.
        """

        if channel < 0 or channel > 7:
            raise Exception("Channel out of range. Select channel between 0 and 7")

        selChannel = 0x1 << channel
        selChannel = 0xFF ^ selChannel

        currState = self.readState()

        channelByte = currState & selChannel

        self._i2c_bus.write_byte(self._device_addr, channelByte)

    def comboSel(self, channelByte):
        """
        Turns off all channels, then enables a combination of channels.
        Channel 0 through 7 are controlled by the state of the LSB to MSB, respectively.
        For example, 0xA4, or b10100100, enables channels 7, 5, and 2.
        See datasheet for more information.
        """
        if channelByte < 0 or channelByte > 255:
            raise Exception("Selection out of range. Select between 0x00 and 0xFF")

        self.allOff()

        self._i2c_bus.write_byte(self._device_addr, channelByte)

    def readState(self):
        """
        Returns state of command register.
        Each bit that is on indicates the state of that channel.
        Fore example, if it returns 0xA4, or b10100100, channels 7, 5, and 2 are enabled.
        """
        return self._i2c_bus.read_byte(self._device_addr)

    def readStateDebug(self):
        """
        Prints out channels state
        """
        channels = self.readState()

        for i in range(8):
            print(f"Channel {i} state: {channels & 1}")
            channels = channels >> 1
        
        print("\n")

test = TCA9548A()

print("Reading state")
test.readStateDebug()
print("Turning everything on")
test.allOn()
test.readStateDebug()
print("Turning everything off")
test.allOff()
test.readStateDebug()
print("Turning channels 2 and 4 on")
test.comboSel(0x14)
test.readStateDebug()
print("Turning channel 2 off")
test.singleOff(2)
test.readStateDebug()
test.singleOn(0)



