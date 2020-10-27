import os
from typing import List

from exchange import Exchange
from measurement import Measurement

TEST_DIR = "../tests/2020_10/"
TEST_FILENAME = "tx_before_send.txt"
PACKET_ID = "ESPPIT"
MAX_TIME = 2**32
MAX_ANOMALY_DEVIATION_PERCENT = 20
PACKET_CNT_AFTER_FILTER = 3000
PACKET_VALUE_CNT = 5


def main():
    test_file_path = os.path.join(TEST_DIR, TEST_FILENAME)
    packets = read_exchange_data(test_file_path)
    packet_exchanges = get_exchange_times(packets)
    measurement = Measurement(packet_exchanges, TEST_FILENAME)
    #measurement.filter_unreceived()
    measurement.show_send_period()
    return
    #print(measurement)

    #measurement = Measurement.filter_anomalies_median(measurement, MAX_ANOMALY_DEVIATION_PERCENT)
    #measurement = Measurement.filter_anomalies_from_shortest_by_limit(measurement, PACKET_CNT_AFTER_FILTER)
    #measurement = Measurement.filter_anomalies_advanced(measurement, 10, 50)
    #print("Removed anomalies")
    #print(measurement)


def read_exchange_data(path: str) -> List[List[str]]:
    test_file = open(path, 'r', errors='ignore')
    file_lines = test_file.readlines()
    packets = [packet_data.split(' ') for packet_data in file_lines[1:-1]]
    return packets


def get_exchange_times(packet_list: List[List[str]]) -> List[Exchange]:
    exchanges = []
    for i in range(0, len(packet_list)-1):
        if len(packet_list[i]) == PACKET_VALUE_CNT:
            exchanges.append(Exchange.list_to_exchange(packet_list[i]))
    return exchanges


if __name__ == "__main__":
    main()



