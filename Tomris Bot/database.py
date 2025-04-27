import sqlite3
import time
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self):
        self.db_file = "bot.db"
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS server_settings
                    (server_id INTEGER PRIMARY KEY,
                     language TEXT DEFAULT 'tr')''')

        c.execute('''CREATE TABLE IF NOT EXISTS economy
                    (user_id INTEGER PRIMARY KEY,
                     coins INTEGER DEFAULT 0,
                     last_daily TIMESTAMP,
                     last_work TIMESTAMP,
                     timezone TEXT DEFAULT 'Europe/Istanbul')''')
        c.execute("PRAGMA table_info(economy)")
        columns = [info[1] for info in c.fetchall()]
        if 'timezone' not in columns:
            c.execute("ALTER TABLE economy ADD COLUMN timezone TEXT DEFAULT 'Europe/Istanbul'")
                     
        c.execute('''CREATE TABLE IF NOT EXISTS levels
                    (user_id INTEGER PRIMARY KEY,
                     server_id INTEGER,
                     xp INTEGER DEFAULT 0,
                     level INTEGER DEFAULT 0,
                     last_message_time TIMESTAMP)''')
                     
        c.execute('''CREATE TABLE IF NOT EXISTS custom_commands
                    (server_id INTEGER,
                     command_name TEXT,
                     response TEXT,
                     created_by INTEGER,
                     created_at TIMESTAMP,
                     PRIMARY KEY (server_id, command_name))''')
                     
        c.execute('''CREATE TABLE IF NOT EXISTS son_harf_oyunu
                    (server_id INTEGER PRIMARY KEY,
                     channel_id INTEGER,
                     active BOOLEAN DEFAULT 0,
                     current_word TEXT,
                     last_user_id INTEGER,
                     used_words TEXT DEFAULT '[]')''')

        conn.commit()
        conn.close()

    def get_server_language(self, server_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT language FROM server_settings WHERE server_id = ?", (server_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 'tr'

    def set_server_language(self, server_id, language):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO server_settings (server_id, language) VALUES (?, ?)",
                 (server_id, language))
        conn.commit()
        conn.close()

    def get_user_economy(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        conn.close()

        if not data:
            self.create_user_economy(user_id)
            return {'user_id': user_id, 'coins': 0, 'last_daily': None, 'last_work': None, 'timezone': 'Europe/Istanbul'}
        
        return {
            'user_id': data[0],
            'coins': data[1],
            'last_daily': data[2],
            'last_work': data[3],
            'timezone': data[4]
        }

    def create_user_economy(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO economy (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

    def update_coins(self, user_id, amount):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("UPDATE economy SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()

    def update_last_daily(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE economy SET last_daily = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        conn.close()

    def update_last_work(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE economy SET last_work = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        conn.close()

    def get_top_users(self, limit=10):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT ?', (limit,))
        results = c.fetchall()
        conn.close()
        return results

    def add_xp(self, user_id, server_id, xp_amount):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("INSERT OR IGNORE INTO levels (user_id, server_id, xp, level, last_message_time) VALUES (?, ?, 0, 0, ?)", 
                 (user_id, server_id, now))
        
        c.execute("UPDATE levels SET xp = xp + ?, last_message_time = ? WHERE user_id = ? AND server_id = ?", 
                 (xp_amount, now, user_id, server_id))
        
        c.execute("SELECT xp, level FROM levels WHERE user_id = ? AND server_id = ?", (user_id, server_id))
        data = c.fetchone()
        
        if data:
            current_xp, current_level = data
            new_level = int(current_xp / 100)  
            
            if new_level > current_level:
                c.execute("UPDATE levels SET level = ? WHERE user_id = ? AND server_id = ?", 
                         (new_level, user_id, server_id))
                conn.commit()
                conn.close()
                return True, new_level 
        
        conn.commit()
        conn.close()
        return False, 0  
    
    def get_user_level(self, user_id, server_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT xp, level FROM levels WHERE user_id = ? AND server_id = ?", (user_id, server_id))
        data = c.fetchone()
        conn.close()
        
        if not data:
            return {'xp': 0, 'level': 0, 'next_level_xp': 100}
        
        xp, level = data
        next_level_xp = (level + 1) * 100
        
        return {
            'xp': xp,
            'level': level,
            'next_level_xp': next_level_xp
        }
    
    def get_server_leaderboard(self, server_id, limit=10):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT user_id, xp, level FROM levels WHERE server_id = ? ORDER BY xp DESC LIMIT ?", 
                 (server_id, limit))
        results = c.fetchall()
        conn.close()
        return results
    
    def add_custom_command(self, server_id, command_name, response, created_by):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            c.execute("INSERT OR REPLACE INTO custom_commands (server_id, command_name, response, created_by, created_at) VALUES (?, ?, ?, ?, ?)",
                     (server_id, command_name.lower(), response, created_by, created_at))
            conn.commit()
            success = True
        except:
            success = False
        
        conn.close()
        return success
    
    def get_custom_command(self, server_id, command_name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("SELECT response FROM custom_commands WHERE server_id = ? AND command_name = ?", 
                 (server_id, command_name.lower()))
        result = c.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def get_server_custom_commands(self, server_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("SELECT command_name, response, created_by, created_at FROM custom_commands WHERE server_id = ? ORDER BY command_name", 
                 (server_id,))
        commands = c.fetchall()
        
        conn.close()
        return commands
    
    def delete_custom_command(self, server_id, command_name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("DELETE FROM custom_commands WHERE server_id = ? AND command_name = ?", 
                 (server_id, command_name.lower()))
        deleted = c.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    def start_son_harf_game(self, server_id, channel_id, first_word):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        used_words = json.dumps([first_word])
        
        c.execute("""INSERT OR REPLACE INTO son_harf_oyunu 
                    (server_id, channel_id, active, current_word, last_user_id, used_words) 
                    VALUES (?, ?, 1, ?, 0, ?)""", 
                    (server_id, channel_id, first_word, used_words))
        
        conn.commit()
        conn.close()
        return True
    
    def stop_son_harf_game(self, server_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("UPDATE son_harf_oyunu SET active = 0 WHERE server_id = ?", (server_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_son_harf_game(self, server_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("SELECT * FROM son_harf_oyunu WHERE server_id = ?", (server_id,))
        data = c.fetchone()
        
        conn.close()
        
        if not data:
            return None
        
        return {
            'server_id': data[0],
            'channel_id': data[1],
            'active': bool(data[2]),
            'current_word': data[3],
            'last_user_id': data[4],
            'used_words': json.loads(data[5])
        }
    
    def update_son_harf_game(self, server_id, current_word, last_user_id, used_words):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        used_words_json = json.dumps(used_words)
        
        c.execute("""UPDATE son_harf_oyunu 
                    SET current_word = ?, last_user_id = ?, used_words = ? 
                    WHERE server_id = ?""", 
                    (current_word, last_user_id, used_words_json, server_id))
        
        conn.commit()
        conn.close()
        return True

    def set_user_timezone(self, user_id, timezone):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("UPDATE economy SET timezone = ? WHERE user_id = ?", (timezone, user_id))
        conn.commit()
        conn.close()

    def get_user_timezone(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT timezone FROM economy WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        conn.close()
        if data and data[0]:
            return data[0]
        return 'Europe/Istanbul'
