from flask import (
    Blueprint,
    url_for,
    request,
    redirect,
    render_template,
    flash,
    abort
)

from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc
from datetime import datetime, timedelta
from json import dumps


from config import login_manager, Session
from models import User, Work, Project

employee_blueprint = Blueprint("employee", __name__)


@employee_blueprint.route("/", methods=["GET"])
@login_required
def index():
    user_id = current_user.id
    has_started_work_today = check_employee_is_working(user_id)

    work_data, sales_data, efficiency_data, total_sales_past_month = retrieve_past_work_data(current_user.id)





    return render_template("worker_page.html",
                           has_started_work=has_started_work_today,
                           work_data=dumps(work_data),
                           sales_data=dumps(sales_data),
                           efficiency_data=dumps(efficiency_data),
                           total_sales_past_month=total_sales_past_month)

@employee_blueprint.route("/start_work", methods=["POST"])
@login_required
def start_work():
    user_id = current_user.id

    
    has_started_work_today = check_employee_is_working(user_id)
    
    if has_started_work_today:
        flash("Have an ongoing work already", "error")
        return redirect(url_for(".index"))
    
    # inserting new work record
    start_datetime = datetime.strptime(request.form["start-datetime"], "%Y-%m-%dT%H:%M:%S")
    session = Session()
    session.add(Work(user_id=user_id, start_datetime=start_datetime))
    session.commit()

    # updating the work status
    user_record = session.query(User).filter(User.id == user_id).first()
    if user_record:
        user_record.is_working = True
    else:
        abort(500, "This user is not registered.")
    session.commit()
    session.close()
    
    # redirect to the worker page
    flash("Started Today's Work", "success")
    return redirect(url_for(".index"))
    
@employee_blueprint.route("/cancel_work", methods=["POST"])
@login_required
def cancel_work():
    # can only cancel if checked in already
    
    # TODO add "are you sure pop up box"

    # check user has started a job
    user_id = current_user.id
    has_started_work_today = check_employee_is_working(user_id)
    if not has_started_work_today:
        flash("Have not yet started today's work", "error")
        return redirect(url_for(".index"))

    # get the latest work
    session = Session()
    work_record = session.query(Work).filter(Work.user_id == user_id).order_by(desc(Work.start_datetime)).first()
    if work_record is None:
        abort(500, "You tried to cancel a work, but has not started working yet")
    session.delete(work_record)
    session.commit()

    # update the user working status
    user_record = session.query(User).filter(User.id == user_id).first()
    if user_record:
        user_record.is_working = False
    else:
        abort(404, "This user is not registered.")
    session.commit()
    session.close()
    flash("Work canceled", "success")
    return redirect(url_for(".index"))


@employee_blueprint.route("/finish_work", methods=["POST"])
@login_required
def finish_work():
    # TODO add "are you sure pop up box"

    # TODO update is_working status
    # check the user has started to work
    user_id = current_user.id
    has_started_work_today = check_employee_is_working(user_id)
    if not has_started_work_today:
        flash("Have not yet started today's work", "error")
        return redirect(url_for(".index"))

    # add the end_datetime value to the corresponding work record
    session = Session()
    work_record = session.query(Work).filter(Work.user_id == user_id).order_by(desc(Work.start_datetime)).first()
    if work_record is None:
        abort(404, "User has not started work yet")
    end_datetime = datetime.strptime(request.form["end-datetime"], "%Y-%m-%dT%H:%M:%S")
    work_record.end_datetime = end_datetime
    session.commit()

    # update the user working status
    user_record = session.query(User).filter(User.id == user_id).first()
    if user_record:
        user_record.is_working = False
    else:
        abort(404, "This user is not registered.")

    session.commit()
    session.close()

    flash("Finished today's work", "success")
    return redirect(url_for(".index"))

def retrieve_past_work_data(user_id: int):
    session = Session()

    try:
        # work data
        work_data = session.query(Work.start_datetime, Work.end_datetime).filter(Work.user_id == user_id).order_by(Work.start_datetime).all()
        work_data = [tuple(row) for row in work_data]


        # sales data
        sales_data = session.query(Project.amount, Project.start_datetime, Project.end_datetime).filter(Project.manager_id == user_id).order_by(Project.end_datetime).all()
        sales_data = [tuple(row) for row in sales_data]

    except:
        session.close()
        abort(404, "This user is not registered")
    else:
        # processing work data
        work_start_dates = []
        work_hours = []
        for work in work_data:
            work_start_date, work_end_date = work

            # last work session not finished yet
            if work_end_date is None:
                continue
            work_start_dates.append(work_start_date.date().isoformat())

            work_hour = work_end_date - work_start_date
            work_hours.append(work_hour.seconds // 3600)

        # TODO: modularize this part
        processed_work_data = [work_start_dates, work_hours]

        # processing sales data
        date_to_sales_map = {}
        sales_start_datetimes, sales_end_datetimes = [], []
        for sale in sales_data:
            sale_amount, sale_start_datetime, sale_end_datetime = sale
            sales_start_datetimes.append(sale_start_datetime)
            sales_end_datetimes.append(sale_end_datetime)
            sale_end_datetime = sale_end_datetime.date().isoformat()
            if sale_end_datetime not in date_to_sales_map:
                date_to_sales_map[sale_end_datetime] = 0

            date_to_sales_map[sale_end_datetime] += sale_amount

        # split keys and sales data
        sale_amounts = []
        sale_end_datetimes_str = []
        for sale_end_datetime, sale_amount in date_to_sales_map.items():
            sale_amounts.append(sale_amount)
            sale_end_datetimes_str.append(sale_end_datetime)

        processed_sale_data = [sale_end_datetimes_str, sale_amounts]


    # calculate efficiency (sales per hours, for each day)
    min_sales_start_date = min(sales_start_datetimes)
    max_sales_end_date = max(sales_end_datetimes)
    total_days = (max_sales_end_date - min_sales_start_date).days + 1

    efficiency_dates = [(min_sales_start_date+timedelta(offset)).date().isoformat() for offset in range(total_days)]
    total_sales_all_days = [0]*total_days
    for amount, start_date, end_date, in sales_data:
        # don't process projects that had not lead to any sales yet
        if amount is None or amount == 0:
            continue

        start_idx = (start_date - min_sales_start_date).days
        num_days = (end_date - start_date).days + 1
        end_idx = num_days + start_idx
        sales_per_day = amount / num_days
        for i in range(start_idx, end_idx):
            total_sales_all_days[i] += sales_per_day

    tot_work_hours_all_days = [0]*(max_sales_end_date - min_sales_start_date).days
    # assume a work does not go over 12pm
    for start_datetime, end_datetime in work_data:
        if start_datetime < min_sales_start_date:
            continue

        work_hours = (end_datetime - start_datetime).seconds / 3600
        day_index = (start_datetime - min_sales_start_date).days
        tot_work_hours_all_days[day_index] += work_hours


    efficiency_all_days = [0]*(max_sales_end_date - min_sales_start_date).days
    for i, (tot_sales_amount, tot_work_hours) in enumerate(zip(total_sales_all_days, tot_work_hours_all_days)):
        efficiency_all_days[i] = tot_sales_amount / tot_work_hours if tot_work_hours > 0 else 0

    efficiency_data = [efficiency_dates, efficiency_all_days]


    # find the sales in the past 30 days
    month_before = datetime.now() - timedelta(days=30)
    total_sales_past_month = 0
    for offset in range(total_days):
        current_date = (min_sales_start_date + timedelta(offset))

        if current_date < month_before:
            break

        total_sales_past_month += efficiency_data[1][offset]

    return processed_work_data, processed_sale_data, efficiency_data, total_sales_past_month



def check_employee_is_working(user_id: int):
    session = Session()

    try:
        user_record = session.query(User.is_working).filter(User.id == user_id).first()
        is_working = user_record[0]
    except:
        session.close()
        abort(404, "This user is not registered")


    session.close()
    return is_working

