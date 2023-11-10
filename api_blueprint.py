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
import datetime

from earnings_metric_calculator import EarningsMetricCalculator
from work_hours_metric_calculator import WorkHoursMetricCalculator

from config import Session
from models import User, Client

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/users/data", methods=["GET"])
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
    else:
        # todo: raise error -> unsupported data
        pass

    # per worker or total sum?
    if is_calculation_per_worker:
        data = mc.get_per_worker_metric_in_a_timeframe()
    else:
        data = mc.get_sum_workers_metric_in_a_timeframe()

    print(data)
    return jsonify(data)

@api_blueprint.route("/user/data", methods=["GET"])
@login_required
def get_single_user_data():
    user_id = int(request.args.get("id"))
    if user_id != current_user.id and not current_user.is_admin:
        return "Access denied. You are neither the user of the requested data nor an admin."

    data_required = request.args.get("dataRequired")

    # parsing start and end months
    start_month_raw = request.args.get("startMonth")
    end_month_raw = request.args.get("endMonth")
    start_month = datetime.datetime.strptime(start_month_raw, "%Y-%m")
    end_month = datetime.datetime.strptime(end_month_raw, "%Y-%m")

    # which metric?
    if data_required == "workingHours":
        mc = WorkHoursMetricCalculator(user_id, start_month, end_month)
    elif data_required == "earnings":
        mc = EarningsMetricCalculator(user_id, start_month, end_month)
    else:
        abort(404, "unknown metrics")


    data = mc.get_sum_workers_metric_in_a_timeframe()

    return data

@api_blueprint.route("/user/profile", methods=["GET"])
@login_required
def get_user_profile():
    user_id = request.args.get("id")
    user_id = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else None

    if user_id != current_user.id and not current_user.is_admin:
        return "Access denied. You are neither the user of the requested data nor an admin."

    with Session() as session:
        user_records = session.query(User).all()
        users = [user_record.to_dict_without_password() for user_record in user_records]


    return jsonify(users)


@api_blueprint.route("/client/profile", methods=["GET"])
@login_required
def get_client_profiles():
    if not current_user.is_admin:
        return "Access denied. You are neither the user of the requested data nor an admin."

    # todo: should return dict (not list)
    with Session() as session:
        client_records = session.query(Client)
        clients = [client_record.to_dict() for client_record in client_records]

    return jsonify(clients)
