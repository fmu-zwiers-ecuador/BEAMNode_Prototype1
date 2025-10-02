import spidev
import board
import busio
import digitalio
import adafruit_bme280

# CS on GPIO5 (pin 29)
CS_PIN = board.D5
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(CS_PIN)

sensor = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

print(f"Temperature (C): {sensor.temperature:.2f}")
print(f"Humidity (%): {sensor.humidity:.2f}")
print(f"Pressure (hPa): {sensor.pressure:.2f}")