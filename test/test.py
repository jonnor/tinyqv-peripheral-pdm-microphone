# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from tqv import TinyQV

# When submitting your design, change this to the peripheral number
# in peripherals.v.  e.g. if your design is i_user_peri05, set this to 5.
# The peripheral number is not used by the test harness.
PERIPHERAL_NUM = 0

# Periphreal register definitions
# ref docs/info.md
REG_CTRL = 0x00
REG_CLKP = 0x04
REG_PCMW = 0x08

@cocotb.test()
async def test_initial(dut):
    dut._log.info("test_initial start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Interact with your design's registers through this TinyQV class.
    tqv = TinyQV(dut, PERIPHERAL_NUM)

    # Reset
    await tqv.reset()

    # Initially the control register is all 0
    assert await tqv.read_word_reg(REG_CTRL) == 0x0

    # Intially the clock scaling is 0
    assert await tqv.read_word_reg(REG_CLKP) == 0x0

    # Set the clock scaling, and read it back
    clock_scale = 32
    await tqv.write_word_reg(REG_CLKP, clock_scale)
    assert await tqv.read_word_reg(REG_CLKP) == clock_scale


@cocotb.test()
async def test_running(dut):
    dut._log.info("test_running start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Interact with your design's registers through this TinyQV class.
    tqv = TinyQV(dut, PERIPHERAL_NUM)

    # Reset
    await tqv.reset()

    # TODO: set a clock scaling, and to running via CTRL register
    # TODO: check that interrupt happens on regular basis

    dut.ui_in[6].value = 1
    await ClockCycles(dut.clk, 1)
    dut.ui_in[6].value = 0

    # Interrupt asserted
    await ClockCycles(dut.clk, 3)
    assert await tqv.is_interrupt_asserted()

    # Interrupt doesn't clear
    await ClockCycles(dut.clk, 10)
    assert await tqv.is_interrupt_asserted()
    
    # Write bottom bit of address 8 high to clear
    await tqv.write_byte_reg(8, 1)
    assert not await tqv.is_interrupt_asserted()

