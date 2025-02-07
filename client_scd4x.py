import network
import socket
import json
import time
from machine import Pin, I2C
from scd4x import SCD4X

# Network configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
SERVER_IP = "your_server_ip"  # Replace with your Raspberry Pi 3's IP address
SERVER_PORT = 8080
DEVICE_ID = "pico_1"  # Change this for each Pico (pico_1, pico_2, pico_3)

# Sensor configuration
ALTITUDE = 0  # Set your altitude in meters for accurate readings
TEMP_OFFSET = 0.0  # Set temperature offset if needed (e.g., 2.0 for 2°C)
MEASUREMENT_INTERVAL = 5  # Seconds between measurements

# Initialize I2C for SCD4X
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Use appropriate GPIO pins
scd4x = SCD4X(i2c)

def setup_sensor():
    """Initialize and configure the SCD4X sensor."""
    try:
        # Stop any previous measurements
        scd4x.stop_periodic_measurement()
        time.sleep_ms(500)
        
        # Configure sensor settings
        scd4x.set_altitude(ALTITUDE)
        scd4x.set_temperature_offset(TEMP_OFFSET)
        scd4x.set_auto_calibration(True)
        
        # Start periodic measurements
        scd4x.start_periodic_measurement()
        print("SCD4X sensor initialized successfully")
        return True
    except Exception as e:
        print("Error initializing sensor:", e)
        return False

def connect_wifi():
    """Connect to WiFi network."""
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
    """Send data to server and receive response."""
    try:
        sock.send(json.dumps(data).encode())
        response = sock.recv(1024).decode()
        return response == 'OK'
    except Exception as e:
        print('Error sending data:', e)
        return False

def read_sensor():
    """Read data from SCD4X sensor."""
    if scd4x.get_data_ready():
        measurement = scd4x.read_measurement()
        if measurement is not None:
            co2, temperature, humidity = measurement
            return {
                'device_id': DEVICE_ID,
                'timestamp': time.time(),
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 1),
                'co2': round(co2)
            }
    return None

def main():
    # Initialize sensor
    if not setup_sensor():
        print("Failed to initialize sensor. Exiting...")
        return
    
    # Connect to WiFi
    wlan = connect_wifi()
    
    # Main loop
    while True:
        try:
            # Create new socket connection
            sock = socket.socket()
            sock.connect((SERVER_IP, SERVER_PORT))
            print("Connected to server")
            
            while True:
                # Read sensor data
                data = read_sensor()
                
                if data:
                    if send_data(sock, data):
                        print(f"Data sent - CO2: {data['co2']} ppm, "
                              f"Temp: {data['temperature']}°C, "
                              f"Humidity: {data['humidity']}%")
                    else:
                        print("Failed to send data")
                        break
                else:
                    print("No valid reading available")
                
                time.sleep(MEASUREMENT_INTERVAL)
                
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
