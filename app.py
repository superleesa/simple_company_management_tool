from flask import (
    url_for,
    request,
    redirect,
    flash,
    render_template
)

from models import Work, User
from flask_login import login_user, logout_user, login_required, current_user


# ========configs==========
from config import app, Session, login_manager

# =======blueprint registering=========
from admin_blueprint import admin_page
app.register_blueprint(admin_page, url_prefix="/admin")

from employee_blueprint import employee_page
app.register_blueprint(employee_page, url_prefix="/employee")


# ===========endpoints========
@app.route("/")
def index():
    return "hello world"


# login related
@login_manager.user_loader
def load_user(user_id):
    session = Session()
    employee = session.query(User).filter(User.id == int(user_id))
    session.close()
    return employee[0]

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # check if a user with given username exists
        session = Session()
        possible_user = session.query(User).filter(User.username == username and User.password == password)
        if len(list(possible_user)) == 1:
            login_user(possible_user[0])
            # serve user's landing page
            return redirect(url_for("employee.worker_page"))

        flash("Incorrect username or pasword")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
