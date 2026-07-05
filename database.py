import sqlite3
import json
import random
import string
import os
from config import DB_PATH

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            amount INTEGER,
            buyer TEXT,
            seller TEXT,
            deal_detail TEXT,
            rls_upi TEXT,
            condition TEXT,
            escrow_till TEXT,
            status TEXT DEFAULT 'pending',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            handled_by INTEGER DEFAULT NULL,
            form_data TEXT,
            message_id INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deal_limit INTEGER DEFAULT 300
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pending_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_data TEXT,
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS deal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT,
            action TEXT,
            performed_by INTEGER,
            performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_admin(user_id, username, added_by, limit=300):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO admins (user_id, username, added_by, deal_limit) VALUES (?, ?, ?, ?)',
              (user_id, username, added_by, limit))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_admins():
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM admins ORDER BY deal_limit DESC').fetchall()

def get_all_admins_with_limits():
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT user_id, username, deal_limit FROM admins ORDER BY deal_limit DESC').fetchall()

def is_admin(user_id):
    conn = get_db()
    c = conn.cursor()
    result = c.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result is not None

def get_admin_limit(user_id):
    conn = get_db()
    c = conn.cursor()
    result = c.execute('SELECT deal_limit FROM admins WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result[0] if result else 0

def set_admin_limit(user_id, limit):
    conn = get_db()
    c = conn.cursor()
    if limit > 12000:
        limit = 12000
    c.execute('UPDATE admins SET deal_limit = ? WHERE user_id = ?', (limit, user_id))
    conn.commit()
    conn.close()

def generate_deal_id():
    return f"KALYUG-{''.join(random.choices(string.digits, k=6))}"

def create_deal(deal_id, form_data, created_by, message_id=None):
    conn = get_db()
    c = conn.cursor()
    amount = int(form_data.get('amount', 0))
    buyer = form_data.get('buyer', '')
    seller = form_data.get('seller', '')
    deal_detail = form_data.get('deal_detail', '')
    rls_upi = form_data.get('rls_upi', '')
    condition = form_data.get('condition', '')
    escrow_till = form_data.get('escrow_till', '')
    c.execute('''
        INSERT INTO deals (
            deal_id, amount, buyer, seller, deal_detail, rls_upi,
            condition, escrow_till, created_by, form_data, message_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (deal_id, amount, buyer, seller, deal_detail, rls_upi,
          condition, escrow_till, created_by, json.dumps(form_data), message_id))
    conn.commit()
    conn.close()

def get_deal(deal_id):
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM deals WHERE deal_id = ?', (deal_id,)).fetchone()

def update_deal_status(deal_id, status, handled_by=None):
    conn = get_db()
    c = conn.cursor()
    if handled_by:
        c.execute('UPDATE deals SET status = ?, updated_at = CURRENT_TIMESTAMP, handled_by = ? WHERE deal_id = ?',
                  (status, handled_by, deal_id))
    else:
        c.execute('UPDATE deals SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE deal_id = ?',
                  (status, deal_id))
    conn.commit()
    conn.close()

def get_deals_by_status(status):
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM deals WHERE status = ? ORDER BY created_at DESC', (status,)).fetchall()

def get_all_deals():
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM deals ORDER BY created_at DESC').fetchall()

def add_log(deal_id, action, performed_by, details=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO deal_logs (deal_id, action, performed_by, details) VALUES (?, ?, ?, ?)',
              (deal_id, action, performed_by, details))
    conn.commit()
    conn.close()

def save_pending_form(form_data, user_id, username, chat_id, message_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO pending_forms (form_data, user_id, username, chat_id, message_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (json.dumps(form_data), user_id, username, chat_id, message_id))
    conn.commit()
    conn.close()
    return c.lastrowid

def get_pending_form(form_id):
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM pending_forms WHERE id = ?', (form_id,)).fetchone()

def delete_pending_form(form_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM pending_forms WHERE id = ?', (form_id,))
    conn.commit()
    conn.close()

def get_all_pending_forms():
    conn = get_db()
    c = conn.cursor()
    return c.execute('SELECT * FROM pending_forms ORDER BY created_at DESC').fetchall()