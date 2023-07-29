import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
# noinspection PyUnresolvedReferences
from axis_drivers import AXISDriverM, AXISDriverS


async def transaction_driver(repeat_times, driver_func, *args):
    arr = []
    for _ in range(repeat_times):
        arr.append(await driver_func(*args))
    return arr


async def init_driver(dut):
    axis_driver_m = AXISDriverM()
    axis_driver_s = AXISDriverS()
    # noinspection PyAsyncCall
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    await axis_driver_m.clear_states()
    await axis_driver_s.clear_states()
    dut.rst.value = 1
    await ClockCycles(dut.clk, 100)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 10)
    return axis_driver_m, axis_driver_s, dut


async def constant_rw_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(nw, axis_driver_m.send_rnd_pld, 100))
    read_pld = await transaction_driver(nw, axis_driver_s.rcv_pld, 100)

    passed = written_pld.result() == read_pld
    assert passed


async def random_rw_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(nw, axis_driver_m.send_rnd_pld, 50))
    read_pld = await transaction_driver(nw, axis_driver_s.rcv_pld, 50)

    passed = written_pld.result() == read_pld
    assert passed


async def wr_rd_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    written_pld = cocotb.start_soon(transaction_driver(nw*2, axis_driver_m.send_rnd_pld, 100))

    while True:
        await ClockCycles(dut.clk, 1)
        if dut.i_axis_param_fifo.full.value:
            break

    read_pld = await transaction_driver(nw*2, axis_driver_s.rcv_pld, 100)

    passed = written_pld.result() == read_pld
    assert passed


async def rd_wr_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    nw = int(dut.NUMWORDS)

    read_pld = cocotb.start_soon(transaction_driver(nw*2, axis_driver_s.rcv_pld, 100))

    await ClockCycles(dut.clk, nw)

    written_pld = cocotb.start_soon(transaction_driver(nw*2, axis_driver_m.send_rnd_pld, 100))

    await ClockCycles(dut.clk, nw*3)

    passed = written_pld.result() == read_pld.result()
    assert passed


async def pkts_test(dut):
    axis_driver_m, axis_driver_s, dut = await init_driver(dut)

    written_pld = cocotb.start_soon(transaction_driver(100, axis_driver_m.send_rnd_pkt, 10, 20, 100))
    read_pld = await transaction_driver(100, axis_driver_s.rcv_pkt, 100, False)

    passed = written_pld.result() == read_pld
    assert passed
