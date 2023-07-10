import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge
from cocotb.regression import TestFactory
import sys


sys.path.insert(0, '../pytest')
import ram as py_tests


for obj in dir(py_tests):
    if obj.endswith("_test"):
        tf = TestFactory(getattr(py_tests, obj))
        tf.generate_tests()
