from machine import I2C
import struct
import time

class SCD4X:
    """MicroPython driver for Sensirion SCD4X CO2 sensors (SCD40, SCD41)"""
    
    # Default I2C address
    DEFAULT_ADDR = 0x62
    
    # Commands
    CMD_START_PERIODIC = 0x21B1
    CMD_READ_MEASUREMENT = 0xEC05
    CMD_STOP_PERIODIC = 0x3F86
    CMD_SET_TEMP_OFFSET = 0x241D
    CMD_GET_TEMP_OFFSET = 0x2318
    CMD_SET_ALTITUDE = 0x2427
    CMD_GET_ALTITUDE = 0x2322
    CMD_SET_AUTO_CALIB = 0x2416
    CMD_GET_AUTO_CALIB = 0x2313
    CMD_FACTORY_RESET = 0x3632
    CMD_SINGLE_SHOT = 0x219D
    CMD_DATA_READY = 0xE4B8
    
    def __init__(self, i2c, addr=DEFAULT_ADDR):
        """Initialize the SCD4X sensor.
        
        Args:
            i2c: Initialized I2C object
            addr: I2C address (default: 0x62)
        """
        self.i2c = i2c
        self.addr = addr
        self.stop_periodic_measurement()
        time.sleep_ms(500)
    
    def _write_command(self, cmd, data=None):
        """Write a command and optional data to the sensor."""
        buf = bytearray([cmd >> 8, cmd & 0xFF])
        if data is not None:
            buf.extend(data)
        self.i2c.writeto(self.addr, buf)
    
    def _read_data(self, size=3):
        """Read data from the sensor."""
        return self.i2c.readfrom(self.addr, size)
    
    def _check_crc(self, data):
        """Calculate and verify CRC for sensor data."""
        crc = 0xFF
        for byte in data[:-1]:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc == data[-1]
    
    def start_periodic_measurement(self):
        """Start periodic measurement."""
        self._write_command(self.CMD_START_PERIODIC)
        time.sleep_ms(1)
    
    def stop_periodic_measurement(self):
        """Stop periodic measurement."""
        self._write_command(self.CMD_STOP_PERIODIC)
        time.sleep_ms(500)
    
    def get_data_ready(self):
        """Check if data is ready to be read."""
        self._write_command(self.CMD_DATA_READY)
        data = self._read_data(3)
        return (data[0] << 8 | data[1]) == 1
    
    def read_measurement(self):
        """Read CO2, temperature, and humidity measurements.
        
        Returns:
            Tuple of (CO2 [ppm], temperature [°C], relative humidity [%])
            or None if CRC check fails
        """
        self._write_command(self.CMD_READ_MEASUREMENT)
        data = self._read_data(9)
        
        # Split data into 3 words of 2 bytes + CRC
        words = [(data[i:i+2], data[i+2]) for i in range(0, 9, 3)]
        
        # Check CRC for each word
        if not all(self._check_crc(word[0] + bytes([word[1]])) for word in words):
            return None
        
        # Convert data
        co2 = struct.unpack('>H', words[0][0])[0]
        temp = -45 + 175 * struct.unpack('>H', words[1][0])[0] / 65535
        hum = 100 * struct.unpack('>H', words[2][0])[0] / 65535
        
        return co2, temp, hum
    
    def single_shot_measurement(self):
        """Perform a single shot measurement.
        
        Returns:
            Same as read_measurement()
        """
        self._write_command(self.CMD_SINGLE_SHOT)
        time.sleep_ms(5000)  # Wait for measurement
        return self.read_measurement()
    
    def set_temperature_offset(self, offset):
        """Set temperature offset in degrees Celsius."""
        offset_ticks = int((offset * 65535) / 175)
        data = struct.pack('>H', offset_ticks)
        self._write_command(self.CMD_SET_TEMP_OFFSET, data)
        time.sleep_ms(1)
    
    def get_temperature_offset(self):
        """Get current temperature offset in degrees Celsius."""
        self._write_command(self.CMD_GET_TEMP_OFFSET)
        data = self._read_data(3)
        if not self._check_crc(data):
            return None
        offset_ticks = struct.unpack('>H', data[:2])[0]
        return (offset_ticks * 175) / 65535
    
    def set_altitude(self, altitude):
        """Set altitude in meters above sea level."""
        data = struct.pack('>H', altitude)
        self._write_command(self.CMD_SET_ALTITUDE, data)
        time.sleep_ms(1)
    
    def set_auto_calibration(self, enable):
        """Enable or disable automatic self-calibration."""
        data = struct.pack('>H', 1 if enable else 0)
        self._write_command(self.CMD_SET_AUTO_CALIB, data)
        time.sleep_ms(1)
    
    def get_auto_calibration(self):
        """Get automatic self-calibration status."""
        self._write_command(self.CMD_GET_AUTO_CALIB)
        data = self._read_data(3)
        if not self._check_crc(data):
            return None
        return struct.unpack('>H', data[:2])[0] == 1
    
    def factory_reset(self):
        """Perform factory reset."""
        self._write_command(self.CMD_FACTORY_RESET)
        time.sleep_ms(1200)
