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
from models import User, Work, Project, Client
from json import dumps

import datetime

from earnings_metric_calculator import EarningsMetricCalculator
from work_hours_metric_calculator import WorkHoursMetricCalculator

admin_blueprint = Blueprint("admin", __name__)


# todo add login setting later
# todo ensure that there is a check if user is admin or not
@admin_blueprint.route("/users/add", methods=["POST", "GET"])
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


@admin_blueprint.route("/clients/add", methods=["GET", "POST"])
@login_required
def add_client():
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

    if request.method == "GET":
        return render_template("admin_add_client.html")


    try:
        client_name = request.form["client-name"]

    except KeyError as e:
        print(e)
        flash("At least one input was not filled in", "error")
        return render_template("admin_add_user.html")


    # add client
    with Session() as session:
        session.add(Client(name=client_name))
        session.commit()

    flash("Client added successfully", "success")
    return render_template("admin_add_client.html")


@admin_blueprint.route("/users")
@login_required
def show_users():
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

    # todo: use get_user_profile API
    session = Session()
    users = session.query(User).all()
    user_objects = [user.to_dict_without_password() for user in users]
    return render_template("check_users2.html", users=user_objects)

@admin_blueprint.route("/")
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

@admin_blueprint.route("/test", methods=["GET"])
def test():
    return render_template("test/test_api.html")

def get_min_available_year_and_month():
    with Session() as session:
        min_datetime_record = session.query(Work.start_datetime).order_by().limit(1).first()
    min_available_year_and_time = min_datetime_record[0]
    return min_available_year_and_time.date().isoformat()


@admin_blueprint.route("/projects", methods=["GET"])
@login_required
def get_projects():
    # servers a list of projects
    # todo create html for this
    # put an edit button
    pass

@admin_blueprint.route("/projects/edit", methods=["POST", "GET"])
@login_required
def edit_project():
    # todo add a page to modify the project (e.g. adding earnings)
    # todo create a project modifying page
    pass


@admin_blueprint.route("/projects/add", methods=["POST", "GET"])
@login_required
def add_project():
    # authentication
    if not current_user.is_admin:
        return "Access denied. You are not an admin."

    # if method == get
    if request.method == "GET":
        return render_template("admin_add_project.html")

    # input validation
    print(request.form)
    try:
        manager_id = int(request.form["manager-id"])
        client_id = request.form.get("client-id")
        client_info = (int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id) or request.form.get("client-name")
        start_date_raw = request.form["start-date"]

    except:
        # print(e)
        flash("At least one input was not filled in", "error")
        return render_template("admin_add_project.html")


    # parse dates
    start_datetime = datetime.datetime.strptime(start_date_raw, "%Y-%m-%d")


    if isinstance(client_info, str):
        # need to create a new client & insert it to the DB
        with Session() as session:
            client = Client(name=client_info)
            session.add(client)
            session.commit()

            # get the client id
            client_id = client.id

    else:
        client_id = client_info

    # add project record
    with Session() as session:
        session.add(Project(client_id=client_id, manager_id=manager_id, start_datetime=start_datetime))
        session.commit()

    flash("Project added successfully", "success")
    return render_template("admin_add_project.html")

