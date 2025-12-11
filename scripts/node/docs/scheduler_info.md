# SCRIPT TO SCHEDULE AND EXECUTE SENSOR READING - scheduler.py

This script should should read frequency values from 'config.json' in minutes, then execute
each sensor on a node periodically after the specified number of minutes has passed.

IMPORTANT: every sensor in config.json should be named exactly the same as the directory they run under. Otherwise,
scheduler.py will not be able to find the script, and won't function correctly.

scheduler.py will only execute scripts from sensors marked as enabled in config.json. Detect.py should write to 
config,json and adjust accordingly.