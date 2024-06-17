import sqlite3
import sys

def add_product(name, price, stock):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", 
                           (name, price, stock))
            conn.commit()
            print(f'Produto "{name}" adicionado com sucesso.')
        except sqlite3.IntegrityError:
            print(f'Produto "{name}" já existe.')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 add_product.py <nome_do_produto> <preco> <estoque>")
        sys.exit(1)
    
    product_name = sys.argv[1]
    product_price = float(sys.argv[2])
    product_stock = int(sys.argv[3])

    add_product(product_name, product_price, product_stock)
