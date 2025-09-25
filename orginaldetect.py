CS_PIN = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT, initial=GPIO.HIGH)


spi = spidev.SpiDev()
spi.open(0, 0)
sp1.max_speed_hz = 1000000
sp1.mode = 0

def rd(reg):
    """Read a register with manual CS toggle MI"""
    GPIO.output(CS_PIN, 0)
    v = spi.xfer2([reg | 0x80, 0x00])[1]
    GPIO.output(CS_PIN, 1)
    return v

try:
    chip = rd(0xD0)
    if chip in (0x60, 0x58):
        print(f"Chip ID: 0x{chip:02x} ({'BME280'if chip=0x60 else 'BMP280'})")
    else:
        print(f"Chip ID: 0x{chip:02x} (unexpected; check wiring)")
finally:
    spi.close()
    GPIO. cleanup()
