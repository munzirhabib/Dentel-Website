"""
Dental Clinic website - Backend
Language : Python
Framework: Flask  (routes, requests, templates sambhalta hai)
Database : SQLite (relational, SQL se baat)
Server   : `flask run` chalate hi ye computer server ban jata hai
"""
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

# public/ folder: Vercel ise CDN se serve karta hai, local par Flask khud
app = Flask(__name__, static_folder="public", static_url_path="")

BASE = os.path.dirname(os.path.abspath(__file__))
# Vercel par sirf /tmp likhne ke qabil hai (aur wo temporary hai)
DB = "/tmp/clinic.db" if os.environ.get("VERCEL") else os.path.join(BASE, "clinic.db")


def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row  # rows ko naam se access karne ke liye
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with get_db() as con, open(os.path.join(BASE, "schema.sql"), encoding="utf-8") as f:
        con.executescript(f.read())


# ---------- ROUTES: URL -> function ----------
@app.route("/")
def home():
    services = get_db().execute("SELECT * FROM services").fetchall()
    return render_template("index.html", services=services)


@app.route("/book", methods=["GET", "POST"])
def book():
    con = get_db()
    if request.method == "POST":           # form submit hua (client -> server request)
        con.execute(
            "INSERT INTO appointments (patient, phone, date, service_id) VALUES (?, ?, ?, ?)",
            (request.form["patient"], request.form["phone"],
             request.form["date"], request.form["service_id"]),
        )
        con.commit()
        return redirect(url_for("appointments"))
    services = con.execute("SELECT * FROM services").fetchall()
    return render_template("book.html", services=services)


@app.route("/appointments")
def appointments():
    # JOIN: dono tables ko service_id se jodna (relational database ka kamal)
    rows = get_db().execute("""
        SELECT a.id, a.patient, a.phone, a.date, s.name AS service, s.price
        FROM appointments a
        JOIN services s ON s.id = a.service_id
        ORDER BY a.date
    """).fetchall()
    return render_template("appointments.html", rows=rows)


@app.route("/delete/<int:appt_id>", methods=["POST"])
def delete(appt_id):
    con = get_db()
    con.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
    con.commit()
    return redirect(url_for("appointments"))


@app.route("/api/appointments")
def api_appointments():
    # JSON format mein data (API): doosri apps/JavaScript yahan se data le sakti hain
    rows = get_db().execute("SELECT * FROM appointments").fetchall()
    return jsonify([dict(r) for r in rows])


init_db()  # import hote hi table ban jayen (Vercel __main__ nahi chalata)

if __name__ == "__main__":
    app.run(debug=True)
