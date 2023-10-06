from metricretriever import MetricRetriever
from models import Work, User
from config import Session

from sqlalchemy import func, desc
import datetime


class WorkHoursRetriever(MetricRetriever):

    def __init__(self, workers, start_datetime, end_datetime, k=None):
        super().__init__(workers, start_datetime, end_datetime, k)

    def get_top_k_workers(self):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= self.start_datetime, Work.start_datetime < self.end_datetime)
                              .group_by(Work.user_id)
                              .order_by(desc("TotalWorkHours"))
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    def get_worst_k_workers(self):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= self.start_datetime, Work.start_datetime < self.end_datetime)
                              .group_by(Work.user_id)
                              .order_by("TotalWorkHours")
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    def get_per_worker_metric_in_a_timeframe(self):
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


    def get_sum_workers_metric_in_a_timeframe(self):
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
