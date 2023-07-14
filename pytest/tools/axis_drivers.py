import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
from cocotb.types import LogicArray
from cocotb.binary import BinaryValue
import numpy as np
from axis import AXIS
from typing import List


class AXISDriver:
    def __init__(self, driver_type=None):
        allowed_driver_types = ["Master", "Slave"]
        if driver_type not in allowed_driver_types:
            raise ValueError(f"Invalid driver type ({driver_type}) in AXISDriver")
        self.__driver_type = driver_type
        self.__dut = cocotb.top
        if driver_type == "Master":
            width_prefix = "WIDTH_AXIS_M_"
            self.__signal_prefix = "axis_m_"
        elif driver_type == "Slave":
            width_prefix = "WIDTH_AXIS_S_"
            self.__signal_prefix = "axis_s_"
        variable_width_fields = ["TDATA", "TUSER", "TID", "TKEEP"]
        self._params_dict = {}
        for variable_width_field in variable_width_fields:
            current_width = int(getattr(self.__dut, width_prefix + variable_width_field))
            self._params_dict[variable_width_field] = {"WIDTH": current_width,
                                                       "MAX": 2 ** current_width - 1}
        self.__axis_payload = AXIS.Payload(0, 0, 0, 0, 0)
        self._clk = getattr(self.__dut, self.__signal_prefix + "clk")
        self._rst = getattr(self.__dut, self.__signal_prefix + "rst")
        self._tvalid = getattr(self.__dut, self.__signal_prefix + "tvalid")
        self._tready = getattr(self.__dut, self.__signal_prefix + "tready")

    @property
    def _axis_payload(self):
        axis_payload = AXIS.Payload()
        for field_type in self._params_dict:
            ft_lower = field_type.lower()
            if self._params_dict[field_type]["WIDTH"] > 0:
                cur_state = getattr(self.__dut, self.__signal_prefix + ft_lower).value
                setattr(axis_payload, ft_lower, cur_state)
        self.__axis_payload = axis_payload
        return self.__axis_payload

    @_axis_payload.setter
    def _axis_payload(self, new_axis_payload: AXIS.Payload):
        if self.__driver_type == "Master":
            self.__axis_payload = new_axis_payload

            self.__dut.axis_m_tlast.value = LogicArray(
                'X') if self.__axis_payload.tlast is None \
                else self.__axis_payload.tlast

            for field_type in self._params_dict:
                if self._params_dict[field_type]["WIDTH"] > 0:
                    cur_field_py_value = getattr(self.__axis_payload, field_type.lower())
                    cur_field_hdl = getattr(self.__dut, "axis_m_" + field_type.lower())
                    cur_field_hdl.value = LogicArray(
                        'X' * self._params_dict[field_type]["WIDTH"]) if cur_field_py_value is None \
                        else cur_field_py_value
        elif self.__driver_type == "Slave":
            raise ValueError("Slave payload can't be set")

    @property
    def _handshake(self):
        return self._tvalid.value & self._tready.value

    @_handshake.setter
    def _handshake(self, value: BinaryValue):
        if self.__driver_type == "Master":
            self._tvalid.value = value
        elif self.__driver_type == "Slave":
            self._tready.value = value

    async def clear_states(self):
        self._handshake = 0

        if self.__driver_type == "Master":
            self._axis_payload = AXIS.Payload(0, 0, 0, 0, 0)

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
                            tdata=np.random.randint(0, max_tdata) if max_tdata > 0 else 0,
                            tuser=np.random.randint(0, max_tuser) if max_tuser > 0 else 0,
                            tid=np.random.randint(0, max_tid) if max_tid > 0 else 0,
                            tkeep=np.random.randint(0, max_tkeep) if max_tkeep > 0 else 0)


class AXISDriverM(AXISDriver):
    def __init__(self):
        super().__init__("Master")

    async def send_pld(self, axis_payload: AXIS.Payload, send_chance=100):
        if send_chance > 100:
            send_chance = 100
        if send_chance <= 0:
            return Exception("Impossible chance")
        tvalid_set = False
        while True:
            cur_chance = np.random.randint(0, 100)
            if not tvalid_set and cur_chance <= send_chance:
                self._handshake = 1
                self._axis_payload = axis_payload
                tvalid_set = True
            await ClockCycles(self._clk, 1)
            if self._handshake:
                await cocotb.start_soon(self.clear_states())
                return self._axis_payload

    async def send_rnd_pld(self, send_chance=100):
        return await cocotb.start_soon(self.send_pld(
            AXISDriver.gen_rnd_pld(self._params_dict["TDATA"]["MAX"], self._params_dict["TUSER"]["MAX"],
                                   self._params_dict["TID"]["MAX"], self._params_dict["TKEEP"]["MAX"]), send_chance))

    async def send_rnd_pkt(self, min_size: int, max_size: int, chance=100):
        if min_size < max_size:
            pkt_size = np.random.randint(min_size, max_size)
        elif min_size == max_size:
            pkt_size = min_size
        elif min_size > max_size:
            raise ValueError(f"send_rnd_pkt - min_size={min_size} is less than max_size={max_size}")
        chances = [chance] * pkt_size
        axis_payloads = [AXISDriver.gen_rnd_pld(self._params_dict["TDATA"]["MAX"],
                                                self._params_dict["TUSER"]["MAX"],
                                                self._params_dict["TID"]["MAX"],
                                                self._params_dict["TKEEP"]["MAX"],
                                                "0" if _ < (pkt_size - 1) else "1") for _ in range(pkt_size)]
        return await cocotb.start_soon(self.send_plds(axis_payloads, chances))

    async def send_plds(self, axis_payloads: List[AXIS.Payload], chances=None):
        if chances is None:
            chances = [100] * len(axis_payloads)
        sent_payloads = []
        for axis_payload, chance in zip(axis_payloads, chances):
            sent_payloads.append(await cocotb.start_soon(self.send_pld(axis_payload, chance)))
        return sent_payloads


class AXISDriverS(AXISDriver):
    def __init__(self):
        super().__init__("Slave")

    async def rcv_pld(self, rcv_chance=100, tready_stays=False):
        if rcv_chance > 100:
            rcv_chance = 100
        if rcv_chance <= 0:
            return Exception("Impossible chance")
        while True:
            cur_chance = np.random.randint(0, 100)
            if cur_chance <= rcv_chance:
                self._handshake = 1
            elif not tready_stays:
                await cocotb.start_soon(self.clear_states())
            await ClockCycles(self._clk, 1)
            if self._handshake:
                await cocotb.start_soon(self.clear_states())
                return self._axis_payload
