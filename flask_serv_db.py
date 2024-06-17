import sqlite3
import time
import serial
import board
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Configuração do banco de dados
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        # Criar tabela de usuários
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, 
                           username TEXT UNIQUE, 
                           password TEXT,
                           saldo REAL DEFAULT 0,
                           fingerprint_id INTEGER)''')
        # Criar tabela de produtos
        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                          (id INTEGER PRIMARY KEY,
                           name TEXT UNIQUE,
                           price REAL,
                           stock INTEGER)''')
        conn.commit()

def cadastrar_usuario(username, password):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, saldo) VALUES (?, ?, ?)", 
                           (username, password, 0.0))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
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

    return users

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']

    success = cadastrar_usuario(username, password)

    if success:
        print(f'Usuário cadastrado! Username: {username}     Password: {password}')
        listar_usuarios()
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'message': 'Username already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
    
    if user:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/list_users', methods=['GET'])
def list_users_route():
    users = listar_usuarios()
    return jsonify(users), 200

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    username = data['username']
    new_balance = data['new_balance']
    
    print(f"Tentando atualizar o saldo para o usuário: {username} para o novo saldo: {new_balance}")

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT saldo FROM users WHERE username=?", (username,))
        user_saldo = cursor.fetchone()
        
        if user_saldo is not None:
            print(f"Saldo atual do usuário: {user_saldo[0]}")
            cursor.execute("UPDATE users SET saldo=? WHERE username=?", (new_balance, username))
            conn.commit()
            cursor.execute("SELECT saldo FROM users WHERE username=?", (username,))
            updated_saldo = cursor.fetchone()
            print(f"Novo saldo do usuário: {updated_saldo[0]}")
        else:
            print(f"Usuário {username} não encontrado.")

    listar_usuarios()

    return jsonify({'message': 'Balance updated successfully'}), 200

@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.get_json()
    username = data['username']

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT saldo FROM users WHERE username=?", (username,))
        user_balance = cursor.fetchone()

    if user_balance:
        return jsonify({'balance': user_balance[0]}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/list_products', methods=['GET'])
def list_products():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products")
        products = cursor.fetchall()
    return jsonify(products), 200

# Endpoint para atualizar o estoque de um produto
@app.route('/update_product_stock', methods=['POST'])
def update_product_stock():
    data = request.get_json()
    product_name = data['name']
    new_stock = data['stock']
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM products WHERE name=?", (product_name,))
        product = cursor.fetchone()
        
        if product:
            cursor.execute("UPDATE products SET stock=? WHERE name=?", (new_stock, product_name))
            conn.commit()
            return jsonify({'message': 'Product stock updated successfully'}), 200
        else:
            return jsonify({'message': 'Product not found'}), 404

# Configuração do sensor de impressão digital
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Configurar a conexão UART
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

@app.route('/register_fingerprint', methods=['POST'])
def register_fingerprint():
    data = request.get_json()
    username = data['username']

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fingerprint_id FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        user_id, fingerprint_id = user

        if fingerprint_id is not None:
            return jsonify({'message': 'User already has a registered fingerprint'}), 409

        # Registrar a impressão digital
        if enroll_finger(user_id):
            cursor.execute("UPDATE users SET fingerprint_id=? WHERE id=?", (user_id, user_id))
            conn.commit()
            return jsonify({'message': 'Fingerprint registered successfully'}), 201
        else:
            return jsonify({'message': 'Failed to register fingerprint'}), 500

@app.route('/fingerprint_login', methods=['POST'])
def fingerprint_login():
    if get_fingerprint():
        fingerprint_id = finger.finger_id
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE fingerprint_id=?", (fingerprint_id,))
            user = cursor.fetchone()

            if user:
                return jsonify({'message': f'Login successful for user {user[0]}'}), 200
            else:
                return jsonify({'message': 'Fingerprint not recognized'}), 401
    else:
        return jsonify({'message': 'Fingerprint not recognized'}), 401

def enroll_finger(location):
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print(f"Storing model #{location}...", end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

def get_fingerprint():
    """Get a fingerprint image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

@app.route('/activate_motor', methods=['POST'])
def activate_motor():
    data = request.get_json()
    motor_id = data.get('id')  # Supondo que você passe o ID do motor no JSON da requisição

    if(motor_id == 1):
        # Execute o script motorX.py usando subprocess
        try:
            subprocess.run(['python3', 'motorX.py'], check=True)
            return jsonify({'message': 'Motor X activated successfully'}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'message': 'Failed to activate motor', 'error': str(e)}), 500
    elif(motor_id == 2):
        # Execute o script motorY.py usando subprocess
        try:
            subprocess.run(['python3', 'motorY.py'], check=True)
            return jsonify({'message': 'Motor Y activated successfully'}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'message': 'Failed to activate motor', 'error': str(e)}), 500
    elif(motor_id == 3):
        # Execute o script motorZ.py usando subprocess
        try:
            subprocess.run(['python3', 'motorZ.py'], check=True)
            return jsonify({'message': 'Motor Z activated successfully'}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'message': 'Failed to activate motor', 'error': str(e)}), 500
        
@app.route('/print_receipt', methods=['POST'])
def print_receipt():
    try:
        # Executa os comandos de shell diretamente
        subprocess.run(['cd / && cd /dev/usb && sudo chmod a+w /dev/usb/lp0 && sudo echo -e "\n\n\n\n\nTest Thermal Print\nTesteB\nTesteC\n123456789*-+\n\n" > /dev/usb/lp0'], shell=True, check=True)
        return jsonify({'message': 'Receipt printed successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'message': 'Failed to print receipt', 'error': str(e)}), 500
    
            
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
