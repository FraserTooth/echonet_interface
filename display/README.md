## How to Install and Run the Display Webapp

Add a text file titled `.env.local` to the `display` folder with the following:

```
NEXT_PUBLIC_INFLUX_URL=<Your Influx Host URL - probably looks like -> https://us-central1-1.gcp.cloud2.influxdata.com>
NEXT_PUBLIC_INFLUX_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_INFLUX_ORG=<Your Influx Org Name>
NEXT_PUBLIC_INFLUX_BUCKET=<Your Influx Bucket Name>
```

With [nvm](https://github.com/nvm-sh/nvm) installed, run the following to launch the display server:

```bash
cd display

nvm use
yarn
yarn start
```
