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
from sqlalchemy import desc, func
import json
from config import login_manager, Session
from models import User, Work, Project
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

    today = datetime.datetime.now()
    three_months_before = today - datetime.timedelta(days=90)

    # retrieve data
    total_worked_hours = retrieve_company_work_hours_in_a_timeframe(three_months_before, today)

    top_working_hours_workers = get_top_k_worker_data_in_a_timeframe(three_months_before, today, 5)


    return render_template("admin_index.html",
                           dateToWorkedHours=dumps(total_worked_hours),
                           topWorkingHoursWorkers=dumps(top_working_hours_workers))



@admin_page.route("/get_user_data/<user_id>", methods=["POST"])
@login_required
def get_user_data(user_id):
    session = Session()

    try:
        sales_data = session.query(Project.amount, Project.end_datetime).filter(Project.manager_id == user_id).order_by(Project.end_datetime).all()
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
