
import time
import machine
from machine import SPI, Pin, PWM

FPGA_CLK = 24
TT_RST = 12

REG_CTRL = 0x00
REG_CLKP = 0x04
REG_PCMW = 0x08


def run_test():

    # Set clock frequency of RP2040
    machine.freq(133_000_000)

    # Set everything to inputs, to be safe
    for i in range(30):
        Pin(i, Pin.IN, pull=None)

    clk = start_peripheral()
    print(clk)

    # The SPI communication expects pico-ice

    interrupt = Pin(1, Pin.IN)
    
    while True:
        #print(interrupt.value())
        time.sleep(0.10)

    return

    # SPI communication

    # Chip select, active low
    spi_cl_n = Pin(9, Pin.OUT)

    spi = SPI(1, 12_000_000,
            sck=Pin(10), mosi=Pin(11), miso=Pin(8),
            bits=32,
            firstbit=SPI.MSB)
    peri = PeripheralCommunicationSPI(spi)

    # select chip
    spi_cl_n.value(0)

    ctrl = peri.read32(REG_CTRL)
    print('control', ctrl)

    # TODO: implement writing and read back

    clkp = peri.read32(REG_CLKP)

    peri.write32(REG_CLKP, bytearray([0x00, 0x00, 0x33, 0x00]))


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

        self.spi.write(bytearray([ 0b01000000, 0, 0, addr ]))
        read_data = bytearray([0, 0, 0, 0])
        self.spi.readinto(read_data)
        return read_data


    def write32(self, addr, data):
        if addr < 0 or addr > 2**5:
            raise ValueError("Invalid address")

        self.spi.write(bytearray([ 0b11000000, 0, 0, addr ]))
        self.spi.write(data)


def start_peripheral():

    # Start the ICE40 FPGA
    ice_creset_b = machine.Pin(27, machine.Pin.OUT)
    ice_creset_b.value(0)

    ice_done = machine.Pin(26, machine.Pin.IN)
    time.sleep_us(10)
    ice_creset_b.value(1)

    while ice_done.value() == 0:
        print(".", end = "")
        time.sleep(0.001)
    print("ICE40 done")


    # Start the TinyTapeout TinyQV peripheral
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
    clk = PWM(FPGA_CLK, freq=14_000_000, duty_u16=32768)
    print("TT clock running")

    return clk


if __name__ == '__main__':
    run_test()



