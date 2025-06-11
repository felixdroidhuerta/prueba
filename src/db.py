import sqlite3
from contextlib import closing

DB_PATH = 'attendance.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('trabajador','administrador')),
    active INTEGER NOT NULL DEFAULT 1,
    sensor_id INTEGER
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
'''


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


def add_user(name, role, sensor_id=None):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            'INSERT INTO users(name, role, sensor_id) VALUES (?, ?, ?)',
            (name, role, sensor_id),
        )
        return c.lastrowid


def update_user(user_id, name=None, role=None, active=None, sensor_id=None):
    fields = []
    values = []
    if name is not None:
        fields.append('name=?')
        values.append(name)
    if role is not None:
        fields.append('role=?')
        values.append(role)
    if active is not None:
        fields.append('active=?')
        values.append(active)
    if sensor_id is not None:
        fields.append('sensor_id=?')
        values.append(sensor_id)
    if not fields:
        return
    values.append(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"UPDATE users SET {','.join(fields)} WHERE id=?", values)


def get_user_by_sensor(sensor_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT * FROM users WHERE sensor_id=? AND active=1', (sensor_id,))
        return cur.fetchone()


def get_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT * FROM users WHERE id=?', (user_id,))
        return cur.fetchone()


def log_event(user_id, event):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('INSERT INTO records(user_id, event) VALUES (?, ?)', (user_id, event))


def list_records():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT r.id, u.name, r.event, r.timestamp FROM records r JOIN users u ON r.user_id = u.id ORDER BY r.timestamp DESC')
        return cur.fetchall()
