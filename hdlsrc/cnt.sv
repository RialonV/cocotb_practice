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
