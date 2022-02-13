import {LineChart, XAxis, YAxis, CartesianGrid, Line} from "recharts"
import {DataPoint} from "../types/types";

interface ChartProps {
    data: DataPoint[]
}

const UsageChart = (props: ChartProps) => {
    return (
        <div id="chart">
              <LineChart width={700} height={300} data={props.data}>
                <XAxis tick={false} />
                <YAxis label={{ value: 'Watts', angle: -90, position: 'insideLeft' }} domain={[-3000, 3000]} />
                <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
                <Line type="monotone" dataKey="value" stroke="#592720" strokeWidth={3} dot={false} isAnimationActive={false} />
              </LineChart>
        </div>
    )
}

export default UsageChart