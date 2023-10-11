from flask import (
    Blueprint,
    url_for,
    request,
    redirect,
    render_template,
    flash,
    abort,
    jsonify
)

from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc, func
import json
from config import login_manager, Session
from models import User, Work, Project
from json import dumps

import datetime

from earnings_metric_calculator import EarningsMetricCalculator
from work_hours_metric_calculator import WorkHoursMetricCalculator

admin_page = Blueprint("admin", __name__)


# todo add login setting later
# todo ensure that there is a check if user is admin or not
@admin_page.route("/add_user", methods=["POST", "GET"])
@login_required
def add_user():
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

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
    if not current_user.is_admin:
        return "Access denied. You are not an admin."
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

    # by default, EarningsAmount and WorkedHours of past two months are shown on the index page
    today = datetime.datetime.now()
    three_months_before = today - datetime.timedelta(days=60)



    # retrieve data
    # total_worked_hours = retrieve_company_work_hours_in_a_timeframe(three_months_before, today)
    # top_working_hours_workers = get_top_k_worker_data_in_a_timeframe(three_months_before, today, 5)

    whmc_all = WorkHoursMetricCalculator("all", three_months_before, today)
    whm_hist_all, whm_labels_all = whmc_all.get_sum_workers_metric_in_a_timeframe()

    whmc_top3 = WorkHoursMetricCalculator("topk", three_months_before, today, 3)
    whm_hist_top3, whm_labels_top3, top3_worker_names = whmc_top3.get_per_worker_metric_in_a_timeframe()

    # get year and month of the oldest available data in the database

    min_available_year_and_time = get_min_available_year_and_month()

    return render_template("admin_index.html",
                           whm_hist_all=dumps(whm_hist_all),
                           whm_label_all=dumps(whm_labels_all),
                           whm_hist_topk=dumps(whm_hist_top3),
                           whm_label_topk=dumps(whm_labels_top3),
                           whm_worker_names_topk=dumps(top3_worker_names),
                           min_available_year_and_time=dumps(min_available_year_and_time)
                           )

@admin_page.route("/test", methods=["GET"])
def test():
    return render_template("test/test_api.html")

def get_min_available_year_and_month():
    with Session() as session:
        min_datetime_record = session.query(Work.start_datetime).order_by().limit(1).first()
    min_available_year_and_time = min_datetime_record[0]
    return min_available_year_and_time.date().isoformat()

@admin_page.route("/api/data", methods=["GET"])
@login_required
def get_data():
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

    data_required = request.args.get("dataRequired")
    data_filter = request.args.get("dataFilter")
    is_calculation_per_worker = True if request.args.get("isCalculationPerWorker") == "true" else False

    print(data_required)
    print(data_filter)
    print(is_calculation_per_worker)

    # todo need to support integers / list of integers too

    # validation
    valid_data = ["workingHours", "earnings"]
    valid_data_filters = ["topk", "worstk", "all"]
    if data_required not in valid_data or data_filter not in valid_data_filters:
        abort(404, "requested invalid data type or filter type")

    # parsing start and end months
    start_month_raw = request.args.get("startMonth")
    end_month_raw = request.args.get("endMonth")
    start_month = datetime.datetime.strptime(start_month_raw, "%Y-%m")
    end_month = datetime.datetime.strptime(end_month_raw, "%Y-%m")

    # which metric?
    if data_required == "workingHours":
        mc = WorkHoursMetricCalculator(data_filter, start_month, end_month)
    elif data_required == "earnings":
        mc = EarningsMetricCalculator(data_filter, start_month, end_month)

    # per worker or total sum?
    if is_calculation_per_worker:
        data = mc.get_per_worker_metric_in_a_timeframe()
    else:
        data = mc.get_sum_workers_metric_in_a_timeframe()

    print(data)
    return jsonify(data)

@admin_page.route("/get_user_data/<user_id>", methods=["POST"])
@login_required
def get_user_data(user_id):
    if not current_user.is_admin:
        return "Access denied. You are not an admin."
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
