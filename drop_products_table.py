import sqlite3

def drop_table():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS products')
        conn.commit()
        print('Tabela excluída com sucesso.')

if __name__ == '__main__':
    drop_table()
