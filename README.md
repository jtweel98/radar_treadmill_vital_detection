(1) Create virtual env and activate
"python3 -m venv venv"
"source venv/bin/activate"

(2) Install dependencies
pip install -r requirements.txt

(3) Start radar sensor
python src/radar_sensor <port>

(4) Start speed sensor (if needed)
python src/speed_sensor <port>