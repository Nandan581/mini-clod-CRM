from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# SQLite database (file will be created automatically)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "crm.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------- MODELS -----------------
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    value = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="New")  # New, Contacted, Won, Lost
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------- ROUTES -----------------
@app.route("/")
def index():
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()

    # Count leads by status
    statuses = ["New", "Contacted", "Won", "Lost"]
    lead_stats = {}
    for s in statuses:
        lead_stats[s] = Lead.query.filter_by(status=s).count()

    return render_template(
        "index.html",
        total_customers=total_customers,
        total_leads=total_leads,
        lead_stats=lead_stats,
    )


# ---- Customers ----
@app.route("/customers")
def customers():
    all_customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template("customers.html", customers=all_customers)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        company = request.form.get("company")

        if name:  # simple validation
            new_cust = Customer(name=name, email=email, phone=phone, company=company)
            db.session.add(new_cust)
            db.session.commit()
            return redirect(url_for("customers"))

    return render_template("add_customer.html")


# ---- Leads ----
@app.route("/leads")
def leads():
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template("leads.html", leads=all_leads)


@app.route("/leads/add", methods=["GET", "POST"])
def add_lead():
    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        value = request.form.get("value") or 0
        status = request.form.get("status") or "New"

        try:
            value = float(value)
        except ValueError:
            value = 0

        if customer_name:
            new_lead = Lead(customer_name=customer_name, value=value, status=status)
            db.session.add(new_lead)
            db.session.commit()
            return redirect(url_for("leads"))

    return render_template("add_lead.html")

if __name__ == "__main__":
    # create tables once, before the first request
    with app.app_context():
        db.create_all()
    app.run(debug=True)
