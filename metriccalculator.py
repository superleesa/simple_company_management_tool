from abc import ABC, abstractmethod
from models import User
from config import Session

import datetime

class MetricCalculator(ABC):
    """Provides filtering of users / computation of scores for users, using a specific metric"""

    def __init__(self, workers, start_datetime, end_datetime, k=4):
        """
        both start_datetime and end_datetime should be inclusive

        :param workers:
        :param start_datetime:
        :param end_datetime:
        :param k:
        """

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.k = k

        # note: after parsing self.workers must be a list of integers (which represent worker ids)
        if isinstance(workers, int):
            # need to put this within a list since methods in this class are meant to iterate through self.workers
            self.workers = [workers]

        elif isinstance(workers, list):
            # note: all elements must be integers
            if not all([isinstance(elem, int) for elem in workers]):
                raise ValueError("if a list is passed to the workers argument, all elements must be integers")
            self.workers = workers

        elif workers == "topk":
            # if not self.k:
            #     raise ValueError("when workers=topk, k and based_on parameters must be set")
            self.workers = self.get_top_k_workers()

        elif workers == "worstk":
            # if not self.k:
            #     raise ValueError("when workers=worstk, k and based_on parameters must be set")
            self.workers = self.get_worst_k_workers()

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

    def get_num_days_between(self):
        return (self.end_datetime - self.start_datetime).days + 1

    def create_date_labels(self):
        num_days = self.get_num_days_between()
        return[(self.start_datetime + datetime.timedelta(days=offset)).date().isoformat() for offset in
                  range(num_days)]


    def _update_metric_history(self, start_datetime, end_datetime, metric_history, metric_amount_per_session):
        """
            if metric is None, work hours is used as metric
            :param start_datetime:
            :param end_datetime:
            :param metric_history:
            :param metric:
            :return:
        """
        current_datetime = start_datetime

        total_hours_worked_for_this_session = (end_datetime - start_datetime).total_seconds() / 3600

        # each iteration represents an indivisual day
        while current_datetime <= end_datetime:
            # Calculate the end of the current day
            end_of_day = datetime.datetime(
                year=current_datetime.year,
                month=current_datetime.month,
                day=current_datetime.day,
                hour=23,
                minute=59,
                second=59
            )

            # Calculate the hours worked on the current day
            hours_worked_on_this_day = min((end_of_day - current_datetime).total_seconds() / 3600,
                                           (end_datetime - current_datetime).total_seconds() / 3600)

            ratio_today_to_overall = hours_worked_on_this_day / total_hours_worked_for_this_session
            earnings_on_this_day = ratio_today_to_overall * metric_amount_per_session

            # update the date_to_work_hours
            date_index = self._get_date_index(current_datetime)
            metric_history[date_index] += earnings_on_this_day

            # move to the next day
            current_datetime += datetime.timedelta(days=1)
            current_datetime = current_datetime.replace(hour=0, minute=0, second=0)

    def _get_date_index(self, current_date):
        return (current_date - self.start_datetime).days

    def _get_worker_name(self, worker_id):
        with Session() as session:
            user = (session.query(User).filter(User.id == worker_id).first())

            return user.get_fullname()
