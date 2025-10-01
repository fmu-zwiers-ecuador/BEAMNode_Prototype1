import board
import adafruit_tsl2591
import json
import schedule
import time
from datetime import datetime

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()

# Initialize the sensor.
sensor = adafruit_tsl2591.TSL2591(i2c)

def save_lux_data():
    lux = sensor.lux
    
    lux_json_data = {
        "date": datetime.now().isoformat,
        "lux": lux
    }

    file_name = f"hourly_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(f"data/tsl5291/{file_name}", 'w') as f:
            json.dump(lux_json_data, f, indent=4)
        print(f"Lux data saved to {file_name} at {datetime.now()}")
    except Exception as e:
        print(f"Error saving lux data: {e}")

# Schedule the function to run every hour
schedule.every().hour.do(save_lux_data)

print("Scheduler started. Saving data every hour...")

# Keep the script running to allow the scheduler to execute
while True:
    schedule.run_pending()
    time.sleep(1) # Check for pending jobs every second