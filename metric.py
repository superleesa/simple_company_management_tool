from abc import ABC, abstractmethod

class Metric(ABC):
    @staticmethod
    @abstractmethod
    def get_top_k_workers(k, start_datetime, end_datetime):
        ...

    @staticmethod
    @abstractmethod
    def get_worst_k_workers(k, start_datetime, end_datetime):
        ...
