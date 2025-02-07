import network
import socket
import json
import time
from machine import Pin, I2C
from scd30 import SCD30

# Network configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
SERVER_IP = "your_server_ip"  # Replace with your Raspberry Pi 3's IP address
SERVER_PORT = 8080
DEVICE_ID = "pico_1"  # Change this for each Pico (pico_1, pico_2, pico_3)

# Initialize I2C for SCD30
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Use appropriate GPIO pins
scd30 = SCD30(i2c, 0x61)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi connected:', wlan.ifconfig())
    return wlan

def send_data(sock, data):
    try:
        sock.send(json.dumps(data).encode())
        response = sock.recv(1024).decode()
        return response == 'OK'
    except Exception as e:
        print('Error sending data:', e)
        return False

def main():
    # Connect to WiFi
    wlan = connect_wifi()
    
    while True:
        try:
            # Create new socket connection
            sock = socket.socket()
            sock.connect((SERVER_IP, SERVER_PORT))
            
            while True:
                if scd30.get_data_ready():
                    measurement = scd30.read_measurement()
                    if measurement is not None:
                        co2, temperature, humidity = measurement
                        
                        data = {
                            'device_id': DEVICE_ID,
                            'timestamp': time.time(),
                            'temperature': temperature,
                            'humidity': humidity,
                            'co2': co2
                        }
                        
                        if send_data(sock, data):
                            print('Data sent successfully')
                        else:
                            print('Failed to send data')
                            break
                            
                time.sleep(2)  # Wait before next reading
                
        except Exception as e:
            print('Connection error:', e)
            time.sleep(5)  # Wait before reconnecting
        finally:
            try:
                sock.close()
            except:
                pass

if __name__ == '__main__':
    main()
