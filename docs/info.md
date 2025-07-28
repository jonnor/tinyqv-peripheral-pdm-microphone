<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

The peripheral index is the number TinyQV will use to select your peripheral.  You will pick a free
slot when raising the pull request against the main TinyQV repository, and can fill this in then.  You
also need to set this value as the PERIPHERAL_NUM in your test script.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

# PDM: Pulse Density Modulation Decoder

Author: Jon Nordby, Martin Stensgård

Peripheral index: TODO(mastensg): pick index at submission.

## What it does

The PDM peripheral outputs a bit clock signal for a PDM microphone,
and decodes the returned density signal into Pulse Code Modulation (PCM) words.

## Register map

| Address | Name  | Access | Description                                                         |
|---------|-------|--------|---------------------------------------------------------------------|
| 0x00    | DATA  | R/W    | PDM clock period (0-64)                                             |
|         |       |        | Number of system clock cycles per PDM clock cycle.                  |
|         |       |        | For example, to generate a 1 MHz clock signal, set this to 64.      |
|---------|-------|--------|---------------------------------------------------------------------|
| 0x04    | DATA  | R      | PCM word                                                            |

## How to test

TODO(mastensg): add example code.

## External hardware

Adafruit PDM MEMS Microphone Breakout
https://www.adafruit.com/product/3492
