import sqlite3

def clear_products():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        conn.commit()
        print("Todos os produtos foram deletados.")

if __name__ == "__main__":
    clear_products()
