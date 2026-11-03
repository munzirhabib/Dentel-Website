"""
Dental Clinic website - Backend
Language : Python
Framework: Flask  (routes, requests, templates sambhalta hai)
Database : SQLite (relational, SQL se baat)
Server   : `python app.py` / Vercel chalate hi ye computer server ban jata hai
"""
import os
import sqlite3
from jinja2 import DictLoader
from flask import Flask, render_template, request, redirect, url_for, jsonify

BASE = os.path.dirname(os.path.abspath(__file__))

# Is single-file version mein HTML, CSS aur JavaScript sab isi file mein hain.
app = Flask(__name__, static_folder=None)

# ---------- HTML pages (templates) ----------
# Is single-file version mein saare HTML pages yahin likhe hain.
PAGES = {
    "base.html": '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Smile Dental{% endblock %}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
:root{
  --ink:#10333a; --teal:#0f766e; --mint:#d9f1ec; --paper:#f6fbfa; --line:#cfe3df;
}
*{box-sizing:border-box}
body{margin:0;font-family:"Manrope",system-ui,sans-serif;color:var(--ink);background:var(--paper);line-height:1.6}
.top{display:flex;justify-content:space-between;align-items:center;padding:16px 6vw;border-bottom:1px solid var(--line);flex-wrap:wrap;gap:8px}
.brand{font-weight:800;font-size:1.25rem;color:var(--teal);text-decoration:none}
nav a{margin-left:20px;color:var(--ink);text-decoration:none;font-weight:600}
nav a:hover,nav a:focus-visible{color:var(--teal);text-decoration:underline}
main{padding:32px 6vw;max-width:1000px;margin:auto}
.hero{padding:48px 0 32px}
.hero h1{font-size:clamp(2.2rem,6vw,4rem);line-height:1.05;margin:0 0 16px;font-weight:800}
.hero p{max-width:46ch;font-size:1.1rem}
.btn{display:inline-block;background:var(--teal);color:#fff;border:0;padding:12px 22px;border-radius:8px;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}
.btn:hover,.btn:focus-visible{background:var(--ink)}
.services{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.service{background:var(--mint);padding:20px;border-radius:12px}
.service h3{margin:0 0 6px}
.form{display:grid;gap:14px;max-width:420px}
label{display:grid;gap:4px;font-weight:600}
input,select{padding:10px;border:1px solid var(--line);border-radius:8px;font:inherit;background:#fff}
input:focus-visible,select:focus-visible{outline:2px solid var(--teal)}
.price{font-weight:800;color:var(--teal);min-height:1.5em;margin:0}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:560px}
th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}
.link{background:none;border:0;color:#b42318;cursor:pointer;font:inherit;text-decoration:underline}
footer{padding:24px 6vw;color:#5b7a7f;border-top:1px solid var(--line);margin-top:40px}
</style>
</head>
<body>
  <header class="top">
    <a class="brand" href="{{ url_for('home') }}">Smile Dental</a>
    <nav>
      <a href="{{ url_for('home') }}">Services</a>
      <a href="{{ url_for('book') }}">Book</a>
      <a href="{{ url_for('appointments') }}">Appointments</a>
    </nav>
  </header>
  <main>{% block content %}{% endblock %}</main>
  <footer>Smile Dental Clinic, Lahore. Demo project.</footer>
  <script>
// JavaScript: browser (client) ke andar chalta hai, server par nahi.
const service = document.getElementById("service");
const price = document.getElementById("price");
const date = document.getElementById("date");

if (service) {
  const showPrice = () => {
    const p = service.selectedOptions[0].dataset.price;
    price.textContent = "Fee: Rs " + p;
  };
  service.addEventListener("change", showPrice);
  showPrice();
}
if (date) {
  // purani tareekh select na ho sakay
  date.min = new Date().toISOString().split("T")[0];
}
</script>
</body>
</html>
''',
    "index.html": '''{% extends "base.html" %}
{% block content %}
<section class="hero">
  <h1>Healthy teeth,<br>no waiting.</h1>
  <p>Checkup se root canal tak, sab ek jagah. Online appointment book karein.</p>
  <a class="btn" href="{{ url_for('book') }}">Book appointment</a>
</section>

<section>
  <h2>Our services</h2>
  <div class="services">
    {% for s in services %}
    <article class="service">
      <h3>{{ s.name }}</h3>
      <p>{{ s.info }}</p>
      <strong>Rs {{ s.price }}</strong>
    </article>
    {% endfor %}
  </div>
</section>
{% endblock %}
''',
    "book.html": '''{% extends "base.html" %}
{% block title %}Book | Smile Dental{% endblock %}
{% block content %}
<h2>Book an appointment</h2>
<form method="post" id="bookForm" class="form">
  <label>Patient name
    <input name="patient" required minlength="2">
  </label>
  <label>Phone
    <input name="phone" required pattern="[0-9+ -]{10,15}" placeholder="03xx xxxxxxx">
  </label>
  <label>Date
    <input type="date" name="date" id="date" required>
  </label>
  <label>Service
    <select name="service_id" id="service" required>
      {% for s in services %}
      <option value="{{ s.id }}" data-price="{{ s.price }}">{{ s.name }}</option>
      {% endfor %}
    </select>
  </label>
  <p id="price" class="price"></p>
  <button class="btn" type="submit">Confirm booking</button>
</form>
{% endblock %}
''',
    "appointments.html": '''{% extends "base.html" %}
{% block title %}Appointments | Smile Dental{% endblock %}
{% block content %}
<h2>Appointments</h2>
{% if rows %}
<div class="scroll">
<table>
  <tr><th>Patient</th><th>Phone</th><th>Date</th><th>Service</th><th>Fee</th><th></th></tr>
  {% for r in rows %}
  <tr>
    <td>{{ r.patient }}</td><td>{{ r.phone }}</td><td>{{ r.date }}</td>
    <td>{{ r.service }}</td><td>Rs {{ r.price }}</td>
    <td>
      <form method="post" action="{{ url_for('delete', appt_id=r.id) }}">
        <button class="link">Cancel</button>
      </form>
    </td>
  </tr>
  {% endfor %}
</table>
</div>
{% else %}
<p>Abhi koi appointment nahi. <a href="{{ url_for('book') }}">Pehli appointment book karein.</a></p>
{% endif %}
{% endblock %}
''',
}
app.jinja_loader = DictLoader(PAGES)

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
