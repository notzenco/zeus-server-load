import sqlite3
import logging

class ConfigManager:
    """Manages configuration settings using SQLite database."""

    def __init__(self, db_path="hwids.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_config_table()

    def create_config_table(self):
        """Create the config table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def get_config(self, key):
        """Retrieve a configuration value by key."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None

    def set_config(self, key, value):
        """Set or update a configuration value."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        ''', (key, value))
        self.conn.commit()
        logging.info(f"Configuration '{key}' set to '{value}'.")

    def close(self):
        """Close the database connection."""
        self.conn.close()
