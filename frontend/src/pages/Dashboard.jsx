import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import axios from "axios";

export default function Dashboard() {
  const [stats, setStats] = useState([]);

  useEffect(() => {
    axios
      .get("/api/insights/stats")
      .then((res) => setStats(res.data))
      .catch((err) => console.error("통계 조회 실패:", err));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">📊 나의 대화 데이터</h2>
      <LineChart width={600} height={300} data={stats}>
        <XAxis dataKey="date" />
        <YAxis />
        <CartesianGrid stroke="#ccc" />
        <Line type="monotone" dataKey="count" stroke="#3b82f6" />
        <Tooltip />
      </LineChart>
    </div>
  );
}
