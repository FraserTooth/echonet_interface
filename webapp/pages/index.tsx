import type { NextPage } from "next";
import { useState, useEffect } from "react";
import styles from "../styles/Home.module.css";
import { parse } from "csv-parse/sync";

/** Environment variables **/
const url = process.env.NEXT_PUBLIC_INFLUX_URL || "";
const token = process.env.NEXT_PUBLIC_INFLUX_TOKEN;
const org = process.env.NEXT_PUBLIC_INFLUX_ORG || "";
const bucket = process.env.NEXT_PUBLIC_INFLUX_BUCKET || "";
const fetchURL = `${url}api/v2/query?org=${org}`;

const headers = [
  ["Content-Type", "application/vnd.flux"],
  ["Accept", "application/csv"],
  ["Authorization", `Token ${token}`],
];

const fluxQuery = `from(bucket: "${bucket}")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "power")
  |> filter(fn: (r) => r["_field"] == "now_power")`;

const solarAvailabilityColor = (reading: number): string => {
  if (reading > 0) {
    const maxColorReading = 3000;
    // Calculate the Hue from 0-60 mapped from 0 to 3000
    const hueCalc = 60 - Math.floor((reading / maxColorReading) * 60);
    const hue = hueCalc > 0 ? hueCalc : 0;
    return `hsl(${hue},100%,50%)`;
  }
  return `hsl(130,100%,50%)`;
};

interface DataPoint {
  time: Date;
  value: number;
}

const Home: NextPage = () => {
  const [data, setData] = useState<DataPoint[]>([]);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(fetchURL, {
        method: "POST",
        body: fluxQuery,
        headers,
      });
      const dataRaw = await res.text();
      const data: DataPoint[] = await parse(dataRaw, {
        columns: true,
        skip_empty_lines: true,
      }).map((point: any) => {
        return { time: new Date(point._time), value: parseInt(point._value) };
      });

      setData(data);
      setLoading(false);
    };

    const id = setInterval(() => fetchData().catch(console.error), 10 * 1000);

    return () => clearInterval(id);
  }, []);

  const mostRecentPoint = data[data.length - 1];
  const color = solarAvailabilityColor(
    mostRecentPoint ? mostRecentPoint.value : 0
  );

  return (
    <div className={styles.container} style={{ backgroundColor: color }}>
      <main className={styles.main}>
        {isLoading ? (
          <div className={styles.description}>Loading...</div>
        ) : (
          <div>
            <h1 className={styles.title}>{mostRecentPoint.value} kW</h1>
            <p className={styles.description}>
              Last Updated: {mostRecentPoint.time.toLocaleTimeString("en-GB")}
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;
