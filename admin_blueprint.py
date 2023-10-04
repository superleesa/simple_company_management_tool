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
import json
from config import login_manager, Session
from models import User, Work, Sales
from json import dumps

import datetime

admin_page = Blueprint("admin", __name__)


# todo add login setting later
# todo ensure that there is a check if user is admin or not
@admin_page.route("/add_user", methods=["POST", "GET"])
@login_required
def add_user():
    if request.method == "GET":
        return render_template("admin_add_user.html")


    try:
        username = request.form["username"]
        password = request.form["password1"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        email_address = request.form["email-address"]
        is_admin = bool(request.form.get("is-admin"))

    except KeyError as e:
        print(e)
        flash("At least one input was not filled in", "error")
        return render_template("admin_add_user.html")


    # check if a user with the inputted username alreadey exits or not
    #TODO don't store passwords literally - store hashed ones
    session = Session()
    existing_user = session.query(User).filter(User.username == username).first()

    if existing_user is not None:
        flash("There was an existing user with the same username", "error")
        session.close()
        return render_template("admin_add_user.html")


    session.add(User(username=username,
                     password=password,
                     first_name=first_name,
                     last_name=last_name,
                     email_address=email_address,
                     is_working=False,
                     is_admin=is_admin))
    session.commit()
    session.close()
    flash("User added successfully", "success")
    return render_template("admin_add_user.html")


@admin_page.route("/show_users")
@login_required
def show_users():
    session = Session()
    users = session.query(User).all()
    user_objects = [user.to_dict_without_password() for user in users]
    # print(json.dumps(user_objects))
    return render_template("check_users2.html", users=user_objects)

@admin_page.route("/")
@login_required
def index():
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

    # retrieve data
    worked_hours = retrieve_company_work_hours()

    return render_template("admin_index.html", worked_hours=dumps(worked_hours))


def retrieve_company_work_hours():
    session = Session()

    # retrieve all work sessions (across workers) from the database
    work_records = session.query(Work).filter(Work.start_datetime, Work.end_datetime).all()

    # prepare data structure to store work sessions
    # find min start datetime and max end datetime
    min_work_start_datetime = min(work_records, key=lambda x: x.start_datetime).start_datetime
    max_work_end_datetime = max(work_records, key=lambda x: x.end_datetime).end_datetime

    num_days = (max_work_end_datetime - min_work_start_datetime).days + 1  # number of days within the data
    date_labels = [(min_work_start_datetime+datetime.timedelta(days=offset)).date().isoformat() for offset in range(num_days)]  # to store date labels in string format
    work_hours_per_day = [0]*num_days  # to store work hours

    # traverse through each work record and add it the data structure
    for work_record in work_records:
        work_start_date, work_end_date = work_record.start_datetime, work_record.end_datetime

        work_sessions = split_work_session(work_start_date, work_end_date, min_work_start_datetime)
        for work_session in work_sessions:
            date_index, worked_hours = work_session
            work_hours_per_day[date_index] += worked_hours

    session.close()

    return date_labels, work_hours_per_day


def get_date_index(date, min_work_start_datetime):
    return (date - min_work_start_datetime).days


def split_work_session(start_datetime, end_datetime, min_work_start_datetime):
    """
    splits one work session to days, if it goes over multiple days
    :param start_datetime:
    :param end_datetime:
    :return:
    """
    current_datetime = start_datetime
    results = []

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
        hours_worked = min((end_of_day - current_datetime).total_seconds() / 3600, (end_datetime - current_datetime).total_seconds() / 3600)

        # Append the date and hours worked to the results
        results.append((get_date_index(current_datetime, min_work_start_datetime), hours_worked))

        # Move to the next day
        current_datetime += datetime.timedelta(days=1)
        current_datetime = current_datetime.replace(hour=0, minute=0, second=0)

    return results


@admin_page.route("/get_user_data/<user_id>", methods=["POST"])
@login_required
def get_user_data(user_id):
    session = Session()

    try:
        sales_data = session.query(Sales.amount, Sales.end_datetime).filter(Sales.manager_id == user_id).order_by(Sales.end_datetime).all()
    except:
        session.close()
        return abort(404, "This user is not registered")

    else:
        date_to_sales_map = {}
        for sale in sales_data:
            sale_amount, sale_start_datetime, sale_end_datetime = sale
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
    return processed_sale_data
