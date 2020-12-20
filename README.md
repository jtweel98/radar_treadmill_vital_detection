(1) Create virtual env and activate
- "python3 -m venv venv"
- "source venv/bin/activate"

(2) Install dependencies
- "pip install -r requirements.txt"

(3) Start radar sensor
- "python src/radar_sensor <port>"

(4) Start speed sensor (if needed)
- "python src/speed_sensor <port>"

(5) Make sure "HOST" constant in both radar_sensor.py and speed_sensor.py is set to the raspberry pi's host IP
- use "hostname -I" command (on pi) to retrieve 
