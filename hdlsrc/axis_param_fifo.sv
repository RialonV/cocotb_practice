// Copyright (c) 2023=2023 All rights reserved
// =============================================================================
// Author : Andrey Vasilchenko (Andrey) andvasilc3@gmail.com
// File   : axis_param_fifo.sv
// Create : 2023-12-03 21:25:29
// Revise : 2023-12-03 21:25:30
// Editor : sublime text4, tab size (2)
// =============================================================================
module axis_param_fifo #(
	parameter     WIDTH_TDATA = 0,
	parameter     WIDTH_TUSER = 0,
	parameter     WIDTH_TID   = 0,
	parameter     WIDTH_TKEEP = 0,
	parameter int NUMWORDS    = 0,
	parameter bit REG_OUT     = 0
) (
	input  logic                   clk,
	input  logic                   rst,
	//
	input  logic                   axis_m_tvalid,
	input  logic [WIDTH_TDATA-1:0] axis_m_tdata,
	input  logic [WIDTH_TUSER-1:0] axis_m_tuser,
	input  logic [  WIDTH_TID-1:0] axis_m_tid,
	input  logic [WIDTH_TKEEP-1:0] axis_m_tkeep,
	input  logic                   axis_m_tlast,
	output logic                   axis_m_tready,
	//
	output logic                   axis_s_tvalid,
	output logic [WIDTH_TDATA-1:0] axis_s_tdata,
	output logic [WIDTH_TUSER-1:0] axis_s_tuser,
	output logic [  WIDTH_TID-1:0] axis_s_tid,
	output logic [WIDTH_TKEEP-1:0] axis_s_tkeep,
	output logic                   axis_s_tlast,
	input  logic                   axis_s_tready
);

localparam WIDTH_PAYLOAD = WIDTH_TDATA + 1 + WIDTH_TUSER + WIDTH_TID + WIDTH_TKEEP; // last width = 1

logic [WIDTH_PAYLOAD-1:0] pld_to_fifo, pld_from_fifo;

wire handshake_in  = axis_m_tvalid && axis_m_tready;
wire handshake_out = axis_s_tvalid && axis_s_tready;

logic wr_en, rd_en, rd_reg_en;
logic [WIDTH_PAYLOAD-1:0] wr_data, rd_data;
logic full, empty;

logic valid_from_fifo;
logic rd_reg_valid;

param_fifo #(.WIDTH_DATA(WIDTH_PAYLOAD), .NUMWORDS(NUMWORDS), .REG_OUT(REG_OUT)) i_param_fifo (
	.clk      (clk      ),
	.rst      (rst      ),
	.wr_en    (wr_en    ),
	.wr_data  (wr_data  ),
	.rd_en    (rd_en    ),
	.rd_reg_en(rd_reg_en),
	.rd_data  (rd_data  ),
	.full     (full     ),
	.empty    (empty    ),
	.usedw    (         )
);

always_comb
	begin
		axis_m_tready = !rst && !full;
		wr_en         = handshake_in;
		wr_data       = pld_to_fifo;
	end



always_comb
	begin
		axis_s_tvalid = valid_from_fifo;
		pld_from_fifo = rd_data;
		rd_en = !empty && (!valid_from_fifo || handshake_out);
	end

if (REG_OUT)
	begin

		always_ff @(posedge clk) 
			if (rst)
				rd_reg_valid <= '0;
			else if (rd_en)
				rd_reg_valid <= '1;
			else if (rd_reg_en)
				rd_reg_valid <= '0;

		always_ff @(posedge clk) 
			if (rst)
				valid_from_fifo <= '0;
			else if (rd_reg_valid)
				valid_from_fifo <= '1;
			else if (handshake_out)
				valid_from_fifo <= '0;

		assign rd_reg_en = (!valid_from_fifo || handshake_out);

	end
else
	begin

		always_ff @(posedge clk) 
			if (rst)
				rd_reg_valid <= '0;
			else if (rd_en)
				rd_reg_valid <= '1;
			else if (handshake_out)
				rd_reg_valid <= '0;

		assign valid_from_fifo = rd_reg_valid;

	end

axis_to_pld #(
	.WIDTH_TDATA   (WIDTH_TDATA   ),
	.WIDTH_TUSER   (WIDTH_TUSER   ),
	.WIDTH_TID     (WIDTH_TID     ),
	.WIDTH_TKEEP   (WIDTH_TKEEP   )
) i_axis_to_pld (
	.axis_in_tdata(axis_m_tdata),
	.axis_in_tlast(axis_m_tlast),
	.axis_in_tuser(axis_m_tuser),
	.axis_in_tid  (axis_m_tid  ),
	.axis_in_tkeep(axis_m_tkeep),
	.out_payload  (pld_to_fifo )
);

axis_from_pld #(
	.WIDTH_TDATA   (WIDTH_TDATA   ),
	.WIDTH_TUSER   (WIDTH_TUSER   ),
	.WIDTH_TID     (WIDTH_TID     ),
	.WIDTH_TKEEP   (WIDTH_TKEEP   )
) i_axis_from_pld (
	.axis_out_tdata(axis_s_tdata ),
	.axis_out_tlast(axis_s_tlast ),
	.axis_out_tuser(axis_s_tuser ),
	.axis_out_tid  (axis_s_tid   ),
	.axis_out_tkeep(axis_s_tkeep ),
	.in_payload    (pld_from_fifo)
);


`ifdef COCOTB_SIM
initial begin
  $dumpfile ("axis_param_fifo.vcd");
  $dumpvars (0, axis_param_fifo);
  #1;
end
`endif

endmodule
