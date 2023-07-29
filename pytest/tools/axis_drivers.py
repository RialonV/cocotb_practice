import cocotb
from cocotb.triggers import ClockCycles
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
            self.__signal_prefix = "axis_m_"
        elif driver_type == "Slave":
            self.__signal_prefix = "axis_s_"

        self._params_dict = {}

        for payload_field in vars(AXIS.Payload()):
            signal_name = self.__signal_prefix+payload_field
            if hasattr(self.__dut, signal_name):
                param_name = "WIDTH_" + signal_name.upper()
                if hasattr(self.__dut, param_name):
                    current_width = int(getattr(self.__dut, param_name))
                else:
                    current_width = getattr(self.__dut, signal_name).value.n_bits
                self._params_dict[payload_field.upper()] = {"WIDTH": current_width}
            else:
                pass

        self.__axis_payload = AXIS.Payload(0, 0, 0, 0, 0)
        self._clk = getattr(self.__dut, self.__signal_prefix + "clk")
        self._rst = getattr(self.__dut, self.__signal_prefix + "rst")
        self._tvalid = getattr(self.__dut, self.__signal_prefix + "tvalid")
        self._tready = getattr(self.__dut, self.__signal_prefix + "tready")

    @property
    def _axis_payload(self):
        axis_payload = AXIS.Payload()
        for payload_field in self._params_dict:
            pf_lower = payload_field.lower()
            if self._params_dict[payload_field]["WIDTH"] > 0:
                cur_state = getattr(self.__dut, self.__signal_prefix + pf_lower).value
                setattr(axis_payload, pf_lower, cur_state)
        self.__axis_payload = axis_payload
        return self.__axis_payload

    @_axis_payload.setter
    def _axis_payload(self, new_axis_payload: AXIS.Payload):
        if self.__driver_type == "Master":
            self.__axis_payload = new_axis_payload

            for payload_field in self._params_dict:
                if self._params_dict[payload_field]["WIDTH"] > 0:
                    cur_field_py_value = getattr(self.__axis_payload, payload_field.lower())
                    cur_field_hdl = getattr(self.__dut, "axis_m_" + payload_field.lower())
                    cur_field_hdl.value = LogicArray(
                        'X' * self._params_dict[payload_field]["WIDTH"]) if cur_field_py_value is None \
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
    def gen_rnd_pld(axis_payload_widths: AXIS.Payload):

        axis_payload = AXIS.Payload()

        for payload_field in vars(AXIS.Payload()):
            field_width = getattr(axis_payload_widths, payload_field)
            if field_width is not None:
                max_value = 2**field_width
                field_value = np.random.randint(0, max_value) if max_value > 1 else None
            else:
                field_value = None
            setattr(axis_payload, payload_field, field_value)

        return axis_payload


class AXISDriverM(AXISDriver):
    def __init__(self):
        super().__init__("Master")

    def gen_rnd_pld(self):
        axis_payload_widths = AXIS.Payload()
        for payload_field in self._params_dict:
            setattr(axis_payload_widths, payload_field.lower(), self._params_dict[payload_field]["WIDTH"])
        return AXISDriver.gen_rnd_pld(axis_payload_widths)

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
                await self.clear_states()
                return self._axis_payload

    async def send_rnd_pld(self, send_chance=100):
        return await self.send_pld(self.gen_rnd_pld(), send_chance)

    async def send_rnd_pkt(self, min_size: int, max_size: int, chance=100):
        pkt_size = None
        if min_size <= max_size:
            pkt_size = np.random.randint(min_size, max_size+1)
        elif min_size > max_size:
            raise ValueError(f"send_rnd_pkt - min_size={min_size} is less than max_size={max_size}")
        chances = [chance] * pkt_size
        axis_payloads = []
        for sample_num in range(pkt_size):
            axis_payload = self.gen_rnd_pld()
            if sample_num < (pkt_size - 1):
                axis_payload.tlast = 0
            else:
                axis_payload.tlast = 1
            axis_payloads.append(axis_payload)
        return await self.send_plds(axis_payloads, chances)

    async def send_plds(self, axis_payloads: List[AXIS.Payload], chances=None):
        if chances is None:
            chances = [100] * len(axis_payloads)
        sent_payloads = []
        for axis_payload, chance in zip(axis_payloads, chances):
            sent_payloads.append(await self.send_pld(axis_payload, chance))
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
                await self.clear_states()
            await ClockCycles(self._clk, 1)
            if self._handshake:
                await self.clear_states()
                return self._axis_payload

    async def rcv_pkt(self, rcv_chance=100, tready_stays=False):
        axis_payloads = []
        while True:
            axis_payload = await self.rcv_pld(rcv_chance, tready_stays)
            axis_payloads.append(axis_payload)
            if axis_payload.tlast == 1:
                break
        return axis_payloads
