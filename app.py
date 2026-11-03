"""
Dental Clinic website - Backend
Language : Python
Framework: Flask  (routes, requests, templates sambhalta hai)
Database : SQLite (relational, SQL se baat)
Server   : `python app.py` / Vercel chalate hi ye computer server ban jata hai
"""
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

BASE = os.path.dirname(os.path.abspath(__file__))

# Poore raste (full path) diye hain taake Vercel par files mil jayen.
# public/: Vercel ise CDN se serve karta hai, local par Flask khud.
app = Flask(
    __name__,
    template_folder=os.path.join(BASE, "templates"),
    static_folder=os.path.join(BASE, "public"),
    static_url_path="",
)

# Vercel par sirf /tmp likhne ke qabil hai (aur wo temporary hai)
DB = "/tmp/clinic.db" if os.environ.get("VERCEL") else os.path.join(BASE, "clinic.db")

# Relational database: do tables aapas mein linked (service_id = rishta)
SCHEMA = """
CREATE TABLE IF NOT EXISTS services (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    price INTEGER NOT NULL,
    info  TEXT
);
CREATE TABLE IF NOT EXISTS appointments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    patient    TEXT NOT NULL,
    phone      TEXT NOT NULL,
    date       TEXT NOT NULL,
    service_id INTEGER NOT NULL,
    FOREIGN KEY (service_id) REFERENCES services(id)
);
"""

SERVICES = [
    ("Checkup", 1000, "Poore daanton ka muaina"),
    ("Scaling", 3000, "Daanton ki safai"),
    ("Filling", 4000, "Cavity ka ilaaj"),
    ("Root Canal", 15000, "Nerve ka ilaaj"),
    ("Whitening", 12000, "Daanton ko chamkana"),
]


def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row  # rows ko naam se access karne ke liye
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)      # tables na hon to ban jayen
    if con.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO services (name, price, info) VALUES (?, ?, ?)", SERVICES
        )
        con.commit()
    return con


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


@app.errorhandler(Exception)
def show_error(e):
    # Debugging ke liye: asal error screen par dikhao (kaam ke baad ye hata dein)
    app.logger.exception(e)
    return f"<h1>Error</h1><pre>{type(e).__name__}: {e}</pre>", 500


if __name__ == "__main__":
    app.run(debug=True)
