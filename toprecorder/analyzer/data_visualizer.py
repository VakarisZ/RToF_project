import os
from typing import List, Dict, Tuple


from main import get_exchange_times, read_exchange_data
from exchange import Exchange
from measurement import Measurement

TEST_DIR = "../tests/20000/"
TEST_FILENAME = "test1.txt"
FILTER_MIN = 35600
FILTER_MAX = 35640
MIN_VALUE_FREQUENCY = 60


def visualize():
    test_file_path = os.path.join(TEST_DIR, TEST_FILENAME)
    exchange_data = read_exchange_data(test_file_path)
    packet_exchanges = Exchange.list_to_exchange(exchange_data)
    measurement = Measurement(exchanges=packet_exchanges, test_name=TEST_FILENAME)
    measurement.filter_unreceived()
    measurement.filter_by_range(low=FILTER_MIN, high=FILTER_MAX)
    measurement.plot()

    results = count_results(packet_exchanges)
    print_sorted(results)

    print("Filtered:")
    results = filter_results_by_frequency(results)
    print_sorted(results)


def count_results(exchanges: List[Exchange]) -> Dict[int, int]:
    results = {}
    for exchange in exchanges:
        if int(exchange) in results:
            results[int(exchange)] += 1
        else:
            results.update({(int(exchange), 1)})
    return results


def filter_results_by_frequency(exchanges: Dict[int, int]) -> Dict[int, int]:
    return {k: v for k, v in exchanges.items() if v >= MIN_VALUE_FREQUENCY}


def print_sorted(data: Dict[int, int]):
    for result_tuple in get_sorted(data):
        print(f"{result_tuple[0]} : {result_tuple[1]}")


def get_sorted(data: Dict[int, int]) -> List:
    return sorted(data.items(), key=lambda x: x[0])


if __name__ == "__main__":
    visualize()
