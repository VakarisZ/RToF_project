from typing import List


class Exchange:

    def __init__(self, sent_time: int, received_time: int, max_time: int):
        self.sent_time = sent_time
        self.received_time = received_time
        self.delay = Exchange.calculate_delay(sent_time, received_time, max_time)

    @staticmethod
    def calculate_delay(sent_time, received_time, max_time):
        if received_time < sent_time:
            return max_time - sent_time + received_time
        else:
            return received_time - sent_time

    @staticmethod
    def packet_pair_to_exchange(sent_packet: List[str], received_packet: List[str]):
        return Exchange(sent_time=int(sent_packet[-1]), received_time=int(received_packet[-1]))
