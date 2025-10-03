import spidev  # not used directly; keeps SPI stack present
import board, busio
from digitalio import DigitalInOut
from adafruit_bme280 import basic  # explicit submodule import

# CS on GPIO5 (pin 29)
CS_PIN = board.D5
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs  = DigitalInOut(CS_PIN)

sensor = basic.Adafruit_BME280_SPI(spi, cs, baudrate=100000)

print("Temperature (C):", sensor.temperature)
print("Humidity (%):",    sensor.humidity)
print("Pressure (hPa):",  sensor.pressure)