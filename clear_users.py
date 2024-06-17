import sqlite3

def clear_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
    
    print("\nBanco de dados limpo. Todos os usuários foram removidos.")

if __name__ == '__main__':
    clear_db()
