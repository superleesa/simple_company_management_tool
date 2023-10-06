from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from flask_login import UserMixin
from config import Session

from models import Base
import datetime

class User(Base, UserMixin):
    __tablename__ = "user_table"
    __table_args__ = (UniqueConstraint("username"),)
    
    id = Column(Integer, primary_key=True)
    username = Column("username", String, nullable=False)
    password = Column(String)
    # profile_img_id = Column(String, nullable=False)
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email_address = Column(String, nullable=False)
    
    is_admin = Column(Boolean, nullable=False)
    is_working = Column(Boolean, nullable=False)
    
    def get_id(self):
        return str(self.id)

    def to_dict_without_password(self):
        return {"id": self.id, "username": self.username,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email_address": self.email_address,
                "is_working": self.is_working}

    def add_worked_sessions_in_a_timeframe(self, start_datetime, end_datetime, hours_worked_on_each_day):
        with Session() as session:
            work_records = (session.query(Work.start_datetime, Work.end_datetime)
                            .where(Work.user_id == worker_id,
                                   Work.start_datetime >= start_datetime,
                                   Work.start_datetime < end_datetime)).all()

        for work_record in work_records:
            self.add_a_work_session(work_record.start_datetime, work_record.end_datetime, hours_worked_on_each_day)

    def add_a_work_session(self, start_datetime, end_datetime, hours_worked_on_each_day):
        """
        add a given work session to hours_worked

        note on implementation:
        splits one work session to days, if it goes over multiple days
        it mutates hours_worked; in-place algorithm
        :param hours_worked_on_each_day: an existing dictionary that maps from a day to working hours on that day
        :param start_datetime:
        :param end_datetime:
        :return:
        """

        current_datetime = start_datetime

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
            hours_worked_on_each_day = min((end_of_day - current_datetime).total_seconds() / 3600,
                                           (end_datetime - current_datetime).total_seconds() / 3600)

            # update the date_to_work_hours
            date_index = get_date_index(current_datetime, start_datetime)
            hours_worked_on_each_day[date_index] += hours_worked_on_each_day

            # Move to the next day
            current_datetime += datetime.timedelta(days=1)
            current_datetime = current_datetime.replace(hour=0, minute=0, second=0)

def get_date_index(date, start_datetime):
    return (date - start_datetime).days
