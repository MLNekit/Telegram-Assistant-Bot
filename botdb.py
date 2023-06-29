import os
import sqlite3

class BotDB:
    def __init__(self, db_file):
        if not os.path.exists(db_file):
            open(db_file, 'a').close()
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                chat_id INTEGER PRIMARY KEY,
                notification_text TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lang (
                chat_id INTEGER PRIMARY KEY,
                lang_text TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_notification(self, chat_id, notification_text):
        cursor = self.conn.cursor()
        cursor.execute('SELECT chat_id FROM notifications WHERE chat_id = ?', (chat_id,))
        existing_record = cursor.fetchone()
        if existing_record:
            cursor.execute('UPDATE notifications SET notification_text = ? WHERE chat_id = ?', (notification_text, chat_id))
        else:
            cursor.execute('INSERT INTO notifications (chat_id, notification_text) VALUES (?, ?)', (chat_id, notification_text))
        self.conn.commit()

    def get_notification(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT notification_text FROM notifications
            WHERE chat_id = ?
        ''', (chat_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def add_lang(self, chat_id, lang_text):
        cursor = self.conn.cursor()
        cursor.execute('SELECT chat_id FROM lang WHERE chat_id = ?', (chat_id,))
        existing_record = cursor.fetchone()
        if existing_record:
            cursor.execute('UPDATE lang SET lang_text = ? WHERE chat_id = ?', (lang_text, chat_id))
        else:
            cursor.execute('INSERT INTO lang (chat_id, lang_text) VALUES (?, ?)', (chat_id, lang_text))
        self.conn.commit()

    def get_lang(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT lang_text FROM lang
            WHERE chat_id = ?
        ''', (chat_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
