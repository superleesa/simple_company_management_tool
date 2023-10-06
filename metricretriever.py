from abc import ABC, abstractmethod
from models import User
from config import Session

class MetricRetriever(ABC):

    def __init__(self, workers, start_datetime, end_datetime, k=None):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.k = k

        # note: after parsing self.workers must be a list of integers (which represent worker ids)
        if isinstance(workers, int) or isinstance(workers, list):
            # note: all elements must be integers
            self.workers = workers

        elif workers == "topk":
            if not self.k:
                raise ValueError("when workers=topk, k and based_on parameters must be set")
            self.workers = self.get_top_k_workers(k, self.start_datetime, self.end_datetime)

        elif workers == "worstk":
            if not self.k:
                raise ValueError("when workers=worstk, k and based_on parameters must be set")
            self.workers = self.get_worst_k_workers(k, self.start_datetime, self.end_datetime)

        elif workers == "all":
            self.workers = self.get_all_workers()

        else:
            raise ValueError("unknown value passed to workers")

    @abstractmethod
    def get_top_k_workers(self):
        ...

    @abstractmethod
    def get_worst_k_workers(self):
        ...

    @abstractmethod
    def get_per_worker_metric_in_a_timeframe(self):
        ...

    @abstractmethod
    def get_sum_workers_metric_in_a_timeframe(self):
        ...

    def get_all_workers(self):
        with Session() as session:
            worker_records = (session
                              .query(User.id)
                              .all())

        worker_ids = [worker.id for worker in worker_records]

        return worker_ids
