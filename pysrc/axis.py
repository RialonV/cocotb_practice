from typing import List
from cocotb.binary import BinaryValue


class AXIS:
    class Payload:
        def __init__(self, tdata=None, tlast=None, tuser=None, tid=None, tkeep=None):
            self.tdata = tdata
            self.tlast = tlast
            self.tuser = tuser
            self.tid = tid
            self.tkeep = tkeep

        @property
        def _all(self):
            return self.tdata, self.tlast, self.tuser, self.tid, self.tkeep

        def __eq__(self, other):
            return isinstance(other, AXIS.Payload) and self._all == other._all

        def __repr__(self):
            def hn(v):  # hex or None
                if type(v) is BinaryValue:
                    if v.is_resolvable:
                        return '%X' % v.integer
                    else:
                        return v.binstr
                elif v is None:
                    return "x"
                else:
                    return '%X' % v
            return "AXIS.Payload(d:{} l:{} u:{} i:{} k:{})".format(*(hn(v) for v in self._all))

    @staticmethod
    def _parse_line(line: str):
        parts = line.split()
        if len(parts) != 7:
            raise ValueError("invalid axis line")
        nones = set('ZzXx')
        values = [(int(p, 16) if nones.isdisjoint(p) else None) for p in parts]
        return AXIS.Payload(*values)

    @staticmethod
    def _build_line(payload: Payload):
        hexes = (('X' if f is None else hex(f)[2:]) for f in payload._all)
        return " ".join(hexes)

    @staticmethod
    def split_packets(payloads: List[Payload]):
        packets = []
        packet = []
        for s in payloads:
            packet.append(s)
            if s.tlast is None:
                raise ValueError("invalid tlast")
            if s.tlast:
                packets.append(packet)
                packet = []
        return packets

    @staticmethod
    def extract_all(payloads: List[Payload]):
        return list(zip(*[s._all for s in payloads]))
