// Copyright (c) 2023=2023 All rights reserved
// =============================================================================
// Author : Andrey Vasilchenko (Andrey) andvasilc3@gmail.com
// File   : axis_param_fifo_wrapper.sv
// Create : 2023-12-03 21:25:33
// Revise : 2023-12-03 21:25:34
// Editor : sublime text4, tab size (4)
// =============================================================================
module axis_param_fifo_wrapper();

localparam     WIDTH_TDATA = 16;
localparam     WIDTH_TUSER = 4;
localparam     WIDTH_TID   = 0;
localparam     WIDTH_TKEEP = 0;
localparam int NUMWORDS    = 1024;
localparam bit REG_OUT     = 1;


localparam WIDTH_AXIS_M_TDATA = WIDTH_TDATA;
localparam WIDTH_AXIS_M_TUSER = WIDTH_TUSER;
localparam WIDTH_AXIS_M_TID   = WIDTH_TID  ;
localparam WIDTH_AXIS_M_TKEEP = WIDTH_TKEEP;

localparam WIDTH_AXIS_S_TDATA = WIDTH_TDATA;
localparam WIDTH_AXIS_S_TUSER = WIDTH_TUSER;
localparam WIDTH_AXIS_S_TID   = WIDTH_TID  ;
localparam WIDTH_AXIS_S_TKEEP = WIDTH_TKEEP;

logic clk;
logic rst;

logic                          axis_m_clk   ;
logic                          axis_m_rst   ;
logic                          axis_m_tvalid;
logic [WIDTH_AXIS_M_TDATA-1:0] axis_m_tdata ;
logic [WIDTH_AXIS_M_TUSER-1:0] axis_m_tuser ;
logic [  WIDTH_AXIS_M_TID-1:0] axis_m_tid   ;
logic [WIDTH_AXIS_M_TKEEP-1:0] axis_m_tkeep ;
logic                          axis_m_tlast ;
logic                          axis_m_tready;

logic                          axis_s_clk   ;
logic                          axis_s_rst   ;
logic                          axis_s_tvalid;
logic [WIDTH_AXIS_M_TDATA-1:0] axis_s_tdata ;
logic [WIDTH_AXIS_M_TUSER-1:0] axis_s_tuser ;
logic [  WIDTH_AXIS_M_TID-1:0] axis_s_tid   ;
logic [WIDTH_AXIS_M_TKEEP-1:0] axis_s_tkeep ;
logic                          axis_s_tlast ;
logic                          axis_s_tready;

assign axis_m_clk = clk;
assign axis_s_clk = clk;

assign axis_m_rst = rst;
assign axis_s_rst = rst;


axis_param_fifo #(
	.WIDTH_TDATA(WIDTH_TDATA),
	.WIDTH_TUSER(WIDTH_TUSER),
	.WIDTH_TID  (WIDTH_TID  ),
	.WIDTH_TKEEP(WIDTH_TKEEP),
	.NUMWORDS   (NUMWORDS   ),
	.REG_OUT    (REG_OUT    )
) i_axis_param_fifo (
	.clk          (clk          ),
	.rst          (rst          ),
	.axis_m_tvalid(axis_m_tvalid),
	.axis_m_tdata (axis_m_tdata ),
	.axis_m_tuser (axis_m_tuser ),
	.axis_m_tid   (axis_m_tid   ),
	.axis_m_tkeep (axis_m_tkeep ),
	.axis_m_tlast (axis_m_tlast ),
	.axis_m_tready(axis_m_tready),
	.axis_s_tvalid(axis_s_tvalid),
	.axis_s_tdata (axis_s_tdata ),
	.axis_s_tuser (axis_s_tuser ),
	.axis_s_tid   (axis_s_tid   ),
	.axis_s_tkeep (axis_s_tkeep ),
	.axis_s_tlast (axis_s_tlast ),
	.axis_s_tready(axis_s_tready)
);

endmodule
