
import time
import machine
from machine import SPI, Pin, PWM

FPGA_CLK = 24
TT_RST = 12

REG_CTRL = 0x0

def run_test():

    # Set clock frequency of RP2040
    machine.freq(133_000_000)

    # Set everything to inputs, to be safe
    for i in range(30):
        Pin(i, Pin.IN, pull=None)

    clk = start_peripheral()

    spi = SPI(1, 12_000_000, sck=Pin(10), mosi=Pin(11), miso=Pin(8),
            bits=32,
            firstbit=SPI.MSB)
    peri = PeripheralCommunicationSPI(spi)
    
    ctrl = peri.read32(REG_CTRL)
    print('control', ctrl)

    # TODO: implement writing and read back


class PeripheralCommunicationSPI():

    """
    Read/write data in TinyQV peripheral over SPI 
    On an FPGA that is flashed with test_harness

    | Bits | Meaning |
    | ---- | ------- |
    | 31    | Read or write command: 1 for a write, 0 for a read |
    | 30-29 | Transaction width 0, 1 or 2 for 8, 16 or 32 bits |
    | 28-6  | Unused |
    | 5-0   | The register address |
    """

    def __init__(self, spi):
        self.spi = spi

    def read32(self, addr : int):
        if addr < 0 or addr > 2**5:
            raise ValueError("Invalid address")

        # Read
        #cmd = (1 >> 31) & (2 << 29) & addr
        
        self.spi.write(bytearray([ 0b01000000, 0, 0, addr ]))
        read_data = bytearray([0, 0, 0, 0])
        self.spi.readinto(read_data)
        return read_data


    def spi_write32(spi, addr):
        pass
        raise NotImplementedError()
        #addr
        #0x


def start_peripheral():

    rst_n = Pin(TT_RST, Pin.OUT)
    clk = Pin(FPGA_CLK, Pin.OUT)

    clk.off()
    rst_n.on()
    time.sleep(0.001)
    rst_n.off()

    clk.on()
    time.sleep(0.001)
    clk.off()
    time.sleep(0.001)

    for i in range(10):
        clk.off()
        time.sleep(0.001)
        clk.on()
        time.sleep(0.001)

    rst_n.on()
    time.sleep(0.001)
    clk.off()

    time.sleep(0.001)
    clk = PWM(Pin(24), freq=14_000_000, duty_u16=32768)

    return clk


if __name__ == '__main__':
    run_test()



