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

admin_page = Blueprint("admin", __name__, template_folder="templates")


# todo add login setting later
@admin_page.route("/add_user", methods=["POST", "GET"])
def admin_add_user():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            first_name = request.form["first-name"]
            last_name = request.form["last-name"]
            is_admin = bool(request.form.get("is_admin"))

        except KeyError:
            flash("At least one input was not filled in", "error")

        else:
            # check if a user with the inputted username alreadey exits or not
            #TODO don't store passwords literally
            session = Session()
            existing_user = session.query(User).filter(User.username == username)
            if len(list(existing_user)) == 0:
                session.add(User(username=username,
                                 password=password,
                                 first_name=first_name,
                                 last_name=last_name,
                                 is_working=False,
                                 is_admin=is_admin))
                session.commit()
                session.close()
                flash("User added successfully", "success")


            # flash unsuccessful message
            flash("There was an existing user with the same username", "error")
            session.close()
    
    
    return render_template("admin_add_user.html")

@admin_page.route("/check_users")
def check_users():
    return render_template("check_users.html")
