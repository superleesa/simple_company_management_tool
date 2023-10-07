from metriccalculator import MetricCalculator
from models import Work, User
from config import Session

from sqlalchemy import func, desc
import datetime


class WorkHoursMetricCalculator(MetricCalculator):

    def __init__(self, workers, start_datetime, end_datetime, k=None):
        super().__init__(workers, start_datetime, end_datetime, k)

    def get_top_k_workers(self):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= self.start_datetime, Work.start_datetime <= self.end_datetime)
                              .group_by(Work.user_id)
                              .order_by(desc("TotalWorkHours"))
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    def get_worst_k_workers(self):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= self.start_datetime, Work.start_datetime <= self.end_datetime)
                              .group_by(Work.user_id)
                              .order_by("TotalWorkHours")
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    def get_per_worker_metric_in_a_timeframe(self):
        num_days = (self.end_datetime - self.start_datetime).days + 1
        metric_history = []

        for worker_id in self.workers:
            work_records = self._get_work_records_for_a_worker(worker_id)

            indivisual_metric_history = [None] * num_days
            for work_record in work_records:
                work_start_datetime, work_end_datetime = work_record

                total_hours_worked_in_this_session = (work_end_datetime - work_start_datetime).total_seconds() / 3600

                # mutates the metric_history inside
                self._update_metric_history(work_start_datetime, work_end_datetime, indivisual_metric_history,
                                            total_hours_worked_in_this_session)

            metric_history.append(indivisual_metric_history)

        # create labels
        labels = [(self.start_datetime + datetime.timedelta(days=offset)).date().isoformat() for offset in
                  range(num_days)]

        return metric_history, labels


    def get_sum_workers_metric_in_a_timeframe(self):
        num_days = (self.end_datetime - self.start_datetime).days + 1
        metric_history = [None] * num_days

        for worker_id in self.workers:
            work_records = self._get_work_records_for_a_worker(worker_id)

            for work_record in work_records:
                work_start_datetime, work_end_datetime = work_record

                total_hours_worked_in_this_session = (work_end_datetime - work_start_datetime).total_seconds() / 3600

                # mutates the metric_history inside
                self._update_metric_history(work_start_datetime, work_end_datetime, metric_history,
                                            total_hours_worked_in_this_session)

        # create labels
        labels = [(self.start_datetime + datetime.timedelta(days=offset)).date().isoformat() for offset in
                  range(num_days)]

        return metric_history, labels

    def _get_work_records_for_a_worker(self, worker_id):
        """returns a project records, within the timeframe, for given worker"""
        with Session() as session:
            work_records = (session
                               .query(Work.start_datetime, Work.end_datetime)
                               .filter(Work.user_id == worker_id,
                                       Work.end_datetime != None,  # note: we must use "!=" here
                                       Work.start_datetime >= self.start_datetime,
                                       Work.end_datetime <= self.end_datetime)
                               .all())
        return work_records
