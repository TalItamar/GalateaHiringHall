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
        improvements INTEGER,
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
        scale INTEGER,
        FOREIGN KEY(owner) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT,
        name TEXT,
        length INTEGER,
        tracks TEXT,
        track_types TEXT,
        base_pay INTEGER,
        salvage_terms INTEGER,
        transport_terms INTEGER,
        support_rights INTEGER,
        command_rights INTEGER,
        status TEXT DEFAULT 'active',
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

def get_role(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT roles FROM users WHERE username=?', (username,))
    roles = c.fetchone()
    conn.close()
    return roles[0] if roles else None

def get_all_companies():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, SupportPoints, mechs, reputation, owner FROM companies')
    companies = c.fetchall()
    conn.close()
    return companies

def update_company(owner, name=None, support_points=None, mechs=None, reputation=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = []
    values = []
    if name is not None:
        fields.append('name=?')
        values.append(name)
    if support_points is not None:
        fields.append('SupportPoints=?')
        values.append(support_points)
    if mechs is not None:
        fields.append('mechs=?')
        values.append(mechs)
    if reputation is not None:
        fields.append('reputation=?')
        values.append(reputation)
    if fields:
        query = f'UPDATE companies SET {", ".join(fields)} WHERE owner=?'
        values.append(owner)
        c.execute(query, tuple(values))
        conn.commit()
    conn.close()

def update_mech(mech_id, name=None, bv=None, tonnage=None, username=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = []
    values = []
    if name is not None:
        fields.append('name=?')
        values.append(name)
    if bv is not None:
        fields.append('bv=?')
        values.append(bv)
    if tonnage is not None:
        fields.append('tonnage=?')
        values.append(tonnage)
    if username is not None:
        fields.append('username=?')
        values.append(username)
    if fields:
        query = f'UPDATE mechs SET {", ".join(fields)} WHERE id=?'
        values.append(mech_id)
        c.execute(query, tuple(values))
        conn.commit()
    conn.close()

def get_all_pilots():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, name, callsign, Pskill, Gskill FROM pilots')
    pilots = c.fetchall()
    conn.close()
    return pilots

def get_all_mechs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, name, bv, tonnage FROM mechs')
    mechs = c.fetchall()
    conn.close()
    return mechs

def add_contract(owner, name, length, tracks, track_types, base_pay, salvage_terms, transport_terms, support_rights, command_rights, status='active'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO contracts (owner, name, length, tracks, track_types, base_pay, salvage_terms, transport_terms, support_rights, command_rights, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (owner, name, length, tracks, track_types, base_pay, salvage_terms, transport_terms, support_rights, command_rights, status))
    conn.commit()
    conn.close()

def get_all_contracts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM contracts WHERE status="active"')
    contracts = c.fetchall()
    conn.close()
    return contracts

def get_company_contracts(owner):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM contracts WHERE owner=? AND status="active"', (owner,))
    contracts = c.fetchall()
    conn.close()
    return contracts

def get_active_contract(owner=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if owner:
        c.execute('SELECT * FROM contracts WHERE owner=? AND status="active"', (owner,))
    else:
        c.execute('SELECT * FROM contracts WHERE status="active"')
    contracts = c.fetchall()
    conn.close()
    return contracts

def update_contract(contract_id, name=None, length=None, tracks=None, track_types=None, base_pay=None, salvage_terms=None, transport_terms=None, support_rights=None, command_rights=None, status=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = []
    values = []
    if name is not None:
        fields.append('name=?')
        values.append(name)
    if length is not None:
        fields.append('length=?')
        values.append(length)
    if tracks is not None:
        fields.append('tracks=?')
        values.append(tracks)
    if track_types is not None:
        fields.append('track_types=?')
        values.append(track_types)
    if base_pay is not None:
        fields.append('base_pay=?')
        values.append(base_pay)
    if salvage_terms is not None:
        fields.append('salvage_terms=?')
        values.append(salvage_terms)
    if transport_terms is not None:
        fields.append('transport_terms=?')
        values.append(transport_terms)
    if support_rights is not None:
        fields.append('support_rights=?')
        values.append(support_rights)
    if command_rights is not None:
        fields.append('command_rights=?')
        values.append(command_rights)
    if status is not None:
        fields.append('status=?')
        values.append(status)
    if fields:
        query = f'UPDATE contracts SET {", ".join(fields)} WHERE id=?'
        values.append(contract_id)
        c.execute(query, tuple(values))
        conn.commit()
    conn.close()

def set_all_contracts_inactive():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE contracts SET status="inactive" WHERE status="active"')
    conn.commit()
    conn.close()