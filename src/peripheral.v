/*
 * Copyright (c) 2025 Jon Nordby, Martin Stensgård
 * SPDX-License-Identifier: ISC
 */

`default_nettype none

// Change the name of this module to something that reflects its functionality and includes your name for uniqueness
// For example tqvp_yourname_spi for an SPI peripheral.
// Then edit tt_wrapper.v line 41 and change tqvp_example to your chosen module name.
module tqvp_jnms_pdm (
    input         clk,          // Clock - the TinyQV project clock is normally set to 64MHz.
    input         rst_n,        // Reset_n - low to reset.

    input  [7:0]  ui_in,        // The input PMOD, always available.  Note that ui_in[7] is normally used for UART RX.
                                // The inputs are synchronized to the clock, note this will introduce 2 cycles of delay on the inputs.

    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected.
                                // Note that uo_out[0] is normally used for UART TX.

    input [5:0]   address,      // Address within this peripheral's address space
    input [31:0]  data_in,      // Data in to the peripheral, bottom 8, 16 or all 32 bits are valid on write.

    // Data read and write requests from the TinyQV core.
    input [1:0]   data_write_n, // 11 = no write, 00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    input [1:0]   data_read_n,  // 11 = no read,  00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    
    output [31:0] data_out,     // Data out from the peripheral, bottom 8, 16 or all 32 bits are valid on read when data_ready is high.
    output        data_ready,

    output        user_interrupt  // Dedicated interrupt request for this peripheral
);
    wire rst = !rst_n;

    reg [31:0] pdm_ctrl;
    reg [31:0] pdm_clkp;

    reg [7:0] pdm_phase;
    reg       pdm_clk;
    reg       pdm_int;

    reg [15:0] pcm;
    reg        pcm_valid;

    wire pdm_clk_out = pdm_ctrl[0] & pdm_clk;
    wire pdm_dat_in = ui_in[0];

    cic3_pdm  cic(pdm_clk, rst, pdm_dat_in, pcm, pcm_valid);

    always @(posedge clk) begin
        if (!rst_n) begin
            pdm_ctrl <= 0;
            pdm_clkp <= 0;
            pdm_phase <= 0;
            pdm_clk <= 0;
        end else begin
            if (address == 6'h0) begin
                if (data_write_n != 2'b11)              pdm_ctrl[7:0]   <= data_in[7:0];
                if (data_write_n[1] != data_write_n[0]) pdm_ctrl[15:8]  <= data_in[15:8];
                if (data_write_n == 2'b10)              pdm_ctrl[31:16] <= data_in[31:16];
            end
            if (address == 6'h4) begin
                if (data_write_n != 2'b11)              pdm_clkp[7:0]   <= data_in[7:0];
                if (data_write_n[1] != data_write_n[0]) pdm_clkp[15:8]  <= data_in[15:8];
                if (data_write_n == 2'b10)              pdm_clkp[31:16] <= data_in[31:16];
            end
            pdm_clk   <= pdm_phase   < (pdm_clkp >> 1);
            pdm_phase <= pdm_phase+1 < pdm_clkp ? pdm_phase+1 : 0;
        end
    end

    // TODO(mastensg): output PCM sample clock on one of the pins.
    assign uo_out = {pdm_clk_out, pdm_clk_out, pdm_clk_out, pdm_clk_out, pdm_clk_out, pdm_clk_out, pdm_clk_out, pdm_clk_out};

    assign data_out = (address == 6'h0) ? pdm_ctrl :
                      (address == 6'h4) ? pdm_clkp :
                      (address == 6'h8) ? {16'h0, pcm} :
                      32'h0;

    assign data_ready = 1;

    // TODO(mastensg): set int when conversion complete, reset when read.
    always @(posedge clk) begin
        if (!rst_n) begin
            pdm_int <= 0;
        end else begin
            pdm_int <= 0;
        end
    end

    assign user_interrupt = pdm_int;

    wire _unused = &{ui_in[7], ui_in[5:0], data_read_n, 1'b0};

endmodule
