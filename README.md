# echonet_interface
Python Script to interface with a Japanese Smart Meter's Echonet protocol via a B Route USB

Based off of the work in [this blog](https://qiita.com/puma_46/items/9dfc27323674641ed5b4)

## How to Run
First, add a file called `config.py` to your project, containing the following:
```python
serialPortDev = '/dev/cu.usbserial-DM03SAK8'    # For MAC
# For windows try 'COM3'
# For Linux try '/dev/ttyUSB0'

# Your B-Route ID
rbid  = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Your B-Route Password
rbpwd = "XXXXXXXXXXXX"

# Name of the Log file for your power readings
POWER_FILE_NAME = "power.log"
# Name of the log file for your daily readings
EACH30_FILE_NAME = "each30.log"
# The folder for your logs
WRITE_PATH="data/"
```

Now Run:
```bash
pip install -r requirements.txt

python get_power.py
```
