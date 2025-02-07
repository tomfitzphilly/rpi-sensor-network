from machine import Pin, I2C
from scd4x import SCD4X
import time

# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Use appropriate GPIO pins for your setup

# Initialize sensor
scd4x = SCD4X(i2c)

# Optional: Configure sensor settings
scd4x.set_auto_calibration(True)  # Enable automatic self-calibration
scd4x.set_temperature_offset(2.0)  # Set temperature offset if needed
scd4x.set_altitude(0)  # Set altitude in meters for pressure compensation

# Start periodic measurements
scd4x.start_periodic_measurement()

try:
    while True:
        if scd4x.get_data_ready():
            # Read measurements
            measurement = scd4x.read_measurement()
            
            if measurement:
                co2, temperature, humidity = measurement
                print(f"CO2: {co2:.0f} ppm")
                print(f"Temperature: {temperature:.1f} °C")
                print(f"Humidity: {humidity:.0f} %")
                print("-" * 20)
            
        time.sleep(5)  # Wait 5 seconds between readings

except KeyboardInterrupt:
    # Clean up
    scd4x.stop_periodic_measurement()
