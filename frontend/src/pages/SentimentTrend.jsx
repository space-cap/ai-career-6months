import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer
} from "recharts";

export default function SentimentTrend() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("/api/insights/sentiment-trend")
      .then((res) => setData(res.data))
      .catch(() => console.error("데이터 불러오기 실패"));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">😊 감정 변화 트렌드</h2>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid stroke="#eee" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#22c55e" name="긍정" strokeWidth={2}/>
          <Line type="monotone" dataKey="neutral" stroke="#facc15" name="중립" strokeWidth={2}/>
          <Line type="monotone" dataKey="negative" stroke="#ef4444" name="부정" strokeWidth={2}/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
