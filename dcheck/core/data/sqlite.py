'''
DCheck Data - Sqlite Backend
'''
# Python
import sqlite3

# DCheck
import dcheck.core.config


class DataEngine:
    '''
    Connect dcheck data to a sqlite backend.
    '''
    def __init__(self):
        self.connection = sqlite3.connect(
                dcheck.core.config.get('sqlite_path'))
        self._create_schema()

    def _create_schema(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.connection.commit()
        cursor.close()

    def set(self, key, value):
        '''
        Set a value in SQLite
        '''
        cursor = self.connection.cursor()
        cursor.execute(
                'INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)',
                (key, value))
        self.connection.commit()
        cursor.close()

    def get(self, key):
        '''
        Get a value from SQLite
        '''
        cursor = self.connection.cursor()
        cursor.execute('SELECT value FROM data WHERE key = ?', (key,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        return None

    def keys(self, pattern):
        '''
        Return keys matching a given pattern
        '''
        cursor = self.connection.cursor()
        cursor.execute('SELECT key FROM data WHERE key LIKE ?', (pattern,))
        keys = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return keys
