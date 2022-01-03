from datetime import datetime

from urllib3.exceptions import ReadTimeoutError

from . import echonet, config
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def write_to_influx(data: dict[echonet.SmartMeterActions, str]):
    with InfluxDBClient(
        url="https://us-central1-1.gcp.cloud2.influxdata.com",
        token=config.INFLUX_TOKEN,
        org=config.INFLUX_ORG,
    ) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point = (
            Point("power")
            .field("now_power", data[echonet.SmartMeterActions.NOW_POWER])
            .time(datetime.utcnow(), WritePrecision.NS)
        )

        try:
            write_api.write(config.INFLUX_BUCKET, config.INFLUX_ORG, point)
        except ReadTimeoutError:
            print("Couldn't write datapoint to influx...")

        client.close()
