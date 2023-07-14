# Makefile


# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PWD=$(shell pwd)

VERILOG_SOURCES += ../hdlsrc/cnt.sv
VERILOG_SOURCES += ../hdlsrc/param_fifo.sv
VERILOG_SOURCES += ../hdlsrc/param_ram.sv
VERILOG_SOURCES += ../hdlsrc/axis_stream_master.sv
VERILOG_SOURCES += ../hdlsrc/axis_tools.sv
VERILOG_SOURCES += ../hdlsrc/axis_param_fifo.sv
VERILOG_SOURCES += ../hdlsrc/axis_param_fifo_wrapper.sv

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL := axis_param_fifo_wrapper

# MODULE is the basename of the Python test file
MODULE := main

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim