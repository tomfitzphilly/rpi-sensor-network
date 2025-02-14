import sqlite3
import socket
import json
from datetime import datetime
import threading

# Database setup
def init_database():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            co2 REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def store_reading(device_id, timestamp, temperature, humidity, co2):
    print("deviceid: ", str(device_id))
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_readings (device_id, timestamp, temperature, humidity, co2)
            VALUES (?, ?, ?, ?, ?)
        ''', (device_id, timestamp, temperature, humidity, co2))
        conn.commit()
    except e:
        print(f"error in store_reading - {e}")
    finally:
        conn.close()

def handle_client(client_socket, addr):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            try:
                reading = json.loads(data.decode())
                print( "sending to store_reading", str(reading))
                print(reading['device_id'])
                store_reading(
                    reading['device_id'],
                    reading['timestamp'],
                    reading['temperature'],
                    reading['humidity'],
                    reading['co2']
                )
                client_socket.send(b'OK')
            except json.JSONDecodeError:
                client_socket.send(b'ERROR: Invalid JSON')
            except KeyError:
                client_socket.send(b'ERROR: Missing required fields')
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()

def main():
    init_database()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(5)
    
    print("Server listening on port 8080...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == '__main__':
    main()
