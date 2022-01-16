# echonet_interface

Python Script to interface with a Japanese Smart Meter's Echonet protocol via a B Route USB

Based off of the work in [this blog](https://qiita.com/puma_46/items/9dfc27323674641ed5b4)

## How to Run

First, add a file to your `meter` folder: `meter/config.py`, containing the following:

```python
serialPortDev = '/dev/cu.usbserial-DM03SAK8'    # For MAC
# For windows try serialPortDev = 'COM3'
# For Linux try serialPortDev = '/dev/ttyUSB0'

# Your B-Route ID
rbid  = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Your B-Route Password
rbpwd = "XXXXXXXXXXXX"

# DB information for Influx
INFLUX_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
INFLUX_ORG = "example@example.com"
INFLUX_BUCKET = "User's Bucket"
```

Now Run:

```bash
pip install -r requirements.txt

python get_power.py
```

## How to Install and Run the Display

With [nvm](https://github.com/nvm-sh/nvm) installed, run the following to launch the display server:

```bash
cd display

nvm use
yarn
yarn start
```

## Echonet/B-Route Information

### Echonet Specs in English:

- Echonet Lite Spec: [https://echonet.jp/spec_v113_lite_en/](https://echonet.jp/spec_v113_lite_en/)
  - Specifically the [Middleware Specifications](<https://echonet.jp/wp/wp-content/uploads/pdf/General/Standard/ECHONET_lite_V1_13_en/ECHONET-Lite_Ver.1.13(02)_E.pdf>)
  - Also the current [Appendix](https://echonet.jp/spec_object_rn_en/) is very useful, search for the "Requirements for low -voltage smart electric energy meter class" section
