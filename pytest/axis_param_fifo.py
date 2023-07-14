import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
from cocotb.types import LogicArray
from cocotb.binary import BinaryValue
import numpy as np
from axis import AXIS
from axis_drivers import AXISDriverM, AXISDriverS
from typing import List


async def transaction_driver(driver_func, perc, repeat_times):
    arr = []
    for _ in range(repeat_times):
        arr.append(await cocotb.start_soon(driver_func(perc)))
    return arr


async def init_driver(dut):
    axis_driver_m = AXISDriverM()
    axis_driver_s = AXISDriverS()
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    await cocotb.start_soon(axis_driver_m.clear_states())
    await cocotb.start_soon(axis_driver_s.clear_states())
    dut.rst.value = 1
    await ClockCycles(dut.clk, 100)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 10)
    return axis_driver_m, axis_driver_s, dut


async def constant_rw_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(axis_driver_m.send_rnd_pld, 100, nw))
    read_pld = await cocotb.start_soon(transaction_driver(axis_driver_s.rcv_pld, 100, nw))

    passed = written_pld.result() == read_pld
    assert passed


async def random_rw_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(axis_driver_m.send_rnd_pld, 50, nw))
    read_pld = await cocotb.start_soon(transaction_driver(axis_driver_s.rcv_pld, 50, nw))

    passed = written_pld.result() == read_pld
    assert passed


async def wr_rd_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(axis_driver_m.send_rnd_pld, 100, nw * 2))

    while True:
        await ClockCycles(dut.clk, 1)
        if dut.i_axis_param_fifo.full.value:
            break

    read_pld = await cocotb.start_soon(transaction_driver(axis_driver_s.rcv_pld, 100, nw * 2))

    passed = written_pld.result() == read_pld
    assert passed


async def rd_wr_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    read_pld = cocotb.start_soon(transaction_driver(axis_driver_s.rcv_pld, 100, nw * 2))

    await ClockCycles(dut.clk, nw)

    written_pld = cocotb.start_soon(transaction_driver(axis_driver_m.send_rnd_pld, 100, nw * 2))

    await ClockCycles(dut.clk, nw*3)

    passed = written_pld.result() == read_pld.result()
    assert passed
