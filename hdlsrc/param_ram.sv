// Copyright (c) 2023=2023 All rights reserved
// =============================================================================
// Author : Andrey Vasilchenko (Andrey) andvasilc3@gmail.com
// File   : param_ram.sv
// Create : 2023-12-03 21:25:55
// Revise : 2023-12-03 21:25:55
// Editor : sublime text4, tab size (2)
// =============================================================================
module param_ram #(
	parameter WIDTH_DATA = 16,
	parameter NUMWORDS   = 256
) (
	input  logic                        clk    ,

	input  logic                        wr_en  ,
	input  logic [$clog2(NUMWORDS)-1:0] wr_addr,
	input  logic [      WIDTH_DATA-1:0] wr_data,

	input  logic                        rd_en  ,
	input  logic [$clog2(NUMWORDS)-1:0] rd_addr,
	output logic [      WIDTH_DATA-1:0] rd_data
);

logic [WIDTH_DATA-1:0] mem [NUMWORDS];

always_ff @(posedge clk)
	if (wr_en)
		mem[wr_addr] <= wr_data;

always_ff @(posedge clk)
	if (rd_en)
		rd_data <= mem[rd_addr];


`ifdef COCOTB_SIM
initial begin
  $dumpfile ("param_ram.vcd");
  $dumpvars (0, param_ram);
  #1;
end
`endif
endmodule
