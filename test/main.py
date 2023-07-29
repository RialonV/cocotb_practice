from cocotb.regression import TestFactory
import sys

sys.path.insert(0, '../pysrc')
sys.path.insert(0, '../pytest')
sys.path.insert(0, '../pytest/tools')
import axis_param_fifo as py_tests


for obj in vars(py_tests):
    if obj.endswith("_test"):
        tf = TestFactory(getattr(py_tests, obj))
        tf.generate_tests()
