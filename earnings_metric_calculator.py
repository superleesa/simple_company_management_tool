from metriccalculator import MetricCalculator
from models import User, Project
from config import Session

from sqlalchemy import func, desc
import datetime


class EarningsMetricCalculator(MetricCalculator):
    """
    Note: this metric calculates earnings averages from the project start date to the end date.
    It is not actual earnings earned on a received date.
    """

    def __init__(self, workers, start_datetime, end_datetime, k=4):
        super().__init__(workers, start_datetime, end_datetime, k)

    def get_top_k_workers(self):
        with Session() as session:
            worker_records = (session
                              .query(Project.manager_id, func.sum(Project.earnings).label("TotalSales"))
                              .where(Project.received_earning_datetime >= self.start_datetime, Project.received_earning_datetime <= self.end_datetime)
                              .group_by(Project.manager_id)
                              .order_by(desc("TotalSales"))
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.manager_id for worker_row in worker_records]

        return top_worker_ids

    def get_worst_k_workers(self):
        with Session() as session:
            worker_records = (session
                              .query(Project.manager_id, func.sum(Project.earnings).label("TotalSales"))
                              .where(Project.received_earning_datetime >= self.start_datetime, Project.received_earning_datetime <= self.end_datetime)
                              .group_by(Project.manager_id)
                              .order_by("TotalSales")
                              .limit(self.k)).all()

        top_worker_ids = [worker_row.manager_id for worker_row in worker_records]

        return top_worker_ids

    def get_sum_workers_metric_in_a_timeframe(self):
        num_days = self.get_num_days_between()
        metric_history = [0] * num_days

        # traverse through each worker and add his/her work on each day to the records
        for worker_id in self.workers:
            project_records = self._get_project_records_for_a_worker(worker_id)

            for project_record in project_records:
                project_start_datetime, project_end_datetime, project_earnings = project_record

                # mutates the metric_history inside
                self._update_metric_history(project_start_datetime, project_end_datetime, metric_history,
                                            project_earnings)


        # create labels
        labels = self.create_date_labels()

        return metric_history, labels

    def get_per_worker_metric_in_a_timeframe(self):
        num_days = self.get_num_days_between()
        metric_history = []
        worker_names = []

        for worker_id in self.workers:
            # get worker name
            fullname = self._get_worker_name(worker_id)
            worker_names.append(fullname)

            # get worker metric history
            project_records = self._get_project_records_for_a_worker(worker_id)

            indivisual_metric_history = [0] * num_days
            for project_record in project_records:
                project_start_datetime, project_end_datetime, project_earnings = project_record


                # mutates the metric_history inside
                self._update_metric_history(project_start_datetime, project_end_datetime, indivisual_metric_history, project_earnings)
            metric_history.append(indivisual_metric_history)

        # create labels
        labels = self.create_date_labels()

        return metric_history, labels, worker_names

    def _get_project_records_for_a_worker(self, worker_id):
        """returns a project records, within the timeframe, for given worker"""
        with Session() as session:
            project_records = (session
                               .query(Project.start_datetime, Project.received_earning_datetime, Project.earnings)
                               .filter(Project.manager_id == worker_id,
                                       Project.received_earning_datetime != None,  # note: we must use "!=" here (cannot use "is")
                                       Project.start_datetime >= self.start_datetime,
                                       Project.received_earning_datetime <= self.end_datetime)
                               .all())

        return project_records

