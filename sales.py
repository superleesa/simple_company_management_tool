from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey, DateTime, func
from flask_login import UserMixin

from models import Base

from config import Session
from metric import Metric

class Sales(Base, Metric):
    __tablename__ = "sales_table"

    id = Column(Integer, primary_key=True)
    manager_id = Column(ForeignKey("user_table.id"))
    amount = Column(Integer)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)

    @staticmethod
    def get_top_k_workers(k, start_datetime, end_datetime):
        with Session() as session:

            worker_records = (session
                              .query(Sales.user_id, func.sum(Sales.amount).label("TotalSales"))
                              .where(Sales.start_datetime >= start_datetime, Sales.start_datetime < end_datetime)
                              .group_by(Sales.manager_id)
                              .order_by(desc("TotalSales"))
                              .limit(k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    @staticmethod
    def get_worst_k_workers(k, start_datetime, end_datetime):
        with Session() as session:
            worker_records = (session
                              .query(Sales.user_id, func.sum(Sales.amount).label("TotalSales"))
                              .where(Sales.start_datetime >= start_datetime, Sales.start_datetime < end_datetime)
                              .group_by(Sales.manager_id)
                              .order_by("TotalSales")
                              .limit(k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

