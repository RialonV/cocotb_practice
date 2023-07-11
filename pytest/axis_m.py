import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
from cocotb.types import LogicArray
import numpy as np
from axis import AXIS
from typing import List


class AXISDriverM:
    def __init__(self):
        self.__dut = cocotb.top
        self.__data_width = int(cocotb.top.WIDTH_AXIS_M_TDATA)
        self.__user_width = int(cocotb.top.WIDTH_AXIS_M_TUSER)
        self.__id_width = int(cocotb.top.WIDTH_AXIS_M_TID)
        self.__keep_width = int(cocotb.top.WIDTH_AXIS_M_TKEEP)
        self.__data_max = 2 ** self.__data_width - 1
        self.__user_max = 2 ** self.__user_width - 1
        self.__id_max = 2 ** self.__id_width - 1
        self.__keep_max = 2 ** self.__keep_width - 1
        self.__axis_payload = AXIS.Payload(0, 0, 0, 0, 0)

    @property
    def _axis_payload(self):
        return self.__axis_payload

    @_axis_payload.setter
    def _axis_payload(self, new_axis_payload: AXIS.Payload):
        self.__axis_payload = new_axis_payload
        self.__dut.axis_m_tdata.value = LogicArray(
            'X' * self.__data_width) if self._axis_payload.tdata is None else self._axis_payload.tdata
        self.__dut.axis_m_tlast.value = LogicArray(
            'X') if self._axis_payload.tlast is None else self._axis_payload.tlast
        if self.__user_max > 0:
            self.__dut.axis_m_tuser.value = LogicArray(
                'X' * self.__user_width) if self._axis_payload.tuser is None else self._axis_payload.tuser
        if self.__id_max > 0:
            self.__dut.axis_m_tid.value = LogicArray(
                'X' * self.__id_width) if self._axis_payload.tid is None else self._axis_payload.tid
        if self.__keep_max > 0:
            self.__dut.axis_m_tkeep.value = LogicArray(
                'X' * self.__keep_width) if self._axis_payload.tkeep is None else self._axis_payload.tkeep

    @staticmethod
    def gen_rnd_pld(max_tdata, max_tuser, max_tid, max_tkeep, state_tlast="rnd"):
        allowed_states_tlast = ["rnd", "1", "0"]
        if state_tlast not in allowed_states_tlast:
            raise ValueError(
                f"gen_rnd_pld - invalid value in state_tlast: {state_tlast}; \n"
                f"Allowed values: {allowed_states_tlast}")
        if state_tlast == "rnd":
            tlast_value = np.random.randint(0, 2)
        elif state_tlast == "1":
            tlast_value = 1
        elif state_tlast == "0":
            tlast_value = 0
        else:
            tlast_value = None
        return AXIS.Payload(tlast=tlast_value,
                            tdata=np.random.randint(0, max_tdata),
                            tuser=np.random.randint(0, max_tuser),
                            tid=np.random.randint(0, max_tid),
                            tkeep=np.random.randint(0, max_tkeep))

    async def clear_states(self):
        self.__dut.axis_m_tvalid.value = 0

        self._axis_payload = AXIS.Payload(0, 0, 0, 0, 0)

    async def send_pld(self, axis_payload: AXIS.Payload, send_chance=100):
        if send_chance > 100:
            send_chance = 100
        if send_chance <= 0:
            return
        while True:
            cur_chance = np.random.randint(0, 100)
            if cur_chance <= send_chance:
                break
            await ClockCycles(self.__dut.axis_m_clk, 1)
        self.__dut.axis_m_tvalid.value = 1
        self._axis_payload = axis_payload
        while True:
            await ClockCycles(self.__dut.axis_m_clk, 1)
            if self.__dut.axis_m_tready.value == 1:
                await cocotb.start_soon(self.clear_states())
                break
        return axis_payload

    async def send_rnd_pld(self, send_chance=100):
        return await cocotb.start_soon(self.send_pld(AXISDriverM.gen_rnd_pld(self.__data_max,
                                                                             self.__user_max,
                                                                             self.__id_max,
                                                                             self.__keep_max), send_chance))

    async def send_rnd_pkt(self, min_size: int, max_size: int, chance=100):
        if min_size < max_size:
            pkt_size = np.random.randint(min_size, max_size)
        elif min_size == max_size:
            pkt_size = min_size
        elif min_size > max_size:
            raise ValueError(f"send_rnd_pkt - min_size={min_size} is less than max_size={max_size}")
        chances = [chance] * pkt_size
        axis_payloads = [AXISDriverM.gen_rnd_pld(self.__data_max,
                                                 self.__user_max,
                                                 self.__id_max,
                                                 self.__keep_max,
                                                       "0" if _ < (pkt_size - 1) else "1") for _ in
                         range(pkt_size)]
        return await cocotb.start_soon(self.send_plds(axis_payloads, chances))

    async def send_plds(self, axis_payloads: List[AXIS.Payload], chances=None):
        if chances is None:
            chances = [100] * len(axis_payloads)
        sent_payloads = []
        for axis_payload, chance in zip(axis_payloads, chances):
            sent_payloads.append(await cocotb.start_soon(self.send_pld(axis_payload, chance)))
        return sent_payloads


async def axi_stream_send_test(dut):
    passed = True
    axi_stream_m = AXISDriverM()
    await cocotb.start_soon(axi_stream_m.clear_states())
    # noinspection PyAsyncCall
    cocotb.start_soon(Clock(dut.axis_m_clk, 2, units="ns").start())
    dut.axis_m_rst.value = 1
    await ClockCycles(dut.axis_m_clk, 100)
    dut.axis_m_rst.value = 0
    for i in range(2):
        print(await cocotb.start_soon(axi_stream_m.send_rnd_pld()))
    await ClockCycles(dut.axis_m_clk, 100)
    for i in range(2):
        print(await cocotb.start_soon(axi_stream_m.send_rnd_pld(25)))
    await ClockCycles(dut.axis_m_clk, 100)
    for i in range(2):
        print(await cocotb.start_soon(axi_stream_m.send_rnd_pkt(3, 6)))
    await ClockCycles(dut.axis_m_clk, 100)
    for i in range(2):
        print(await cocotb.start_soon(axi_stream_m.send_rnd_pkt(3, 6, np.random.randint(30, 100))))
    await ClockCycles(dut.axis_m_clk, 100)
    for i in range(2):
        print(await cocotb.start_soon(axi_stream_m.send_rnd_pkt(3, 3)))
    await ClockCycles(dut.axis_m_clk, 100)
    try:
        for i in range(2):
            print(await cocotb.start_soon(axi_stream_m.send_rnd_pkt(3, 2)))
        await ClockCycles(dut.axis_m_clk, 100)
    except ValueError as e:
        print(e)
        pass
    try:
        tlast_states = ["rnd", "1", "0", None]
        for tlast_state in tlast_states:
            print(AXISDriverM.gen_rnd_pld(10, 10, 10, 10, tlast_state))
    except ValueError as e:
        print(e)
        pass
    for i in range(32):
        axis_payload = AXIS.Payload()
        print(await cocotb.start_soon(axi_stream_m.send_pld(axis_payload)))
    assert passed
