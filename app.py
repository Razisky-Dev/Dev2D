from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# =====================
# CONFIG
# =====================
app.config["SECRET_KEY"] = "super-secret-key-change-later"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================
# USER MODEL
# =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    mobile = db.Column(db.String(20))
    password = db.Column(db.String(200))

# =====================
# USER LOADER
# =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================
# ROUTES
# =====================
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        new_user = User(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            username=request.form["username"],
            email=request.form["email"],
            mobile=request.form["mobile"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Login now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if not user or not check_password_hash(user.password, request.form["password"]):
            flash("Invalid login details", "error")
            return redirect(url_for("login"))

        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))

# =====================
# RUN
# =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
