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
import json
from config import login_manager, Session
from models import User, Work

admin_page = Blueprint("admin", __name__)


# todo add login setting later
@admin_page.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "GET":
        return render_template("admin_add_user.html")


    try:
        username = request.form["username"]
        password = request.form["password1"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        is_admin = bool(request.form.get("is-admin"))

    except KeyError as e:
        print(e)
        flash("At least one input was not filled in", "error")
        return render_template("admin_add_user.html")


    # check if a user with the inputted username alreadey exits or not
    #TODO don't store passwords literally - store hashed ones
    session = Session()
    existing_user = session.query(User).filter(User.username == username)

    if len(list(existing_user)) == 0:
        flash("There was an existing user with the same username", "error")
        session.close()
        return render_template("admin_add_user.html")


    session.add(User(username=username,
                     password=password,
                     first_name=first_name,
                     last_name=last_name,
                     is_working=False,
                     is_admin=is_admin))
    session.commit()
    session.close()
    flash("User added successfully", "success")
    return render_template("admin_add_user.html")


@admin_page.route("/show_users")
def show_users():
    session = Session()
    users = session.query(User).all()
    user_objects = [user.to_dict_without_password() for user in users]
    # print(json.dumps(user_objects))
    return render_template("check_users2.html", users=user_objects)
