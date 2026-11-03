# Smile Dental - Flask project (mentor ke sawalon ke liye)

## Chalane ka tareeqa (VS Code / Cursor ka terminal)
```
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Browser mein kholein: http://127.0.0.1:5000

## Git / GitHub
```
git init
git add .
git commit -m "v1: dental website"
git tag v1.0
git remote add origin <GitHub repo link>
git push -u origin main
```

## Har concept website mein kahan hai
| Concept | Kahan |
|---|---|
| Code | Is folder ki saari files |
| Language | Python (app.py), HTML (templates), CSS (style.css), JavaScript (script.js), SQL (schema.sql) |
| Framework | Flask (app.py ki pehli lines). Routes, requests, templates wahi sambhalta hai |
| Server | `app.run()`: aap ka computer server, browser client |
| Operating System | Aap ka Windows is server ko chala raha hai. Live karte waqt aksar Linux server |
| Virtual environment | `venv/` folder: Flask sirf is project ke liye |
| Versions | `requirements.txt` mein `Flask==3.0.3`, aur git tag `v1.0` |
| Git / GitHub | `.gitignore`, commits, push |
| Relational database | SQLite: `schema.sql`, do tables jude hue (`service_id` foreign key) |
| Rishta (relation) | `appointments.service_id` -> `services.id`, aur `JOIN` query (`/appointments`) |
| Non-relational | Neeche dekhein |
| API / JSON | `/api/appointments` |
| VS Code / Cursor | Jahan ye project khola aur likha gaya |

## NoSQL (MongoDB) mein wahi appointment aise hoti
```json
{
  "patient": "Ali", "phone": "0300...", "date": "2026-11-10",
  "service": { "name": "Scaling", "price": 3000 }
}
```
Service ki detail appointment ke andar hi hai (alag table nahi). Fast, lekin price badalni ho to har appointment mein badalni paray.

## Doosri language mein yahi kaam
| | Python (Flask) | JavaScript (Express) | Java (Spring Boot) |
|---|---|---|---|
| Route | `@app.route("/book")` | `app.get("/book", ...)` | `@GetMapping("/book")` |
| Libraries/versions file | `requirements.txt` | `package.json` | `pom.xml` |
| Project ka alag environment | `venv` | `node_modules` | Maven/Gradle |
| Chalana | `python app.py` | `node app.js` | Pehle compile, phir run |
| Code ki lambai | Kam | Kam | Zyada |

## GitHub par upload
```
git init
git add .
git commit -m "v1: dental website"
git branch -M main
git remote add origin https://github.com/<username>/dental-clinic.git
git push -u origin main
```

## Vercel par deploy
1. vercel.com par GitHub se login karein
2. Add New, phir Project, `dental-clinic` repo Import karein
3. Framework "Flask" khud detect hoga, Deploy dabayein
4. Link milega: `dental-clinic-xxxx.vercel.app`

Note: Vercel serverless hai. SQLite file `/tmp` mein banti hai, is liye booking data temporary hota hai (kuch der baad reset ho jata hai). Asli data ke liye hosted database (Postgres, Neon, Supabase) lagta hai.
