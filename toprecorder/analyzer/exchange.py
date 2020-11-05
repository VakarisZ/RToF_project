from __future__ import annotations

from typing import List


class Exchange:

    def __init__(self,
                 success: bool,
                 id_: int,
                 cc_on_send: int,
                 cc_on_receive: int,
                 delay: int,
                 tx_before: int,
                 tx_after: int):
        self.success = bool(success)
        self.id_ = id_
        self.cc_on_send = cc_on_send
        self.cc_on_receive = cc_on_receive
        self.delay = delay
        self.tx_before = tx_before
        self.tx_after = tx_after

    def __int__(self):
        return -1 if not self.success else int(self.delay)

    @staticmethod
    def list_to_exchange(exchanges_input: List) -> Exchange:
        return Exchange._input_list_to_exchange(exchanges_input)

    @staticmethod
    def _input_list_to_exchange(input_list: List):

        return Exchange(success=bool(int(input_list[0])),
                        id_=input_list[1],
                        cc_on_send=input_list[3],
                        cc_on_receive=input_list[2],
                        delay=int(input_list[4]),
                        tx_before=input_list[5],
                        tx_after=input_list[6])
