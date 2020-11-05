from __future__ import annotations

from typing import List
import statistics

import matplotlib.pyplot as plt

from exchange import Exchange


class Measurement:

    def __init__(self, exchanges: List[Exchange], test_name):
        self.test_name = test_name
        self.exchanges = exchanges
        self.average_delay = None
        self.median_delay = None
        self.longest_delay = None
        self.shortest_delay = None
        self.calculate_statistic_values()

    def plot(self):
        plt.plot(range(len(self.exchanges)), self.to_int_list())
        plt.show()

    def filter_unreceived(self):
        self.exchanges = [exchange for exchange in self.exchanges if exchange.success]

    def calculate_statistic_values(self):
        self.average_delay = self.get_average_delay()
        self.median_delay = statistics.median(self.to_int_list())
        self.longest_delay = max(self.to_int_list())
        self.shortest_delay = min(self.to_int_list())

    def get_average_delay(self) -> float:
        return sum(self.to_int_list())/len(self.exchanges)

    def to_int_list(self):
        return [int(exchange) for exchange in self.exchanges]

    def filter_by_range(self, low: int, high: int):
        self.exchanges = [exchange for exchange in self.exchanges if low < int(exchange) < high]

    def filter_period(self, period):
        return bool(8959900 < period < 8960100)

    def show_send_periods(self, n=300):
        cc_periods = []
        before_periods = []
        after_periods = []

        for i in range(len(self.exchanges) - 1):
            cc_period = int(self.exchanges[i+1].cc_on_send) - int(self.exchanges[i].cc_on_send)
            before_period = int(self.exchanges[i + 1].tx_before) - int(self.exchanges[i].tx_before)
            after_period = int(self.exchanges[i + 1].tx_after) - int(self.exchanges[i].tx_after)
            if self.filter_period(cc_period):
                cc_periods.append(cc_period)
            if self.filter_period(before_period):
                before_periods.append(before_period)
            if self.filter_period(after_period):
                after_periods.append(after_period)

        plt.plot(range(len(cc_periods)), cc_periods, 'r--',range(len(after_periods)), after_periods, 'g--', range(len(before_periods)), before_periods, 'b--')
        plt.show()

        for i in range(len(self.exchanges)):
            if i == n:
                break
            cc_period = int(self.exchanges[i+1].cc_on_send)-int(self.exchanges[i].cc_on_send)
            before_period = int(self.exchanges[i+1].tx_before)-int(self.exchanges[i].tx_before)
            after_period = int(self.exchanges[i+1].tx_after)-int(self.exchanges[i].tx_after)
            print(f"Periods: {cc_period} {before_period} {after_period}")

    def show_success_chance(self):
        successful = [x.success for x in self.exchanges if x.success]
        print(f"Success chance: {(len(successful) / len(self.exchanges)) * 100}")

    def show_anomalies_in_tx(self):
        anomalies = [x for x in self.exchanges if x.success and (x.cc_on_send > x.tx_after or x.cc_on_send < x.tx_before)]
        for anomaly in anomalies:
            print(f"Anomaly {anomaly.tx_before} {anomaly.cc_on_send} {anomaly.tx_after}")

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

    @staticmethod
    def filter_anomalies_advanced(measurement: Measurement, shortest_trim: int, longest_trim: int):
        pkt_cnt = len(measurement.exchanges)
        measurement.exchanges.sort()
        shortest_trim_cnt = int(pkt_cnt / 100 * shortest_trim)
        longest_trim_cnt = int(pkt_cnt / 100 * longest_trim)

        measurement.exchanges = measurement.exchanges[shortest_trim_cnt: (pkt_cnt - longest_trim_cnt)]
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
