import json

import sqlite3

DB_PATH = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        last_login TEXT,
        roles TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS mechs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        bv TEXT,
        tonnage TEXT,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pilots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        callsign TEXT,
        Pskill INTEGER,
        Gskill INTEGER,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT,
        name TEXT,
        SupportPoints INTEGER,
        mechs TEXT,
        pilots TEXT,
        reputation INTEGER,
        FOREIGN KEY(owner) REFERENCES users(username)
    )''')
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def update_last_login(username, last_login):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET last_login=? WHERE username=?', (last_login, username))
    conn.commit()
    conn.close()

def add_user(username, name, email, roles):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (username, name, email, last_login, roles) VALUES (?, ?, ?, ?, ?)',
              (username, name, email, '', roles))
    conn.commit()
    conn.close()

def add_mech(username, name, bv, tonnage):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO mechs (username, name, bv, tonnage) VALUES (?, ?, ?, ?)',
              (username, name, bv, tonnage))
    conn.commit()
    # Update the mechs field in the associated company
    c.execute('SELECT mechs FROM companies WHERE owner=?', (username,))
    result = c.fetchone()
    if result is not None:
        mechs_list = []
        if result[0]:
            try:
                mechs_list = json.loads(result[0])
            except Exception:
                mechs_list = []
        mechs_list.append({'name': name, 'bv': bv, 'tonnage': tonnage})
        c.execute('UPDATE companies SET mechs=? WHERE owner=?', (json.dumps(mechs_list), username))
        conn.commit()
    conn.close()

def get_mechs(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, bv, tonnage FROM mechs WHERE username=?', (username,))
    mechs = c.fetchall()
    conn.close()
    return mechs

def get_company(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, SupportPoints, mechs, reputation FROM companies WHERE owner=?', (username,))
    company = c.fetchone()
    conn.close()
    return company

def add_company(name, support_points, mechs, reputation, owner):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO companies (name, SupportPoints, mechs, reputation, owner) VALUES (?, ?, ?, ?, ?)',
              (name, support_points, mechs, reputation, owner))
    conn.commit()
    conn.close()

def company_exists(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM companies WHERE owner=? LIMIT 1', (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def remove_mech(username, mech_id):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Get mech details before deleting
    c.execute('SELECT name, bv, tonnage FROM mechs WHERE id=? AND username=?', (mech_id, username))
    mech = c.fetchone()
    # Delete from mechs table
    c.execute('DELETE FROM mechs WHERE id=? AND username=?', (mech_id, username))
    conn.commit()
    # Update company mechs JSON list
    if mech:
        c.execute('SELECT mechs FROM companies WHERE owner=?', (username,))
        result = c.fetchone()
        if result is not None:
            mechs_list = []
            if result[0]:
                try:
                    mechs_list = json.loads(result[0])
                except Exception:
                    mechs_list = []
            # Remove the mech matching all fields
            mechs_list = [m for m in mechs_list if not (m['name'] == mech[0] and int(m['bv']) == int(mech[1]) and int(m['tonnage']) == int(mech[2]))]
            c.execute('UPDATE companies SET mechs=? WHERE owner=?', (json.dumps(mechs_list), username))
            conn.commit()
    conn.close()

def update_support_points(username, new_points):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE companies SET SupportPoints=? WHERE owner=?', (new_points, username))
    conn.commit()
    conn.close()

def add_pilot(username, name, callsign, Pskill, Gskill):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO pilots (username, name, callsign, Pskill, Gskill) VALUES (?, ?, ?, ?, ?)',
              (username, name, callsign, Pskill, Gskill))
    conn.commit()
    conn.close()

def get_pilots(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, callsign, Pskill, Gskill FROM pilots WHERE username=?', (username,))
    pilots = c.fetchall()
    conn.close()
    return pilots

def update_pilot(pilot_id, name=None, callsign=None, Pskill=None, Gskill=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = []
    values = []
    if name is not None:
        fields.append('name=?')
        values.append(name)
    if callsign is not None:
        fields.append('callsign=?')
        values.append(callsign)
    if Pskill is not None:
        fields.append('Pskill=?')
        values.append(Pskill)
    if Gskill is not None:
        fields.append('Gskill=?')
        values.append(Gskill)
    if fields:
        query = f'UPDATE pilots SET {", ".join(fields)} WHERE id=?'
        values.append(pilot_id)
        c.execute(query, tuple(values))
        conn.commit()
    conn.close()
