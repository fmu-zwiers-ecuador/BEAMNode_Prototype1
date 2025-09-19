import board
import adafruit_tsl2591

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()

# Initialize the sensor.
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read and calculate the light level in lux.
lux = sensor.lux
print(f"Lux: {lux}")