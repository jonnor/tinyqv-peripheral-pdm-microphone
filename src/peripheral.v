/*
 * Copyright (c) 2025 Your Name
 * SPDX-License-Identifier: Apache-2.0
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

    reg [31:0] pdm_ctrl;
    reg [31:0] pdm_clkp;
    reg [31:0] pdm_pcmw;

    reg [7:0] pdm_phase;
    reg       pdm_clk;

    always @(posedge clk) begin
        if (!rst_n) begin
            pdm_ctrl <= 0;
            pdm_clkp <= 0;
            pdm_pcmw <= 0;
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
            if (address == 6'h8) begin
                if (data_write_n != 2'b11)              pdm_pcmw[7:0]   <= data_in[7:0];
                if (data_write_n[1] != data_write_n[0]) pdm_pcmw[15:8]  <= data_in[15:8];
                if (data_write_n == 2'b10)              pdm_pcmw[31:16] <= data_in[31:16];
            end
        end
    end

    // The bottom 8 bits of the stored data are added to ui_in and output to uo_out.
    //assign uo_out = example_data[7:0] + ui_in;
    assign uo_out[7:2] = 6'b000000;
    assign uo_out[1] = pdm_ctrl[0] && pdm_clk;
    assign uo_out[0] = 0;

    always @(posedge clk) begin
    	    pdm_phase <= pdm_phase<9 ? pdm_phase+1 : 0;
    	    pdm_clk <= pdm_phase<5;
    end

    // Address 0 reads the example data register.  
    // Address 4 reads ui_in
    // All other addresses read 0.
    assign data_out = (address == 6'h0) ? pdm_ctrl :
                      (address == 6'h4) ? pdm_clkp :
                      (address == 6'h8) ? pdm_pcmw :
                      32'h0;

    // All reads complete in 1 clock
    assign data_ready = 1;
    
    // User interrupt is generated on rising edge of ui_in[6], and cleared by writing a 1 to the low bit of address 8.
    reg example_interrupt;
    reg last_ui_in_6;

    always @(posedge clk) begin
        if (!rst_n) begin
            example_interrupt <= 0;
        end

        if (ui_in[6] && !last_ui_in_6) begin
            example_interrupt <= 1;
        end else if (address == 6'h8 && data_write_n != 2'b11 && data_in[0]) begin
            example_interrupt <= 0;
        end

        last_ui_in_6 <= ui_in[6];
    end

    assign user_interrupt = example_interrupt;

    // List all unused inputs to prevent warnings
    // data_read_n is unused as none of our behaviour depends on whether
    // registers are being read.
    wire _unused = &{ui_in[7], ui_in[5:0], data_read_n, 1'b0};

endmodule
