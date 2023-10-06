from config import login_manager, Session
from models import User, Work, Sales
import datetime
from sqlalchemy import desc, func

from admin_blueprint import add_a_work_session
from metric import Metric

from typing import Type


class WorkerGroup:
    """
    call functions again, if you changed the timeframe

    """

    def __init__(self, workers, start_datetime, end_datetime, k=None, k_metric: Type[Metric] = None):
        """

        :param workers: if int -> worker id; if string, it must be one of "topk", "worstk", "all", "working"; if a list of integers -> a list of worker ids
        :param start_datetime:
        :param end_datetime:
        """

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        # note: after parsing self.workers must be a list of integers (which represent worker ids)
        if isinstance(workers, int) or isinstance(workers, list):
            # note: all elements must be integers
            self.workers = workers

        elif workers == "topk":
            if not k or not k_metric:
                raise ValueError("when workers=topk, k and based_on parameters must be set")
            self.workers = k_metric.get_top_k_workers(k, self.start_datetime, self.end_datetime)

        elif workers == "worstk":
            if not k or not k_metric:
                raise ValueError("when workers=worstk, k and based_on parameters must be set")
            self.workers = k_metric.get_worst_k_workers(k, self.start_datetime, self.end_datetime)

        elif workers == "all":
            self.workers = self.get_all_workers()

        else:
            raise ValueError("unknown value passed to workers")

    def get_all_workers(self):
        with Session() as session:
            worker_records = (session
                              .query(User.id)
                              .all())

        worker_ids = [worker.id for worker in worker_records]

        return worker_ids

    def get_total_worked_hours(self):

        num_days = (self.end_datetime - self.start_datetime).days + 1
        hours_worked_on_each_day = [None] * num_days

        # traverse through each worker and add his/her work on each day to the records
        for worker_id in self.workers:
            with Session() as session:
                worker = session.query(User).filter(User.id == worker_id).first()

                # mutates the hours_worked_on_each_day inside
                worker.add_worked_sessions_in_a_timeframe(self.start_datetime, self.end_datetime,
                                                          hours_worked_on_each_day)

        # create labels
        labels = [(self.start_datetime + datetime.timedelta(days=offset)).date().isoformat() for offset in
                  range(num_days)]

        return hours_worked_on_each_day, labels

    def get_worked_hours_per_worker(self):
        num_days = (self.end_datetime - self.start_datetime).days + 1

        per_worker_hours_worked_on_each_day = []

        # traverse through each worker and add his/her work on each day to the records
        for worker_id in self.workers:
            with Session() as session:
                worker = session.query(User).filter(User.id == worker_id).first()
                hours_worked_on_each_day = [None] * num_days

                # mutates the hours_worked_on_each_day inside
                worker.add_worked_sessions_in_a_timeframe(self.start_datetime, self.end_datetime,
                                                          hours_worked_on_each_day)

                per_worker_hours_worked_on_each_day.append(hours_worked_on_each_day)

        # create labels
        labels = [(self.start_datetime + datetime.timedelta(days=offset)).date().isoformat() for offset in
                  range(num_days)]

        return per_worker_hours_worked_on_each_day, labels

    def get_total_sales_amount(self):
        pass

    def get_sales_amount_per_worker(self):
        pass

    def get_efficiency_per_worker(self):
        pass

    def get_total_efficiency(self):
        pass
