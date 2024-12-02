import sqlite3
import logging

class HWIDManager:
    """Manages whitelisted HWIDs using SQLite database."""

    def __init__(self, db_path="hwids.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_hwid_table()

    def create_hwid_table(self):
        """Create HWID table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hwids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hwid TEXT UNIQUE NOT NULL
            )
        ''')
        self.conn.commit()

    def is_hwid_whitelisted(self, hwid):
        """Check if the provided HWID is in the whitelist."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM hwids WHERE hwid = ?', (hwid,))
        return cursor.fetchone() is not None

    def add_hwid(self, hwid):
        """Add a new HWID to the whitelist."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO hwids (hwid) VALUES (?)', (hwid,))
            self.conn.commit()
            logging.info(f"HWID '{hwid}' added to whitelist.")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"HWID '{hwid}' is already in the whitelist.")
            return False

    def get_all_hwids(self):
        """Retrieve all HWIDs from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT hwid FROM hwids ORDER BY id')
        hwid_list = [row[0] for row in cursor.fetchall()]
        return hwid_list

    def delete_hwid(self, hwid):
        """Delete an HWID from the whitelist."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM hwids WHERE hwid = ?', (hwid,))
        self.conn.commit()
        if cursor.rowcount > 0:
            logging.info(f"HWID '{hwid}' deleted from whitelist.")
            return True
        else:
            logging.warning(f"HWID '{hwid}' not found in the whitelist.")
            return False

    def close(self):
        """Close the database connection."""
        self.conn.close()
