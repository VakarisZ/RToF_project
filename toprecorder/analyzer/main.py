import os
from typing import List

from exchange import Exchange
from measurement import Measurement

TEST_DIR = "../tests/"
TEST_FILENAME = "test5"
SENT_PACKET_ID = "ESPTXX"
RECEIVED_PACKET_ID = "BOUNCE"
MAX_TIME = 2**32
MAX_ANOMALY_DEVIATION_PERCENT = 40
PACKET_VALUE_CNT = 7


def main():
    test_file_path = os.path.join(TEST_DIR, TEST_FILENAME)
    test_file = open(test_file_path, 'r', errors='ignore')
    file_lines = test_file.readlines()
    packets = [packet_data.split(' ') for packet_data in file_lines[1:-1]]
    packet_exchanges = get_exchanges(packets)
    measurement = Measurement(packet_exchanges, TEST_FILENAME)
    print(measurement)

    measurement = Measurement.filter_anomalies(measurement, MAX_ANOMALY_DEVIATION_PERCENT)
    print("Removed anomalies")
    print(measurement)


def get_exchanges(packet_list: List[List[str]]):
    exchanges = []
    for i in range(1, len(packet_list)):
        if len(packet_list[i]) == PACKET_VALUE_CNT and len(packet_list[i-1]) == PACKET_VALUE_CNT and\
                packet_list[i][-3] == RECEIVED_PACKET_ID and packet_list[i-1][-3] == SENT_PACKET_ID:
            sent_time = int(packet_list[i-1][-1])
            receive_time = int(packet_list[i][-1])
            exchanges.append(Exchange(sent_time, receive_time, MAX_TIME))
    return exchanges


if __name__ == "__main__":
    main()



