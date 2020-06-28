from __future__ import annotations

from typing import List


class Exchange:

    def __init__(self, success: bool, id_: int, cc_on_send: int, cc_on_receive: int, delay: int):
        self.success = bool(success)
        self.id_ = id_
        self.cc_on_send = cc_on_send
        self.cc_on_receive = cc_on_receive
        self.delay = delay

    def __int__(self):
        return -1 if not self.success else int(self.delay)

    @staticmethod
    def list_to_exchange(exchanges_input: List) -> List[Exchange]:
        return [Exchange._input_list_to_exchange(input_list) for input_list in exchanges_input if input_list[0]]

    @staticmethod
    def _input_list_to_exchange(input_list: List):
        return Exchange(success=bool(int(input_list[0])),
                        id_=input_list[1],
                        cc_on_send=input_list[3],
                        cc_on_receive=input_list[2],
                        delay=input_list[4])
