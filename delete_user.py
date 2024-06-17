import sqlite3
import sys

def delete_user(username):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        
        if user is None:
            print(f"User '{username}' not found.")
            return

        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        print(f"User '{username}' deleted successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    delete_user(username)
