import sqlite3

def listar_usuarios():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, saldo, fingerprint_id FROM users")
        users = cursor.fetchall()

    print('\nLista de usuários:')
    if not users:
        print('\nNenhum usuário cadastrado!\n')
    else:
        for user in users:
            print(f'Username: {user[0]}     Password: {user[1]}     Saldo: {user[2]}     Fingerprint ID: {user[3]}')




if __name__ == '__main__':
    listar_usuarios()
