
import time
import machine
import struct
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
    
    for i in range(10):
        print(interrupt.value())
        time.sleep(0.10)


    # SPI communication
    # Chip select, active low
    spi_cs_n = Pin(13, Pin.OUT) # Pin 9 is used for ICE40 flash SS, should be avoided

    # NOTE: Above 6 Mhz started to get read/write errors
    spi = SPI(0, 6_000_000,
            sck=Pin(2),
            mosi=Pin(3),
            miso=Pin(0),
            #sck=Pin(10),
            #mosi=Pin(11),
            #miso=Pin(8),
            bits=8,
            phase=0,
            polarity=0,
            firstbit=SPI.MSB)
    peri = PeripheralCommunicationSPI(spi, spi_cs_n)


    ctrl = peri.read32(REG_CTRL)
    print('control', ctrl)

    # Set and check scale
    clkp = peri.read32(REG_CLKP)
    scale_config = bytearray([0x00, 0x00, 0x00, 64])
    peri.write32(REG_CLKP, scale_config)

    clkp = peri.read32(REG_CLKP)
    assert clkp == scale_config, (clkp, scale_config)

    #for i in range(10):
    #    peri.write32(REG_CTRL, bytearray([0x00, 0x00, 0x00, 0x01]))
    #    time.sleep(2.0)
    #    peri.write32(REG_CTRL, bytearray([0x00, 0x00, 0x00, 0x00]))
    #    time.sleep(2.0)

    # Enable the PDM clock
    print('enable clock')
    clock_config = bytearray([0x00, 0x00, 0x00, 0x01])
    peri.write32(REG_CTRL, clock_config)
    ctrl = peri.read32(REG_CTRL)
    assert ctrl == clock_config, (ctrl, clock_config)


    print("PCM:")
    pcm_start = time.ticks_us()
    n_samples = 100
    samples = bytearray(n_samples)
    read_pcm_samples(peri, samples)
    pcm_read_duration = time.ticks_diff(time.ticks_us(), pcm_start)
    per_sample = pcm_read_duration / n_samples
    deadline = 62 # at 16khz, only have 62 us between each sample
    print('PCM read duration', per_sample)
    assert per_sample < deadline, (per_sample, deadline)

    print(samples)

@micropython.native
def read_pcm_samples(peri, samples):

    n_samples = len(samples) # 1 byte per each, for now

    # pre-allocate buffers
    mem = memoryview(samples) 
    cmd = bytearray([ 0b01000000, 0, 0, REG_PCMW ])
    pcm = bytearray(4)

    # cache member references, avoids lookup
    # and we do not have the function call overhead
    cs_n = peri.cs_n
    spi = peri.spi

    for i in range(n_samples):
        cs_n.value(0)
        spi.write(cmd)
        spi.readinto(pcm)
        mem[i] = pcm[3]
        cs_n.value(1)

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

    def __init__(self, spi, cs_n):
        self.spi = spi
        self.cs_n = cs_n

    @micropython.native
    def read32_into(self, addr : int, buf, cmd):
        """
        Read into a pre-allocated buffer. Fastest
        """

        self.cs_n.value(0)
        self.spi.write(cmd)
        self.spi.readinto(buf)
        self.cs_n.value(1)

    @micropython.native
    def read32(self, addr : int):
        if addr < 0 or addr > 2**5:
            raise ValueError("Invalid address")

        cmd = bytearray([ 0b01000000, 0, 0, addr ])
        read_data = bytearray([0xFF, 0, 0xFF, 0])
        self.read32_into(addr, read_data, cmd)
        return read_data


    def write32(self, addr, data):
        if addr < 0 or addr > 2**5:
            raise ValueError("Invalid address")

        self.cs_n.value(0)
        cmd = [ 0b11000000, 0, 0, addr ]
        p = bytearray(cmd + list(data))
        #print('write', p)

        #spi.write(b'\xC0\x00\x00' + struct.pack('>B', address) + struct.pack('>L', data))

        self.spi.write(p)
        self.cs_n.value(1)

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
    clk = PWM(FPGA_CLK, freq=64_000_000, duty_u16=32768)
    print("TT clock running")

    return clk


if __name__ == '__main__':
    run_test()



