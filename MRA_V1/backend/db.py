import sqlite3

class DBConnection:
    def __enter__(self):
        # Connect to (or create) the database file in the backend directory
        self.conn = sqlite3.connect("backend/mydatabase.db")
        
        # Optional: Row factory so we get dict-like row objects
        self.conn.row_factory = sqlite3.Row
        
        # Create the cursor
        self.cursor = self.conn.cursor()
        
        return self  # return the DBConnection instance itself

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the cursor and connection on exit
        self.cursor.close()
        self.conn.close()

    def execute(self, query, params=None):
        """Execute a single SQL query with optional params."""
        if params is None:
            params = ()
        self.cursor.execute(query, params)

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def fetchone(self):
        """Fetch the next row of a query result, returning a single result."""
        return self.cursor.fetchone()

    def fetchall(self):
        """Fetch all (remaining) rows of a query result."""
        return self.cursor.fetchall()