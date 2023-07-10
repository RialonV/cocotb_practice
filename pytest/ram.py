import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
import numpy as np


WIDTH_DATA = int(cocotb.top.WIDTH_DATA)
NUMWORDS = int(cocotb.top.NUMWORDS)


data_cap = 2**WIDTH_DATA-1


class RAMBfm:
    def __init__(self):
        self.dut = cocotb.top
        self.WIDTH_DATA = int(cocotb.top.WIDTH_DATA)
        self.NUMWORDS = int(cocotb.top.NUMWORDS)
        self.data_cap = 2 ** self.WIDTH_DATA-1

    async def init_ram(self):
        self.dut.wr_en.value = 0
        self.dut.wr_addr.value = 0
        self.dut.wr_addr.value = 0
        self.dut.wr_data.value = 0
        self.dut.rd_en.value = 0
        self.dut.rd_addr.value = 0

    async def send_cmd(self, direction: str, addr: int, data=None):
        if direction == "write":
            self.dut.wr_en.value = 1
            self.dut.wr_addr.value = addr
            self.dut.wr_data.value = data
            await ClockCycles(self.dut.clk, 1)
            self.dut.wr_en.value = 0
        elif direction == "read":
            self.dut.rd_en.value = 1
            self.dut.rd_addr.value = addr
            await ClockCycles(self.dut.clk, 1)
            self.dut.rd_en.value = 0
            await ClockCycles(self.dut.clk, 1)
            data = self.dut.rd_data.value
            self.dut.rd_en.value = 0
        return data


async def ram_rnd_test(dut):
    passed = True
    ram_bfm = RAMBfm()
    await cocotb.start_soon(ram_bfm.init_ram())
    # noinspection PyAsyncCall
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    for i in range(NUMWORDS):
        data, addr = np.random.randint(0, ram_bfm.data_cap), np.random.randint(0, NUMWORDS-1)
        data = await cocotb.start_soon(ram_bfm.send_cmd("write", addr, data))
        if data != await cocotb.start_soon(ram_bfm.send_cmd("read", addr)):
            passed = False
            break
    assert passed


async def ram_full_test(dut):
    ram_bfm = RAMBfm()
    await cocotb.start_soon(ram_bfm.init_ram())
    # noinspection PyAsyncCall
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    data_written = []
    for i in range(NUMWORDS):
        data = np.random.randint(0, data_cap)
        data_written.append(await cocotb.start_soon(ram_bfm.send_cmd("write", i, data)))
    data_read = []
    for i in range(NUMWORDS):
        data_read.append(await cocotb.start_soon(ram_bfm.send_cmd("read", i)))
    assert data_written == data_read
