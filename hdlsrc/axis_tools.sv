module axis_from_pld #(
	parameter WIDTH_TDATA,
	parameter WIDTH_TUSER,
	parameter WIDTH_TID  ,
	parameter WIDTH_TKEEP
)(
	in_payload,
	axis_out_tdata,
	axis_out_tlast,
	axis_out_tuser,
	axis_out_tid,
	axis_out_tkeep

);
	
	localparam PAYLOAD_WIDTH = WIDTH_TDATA + 1 + WIDTH_TUSER + WIDTH_TID + WIDTH_TKEEP; // last width = 1
	localparam logic [2:0] WIDTH_CHECKS = {WIDTH_TUSER > 0, WIDTH_TID > 0, WIDTH_TKEEP > 0};

	input logic [PAYLOAD_WIDTH-1:0] in_payload;

	output logic [                        WIDTH_TDATA-1:0] axis_out_tdata;
	output logic [                                    0:0] axis_out_tlast;
	output logic [(WIDTH_TUSER > 0 ? WIDTH_TUSER - 1:0):0] axis_out_tuser;
	output logic [(WIDTH_TID   > 0 ? WIDTH_TID   - 1:0):0] axis_out_tid  ;
	output logic [(WIDTH_TKEEP > 0 ? WIDTH_TKEEP - 1:0):0] axis_out_tkeep;
	
	always_comb
		case (WIDTH_CHECKS)
			3'b000:
				{axis_out_tdata, axis_out_tlast} = in_payload;
			3'b001:
				{axis_out_tdata, axis_out_tlast, axis_out_tkeep} = in_payload;
			3'b010:
				{axis_out_tdata, axis_out_tlast, axis_out_tid} = in_payload;
			3'b011:
				{axis_out_tdata, axis_out_tlast, axis_out_tid, axis_out_tkeep} = in_payload;
			3'b100:
				{axis_out_tdata, axis_out_tlast, axis_out_tuser} = in_payload;
			3'b101:
				{axis_out_tdata, axis_out_tlast, axis_out_tuser, axis_out_tkeep} = in_payload;
			3'b110:
				{axis_out_tdata, axis_out_tlast, axis_out_tuser, axis_out_tid} = in_payload;
			3'b111:
				{axis_out_tdata, axis_out_tlast, axis_out_tuser, axis_out_tid, axis_out_tkeep} = in_payload;
		endcase

endmodule

module axis_to_pld #(
	parameter WIDTH_TDATA,
	parameter WIDTH_TUSER,
	parameter WIDTH_TID  ,
	parameter WIDTH_TKEEP
)(
	
	axis_in_tdata,
	axis_in_tlast,
	axis_in_tuser,
	axis_in_tid,
	axis_in_tkeep,
	out_payload
	
);

	localparam PAYLOAD_WIDTH = WIDTH_TDATA + 1 + WIDTH_TUSER + WIDTH_TID + WIDTH_TKEEP; // last width = 1
	localparam logic [2:0] WIDTH_CHECKS = {WIDTH_TUSER > 0, WIDTH_TID > 0, WIDTH_TKEEP > 0};

	output logic [PAYLOAD_WIDTH-1:0] out_payload;

	input logic [                        WIDTH_TDATA-1:0] axis_in_tdata;
	input logic [                                    0:0] axis_in_tlast;
	input logic [(WIDTH_TUSER > 0 ? WIDTH_TUSER - 1:0):0] axis_in_tuser;
	input logic [(WIDTH_TID   > 0 ? WIDTH_TID   - 1:0):0] axis_in_tid  ;
	input logic [(WIDTH_TKEEP > 0 ? WIDTH_TKEEP - 1:0):0] axis_in_tkeep;

	always_comb
		case (WIDTH_CHECKS)
			3'b000:
				out_payload = {axis_in_tdata, axis_in_tlast};
			3'b001:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tkeep};
			3'b010:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tid};
			3'b011:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tid, axis_in_tkeep};
			3'b100:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tuser};
			3'b101:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tuser, axis_in_tkeep};
			3'b110:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tuser, axis_in_tid};
			3'b111:
				out_payload = {axis_in_tdata, axis_in_tlast, axis_in_tuser, axis_in_tid, axis_in_tkeep};
		endcase

endmodule