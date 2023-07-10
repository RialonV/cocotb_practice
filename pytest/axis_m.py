import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
import numpy as np


class AxiStreamM:
    def __init__(self):
        self.dut = cocotb.top

    async def clear_states(self):
        self.dut.axis_m_tvalid.value = 0
        self.dut.axis_m_tdata.value = 0
        self.dut.axis_m_tuser.value = 0
        self.dut.axis_m_tid.value = 0
        self.dut.axis_m_tkeep.value = 0
        self.dut.axis_m_tlast.value = 0

    async def send_beat(self, tdata: int, tuser=None, tid=None, tkeep=None, tlast=None):
        self.dut.axis_m_tvalid.value = 1
        self.dut.axis_m_tdata.value = tdata
        if tuser is not None:
            self.dut.axis_m_tuser.value = tuser
        if tid is not None:
            self.dut.axis_m_tid.value = tid
        if tkeep is not None:
            self.dut.axis_m_tkeep.value = tkeep
        if tlast is not None:
            self.dut.axis_m_tlast.value = tlast
        while True:
            await ClockCycles(self.dut.clk, 1)
            if self.dut.axis_m_tready.value == 1:
                await cocotb.start_soon(self.clear_states())
                break


async def axi_stream_send_test(dut):
    passed = True
    axi_stream_m = AxiStreamM()
    await cocotb.start_soon(axi_stream_m.clear_states())
    # noinspection PyAsyncCall
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    for i in range(32):
        tdata = np.random.randint(0, 256)
        tuser = np.random.randint(0, 256)
        tid = np.random.randint(0, 256)
        tkeep = np.random.randint(0, 256)
        tlast = np.random.randint(0, 2)
        await cocotb.start_soon(axi_stream_m.send_beat(tdata, tuser, tid, tkeep, tlast))
        print(tdata, tuser, tid, tkeep, tlast)
    await ClockCycles(axi_stream_m.dut.clk, 10)
    for i in range(32):
        tdata = np.random.randint(0, 256)
        tuser = np.random.randint(0, 256)
        tid = np.random.randint(0, 256)
        tkeep = np.random.randint(0, 256)
        tlast = np.random.randint(0, 2)
        await cocotb.start_soon(axi_stream_m.send_beat(tdata, tuser, tid, tkeep, tlast))
        print(tdata, tuser, tid, tkeep, tlast)
        await ClockCycles(axi_stream_m.dut.clk, 1)
    assert passed
