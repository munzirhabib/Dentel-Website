"""
Smile Dental Clinic - single file website
Language : Python (backend), HTML (pages), CSS (styling), JavaScript (browser), SQL (database)
Framework: Flask
Database : SQLite (relational): services, appointments (linked), messages
Server   : Runs on Vercel (client = browser, server = Vercel)
"""
import os
import sqlite3
from jinja2 import DictLoader
from markupsafe import Markup
from flask import Flask, render_template, request, redirect, url_for, jsonify

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)

# On Vercel only /tmp is writable (and it is temporary)
DB = "/tmp/clinic.db" if os.environ.get("VERCEL") else os.path.join(BASE, "clinic.db")

# ---------------- DATABASE ----------------
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
CREATE TABLE IF NOT EXISTS messages (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    phone   TEXT NOT NULL,
    message TEXT NOT NULL
);
"""

SERVICES = [
    ("Checkup", 1000, "A complete examination of your teeth and gums."),
    ("Scaling", 3000, "Deep cleaning that removes plaque and yellow buildup."),
    ("Filling", 4000, "Cavity cleaning with a strong, natural-looking filling."),
    ("Root Canal", 15000, "Painless nerve treatment that saves your tooth."),
    ("Whitening", 12000, "Brighten your teeth several shades in a single visit."),
]

DOCTORS = [
    ("Dr. Ayesha Khan", "Lead Dentist", "#0f766e"),
    ("Dr. Bilal Ahmed", "Root Canal Specialist", "#1d4ed8"),
    ("Dr. Sana Malik", "Cosmetic Dentist", "#be185d"),
    ("Dr. Usman Raza", "Orthodontist", "#b45309"),
]


def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row  # access columns by name
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)      # create the tables if they are missing
    if con.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO services (name, price, info) VALUES (?, ?, ?)", SERVICES
        )
        con.commit()
    return con


# ---------------- ICONS / PICTURES (inline SVG: no image files needed) ----------------
ICON_PATHS = {
    "tooth": '<path d="M7 3c-2 0-4 2-4 5 0 3 1 5 2 7 .7 1.5 1 4 2 6 .6 1 2 1 2.4-.5.5-2 1-4 2.6-4s2.1 2 2.6 4c.4 1.5 1.8 1.5 2.4.5 1-2 1.3-4.5 2-6 1-2 2-4 2-7 0-3-2-5-4-5-2 0-3 1-5 1S9 3 7 3z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5L16 9.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "heart": '<path d="M12 21s-8-5.3-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 5.7-8 11-8 11z"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"/><path d="M19 16v4M17 18h4"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0114 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "check": '<path d="M5 12l4.5 4.5L19 7"/>',
}
SERVICE_ICON = {"Checkup": "shield", "Scaling": "sparkle", "Filling": "tooth",
                "Root Canal": "heart", "Whitening": "sparkle"}


def icon(name):
    return Markup(
        '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true">' + ICON_PATHS[name] + "</svg>"
    )


@app.context_processor
def helpers():
    # These helpers are available in every template
    return dict(icon=icon, svc_icon=lambda n: SERVICE_ICON.get(n, "tooth"),
                doctors=DOCTORS, money=lambda n: "Rs {:,}".format(n))


# ---------------- HTML PAGES (templates) ----------------
PAGES = {

"base.html": '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Smile Dental Clinic{% endblock %}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
:root{--ink:#10333a;--teal:#0f766e;--teal-d:#0b5a54;--mint:#d9f1ec;--paper:#f6fbfa;--line:#cfe3df;--muted:#4f6f74}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"Manrope",system-ui,sans-serif;color:var(--ink);background:var(--paper);line-height:1.65}
h1,h2,h3{line-height:1.15;margin:0 0 12px}
h2{font-size:clamp(1.6rem,3.4vw,2.3rem);font-weight:800}
a{color:var(--teal)}
.ico{width:1.4em;height:1.4em;flex:none}
.wrap{max-width:1100px;margin:auto;padding:0 6vw}
section{padding:64px 0}
.alt{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.78rem;font-weight:800;color:var(--teal)}
.lead{font-size:1.1rem;color:var(--muted);max-width:52ch}

/* header */
.top{position:sticky;top:0;z-index:20;background:rgba(246,251,250,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 6vw;max-width:1100px;margin:auto}
.brand{display:flex;align-items:center;gap:8px;font-weight:800;font-size:1.25rem;color:var(--teal);text-decoration:none}
.brand .ico{width:1.7em;height:1.7em}
nav{display:flex;align-items:center;gap:6px}
nav a{padding:8px 12px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}
nav a:hover,nav a:focus-visible{background:var(--mint)}
nav a.active{color:var(--teal);background:var(--mint)}
nav a.cta{background:var(--teal);color:#fff;margin-left:6px}
nav a.cta:hover{background:var(--teal-d)}
.menu{display:none;background:none;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font:inherit;font-weight:600;cursor:pointer;color:var(--ink)}
@media(max-width:820px){
  .menu{display:block}
  nav{display:none;position:absolute;left:0;right:0;top:100%;flex-direction:column;align-items:stretch;background:var(--paper);padding:12px 6vw 18px;border-bottom:1px solid var(--line)}
  nav.open{display:flex}
  nav a.cta{margin:6px 0 0;text-align:center}
}

/* buttons */
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--teal);color:#fff;border:0;padding:13px 24px;border-radius:10px;font:inherit;font-weight:700;text-decoration:none;cursor:pointer}
.btn:hover,.btn:focus-visible{background:var(--ink)}
.btn.ghost{background:transparent;color:var(--teal);border:2px solid var(--teal)}
.btn.ghost:hover{background:var(--mint);color:var(--teal)}
.row{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}

/* hero */
.hero{padding:56px 0 40px}
.hero .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:32px;align-items:center}
.hero h1{font-size:clamp(2.4rem,6vw,4.2rem);font-weight:800;letter-spacing:-.02em}
.hero h1 span{color:var(--teal)}
.badges{display:flex;gap:18px;flex-wrap:wrap;margin-top:22px;color:var(--muted);font-weight:600;font-size:.95rem}
.badges span{display:flex;align-items:center;gap:6px}
.badges .ico{color:var(--teal)}
.art{width:100%;height:auto}
@media(max-width:820px){.hero .wrap{grid-template-columns:1fr}.art{max-width:380px;margin:auto}}
.pagehead{padding:48px 0 24px;background:linear-gradient(180deg,var(--mint),var(--paper))}

/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;text-align:center}
.stats b{display:block;font-size:2.2rem;font-weight:800;color:var(--teal)}
.stats span{color:var(--muted);font-weight:600}

/* cards */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px;margin-top:28px}
.card{background:var(--mint);padding:24px;border-radius:14px}
.alt .card{background:var(--paper);border:1px solid var(--line)}
.card .badge{width:46px;height:46px;border-radius:12px;background:#fff;color:var(--teal);display:grid;place-items:center;margin-bottom:12px}
.card h3{font-size:1.15rem}
.card p{margin:0 0 10px;color:var(--muted)}
.price{font-weight:800;color:var(--teal)}
.card .more{font-weight:700;text-decoration:none}
.card .more:hover{text-decoration:underline}
.step{counter-increment:s}
.step::before{content:counter(s);display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:var(--teal);color:#fff;font-weight:800;margin-bottom:12px}
.steps{counter-reset:s}
.quote p{font-size:1.02rem;color:var(--ink)}
.quote small{color:var(--muted);font-weight:600}
.stars{color:#d97706;letter-spacing:2px}
.team .card{text-align:center;background:#fff;border:1px solid var(--line)}
.team svg{width:96px;height:96px;margin:0 auto 10px;display:block}
.split{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:center}
@media(max-width:820px){.split{grid-template-columns:1fr}}
.cta-band{background:var(--teal);color:#fff;border-radius:18px;padding:40px;text-align:center}
.cta-band h2{color:#fff}
.cta-band p{color:#d7f0ec}
.cta-band .btn{background:#fff;color:var(--teal)}
.cta-band .btn:hover{background:var(--mint)}
details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin-bottom:10px}
summary{cursor:pointer;font-weight:700}
details p{margin:10px 0 0;color:var(--muted)}
.info{display:flex;gap:12px;align-items:flex-start;margin-bottom:18px}
.info .badge{width:42px;height:42px;border-radius:10px;background:var(--mint);color:var(--teal);display:grid;place-items:center;flex:none}
.info b{display:block}

/* forms + table */
.form{display:grid;gap:14px;max-width:440px}
label{display:grid;gap:4px;font-weight:600}
input,select,textarea{padding:11px;border:1px solid var(--line);border-radius:8px;font:inherit;background:#fff;color:var(--ink)}
input:focus-visible,select:focus-visible,textarea:focus-visible,summary:focus-visible{outline:2px solid var(--teal)}
.fee{font-weight:800;color:var(--teal);min-height:1.5em;margin:0}
.ok{background:var(--mint);border:1px solid var(--line);padding:12px 16px;border-radius:10px;font-weight:600;max-width:440px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:560px;background:#fff}
th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line)}
th{background:var(--mint)}
.link{background:none;border:0;color:#b42318;cursor:pointer;font:inherit;text-decoration:underline}

/* footer */
footer{background:var(--ink);color:#cfe3df;padding:48px 0 20px}
footer a{color:#cfe3df;text-decoration:none}
footer a:hover{text-decoration:underline}
footer h4{color:#fff;margin:0 0 10px}
.fgrid{display:grid;grid-template-columns:1.4fr 1fr 1.2fr;gap:28px}
@media(max-width:820px){.fgrid{grid-template-columns:1fr}}
.fgrid p{margin:4px 0}
.fgrid li{list-style:none;margin:4px 0}
.fgrid ul{padding:0;margin:0}
.copy{border-top:1px solid #2c5058;margin-top:28px;padding-top:16px;font-size:.9rem;color:#9fbfc0}

/* scroll animation */
.fade{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease}
.fade.show{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.fade{opacity:1;transform:none;transition:none}html{scroll-behavior:auto}}
  </style>
</head>
<body>
  <header class="top">
    <div class="bar">
      <a class="brand" href="{{ url_for('home') }}">{{ icon('tooth') }} Smile Dental</a>
      <button class="menu" id="menuBtn" aria-expanded="false" aria-controls="nav">Menu</button>
      <nav id="nav">
        <a href="{{ url_for('home') }}" class="{{ 'active' if request.endpoint == 'home' }}">Home</a>
        <a href="{{ url_for('about') }}" class="{{ 'active' if request.endpoint == 'about' }}">About</a>
        <a href="{{ url_for('services') }}" class="{{ 'active' if request.endpoint == 'services' }}">Services</a>
        <a href="{{ url_for('contact') }}" class="{{ 'active' if request.endpoint == 'contact' }}">Contact</a>
        <a href="{{ url_for('appointments') }}" class="{{ 'active' if request.endpoint == 'appointments' }}">Appointments</a>
        <a href="{{ url_for('book') }}" class="cta">Book now</a>
      </nav>
    </div>
  </header>

  <main>{% block content %}{% endblock %}</main>

  <footer>
    <div class="wrap">
      <div class="fgrid">
        <div>
          <a class="brand" href="{{ url_for('home') }}" style="color:#fff">{{ icon('tooth') }} Smile Dental</a>
          <p>Your smile is our responsibility. A clean environment, experienced doctors, and painless treatment.</p>
        </div>
        <div>
          <h4>Quick links</h4>
          <ul>
            <li><a href="{{ url_for('about') }}">About us</a></li>
            <li><a href="{{ url_for('services') }}">Services</a></li>
            <li><a href="{{ url_for('book') }}">Book appointment</a></li>
            <li><a href="{{ url_for('contact') }}">Contact</a></li>
          </ul>
        </div>
        <div>
          <h4>Visit us</h4>
          <p>Main Boulevard, Gulberg, Lahore</p>
          <p>042-1234 5678</p>
          <p>Mon to Sat: 10am - 8pm</p>
        </div>
      </div>
      <div class="copy">&copy; 2026 Smile Dental Clinic. Demo project (names, numbers and reviews are fictional).</div>
    </div>
  </footer>

  <script>
// JavaScript: runs inside the browser (client), not on the server.
const btn = document.getElementById("menuBtn");
const nav = document.getElementById("nav");
btn.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  btn.setAttribute("aria-expanded", open);
});

const service = document.getElementById("service");
const fee = document.getElementById("fee");
if (service) {
  const showFee = () => {
    const p = Number(service.selectedOptions[0].dataset.price);
    fee.textContent = "Fee: Rs " + p.toLocaleString("en-US");
  };
  service.addEventListener("change", showFee);
  showFee();
}
const date = document.getElementById("date");
if (date) date.min = new Date().toISOString().split("T")[0];

// sections fade in gently when scrolled into view
const els = document.querySelectorAll(".fade");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((list) => list.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("show"); io.unobserve(e.target); }
  }), { threshold: 0.12 });
  els.forEach((el) => io.observe(el));
} else { els.forEach((el) => el.classList.add("show")); }
  </script>
</body>
</html>''',

"index.html": '''{% extends "base.html" %}
{% block content %}
<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">Family dental care, Lahore</p>
      <h1>Healthy teeth,<br><span>happy smile.</span></h1>
      <p class="lead">From checkups to root canals, everything under one roof. Book your appointment online and skip the long queue.</p>
      <div class="row">
        <a class="btn" href="{{ url_for('book') }}">Book appointment</a>
        <a class="btn ghost" href="{{ url_for('services') }}">Our services</a>
      </div>
      <div class="badges">
        <span>{{ icon('check') }} Painless treatment</span>
        <span>{{ icon('check') }} Sterilised tools</span>
        <span>{{ icon('check') }} Same-day slots</span>
      </div>
    </div>
    <svg class="art" viewBox="0 0 400 360" role="img" aria-label="Smiling tooth">
      <circle cx="205" cy="180" r="160" fill="#d9f1ec"/>
      <circle cx="330" cy="70" r="26" fill="#b7e4dc"/>
      <circle cx="68" cy="290" r="18" fill="#b7e4dc"/>
      <g transform="translate(92 40) scale(12)" fill="#fff" stroke="#0f766e" stroke-width=".5" stroke-linejoin="round">
        <path d="M7 3c-2 0-4 2-4 5 0 3 1 5 2 7 .7 1.5 1 4 2 6 .6 1 2 1 2.4-.5.5-2 1-4 2.6-4s2.1 2 2.6 4c.4 1.5 1.8 1.5 2.4.5 1-2 1.3-4.5 2-6 1-2 2-4 2-7 0-3-2-5-4-5-2 0-3 1-5 1S9 3 7 3z"/>
      </g>
      <circle cx="205" cy="165" r="7" fill="#10333a"/><circle cx="267" cy="165" r="7" fill="#10333a"/>
      <path d="M208 198 Q236 228 264 198" fill="none" stroke="#10333a" stroke-width="6" stroke-linecap="round"/>
      <circle cx="188" cy="190" r="9" fill="#f9b4b4" opacity=".6"/><circle cx="284" cy="190" r="9" fill="#f9b4b4" opacity=".6"/>
      <g fill="#0f766e"><path d="M338 160l5 14 14 5-14 5-5 14-5-14-14-5 14-5z"/><path d="M92 120l4 10 10 4-10 4-4 10-4-10-10-4 10-4z"/></g>
      <g transform="rotate(-28 90 250)"><rect x="40" y="244" width="110" height="14" rx="7" fill="#0f766e"/><rect x="128" y="226" width="26" height="22" rx="4" fill="#10333a"/></g>
    </svg>
  </div>
</section>

<section class="alt fade">
  <div class="wrap">
    <div class="stats">
      <div><b>5,000+</b><span>Happy patients</span></div>
      <div><b>12 years</b><span>Experience</span></div>
      <div><b>4</b><span>Expert dentists</span></div>
      <div><b>4.9 / 5</b><span>Patient rating</span></div>
    </div>
  </div>
</section>

<section class="fade">
  <div class="wrap">
    <p class="eyebrow">What we do</p>
    <h2>Our popular services</h2>
    <div class="grid">
      {% for s in services[:4] %}
      <article class="card">
        <div class="badge">{{ icon(svc_icon(s.name)) }}</div>
        <h3>{{ s.name }}</h3>
        <p>{{ s.info }}</p>
        <span class="price">{{ money(s.price) }}</span>
      </article>
      {% endfor %}
    </div>
    <div class="row"><a class="btn ghost" href="{{ url_for('services') }}">See all services</a></div>
  </div>
</section>

<section class="alt fade">
  <div class="wrap">
    <p class="eyebrow">Why Smile Dental</p>
    <h2>Why you can trust us</h2>
    <div class="grid">
      <div class="card"><div class="badge">{{ icon('shield') }}</div><h3>Safe &amp; clean</h3><p>Instruments are sterilised after every patient.</p></div>
      <div class="card"><div class="badge">{{ icon('heart') }}</div><h3>Gentle care</h3><p>Soft, careful treatment for children and adults.</p></div>
      <div class="card"><div class="badge">{{ icon('clock') }}</div><h3>On time</h3><p>Arrive for your appointment, no long waiting.</p></div>
      <div class="card"><div class="badge">{{ icon('sparkle') }}</div><h3>Modern tools</h3><p>Newer equipment for faster, better results.</p></div>
    </div>
  </div>
</section>

<section class="fade">
  <div class="wrap">
    <p class="eyebrow">How it works</p>
    <h2>3 simple steps</h2>
    <div class="grid steps">
      <div class="step"><h3>Book online</h3><p>Enter your name, number and date, then choose a service.</p></div>
      <div class="step"><h3>Visit the clinic</h3><p>Come at your chosen time and the doctor will examine you.</p></div>
      <div class="step"><h3>Smile</h3><p>You get aftercare advice and a follow-up after treatment.</p></div>
    </div>
  </div>
</section>

<section class="alt fade">
  <div class="wrap">
    <p class="eyebrow">Reviews</p>
    <h2>Patient reviews</h2>
    <div class="grid">
      <div class="card quote"><div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p>I was scared of a root canal, but it was completely painless. Thank you so much.</p><small>Hamza, Gulberg</small></div>
      <div class="card quote"><div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p>A clean clinic and very friendly staff. My kids liked it too.</p><small>Maryam, DHA</small></div>
      <div class="card quote"><div class="stars">&#9733;&#9733;&#9733;&#9733;&#9734;</div><p>The difference after whitening was clearly visible. Online booking was very easy.</p><small>Talha, Model Town</small></div>
    </div>
  </div>
</section>

<section class="fade">
  <div class="wrap">
    <div class="cta-band">
      <h2>Take care of your smile</h2>
      <p>Book your appointment today. It takes less than a minute.</p>
      <a class="btn" href="{{ url_for('book') }}">Book now</a>
    </div>
  </div>
</section>
{% endblock %}''',

"about.html": '''{% extends "base.html" %}
{% block title %}About | Smile Dental{% endblock %}
{% macro avatar(color) %}
<svg viewBox="0 0 96 96" role="img" aria-label="Doctor"><circle cx="48" cy="48" r="48" fill="#d9f1ec"/><circle cx="48" cy="38" r="15" fill="#f1c9a5"/><path d="M18 90c2-20 14-30 30-30s28 10 30 30z" fill="{{ color }}"/><path d="M40 60l8 14 8-14" fill="#fff"/></svg>
{% endmacro %}
{% block content %}
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">About us</p>
    <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:800">Who we are</h1>
    <p class="lead">For 12 years, Smile Dental has been caring for the smiles of families across Lahore.</p>
  </div>
</section>

<section class="fade">
  <div class="wrap split">
    <div>
      <h2>Our story</h2>
      <p>The clinic started in one small room. The goal was simple: dental care should not be expensive, scary or complicated. Today we have 4 expert doctors and modern equipment, but our belief is the same: patients come first.</p>
      <p>Before every treatment we explain clearly what will be done and what it will cost, so there are no surprises.</p>
    </div>
    <svg viewBox="0 0 400 280" class="art" role="img" aria-label="Clinic illustration">
      <rect width="400" height="280" rx="20" fill="#d9f1ec"/>
      <rect x="40" y="70" width="320" height="170" rx="10" fill="#fff" stroke="#0f766e" stroke-width="3"/>
      <rect x="40" y="70" width="320" height="34" rx="10" fill="#0f766e"/>
      <rect x="70" y="130" width="70" height="110" fill="#b7e4dc"/><rect x="160" y="130" width="70" height="60" rx="6" fill="#b7e4dc"/><rect x="250" y="130" width="80" height="60" rx="6" fill="#b7e4dc"/>
      <g transform="translate(180 20) scale(1.7)" fill="#fff" stroke="#0f766e" stroke-width="1.2" stroke-linejoin="round"><path d="M7 3c-2 0-4 2-4 5 0 3 1 5 2 7 .7 1.5 1 4 2 6 .6 1 2 1 2.4-.5.5-2 1-4 2.6-4s2.1 2 2.6 4c.4 1.5 1.8 1.5 2.4.5 1-2 1.3-4.5 2-6 1-2 2-4 2-7 0-3-2-5-4-5-2 0-3 1-5 1S9 3 7 3z"/></g>
    </svg>
  </div>
</section>

<section class="alt fade">
  <div class="wrap">
    <p class="eyebrow">Our values</p>
    <h2>What we stand for</h2>
    <div class="grid">
      <div class="card"><div class="badge">{{ icon('heart') }}</div><h3>Compassion</h3><p>We treat you with an understanding of your pain.</p></div>
      <div class="card"><div class="badge">{{ icon('shield') }}</div><h3>Cleanliness</h3><p>Sterilisation is our first rule.</p></div>
      <div class="card"><div class="badge">{{ icon('check') }}</div><h3>Honesty</h3><p>Only the treatment that is truly necessary.</p></div>
    </div>
  </div>
</section>

<section class="fade">
  <div class="wrap team">
    <p class="eyebrow">Our team</p>
    <h2>Our doctors</h2>
    <div class="grid">
      {% for name, role, color in doctors %}
      <div class="card">{{ avatar(color) }}<h3>{{ name }}</h3><p>{{ role }}</p></div>
      {% endfor %}
    </div>
  </div>
</section>

<section class="fade">
  <div class="wrap">
    <div class="cta-band"><h2>Meet us</h2><p>Your first visit includes an examination and advice at an easy price.</p><a class="btn" href="{{ url_for('book') }}">Book now</a></div>
  </div>
</section>
{% endblock %}''',

"services.html": '''{% extends "base.html" %}
{% block title %}Services | Smile Dental{% endblock %}
{% block content %}
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Services</p>
    <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:800">Our services</h1>
    <p class="lead">This list comes straight from the <b>services</b> table in the database.</p>
  </div>
</section>

<section class="fade">
  <div class="wrap">
    <div class="grid">
      {% for s in services %}
      <article class="card">
        <div class="badge">{{ icon(svc_icon(s.name)) }}</div>
        <h3>{{ s.name }}</h3>
        <p>{{ s.info }}</p>
        <span class="price">{{ money(s.price) }}</span><br>
        <a class="more" href="{{ url_for('book', service=s.id) }}">Book this &rarr;</a>
      </article>
      {% endfor %}
    </div>
  </div>
</section>

<section class="alt fade">
  <div class="wrap">
    <p class="eyebrow">FAQ</p>
    <h2>Common questions</h2>
    <details><summary>Will the treatment hurt?</summary><p>We numb the area before treatment, so you usually feel no pain.</p></details>
    <details><summary>How often should I get my teeth cleaned?</summary><p>Scaling and a checkup every 6 months is usually best.</p></details>
    <details><summary>Can I visit without an appointment?</summary><p>Yes, but booking an appointment means you will not have to wait.</p></details>
    <details><summary>Do you treat children?</summary><p>Yes, our doctors treat children in a gentle, friendly way.</p></details>
  </div>
</section>
{% endblock %}''',

"contact.html": '''{% extends "base.html" %}
{% block title %}Contact | Smile Dental{% endblock %}
{% block content %}
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Contact</p>
    <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:800">Get in touch</h1>
    <p class="lead">Have a question? Send us a message and we will reply soon.</p>
  </div>
</section>

<section class="fade">
  <div class="wrap split" style="align-items:start">
    <div>
      <div class="info"><div class="badge">{{ icon('pin') }}</div><div><b>Address</b>Main Boulevard, Gulberg, Lahore</div></div>
      <div class="info"><div class="badge">{{ icon('phone') }}</div><div><b>Phone</b>042-1234 5678</div></div>
      <div class="info"><div class="badge">{{ icon('mail') }}</div><div><b>Email</b>hello@smiledental.example</div></div>
      <div class="info"><div class="badge">{{ icon('clock') }}</div><div><b>Timing</b>Mon to Sat: 10am - 8pm<br>Sunday: closed</div></div>
    </div>
    <div>
      {% if request.args.get('sent') %}<p class="ok">Thank you! Your message has been saved.</p>{% endif %}
      <form method="post" class="form">
        <label>Name <input name="name" required minlength="2"></label>
        <label>Phone <input name="phone" required pattern="[0-9+ -]{10,15}" placeholder="03xx xxxxxxx"></label>
        <label>Message <textarea name="message" rows="4" required></textarea></label>
        <button class="btn" type="submit">Send message</button>
      </form>
    </div>
  </div>
</section>
{% endblock %}''',

"book.html": '''{% extends "base.html" %}
{% block title %}Book | Smile Dental{% endblock %}
{% block content %}
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Appointment</p>
    <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:800">Book an appointment</h1>
  </div>
</section>
<section>
  <div class="wrap">
    <form method="post" class="form">
      <label>Patient name <input name="patient" required minlength="2"></label>
      <label>Phone <input name="phone" required pattern="[0-9+ -]{10,15}" placeholder="03xx xxxxxxx"></label>
      <label>Date <input type="date" name="date" id="date" required></label>
      <label>Service
        <select name="service_id" id="service" required>
          {% for s in services %}
          <option value="{{ s.id }}" data-price="{{ s.price }}" {{ 'selected' if request.args.get('service') == s.id|string }}>{{ s.name }}</option>
          {% endfor %}
        </select>
      </label>
      <p id="fee" class="fee"></p>
      <button class="btn" type="submit">Confirm booking</button>
    </form>
  </div>
</section>
{% endblock %}''',

"appointments.html": '''{% extends "base.html" %}
{% block title %}Appointments | Smile Dental{% endblock %}
{% block content %}
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">Database</p>
    <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:800">Appointments</h1>
    <p class="lead">This data comes from joining two database tables (appointments and services).</p>
  </div>
</section>
<section>
  <div class="wrap">
    {% if rows %}
    <div class="scroll">
    <table>
      <tr><th>Patient</th><th>Phone</th><th>Date</th><th>Service</th><th>Fee</th><th></th></tr>
      {% for r in rows %}
      <tr>
        <td>{{ r.patient }}</td><td>{{ r.phone }}</td><td>{{ r.date }}</td>
        <td>{{ r.service }}</td><td>{{ money(r.price) }}</td>
        <td><form method="post" action="{{ url_for('delete', appt_id=r.id) }}"><button class="link">Cancel</button></form></td>
      </tr>
      {% endfor %}
    </table>
    </div>
    {% else %}
    <p>No appointments yet. <a href="{{ url_for('book') }}">Book the first appointment.</a></p>
    {% endif %}
  </div>
</section>
{% endblock %}''',
}
app.jinja_loader = DictLoader(PAGES)


# ---------------- ROUTES: URL -> function ----------------
def all_services():
    return get_db().execute("SELECT * FROM services").fetchall()


@app.route("/")
def home():
    return render_template("index.html", services=all_services())


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html", services=all_services())


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        con = get_db()
        con.execute(
            "INSERT INTO messages (name, phone, message) VALUES (?, ?, ?)",
            (request.form["name"], request.form["phone"], request.form["message"]),
        )
        con.commit()
        return redirect(url_for("contact", sent=1))
    return render_template("contact.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    con = get_db()
    if request.method == "POST":           # the form was submitted (client -> server request)
        con.execute(
            "INSERT INTO appointments (patient, phone, date, service_id) VALUES (?, ?, ?, ?)",
            (request.form["patient"], request.form["phone"],
             request.form["date"], request.form["service_id"]),
        )
        con.commit()
        return redirect(url_for("appointments"))
    return render_template("book.html", services=all_services())


@app.route("/appointments")
def appointments():
    # JOIN: combine both tables using service_id (the power of a relational database)
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
    # Data in JSON format (API): other apps/JavaScript can read data from here
    rows = get_db().execute("SELECT * FROM appointments").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/messages")
def api_messages():
    rows = get_db().execute("SELECT * FROM messages").fetchall()
    return jsonify([dict(r) for r in rows])


@app.errorhandler(Exception)
def show_error(e):
    # For debugging: show the real error on screen (remove this when finished)
    app.logger.exception(e)
    return f"<h1>Error</h1><pre>{type(e).__name__}: {e}</pre>", 500


if __name__ == "__main__":
    app.run(debug=True)
