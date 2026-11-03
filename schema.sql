-- Relational database (SQLite): do tables aapas mein linked hain
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
    FOREIGN KEY (service_id) REFERENCES services(id)  -- yehi "rishta" (relation) hai
);

INSERT INTO services (name, price, info)
SELECT 'Checkup', 1000, 'Poore daanton ka muaina'
WHERE NOT EXISTS (SELECT 1 FROM services);
INSERT INTO services (name, price, info)
SELECT 'Scaling', 3000, 'Daanton ki safai'
WHERE (SELECT COUNT(*) FROM services) = 1;
INSERT INTO services (name, price, info)
SELECT 'Filling', 4000, 'Cavity ka ilaaj'
WHERE (SELECT COUNT(*) FROM services) = 2;
INSERT INTO services (name, price, info)
SELECT 'Root Canal', 15000, 'Nerve ka ilaaj'
WHERE (SELECT COUNT(*) FROM services) = 3;
INSERT INTO services (name, price, info)
SELECT 'Whitening', 12000, 'Daanton ko chamkana'
WHERE (SELECT COUNT(*) FROM services) = 4;
