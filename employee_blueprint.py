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
from datetime import datetime


from config import login_manager, Session
from models import User, Work, Sales

employee_page = Blueprint("employee", __name__)


@employee_page.route("/", methods=["GET"])
@login_required
def index():
    user_id = current_user.id
    has_started_work_today = check_employee_is_working(user_id)

    work_data, sales_data = retrieve_past_work_data(current_user.id)
    print(work_data)
    print(sales_data)

    print(type(work_data))
    print(type(work_data[0]))
    print(type(sales_data))

    return render_template("worker_page.html",
                           has_started_work=has_started_work_today,
                           work_data=work_data,
                           sales_data=sales_data)

@employee_page.route("/start_work", methods=["POST"])
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
    
@employee_page.route("/cancel_work", methods=["POST"])
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


@employee_page.route("/finish_work", methods=["POST"])
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
        work_data = session.query(Work.start_datetime, Work.end_datetime).filter(Work.user_id == user_id).all()
        work_data = [tuple(row) for row in work_data]

        # sales data
        sales_data = session.query(Sales.amount, Sales.start_datetime, Sales.end_datetime).filter(Sales.manager_id == user_id).all()
        sales_data = [tuple(row) for row in sales_data]

    except:
        session.close()
        abort(404, "This user is not registered")

    return work_data, sales_data



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

