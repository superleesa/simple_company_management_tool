from flask import (
    Blueprint,
    url_for,
    request,
    redirect,
    render_template,
    flash
)

from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc
from config import login_manager, Session
from models import User, Work

employee_page = Blueprint("employee", __name__, template_folder="templates")


#TODO add is_working attribute

@employee_page.route("/worker_page", methods=["GET"])
@login_required
def worker_page():
    
    # access the database and check if the start datetime is records
    user_id = current_user.id
    session = Session()
    
    query = (session.query(Work.end_datetime)
                        .filter(Work.user_id == user_id)
                        .order_by(desc(Work.start_datetime)).all())
    session.close()
    
    print(query)
    if len(query) == 0:
        has_started_todays_work = False
    else:
        has_started_todays_work = query[0].end_datetime is None
        
    
    return render_template("worker_page.html", has_started_work=has_started_todays_work)

@employee_page.route("/start_work", methods=["POST"])
@login_required
def start_work():
    user_id = current_user.id
    session = Session()
    
    # TODO check the worker has not started todays work
    query = (session.query(Work.end_datetime)
                        .filter(Work.user_id == user_id)
                        .order_by(desc(Work.start_datetime)).all())
    
    
    if len(query) == 0:
        has_started_todays_work = False
    else:
        has_started_todays_work = query[0].end_datetime is None
    
    if has_started_todays_work:
        flash("Have an ongoing work already", "error")
        session.close()
        return redirect(url_for("worker_page"))
    
    
    start_datetime = datetime.strptime(request.form["start-datetime"], "%Y-%m-%dT%H:%M:%S")
    # parse this into date object somehow
    
    session.add(Work(user_id=user_id, start_datetime=start_datetime))
    session.commit()
    session.close()
    
    # redirect to the worker page
    flash("Started Today's Work", "success")
    return redirect(url_for("worker_page"))
    
@employee_page.route("/cancel_work", methods=["POST"])
@login_required
def cancel_work():
    # can only cancel if checked in already
    
    # TODO add "are you sure pop up box"
    
    user_id = current_user.id
    session = Session()
    res = session.query(Work.end_datetime, Work.id).filter(Work.user_id == user_id).order_by(desc(Work.start_datetime)).first()
    if res is None:
        has_started_todays_work = False
    else:
        last_work_end_datetime, last_work_id = res[0], res[1]
        has_started_todays_work =  last_work_end_datetime is None
        
    if has_started_todays_work:
        
        session.query(Work).filter(Work.id == last_work_id).delete()
        session.commit()
        session.close()
        flash("Work canceled", "success")
        return redirect(url_for("worker_page"))
    
    
    flash("Have not yet started today's work", "error")
    session.close()
    return redirect(url_for("worker_page"))

@employee_page.route("/finish_work", methods=["POST"])
@login_required
def finish_work():
    # TODO add "are you sure pop up box"
    
    user_id = current_user.id
    print(user_id)
    session = Session()
    res = session.query(Work).filter(Work.user_id == user_id).order_by(desc(Work.start_datetime)).first()
    if res is None:
        has_started_todays_work = False
    else:
        last_work_end_datetime = res.end_datetime
        has_started_todays_work =  last_work_end_datetime is None
        
    if has_started_todays_work:
        end_datetime = datetime.strptime(request.form["end-datetime"], "%Y-%m-%dT%H:%M:%S")
        res.end_datetime = end_datetime
        session.commit()
        session.close()
        flash("Finished today's work", "success")
        return redirect(url_for("worker_page"))
    
    # todo flash message
    session.close()
    flash("Have not yet started today's work", "error")
    return redirect(url_for("worker_page"))
