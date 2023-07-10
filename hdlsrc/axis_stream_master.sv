module axis_stream_master (
	input clk,
	input rst_n,
	
	input logic axis_m_tvalid,
	input logic [7:0] axis_m_tdata,
	input logic [7:0] axis_m_tuser,
	input logic [7:0] axis_m_tid,
	input logic [7:0] axis_m_tkeep,
	input logic axis_m_tlast,
	output logic axis_m_tready
);


always_ff @(posedge clk)
	if (!rst_n)
		axis_m_tready <= '0;
	else
		axis_m_tready <= $random();



logic [7:0] axis_m_tdata_lc,
axis_m_tuser_lc,
axis_m_tid_lc,
axis_m_tkeep_lc;

logic axis_m_tlast_lc;

always_ff @(posedge clk)
	if (axis_m_tvalid && axis_m_tready)
		{axis_m_tdata_lc,
		 axis_m_tuser_lc,
		 axis_m_tid_lc,
		 axis_m_tkeep_lc,
		 axis_m_tlast_lc} <= {axis_m_tdata,
							  axis_m_tuser,
							  axis_m_tid,
							  axis_m_tkeep,
							  axis_m_tlast};


`ifdef COCOTB_SIM
initial begin
  $dumpfile ("axis_stream_master.vcd");
  $dumpvars (0, axis_stream_master);
  #1;
end
`endif
endmodule
