from __future__ import annotations

from typing import List
import statistics

from exchange import Exchange


class Measurement:

    def __init__(self, exchanges: List[int], test_name):
        self.test_name = test_name
        self.exchanges = exchanges
        self.average_delay = None
        self.median_delay = None
        self.longest_delay = None
        self.shortest_delay = None
        self.calculate_statistic_values()

    def calculate_statistic_values(self):
        self.average_delay = Measurement.get_average_delay(self.exchanges)
        self.median_delay = statistics.median(self.exchanges)
        self.longest_delay = max(self.exchanges)
        self.shortest_delay = min(self.exchanges)

    @staticmethod
    def get_average_delay(exchanges: List[int]) -> float:
        return sum(exchanges)/len(exchanges)

    @staticmethod
    def filter_anomalies_median(measurement: Measurement, max_deviation_percent: int):
        delays = []
        for delay in measurement.exchanges:
            if abs(measurement.median_delay - delay) / measurement.median_delay * 100 < max_deviation_percent:
                delays.append(delay)
        measurement.exchanges = delays
        measurement.calculate_statistic_values()
        return measurement

    @staticmethod
    def filter_anomalies_from_shortest_by_limit(measurement: Measurement, limit: int):
        measurement.exchanges.sort()
        measurement.exchanges = measurement.exchanges[:limit]
        measurement.calculate_statistic_values()
        return measurement

    def __str__(self):
        return "{}\n" \
               "Average delay: {}\n" \
               "Median delay: {}\n" \
               "Highest delay: {}\n" \
               "Shortest_delay: {}\n" \
               "Total exchanges: {}\n".format(self.test_name, self.average_delay,
                                              self.median_delay, self.longest_delay,
                                              self.shortest_delay, len(self.exchanges))
