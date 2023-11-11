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
from admin_blueprint import admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix="/admin")

from employee_blueprint import employee_blueprint
app.register_blueprint(employee_blueprint, url_prefix="/employee")

from api_blueprint import api_blueprint
app.register_blueprint(api_blueprint, url_prefix="/api")


# ===========endpoints========
@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    if current_user.is_admin:
        return redirect(url_for("admin.index"))
    else:
        return redirect(url_for("employee.index"))


# login related
@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).filter(User.id == int(user_id)).first()
    session.close()
    return user

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check if a user with given username exists
        with Session() as session:
            possible_user = session.query(User).filter(User.username == username and User.password == password).first()
        if possible_user is not None:
            login_user(possible_user)  # use flask-login's function to log in this user

            if possible_user.is_admin:
                return redirect(url_for("admin.index"))
            else:
                # if user is worker: serve worker's landing page
                print("hello mates")
                print(possible_user)
                print(current_user)
                return redirect(url_for("employee.index"))

        flash("Incorrect username or pasword")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
