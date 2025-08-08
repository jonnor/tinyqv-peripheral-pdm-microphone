# PDM: Pulse Density Modulation Decoder

Author: Jon Nordby, Martin Stensgård

Peripheral index: TODO(mastensg): pick index at submission.

## What it does

The PDM peripheral outputs a bit clock signal for a PDM microphone,
and decodes the returned density signal into Pulse Code Modulation (PCM) words.

## Register map

| Address | Name  | Access | Description                                                         |
|---------|-------|--------|---------------------------------------------------------------------|
| 0x00    | CTRL  | R/W    | PDM control.                                                        |
| 0x04    | CLKP  | R/W    | PDM clock period (0-64).                                            |
| 0x08    | PCMW  | R      | PCM word, result of conversion.                                     |

### CTRL
Bit 0: Enable clock generation.

### CLKP
Number of system clock cycles per PDM clock cycle.
For example, to generate a 1 MHz clock signal, set this to 64.

### PCMW
32-bit signed integer.
TODO(mastensg): pick final output format.

## How to test

TODO(mastensg): add example code.

## External hardware

Adafruit PDM MEMS Microphone Breakout
https://www.adafruit.com/product/3492
