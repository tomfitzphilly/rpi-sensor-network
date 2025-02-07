import struct
import time

class SCD30:
    def __init__(self, i2c, addr=0x61):
        self.i2c = i2c
        self.addr = addr
        self._start_continuous_measurement()
        
    def _write_command(self, cmd, data=None):
        buf = bytearray([cmd >> 8, cmd & 0xFF])
        if data is not None:
            buf.extend(data)
            buf.extend(self._calculate_crc(data))
        self.i2c.writeto(self.addr, buf)
        
    def _read_register(self, cmd, length=3):
        self._write_command(cmd)
        time.sleep_ms(4)  # Wait for the sensor to process
        return self.i2c.readfrom(self.addr, length)
        
    def _calculate_crc(self, data):
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return bytes([crc])
        
    def _start_continuous_measurement(self, pressure=0):
        pressure_bytes = struct.pack('>H', pressure)
        self._write_command(0x0010, pressure_bytes)
        
    def get_data_ready(self):
        data = self._read_register(0x0202, 3)
        return (data[0] << 8 | data[1]) == 1
        
    def read_measurement(self):
        if not self.get_data_ready():
            return None
            
        data = self._read_register(0x0300, 18)
        
        # Check CRC and unpack data
        buf = []
        for i in range(0, 18, 3):
            word = data[i:i+2]
            crc = data[i+2:i+3]
            if self._calculate_crc(word) != crc:
                return None
            buf.extend(word)
            
        co2 = struct.unpack('>f', bytes(buf[0:4]))[0]
        temp = struct.unpack('>f', bytes(buf[4:8]))[0]
        hum = struct.unpack('>f', bytes(buf[8:12]))[0]
        
        return co2, temp, hum
