// Copyright (c) 2023=2023 All rights reserved
// =============================================================================
// Author : Andrey Vasilchenko (Andrey) andvasilc3@gmail.com
// File   : cnt.sv
// Create : 2023-12-03 21:25:48
// Revise : 2023-12-03 21:25:49
// Editor : sublime text4, tab size (2)
// =============================================================================
module cnt (
	input logic clk,
	input logic rst,

	output logic pulse
);


localparam int CAP = 10'd1000;


logic [31:0] cnt_reg;

always_ff @(posedge clk or posedge rst)
	if (rst)
		cnt_reg <= '0;
	else
		cnt_reg <= cnt_reg == CAP - 1 ? '0 : cnt_reg + 1'b1;

always_ff @(posedge clk or posedge rst)
	if (rst)
		pulse <= '0;
	else
		pulse <= cnt_reg == CAP - 1;

`ifdef COCOTB_SIM
initial begin
  $dumpfile ("cnt.vcd");
  $dumpvars (0, cnt);
  #1;
end
`endif
endmodule
