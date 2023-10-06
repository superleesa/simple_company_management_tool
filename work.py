from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, desc, func, desc
from sqlalchemy.ext.declarative import declarative_base

from models import Base
from config import Session
from metric import Metric


class Work(Base, Metric):
    __tablename__ = "work_table"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user_table.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    worked_hours = Column(Integer)

    @staticmethod
    def get_top_k_workers(k, start_datetime, end_datetime):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= start_datetime, Work.start_datetime < end_datetime)
                              .group_by(Work.user_id)
                              .order_by(desc("TotalWorkHours"))
                              .limit(k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids

    @staticmethod
    def get_worst_k_workers(k, start_datetime, end_datetime):
        with Session() as session:
            worker_records = (session.query(Work.user_id, func.sum(Work.worked_hours).label("TotalWorkHours"))
                              .where(Work.start_datetime >= start_datetime, Work.start_datetime < end_datetime)
                              .group_by(Work.user_id)
                              .order_by("TotalWorkHours")
                              .limit(k)).all()

        top_worker_ids = [worker_row.user_id for worker_row in worker_records]

        return top_worker_ids
