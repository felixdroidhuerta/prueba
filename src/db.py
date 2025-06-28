import mysql.connector
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'Iris.iker1',
    'database': 'asistencia'
}

@contextmanager
def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    import mysql.connector

    base_cfg = DB_CONFIG.copy()
    db_name = base_cfg.pop('database')  # 'asistencia'

    # 1) Conectar SIN especificar database ? crearla si no existe
    with mysql.connector.connect(**base_cfg) as conn:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        conn.commit()

    # 2) Conectar a la nueva BD y crear tablas
    with mysql.connector.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                role ENUM('trabajador','administrador') NOT NULL,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                sensor_id INT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                event VARCHAR(50) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()



def add_user(name, role, sensor_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, role, sensor_id) VALUES (%s, %s, %s)',
            (name, role, sensor_id)
        )
        conn.commit()
        return cursor.lastrowid


def update_user(user_id, name=None, role=None, active=None, sensor_id=None):
    fields = []
    values = []
    if name is not None:
        fields.append('name=%s')
        values.append(name)
    if role is not None:
        fields.append('role=%s')
        values.append(role)
    if active is not None:
        fields.append('active=%s')
        values.append(active)
    if sensor_id is not None:
        fields.append('sensor_id=%s')
        values.append(sensor_id)
    if not fields:
        return
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id=%s"
    with get_connection() as conn:
        conn.cursor().execute(query, values)
        conn.commit()


def get_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        return cursor.fetchone()


def get_user_by_sensor(sensor_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE sensor_id = %s AND active = 1', (sensor_id,))
        return cursor.fetchone()


def log_event(user_id, event):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO records (user_id, event) VALUES (%s, %s)', (user_id, event))
        conn.commit()


def list_records():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, u.name, r.event, r.timestamp
            FROM records r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.timestamp DESC
        ''')
        return cursor.fetchall()
