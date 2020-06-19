import os
from typing import List

from measurement import Measurement

TEST_DIR = "../tests/6000/"
TEST_FILENAME = "test2"
PACKET_ID = "ESPPIT"
MAX_TIME = 2**32
MAX_ANOMALY_DEVIATION_PERCENT = 20
PACKET_CNT_AFTER_FILTER = 5000
PACKET_VALUE_CNT = 7


def main():
    test_file_path = os.path.join(TEST_DIR, TEST_FILENAME)
    test_file = open(test_file_path, 'r', errors='ignore')
    file_lines = test_file.readlines()
    packets = [packet_data.split(' ') for packet_data in file_lines[1:-1]]
    packet_exchanges = get_exchange_times(packets)
    measurement = Measurement(packet_exchanges, TEST_FILENAME)
    print(measurement)

    #measurement = Measurement.filter_anomalies_median(measurement, MAX_ANOMALY_DEVIATION_PERCENT)
    measurement = Measurement.filter_anomalies_from_shortest_by_limit(measurement, PACKET_CNT_AFTER_FILTER)
    print("Removed anomalies")
    print(measurement)


def get_exchange_times(packet_list: List[List[str]]) -> List[int]:
    exchanges = []
    for i in range(0, len(packet_list)):
        if len(packet_list[i]) == PACKET_VALUE_CNT \
               and packet_list[i][-3] == PACKET_ID:
            exchanges.append(int(packet_list[i][PACKET_VALUE_CNT-1]))
    return exchanges


if __name__ == "__main__":
    main()



