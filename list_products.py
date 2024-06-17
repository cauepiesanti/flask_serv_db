import sqlite3

def listar_produtos():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock FROM products")
        products = cursor.fetchall()

    if not products:
        print('Nenhum produto cadastrado!')
    else:
        print('Lista de produtos:')
        for product in products:
            print(f'Nome: {product[0]} | Preço: {product[1]:.2f} | Estoque: {product[2]}')

if __name__ == "__main__":
    listar_produtos()
