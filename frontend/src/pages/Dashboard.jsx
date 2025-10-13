import { useEffect, useState } from "react";
import { LineChart, Line, PieChart, Pie, Cell, Legend, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import axios from "axios";

export default function Dashboard() {
  const [stats, setStats] = useState([]);
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, topicsRes] = await Promise.all([
          axios.get("/api/insights/stats"),
          axios.get("/api/insights/topics")
        ]);
        setStats(statsRes.data);
        setTopics(topicsRes.data);
      } catch (err) {
        console.error("데이터 조회 실패:", err);
      }
    };

    fetchData();
  }, []);

  const colors = ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa"];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* 일별 대화 통계 */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-3xl font-bold mb-6 text-gray-700">📊 나의 대화 데이터</h2>
          <LineChart width={600} height={300} data={stats}>
            <XAxis dataKey="date" />
            <YAxis />
            <CartesianGrid stroke="#ccc" />
            <Line type="monotone" dataKey="count" stroke="#3b82f6" />
            <Tooltip />
          </LineChart>
        </div>

        {/* 주제별 비율 */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-3xl font-bold mb-6 text-gray-700">🧩 주제별 대화 비율</h2>
          <PieChart width={600} height={300}>
            <Pie
              data={topics}
              dataKey="count"
              nameKey="topic"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              label
            >
              {topics.map((_, i) => (
                <Cell key={i} fill={colors[i % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>
      </div>
    </div>
  );
}
